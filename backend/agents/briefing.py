from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

try:
    from openai import OpenAI as _OpenAI
    _OPENAI_AVAILABLE = True
except ImportError:
    _OpenAI = None  # type: ignore[assignment,misc]
    _OPENAI_AVAILABLE = False

try:
    import anthropic
    _ANTHROPIC_AVAILABLE = True
except ImportError:
    anthropic = None  # type: ignore[assignment]
    _ANTHROPIC_AVAILABLE = False

from backend.config import settings
from backend.models.schemas import BriefingReport, RepoActivity, SlackMessage

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a team coordinator. Given GitHub activity and Slack messages, \
write a concise daily briefing that helps the team understand what happened, what decisions \
were made, and what needs attention.

Respond ONLY with valid JSON matching this schema:
{
  "summary": "2-3 sentence overview of the day's activity",
  "key_decisions": ["decision 1", "decision 2"],
  "blockers": ["blocker 1", "blocker 2"],
  "momentum": "one sentence on velocity/energy of the team",
  "action_items": ["action 1", "action 2"]
}

Be specific, concise, and actionable. If no data was provided, say so gracefully.
Keep each list to 3-5 items max. No markdown in the JSON string values."""


def _build_user_message(
    repo_activities: list[RepoActivity],
    slack_messages: list[SlackMessage],
    team_name: str,
    hours: int,
) -> str:
    parts = [f"Team: {team_name}", f"Period: last {hours} hours", ""]

    # GitHub section
    if repo_activities:
        parts.append("=== GitHub Activity ===")
        for activity in repo_activities:
            parts.append(f"\nRepo: {activity.repo}")
            if activity.prs:
                parts.append(f"PRs ({len(activity.prs)}):")
                for pr in activity.prs[:10]:
                    parts.append(f"  [{pr.state}] #{pr.number} {pr.title} by @{pr.author}")
            if activity.commits:
                parts.append(f"Commits ({len(activity.commits)}):")
                for c in activity.commits[:10]:
                    parts.append(f"  {c.sha} {c.message} by @{c.author}")
            if activity.issues:
                parts.append(f"Issues ({len(activity.issues)}):")
                for issue in activity.issues[:10]:
                    parts.append(f"  [{issue.state}] #{issue.number} {issue.title} by @{issue.author}")
    else:
        parts.append("=== GitHub Activity ===\nNo repos configured.")

    # Slack section
    parts.append("\n=== Slack Messages ===")
    if slack_messages:
        for msg in slack_messages[:30]:
            parts.append(f"  @{msg.user}: {msg.text[:200]}")
    else:
        parts.append("No Slack messages or Slack not configured.")

    return "\n".join(parts)


def _mock_briefing(
    repo_activities: list[RepoActivity],
    slack_messages: list[SlackMessage],
    team_name: str,
) -> BriefingReport:
    """Return a realistic mock briefing when no API key is set."""
    total_prs = sum(len(a.prs) for a in repo_activities)
    total_commits = sum(len(a.commits) for a in repo_activities)
    total_issues = sum(len(a.issues) for a in repo_activities)
    repo_names = [a.repo.split("/")[-1] for a in repo_activities] if repo_activities else ["your repos"]

    summary = (
        f"{team_name} had {total_commits} commit(s) and {total_prs} PR(s) across "
        f"{', '.join(repo_names)} in the last 24 hours. "
        f"There are {total_issues} issue(s) with recent activity. "
        "(This is a mock briefing — set ANTHROPIC_API_KEY for AI-generated summaries.)"
    )

    key_decisions: list[str] = []
    if total_prs > 0:
        key_decisions.append(f"{total_prs} pull request(s) updated — review and merge as appropriate")
    if total_commits > 0:
        key_decisions.append(f"{total_commits} commit(s) landed — verify CI is green")

    blockers: list[str] = []
    open_issues = [
        issue
        for a in repo_activities
        for issue in a.issues
        if issue.state == "open"
    ]
    if open_issues:
        blockers.append(f"{len(open_issues)} open issue(s) need triage")

    return BriefingReport(
        summary=summary,
        key_decisions=key_decisions or ["No notable decisions — quiet day"],
        blockers=blockers or [],
        momentum="Steady progress with no major disruptions detected." if total_commits > 0 else "Low activity detected.",
        action_items=["Review open pull requests", "Check CI status"] if total_prs > 0 else ["Check for any pending issues"],
    )


def _parse_content(content: str) -> BriefingReport:
    """Parse JSON content, stripping markdown fences if present."""
    content = content.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()
    data = json.loads(content)
    return BriefingReport(**data)


async def _run_with_do_gradient(user_message: str) -> str:
    """Call DigitalOcean Gradient AI serverless inference (OpenAI-compatible)."""
    client = _OpenAI(
        base_url=settings.do_inference_base_url,
        api_key=settings.do_model_access_key,
    )
    response = client.chat.completions.create(
        model=settings.do_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.3,
        max_completion_tokens=1024,
    )
    return response.choices[0].message.content or ""


async def _run_with_anthropic(user_message: str) -> str:
    """Fallback: Anthropic Claude."""
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text


async def synthesize_briefing(
    repo_activities: list[RepoActivity],
    slack_messages: list[SlackMessage],
    team_name: str = "Team",
    hours: int = 24,
) -> BriefingReport:
    if settings.use_mock:
        logger.info("Mock mode active — returning mock briefing")
        return _mock_briefing(repo_activities, slack_messages, team_name)

    user_message = _build_user_message(repo_activities, slack_messages, team_name, hours)

    try:
        if settings.use_do_gradient and _OPENAI_AVAILABLE:
            logger.info("Synthesizing briefing via DigitalOcean Gradient AI")
            raw = await _run_with_do_gradient(user_message)
        elif _ANTHROPIC_AVAILABLE and settings.anthropic_api_key:
            logger.info("Synthesizing briefing via Anthropic Claude (fallback)")
            raw = await _run_with_anthropic(user_message)
        else:
            logger.warning("No AI backend configured — returning mock briefing")
            return _mock_briefing(repo_activities, slack_messages, team_name)

        return _parse_content(raw)
    except json.JSONDecodeError as e:
        logger.error("Failed to parse AI JSON response: %s", e)
        return _mock_briefing(repo_activities, slack_messages, team_name)
    except Exception as e:
        logger.error("AI synthesis failed: %s", e)
        return _mock_briefing(repo_activities, slack_messages, team_name)

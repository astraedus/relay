from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta, timezone

try:
    from slack_sdk.web.async_client import AsyncWebClient
    from slack_sdk.errors import SlackApiError
    _SLACK_AVAILABLE = True
except ImportError:
    AsyncWebClient = None  # type: ignore[assignment,misc]
    SlackApiError = Exception  # type: ignore[assignment,misc]
    _SLACK_AVAILABLE = False

from backend.config import settings
from backend.models.schemas import BriefingReport, SlackMessage

logger = logging.getLogger(__name__)


def _slack_client() -> "AsyncWebClient | None":
    if not _SLACK_AVAILABLE:
        logger.warning("slack_sdk not installed")
        return None
    if not settings.slack_bot_token:
        logger.warning("SLACK_BOT_TOKEN not set")
        return None
    return AsyncWebClient(token=settings.slack_bot_token)


async def get_channel_messages(channel_id: str, hours: int = 24) -> list[SlackMessage]:
    client = _slack_client()
    if client is None:
        return []
    oldest = str(time.time() - hours * 3600)
    try:
        resp = await client.conversations_history(
            channel=channel_id,
            oldest=oldest,
            limit=100,
        )
        messages = []
        for msg in resp.get("messages", []):
            # skip bot messages and subtypes
            if msg.get("subtype"):
                continue
            messages.append(
                SlackMessage(
                    user=msg.get("user", "unknown"),
                    text=msg.get("text", ""),
                    ts=msg.get("ts", ""),
                )
            )
        return messages
    except SlackApiError as e:
        logger.warning("Slack API error fetching messages: %s", e)
        return []


def _format_briefing(briefing: BriefingReport, team_name: str) -> str:
    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"*Daily Briefing: {team_name}* — {now}",
        "",
        f"*Summary*\n{briefing.summary}",
        "",
    ]
    if briefing.momentum:
        lines += [f"*Momentum*\n{briefing.momentum}", ""]
    if briefing.key_decisions:
        lines.append("*Key Decisions*")
        lines += [f"  • {d}" for d in briefing.key_decisions]
        lines.append("")
    if briefing.blockers:
        lines.append("*Blockers*")
        lines += [f"  :warning: {b}" for b in briefing.blockers]
        lines.append("")
    if briefing.action_items:
        lines.append("*Action Items*")
        lines += [f"  :white_check_mark: {a}" for a in briefing.action_items]
        lines.append("")
    return "\n".join(lines).strip()


async def post_digest(channel_id: str, briefing: BriefingReport, team_name: str = "Team") -> bool:
    client = _slack_client()
    if client is None:
        return False
    text = _format_briefing(briefing, team_name)
    try:
        await client.chat_postMessage(channel=channel_id, text=text, mrkdwn=True)
        logger.info("Digest posted to Slack channel %s", channel_id)
        return True
    except SlackApiError as e:
        logger.warning("Slack API error posting digest: %s", e)
        return False

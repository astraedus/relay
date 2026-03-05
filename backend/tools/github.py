from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

try:
    import httpx
except ImportError:
    httpx = None  # type: ignore[assignment]

from backend.config import settings
from backend.models.schemas import CommitInfo, IssueInfo, PRInfo, RepoActivity

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"


def _headers() -> dict[str, str]:
    h: dict[str, str] = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if settings.github_token:
        h["Authorization"] = f"Bearer {settings.github_token}"
    return h


def _cutoff_iso(hours: int) -> str:
    cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=hours)
    return cutoff.isoformat()


async def get_recent_prs(repo: str, hours: int = 24) -> list[PRInfo]:
    if httpx is None:
        logger.warning("httpx not installed; returning empty PR list")
        return []
    cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=hours)
    async with httpx.AsyncClient(headers=_headers(), timeout=15) as client:
        resp = await client.get(
            f"{GITHUB_API}/repos/{repo}/pulls",
            params={"state": "all", "sort": "updated", "direction": "desc", "per_page": 30},
        )
        if resp.status_code != 200:
            logger.warning("GitHub PRs %s → %d", repo, resp.status_code)
            return []
        data = resp.json()
    prs = []
    for item in data:
        updated = datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00"))
        if updated < cutoff:
            break
        prs.append(
            PRInfo(
                number=item["number"],
                title=item["title"],
                state=item["state"],
                author=item["user"]["login"],
                url=item["html_url"],
                updated_at=item["updated_at"],
            )
        )
    return prs


async def get_recent_commits(repo: str, hours: int = 24) -> list[CommitInfo]:
    if httpx is None:
        logger.warning("httpx not installed; returning empty commits list")
        return []
    since = _cutoff_iso(hours)
    async with httpx.AsyncClient(headers=_headers(), timeout=15) as client:
        resp = await client.get(
            f"{GITHUB_API}/repos/{repo}/commits",
            params={"since": since, "per_page": 30},
        )
        if resp.status_code != 200:
            logger.warning("GitHub commits %s → %d", repo, resp.status_code)
            return []
        data = resp.json()
    commits = []
    for item in data:
        commit = item.get("commit", {})
        author = commit.get("author", {})
        committer_login = (item.get("author") or {}).get("login", author.get("name", "unknown"))
        commits.append(
            CommitInfo(
                sha=item["sha"][:7],
                message=commit.get("message", "").split("\n")[0],
                author=committer_login,
                url=item.get("html_url", ""),
                committed_at=author.get("date", ""),
            )
        )
    return commits


async def get_recent_issues(repo: str, hours: int = 24) -> list[IssueInfo]:
    if httpx is None:
        logger.warning("httpx not installed; returning empty issues list")
        return []
    since = _cutoff_iso(hours)
    async with httpx.AsyncClient(headers=_headers(), timeout=15) as client:
        resp = await client.get(
            f"{GITHUB_API}/repos/{repo}/issues",
            params={"state": "all", "since": since, "per_page": 30},
        )
        if resp.status_code != 200:
            logger.warning("GitHub issues %s → %d", repo, resp.status_code)
            return []
        data = resp.json()
    issues = []
    for item in data:
        # issues endpoint also returns PRs; skip those
        if "pull_request" in item:
            continue
        issues.append(
            IssueInfo(
                number=item["number"],
                title=item["title"],
                state=item["state"],
                author=item["user"]["login"],
                url=item["html_url"],
                updated_at=item["updated_at"],
            )
        )
    return issues


async def get_repo_activity(repo: str, hours: int = 24) -> RepoActivity:
    prs = await get_recent_prs(repo, hours)
    commits = await get_recent_commits(repo, hours)
    issues = await get_recent_issues(repo, hours)
    return RepoActivity(repo=repo, prs=prs, commits=commits, issues=issues)

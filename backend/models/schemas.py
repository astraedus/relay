from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


# ---- GitHub activity ----

class PRInfo(BaseModel):
    number: int
    title: str
    state: str
    author: str
    url: str
    updated_at: str


class CommitInfo(BaseModel):
    sha: str
    message: str
    author: str
    url: str
    committed_at: str


class IssueInfo(BaseModel):
    number: int
    title: str
    state: str
    author: str
    url: str
    updated_at: str


class RepoActivity(BaseModel):
    repo: str
    prs: list[PRInfo] = []
    commits: list[CommitInfo] = []
    issues: list[IssueInfo] = []


# ---- Slack ----

class SlackMessage(BaseModel):
    user: str
    text: str
    ts: str


# ---- Briefing ----

class BriefingReport(BaseModel):
    summary: str
    key_decisions: list[str] = []
    blockers: list[str] = []
    momentum: str = ""
    action_items: list[str] = []


# ---- API request/response ----

class GenerateRequest(BaseModel):
    workspace_id: int | None = None
    team_name: str = "Team"
    github_repos: list[str] = []
    slack_channel_id: str = ""
    hours: int = 24


class GenerateResponse(BaseModel):
    briefing_id: int
    status: str
    report: BriefingReport | None = None


# ---- DB row shapes ----

class WorkspaceRow(BaseModel):
    id: int
    name: str
    github_repos: list[str]
    slack_channel_id: str
    schedule: str
    created_at: str


class BriefingRow(BaseModel):
    id: int
    workspace_id: int | None
    team_name: str
    content: dict[str, Any]
    created_at: str

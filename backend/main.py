from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.agents.briefing import synthesize_briefing
from backend.config import settings
from backend.db.database import (
    get_briefing,
    get_briefings,
    get_workspaces,
    init_db,
    save_briefing,
    save_workspace,
)
from backend.models.schemas import GenerateRequest, GenerateResponse
from backend.tools.github import get_repo_activity
from backend.tools.slack import get_channel_messages, post_digest

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("Relay started (mock_mode=%s)", settings.use_mock)
    yield
    logger.info("Relay shutting down")


app = FastAPI(title="Relay", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_briefing(req: GenerateRequest) -> GenerateResponse:
    """Trigger briefing generation for given repos and Slack channel."""
    # Gather GitHub activity
    repo_activities = []
    for repo in req.github_repos:
        activity = await get_repo_activity(repo, hours=req.hours)
        repo_activities.append(activity)

    # Gather Slack messages
    slack_messages = []
    if req.slack_channel_id:
        slack_messages = await get_channel_messages(req.slack_channel_id, hours=req.hours)

    # Synthesize
    report = await synthesize_briefing(
        repo_activities=repo_activities,
        slack_messages=slack_messages,
        team_name=req.team_name,
        hours=req.hours,
    )

    # Persist
    briefing_id = await save_briefing(
        team_name=req.team_name,
        content=report.model_dump(),
        workspace_id=req.workspace_id,
    )

    # Optionally post to Slack
    if req.slack_channel_id:
        posted = await post_digest(req.slack_channel_id, report, req.team_name)
        logger.info("Slack digest posted=%s", posted)

    return GenerateResponse(briefing_id=briefing_id, status="done", report=report)


@app.get("/api/briefings")
async def list_briefings(limit: int = 20) -> list[dict]:
    return await get_briefings(limit=min(limit, 100))


@app.get("/api/briefings/{briefing_id}")
async def get_briefing_detail(briefing_id: int) -> dict:
    row = await get_briefing(briefing_id)
    if not row:
        raise HTTPException(status_code=404, detail="Briefing not found")
    return row


@app.get("/api/workspaces")
async def list_workspaces() -> list[dict]:
    return await get_workspaces()


@app.post("/api/workspaces")
async def create_workspace(
    name: str,
    github_repos: list[str] | None = None,
    slack_channel_id: str = "",
    schedule: str = "daily",
) -> dict:
    workspace_id = await save_workspace(
        name=name,
        github_repos=github_repos or [],
        slack_channel_id=slack_channel_id,
        schedule=schedule,
    )
    return {"id": workspace_id, "name": name}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "relay", "mock_mode": str(settings.use_mock)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=settings.port, reload=True)

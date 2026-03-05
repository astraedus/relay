# DevPost Submission — Relay

## Title
Relay

## Tagline
AI-powered daily briefings for engineering teams, built entirely on DigitalOcean.

## Inspiration
Engineering teams ship code all day. By end of week, nobody has a clear picture of what changed, what broke, and what needs attention. Stand-ups miss things. Slack scrollback is overwhelming. Managers ask "what did we ship?" and engineers spend 30 minutes writing status updates instead of building.

Relay automates that. One AI-generated briefing per day — or on demand — that captures everything that matters from GitHub and Slack.

## What It Does

Relay connects to your GitHub repositories and Slack channels. When triggered (manually or on a daily schedule), it:

1. **Fetches GitHub activity**: recent pull requests, commits, and open issues from the last 24 hours
2. **Fetches Slack activity**: recent messages from the team channel
3. **Synthesizes with DigitalOcean Gradient AI**: a structured briefing with summary, key decisions, open blockers, momentum signals, and action items
4. **Posts to Slack**: the briefing lands in the team channel automatically

The dashboard shows briefing history. Any team member can click "Generate Now" to get an instant briefing on demand.

## How We Built It

**DigitalOcean Gradient AI** is the AI brain. We use the OpenAI-compatible inference API (`https://inference.do-ai.run/v1/`) with Llama 3 8B Instruct to synthesize raw GitHub + Slack data into a structured JSON briefing. Gradient AI's serverless model means zero GPU management — it just scales.

**FastAPI** handles the backend: briefing generation endpoint, workspace management, and briefing history API.

**GitHub API** (via httpx) fetches recent PRs, commits, and issues for configured repos.

**Slack SDK** reads channel messages and posts briefings back to the team.

**SQLite** (local dev) / **DigitalOcean Managed Postgres** (prod) stores workspaces and briefing history.

**Next.js 15** provides the dashboard: briefing list, generate button, workspace configuration.

**DigitalOcean App Platform** hosts everything — backend + frontend in a single app spec (.do/app.yaml).

## Challenges

Getting Gradient AI to reliably produce structured JSON briefings required careful prompt engineering. The model needed explicit schema instructions to consistently output the `summary`, `key_decisions`, `blockers`, `momentum`, and `action_items` fields we needed for the UI.

Building graceful degradation across three modes (DO Gradient AI → Anthropic → mock) meant the app works in any configuration — handy for development before credentials are set up.

## Accomplishments

- End-to-end briefing pipeline: GitHub + Slack in, Slack briefing out, no human in the loop
- Works with any GitHub repository (no installation required — just a personal access token)
- 100% deployed on DigitalOcean: App Platform (backend + frontend) + Gradient AI + Managed Postgres
- Mock mode: the full app runs without any API keys, making it easy to demo the UI

## What We Learned

DigitalOcean Gradient AI's OpenAI-compatible API makes it drop-in easy to swap from any other provider. The inference endpoint is fast — Llama 3 8B produces a full briefing in under 5 seconds for a typical day's worth of activity.

## What's Next

- Scheduled daily briefings (cron-triggered, zero human interaction)
- GitHub Actions integration: post a Relay briefing on every merge to main
- Multi-workspace support: one Relay instance, multiple teams
- Custom briefing templates per team (different fields for platform teams vs. product teams)

## Built With

- digitalocean-gradient-ai
- fastapi
- python
- next.js
- github-api
- slack-sdk
- sqlite
- aiosqlite
- httpx
- openai (SDK — used to call Gradient AI's OpenAI-compatible endpoint)

## Links

- GitHub: https://github.com/astraedus/relay
- Demo video: [coming]

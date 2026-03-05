# Relay Demo Narration Script
# Voice: en-US-JennyNeural (female)
# Target: 90-120 seconds
# Platform: DigitalOcean Gradient AI Hackathon

---

## SECTION 1: Hook (0-10s)
Your team ships code all day. By end of week, nobody has a clear picture of what changed, what broke, and what needs attention.
Relay fixes that. One AI-generated briefing per day, automatically.

## SECTION 2: What It Is (10-25s)
Relay connects to your GitHub repos and Slack channels.
Every day — or on demand — it pulls recent pull requests, commits, issues, and team messages.
Then DigitalOcean Gradient AI synthesizes everything into a structured briefing.
Summary, decisions, blockers, momentum, action items. In seconds.

## SECTION 3: Live Demo (25-70s)
Here is Relay connected to the astraedus GitHub org.
[click Generate Briefing]
Relay is now pulling activity from the last 24 hours — commits, pull requests, issues.
[loading animation plays]
And here is the briefing.
[briefing appears]
The summary captures what changed. Key decisions are surfaced from PR descriptions and merge activity.
Open blockers are listed from issue comments. Action items are concrete and ranked.
This is powered by DigitalOcean Gradient AI serverless inference — no GPU to manage, scales automatically.

## SECTION 4: Where It Runs (70-95s)
Relay is deployed entirely on DigitalOcean.
The backend runs on App Platform. The database is DigitalOcean Managed Postgres.
Inference is handled by Gradient AI.
One platform. No infrastructure management.

## SECTION 5: Close (95-110s)
Relay is open source, connects to any GitHub repo, and delivers briefings to Slack or email.
Built on DigitalOcean from day one.

---
# Recording notes:
# - Start backend: source venv/bin/activate && uvicorn backend.main:app --port 8000
# - Start frontend: cd frontend && npm run dev -- --port 3001
# - Use real GitHub token pointing to astraedus/relay + astraedus/devpilot repos
# - Show the "Generate Now" button → loading → briefing appearing
# - Mock Slack if needed (SLACK_BOT_TOKEN empty = skip Slack section gracefully)
# - Capture 2-3 generated briefings in history list for visual depth

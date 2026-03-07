# Relay

Async team briefing agent. Connects to GitHub repos and Slack workspaces, extracts recent activity, and uses Claude to synthesize a daily digest delivered to Slack or email.

Built for the DigitalOcean Gradient AI Hackathon (March 2026, $20K prize).

## Hackathon Submissions

| Hackathon | Platform | Track | Status |
|-----------|----------|-------|--------|
| [DigitalOcean Gradient AI 2026](https://digitalocean.devpost.com/) | DevPost | Open | BLOCKED -- DO_MODEL_ACCESS_KEY requires payment method (card rejected). Deadline March 18. |

**Special adaptations**: Multi-tier AI fallback (DO Gradient AI -> Anthropic -> Mock) so app works without DO key. DevPost registered as participant #2251.

## Stack

- **Backend**: Python FastAPI + aiosqlite
- **AI**: DigitalOcean Gradient AI serverless inference (Llama 3 8B — primary) + Gemini fallback (free)
- **GitHub**: httpx + GitHub REST API
- **Slack**: slack-sdk
- **Frontend**: Next.js 15 + dark theme
- **Deploy**: DigitalOcean App Platform

## Local Setup

### Backend

```bash
cd /home/astraedus/projects/relay
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

cp .env.example .env
# Edit .env and add your API keys

uvicorn backend.main:app --reload
# Runs on http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
# Runs on http://localhost:3001
```

## API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/generate` | Generate a briefing |
| GET | `/api/briefings` | List all briefings |
| GET | `/api/briefings/{id}` | Get a specific briefing |
| GET | `/api/workspaces` | List workspaces |
| POST | `/api/workspaces` | Create a workspace |
| GET | `/health` | Health check |

### Generate Example

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "team_name": "Backend Team",
    "github_repos": ["owner/repo"],
    "slack_channel_id": "C0123456789",
    "hours": 24
  }'
```

## Deploy (DigitalOcean)

```bash
doctl apps create --spec .do/app.yaml
```

Set secrets via the DO dashboard or:

```bash
doctl apps update <app-id> --set-env ANTHROPIC_API_KEY=sk-ant-...
```

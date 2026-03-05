# Relay — Project Lessons

## Setup

- Python venv at `/home/astraedus/projects/relay/venv/`
- Run backend: `cd /home/astraedus/projects/relay && venv/bin/uvicorn backend.main:app --reload`
- Run frontend: `cd /home/astraedus/projects/relay/frontend && npm run dev`
- Smoke test (no server needed): `venv/bin/python3 -c "from backend.db.database import init_db; import asyncio; asyncio.run(init_db())"` then use TestClient

## AI Routing

- DO Gradient AI is PRIMARY (required for hackathon eligibility) — OpenAI-compatible endpoint at `https://inference.do-ai.run/v1/`
- Anthropic is FALLBACK
- Mock is last resort (when neither key is set)
- `settings.use_mock` is True when both `do_model_access_key` and `anthropic_api_key` are empty

## SQLite / DB

- DB lives at `relay.db` (cwd-relative) — TestClient does NOT run lifespan, so call `init_db()` manually before tests
- `cursor.lastrowid` can be None if insert fails silently — check for errors

## Frontend

- Same dark theme pattern as DevPilot: `#0a0a0a` bg, `#141414` cards, `#222` borders
- Accent color for Relay is `#7c6af7` (purple) vs DevPilot's `#5b9cf6` (blue)
- `npx tsc --noEmit` from frontend/ to type-check

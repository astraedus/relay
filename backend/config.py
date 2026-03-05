from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # DigitalOcean Gradient AI (primary — required for hackathon)
    # Get from: cloud.digitalocean.com → AI → API Keys
    do_model_access_key: str = ""
    do_inference_base_url: str = "https://inference.do-ai.run/v1/"
    do_model: str = "llama3-8b-instruct"

    # Gemini (fallback if DO not configured — free tier via OpenAI-compatible endpoint)
    gemini_api_key: str = ""

    # GitHub
    github_token: str = ""

    # Slack
    slack_bot_token: str = ""

    # Database — SQLite by default, swap to postgres:// in prod
    database_url: str = "relay.db"

    # App
    port: int = 8000
    log_level: str = "INFO"
    mock_mode: bool = False

    class Config:
        env_file = ".env"

    @property
    def use_mock(self) -> bool:
        return self.mock_mode or (not self.do_model_access_key and not self.gemini_api_key)

    @property
    def use_do_gradient(self) -> bool:
        return bool(self.do_model_access_key)


settings = Settings()

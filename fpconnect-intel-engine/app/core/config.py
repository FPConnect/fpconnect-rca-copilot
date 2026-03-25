from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    database_url: str = Field(..., alias='DATABASE_URL')
    sources_yaml: str = Field('/app/sources.yaml', alias='SOURCES_YAML')
    poll_interval_seconds: int = Field(900, alias='POLL_INTERVAL_SECONDS')
    app_lang: str = Field('bilingual', alias='APP_LANG')

    # Optional
    openai_api_key: str | None = Field(default=None, alias='OPENAI_API_KEY')
    github_token: str | None = Field(default=None, alias='GITHUB_TOKEN')
    github_repo: str | None = Field(default=None, alias='GITHUB_REPO')

    class Config:
        case_sensitive = False

settings = Settings()

from __future__ import annotations

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SPEAK_TO_USER_DEV_",
        env_file=(REPO_ROOT / ".env", REPO_ROOT / ".env.local"),
        extra="ignore",
    )

    host: str = "127.0.0.1"
    port: int = 7461
    mcp_path: str = "/mcp"
    log_level: str = "INFO"
    workspace_root: Path = Field(default=REPO_ROOT.parent / "speak-to-user")
    default_owner: str = "codex"
    server_name: str = "speak-to-user-dev"

    @field_validator("workspace_root", mode="before")
    @classmethod
    def expand_path(cls, value: object) -> object:
        path = Path(str(value)).expanduser()
        if path.is_absolute():
            return path.resolve()
        return (REPO_ROOT / path).resolve()

    @field_validator("mcp_path")
    @classmethod
    def normalize_path(cls, value: str) -> str:
        if not value.startswith("/"):
            return f"/{value}"
        return value

    def repo_relative(self, path: Path) -> str:
        try:
            return str(path.relative_to(REPO_ROOT))
        except ValueError:
            return str(path)

from __future__ import annotations

from pathlib import Path

from speak_to_user_dev.settings import REPO_ROOT, Settings


def make_settings(**overrides: object) -> Settings:
    return Settings(_env_file=(), **overrides)  # type: ignore[call-arg,arg-type]


def test_settings_expand_relative_workspace_root() -> None:
    settings = make_settings(workspace_root=Path("../speak-to-user"))
    assert settings.workspace_root == REPO_ROOT.parent / "speak-to-user"


def test_settings_normalize_mcp_path() -> None:
    settings = make_settings(mcp_path="queue")
    assert settings.mcp_path == "/queue"


def test_repo_relative_falls_back_for_external_path() -> None:
    settings = make_settings()
    assert settings.repo_relative(Path("/tmp/example")) == "/tmp/example"

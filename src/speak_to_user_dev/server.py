from __future__ import annotations

import logging

from fastmcp import FastMCP

from .coordinator import WorkspaceCoordinator
from .prompts import register_prompts
from .resources import register_resources
from .settings import Settings
from .tools import register_tools


def configure_logging(settings: Settings) -> None:
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def create_server(settings: Settings | None = None) -> tuple[FastMCP, WorkspaceCoordinator]:
    resolved = settings or Settings()
    coordinator = WorkspaceCoordinator(resolved)
    mcp = FastMCP(
        name=resolved.server_name,
        instructions=(
            "Local FastMCP coordinator for multi-repo speak-to-user development work. "
            "It serializes heavy or risky workflows into named lanes, exposes queue state "
            "through tools and resources, and is intended to grow into an execution-aware "
            "operator surface for docs sweeps, submodule pin bumps, and heavyweight test runs."
        ),
    )
    register_tools(mcp, coordinator)
    register_prompts(mcp)
    register_resources(mcp, coordinator, resolved)
    return mcp, coordinator


def main() -> None:
    settings = Settings()
    configure_logging(settings)
    server, _ = create_server(settings)
    server.run(
        transport="streamable-http",
        host=settings.host,
        port=settings.port,
        path=settings.mcp_path,
        show_banner=False,
    )

from __future__ import annotations

import json

from fastmcp import FastMCP

from .coordinator import WorkspaceCoordinator
from .settings import Settings


def register_resources(mcp: FastMCP, coordinator: WorkspaceCoordinator, settings: Settings) -> None:
    @mcp.resource(
        "dev://status",
        name="status_resource",
        description="Read the current coordinator health and queue totals.",
        mime_type="application/json",
    )
    def status_resource() -> str:
        return coordinator.status().model_dump_json(indent=2)

    @mcp.resource(
        "dev://lanes",
        name="lanes_resource",
        description="Read the configured coordination lanes and their current snapshots.",
        mime_type="application/json",
    )
    def lanes_resource() -> str:
        payload = {
            "definitions": [lane.model_dump(mode="json") for lane in coordinator.list_lanes()],
            "snapshots": [
                snapshot.model_dump(mode="json") for snapshot in coordinator.snapshot_lanes()
            ],
        }
        return json.dumps(payload, indent=2)

    @mcp.resource(
        "dev://requests",
        name="requests_resource",
        description="Read every known queued, running, completed, or canceled request.",
        mime_type="application/json",
    )
    def requests_resource() -> str:
        payload = [request.model_dump(mode="json") for request in coordinator.list_requests()]
        return json.dumps(payload, indent=2)

    @mcp.resource(
        "dev://runtime",
        name="runtime_resource",
        description="Read the effective runtime configuration for this coordinator service.",
        mime_type="application/json",
    )
    def runtime_resource() -> str:
        payload = {
            "host": settings.host,
            "port": settings.port,
            "mcp_path": settings.mcp_path,
            "workspace_root": str(settings.workspace_root),
            "default_owner": settings.default_owner,
            "log_level": settings.log_level,
        }
        return json.dumps(payload, indent=2)

    @mcp.resource(
        "dev://requests/{request_id}",
        name="request_detail_resource",
        description="Read one queued or historical coordination request by id.",
        mime_type="application/json",
    )
    def request_detail_resource(request_id: str) -> str:
        request = next(
            (
                item
                for item in coordinator.list_requests()
                if item.request_id == request_id
            ),
            None,
        )
        if request is None:
            raise ValueError(
                f"Unknown request '{request_id}'. Use dev://requests to inspect known request ids."
            )
        return request.model_dump_json(indent=2)

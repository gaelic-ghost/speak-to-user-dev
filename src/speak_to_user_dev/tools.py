from __future__ import annotations

from fastmcp import FastMCP

from .coordinator import WorkspaceCoordinator
from .models import LaneDefinition, QueueTaskResult, StatusResult, TaskRecord


def register_tools(mcp: FastMCP, coordinator: WorkspaceCoordinator) -> None:
    @mcp.tool(
        name="status",
        description="Report queue totals, runtime configuration, and current coordinator health.",
    )
    def status() -> StatusResult:
        return coordinator.status()

    @mcp.tool(
        name="list_lanes",
        description="List the available coordination lanes for local dev work.",
    )
    def list_lanes() -> list[LaneDefinition]:
        return coordinator.list_lanes()

    @mcp.tool(
        name="list_requests",
        description=(
            "List queued or historical coordination requests, optionally filtered by lane "
            "or status."
        ),
    )
    def list_requests(
        lane: str | None = None,
        status: str | None = None,
    ) -> list[TaskRecord]:
        return coordinator.list_requests(lane=lane, status=status)

    @mcp.tool(
        name="queue_task",
        description=(
            "Queue a coordination request into one serial lane without executing it yet. "
            "Use this to reserve heavy local-dev work before an execution layer exists."
        ),
    )
    async def queue_task(
        lane: str,
        title: str,
        owner: str,
        description: str | None = None,
        command: list[str] | None = None,
        metadata: dict[str, str] | None = None,
    ) -> QueueTaskResult:
        return await coordinator.queue_task(
            lane=lane,
            title=title,
            owner=owner,
            description=description,
            command=command,
            metadata=metadata,
        )

    @mcp.tool(
        name="start_next_task",
        description="Promote the next queued request in a lane into the active running slot.",
    )
    async def start_next_task(lane: str) -> TaskRecord:
        return await coordinator.start_next_task(lane)

    @mcp.tool(
        name="complete_task",
        description="Mark a running request as completed and free its lane for the next task.",
    )
    async def complete_task(
        request_id: str,
        outcome: str | None = None,
    ) -> TaskRecord:
        return await coordinator.complete_task(request_id, outcome=outcome)

    @mcp.tool(
        name="cancel_task",
        description="Cancel a queued or running request and record why it was abandoned.",
    )
    async def cancel_task(
        request_id: str,
        outcome: str | None = None,
    ) -> TaskRecord:
        return await coordinator.cancel_task(request_id, outcome=outcome)

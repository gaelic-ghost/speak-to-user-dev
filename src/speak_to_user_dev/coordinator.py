from __future__ import annotations

import asyncio
from collections import deque
from uuid import uuid4

from .models import LaneDefinition, LaneSnapshot, QueueTaskResult, StatusResult, TaskRecord, utc_now
from .settings import Settings


class WorkspaceCoordinator:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._lanes = {
            lane.lane: lane
            for lane in [
                LaneDefinition(
                    lane="heavy-e2e",
                    title="Heavy End-to-End",
                    description=(
                        "Serialize heavyweight end-to-end runs so local Apple and Python "
                        "toolchains do not stampede Gale's machine."
                    ),
                ),
                LaneDefinition(
                    lane="docs-sync",
                    title="Cross-Repo Docs",
                    description=(
                        "Queue README, roadmap, and release-note sweeps that need consistent "
                        "wording across multiple speak-to-user repositories."
                    ),
                ),
                LaneDefinition(
                    lane="submodule-pins",
                    title="Submodule Pins",
                    description=(
                        "Coordinate umbrella monorepo submodule bumps so pin updates stay "
                        "narrow, reviewable, and intentionally verified."
                    ),
                ),
                LaneDefinition(
                    lane="release-train",
                    title="Release Train",
                    description=(
                        "Reserve cross-repo release work such as tagging, changelog sync, and "
                        "post-release verification."
                    ),
                ),
            ]
        }
        self._queued: dict[str, deque[TaskRecord]] = {lane: deque() for lane in self._lanes}
        self._active: dict[str, TaskRecord | None] = {lane: None for lane in self._lanes}
        self._completed: dict[str, list[TaskRecord]] = {lane: [] for lane in self._lanes}
        self._canceled: dict[str, list[TaskRecord]] = {lane: [] for lane in self._lanes}
        self._requests: dict[str, TaskRecord] = {}
        self._lock = asyncio.Lock()

    def list_lanes(self) -> list[LaneDefinition]:
        return list(self._lanes.values())

    async def queue_task(
        self,
        *,
        lane: str,
        title: str,
        owner: str,
        description: str | None = None,
        command: list[str] | None = None,
        metadata: dict[str, str] | None = None,
    ) -> QueueTaskResult:
        async with self._lock:
            self._require_lane(lane)
            request = TaskRecord(
                request_id=f"req-{uuid4().hex[:12]}",
                lane=lane,
                title=title,
                owner=owner,
                description=description,
                status="queued",
                command=command or [],
                metadata=metadata or {},
            )
            self._queued[lane].append(request)
            self._requests[request.request_id] = request
            return QueueTaskResult(
                request_id=request.request_id,
                lane=lane,
                status=request.status,
                queue_position=len(self._queued[lane]),
                owner=request.owner,
                title=request.title,
            )

    async def start_next_task(self, lane: str) -> TaskRecord:
        async with self._lock:
            self._require_lane(lane)
            if self._active[lane] is not None:
                active = self._active[lane]
                assert active is not None
                raise ValueError(
                    f"Lane '{lane}' already has an active request: {active.request_id}."
                )
            if not self._queued[lane]:
                raise ValueError(f"Lane '{lane}' does not have a queued request to start.")
            request = self._queued[lane].popleft()
            request.status = "running"
            request.started_at = utc_now()
            self._active[lane] = request
            self._requests[request.request_id] = request
            return request

    async def complete_task(self, request_id: str, outcome: str | None = None) -> TaskRecord:
        async with self._lock:
            request = self._require_request(request_id)
            if request.status != "running":
                raise ValueError(
                    f"Request '{request_id}' is not running, so it cannot be completed."
                )
            request.status = "completed"
            request.finished_at = utc_now()
            request.outcome = outcome
            self._active[request.lane] = None
            self._completed[request.lane].append(request)
            return request

    async def cancel_task(self, request_id: str, outcome: str | None = None) -> TaskRecord:
        async with self._lock:
            request = self._require_request(request_id)
            if request.status == "completed":
                raise ValueError(
                    f"Request '{request_id}' is already completed and cannot be canceled."
                )

            if request.status == "queued":
                self._remove_queued_request(request)
            elif request.status == "running":
                self._active[request.lane] = None

            request.status = "canceled"
            request.finished_at = utc_now()
            request.outcome = outcome
            self._canceled[request.lane].append(request)
            return request

    def list_requests(
        self,
        *,
        lane: str | None = None,
        status: str | None = None,
    ) -> list[TaskRecord]:
        requests = list(self._requests.values())
        if lane is not None:
            self._require_lane(lane)
            requests = [request for request in requests if request.lane == lane]
        if status is not None:
            requests = [request for request in requests if request.status == status]
        return sorted(requests, key=lambda request: request.created_at)

    def snapshot_lanes(self) -> list[LaneSnapshot]:
        return [
            LaneSnapshot(
                lane=lane,
                sequential=self._lanes[lane].sequential,
                active_request=self._active[lane],
                queued_requests=list(self._queued[lane]),
                completed_requests=list(self._completed[lane]),
                canceled_requests=list(self._canceled[lane]),
            )
            for lane in self._lanes
        ]

    def status(self) -> StatusResult:
        queued_count = sum(len(queue) for queue in self._queued.values())
        running_count = sum(1 for request in self._active.values() if request is not None)
        completed_count = sum(len(items) for items in self._completed.values())
        canceled_count = sum(len(items) for items in self._canceled.values())
        return StatusResult(
            server_name=self._settings.server_name,
            workspace_root=str(self._settings.workspace_root),
            host=self._settings.host,
            port=self._settings.port,
            mcp_path=self._settings.mcp_path,
            default_owner=self._settings.default_owner,
            lane_count=len(self._lanes),
            queued_request_count=queued_count,
            running_request_count=running_count,
            completed_request_count=completed_count,
            canceled_request_count=canceled_count,
        )

    def _require_lane(self, lane: str) -> None:
        if lane not in self._lanes:
            known_lanes = ", ".join(sorted(self._lanes))
            raise ValueError(
                f"Unknown lane '{lane}'. Known lanes are: {known_lanes}."
            )

    def _require_request(self, request_id: str) -> TaskRecord:
        try:
            return self._requests[request_id]
        except KeyError as error:
            raise ValueError(
                f"Unknown request '{request_id}'. Use list_requests to inspect the current queue."
            ) from error

    def _remove_queued_request(self, request: TaskRecord) -> None:
        lane_queue = self._queued[request.lane]
        for queued_request in list(lane_queue):
            if queued_request.request_id == request.request_id:
                lane_queue.remove(queued_request)
                return

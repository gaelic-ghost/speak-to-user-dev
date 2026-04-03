from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(UTC)


TaskStatus = Literal["queued", "running", "completed", "canceled"]


class LaneDefinition(BaseModel):
    lane: str
    title: str
    description: str
    sequential: bool = True


class QueueTaskResult(BaseModel):
    request_id: str
    lane: str
    status: TaskStatus
    queue_position: int
    owner: str
    title: str


class TaskRecord(BaseModel):
    request_id: str
    lane: str
    title: str
    owner: str
    status: TaskStatus
    description: str | None = None
    command: list[str] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)
    started_at: datetime | None = None
    finished_at: datetime | None = None
    outcome: str | None = None


class LaneSnapshot(BaseModel):
    lane: str
    sequential: bool
    active_request: TaskRecord | None
    queued_requests: list[TaskRecord]
    completed_requests: list[TaskRecord]
    canceled_requests: list[TaskRecord]


class StatusResult(BaseModel):
    server_name: str
    workspace_root: str
    host: str
    port: int
    mcp_path: str
    default_owner: str
    lane_count: int
    queued_request_count: int
    running_request_count: int
    completed_request_count: int
    canceled_request_count: int


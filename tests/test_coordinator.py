from __future__ import annotations

import pytest

from speak_to_user_dev.coordinator import WorkspaceCoordinator
from speak_to_user_dev.settings import Settings


def make_settings(**overrides: object) -> Settings:
    return Settings(_env_file=(), **overrides)  # type: ignore[call-arg,arg-type]


@pytest.mark.asyncio
async def test_queue_start_complete_flow() -> None:
    coordinator = WorkspaceCoordinator(make_settings())

    queued = await coordinator.queue_task(
        lane="heavy-e2e",
        title="Run SpeakSwiftlyServer e2e suite",
        owner="codex",
    )

    assert queued.queue_position == 1
    running = await coordinator.start_next_task("heavy-e2e")
    assert running.request_id == queued.request_id
    assert running.status == "running"

    completed = await coordinator.complete_task(running.request_id, outcome="passed")
    assert completed.status == "completed"
    assert completed.outcome == "passed"
    assert coordinator.status().completed_request_count == 1


@pytest.mark.asyncio
async def test_cannot_start_when_lane_is_busy() -> None:
    coordinator = WorkspaceCoordinator(make_settings())

    first = await coordinator.queue_task(
        lane="submodule-pins",
        title="Pin speak-to-user-dev",
        owner="codex",
    )
    await coordinator.queue_task(
        lane="submodule-pins",
        title="Pin SpeakSwiftlyServer",
        owner="codex",
    )
    await coordinator.start_next_task("submodule-pins")

    with pytest.raises(ValueError, match="already has an active request"):
        await coordinator.start_next_task("submodule-pins")

    canceled = await coordinator.cancel_task(first.request_id, outcome="no longer needed")
    assert canceled.status == "canceled"


def test_unknown_lane_error_is_descriptive() -> None:
    coordinator = WorkspaceCoordinator(make_settings())

    with pytest.raises(ValueError, match="Known lanes are"):
        coordinator.list_requests(lane="not-a-lane")

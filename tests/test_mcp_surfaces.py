from __future__ import annotations

import json
from typing import Any

import pytest
from fastmcp import Client

from speak_to_user_dev.server import create_server
from speak_to_user_dev.settings import Settings


def make_settings(**overrides: object) -> Settings:
    return Settings(_env_file=(), **overrides)  # type: ignore[call-arg,arg-type]


def result_payload(result: Any) -> dict[str, Any]:
    data = getattr(result, "data", None)
    model_dump = getattr(data, "model_dump", None)
    if callable(model_dump):
        return dict(model_dump())
    if isinstance(data, dict):
        return data

    structured = getattr(result, "structured_content", None)
    if isinstance(structured, dict):
        return structured

    raise AssertionError(f"Tool result did not expose structured content: {result!r}")


@pytest.mark.asyncio
async def test_create_server_registers_expected_surfaces() -> None:
    mcp, _ = create_server(make_settings())

    tool_names = {tool.name for tool in await mcp.list_tools()}
    prompt_names = {prompt.name for prompt in await mcp.list_prompts()}
    resource_uris = {str(resource.uri) for resource in await mcp.list_resources()}
    resource_templates = {
        template.uri_template for template in await mcp.list_resource_templates()
    }

    assert {
        "status",
        "list_lanes",
        "list_requests",
        "queue_task",
        "start_next_task",
        "complete_task",
        "cancel_task",
    } <= tool_names
    assert {
        "draft_docs_sync_plan",
        "draft_submodule_pin_checklist",
        "draft_heavy_e2e_request",
    } <= prompt_names
    assert {
        "dev://status",
        "dev://lanes",
        "dev://requests",
        "dev://runtime",
    } <= resource_uris
    assert "dev://requests/{request_id}" in resource_templates


@pytest.mark.asyncio
async def test_client_can_queue_and_read_request_state() -> None:
    mcp, _ = create_server(make_settings())

    async with Client(mcp) as client:
        initial_status = await client.call_tool("status")
        status_payload = result_payload(initial_status)
        assert status_payload["queued_request_count"] == 0

        queued = await client.call_tool(
            "queue_task",
            {
                "lane": "docs-sync",
                "title": "Update roadmap wording",
                "owner": "codex",
                "description": "Keep sibling repos aligned after bootstrap.",
                "metadata": {"scope": "workspace-docs"},
            },
        )
        request_id = result_payload(queued)["request_id"]

        requests_resource = await client.read_resource("dev://requests")
        requests_payload = json.loads(requests_resource[0].text)
        assert requests_payload[0]["request_id"] == request_id
        assert requests_payload[0]["lane"] == "docs-sync"

        detail_resource = await client.read_resource(f"dev://requests/{request_id}")
        detail_payload = json.loads(detail_resource[0].text)
        assert detail_payload["metadata"] == {"scope": "workspace-docs"}

        prompt = await client.get_prompt(
            "draft_submodule_pin_checklist",
            {
                "submodule_path": "mcps/speak-to-user-dev",
                "target_revision": "main@deadbeef",
                "validation_notes": "confirm docs and pin match",
            },
        )
        assert "mcps/speak-to-user-dev" in prompt.messages[0].content.text

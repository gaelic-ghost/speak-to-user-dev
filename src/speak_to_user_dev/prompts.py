from __future__ import annotations

from fastmcp import FastMCP


def register_prompts(mcp: FastMCP) -> None:
    @mcp.prompt(
        name="draft_docs_sync_plan",
        description="Draft a cross-repo docs update plan for a queued workspace task.",
    )
    def draft_docs_sync_plan(
        repositories: str,
        change_summary: str,
        rollout_risk: str,
    ) -> str:
        return (
            "Draft a concise cross-repo documentation change plan.\n"
            f"Repositories: {repositories}\n"
            f"Requested change: {change_summary}\n"
            f"Rollout risk to watch: {rollout_risk}\n"
            "Cover README alignment, roadmap updates, release-note impacts, and the exact "
            "verification steps needed before any doc sweep lands."
        )

    @mcp.prompt(
        name="draft_submodule_pin_checklist",
        description=(
            "Draft a careful checklist for bumping a submodule pin in the umbrella "
            "monorepo."
        ),
    )
    def draft_submodule_pin_checklist(
        submodule_path: str,
        target_revision: str,
        validation_notes: str,
    ) -> str:
        return (
            "Draft a narrow, reviewable submodule pin bump checklist.\n"
            f"Submodule path: {submodule_path}\n"
            f"Target revision: {target_revision}\n"
            f"Validation notes: {validation_notes}\n"
            "Keep the checklist focused on exact pin verification, umbrella docs alignment, "
            "and PR-ready review notes."
        )

    @mcp.prompt(
        name="draft_heavy_e2e_request",
        description="Draft a queue request for a heavyweight sequential test run.",
    )
    def draft_heavy_e2e_request(
        repository: str,
        test_target: str,
        reason: str,
    ) -> str:
        return (
            "Draft a queue request for the heavy-e2e lane.\n"
            f"Repository: {repository}\n"
            f"Target test or suite: {test_target}\n"
            f"Why it needs serialization: {reason}\n"
            "Include the owner, expected machine impact, and the success signal that should be "
            "recorded when the run completes."
        )

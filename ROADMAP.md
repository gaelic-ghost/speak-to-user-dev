# ROADMAP

## Milestone 1: Bootstrap The Coordinator

- [x] Create the initial FastMCP service scaffold with Streamable HTTP transport.
- [x] Add typed `pydantic-settings` configuration with committed safe defaults and gitignored local overrides.
- [x] Define the initial serial coordination lanes for heavyweight e2e runs, docs sync, submodule pinning, and release chores.
- [x] Expose the first tool, prompt, and resource surfaces for queue lifecycle management.
- [x] Add baseline tests, linting, and type-checking for the scaffold.

## Milestone 2: Real Queue Execution

- [ ] Add a durable queue store so requests survive service restarts.
- [ ] Introduce explicit worker and executor models for serial shell tasks without smuggling in unnecessary abstraction layers.
- [ ] Add lease, timeout, retry, and stale-request recovery semantics for long-running local tasks.
- [ ] Add per-lane concurrency policy so some lanes can stay serial while lighter lanes can eventually opt into bounded parallelism.
- [ ] Add structured operator-readable logs and task event history.

## Milestone 3: Workspace-Aware Automation

- [ ] Add repo-aware workflows for cross-repo README and roadmap updates across the `speak-to-user` workspace.
- [ ] Add submodule-pin workflows for the umbrella monorepo, including exact target verification and docs alignment.
- [ ] Add release-train workflows for cross-repo version bumps, release notes, and post-release verification.
- [ ] Add guardrails that understand Gale's machine-level serialization constraints for build and test toolchains.
- [ ] Add safe dry-run support for high-impact write operations.

## Milestone 4: OpenAI And MCP App Surface

- [ ] Build an OpenAI/FastMCP App for this coordinator so queue state and task controls have a richer operator interface.
- [ ] Register UI resources for lane dashboards, request detail views, and task lifecycle controls.
- [ ] Add app-aware prompt and tool metadata so the coordinator reads cleanly inside MCP-capable clients.
- [ ] Add auth and local-operator guardrails that match the eventual app surface.

## Milestone 5: Skills And Plugin Bundles

- [ ] Package companion agent skills that know how to target this coordinator for docs sweeps, e2e serialization, and submodule bump flows.
- [ ] Bundle those skills into a Codex plugin milestone that can ship the coordinator MCP plus the future MCP App surface together.
- [ ] Bundle those skills into a Claude Code plugin milestone with matching discovery and operator guidance.
- [ ] Add docs that explain when to use the raw MCP, the future app surface, and the plugin-wrapped workflows.

## Milestone 6: Umbrella Monorepo Integration

- [ ] Add this repository to the `speak-to-user` umbrella monorepo as a pinned submodule once the target top-level path is chosen.
- [ ] Update the umbrella README and roadmap to distinguish the real vendored coordinator repo from later plugin and app milestones.
- [ ] Add a narrow pin-bump workflow for future releases of this repository in the umbrella monorepo.

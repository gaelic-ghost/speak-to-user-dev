# speak-to-user-dev

Local FastMCP coordinator for Gale's multi-repo `speak-to-user` development work, with streamable HTTP transport, typed `pydantic-settings` configuration, and the first queueing surface for serial local-dev tasks.

## Table of Contents

- [Overview](#overview)
- [Setup](#setup)
- [Usage](#usage)
- [Development](#development)
- [Verification](#verification)
- [Roadmap Highlights](#roadmap-highlights)
- [License](#license)

## Overview

This repository is the source-of-truth coordinator service for local `speak-to-user` development chores that should not all run at once.

### Motivation

The broader `speak-to-user` workspace now spans multiple runtimes, services, apps, and umbrella-repo pinning work. Some of the important chores in that workspace are intentionally sequential or at least deserve a shared control surface before they become automated: heavyweight end-to-end suites, cross-repo README and roadmap sweeps, careful submodule pin bumps in the umbrella monorepo, and future release-train coordination.

This service exists to give those tasks one local coordination point before a heavier orchestration layer is added. The current scaffold keeps the contract honest:

- it exposes a real FastMCP server over Streamable HTTP
- it loads typed configuration through `pydantic-settings`
- it defines named serial lanes for heavy e2e work, docs sync, submodule pinning, and release chores
- it lets clients queue, start, complete, cancel, and inspect requests
- it does not yet execute shell commands or mutate sibling repositories on its own

That last point matters. New layers are easy to overcomplicate, so this repo starts with the smallest useful coordinator surface first and leaves actual executor, agent, and plugin integration for explicit milestones.

This standalone repository is also intended to be the source-of-truth development home even after the umbrella `speak-to-user` monorepo vendors it under `mcps/speak-to-user-dev`. The monorepo copy should stay an integration submodule, while feature development, releases, and first-pass verification continue to happen here.

## Setup

Install the project dependencies:

```bash
uv sync
```

Configuration is loaded through `pydantic-settings`.

- Safe defaults live in [`.env`](/Users/galew/Workspace/speak-to-user-dev/.env).
- Machine-local overrides belong in `.env.local`, which is gitignored.
- Environment variables use the `SPEAK_TO_USER_DEV_` prefix.

Key defaults:

- host: `127.0.0.1`
- port: `7461`
- MCP path: `/mcp`
- workspace root: `../speak-to-user`
- default owner: `codex`

## Usage

Run the coordinator locally:

```bash
uv run speak-to-user-dev
```

The service exposes Streamable HTTP on `http://127.0.0.1:7461/mcp`.

Today the main operator-facing tools and resources are:

- `status`
  - current queue totals and runtime configuration
- `list_lanes`
  - available serial coordination lanes
- `queue_task`
  - create a queued request in a named lane without executing it yet
- `start_next_task`, `complete_task`, `cancel_task`
  - advance queued work through an explicit lifecycle
- `dev://status`, `dev://lanes`, `dev://requests`, `dev://runtime`
  - JSON resources for machine-readable inspection

## Development

Run the service directly while iterating:

```bash
uv run speak-to-user-dev
```

This scaffold intentionally stops short of shell execution. It is a queueing and coordination service first, not a silent command runner. That keeps the early surface easier to reason about while the real execution design gets nailed down around Gale's machine constraints, sequential build rules, and the difference between safe read-only tasks and high-impact write tasks.

The initial lane set is:

- `heavy-e2e`
  - serialize heavyweight end-to-end runs that would otherwise compete for local toolchains or memory
- `docs-sync`
  - coordinate cross-repo README, roadmap, and release-note sweeps
- `submodule-pins`
  - coordinate careful umbrella monorepo pin bumps
- `release-train`
  - reserve cross-repo release chores that should be advanced in order

Future milestones cover executor integration, queue persistence, repo-aware guardrails, an OpenAI/FastMCP App surface, and bundled skills plus Codex and Claude Code plugins.

When those plugin bundles arrive, they should live as dedicated plugin roots inside this repository so each plugin can keep its own expected `skills/`, `.mcp.json`, and manifest structure without warping the core service layout.

## Verification

Run the baseline checks before committing:

```bash
uv run pytest
uv run ruff check .
uv run mypy .
```

## Roadmap Highlights

The first roadmap pass in [ROADMAP.md](/Users/galew/Workspace/speak-to-user-dev/ROADMAP.md) focuses on:

- durable execution-aware queueing for heavyweight local-dev chores
- umbrella-monorepo submodule and docs workflows
- an OpenAI/FastMCP App surface for the coordinator
- bundled agent skills plus Codex and Claude Code plugin distribution
- Codex multi-agent and Claude Code subagent configuration management

## License

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).

# AGENTS.md

## Repository role

- Treat this repository as the source of truth for the `speak-to-user-dev` FastMCP coordinator service.
- Treat the future umbrella-repo copy at `../speak-to-user/mcps/speak-to-user-dev` as the integration submodule, not the main development home.
- Keep queue semantics, operator-facing wording, and repo-local documentation aligned here before updating any umbrella submodule pointer.

## Monorepo and submodule workflow

- Treat the local `../speak-to-user` checkout as a protected clean base checkout only. It must stay on `main`, and it must stay clean.
- Never switch the local branch of the base `../speak-to-user` checkout for feature work, experiments, doc updates, or submodule updates.
- For any umbrella-repo change, create a new branch in a new `git worktree` and do the work there instead of touching the base `../speak-to-user` checkout.
- Land umbrella submodule bumps and umbrella-doc updates through pull requests against the monorepo instead of pushing directly to monorepo `main`.
- After a monorepo branch is merged, pull or fast-forward the base `../speak-to-user` checkout back to `main` and delete the merged worktree and branch.
- When the umbrella repo adopts a new `speak-to-user-dev` version, prefer updating the submodule pointer to a tagged release rather than an arbitrary branch tip unless Gale explicitly asks otherwise.

## Repository-specific guidance

- Keep this service intentionally small and explicit while the real execution layer is still being designed.
- Do not add a new coordinator, manager, executor, wrapper, repository, or abstraction layer casually. New layers are often unnecessary here and need extra review before and after they are introduced.
- Keep operator-facing error strings descriptive and grounded in the actual lane, request, or repo workflow that failed.
- Keep queueing, lifecycle control, and resource inspection honest about what exists today. Do not imply that shell execution, repo mutation, or durable state already exists when they are still roadmap work.
- Keep plugin packaging concerns separate from the raw service contract. If Codex or Claude Code plugins are added later, treat those as plugin-root bundles inside this repository rather than letting plugin structure distort the core service layout.

## Python workflow

- Use `uv` for dependency management, environments, and command execution.
- Run Python commands with `uv run`.
- Keep `pyproject.toml` and `uv.lock` aligned in the same change when dependencies move.
- Baseline verification for this repository is:
  - `uv run pytest`
  - `uv run ruff check .`
  - `uv run mypy .`

## Release and distribution

- Treat this standalone repository as the source of truth for tags and releases.
- Keep the umbrella `mcps/speak-to-user-dev` submodule update separate from unrelated monorepo changes unless Gale explicitly asks to bundle them.
- When plugin bundles or MCP App surfaces are introduced later, keep the docs explicit about whether they live in this repo, in the umbrella repo, or are still only roadmap items.

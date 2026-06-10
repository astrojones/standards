# Why these rules

The Python tooling standard is opinionated on purpose. The rationale:

## pyproject.canonical.toml is the source of truth

The org maintains many production Python projects. Their `pyproject.toml`
tooling sections converged on the same shape. Forking that shape into per-repo
templates guarantees drift — active projects evolve, copies don't. So the
canonical config lives **here**, once, and every consumer renders from it:

- `pyproject-canon` skill — generates/upgrades a project's `pyproject.toml`.
- `/new-app` (astrojones-dev) — scaffolds Python backends from it.
- CI — can diff a project's tooling sections against this to detect drift.

Edit the standard here, nowhere else.

## Verify-on-init must fail loud

A green-looking project with an unresolvable ruff selector, a mismatched
`requires-python` vs `target-version`, or a missing dev-group tool is worse
than an obvious failure — the breakage surfaces later, after code has been
written on a broken foundation.

**Rule:** `uv sync && pytest && ruff check && ty check` must all pass before
the first commit. If any fail, stop and fix the foundation first.

## Pydantic-everywhere

No `dict`, `list[dict]`, or `Any` crossing public function boundaries.
Construct Pydantic models at the call site and pass them. `ANN401` blocks
`Any` in annotations; `ty` and code review enforce the rest. Loose dicts at
boundaries are where type safety silently dies.

## ty, not mypy

`ty` (Astral) is fast and strict. The org migrated off mypy. Three rules at
`error` by default (`unresolved-import`, `unresolved-reference`,
`invalid-assignment`); a documented loose variant exists for bot/cog projects
with dynamic attribute access.

## ruff preview + the full rule set

`preview = true` is required — several selected rules only exist in preview.
Each rule family in the canonical list has caught a real bug or merge-blocking
drift in production. Don't trim the list; the `D` (docstring) rules in
particular depend on the calibrated `tests/**` per-file-ignores to stay usable
in tests.

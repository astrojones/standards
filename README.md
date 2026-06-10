# astrojones/standards

**Single source of truth for the astrojones org's engineering standards.**

Not buried in a skill or a plugin — a plain, versioned repo that every consumer
reads from. Edit a standard here, and every project that regenerates from it
picks up the change.

## What's here

| Path | Standard |
|------|----------|
| [`python/pyproject.canonical.toml`](python/pyproject.canonical.toml) | The canonical Python tooling config — ruff (full preview rule set), ty (strict), pytest, coverage, hatchling build, PEP 735 dev deps. **The SSOT.** |
| [`python/variants.md`](python/variants.md) | Which fields are non-negotiable vs. the few axes that legitimately vary (Python version, line length, project shape, ty strictness…). |
| [`python/why-these-rules.md`](python/why-these-rules.md) | Rationale: pydantic-everywhere, ty-not-mypy, fail-loud verify-on-init. |
| [`ci-cd/README.md`](ci-cd/README.md) | Org CI/CD conventions and the reusable-workflow index. |

## Who consumes it

- **`pyproject-canon` skill** — renders a project's `pyproject.toml` from `python/pyproject.canonical.toml`.
- **`/new-app`** (astrojones-dev plugin) — scaffolds standard-compliant Python backends from it.
- **CI** — an app's lint/test gate uses the same tooling config; CI can diff against this to catch drift.
- **You, by hand** — `extend`/copy the relevant section when aligning an existing repo.

## The Python gate (non-negotiable)

Any project with a Python backend must pass, locally and in CI:

```bash
uv sync && uv run pytest && uv run ruff check . && uv run ty check
```

Green here means green everywhere. Don't weaken the rules per-project — pick a
documented variant or regenerate.

## How to change a standard

1. Edit the file here.
2. Bump the tag (`git tag vX.Y.Z`) so consumers can pin if they need to.
3. Regenerate downstream projects with `pyproject-canon` (it reads this repo).

Never hand-patch tooling sections in individual repos — that's how drift starts.

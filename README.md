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
| [`typescript/biome.canonical.json`](typescript/biome.canonical.json) | The canonical TypeScript formatter + linter — Biome with the org rules, import sorting via Assist. **The SSOT.** |
| [`typescript/tsconfig.canonical.json`](typescript/tsconfig.canonical.json) | The canonical `tsconfig.json` — full strict family, ESNext/Bundler, no emit. **The SSOT.** |
| [`typescript/package.canonical.json`](typescript/package.canonical.json) | The canonical `package.json` tooling — scripts, dev-dependency floors, engines, pnpm pin. **The SSOT.** |
| [`typescript/npmrc.canonical`](typescript/npmrc.canonical) | Canonical `.npmrc` — `engine-strict=true` so a wrong Node version fails loudly. |
| [`typescript/variants.md`](typescript/variants.md) | Which fields are non-negotiable vs. the few axes that legitimately vary (Node version, project shape, workspace…). |
| [`typescript/why-these-rules.md`](typescript/why-these-rules.md) | Rationale: Biome-not-eslint+prettier, tsc-strict-as-ty, vitest, pnpm frozen lockfile, no `any`. |
| [`ci-cd/README.md`](ci-cd/README.md) | Org CI/CD conventions and the reusable-workflow index. |

## Who consumes it

- **Generator skills** — `pyproject-canon` renders a Python project's `pyproject.toml` from `python/pyproject.canonical.toml`; the TypeScript canonical files are rendered the same way.
- **`/new-app`** (deploy plugin) — scaffolds standard-compliant backends and front-ends from it.
- **CI** — a project's lint/test gate uses the same tooling config; CI can diff against this to catch drift.
- **You, by hand** — `extend`/copy the relevant section when aligning an existing repo.

## The Python gate (non-negotiable)

Any project with a Python backend must pass, locally and in CI:

```bash
uv sync && uv run pytest && uv run ruff check . && uv run ty check
```

## The TypeScript gate (non-negotiable)

Any project with a TypeScript/JavaScript surface must pass, locally and in CI:

```bash
pnpm install --frozen-lockfile && pnpm run lint && pnpm run build && pnpm run test
```

The typecheck lives inside `lint` (`biome ci . && tsc --noEmit`); there is no
separate typecheck step in the gate. Green here means green everywhere. Don't
weaken the rules per-project — pick a documented variant or regenerate.

## How to change a standard

1. Edit the file here.
2. Bump the tag (`git tag vX.Y.Z`) so consumers can pin if they need to.
3. Regenerate downstream projects from the canonical files (the generator skills
   read this repo).

Never hand-patch tooling sections in individual repos — that's how drift starts.

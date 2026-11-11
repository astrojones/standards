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
| [`typescript/npmrc.canonical`](typescript/npmrc.canonical) | Canonical `.npmrc` — `engine-strict=true` for npm compatibility only; the fail-loud engine guard is `engineStrict: true` in `pnpm-workspace.yaml`. |
| [`typescript/pnpm-workspace.canonical.yaml`](typescript/pnpm-workspace.canonical.yaml) | Canonical `pnpm-workspace.yaml` — `engineStrict: true` (the pnpm 12 engine guard) plus the workspace variant. **The SSOT.** |
| [`typescript/variants.md`](typescript/variants.md) | Which fields are non-negotiable vs. the few axes that legitimately vary (Node version, project shape, workspace…). |
| [`typescript/why-these-rules.md`](typescript/why-these-rules.md) | Rationale: Biome-not-eslint+prettier, tsc-strict-as-ty, vitest, pnpm frozen lockfile, no `any`. |
| [`rust/Makefile.canonical`](rust/Makefile.canonical) | The canonical Rust `Makefile`: `check` (the gate), `build`, `install`, `dist` (release archive + sha256), `brew-style`. Needs no edits. **The SSOT.** |
| [`rust/rust-toolchain.canonical.toml`](rust/rust-toolchain.canonical.toml) | Exact toolchain pin with `rustfmt` and `clippy`. **The SSOT.** |
| [`rust/Cargo.canonical.toml`](rust/Cargo.canonical.toml) | The `[package]` header: edition 2024, license, repository, `publish = false`. **The SSOT.** |
| [`rust/variants.md`](rust/variants.md) | Which Rust rules are non-negotiable vs. the axes that vary (shape, publishing, distribution, toolchain). |
| [`rust/why-these-rules.md`](rust/why-these-rules.md) | Rationale: one gate spelled once, `--locked`, exact toolchain, release naming, repo-as-tap. |
| [`ci-cd/README.md`](ci-cd/README.md) | Org CI/CD conventions and the reusable-workflow index. |
| [`floors/`](floors/) | Real, parseable manifests (`pyproject.toml` + `uv.lock`, `package.json` + `pnpm-lock.yaml`) holding every dependency floor. **Dependabot bumps these**; the canonical files mirror them. |
| [`scripts/check_floors.py`](scripts/check_floors.py) | Fails when a canonical file disagrees with `floors/`; `--write` syncs the canonical files from `floors/`. |

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

Green here means green everywhere. Don't weaken the rules per-project — pick a
documented variant or regenerate.

## The TypeScript gate (non-negotiable)

Any project with a TypeScript/JavaScript surface must pass, locally and in CI:

```bash
pnpm install --frozen-lockfile && pnpm run lint && pnpm run build && pnpm run test
```

The typecheck lives inside `lint` (`biome ci . && tsc --noEmit`); there is no
separate typecheck step in the gate. Green here means green everywhere. Don't
weaken the rules per-project — pick a documented variant or regenerate.

## The Rust gate (non-negotiable)

Any project with a Rust crate must pass, locally and in CI:

```bash
make check   # cargo fmt --check && cargo clippy --all-targets --locked -- -D warnings && cargo test --locked
```

Green here means green everywhere. Don't weaken the gate per-project — pick a
documented variant. The Rust files are not tracked by `floors/` yet: the toolchain is an exact
pin that is bumped by hand.

## Keeping versions current

The canonical files carry `{{ … }}` placeholders, so Dependabot cannot parse
them. Every dependency floor therefore also lives in `floors/`, a pair of real
manifests that Dependabot (`.github/dependabot.yml`) bumps weekly with
`versioning-strategy: increase`. CI (`.github/workflows/floors.yml`) then fails
until the canonical files carry the same floors:

```bash
uv run python scripts/check_floors.py --write
```

Run that on a Dependabot PR branch, commit the result, merge. To add or drop a
dependency, edit **both** `floors/…` and the canonical file (the check reports
an entry present in only one), then `uv lock` / `pnpm install` inside `floors/…`.

## How to change a standard

1. Edit the file here (floors: edit `floors/` too, see above).
2. Bump the tag (`git tag vX.Y.Z`) so consumers can pin if they need to.
3. Regenerate downstream projects from the canonical files (the generator skills
   read this repo).

Never hand-patch tooling sections in individual repos — that's how drift starts.

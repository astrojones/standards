# Decisions: when to default, when to ask

The canonical config converged across the user's recent projects. Most of it
is non-negotiable — apply without asking. A small set of axes legitimately
varies; ask only those.

## Default silently (do NOT ask)

These are stable across the org's TypeScript projects. If you find yourself
omitting one, re-justify why.

- `biome.canonical.json` as the single formatter + linter (no eslint, no prettier)
- Biome formatter: spaces, `indentWidth` 2, `lineWidth` 120
- Biome linter: `preset: "recommended"` plus `suspicious.noExplicitAny: "error"` and `style.noNonNullAssertion: "error"`
- Import sorting via the Assist feature (`assist.actions.source.organizeImports`)
- `tsconfig.canonical.json` as-is, including all strict flags (`strict`,
  `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noImplicitOverride`,
  `noFallthroughCasesInSwitch`, `verbatimModuleSyntax`, `isolatedModules`)
- `target: "ES2022"`, `module: "ESNext"`, `moduleResolution: "Bundler"`, `noEmit`, `skipLibCheck`
- `package.canonical.json` scripts: `lint` = `biome ci . && tsc --noEmit`,
  `typecheck` = `tsc --noEmit`, `test` = `vitest run`
- `type: "module"` (ESM everywhere)
- `engines.node` floor matching the chosen Node version
- `.npmrc` with `engine-strict=true`
- `packageManager` pinned via `corepack`; CI and local resolve the same pnpm
- Dependency floors (`^x.y.z`), never exact pins, in `dependencies` / `devDependencies`
- Vitest as the test runner; tests colocated as `*.test.ts` beside the source

## Variation axes (ask if not inferable)

Infer from context first — only ask if there's no clear signal. Use a single
batched question if more than one axis is unclear.

### 1. Node version → `engines.node` + CI `node-version`
- Signals: existing `.nvmrc`, CI matrix, a dependency's `engines` floor.
- Default: **24** (current LTS). Fall back to **22** only when a required dep or
  deployment target has not moved to 24 yet, and change `engines.node`, the
  local toolchain pin, and the CI `node-version` together so local/CI/prod stay
  aligned.
- `astrojones/.github` `ci.yml` must set `node-version: "24"` explicitly for
  repos on the default — do not rely on the runner's preinstalled Node.

### 2. Project shape → which template branch
Pick one based on project intent. Ask only if intent is genuinely ambiguous.

| Shape              | Signals                                   | Adds                                                              |
|--------------------|-------------------------------------------|-------------------------------------------------------------------|
| `library`          | publishable, no entrypoint                | base canonical only                                                |
| `app`              | Vite, a rendered UI, a dev server         | `vite` in dev deps; `build` = `vite build`; `index.html` entry     |
| `single-file-view` | MCP-apps view embedded as one HTML file    | Vite with a single-file build plugin; `build` emits one self-contained `.html` |

### 3. `workspace` (pnpm workspace beside a Python root)
- Signals: a Python root (`pyproject.toml` at the repo root) that also ships
  front-end or TypeScript members, or a repo that will grow several TS packages.
- Adds: `pnpm-workspace.canonical.yaml` at the root as `pnpm-workspace.yaml`
  with `packages: ["web/*"]`; TS members live under `web/<name>`.
- The **root** `package.json` overrides the scripts (do not put these in the
  canonical single-project file):
  - `lint` = `biome ci . && pnpm -r typecheck`
  - `build` = `pnpm -r build`
  - `test` = `pnpm -r test`
- The `lint` override recurses into every member's `typecheck`, so a type error
  in any `web/*` package fails the root gate. `biome ci .` at the root lints all
  members from a single config.

## Anti-patterns (refuse silently)

If the existing config or user request includes any of these, replace with the
canonical equivalent:

- **eslint** or **prettier** → use Biome. One tool, fast, no plugin drift.
- **`any`** in application code → `suspicious.noExplicitAny` blocks it; type the
  boundary or use `unknown` plus a narrowing check.
- **`!` non-null assertions** → `style.noNonNullAssertion` blocks it; narrow the
  type or assert explicitly with a check.
- **`npm install` / `yarn`** → use pnpm with `--frozen-lockfile`. Different
  installers produce different trees and lockfiles.
- **Exact version pins** in `dependencies` / `devDependencies` → use floors
  (`^x.y.z`). Exception: the `packageManager` pin is exact on purpose.
- **`tsconfig.json` with strict off** or individual strict flags dropped → use
  the canonical set wholesale; partial adoption breaks rule interactions.
- **A committed `dist/` built by hand** → build is reproducible from source; the
  build output is generated, not tracked.

## Authoring rule

When updating an existing TypeScript project, **preserve the project's `name`,
`version`, and any project-specific fields**. Replace the tooling sections
wholesale: `scripts`, `devDependencies`, `engines`, `packageManager`, and the
`biome.json` / `tsconfig.json` configs. Don't merge — the canonical config is
internally consistent, and partial adoption breaks rule interactions (e.g. the
`lint` script assumes `tsc --noEmit` reads the canonical `tsconfig.json`).

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
- An engine guard that fails loudly on the wrong Node: `engineStrict: true` in
  `pnpm-workspace.yaml` (see axis 3) **and** `engine-strict=true` in `.npmrc`.
  pnpm 12 reads only auth/registry settings from `.npmrc`, so the guard that
  matters is `pnpm-workspace.yaml`'s; the `.npmrc` line covers npm-compat
  consumers.
- `packageManager` pinned via `corepack`; CI and local resolve the same pnpm.
  Pinning pnpm 12 needs **corepack ≥ 0.36** — Node ships an older bundled
  corepack (0.33 as of Node 26) whose hardcoded `bin/pnpm.cjs` path no longer
  exists in pnpm 12's native-binary layout, so `corepack pnpm` dies with
  `MODULE_NOT_FOUND`. If the runner's corepack is older, upgrade it (`npm i -g
  corepack@latest` before `corepack enable`) or launch pnpm with
  `pnpm/action-setup`.
- Dependency floors (`^x.y.z`), never exact pins, in `dependencies` /
  `devDependencies`. Floors let the lockfile pin the resolved tree and keep the
  manifest from drifting out of step. The `$schema` URL in
  `biome.canonical.json` is pinned to the current Biome minor and may lag once a
  floor resolves a newer one — harmless, it only feeds editor hints.
- Vitest as the test runner; tests colocated as `*.test.ts` beside the source

Render placeholders: `{{ project_name }}` (the package name) and
`{{ node_version }}` (the Node floor in `engines.node`, e.g. `24`). Those are
the only two; `packageManager` is a concrete pin, not a placeholder.

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
  repos on the default — the reusable workflow defaults to `"20"`, so relying on
  it installs against an unsupported runtime.

### 2. Project shape → which template branch
Pick one based on project intent. Ask only if intent is genuinely ambiguous.

| Shape              | Signals                                   | Adds                                                              |
|--------------------|-------------------------------------------|-------------------------------------------------------------------|
| `library`          | publishable, no entrypoint                | base canonical only                                                |
| `app`              | Vite, a rendered UI, a dev server         | `vite` in dev deps; `build` = `vite build`; `index.html` entry     |
| `single-file-view` | MCP-apps view embedded as one HTML file    | Vite with a single-file build plugin; `build` emits one self-contained `.html` |

The canonical `tsconfig.canonical.json` pins `lib: ["ES2022"]` and includes no
DOM types. The browser shapes (`app`, `single-file-view`) need them — add
`"DOM"` (and `"DOM.Iterable"` when you iterate DOM collections) to `lib`:
`"lib": ["ES2022", "DOM", "DOM.Iterable"]`. `library` keeps the canonical `lib`
as-is.

The canonical `build` script is the `library` placeholder: `tsc --noEmit`, which
always passes for a type-only package and emits nothing. The `app` and
`single-file-view` shapes override it with a real bundler build (`vite build`).

The canonical `private: true` is correct for apps and internal packages. A
**publishable** `library` flips it to `false`; `engines` and the rest stay.

### 3. `workspace` + the `pnpm-workspace.yaml` file
Every TypeScript project ships `pnpm-workspace.canonical.yaml` as its
`pnpm-workspace.yaml` — that is where pnpm 12 keeps non-auth settings, including
`engineStrict`. Single projects ship it **settings-only** (no `packages`, so the
workspace is just the root). A workspace additionally declares members.

- Signals: a Python root (`pyproject.toml` at the repo root) that also ships
  front-end or TypeScript members, or a repo that will grow several TS packages.
- Adds: uncomment `packages: ["web/*"]`; TS members live under `web/<name>`.
- The **root** `package.json` overrides the scripts (do not put these in the
  canonical single-project file):
  - `lint` = `biome ci . && pnpm -r typecheck`
  - `build` = `pnpm -r build`
  - `test` = `pnpm -r test`
- The `lint` override recurses into every member's `typecheck`, so a type error
  in any `web/*` package fails the root gate. `biome ci .` at the root lints all
  members from a single config.
- pnpm rewrites `pnpm-workspace.yaml` on install: with a lockfile it auto-appends
  a `minimumReleaseAgeExclude` block for packages younger than the supply-chain
  age gate, e.g.
  ```yaml
  minimumReleaseAgeExclude:
    - "@vitest/mocker@5.0.4"
    - "@vitest/spy@5.0.4"
    - vitest@5.0.4
  ```
  This is expected, not drift — commit it. Keep the canonical file settings-only;
  let pnpm manage that list, never hand-maintain it.

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

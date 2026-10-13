# Why these rules

The TypeScript tooling standard is opinionated on purpose. The rationale:

## The canonical files are the source of truth

The org maintains several TypeScript projects. Their `biome.json`,
`tsconfig.json`, and `package.json` tooling sections converged on the same
shape. Forking that shape into per-repo templates guarantees drift — active
projects evolve, copies don't. So the canonical config lives **here**, once,
and every consumer renders from it. Edit the standard here, nowhere else.

## Biome instead of eslint + prettier

Biome is one tool for formatting and linting, written in Rust, so it is fast
enough to run on every save and in CI without a caching layer. eslint plus
prettier is two tools, two configs, and a plugin ecosystem that drifts: every
upgrade can change what fails. Biome ships a fixed rule set (the `recommended`
preset) plus the two rules the org cares about by name — `noExplicitAny` and
`noNonNullAssertion`. Import sorting uses Biome's Assist feature instead of a
separate plugin.

## `tsc --strict` is the counterpart to ty

The Python standard runs `ty` at strict settings. TypeScript's equivalent is
`tsc` with the full strict family, not just `strict: true`. The canonical adds
`noUncheckedIndexedAccess` and `exactOptionalPropertyTypes` on top of the usual
flags, because the two silent bugs that hurt most are an unindexed lookup
returning `undefined` and an optional property being written as `null`.
`verbatimModuleSyntax` and `isolatedModules` keep the source honest about ESM so
a bundler and a plain `tsc` agree.

## vitest

Vitest runs the same suite in watch mode locally and once in CI (`vitest run`),
understands ESM and TypeScript without a build step, and needs no separate
transpile config. It is the test runner the org standardizes on; the gate is
`vitest run`, so CI is deterministic.

## pnpm with `--frozen-lockfile`

pnpm is faster, stricter about phantom dependencies, and its lockfile is the
only supported source of truth for the dependency tree. `--frozen-lockfile`
makes CI fail when `package.json` and the lockfile disagree instead of quietly
resolving a different tree. `engine-strict=true` extends the same fail-loud
principle to the Node version: a consumer on the wrong Node stops at install
rather than building against a runtime the project never supported.

## No `any`

Loose `any` at the boundaries is where type safety silently dies — the same
reason the Python standard forbids `Any` and bare `dict` in public signatures.
`noExplicitAny` and `noNonNullAssertion` are errors, not warnings, so a typed
boundary is the only way to get past the gate.

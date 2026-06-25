# astrojones CI/CD standards

The org's canonical CI/CD lives in two places — this doc is the index, not a
copy. It exists so the patterns are preserved as org knowledge, not buried in a
single project or a personal skill.

## Default path: nuklaut auto-deploy

Most org apps deploy to the **nuklaut** controller (astrojones.de). The standard
is the reusable workflow + four-file convention documented by the
`deploy` plugin (`nuklaut-deploy` skill). Summary:

- App repo calls `astrojones/.github/.github/workflows/nuk-deploy.yml@main` from
  a 3-line `deploy.yml` with `secrets: inherit`.
- Push to `main` → build → push `ghcr.io/astrojones/<repo>:latest` (two-segment)
  → `nuk apply` → live at `https://<repo>.astrojones.de`.
- Secrets via the `APP_ENV` repo secret; no SSH.

Scaffold a compliant app with `/new-app` (deploy plugin).

## The reusable workflow hub: `astrojones/.github`

All org-wide reusable workflows live there. The **canonical per-workflow
reference** — call form, required inputs, secrets, and contracts — is the
[reusable-workflow catalog](https://github.com/astrojones/.github#reusable-workflow-catalog)
in that repo's README. The table below is a thin index, not a second copy; when
the two disagree, the catalog wins.

| Workflow | Purpose |
|----------|---------|
| `ci.yml` | Org-wide minimum CI gate: lint + format + test (trivial green for content-only repos) |
| `app-ci.yml` | Build + push an image matrix to GHCR |
| `release.yml` | No-PR conventional-commit release (version bump, tag, GitHub release) |
| `nuk-deploy.yml` | Build → GHCR → `nuk apply` (the default deploy path) |
| `nuk-apply.yml` | Deploy-only: apply a manifest without rebuilding (multi-image stacks) |
| `nuk-preview.yml` | Per-PR ephemeral preview stack |
| `e2e-compose-playwright.yml` | Sharded Playwright E2E against a compose stack on an ephemeral runner |
| `migration-shadow-check.yml` | Pre-deploy migration safety gate (shadow DB) |
| `runner-up.yml` / `runner-down.yml` | Ephemeral Hetzner CI-runner lifecycle |
| `runner-sweep.yml` | Internal hourly orphan-runner backstop (scheduled, not a reusable workflow) |

Edit reusable CI **there**, not in app repos. App repos only call them. For the
authoritative inputs/secrets of any workflow above, follow the catalog link
rather than duplicating them here.

## Advanced patterns (for apps that outgrow the simple path)

Production-grade patterns — CalVer versioning, `workflow_run` cascades,
blue/green via the Traefik file provider, PR preview environments with a cap,
and auto-rollback with a migration-compatibility check — are captured in the
`kolbe-gha-patterns` skill. Reach for them when an app needs zero-downtime
deploys or preview environments beyond what `nuk apply` gives. These were
proven on the `kolbe` platform; they are the org's reference for heavier CI/CD.

## Python app CI

A Python app's CI must run the same gate as local: `uv sync`, `pytest`,
`ruff check`, `ty check` — all green. The tooling config those commands read is
the org [Python standard](../python/pyproject.canonical.toml). Keep CI and the
local gate identical so green-on-CI means green-on-laptop.

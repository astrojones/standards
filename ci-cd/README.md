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

All org-wide reusable workflows live there. Current set:

| Workflow | Purpose |
|----------|---------|
| `nuk-deploy.yml` | Build → GHCR → `nuk apply` (the default deploy path) |
| `nuk-apply.yml` | Apply a manifest without rebuilding |
| `nuk-preview.yml` | Preview/ephemeral deploys |
| `app-ci.yml` | Lint + test for app repos |
| `e2e-compose-playwright.yml` | End-to-end tests against a compose stack |
| `migration-shadow-check.yml` | Validate DB migrations against a shadow DB |
| `runner-up.yml` / `runner-down.yml` / `runner-sweep.yml` | Self-hosted runner lifecycle |

Edit reusable CI **there**, not in app repos. App repos only call them.

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

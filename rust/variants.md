# Decisions: when to default, when to ask

Most of the Rust standard is non-negotiable: apply it without asking. A few axes
legitimately vary.

## Default silently (do NOT ask)

- The gate, spelled exactly as in `Makefile.canonical`:
  `cargo fmt --check`, `cargo clippy --all-targets --locked -- -D warnings`, `cargo test --locked`.
- A committed `Cargo.lock` for every binary, and `--locked` on every cargo call that reads it
  (CI, `make`, release builds). A lockfile that is out of date fails the build, it is not rewritten.
- `rust-toolchain.toml` with an exact `channel` and `components = ["rustfmt", "clippy"]`.
- `edition = "2024"` for new projects.
- `license`, `repository`, `description`, `readme` in `[package]`, and a `LICENSE` file.
- The `Makefile` target names: `help`, `build`, `install`, `fmt`, `fmt-check`, `lint`, `test`,
  `check`, `dist`, `clean`. Add targets; do not rename these.
- Release archives named `<bin>-v<version>-<target-triple>.tar.gz` with a `.sha256` next to them.
- Lint exceptions on the smallest item that needs them, with a comment saying why. Never loosen the
  gate (`-D warnings`, the lint set) to make a change pass.

## Variation axes (ask if not inferable)

### 1. Project shape
| Shape | Signals | Adds |
|---|---|---|
| `bin` | `src/main.rs` | `install` and `dist` targets as canonical |
| `lib` | `src/lib.rs` only | drop `dist` and `install`; keep the rest |
| `workspace` | `[workspace]` in the root manifest | `--workspace` on `lint` and `test`; one `Cargo.lock` |

### 2. Where the crate goes
- **Not published** (default): `publish = false`. Required while any dependency is a git dependency.
- **crates.io**: remove `publish = false`, add `keywords` and `categories`, no git dependencies.

### 3. How the binary reaches users
- **Source only**: nothing more than the above.
- **Release archives**: `make dist` per platform, uploaded to the GitHub release.
- **Homebrew**: a formula that builds from source with `std_cargo_args`. For a private repo the
  repository is its own tap (`Formula/<bin>.rb`, tapped with an explicit URL) and the formula clones
  over SSH. For a public one a separate `homebrew-<name>` repo is also fine.
- Platforms follow the runners that exist (see `ci-cd/README.md`): Linux x86_64 in CI; macOS and
  arm64 builds come from a developer machine or a hosted runner.

### 4. Toolchain version
- The current stable at project start. Moving it is a deliberate commit, not a side effect.
- Never `stable` or `nightly` as the channel: a floating channel makes "green here" mean nothing.

## Anti-patterns (refuse silently)

- `cargo build` / `cargo test` without `--locked` in CI.
- `#![allow(warnings)]`, or blanket `#![allow(clippy::...)]` at crate level, to get past the gate.
- A floating `channel` in `rust-toolchain.toml`.
- A binary crate without `Cargo.lock` in git.
- A CI gate that differs from `make check`.

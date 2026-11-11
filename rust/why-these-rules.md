# Why these rules

The Rust standard is small on purpose. It was extracted from `jonesh-de/code-store`, the
org's first Rust project, and holds only what that project's gate and release already proved.
More (lint sets, `cargo deny`, MSRV policy) joins when a second project shows the need.

## One gate, spelled once

`make check` runs format, clippy and tests, in that order, cheapest first. CI calls the same
target, so green on a laptop and green on CI are the same statement. A gate that exists twice
(a script and a workflow) drifts.

## `--locked` and `-D warnings`

`--locked` makes a stale `Cargo.lock` a failure instead of a silent rewrite, so what was tested is
what is built and released. `-D warnings` turns clippy into a gate; a warning that may stay is a
warning nobody reads. Exceptions belong on the item, with a reason, so the next reader can judge
them.

## Exact toolchain

Clippy gains lints with every release. With a floating channel, an unrelated commit goes red the
day a new stable ships. An exact `channel` makes toolchain bumps their own commit, and the
CI cache (the compiler is part of the key) stays valid until then.

## Metadata and LICENSE

Package managers read `license`, `description` and `repository` from `Cargo.toml`, and Homebrew
audits a formula against the same facts. Filling them in once is cheaper than every consumer asking.
`publish = false` is not decoration: it stops an accidental `cargo publish`, and crates.io rejects
git dependencies anyway.

## Release archive naming

`<bin>-v<version>-<target-triple>.tar.gz` plus `.sha256` is what a Homebrew formula, an install
script or a human can guess without a manifest. The triple comes from `rustc -vV`, so the same
`make dist` is right on every platform. The version is the git tag; Cargo.toml is not stamped by
the shared release workflow (it cannot update `Cargo.lock`), so the Makefile reads the tag first.

## Why the repo can be its own Homebrew tap

`brew tap <user>/<name> <url>` accepts any git repository with a `Formula/` directory. A private
repository then needs no second repository and no token: Homebrew clones over SSH with the
developer's keys. A separate `homebrew-<name>` repo only pays off once the project is public and has
prebuilt bottles.

"""Keep the canonical tooling files in step with the Dependabot-readable floors manifests.

The canonical files carry render-time placeholders, so Dependabot cannot parse them.
`floors/` holds real manifests that Dependabot bumps; this script fails when a
canonical file disagrees with them, and `--write` copies the manifest floors across.

    uv run python scripts/check_floors.py           # check (CI)
    uv run python scripts/check_floors.py --write   # sync canonical files from floors/
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY_MANIFEST = ROOT / "floors/python/pyproject.toml"
PY_CANONICAL = ROOT / "python/pyproject.canonical.toml"
TS_MANIFEST = ROOT / "floors/typescript/package.json"
TS_CANONICAL = ROOT / "typescript/package.canonical.json"
BIOME_CANONICAL = ROOT / "typescript/biome.canonical.json"

# A quoted requirement with a floor, e.g. "uvicorn[standard]>=0.54". Placeholders such as
# ">={{ python_version }}" have no leading name and never match.
REQUIREMENT = re.compile(r'"([A-Za-z0-9][A-Za-z0-9._-]*(?:\[[^\]]+\])?)>=([0-9][^"\s]*)"')
BIOME_SCHEMA = re.compile(r"(schemas/)([0-9][^/]*)(/schema\.json)")


def rel(path: Path) -> str:
    """Return `path` relative to the repo root, for messages."""
    return str(path.relative_to(ROOT))


def requirements_in(text: str) -> list[str]:
    """Return every `name>=floor` requirement quoted in `text`, comments included."""
    return [f"{name}>={floor}" for name, floor in REQUIREMENT.findall(text)]


def name_of(requirement: str) -> str:
    """Return the `name[extras]` part of a `name>=floor` requirement."""
    return requirement.split(">=", maxsplit=1)[0]


def python_problems(*, write: bool) -> list[str]:
    """Compare the canonical pyproject floors with the manifest; rewrite them when `write`."""
    wanted = {name_of(r): r for r in requirements_in(PY_MANIFEST.read_text())}
    text = PY_CANONICAL.read_text()
    problems: list[str] = []
    seen: set[str] = set()
    for requirement in dict.fromkeys(requirements_in(text)):
        name = name_of(requirement)
        seen.add(name)
        if name not in wanted:
            problems.append(f"{rel(PY_CANONICAL)}: {requirement} is not tracked in {rel(PY_MANIFEST)}")
        elif wanted[name] != requirement:
            if write:
                text = text.replace(f'"{requirement}"', f'"{wanted[name]}"')
                print(f"updated {rel(PY_CANONICAL)}: {requirement} -> {wanted[name]}")
            else:
                problems.append(f"{rel(PY_CANONICAL)}: {requirement} but {rel(PY_MANIFEST)} has {wanted[name]}")
    problems.extend(
        f"{rel(PY_MANIFEST)}: {name} is missing from {rel(PY_CANONICAL)}" for name in sorted(wanted.keys() - seen)
    )
    if write:
        PY_CANONICAL.write_text(text)
    return problems


def typescript_problems(*, write: bool) -> list[str]:
    """Compare the canonical package.json and biome schema pins with the manifest; rewrite them when `write`."""
    manifest = json.loads(TS_MANIFEST.read_text())
    text = TS_CANONICAL.read_text()
    canonical = json.loads(text)
    problems: list[str] = []

    pins = {**manifest["devDependencies"], "packageManager": manifest["packageManager"]}
    have = {**canonical["devDependencies"], "packageManager": canonical["packageManager"]}
    for name in sorted(pins.keys() | have.keys()):
        if name not in pins or name not in have:
            problems.append(f"{rel(TS_CANONICAL)}: {name} must be in both it and {rel(TS_MANIFEST)}")
        elif pins[name] != have[name]:
            if write:
                text = text.replace(f'"{name}": "{have[name]}"', f'"{name}": "{pins[name]}"')
                print(f"updated {rel(TS_CANONICAL)}: {name} {have[name]} -> {pins[name]}")
            else:
                problems.append(f"{rel(TS_CANONICAL)}: {name} is {have[name]} but {rel(TS_MANIFEST)} has {pins[name]}")
    if write:
        TS_CANONICAL.write_text(text)

    # The schema URL is an editor hint, but it is cheap to keep on the Biome version the floor resolves to.
    biome = manifest["devDependencies"]["@biomejs/biome"].lstrip("^~")
    schema_text = BIOME_CANONICAL.read_text()
    found = BIOME_SCHEMA.search(schema_text)
    if found is None:
        problems.append(f"{rel(BIOME_CANONICAL)}: no biome schema URL found")
    elif found.group(2) != biome:
        if write:
            BIOME_CANONICAL.write_text(BIOME_SCHEMA.sub(rf"\g<1>{biome}\g<3>", schema_text, count=1))
            print(f"updated {rel(BIOME_CANONICAL)}: schema {found.group(2)} -> {biome}")
        else:
            problems.append(f"{rel(BIOME_CANONICAL)}: schema {found.group(2)} but the Biome floor is {biome}")
    return problems


def main() -> int:
    """Run the checks; return a non-zero exit code when canonical files drift from `floors/`."""
    write = "--write" in sys.argv[1:]
    problems = [*python_problems(write=write), *typescript_problems(write=write)]
    for problem in problems:
        print(f"drift: {problem}")
    if problems:
        hint = "fix the entries above by hand" if write else "run `uv run python scripts/check_floors.py --write`"
        print(f"\n{len(problems)} problem(s); {hint}.")
        return 1
    print("canonical files match floors/")
    return 0


if __name__ == "__main__":
    sys.exit(main())

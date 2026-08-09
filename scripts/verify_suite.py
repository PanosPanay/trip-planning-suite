#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def version_tuple(value):
    parts = []
    for token in str(value).split("."):
        digits = "".join(ch for ch in token if ch.isdigit())
        parts.append(int(digits or 0))
    return tuple(parts)


def find_skill(target, name):
    root = target / name
    candidates = [root / "SKILL.md", *root.glob(f"**/{name}/SKILL.md")]
    return next((path for path in candidates if path.exists()), None)


def external_version(target, skill, name):
    marker = target / name / ".redskill-installed"
    if marker.exists():
        return json.loads(marker.read_text(encoding="utf-8")).get("version"), "Red Skill marker"
    package = skill.parent / "package.json"
    if package.exists():
        return json.loads(package.read_text(encoding="utf-8")).get("version"), "installed package metadata"
    return None, None


def main():
    parser = argparse.ArgumentParser(description="Verify that Trip Planning Suite and every required dependency are ready.")
    parser.add_argument("--target", type=Path, default=Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "skills")
    parser.add_argument("--run-external-tests", action="store_true")
    args = parser.parse_args()
    target = args.target.expanduser().resolve()
    config = json.loads((ROOT / "suite-dependencies.json").read_text(encoding="utf-8"))
    errors = []

    for name in config["bundledSkills"]:
        if not find_skill(target, name):
            errors.append(f"missing bundled skill: {name}")

    for dependency in config["externalSkills"]:
        name = dependency["name"]
        skill = find_skill(target, name)
        if not skill:
            errors.append(f"missing required external skill: {name}")
            continue
        installed_version, version_source = external_version(target, skill, name)
        minimum = dependency.get("minimumVersion", "0.0.0")
        if not installed_version:
            errors.append(f"{name} is present but has no verifiable version metadata")
            continue
        if version_tuple(installed_version) < version_tuple(minimum):
            errors.append(f"{name} {installed_version} is older than required {minimum}")
        else:
            print(f"verified external skill: {name} {installed_version} ({version_source})")
        if args.run_external_tests:
            tests = list(skill.parent.glob("scripts/test-skill-contract.js"))
            if tests and shutil.which("node"):
                result = subprocess.run(["node", str(tests[0])], capture_output=True, text=True)
                if result.returncode:
                    errors.append(f"external skill test failed for {name}: {result.stderr or result.stdout}")

    for command in ["python3", "node", "pandoc", "pdftoppm"]:
        if not shutil.which(command):
            errors.append(f"missing runtime command: {command}")
    try:
        import playwright  # noqa: F401
    except ImportError:
        errors.append("missing Python Playwright; required for Ctrip queries and image/PDF export")

    if errors:
        raise SystemExit("\n".join(errors))
    print("trip-planning-suite ready")


if __name__ == "__main__":
    main()

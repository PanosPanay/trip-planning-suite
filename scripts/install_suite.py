#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def locate_redskill():
    found = shutil.which("redskill")
    if found:
        return found
    candidate = Path.home() / ".local" / "bin" / "redskill"
    return str(candidate) if candidate.exists() else None


def find_installed(target, name):
    root = target / name
    if not root.exists():
        return None
    direct = root / "SKILL.md"
    if direct.exists():
        return direct
    matches = list(root.glob(f"**/{name}/SKILL.md"))
    return matches[0] if matches else None


def copy_skill(source, destination, force):
    if destination.exists():
        if not force:
            print(f"skip existing bundled skill: {destination.name}")
            return
        shutil.rmtree(destination)
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns(".DS_Store", "__pycache__", "*.pyc", "tests"))
    print(f"installed bundled skill: {destination.name}")


def main():
    parser = argparse.ArgumentParser(description="Install every bundled skill and required Red Skill dependency for Trip Planning Suite.")
    parser.add_argument("--target", type=Path, default=Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "skills")
    parser.add_argument("--force", action="store_true", help="Replace existing bundled skills. Does not force-replace external Red Skills.")
    parser.add_argument("--skip-external", action="store_true", help="Test-only: copy bundled skills without installing required external skills.")
    args = parser.parse_args()
    target = args.target.expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)

    config = json.loads((ROOT / "suite-dependencies.json").read_text(encoding="utf-8"))
    for name in config["bundledSkills"]:
        copy_skill(ROOT / "skills" / name, target / name, args.force)

    if not args.skip_external:
        redskill = locate_redskill()
        for dependency in config["externalSkills"]:
            name = dependency["name"]
            if find_installed(target, name):
                print(f"external skill already present: {name}")
                continue
            if dependency.get("source") != "redskill" or not redskill:
                page = dependency.get("installPage", "https://redskill.xiaohongshu.net/install.md")
                raise SystemExit(f"Red Skill CLI is required. Install it from {page}, then rerun this installer.")
            subprocess.run([redskill, "install", name, "--dir", str(target)], check=True)

    verifier = ROOT / "scripts" / "verify_suite.py"
    if not args.skip_external:
        subprocess.run(["python3", str(verifier), "--target", str(target)], check=True)
    print(target)


if __name__ == "__main__":
    main()

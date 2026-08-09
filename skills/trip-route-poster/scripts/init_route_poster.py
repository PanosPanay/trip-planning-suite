#!/usr/bin/env python3
import argparse
import shutil
from pathlib import Path


def copy_new(source, destination):
    if destination.exists():
        print(f"keep existing: {destination}")
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    print(f"created: {destination}")


def main():
    parser = argparse.ArgumentParser(description="Install the editable route-poster HTML template into a trip project.")
    parser.add_argument("project", type=Path)
    args = parser.parse_args()
    project = args.project.expanduser().resolve()
    assets = Path(__file__).resolve().parents[1] / "assets"
    copy_new(assets / "route-poster.html", project / "maps" / "route-poster.html")
    copy_new(assets / "route-poster.css", project / "maps" / "assets" / "route-poster.css")
    copy_new(assets / "route-poster.js", project / "maps" / "assets" / "route-poster.js")
    copy_new(assets / "route-poster-data.example.json", project / "data" / "route-poster.json")


if __name__ == "__main__":
    main()

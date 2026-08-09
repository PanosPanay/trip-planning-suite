#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def write_new(path, content):
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def main():
    parser = argparse.ArgumentParser(description="Create a portable trip-planning project without overwriting existing files.")
    parser.add_argument("project", type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--language", default="zh-CN")
    args = parser.parse_args()

    project = args.project.expanduser().resolve()
    for relative in ["docs/online-logic", "data", "maps", "screenshots", "output/pdf", "tools"]:
        (project / relative).mkdir(parents=True, exist_ok=True)

    skill_root = Path(__file__).resolve().parents[1]
    itinerary = (skill_root / "assets" / "itinerary-template.md").read_text(encoding="utf-8")
    itinerary = itinerary.replace("{{TRIP_TITLE}}", args.title)

    files = {
        "README.md": f"# {args.title}\n\nCanonical itinerary: `docs/itinerary.md`\n\nMap: `maps/itinerary-map.html`\n",
        "docs/itinerary.md": itinerary,
        "docs/decisions.md": "# Decisions\n\nRecord accepted choices, rejected alternatives, and downstream effects.\n",
        "docs/reservations.md": "# Reservations\n\n| Item | Date | Booking window | Status | Cancellation / notes |\n| --- | --- | --- | --- | --- |\n",
        "docs/sources.md": "# Sources\n\nRecord direct links, claims supported, and checked dates.\n",
        "docs/online-logic/map.md": "# Map Behavior\n\nDocument only behavior implemented in the current map.\n",
    }
    for relative, content in files.items():
        write_new(project / relative, content)

    json_files = {
        "data/trip.json": {
            "title": args.title,
            "language": args.language,
            "dates": {"start": None, "end": None},
            "travelers": {"count": None, "origins": [], "rooms": None},
            "transportMode": None,
            "priorities": [],
            "constraints": [],
            "lastReviewedAt": None,
        },
        "data/pois.json": {"places": []},
        "data/itinerary.json": {"days": []},
        "data/sources.json": {"sources": []},
    }
    for relative, data in json_files.items():
        write_new(project / relative, json.dumps(data, ensure_ascii=False, indent=2) + "\n")

    print(project)


if __name__ == "__main__":
    main()

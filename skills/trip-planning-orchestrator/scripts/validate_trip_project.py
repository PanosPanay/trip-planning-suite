#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


REQUIRED = [
    "README.md",
    "docs/itinerary.md",
    "docs/sources.md",
    "docs/reservations.md",
    "data/trip.json",
    "data/pois.json",
    "data/itinerary.json",
    "data/sources.json",
]


def load_json(path, errors):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid JSON {path}: {exc}")
        return {}


def list_value(data, key):
    if isinstance(data, list):
        return data
    value = data.get(key, []) if isinstance(data, dict) else []
    return value if isinstance(value, list) else []


def main():
    parser = argparse.ArgumentParser(description="Validate the portable trip project contract.")
    parser.add_argument("project", type=Path)
    parser.add_argument("--allow-draft", action="store_true", help="Allow empty dates, days, places, and sources.")
    args = parser.parse_args()

    root = args.project.expanduser().resolve()
    errors = []
    for relative in REQUIRED:
        if not (root / relative).exists():
            errors.append(f"missing {relative}")
    if errors:
        raise SystemExit("\n".join(errors))

    trip = load_json(root / "data/trip.json", errors)
    pois = list_value(load_json(root / "data/pois.json", errors), "places")
    days = list_value(load_json(root / "data/itinerary.json", errors), "days")
    sources = list_value(load_json(root / "data/sources.json", errors), "sources")

    ids = set()
    for poi in pois:
        poi_id = poi.get("id")
        if not poi_id or poi_id in ids:
            errors.append(f"missing or duplicate place id: {poi_id}")
        ids.add(poi_id)
        lat = poi.get("lat", poi.get("latitude"))
        lng = poi.get("lng", poi.get("longitude"))
        coords = poi.get("coordinates")
        if (lat is None or lng is None) and isinstance(coords, list) and len(coords) >= 2:
            lat, lng = coords[:2]
        if not isinstance(lat, (int, float)) or not -90 <= lat <= 90:
            errors.append(f"invalid latitude for {poi_id}")
        if not isinstance(lng, (int, float)) or not -180 <= lng <= 180:
            errors.append(f"invalid longitude for {poi_id}")

    for index, day in enumerate(days, 1):
        if not day.get("date") or not day.get("title"):
            errors.append(f"day {index} needs date and title")
        if not isinstance(day.get("items", []), list):
            errors.append(f"day {index} items must be a list")
        if index < len(days) and not (day.get("overnight") or day.get("stayId")):
            errors.append(f"day {index} is missing an overnight stay")

    itinerary_md = (root / "docs/itinerary.md").read_text(encoding="utf-8")
    required_heading_groups = [
        ("Trip Facts", "行程信息"),
        ("Pre-Trip TODOs", "行前待办"),
        ("Trip Summary", "行程汇总"),
        ("Daily Itinerary", "每日行程"),
        ("Sources", "资料入口"),
    ]
    for alternatives in required_heading_groups:
        if not any(value in itinerary_md for value in alternatives):
            errors.append(f"itinerary is missing a heading like {alternatives[0]}")

    if not args.allow_draft:
        dates = trip.get("dates", {}) if isinstance(trip, dict) else {}
        if not dates.get("start") or not dates.get("end"):
            errors.append("trip dates are incomplete")
        if not days:
            errors.append("itinerary has no days")
        if not pois:
            errors.append("project has no places")
        if not sources:
            errors.append("project has no sources")

    if errors:
        raise SystemExit("\n".join(errors))
    print("trip project valid")


if __name__ == "__main__":
    main()

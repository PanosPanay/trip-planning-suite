#!/usr/bin/env python3
import tempfile
import subprocess
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    skill_md = SKILL / "SKILL.md"
    require(skill_md.exists(), "missing SKILL.md")
    body = skill_md.read_text(encoding="utf-8")
    require("name: trip-planning-orchestrator" in body, "wrong skill name")
    require("description: Use when" in body, "description must be trigger-focused")

    required_refs = {
        "workflow.md",
        "project-contract.md",
        "tool-sources.md",
        "quality-gates.md",
        "lessons-learned.md",
    }
    actual_refs = {path.name for path in (SKILL / "references").glob("*.md")}
    require(required_refs <= actual_refs, f"missing references: {sorted(required_refs - actual_refs)}")

    required_terms = [
        "destination",
        "flight",
        "hotel",
        "Markdown",
        "PDF",
        "dynamic map",
        "route poster",
        "iteration",
        "visual inspection",
    ]
    searchable = "\n".join(
        [body]
        + [path.read_text(encoding="utf-8") for path in (SKILL / "references").glob("*.md")]
    )
    for term in required_terms:
        require(term.lower() in searchable.lower(), f"workflow does not cover {term}")

    sources = (SKILL / "references" / "tool-sources.md").read_text(encoding="utf-8")
    for dependency in [
        "interactive-trip-planner",
        "ctrip-flight-prices",
        "ctrip-hotel-search",
        "trip-route-poster",
        "trip-itinerary-pdf",
        "browser",
    ]:
        require(dependency in sources, f"missing source attribution for {dependency}")

    require((SKILL / "agents" / "openai.yaml").exists(), "missing agents/openai.yaml")
    init_script = SKILL / "scripts" / "init_trip_project.py"
    validate_script = SKILL / "scripts" / "validate_trip_project.py"
    require(init_script.exists(), "missing project initializer")
    require(validate_script.exists(), "missing project validator")
    for removed_fallback in ["check_capabilities.py", "build_trip_map.py", "export_trip_pdf.py"]:
        require(not (SKILL / "scripts" / removed_fallback).exists(), f"reduced fallback should not be bundled: {removed_fallback}")

    with tempfile.TemporaryDirectory() as temp_dir:
        project = Path(temp_dir) / "sample-trip"
        subprocess.run(["python3", str(init_script), str(project), "--title", "Sample Trip"], check=True)
        for relative in [
            "README.md",
            "docs/itinerary.md",
            "docs/sources.md",
            "data/pois.json",
            "data/itinerary.json",
            "data/sources.json",
            "maps",
            "output/pdf",
        ]:
            require((project / relative).exists(), f"initializer missed {relative}")
        subprocess.run(["python3", str(validate_script), str(project), "--allow-draft"], check=True)

    forbidden = ["SAMPLE_BOOKING_CODE", "SAMPLE_PRIVATE_HOTEL", "SAMPLE_TRAVELER_NAME"]
    for value in forbidden:
        require(value not in searchable, f"shareable skill leaked trip-specific data: {value}")

    print("trip-planning-orchestrator contract valid")


if __name__ == "__main__":
    main()

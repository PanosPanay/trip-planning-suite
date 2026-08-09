#!/usr/bin/env python3
import json
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    manifest_path = ROOT / ".codex-plugin" / "plugin.json"
    require(manifest_path.exists(), "missing plugin manifest")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    require(manifest.get("name") == "trip-planning-suite", "wrong plugin name")

    bundled = {
        "trip-planning-orchestrator",
        "ctrip-flight-prices",
        "ctrip-hotel-search",
        "trip-route-poster",
        "trip-itinerary-pdf",
    }
    for name in bundled:
        require((ROOT / "skills" / name / "SKILL.md").exists(), f"missing bundled skill {name}")

    poster_skill = ROOT / "skills" / "trip-route-poster"
    poster_body = (poster_skill / "SKILL.md").read_text(encoding="utf-8")
    for term in ["route-poster.html", "structured", "solid", "dashed", "visual", "approval", "high-resolution"]:
        require(term.lower() in poster_body.lower(), f"route poster skill missed {term}")
    for relative in [
        "assets/route-poster.html",
        "assets/route-poster.css",
        "assets/route-poster.js",
        "scripts/export_route_poster.py",
        "scripts/validate_route_poster.mjs",
    ]:
        require((poster_skill / relative).exists(), f"route poster skill missed {relative}")

    pdf_skill = ROOT / "skills" / "trip-itinerary-pdf"
    require((pdf_skill / "scripts" / "export_itinerary_pdf.py").exists(), "PDF skill missed exporter")
    hotel_skill = ROOT / "skills" / "ctrip-hotel-search"
    require((hotel_skill / "scripts" / "query_ctrip_hotels.py").exists(), "hotel skill missed query script")

    dependencies = json.loads((ROOT / "suite-dependencies.json").read_text(encoding="utf-8"))
    required_external = {item["name"]: item for item in dependencies.get("externalSkills", [])}
    require("interactive-trip-planner" in required_external, "interactive-trip-planner must be an external dependency")
    require(required_external["interactive-trip-planner"].get("required") is True, "interactive-trip-planner must be required")
    require(required_external["interactive-trip-planner"].get("source") == "redskill", "wrong dependency source")

    installer = ROOT / "scripts" / "install_suite.py"
    verifier = ROOT / "scripts" / "verify_suite.py"
    require(installer.exists(), "missing suite installer")
    require(verifier.exists(), "missing suite verifier")
    subprocess.run(["python3", str(installer), "--help"], check=True, capture_output=True, text=True)
    subprocess.run(["python3", str(verifier), "--help"], check=True, capture_output=True, text=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        target = Path(temp_dir) / "skills"
        subprocess.run(
            ["python3", str(installer), "--target", str(target), "--skip-external"],
            check=True,
        )
        for name in bundled:
            require((target / name / "SKILL.md").exists(), f"installer missed {name}")
        result = subprocess.run(
            ["python3", str(verifier), "--target", str(target)],
            capture_output=True,
            text=True,
        )
        require(result.returncode != 0, "verifier should reject a suite missing required external skills")
        require("interactive-trip-planner" in result.stdout + result.stderr, "verifier did not name the missing dependency")

    print("trip-planning-suite contract valid")


if __name__ == "__main__":
    main()

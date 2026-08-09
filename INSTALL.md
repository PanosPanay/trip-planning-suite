# Trip Planning Suite Installation

This bundle installs the complete workflow. It does not provide a reduced mode.

## Install

```bash
python3 scripts/install_suite.py --force
```

The installer copies all bundled child Skills into `${CODEX_HOME:-~/.codex}/skills` and installs the required `interactive-trip-planner` dependency through Red Skill. If the Red Skill CLI is missing, install it from <https://redskill.xiaohongshu.net/install.md> and rerun the command.

## Verify

```bash
python3 scripts/verify_suite.py --run-external-tests
```

The verifier fails when a child Skill or required runtime is absent. Required runtime includes Python, Node.js, Playwright with Chromium, Pandoc, and Poppler.

## Give Another AI

Share the entire `trip-planning-suite` folder or its release ZIP and ask the receiving AI to run the install and verify commands above. After installation, invoke `trip-planning-orchestrator` for a complete new trip.

The route-poster stage always follows this order:

1. Generate `maps/route-poster.html` from structured geographic data.
2. Open and edit the HTML with the user until all annotations and visual checks pass.
3. After explicit approval, export high-resolution landscape and portrait images.


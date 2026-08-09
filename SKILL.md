---
name: trip-planning-suite
description: Use when planning or revising a multi-day trip end to end, especially when live flight and hotel research, iterative itinerary design, dynamic maps, editable route posters, high-resolution images, and shareable PDFs must remain synchronized.
---

# Trip Planning Suite

Use this as the entry point for the complete travel-planning bundle. Do not replace the bundled workflow with a text-only or reduced-capability fallback.

## First use

Resolve this Skill's directory as `<SUITE_DIR>`. Before planning, verify the bundled and external Skills:

```bash
python3 <SUITE_DIR>/scripts/install_suite.py --force
python3 <SUITE_DIR>/scripts/verify_suite.py --run-external-tests
```

The installer must provide all five bundled Skills plus the required `interactive-trip-planner` dependency. If installation or verification fails, report the missing capability and stop instead of silently degrading the deliverable.

## Workflow

Load `skills/trip-planning-orchestrator/SKILL.md` and follow it as the primary workflow. Delegate specialized work to:

- `skills/ctrip-flight-prices/SKILL.md` for live flight comparisons.
- `skills/ctrip-hotel-search/SKILL.md` for hotel availability, rooms, prices, and cancellation policies.
- `interactive-trip-planner` for canonical itinerary data and the clickable daily map.
- `skills/trip-route-poster/SKILL.md` for geographically grounded route posters.
- `skills/trip-itinerary-pdf/SKILL.md` for shareable PDF production and visual verification.

Keep the itinerary Markdown, hotels, map data, route poster, and PDF synchronized as decisions change.

## Non-negotiable output quality

- Use current sources for flights, hotels, tickets, opening hours, traffic, weather, and other time-sensitive facts.
- Treat hotels, meals, rest, airport transfers, congestion buffers, and alternatives as part of the actual route.
- Build route posters from real coordinates and road geometry.
- Produce an editable HTML route-poster page first. Revise it with the user until approved, then export high-resolution landscape and portrait PNG files.
- Draw default routes as solid lines and mutually exclusive or weather-dependent alternatives as dashed lines.
- Prevent labels, icons, distances, driving times, and accommodation markers from covering routes or one another.
- Export the approved Markdown and route image to PDF, render representative pages, and inspect them before delivery.

Read `suite-dependencies.json` for the exact dependency contract and `skills/trip-planning-orchestrator/references/quality-gates.md` before final delivery.

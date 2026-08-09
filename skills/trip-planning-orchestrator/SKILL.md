---
name: trip-planning-orchestrator
description: Use when planning or revising a multi-day trip from destination and live transport research through hotel selection, detailed itinerary files, maps, route posters, and a shareable PDF, especially when the plan will evolve through multiple user conversations.
---

# Trip Planning Orchestrator

## Overview

Orchestrate an end-to-end travel project through the complete child-skill suite. Keep one canonical project on disk so every confirmed decision reaches the itinerary, data, editable HTML maps, high-resolution route images, and final PDF.

## Use This Skill For

- Open-ended destination selection, date optimization, or multi-origin traveler comparisons.
- Iterative planning that continues through flights, hotels, reservations, daily schedules, maps, and a shareable document.
- Revising an existing trip without losing confirmed choices or reintroducing rejected options.

For a single flight lookup, hotel lookup, PDF edit, or map tweak, use the specialized skill directly. This skill is the coordinator when several stages must stay consistent.

## Start Correctly

1. Confirm that `ctrip-flight-prices`, `ctrip-hotel-search`, `interactive-trip-planner`, `trip-route-poster`, and `trip-itinerary-pdf` are installed and callable. If any is missing, stop and run the suite installer; do not substitute a reduced workflow.
2. Read the nearest workspace instructions and the current trip's `README.md`, `docs/`, `data/`, `maps/`, and generation tools. Current files outrank chat memory.
3. If no project exists, run `python3 scripts/init_trip_project.py <project-path> --title "<trip title>"`.
4. Restate only unknowns that can change route, safety, dates, budget, or feasibility. Do not re-ask facts already supplied.
5. Separate every important statement into current fact, inference, or recommendation. Date live quotes and volatile checks.
6. Read [references/workflow.md](references/workflow.md) for the active phase and [references/project-contract.md](references/project-contract.md) before writing files.

## End-to-End Workflow

### 1. Discover Destinations And Transport

Use `ctrip-flight-prices`. Compare realistic trip packages, not isolated cheap fares. For each candidate include all origins, round-trip price snapshots, flight times, usable hours, leave days, transfers, seasonal fit, local transport, and likely crowding. Use live search for volatile data and record the checked time.

Output a small set of meaningfully different destination or route candidates and make a recommendation with tradeoffs. Do not manufacture precision when fares or schedules are unavailable.

### 2. Confirm The Trip Design

Turn the chosen direction into a route proposal: trip theme, route segments, nights, transport mode, must-do experiences, deliberate exclusions, hotel-base logic, and daily anchors. Obtain confirmation on decisions that materially change the skeleton; continue directly when the user has already confirmed them.

### 3. Build And Iterate The Route

Place flights, booked hotels, reservations, sunset windows, and other hard constraints first. Give each day 1-3 main anchors, explicit transfer legs, meals/rest, overnight location, a same-direction fallback, and crowd/weather/safety buffers. Compare real road or transit sequences when order matters.

After every accepted change, update the canonical Markdown and structured data before changing maps or exports. Never let a polished visualization become the only source of truth.

### 4. Select And Track Hotels

Choose the stay area before comparing properties. Evaluate route fit, room type and count, total nightly price, opening/renovation recency as a bonus, rating evidence, parking or transit, altitude and heating/oxygen where relevant, arrival cutoffs, and cancellation policy. Clearly distinguish sold out from inventory not yet released.

Use `ctrip-hotel-search` for discovery and the logged-in browser verification loop. For live prices, log check time and room conditions. Preserve booked hotels and cancellation deadlines as hard constraints. Read the hotel section in [references/workflow.md](references/workflow.md).

### 5. Produce The Detailed Markdown

The itinerary must include trip facts, confirmed flights and hotels, pre-trip TODOs, a compact multi-day summary, and one detailed section per day with timings, segment distances, normal versus peak-period duration, costs, reservations, risks, fallback rules, and overnight stay. Use direct source links near volatile claims.

Use [assets/itinerary-template.md](assets/itinerary-template.md) as a starting shape, then adapt it to the trip rather than filling every field mechanically.

### 6. Build Maps And Route Posters

Use the required `interactive-trip-planner` child Skill for the clickable dynamic map. Use verified coordinates and road/transit geometry; a straight connector is only an order guide and must be labeled as such. Show daily details, stays, transport legs, alternatives, photos, and source links.

Use `trip-route-poster` for the static route artifact. First generate and edit `maps/route-poster.html`; keep it open as the review surface while the user annotates it. Draw the default route as solid lines and mutually exclusive alternatives as dashed lines. Keep labels outside route strokes, use marker numbers and short leader lines, reserve room for legends, and visually inspect for overlap, clipping, overflow, empty framing, and geographic reversals. Export high-resolution landscape and portrait images only after the user explicitly approves the HTML. Read [references/quality-gates.md](references/quality-gates.md) and [references/lessons-learned.md](references/lessons-learned.md) before finalizing either map.

### 7. Export A Shareable PDF

Use `trip-itinerary-pdf`. Prefer a cover, the approved high-resolution landscape route image, a landscape summary table when needed, and portrait detailed pages. Preserve selectable text and working links. Render the final PDF to images and inspect the cover, route page, summary, dense daily pages, and final page before delivery.

### 8. Validate And Deliver

Run `python3 scripts/validate_trip_project.py <project-path>` when the project is complete. Then perform the applicable live and visual checks in [references/quality-gates.md](references/quality-gates.md). Report what was verified, what remains a dated snapshot, and what must be reconfirmed shortly before departure.

## Iteration Rules

- Treat the conversation as progressive specification: summarize each new decision, note affected days, and keep unrelated confirmed choices intact.
- Keep alternatives explicit and mutually exclusive when they cannot fit together.
- Do not update the map or PDF while the user says the route is still under discussion.
- When the user annotates a visual, address every annotation and recheck the whole composition, not only the marked pixels.
- Never claim a source was read when access failed. Ask for a usable browser state or mark the claim unverified.

## Required Dependencies

Read [references/tool-sources.md](references/tool-sources.md) before starting. Every listed child Skill is a hard requirement for the complete workflow. If a dependency is missing or fails verification, repair the installation before continuing; do not silently downgrade the map, poster, hotel, flight, or PDF stage. The external Red Skill is installed from its source rather than copied into this package.

## Reference Index

- Phase details and exit criteria: [references/workflow.md](references/workflow.md)
- Canonical files and data boundaries: [references/project-contract.md](references/project-contract.md)
- Required child skills and origins: [references/tool-sources.md](references/tool-sources.md)
- Automated and visual acceptance checks: [references/quality-gates.md](references/quality-gates.md)
- Reusable mistakes and corrections: [references/lessons-learned.md](references/lessons-learned.md)

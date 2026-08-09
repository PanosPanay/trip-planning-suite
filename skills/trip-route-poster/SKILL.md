---
name: trip-route-poster
description: Use when a finalized or nearly finalized trip needs a geographically grounded, editable route-poster.html with daily routes, stays, alternatives, detail insets, and high-resolution landscape or portrait image exports.
---

# Trip Route Poster

## Core Contract

Build the route poster from structured trip data and real coordinates/route geometry. The editable `route-poster.html` is the review surface; high-resolution images are derivative artifacts generated only after explicit user approval.

## Initialize

```bash
python3 scripts/init_route_poster.py <trip-project>
```

This copies the generic HTML/CSS/JS poster template and creates `data/route-poster.json` only when absent. Replace the example data with the trip's days, points, solid default segments, dashed optional segments, labels, and insets.

## Data And Geography

- Point coordinates determine geographic position. Never manually reverse left/right placement to make a prettier story.
- Default segments need road/transit geometry and use solid lines.
- Mutually exclusive alternatives use dashed lines, endpoint labels, and activation conditions.
- Segment distance and time are planning values with provenance; holiday buffers belong in text labels, not invented geometry.
- Configure point callout offsets and widths in structured `poster` fields rather than hard-coding a destination into the renderer.

Run:

```bash
node scripts/validate_route_poster.js <trip-project>/data/route-poster.json
```

## HTML Review Loop

1. Start a local server from the trip project and open `maps/route-poster.html?layout=landscape`.
2. Adjust JSON offsets, widths, inset bounds, and CSS while the user comments on the HTML.
3. Address every annotation. Reinspect all labels, marker numbers, stays, distance/time chips, default and optional lines, legend, day strip, insets, and page edges.
4. Do not export screenshots when the user says to keep editing.

Visual acceptance requires no route/label overlap, text overflow, clipped content, incorrect geographic order, hidden dashed branches, crowded numbers, or wasted empty map area. Move labels outside the route and use short leader lines. Use matching marker and label tokens.

## High-Resolution Export

Only after explicit approval:

```bash
python3 scripts/export_route_poster.py <trip-project> --approved --scale 3
```

The exporter runs the editable HTML through a local server, waits for the poster and map tiles, and captures fixed 1920x1350 landscape and 1440x2200 portrait canvases at device scale. Inspect both exported images at full size and normal sharing size before delivery.

Read [references/review-checklist.md](references/review-checklist.md) for the complete visual pass.

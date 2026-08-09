# Canonical Trip Project Contract

## Directory Shape

```text
trip-project/
  README.md
  docs/
    itinerary.md
    decisions.md
    reservations.md
    sources.md
    online-logic/map.md
  data/
    trip.json
    pois.json
    itinerary.json
    sources.json
  maps/
    itinerary-map.html
  screenshots/
  output/pdf/
  tools/
```

Empty output files need not exist during early discovery. Use `scripts/init_trip_project.py` to create a portable draft.

## Source Of Truth

- `docs/itinerary.md`: traveler-facing canonical plan.
- `data/itinerary.json`: ordered daily route and movement data used by maps.
- `data/pois.json`: reusable places with coordinates, roles, evidence, and notes.
- `data/sources.json`: dated evidence for volatile facts.
- `docs/decisions.md`: accepted choices, rejected alternatives, and why.
- `docs/reservations.md`: booking windows, status, cancellation deadlines, and confirmation needs.
- `docs/online-logic/map.md`: what the current map actually supports.

The Markdown and structured data must agree. A map or PDF is a derivative artifact and never the only record of a decision.

## Minimum Structured Data

`trip.json` should record title, language, dates, travelers, origins, transport mode, room needs, priorities, constraints, and last review time.

Each POI should have a stable ID, localized name, role, latitude/longitude, area, why it fits, visit duration, booking/cost status, source IDs, and last verification date where applicable.

Each day should have date, title/theme, start, ordered items, movement legs, overnight stay, fallback, risk notes, and decision cutoffs. A movement leg should distinguish route distance, normal duration, peak-period budget, mode, geometry provenance, and navigation/recheck needs.

Each source should have ID, title, direct URL, publisher, checked time, supported claim, and source type. Search result pages and AI summaries are discovery aids, not final evidence.

## Privacy And Sharing

Before packaging or publishing:

- Remove traveler names, phone numbers, IDs, booking codes, cookies, browser profiles, local temporary paths, and payment details.
- Keep flight numbers or hotel names only in a trip artifact when the user intends to share them; never embed one trip's bookings in a reusable skill.
- Do not bundle logged-in browser state or copied third-party skill implementations.
- Prefer templates and schemas over a full personal trip as the example.

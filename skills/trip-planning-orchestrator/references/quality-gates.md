# Quality Gates

## Research

- Dates, traveler origins, group size, room requirements, budget, and hard constraints are explicit.
- Live fares, room prices, schedules, hours, tickets, policies, closures, and road status have a checked date and direct source.
- Recommendation compares total trip utility, not only headline price.
- Unverified claims are labeled; inaccessible referenced pages are not paraphrased as if read.

## Itinerary

- Every calendar day is present and numbered without gaps.
- Arrival, departure, cross-region travel, hotel check-in, meals/rest, and overnight stay are visible itinerary items.
- Every driving/transit leg has mode and duration; critical legs include distance and peak-period budget.
- Each day has 1-3 anchors, a removable low-priority item, and a weather/crowd/energy fallback.
- Bookings, cancellation deadlines, ticket windows, costs, and eligibility policies are in TODOs and the relevant day.
- A user change has not silently invalidated later hotels or return transport.

## Hotels

- Stay area supports previous arrival and next departure.
- Requested room type and count are checked, not inferred from a hotel's general availability.
- Price unit, taxes/fees, breakfast, prepayment, arrival cutoff, and cancellation are clear.
- Opening/renovation recency is a bonus signal, not the sole ranking criterion.
- "Sold out", "not released", and "login to view" remain distinct.

## Dynamic Map

- Coordinates are plausible and place names match the itinerary.
- Claimed routes follow verified road/transit geometry; guide lines are labeled as guides.
- Daily tabs contain stops, movement, stay, and alternatives in the correct order.
- Details, filters, route state, refresh persistence, external links, desktop, and mobile are tested.
- No blank map, missing tiles, console errors, or UI overlap.

## Route Poster

- Geographic orientation and left/right placement agree with coordinates.
- Default lines are solid; alternatives are dashed, named, separated, and endpoint-labeled.
- POI labels, stay badges, numbered markers, day labels, distance/time chips, leader lines, route strokes, legend, and inset labels do not overlap.
- Long names wrap inside boxes. Nothing clips at page edges or spills below the canvas.
- Labels sit beside the route when possible. Use a short leader line instead of covering the road.
- Dense markers are offset or grouped without obscuring their day/point numbers.
- Empty map regions are cropped; detail insets use the freed space.
- Inspect at full size and at normal sharing size on both landscape and portrait exports.

## PDF

- Text is selectable, links work, and the file opens without warnings that affect readers.
- Cover, route page, summary, dense daily pages, and final page are visually inspected after rendering to images.
- Portrait/landscape transitions do not create a blank or heading-only page.
- Tables do not clip, headings do not orphan, and footer/page numbers stay inside margins.
- High-resolution maps remain legible when zoomed; use fixed canvas export with device scale 2 or higher instead of stitched long-page screenshots.

## Final Delivery

- Run `scripts/validate_trip_project.py` and project-specific validators.
- State what was verified, what is a dated snapshot, and what requires pre-departure reconfirmation.
- Deliver the canonical Markdown, map, route poster, and PDF paths without exposing private temporary data.

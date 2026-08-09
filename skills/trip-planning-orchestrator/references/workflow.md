# Workflow And Exit Criteria

## Contents

1. Intake and destination discovery
2. Flight and transport comparison
3. Route design and iteration
4. Hotel selection
5. Detailed itinerary
6. Maps, route poster, and PDF
7. Change protocol

## 1. Intake And Destination Discovery

Capture dates and flexibility, traveler origins, leave-day constraints, group size, room needs, budget, transport preference, physical limits, interests, must-do and avoid lists, passports/visas when relevant, and existing bookings. Ask only questions that can change feasibility or route structure.

Compare destination candidates using a decision table:

- Total travel cost and whether quoted fares include both directions.
- Flight times and the usable portion of arrival/departure days.
- Shared-destination affordability for every origin.
- Seasonal scenery, weather, daylight, holidays, closures, and crowding.
- Ground transport, altitude, driving load, and required leave days.
- Experience fit and what must be sacrificed.

Exit when the user has selected a destination/route family and travel dates, or when one recommendation is clearly superior and the user accepts it.

## 2. Flight And Transport Comparison

Use live flight or rail data. Record search time, origin/destination, dates, direct/transfer status, departure/arrival, airport/station, baggage or fare caveats, and observed price. When travelers depart from different cities, optimize the whole group rather than finding one cheap origin.

Treat prices as snapshots. Do not mix a one-way fare with a round-trip total. If a platform exposes ambiguous package pricing, label it and verify in the booking flow before recommending payment.

Exit when the route has realistic arrival/departure hard constraints and a fallback transport option where disruption would break the trip.

## 3. Route Design And Iteration

Build from hard constraints outward:

1. Flights, trains, booked rooms, timed reservations, closures, and sunsets.
2. Overnight bases and transfer days.
3. One to three daily anchors.
4. Meals, rest, luggage, fuel/charging, and safe return windows.
5. Same-direction weather, crowd, and physical-effort alternatives.

Always show transfer legs as itinerary items. Split normal drive time from holiday or disruption budget. For mountain or holiday routes, include cutoff rules such as: "If ETA passes 18:20, skip sunset and go directly to the hotel."

Exit when every day has a start, ordered stops, movement, food/rest, overnight location, time buffer, and a clearly removable low-priority item.

## 4. Hotel Selection

Choose an area based on the previous day's arrival and next day's first movement. Then compare at least three to five realistic properties when inventory permits.

Record:

- Exact stay date, area, and why the area works.
- Property name, room type, number of rooms, room size, and observed total price.
- Opening or renovation year when verified; recent inventory is a bonus, not a substitute for location.
- Rating, review volume, heating/air-conditioning, elevator, parking, breakfast, airport transfer, altitude support, and arrival cutoff as relevant.
- Free-cancellation deadline, prepayment, invoice, and no-show policy.
- Check time and direct booking URL.

Inventory rules:

- "Sold out" requires a real availability result for the requested dates/rooms.
- "Not released" is a separate state when future holiday inventory may not be open.
- Login-only pricing is not a numeric quote until the logged-in booking page is read.
- Preserve refundable backup bookings when a weather-dependent route may change the overnight base.

Exit when each night has a chosen stay or a documented booking decision, plus a backup for high-risk nights.

## 5. Detailed Itinerary

The Markdown should contain:

- Trip facts and explicit planning principles.
- Pre-trip TODOs with booking windows and responsible channel.
- Confirmed flights, rooms, cancellation rules, and reservation status.
- A compact summary table covering route, drive/transit budget, hotel, and experience.
- Daily timelines with segment distance/time, activities, meals/rest, cost, tickets, risks, cutoff rules, and overnight stay.
- Alternative branches and the conditions that activate them.
- A source section and a dated pre-departure recheck list.

Exit when a traveler can execute the trip from the document without reconstructing decisions from chat.

## 6. Dynamic Map, Route Poster, And PDF

Dynamic map requirements:

- Overview, day navigation, ordered stops, movement legs, stay anchors, filters, details, and source/navigation links.
- Real route geometry where claimed; otherwise clearly labeled sequence guidance.
- Alternatives visibly different from the default and explained as mutually exclusive when applicable.

Route poster requirements:

- Geographic position is derived from coordinates and the map projection.
- Day colors, numbered markers, stays, distances, drive-time labels, insets, and a legend are consistent.
- Default route is solid; optional branches are dashed and labeled at their endpoints.

PDF requirements:

- Cover, route overview, summary, daily detail, TODOs/bookings, and source links.
- Correct page orientation and no blank transition page between portrait and landscape sections.

Exit only after visual inspection at intended share and zoom sizes.

## 7. Change Protocol

For every user revision:

1. State the accepted change and affected days.
2. Recompute downstream transport, hotel, reservation, and safety effects.
3. Update canonical Markdown and structured data.
4. Update dynamic map and poster only after route text is agreed.
5. Re-export the PDF last.
6. Rerun validation and visually inspect changed and neighboring areas.

Do not silently resurrect rejected destinations or delete confirmed stays while solving a local change.

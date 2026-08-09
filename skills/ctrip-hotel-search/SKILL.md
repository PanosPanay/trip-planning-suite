---
name: ctrip-hotel-search
description: Use when researching current Ctrip hotel availability, room prices, room type and count, opening or renovation recency, ratings, location, arrival limits, and cancellation policy for specific travel dates.
---

# Ctrip Hotel Search

## Purpose

Find realistic hotel candidates for a known stay area and then verify the exact room offer. Discovery results are not sufficient evidence for cancellation, breakfast, or the ability to book multiple twin rooms.

## Workflow

1. Confirm check-in/out, city or scenic area, traveler count, room count, required bed type, price ceiling, location anchor, and refundable requirement.
2. If logged-in pricing is needed, run:

```bash
python3 scripts/query_ctrip_hotels.py --login-only --headed
```

The browser profile is stored outside the skill and is never included when sharing.

3. Run discovery with the requested dates and room count:

```bash
python3 scripts/query_ctrip_hotels.py \
  --city 2 --keyword "成都南站" \
  --checkin 2026-10-01 --checkout 2026-10-02 \
  --rooms 2 --adults 4 --include "成都南站,桔子水晶" --json-out results.json
```

4. Open the top candidates in the logged-in browser. Verify the exact twin-room inventory for all requested rooms, total nightly price, taxes/fees, breakfast, prepayment, cancellation deadline, no-show rule, arrival cutoff, room size, opening/renovation year, and direct booking URL.
5. Return at least five options when real inventory permits. Rank location and route fit before cosmetic recency; treat a property opened or renovated in the last two years as a bonus.
6. Record query time and note that price/inventory are snapshots.

## Inventory Language

- Use **sold out** only when the requested dates, room count, and room type return no inventory.
- Use **not released** when a future holiday date may not yet be open.
- Use **login required** when the platform withholds price.
- Do not quote a list-page price as the exact twin-room price until the room offer is opened.

## Required Output Columns

Hotel, stay area, route rationale, verified room and room count, observed total price, opening/renovation evidence, rating/review evidence, key facilities, free-cancellation deadline, arrival warning, query time, and direct link.

For route-base and backup-booking rules, follow `$trip-planning-orchestrator`.

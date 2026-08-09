---
name: ctrip-flight-prices
description: Query Ctrip flight prices for one-way or round-trip itineraries, given origin, destination, departure date, and optional return date. Use when Codex needs to research current Ctrip/携程 airfare, compare flights by price, sort results from cheapest to most expensive, or help plan China domestic trips using live flight prices.
---

# Ctrip Flight Prices

## Quick Start

Use the bundled script whenever a user asks for current Ctrip airfare.

```bash
python3 scripts/query_ctrip_flights.py 深圳 丽江 2026-06-01
python3 scripts/query_ctrip_flights.py 深圳 丽江 2026-06-01 --return-date 2026-06-12
python3 scripts/query_ctrip_flights.py SZX LJG 2026-06-01 --return-date 2026-06-12 --limit 20
```

The script accepts Chinese city names or three-letter airport/city codes. It prints a price-sorted table and can emit JSON with `--json`.

## Workflow

1. Run `scripts/query_ctrip_flights.py` with origin, destination, departure date, and optional `--return-date`.
2. If Playwright is missing, install it in the active environment and run `python3 -m playwright install chromium`.
3. If the script cannot resolve a city, rerun with the airport code, for example `SZX`, `ZUH`, `LJG`, `DLU`, `DIG`, or `KMG`.
4. Treat results as a live quote snapshot. Tell the user when the query was run and recommend rechecking before payment.

## Notes

- Ctrip changes page internals often. The script deliberately extracts prices from both network JSON responses and rendered page text, then deduplicates and sorts candidates.
- For round trips, Ctrip may expose total package prices or separate outbound/inbound prices depending on the page state. Prefer candidates marked with richer airline/time context.
- If the page blocks automation, rerun with `--show-browser` so Codex can inspect the browser state or let the user complete verification manually.

---
name: trip-itinerary-pdf
description: Use when a finalized trip Markdown document and approved route-poster image need to become a polished, shareable PDF with selectable text, working links, mixed page orientations, and rendered-page visual QA.
---

# Trip Itinerary PDF

## Contract

Export only from the canonical itinerary Markdown. When a route poster is included, use the user-approved high-resolution image produced from the editable route-poster HTML. Do not rebuild route content independently inside the PDF.

Required runtime: Pandoc, Python Playwright with Chromium, and Poppler (`pdftoppm`). Missing runtime is a hard failure.

## Export

```bash
python3 scripts/export_itinerary_pdf.py <trip-project> \
  --source docs/itinerary.md \
  --poster screenshots/route-poster-landscape-ultra-hd.png \
  --output output/pdf/itinerary-share.pdf
```

The exporter creates print HTML, a PDF, and rendered page previews under `tmp/pdf-preview/`. It uses a portrait cover and detailed pages, plus landscape route and summary pages when present.

## Visual QA

Inspect the rendered PNG pages, not only the PDF metadata. Check:

- cover, route image, summary table, densest daily page, and final page;
- no blank or heading-only page at orientation changes;
- no clipped tables, orphan headings, footer collisions, or text overflow;
- route text remains readable at 100% and when zoomed;
- links remain clickable and body text remains selectable.

Fix the Markdown or print CSS and export again until the rendered pages pass. Never call a PDF complete based only on a successful command exit.


# Required Child Skills And Sources

The suite is complete only when every row below is available. Missing capabilities are installation failures, not prompts to produce a reduced artifact.

| Capability | Required skill/tool | Source and role |
| --- | --- | --- |
| Deep itinerary and clickable dynamic map | `interactive-trip-planner` | External Red Skill, installed from `https://redskill.xiaohongshu.net/install.md`; verified with version 0.0.2. Provides staged research, canonical trip data, daily detail panels, photos, alternatives, and interactive-map validation. Its source is not copied into this bundle. |
| Live Ctrip flights | `ctrip-flight-prices` | Bundled from the locally verified Codex Skill; queries current one-way/round-trip results and records dated snapshots. |
| Ctrip hotel research | `ctrip-hotel-search` | Bundled suite child Skill; combines discovery with persistent logged-in browser verification for exact room count, room type, price, breakfast, arrival cutoff, and cancellation. |
| Editable static route poster | `trip-route-poster` | Bundled suite child Skill derived from the validated West Sichuan workflow: structured geographic data -> editable HTML -> annotation loop -> approved high-resolution image export. |
| Shareable itinerary PDF | `trip-itinerary-pdf` | Bundled suite child Skill: Markdown -> print HTML -> PDF -> rendered-page visual QA. |
| Browser and filesystem runtime | Codex Browser/Computer Use plus local commands | Required for reading supplied pages, persistent login, editing project files, and rendering artifacts. |

## Source Rules

- Official destination, venue, operator, ticketing, transport, and policy pages outrank community posts for hours, price, eligibility, closures, and safety.
- Community content is useful for experience and recent friction, but should not be the only evidence for volatile operational facts.
- Use direct page links near claims. Record when each volatile source was checked.
- Run the suite installer before first use. It installs all bundled child Skills and invokes Red Skill for `interactive-trip-planner`.
- Run the suite verifier after installation. Python, Node.js, Playwright/Chromium, Pandoc, and Poppler are hard runtime checks because the requested deliverables include dynamic maps, editable HTML posters, high-resolution PNGs, and visually verified PDFs.
- Do not report the suite as ready when any required dependency is absent.

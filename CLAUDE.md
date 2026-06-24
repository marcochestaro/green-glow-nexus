# Marco's Dashboard — Standing Rules

This is @marcomarkets' personal Instagram + Meta ads command center.
Every rule below applies permanently. Never break these without Marco explicitly asking.

---

## Git / Deploy

- Always push to `main` immediately. The `sync-dashboard.yml` workflow auto-syncs to `gh-pages` and the site goes live.
- Never push to a feature branch without Marco asking.
- All logic lives in a single file: `dashboard/index.html` (inline HTML/CSS/JS).

---

## Weekly Scripts — Content Rules

### CTA rule (most important)
- Max **2 out of 7 videos per week** may have any CTA (pitch, "DM me ADS", "follow @marcomarkets").
- The script spoken lines and the captions must **always match** — if a caption has no CTA, the script Close must also have no CTA, and vice versa.
- Non-CTA videos end the script Close with a clean value statement — no ask, no pitch, no "follow".
- CTA videos: Close line says the CTA, and at least one caption option can include it.

### Captions — josh.hills0 style
- Always 3 options: A, B, C.
- All lowercase, conversational.
- No hashtags (or max 1–2 only).
- Option A: 1–2 lines, pure insight, no CTA.
- Option B: 2–3 lines expanding the idea (long only if the hook teases "see the caption" — then B can be the full 5–10 line breakdown).
- Option C: one sentence — the core point only.
- No pitching on non-CTA videos in any caption option.

### Script tone
- Professional and confident — sounds like someone who knows exactly what they're doing and has seen the results.
- Chill and easy to follow — like a knowledgeable friend, not a hype guy or corporate marketer.
- Never self-deprecating or "figuring it out" — Marco is the authority on Meta ads for service businesses.
- Conversational but sharp. Never stiff. Never salesy.
- Never use "tradies" — say "service business owners", "business owners", or name the trade directly.
- Scripts are for Instagram and TikTok.
- **Majority Talking Head** — most weeks should be 4-5 Talking Head, 1 Screen Record, 1 Carousel.

### Script lines
- Strong hook first (3–5s), real value in the middle, clean close.
- Close line: CTA only on the 2 allowed videos; otherwise end on insight.
- Script and captions must never contradict each other on CTA.

### Post format
- Every script shows a badge: 🎬 Reel (+ share to Stories after) for Talking Head / Screen Record, 📸 Carousel Post for Carousel.

### Script version toggle
- Short = hook + close only.
- Medium = hook + first half of middle lines + close.
- Full = everything.

---

## Miro Carousel Boards

- Created automatically every Sunday via `scripts/create_miro_boards.py`.
- 42 unique topics in the pool — **topics never repeat**. Pool stops when exhausted (does not reset).
- 3 new boards created per week.
- Requires `MIRO_ACCESS_TOKEN` GitHub Actions secret.

---

## Dashboard — Agent Action System

- Each agent (Ads, Creative, Critic, Competitor) allows **1 pick per week**.
- Picking locks the row, shows where it went, and allows undo.
- Picks persist in `localStorage` (`mm_used_actions`).
- Picked items appear in a dedicated "From Agents" section inside Tomorrow's Plan.
- 3 action options: Turn into Reel script (recommended), Add to tomorrow's plan, Copy text.

---

## Caption A/B/C Switcher

- Uses `CAP_STORE` JS object (not DOM attributes) to avoid encoding issues with apostrophes.
- Context-prefixed IDs: `cap-today-0`, `cap-modal-0`, `cap-wk-0` to avoid duplicate IDs.

---

## General Preferences

- Never use Claude API calls unless truly necessary — prefer free alternatives.
- Script generation model: `claude-haiku-4-5-20251001`.
- Never add comments explaining what code does — only add a comment if the WHY is non-obvious.
- Don't pitch every video. Marco's brand is pure value first.
- Always apply every rule above when generating or updating weekly scripts, not just the current week.

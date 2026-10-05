# Work 015 decisions

### DEC-015-1 — Responsive optimization, no redesign

**Decision:** Preserve the Sulocraft visual identity and desktop hero composition. Change only responsive behavior needed to make mobile browsing more compact.

**Reason:** The current desktop treatment is already accepted; the issue is that the hero dominates the mobile first screen.

**Impact:** Do not change site palette, typography, homepage section order, or campaign count as part of this work.

### DEC-015-2 — Keep hero content and assets backend-driven

**Decision:** Hero text, links, campaign order, visibility, and responsive image URLs remain backend-managed. The frontend owns layout and rendering only.

**Reason:** Campaigns are administered as data and must remain reusable without source edits.

**Impact:** If mobile-specific image data is needed, expose a compatible API/admin field and use the desktop image as a fallback; do not hardcode image paths or campaign copy.

### DEC-015-3 — Compact mobile first screen

**Decision:** Target a 300–340px mobile hero, with no `100vh`/`100svh` takeover, and make the next homepage section discoverable in the first viewport where practical.

**Reason:** Mobile visitors should see the campaign and get an early hint of products/categories below it.

**Impact:** Use only one heading, one short supporting line, and one CTA on mobile; avoid layout shift and clipping.

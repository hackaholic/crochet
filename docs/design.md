# Design system

This is the source of truth for visual work. Do not introduce a new font, colour, shadow, border radius, or button style without first updating this document and `src/index.css`.

## Brand direction

Sulocraft should feel warm, handmade, quietly premium, and approachable. Use soft paper-like backgrounds, earthy contrast, floral accents, generous whitespace, and gentle motion. Avoid neon colours, glass effects, or sharp-cornered controls.

## Typography

| Role | Family | Weight | Rule |
| --- | --- | --- | --- |
| Display and headings | Playfair Display | 400–600 | Use for page titles and meaningful product names only |
| Body and interface | Nunito | 400–800 | Use for navigation, copy, forms, labels, prices, and buttons |

Use the existing `--font-serif` and `--font-sans` tokens. Do not add another typeface.

## Colour system

Use the existing Tailwind theme tokens in `src/index.css`.

| Token | Hex | Intended use |
| --- | --- | --- |
| `cream` | `#FAF7F2` | Primary page background |
| `cream-dark` | `#F5EDE0` | Soft panels and hover backgrounds |
| `ink` | `#2C1810` | Main text and dark footer surface |
| `brown-dark` | `#5C3D2E` | Strong secondary text |
| `brown` | `#8B6B4A` | Muted text and supporting icons |
| `terracotta` | `#C4622D` | Primary actions, links, and focus accents |
| `terracotta-light` | `#D4795A` | Primary-action hover state |
| `terracotta-pale` | `#F5E0D3` | Warm callouts and soft accents |
| `blush` | `#F2C4CE` | Romantic category accents |
| `blush-mid` | `#E8A5B5` | Stronger blush accent only |
| `sage` | `#8FAF8C` | Success states and natural accents |
| `sage-light` | `#C2D9BF` | Soft success backgrounds |
| `sage-pale` | `#EBF3EA` | Success panels |
| `lavender` | `#C5B9D6` | Supporting collection accent |
| `lavender-pale` | `#EDE9F5` | Soft supporting backgrounds |
| `beige` | `#EDE4D0` | Borders and neutral decoration |

Rules: use `ink` or `brown-dark` for readable text; reserve terracotta for the main action on a view; use pale colours as backgrounds, not text; use sage only for positive status; do not use raw hex values in new components when a token exists.

## Layout and components

| Element | Standard |
| --- | --- |
| Storefront width | Full viewport via `.storefront-shell`, with fluid `clamp(1rem, 3vw, 4rem)` side gutters and no global maximum width |
| Readable content | Constrain prose, forms, checkout steps, dialogs, and hero copy locally; do not constrain the surrounding section |
| Panels and cards | White or cream surface, `rounded-xl` or `rounded-2xl`, subtle beige border |
| Primary button | Terracotta fill, white semibold Nunito label, fully rounded |
| Secondary button | Cream or white surface, brown text, beige border, fully rounded |
| Inputs | White surface, beige border, brown text, visible terracotta focus state |
| Product imagery | Consistent portrait frame (`aspect-[3/4]`) matching category highlights, with `object-cover`, rounded corners, and meaningful alt text |
| Motion | 200–300ms ease-out transitions; no looping decorative motion unless it communicates state |

## Responsive rules

Start with a narrow layout, retain checkout and cart actions at every width, and make tap targets at least 44px high or wide. Grids should collapse before text or controls become cramped. Do not rely on hover for an action that mobile users need. Verify the final render in Chrome/Chromium, Firefox, and the mobile viewport matrix in `docs/testing-plan.md`; account for Firefox font metrics and test the longest database-driven content.

Storefront discovery surfaces—including the hero, category grids, product collections, promotions, reviews, header, and footer—must use the available viewport width. Use full-bleed section backgrounds and `.storefront-shell` for responsive gutters. On wide screens, add useful columns or horizontal rail capacity instead of stretching a narrow centered layout. Text blocks retain sensible line lengths inside the full-width section. Operational pages such as authentication, checkout, account forms, and long-form prose may remain constrained for readability and task focus.

## Assets and content

Current product photography includes placeholder content from Unsplash and generated campaign artwork. Replace or approve every production asset before launch. Product names, prices, reviews, delivery promises, and social links remain prototype content until confirmed.

## Change control

Record material visual changes in [decisions.md](decisions.md), especially changes to this palette, typography, component rules, navigation, or product-card behaviour.

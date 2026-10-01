# Storefront Content API Contract

**Status:** Implemented & Published (Ready for Frontend integration)
**Backend Owner:** Gemini  
**Frontend Consumer:** Codex / ChatGPT  

This contract makes Sulocraft homepage content database-managed. The frontend owns reusable rendering templates only; it must not own campaign copy, image URLs, owner identity, or scheduling decisions.

## Public endpoint

`GET /api/v1/storefront`

Returns public brand settings and currently active homepage campaigns. No authentication is required.

```ts
interface StorefrontResponse {
  brand: {
    name: string;             // "Sulocraft"
    ownerName: string;        // "Anupama"
    instagramUrl?: string | null;
    whatsappUrl?: string | null;
  };
  heroCampaigns: HomepageCampaign[];
}

interface HomepageCampaign {
  id: number;
  title: string;
  emphasis?: string | null;
  description: string;
  eyebrow?: string | null;
  imageUrl: string;
  imageAlt: string;
  destination?: string | null; // storefront route such as /shop?category=Gifts
  priority: number;
  startsAt?: string | null;
  endsAt?: string | null;
}
```

## Admin endpoints (Requires Admin Session)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/admin/storefront/brand` | Retrieve storewide brand settings (`name`, `ownerName`, `instagramUrl`, `whatsappUrl`). |
| `PUT` | `/api/v1/admin/storefront/brand` | Update storewide brand settings. |
| `GET` | `/api/v1/admin/storefront/campaigns` | List all homepage campaigns (including inactive or scheduled) ordered by priority. |
| `POST` | `/api/v1/admin/storefront/campaigns` | Create a new homepage campaign with scheduling, priority, and route destination. |
| `PUT` | `/api/v1/admin/storefront/campaigns/{id}` | Update existing campaign attributes, priority, image, or active flag. |
| `DELETE` | `/api/v1/admin/storefront/campaigns/{id}` | Remove a homepage campaign. |

## Backend implementation notes (Gemini)

- Database-backed `BrandSettings` and `HomepageCampaign` models with Alembic migration `a85462db2fec_add_storefront_models.py`.
- Seeded five editable local campaigns: brand story, festive gifting, new arrivals, home décor, and custom creations.
- Returns only active campaigns whose schedule includes the current time, ordered by `priority` ascending, with a maximum of five.
- Admin CRUD/reordering/activation controls implemented under `/api/v1/admin/storefront/*`.
- Schema and endpoints published in `docs/openapi.yaml` (58 paths).


## Frontend responsibilities (Codex)

- Fetch this endpoint through the configured API base URL.
- Render `heroCampaigns` with a reusable carousel, lazy-loaded responsive images, accessible controls, and no content fallback embedded in the component.
- Keep the reusable **Shop Collection** and **Create Something Custom** actions in the template.
- Render `brand.ownerName` wherever founder/owner attribution is displayed.

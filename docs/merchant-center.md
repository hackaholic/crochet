# Google Merchant Center & Free Listings Integration

**Status:** Backend Feed Implemented; Owner Account Setup Ready

Sulocraft publishes an automated, dynamic product data feed strictly adhering to the [Google Merchant Center Product Data Specification](https://support.google.com/merchants/answer/7052112).

---

## 1. Feed Endpoints

| Feed Type | URL Path | Format / MIME | Purpose |
| --- | --- | --- | --- |
| **Primary XML Feed** | `/api/v1/seo/merchant-feed.xml` | `application/xml; charset=utf-8` (RSS 2.0 + `g:` namespace) | Production feed registered in Google Merchant Center for scheduled daily fetching |
| **Inspection JSON Feed** | `/api/v1/seo/merchant-feed` | `application/json` | Programmatic verification, automated testing, and admin audit |

In production, the feed is served from `https://sulocraft.com/api/v1/seo/merchant-feed.xml`. In preproduction and local development, feed links and image links safely resolve against the configured environment base URL (e.g. `https://dev.sulocraft.com` or `http://localhost:8080`).

---

## 2. Product Data Attribute Mapping

| Google Attribute | Sulocraft Data Source | Format / Value | Notes |
| --- | --- | --- | --- |
| `g:id` | `ProductVariant.sku` | String (e.g. `SULO-FLR-ROSE-001`) | Stable unique SKU identifier across feeds and orders |
| `g:title` | `Product.name` + `ProductVariant.name` | String, max 150 chars | Appends variant name if distinct (e.g. `Forever Crochet Rose Bouquet - 5 Roses / Deep Crimson`) |
| `g:description` | `Product.description` / `short_description` | Plain text, max 5000 chars | Clean, human-readable handcrafted details; XML-escaped |
| `g:link` | `{base_url}/products/{Product.slug}` | Absolute URL | Canonical landing page matching storefront canonical URL |
| `g:image_link` | `Product.primary_image` | Absolute URL (R2 CDN or origin) | High-resolution primary image (1024x1024 PNG) |
| `g:additional_image_link` | `ProductImage` gallery | Up to 10 absolute URLs | Additional angles, close-ups, and lifestyle shots |
| `g:availability` | `ProductVariant.stock_quantity > 0` | `in_stock` \| `out_of_stock` | Real-time parity with database inventory |
| `g:price` | `ProductVariant.price` or `compare_at_price` | `XXXX.XX INR` (e.g. `2599.00 INR`) | Regular selling price with ISO 4217 currency |
| `g:sale_price` | `ProductVariant.price` | `XXXX.XX INR` (optional) | Populated only when genuine `compare_at_price > price` |
| `g:brand` | `Product.brand` | `Sulocraft` | Official brand identity |
| `g:condition` | Constant | `new` | All items are newly handcrafted crochet creations |
| `g:item_group_id` | `Product.slug` | String (e.g. `forever-crochet-rose-bouquet`) | Groups variants of the same product together in Google Shopping |
| `g:identifier_exists` | Constant | `no` | **Truthful declaration:** Custom handmade goods without manufacturer GTIN/MPN |
| `g:product_type` | `Category` hierarchy | String (e.g. `Bouquets > Roses`) | Visible storefront navigation ancestry |
| `g:shipping_weight` | `ProductVariant.weight` | e.g. `350 g` (optional) | Item weight in grams when recorded |
| `g:custom_label_0` | `Product.badge` | e.g. `Bestseller`, `New` (optional) | Merchandising badge |
| `g:custom_label_1` | Primary `Collection.name` | e.g. `Gifts for Her` (optional) | Curated collection association |

---

## 3. Truthful Identifier Policy

> [!IMPORTANT]
> **No Fabricated GTINs or MPNs:**  
> Sulocraft products are handcrafted, direct-to-consumer artisanal creations. They do not have manufacturer Global Trade Item Numbers (UPC, EAN, ISBN) or manufacturer part numbers. In compliance with Google's specification, `<g:identifier_exists>no</g:identifier_exists>` is explicitly set, and fake GTIN/MPN values are never emitted.

---

## 4. Product Eligibility Rules

Only items meeting all of the following criteria are exported to the feed:
1. **Product Status:** `Product.status == "ACTIVE"`. `DRAFT` and `ARCHIVED` products are strictly excluded.
2. **Variant Status:** `ProductVariant.status == "ACTIVE"`. Inactive or deleted variants are excluded.
3. **Valid Pricing:** Active price greater than 0 INR.
4. **Valid Landing Page:** Valid slug and reachable canonical landing page URL.
5. **Primary Image:** Valid, reachable image URL.

---

## 5. Merchant Center Owner Setup Checklist

The following actions are performed once in the Google Merchant Center web console by the store owner:

- [ ] **Step 1: Create Google Merchant Center Account**  
  Sign in to [Google Merchant Center](https://merchants.google.com/) using the official business Google account. Set business country to **India** and time zone to **IST (GMT+05:30)**.

- [ ] **Step 2: Claim & Verify Website URL**  
  Enter `https://sulocraft.com`. Verify ownership via:
  - **Option A (Recommended):** Add DNS TXT verification record to Cloudflare DNS.
  - **Option B:** Add HTML `<meta name="google-site-verification" content="...">` tag to the storefront head via Cloudflare Worker.

- [ ] **Step 3: Configure Shipping Settings**  
  Under **Settings > Shipping and returns > Shipping services**:
  - Service Name: `Standard Domestic Delivery`
  - Delivery Country: `India (IN)`
  - Currency: `INR`
  - Transit Time: `3 to 5 business days` (Handling: `1-2 business days`)
  - Shipping Rates:
    - Orders ₹999 and above: **Free Shipping (₹0)**
    - Orders below ₹999: **₹100 flat standard courier fee**

- [ ] **Step 4: Configure Return Policy**  
  Under **Settings > Shipping and returns > Return policies**:
  - Return Window: `7 days` from delivery
  - Return Reason: Transit damage or defective item replacement
  - Policy Link: `https://sulocraft.com/return-policy`
  - Customer Return Fee: Free for defective/damaged items

- [ ] **Step 5: Register Primary Product Feed**  
  Under **Products > Feeds > Add primary feed**:
  - Target Countries: `India`
  - Language: `English`
  - Destination: `Free listings` and `Shopping ads`
  - Feed Name: `Sulocraft Primary Product Feed`
  - Input Method: **Scheduled Fetch**
  - File Name: `merchant-feed.xml`
  - Fetch Frequency: `Daily`
  - Fetch Time: `02:00 AM IST`
  - File URL: `https://sulocraft.com/api/v1/seo/merchant-feed.xml` (No username/password required)

- [ ] **Step 6: Activate Free Product Listings**  
  Complete the Free Listings onboarding program. Products will be reviewed by Google within 24–48 hours and begin showing across Google Search, Google Images, and Google Shopping.

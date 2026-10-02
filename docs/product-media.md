# Product media manifest

Sulocraft-managed product media uses a stable slug hierarchy:

```text
products/<product-slug>/primary.png
products/<product-slug>/gallery-01.png
products/<product-slug>/gallery-02.png
```

The database stores the object key. The API prepends `IMAGE_BASE_URL`; React renders the returned URL unchanged.

## Seed catalogue: approved SKU and unique primary image

The SKU belongs to the default sellable variant. Future size, color, or customization variants receive their own SKU and may share a product gallery only when they are genuinely the same product.

| Product slug | Default variant SKU | Source file / object key |
| --- | --- | --- |
| `forever-crochet-rose-bouquet` | `SULO-FLR-ROSE-001` | `products/forever-crochet-rose-bouquet/primary.png` |
| `crochet-tulip-bouquet` | `SULO-FLR-TULIP-001` | `products/crochet-tulip-bouquet/primary.png` |
| `heart-bear` | `SULO-BABY-BEAR-001` | `products/heart-bear/primary.png` |
| `couple-bunny-set` | `SULO-AMI-BUNNY-001` | `products/couple-bunny-set/primary.png` |
| `mini-panda-amigurumi` | `SULO-AMI-PANDA-001` | `products/mini-panda-amigurumi/primary.png` |
| `crochet-bunny` | `SULO-AMI-BUNNY-002` | `products/crochet-bunny/owner-pink-bunny.png` |
| `crochet-marigold-garland` | `SULO-POOJA-GARLAND-001` | `products/crochet-marigold-garland/primary.png` |
| `sunflower-bouquet` | `SULO-FLR-SUNFLOWER-001` | `products/sunflower-bouquet/primary.png` |
| `crochet-hanging-planter` | `SULO-HOME-PLANT-001` | `products/crochet-hanging-planter/primary.png` |
| `boho-wall-hanging` | `SULO-HOME-WALL-001` | `products/boho-wall-hanging/primary.png` |
| `love-letter-crochet-set` | `SULO-GIFT-LOVE-001` | `products/love-letter-crochet-set/primary.png` |
| `mini-rose-box` | `SULO-FLR-ROSE-002` | `products/mini-rose-box/primary.png` |
| `lotus-mala` | `SULO-POOJA-MALA-001` | `products/lotus-mala/primary.png` |
| `crochet-toran` | `SULO-POOJA-TORAN-001` | `products/crochet-toran/primary.png` |
| `daisy-coaster-set` | `SULO-HOME-COASTER-001` | `products/daisy-coaster-set/primary.png` |
| `mini-teddy-bear` | `SULO-AMI-TEDDY-001` | `products/mini-teddy-bear/primary.png` |
| `baby-gift-hamper` | `SULO-BABY-HAMPER-001` | `products/baby-gift-hamper/primary.png` |
| `crochet-heart-planter` | `SULO-HOME-HEART-001` | `products/crochet-heart-planter/primary.png` |
| `baby-blanket` | `SULO-BABY-BLNK-001` | `products/baby-blanket/primary.png` |
| `bunny-amigurami-set` | `SULO-AMI-BUNNY-003` | `products/bunny-amigurami-set/primary.png` |
| `amigurumi-flower-bouquet` | `SULO-FLR-AMI-001` | `products/amigurumi-flower-bouquet/primary.png` |
| `octopus-amigurami-set` | `SULO-AMI-OCTO-001` | `products/octopus-amigurami-set/primary.png` |
| `pooja-dress` | `SULO-POOJA-DRESS-001` | `products/pooja-dress/primary.png` |
| `potli-handbag` | `SULO-ACC-POTLI-001` | `products/potli-handbag/primary.png` |

Every listed file is a distinct generated asset under `public/images/`. Do not reuse another product's image as a fallback. If an asset is missing, return an explicit placeholder state and fix the data rather than silently substituting unrelated photography.

Production upload target for each file is the same object key beneath `https://images.sulocraft.com/`.

## Category card artwork

Category cards use versioned object keys so replacing an image does not leave browser or CDN caches serving stale pixels. Keep the category database `image_key`, local asset, and R2 key aligned.

| Category slug | Local asset / R2 key | SHA-256 |
| --- | --- | --- |
| `amigurumi` | `categories/amigurumi/card-v2.png` | `07c7c90f5fce0975824b9a5b37c2535af619313ad3e63c3530a3608be8453276` |
| `home-decor` | `categories/home-decor/card-v2.png` | `b92a89d6af21ca5304caa772b0873423009c3099cdcbb159997daf3f58ba980c` |

## Approved secondary gallery images

| Product slug | Gallery object key | Purpose |
| --- | --- | --- |
| `forever-crochet-rose-bouquet` | `products/forever-crochet-rose-bouquet/gallery-01.png` | Alternate three-quarter product view |
| `crochet-tulip-bouquet` | `products/crochet-tulip-bouquet/gallery-01.png` | Alternate three-quarter product view |
| `heart-bear` | `products/heart-bear/gallery-01.png` | Alternate three-quarter product view |
| `couple-bunny-set` | `products/couple-bunny-set/gallery-01.png` | Alternate three-quarter product view |
| `crochet-bunny` | `products/crochet-bunny/gallery-01-owner-collage.png` | Owner collection collage view |
| `pooja-dress` | `products/pooja-dress/gallery-01.png` | Pooja deity poshak alternate view 1 |
| `pooja-dress` | `products/pooja-dress/gallery-02.png` | Pooja deity poshak alternate view 2 |
| `pooja-dress` | `products/pooja-dress/gallery-03.png` | Pooja deity poshak alternate view 3 |
| `potli-handbag` | `products/potli-handbag/gallery-01.png` | Potli handbag detail close-up |
| `sunflower-bouquet` | `products/sunflower-bouquet/gallery-01-owner-lifestyle.png` | Lifestyle/gallery photo for Sunflower Bouquet |

The structured SKU, classification, media order, alt text, and integrity hashes for all controlled products are published in [product-catalogue-seed.json](product-catalogue-seed.json). Only gallery files that exist and pass validation may be added to database seeds.

## Publication gate

A product is not seed-ready or publish-ready unless all of the following are true:

- every sellable variant has a non-empty globally unique SKU;
- the product has exactly one primary image record with meaningful alt text;
- the referenced local file exists during local development, or the R2 object returns HTTP `200` in production;
- the primary image is not reused by a different product slug;
- image records have deterministic display order and only existing gallery objects are included.

Seed validation must fail loudly when any gate fails. Do not create database rows pointing at planned or missing media. This manifest is the controlled starting catalogue; new products must be added to the manifest or an equivalent admin import before publication.

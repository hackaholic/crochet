# Product media manifest

Sulocraft-managed product media uses a stable slug hierarchy:

```text
products/<product-slug>/primary.png
products/<product-slug>/gallery-01.png
products/<product-slug>/gallery-02.png
```

The database stores the object key. The API prepends `IMAGE_BASE_URL`; React renders the returned URL unchanged.

## Approved unique primary images

| Product slug | Source file / object key |
| --- | --- |
| `forever-crochet-rose-bouquet` | `products/forever-crochet-rose-bouquet/primary.png` |
| `crochet-tulip-bouquet` | `products/crochet-tulip-bouquet/primary.png` |
| `heart-bear` | `products/heart-bear/primary.png` |
| `couple-bunny-set` | `products/couple-bunny-set/primary.png` |
| `mini-panda-amigurumi` | `products/mini-panda-amigurumi/primary.png` |
| `crochet-bunny` | `products/crochet-bunny/primary.png` |
| `crochet-marigold-garland` | `products/crochet-marigold-garland/primary.png` |
| `sunflower-bouquet` | `products/sunflower-bouquet/primary.png` |
| `crochet-hanging-planter` | `products/crochet-hanging-planter/primary.png` |
| `boho-wall-hanging` | `products/boho-wall-hanging/primary.png` |
| `love-letter-crochet-set` | `products/love-letter-crochet-set/primary.png` |
| `mini-rose-box` | `products/mini-rose-box/primary.png` |
| `lotus-mala` | `products/lotus-mala/primary.png` |
| `crochet-toran` | `products/crochet-toran/primary.png` |
| `daisy-coaster-set` | `products/daisy-coaster-set/primary.png` |
| `mini-teddy-bear` | `products/mini-teddy-bear/primary.png` |

Every listed file is a distinct generated asset under `public/images/`. Do not reuse another product's image as a fallback. If an asset is missing, return an explicit placeholder state and fix the data rather than silently substituting unrelated photography.

Production upload target for each file is the same object key beneath `https://images.sulocraft.com/`.

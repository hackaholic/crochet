"""Central asset image path builder and development mock resolver."""

from app.core.config import settings


def _unsplash(photo_id: str, w: int = 800, h: int = 800) -> str:
    """Format Unsplash source photo URL."""
    return f"https://images.unsplash.com/{photo_id}?w={w}&h={h}&fit=crop&auto=format"


# Canonical mapping from internal relative paths to high-resolution artisanal mock images
MOCK_IMAGE_MAP: dict[str, str] = {
    # Products
    "products/forever-crochet-rose-bouquet/primary.jpg": _unsplash("photo-1700171518313-5dd219beaaa6"),
    "products/forever-crochet-rose-bouquet/gallery-1.jpg": _unsplash("photo-1700171518313-5dd219beaaa6"),
    "products/forever-crochet-rose-bouquet/gallery-2.jpg": _unsplash("photo-1700171394718-2457b1190444"),
    "products/forever-crochet-rose-bouquet/gallery-3.jpg": _unsplash("photo-1700170447159-9d2d0da133a5"),
    "products/forever-crochet-rose-bouquet/gallery-4.jpg": _unsplash("photo-1700171458554-46cfd3f2a87a"),

    "products/crochet-tulip-bouquet/primary.jpg": _unsplash("photo-1700171394718-2457b1190444"),
    "products/crochet-tulip-bouquet/gallery-1.jpg": _unsplash("photo-1700171394718-2457b1190444"),

    "products/heart-bear/primary.jpg": _unsplash("photo-1602773984044-3ecbed81556d"),
    "products/heart-bear/gallery-1.jpg": _unsplash("photo-1602773984044-3ecbed81556d"),

    "products/couple-bunny-set/primary.jpg": _unsplash("photo-1629019317873-3f603b269723"),
    "products/couple-bunny-set/gallery-1.jpg": _unsplash("photo-1629019317873-3f603b269723"),

    "products/mini-panda-amigurumi/primary.jpg": _unsplash("photo-1602773974733-b56200c8653f"),
    "products/mini-panda-amigurumi/gallery-1.jpg": _unsplash("photo-1602773974733-b56200c8653f"),

    "products/crochet-bunny/primary.jpg": _unsplash("photo-1753370241607-5d48d8aaa70e"),
    "products/crochet-bunny/gallery-1.jpg": _unsplash("photo-1753370241607-5d48d8aaa70e"),

    "products/crochet-marigold-garland/primary.jpg": _unsplash("photo-1700170447159-9d2d0da133a5"),
    "products/crochet-marigold-garland/gallery-1.jpg": _unsplash("photo-1700170447159-9d2d0da133a5"),

    "products/sunflower-bouquet/primary.jpg": _unsplash("photo-1700171458554-46cfd3f2a87a"),
    "products/sunflower-bouquet/gallery-1.jpg": _unsplash("photo-1700171458554-46cfd3f2a87a"),

    "products/crochet-hanging-planter/primary.jpg": _unsplash("photo-1550376026-7375b92bb318"),
    "products/crochet-hanging-planter/gallery-1.jpg": _unsplash("photo-1550376026-7375b92bb318"),

    "products/boho-wall-hanging/primary.jpg": _unsplash("photo-1618574760337-2750f6251d20"),
    "products/boho-wall-hanging/gallery-1.jpg": _unsplash("photo-1618574760337-2750f6251d20"),

    "products/love-letter-crochet-set/primary.jpg": _unsplash("photo-1646182504823-a02b768e28b5"),
    "products/love-letter-crochet-set/gallery-1.jpg": _unsplash("photo-1646182504823-a02b768e28b5"),

    "products/mini-rose-box/primary.jpg": _unsplash("photo-1608825154649-2e9bb4cd4211"),
    "products/mini-rose-box/gallery-1.jpg": _unsplash("photo-1608825154649-2e9bb4cd4211"),

    "products/lotus-mala/primary.jpg": _unsplash("photo-1700171518313-5dd219beaaa6"),
    "products/lotus-mala/gallery-1.jpg": _unsplash("photo-1700171518313-5dd219beaaa6"),

    "products/crochet-toran/primary.jpg": _unsplash("photo-1700171394718-2457b1190444"),
    "products/crochet-toran/gallery-1.jpg": _unsplash("photo-1700171394718-2457b1190444"),

    "products/daisy-coaster-set/primary.jpg": _unsplash("photo-1700170447159-9d2d0da133a5"),
    "products/daisy-coaster-set/gallery-1.jpg": _unsplash("photo-1700170447159-9d2d0da133a5"),

    "products/mini-teddy-bear/primary.jpg": _unsplash("photo-1602773974733-b56200c8653f"),
    "products/mini-teddy-bear/gallery-1.jpg": _unsplash("photo-1602773974733-b56200c8653f"),

    # Categories
    "categories/romantic.jpg": _unsplash("photo-1700171518313-5dd219beaaa6", 600, 700),
    "categories/birthday.jpg": _unsplash("photo-1602773984044-3ecbed81556d", 600, 700),
    "categories/pooja.jpg": _unsplash("photo-1700170447159-9d2d0da133a5", 600, 700),
    "categories/pooja-items.jpg": _unsplash("photo-1700170447159-9d2d0da133a5", 600, 700),
    "categories/home.jpg": _unsplash("photo-1618574760337-2750f6251d20", 600, 700),
    "categories/home-decor.jpg": _unsplash("photo-1618574760337-2750f6251d20", 600, 700),
    "categories/flowers.jpg": _unsplash("photo-1700171394718-2457b1190444", 600, 700),
    "categories/amigurumi.jpg": _unsplash("photo-1753370241607-5d48d8aaa70e", 600, 700),
    "categories/baby.jpg": _unsplash("photo-1629019317873-3f603b269723", 600, 700),
    "categories/keychains.jpg": _unsplash("photo-1700171458554-46cfd3f2a87a", 600, 700),
    "categories/gifts.jpg": _unsplash("photo-1602773984044-3ecbed81556d", 600, 700),

    # Occasions (distinct Sulocraft handmade assets)
    "occasions/birthday.jpg": _unsplash("photo-1513151233558-d860c5398176", 400, 300),
    "occasions/birthday-gifting-v2.png": _unsplash("photo-1513151233558-d860c5398176", 400, 300),
    "occasions/justbecause-gifting.png": _unsplash("photo-1602773974733-b56200c8653f", 400, 300),
    "occasions/just-because-gifting.png": _unsplash("photo-1602773974733-b56200c8653f", 400, 300),
    "occasions/anniversary.jpg": _unsplash("photo-1518199266791-5375a83190b7", 400, 300),
    "occasions/anniversary-gifting-v2.png": _unsplash("photo-1518199266791-5375a83190b7", 400, 300),
    "occasions/babyshower.jpg": _unsplash("photo-1629019317873-3f603b269723", 400, 300),
    "occasions/babyshower-gifting.png": _unsplash("photo-1629019317873-3f603b269723", 400, 300),
    "occasions/baby-shower-hamper.png": _unsplash("photo-1629019317873-3f603b269723", 400, 300),
    "occasions/wedding.jpg": _unsplash("photo-1519741497674-611481863552", 400, 300),
    "occasions/wedding-gifting-v2.png": _unsplash("photo-1519741497674-611481863552", 400, 300),
    "occasions/valentine.jpg": _unsplash("photo-1646182504823-a02b768e28b5", 400, 300),
    "occasions/valentine-gifting.png": _unsplash("photo-1646182504823-a02b768e28b5", 400, 300),
    "occasions/valentine-couple-bunnies.png": _unsplash("photo-1646182504823-a02b768e28b5", 400, 300),
    "occasions/decor.jpg": _unsplash("photo-1618574760337-2750f6251d20", 400, 300),
    "occasions/decor-gifting.png": _unsplash("photo-1618574760337-2750f6251d20", 400, 300),
    "occasions/decor-hanging-planter.png": _unsplash("photo-1618574760337-2750f6251d20", 400, 300),
    "occasions/diwali.jpg": _unsplash("photo-1700170447159-9d2d0da133a5", 400, 300),
    "occasions/diwali-gifting.png": _unsplash("photo-1700170447159-9d2d0da133a5", 400, 300),
    "occasions/diwali-marigold-garland.png": _unsplash("photo-1700170447159-9d2d0da133a5", 400, 300),
    "occasions/mother.jpg": _unsplash("photo-1700171394718-2457b1190444", 400, 300),
    "occasions/mother-gifting.png": _unsplash("photo-1700171394718-2457b1190444", 400, 300),
    "occasions/mothers-day-rose-bouquet.png": _unsplash("photo-1700171394718-2457b1190444", 400, 300),
    "occasions/father.jpg": _unsplash("photo-1700170447159-9d2d0da133a5", 400, 300),
    "occasions/father-gifting.png": _unsplash("photo-1700170447159-9d2d0da133a5", 400, 300),
    "occasions/fathers-day-coaster-set.png": _unsplash("photo-1700170447159-9d2d0da133a5", 400, 300),
    "occasions/rakhi.jpg": _unsplash("photo-1700170447159-9d2d0da133a5", 400, 300),
    "occasions/rakhi-gifting.png": _unsplash("photo-1700170447159-9d2d0da133a5", 400, 300),
    "occasions/rakhi-gift-potli.png": _unsplash("photo-1700170447159-9d2d0da133a5", 400, 300),
    "occasions/housewarming.jpg": _unsplash("photo-1550376026-7375b92bb318", 400, 300),
    "occasions/housewarming-gifting.png": _unsplash("photo-1550376026-7375b92bb318", 400, 300),
    "occasions/housewarming-wall-hanging.png": _unsplash("photo-1550376026-7375b92bb318", 400, 300),
    "occasions/justbecause.jpg": _unsplash("photo-1602773974733-b56200c8653f", 400, 300),
    "occasions/christmas.jpg": _unsplash("photo-1608825154649-2e9bb4cd4211", 400, 300),
    "occasions/christmas-gifting.png": _unsplash("photo-1608825154649-2e9bb4cd4211", 400, 300),
    "occasions/christmas-toran.png": _unsplash("photo-1608825154649-2e9bb4cd4211", 400, 300),

    # Campaigns & Hero Artworks
    "campaigns/hero-brand-story.jpg": _unsplash("photo-1700171518313-5dd219beaaa6", 1200, 600),
    "campaigns/hero-festive-gifting.jpg": _unsplash("photo-1700170447159-9d2d0da133a5", 1200, 600),
    "campaigns/hero-new-arrivals.jpg": _unsplash("photo-1700171394718-2457b1190444", 1200, 600),
    "campaigns/hero-home-decor.jpg": _unsplash("photo-1618574760337-2750f6251d20", 1200, 600),
    "campaigns/hero-custom-creations.jpg": _unsplash("photo-1646182504823-a02b768e28b5", 1200, 600),
    "campaigns/promo-gift-warmth.jpg": _unsplash("photo-1700171518313-5dd219beaaa6", 1600, 800),
    "campaigns/story-craft.jpg": _unsplash("photo-1602773974733-b56200c8653f", 1200, 800),
    "hero/heritage.png": _unsplash("photo-1700171518313-5dd219beaaa6", 1600, 900),
    "hero/festive-gifting.png": _unsplash("photo-1700170447159-9d2d0da133a5", 1600, 900),
    "hero/flower-bouquet.png": _unsplash("photo-1700171394718-2457b1190444", 1600, 900),
    "hero/home-decor.png": _unsplash("photo-1618574760337-2750f6251d20", 1600, 900),
    "hero/custom-bouquet.png": _unsplash("photo-1646182504823-a02b768e28b5", 1600, 900),
    "hero/amigurumi.png": _unsplash("photo-1753370241607-5d48d8aaa70e", 1600, 900),

    # Avatars
    "avatars/priya-sharma.jpg": "https://i.pravatar.cc/120?img=47",
    "avatars/ananya-krishnan.jpg": "https://i.pravatar.cc/120?img=44",
    "avatars/ritu-agarwal.jpg": "https://i.pravatar.cc/120?img=41",
    "avatars/meera-pillai.jpg": "https://i.pravatar.cc/120?img=49",
}

# Local development serves the same approved occasion artwork that is uploaded
# to R2 in production. Database object keys intentionally remain stable; these
# aliases connect those keys to the checked-in local copies without redirecting
# occasion cards to generic stock photography.
LOCAL_IMAGE_ASSET_MAP: dict[str, str] = {
    "occasions/birthday-gifting-v2.png": "occasions/birthday-gifting-v2.png",
    "occasions/just-because-gifting.png": "occasions/justbecause-gifting.png",
    "occasions/anniversary-gifting-v2.png": "occasions/anniversary-gifting-v2.png",
    "occasions/baby-shower-hamper.png": "occasions/babyshower-gifting.png",
    "occasions/wedding-gifting-v2.png": "occasions/wedding-gifting-v2.png",
    "occasions/valentine-couple-bunnies.png": "occasions/valentine-gifting.png",
    "occasions/decor-hanging-planter.png": "occasions/decor-gifting.png",
    "occasions/diwali-marigold-garland.png": "occasions/diwali-gifting.png",
    "occasions/mothers-day-rose-bouquet.png": "occasions/mother-gifting.png",
    "occasions/fathers-day-coaster-set.png": "occasions/father-gifting.png",
    "occasions/rakhi-gift-potli.png": "occasions/rakhi-gifting.png",
    "occasions/housewarming-wall-hanging.png": "occasions/housewarming-gifting.png",
    "occasions/christmas-toran.png": "occasions/christmas-gifting.png",
}


def build_image_url(relative_path: str) -> str:
    """Build public CDN or local mock image URL from an environment-agnostic internal path.

    Example:
        build_image_url("products/forever-crochet-rose-bouquet/primary.jpg")
        -> "https://images.sulocraft.com/products/forever-crochet-rose-bouquet/primary.jpg" (in cloud)
        -> "http://localhost:8000/static/images/products/forever-crochet-rose-bouquet/primary.jpg" (in local mock)
    """
    if not relative_path:
        return ""
    if relative_path.startswith(("http://", "https://")):
        return relative_path
    clean_path = relative_path.lstrip("/")
    base = settings.image_base_url.rstrip("/")
    return f"{base}/{clean_path}"


def resolve_mock_image_source(relative_path: str) -> str:
    """Lookup the upstream high-resolution mock photo URL for local serving/redirect."""
    clean_path = relative_path.lstrip("/")
    if clean_path in MOCK_IMAGE_MAP:
        return MOCK_IMAGE_MAP[clean_path]
    # Fallback to high-res crochet photo
    return _unsplash("photo-1700171518313-5dd219beaaa6")

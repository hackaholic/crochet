"""Catalogue seed script conforming to Section 10 & 13 of the Multi-Agent Specification
and Sulocraft product-taxonomy.md & product-media.md contracts.
"""

from datetime import datetime, timezone
from pathlib import Path
import re
import sys
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.catalogue import (
    Category,
    Collection,
    Occasion,
    Product,
    ProductCategory,
    ProductCollection,
    ProductImage,
    ProductVariant,
    Review,
    Tag,
    product_categories,
    product_collections,
    product_tags,
)
from app.models.storefront import BrandSettings, HomepageCampaign, HomepageSection
from app.models.user import User, UserIdentity


APP_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = APP_ROOT if (APP_ROOT / "public" / "images").is_dir() else APP_ROOT.parent
LOCAL_IMAGE_DIR = PROJECT_ROOT / "public" / "images"


def slugify(text: str) -> str:
    """Convert text into a URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s_-]+", "-", text)


# -----------------------------------------------------------------------------
# Canonical Category Tree (5 Roots in Storefront Order)
# -----------------------------------------------------------------------------
TAXONOMY_TREE = [
    {
        "name": "Flowers",
        "slug": "flowers",
        "description": "Handcrafted permanent blooms, bouquets, and stems",
        "image_key": "categories/flowers/card.png",
        "children": [
            {"name": "Bouquets", "slug": "bouquets"},
            {"name": "Single Flowers", "slug": "single-flowers"},
            {"name": "Roses", "slug": "roses"},
            {"name": "Sunflowers", "slug": "sunflowers"},
            {"name": "Tulips", "slug": "tulips"},
            {"name": "Daisies", "slug": "daisies"},
            {"name": "Cosmos", "slug": "cosmos"},
            {"name": "Lilies", "slug": "lilies"},
            {"name": "Lavender", "slug": "lavender"},
            {"name": "Custom Bouquets", "slug": "custom-bouquets"},
        ],
    },
    {
        "name": "Amigurumi",
        "slug": "amigurumi",
        "description": "Hand-stitched plush toys, animals, and miniature keepsakes",
        "image_key": "categories/amigurumi/card.png",
        "children": [
            {"name": "Bunny", "slug": "bunny"},
            {"name": "Rabbit", "slug": "rabbit"},
            {"name": "Teddy Bear", "slug": "teddy-bear"},
            {"name": "Octopus", "slug": "octopus"},
            {"name": "Dolls", "slug": "dolls"},
            {"name": "Animals", "slug": "animals"},
            {"name": "Cartoon-Inspired Characters", "slug": "cartoon-inspired-characters"},
            {"name": "Mini Amigurumi", "slug": "mini-amigurumi"},
            {"name": "Custom / Personalized Figures", "slug": "custom-personalized-figures"},
        ],
    },
    {
        "name": "Baby",
        "slug": "baby",
        "description": "Soft cotton booties, rattles, blankets, and nursery décor",
        "image_key": "categories/baby/card.png",
        "children": [
            {"name": "Blankets", "slug": "blankets"},
            {"name": "Rattles", "slug": "rattles"},
            {"name": "Baby Mobiles", "slug": "baby-mobiles"},
            {"name": "Toys", "slug": "toys"},
            {"name": "Caps & Beanies", "slug": "caps-beanies"},
            {"name": "Bassinets / Baby Baskets", "slug": "bassinets-baby-baskets"},
            {"name": "Baby Gift Sets", "slug": "baby-gift-sets"},
        ],
    },
    {
        "name": "Home & Decor",
        "slug": "home-decor",
        "description": "Crochet wall hangings, planters, coasters, and festive decor",
        "image_key": "categories/home-decor/card.png",
        "children": [
            {"name": "Doilies", "slug": "doilies"},
            {"name": "Table Runners", "slug": "table-runners"},
            {"name": "Sofa Throws", "slug": "sofa-throws"},
            {"name": "Motifs", "slug": "motifs"},
            {"name": "Coasters", "slug": "coasters"},
            {"name": "Flower / Plant Decor", "slug": "flower-plant-decor"},
            {"name": "Wall Decor", "slug": "wall-decor"},
            {"name": "Decorative Covers", "slug": "decorative-covers"},
            {"name": "Other Home Decor", "slug": "other-home-decor"},
        ],
    },
    {
        "name": "Pooja & Devotional",
        "slug": "pooja-devotional",
        "description": "Devotional garlands, malas, torans, and temple décor",
        "image_key": "categories/pooja-devotional/card.png",
        "children": [
            {"name": "Garlands", "slug": "garlands"},
            {"name": "Thalpos / Decorative Covers", "slug": "thalpos-decorative-covers"},
            {"name": "Torans", "slug": "torans"},
            {"name": "Poshak / God Clothes", "slug": "poshak-god-clothes"},
            {"name": "Laddu Gopal Clothes", "slug": "laddu-gopal-clothes"},
            {"name": "Temple Decor", "slug": "temple-decor"},
            {"name": "Festival Decor", "slug": "festival-decor"},
        ],
    },
]

# -----------------------------------------------------------------------------
# Gift and Merchandising Collections
# -----------------------------------------------------------------------------
COLLECTIONS_DATA = [
    {"name": "Gifts", "slug": "gifts", "collection_type": "EVERGREEN", "display_order": 1, "description": "Handcrafted crochet gift ideas for every occasion"},
    {"name": "Birthday Gifts", "slug": "birthday-gifts", "collection_type": "EVERGREEN", "display_order": 2, "description": "Make birthdays memorable with vibrant handcrafted blooms and adorable companions"},
    {"name": "Anniversary Gifts", "slug": "anniversary-gifts", "collection_type": "EVERGREEN", "display_order": 3, "description": "Everlasting crochet flowers and love keepsakes celebrating shared milestones"},
    {"name": "Wedding Gifts", "slug": "wedding-gifts", "collection_type": "EVERGREEN", "display_order": 4, "description": "Elegant heirloom crochet designs for couples and new journeys"},
    {"name": "Baby Shower Gifts", "slug": "baby-shower-gifts", "collection_type": "EVERGREEN", "display_order": 5, "description": "Gentle baby treasures and plush companions celebrating newborn joy"},
    {"name": "Newborn Gifts", "slug": "newborn-gifts", "collection_type": "EVERGREEN", "display_order": 6, "description": "Safe, soft cotton keepsakes hand-crocheted for little ones"},
    {"name": "Housewarming Gifts", "slug": "housewarming-gifts", "collection_type": "EVERGREEN", "display_order": 7, "description": "Warm artisanal coasters, planters, and boho wall hangings for new homes"},
    {"name": "Festival Gifts", "slug": "festival-gifts", "collection_type": "EVERGREEN", "display_order": 8, "description": "Festive malas, torans, and vibrant blooms for Diwali and holy celebrations"},
    {"name": "Gifts for Kids", "slug": "gifts-for-kids", "collection_type": "EVERGREEN", "display_order": 9, "description": "Playful amigurumi animals and snuggly handmade friends"},
    {"name": "Gifts for Her", "slug": "gifts-for-her", "collection_type": "EVERGREEN", "display_order": 10, "description": "Delicate floral bouquets, personalized letters, and timeless keepsakes"},
    {"name": "Gifts for Him", "slug": "gifts-for-him", "collection_type": "EVERGREEN", "display_order": 11, "description": "Subtle artisanal desk accents, coasters, and thoughtful handmade pieces"},
    {"name": "Personalized Gifts", "slug": "personalized-gifts", "collection_type": "EVERGREEN", "display_order": 12, "description": "Customizable colors, messages, and bespoke handcrafted designs"},
    {"name": "Custom Gifts", "slug": "custom-gifts", "collection_type": "EVERGREEN", "display_order": 13, "description": "Bespoke commissions crafted to order by Anupama and the Sulocraft team"},
    {"name": "Best Sellers", "slug": "bestsellers", "collection_type": "MERCHANDISING", "display_order": 14, "description": "Sulocraft's most cherished and highly requested handcrafted creations"},
    {"name": "New Arrivals", "slug": "new-arrivals", "collection_type": "MERCHANDISING", "display_order": 15, "description": "Fresh designs and newly released artisanal pieces from our studio"},
]

OCCASIONS_DATA = [
    {"id": "birthday", "name": "Birthday", "icon": "🎂", "image_url": "occasions/birthday.jpg"},
    {"id": "anniversary", "name": "Anniversary", "icon": "💍", "image_url": "occasions/anniversary.jpg"},
    {"id": "valentine", "name": "Valentine's Day", "icon": "❤️", "image_url": "occasions/valentine.jpg"},
    {"id": "wedding", "name": "Wedding", "icon": "💐", "image_url": "occasions/wedding.jpg"},
    {"id": "babyshower", "name": "Baby Shower", "icon": "🍼", "image_url": "occasions/babyshower.jpg"},
    {"id": "housewarming", "name": "Housewarming", "icon": "🏠", "image_url": "occasions/housewarming.jpg"},
    {"id": "rakhi", "name": "Rakhi", "icon": "🪡", "image_url": "occasions/rakhi.jpg"},
    {"id": "diwali", "name": "Diwali", "icon": "🪔", "image_url": "occasions/diwali.jpg"},
    {"id": "mother", "name": "Mother's Day", "icon": "🌷", "image_url": "occasions/mother.jpg"},
    {"id": "justbecause", "name": "Just Because", "icon": "🎁", "image_url": "occasions/justbecause.jpg"},
]

# -----------------------------------------------------------------------------
# 16 Controlled Launch Products (Matching docs/product-media.md)
# -----------------------------------------------------------------------------
PRODUCTS_DATA = [
    {
        "id": 1,
        "name": "Forever Crochet Rose Bouquet",
        "slug": "forever-crochet-rose-bouquet",
        "price": 2599,
        "rating": 4.9,
        "reviews": 128,
        "image": "products/forever-crochet-rose-bouquet/primary.png",
        "images": ["products/forever-crochet-rose-bouquet/primary.png", "products/forever-crochet-rose-bouquet/gallery-01.png"],
        "primary_category_slug": "bouquets",
        "secondary_category_slugs": ["roses"],
        "collection_slugs": ["bestsellers", "anniversary-gifts", "gifts-for-her", "gifts"],
        "badge": "Bestseller",
        "tags": ["romantic", "anniversary", "valentine", "handmade", "roses"],
        "description": "A timeless bouquet of handcrafted crochet roses that never wilt. Each petal is lovingly stitched by hand, making every bouquet truly one of a kind.",
        "customizable": True,
        "variants": [
            {"sku": "SULO-FLR-ROSE-001", "name": "5 Roses / Deep Crimson", "price": 2599, "stock": 15, "attributes": {"color": "Deep Crimson", "stems": 5}},
        ],
    },
    {
        "id": 2,
        "name": "Crochet Tulip Bouquet",
        "slug": "crochet-tulip-bouquet",
        "price": 1599,
        "rating": 4.8,
        "reviews": 96,
        "image": "products/crochet-tulip-bouquet/primary.png",
        "images": ["products/crochet-tulip-bouquet/primary.png", "products/crochet-tulip-bouquet/gallery-01.png"],
        "primary_category_slug": "tulips",
        "secondary_category_slugs": ["bouquets"],
        "collection_slugs": ["new-arrivals", "birthday-gifts", "gifts-for-her", "gifts"],
        "badge": "New",
        "tags": ["romantic", "birthday", "tulips", "handmade"],
        "description": "Delicate, pastel crochet tulips wrapped in artisanal craft paper. Bring spring into your home forever without watering.",
        "customizable": True,
        "variants": [
            {"sku": "SULO-FLR-TULIP-001", "name": "3 Tulips / Pastel Mix", "price": 1599, "stock": 20, "attributes": {"color": "Pastel Mix", "stems": 3}},
        ],
    },
    {
        "id": 3,
        "name": "Heart Bear",
        "slug": "heart-bear",
        "price": 1799,
        "rating": 4.9,
        "reviews": 84,
        "image": "products/heart-bear/primary.png",
        "images": ["products/heart-bear/primary.png", "products/heart-bear/gallery-01.png"],
        "primary_category_slug": "toys",
        "secondary_category_slugs": ["teddy-bear"],
        "collection_slugs": ["bestsellers", "baby-shower-gifts", "gifts-for-kids", "gifts"],
        "badge": "Bestseller",
        "tags": ["romantic", "valentine", "birthday", "amigurumi", "baby"],
        "description": "An adorable teddy bear clutching a bright red heart. Stitched with hypoallergenic cotton yarn, perfect for babies and keepsakes.",
        "customizable": False,
        "variants": [
            {"sku": "SULO-BABY-BEAR-001", "name": "Standard / Warm Brown", "price": 1799, "stock": 10, "attributes": {"color": "Warm Brown"}},
        ],
    },
    {
        "id": 4,
        "name": "Couple Bunny Set",
        "slug": "couple-bunny-set",
        "price": 3299,
        "rating": 5.0,
        "reviews": 52,
        "image": "products/couple-bunny-set/primary.png",
        "images": ["products/couple-bunny-set/primary.png", "products/couple-bunny-set/gallery-01.png"],
        "primary_category_slug": "bunny",
        "secondary_category_slugs": [],
        "collection_slugs": ["wedding-gifts", "anniversary-gifts", "gifts-for-her", "gifts"],
        "badge": "Limited",
        "tags": ["romantic", "anniversary", "wedding", "amigurumi"],
        "description": "A charming pair of groom and bride bunnies in custom bridal outfits. An unforgettable handmade wedding or anniversary gift.",
        "customizable": True,
        "variants": [
            {"sku": "SULO-AMI-BUNNY-001", "name": "Pair Set (Boy & Girl)", "price": 3299, "stock": 8, "attributes": {"set": "Pair"}},
        ],
    },
    {
        "id": 5,
        "name": "Mini Panda Amigurumi",
        "slug": "mini-panda-amigurumi",
        "price": 1299,
        "rating": 4.7,
        "reviews": 73,
        "image": "products/mini-panda-amigurumi/primary.png",
        "images": ["products/mini-panda-amigurumi/primary.png"],
        "primary_category_slug": "animals",
        "secondary_category_slugs": ["mini-amigurumi"],
        "collection_slugs": ["gifts-for-kids", "birthday-gifts", "gifts"],
        "badge": "Handmade",
        "tags": ["baby", "birthday", "amigurumi", "panda"],
        "description": "Palm-sized panda bear amigurumi holding a green bamboo shoot. Cute, durable, and handcrafted with tight detailed stitching.",
        "customizable": False,
        "variants": [
            {"sku": "SULO-AMI-PANDA-001", "name": "Standard Mini Panda", "price": 1299, "stock": 18, "attributes": {"size": "Mini"}},
        ],
    },
    {
        "id": 6,
        "name": "Crochet Bunny",
        "slug": "crochet-bunny",
        "price": 1199,
        "rating": 4.8,
        "reviews": 61,
        "image": "products/crochet-bunny/owner-pink-bunny.png",
        "images": ["products/crochet-bunny/owner-pink-bunny.png", "products/crochet-bunny/gallery-01-owner-collage.png"],
        "primary_category_slug": "bunny",
        "secondary_category_slugs": ["toys"],
        "collection_slugs": ["newborn-gifts", "gifts-for-kids", "gifts"],
        "tags": ["baby", "birthday", "amigurumi", "bunny"],
        "description": "Classic flopping-ear crochet rabbit toy crafted from soft pastel cotton yarn. Gentle on sensitive infant skin.",
        "customizable": False,
        "variants": [
            {"sku": "SULO-AMI-BUNNY-002", "name": "Single Bunny / Pink", "price": 1199, "stock": 25, "attributes": {"color": "Pink"}},
        ],
    },
    {
        "id": 7,
        "name": "Crochet Marigold Garland",
        "slug": "crochet-marigold-garland",
        "price": 1999,
        "rating": 4.9,
        "reviews": 45,
        "image": "products/crochet-marigold-garland/primary.png",
        "images": ["products/crochet-marigold-garland/primary.png"],
        "primary_category_slug": "garlands",
        "secondary_category_slugs": ["festival-decor"],
        "collection_slugs": ["festival-gifts", "housewarming-gifts", "bestsellers", "gifts"],
        "badge": "Bestseller",
        "tags": ["pooja", "diwali", "festive", "marigold", "garland"],
        "description": "Vibrant yellow and saffron marigold garland hand-crocheted for temple mandir, doorframes, and Diwali celebrations.",
        "customizable": True,
        "variants": [
            {"sku": "SULO-POOJA-GARLAND-001", "name": "5 Feet Garland / Yellow & Orange", "price": 1999, "stock": 30, "attributes": {"length": "5ft"}},
        ],
    },
    {
        "id": 8,
        "name": "Sunflower Bouquet",
        "slug": "sunflower-bouquet",
        "price": 2199,
        "rating": 4.8,
        "reviews": 88,
        "image": "products/sunflower-bouquet/primary.png",
        "images": [
            "products/sunflower-bouquet/primary.png",
            "products/sunflower-bouquet/gallery-01-owner-lifestyle.png",
        ],
        "primary_category_slug": "sunflowers",
        "secondary_category_slugs": ["bouquets"],
        "collection_slugs": ["birthday-gifts", "housewarming-gifts", "bestsellers", "gifts"],
        "badge": "Bestseller",
        "tags": ["birthday", "housewarming", "sunflowers"],
        "description": "Radiant yellow sunflowers crafted with golden yarn centers and eucalyptus foliage. Radiates sunshine year-round.",
        "customizable": True,
        "variants": [
            {"sku": "SULO-FLR-SUNFLOWER-001", "name": "3 Sunflowers + Foliage", "price": 2199, "stock": 14, "attributes": {"stems": 3}},
        ],
    },
    {
        "id": 9,
        "name": "Crochet Hanging Planter",
        "slug": "crochet-hanging-planter",
        "price": 1499,
        "rating": 4.6,
        "reviews": 39,
        "image": "products/crochet-hanging-planter/primary.png",
        "images": ["products/crochet-hanging-planter/primary.png"],
        "primary_category_slug": "flower-plant-decor",
        "secondary_category_slugs": ["other-home-decor"],
        "collection_slugs": ["housewarming-gifts", "gifts-for-her", "gifts"],
        "tags": ["housewarming", "home", "planter", "decor"],
        "description": "Bohemian suspended macrame and crochet planter basket. Fits standard 4-inch nursery pots and indoor plants.",
        "customizable": False,
        "variants": [
            {"sku": "SULO-HOME-PLANT-001", "name": "Natural Cotton Finish", "price": 1499, "stock": 15, "attributes": {"material": "Cotton"}},
        ],
    },
    {
        "id": 10,
        "name": "Boho Wall Hanging",
        "slug": "boho-wall-hanging",
        "price": 2999,
        "rating": 4.7,
        "reviews": 54,
        "image": "products/boho-wall-hanging/primary.png",
        "images": ["products/boho-wall-hanging/primary.png"],
        "primary_category_slug": "wall-decor",
        "secondary_category_slugs": ["other-home-decor"],
        "collection_slugs": ["housewarming-gifts", "custom-gifts", "gifts"],
        "tags": ["housewarming", "home", "boho", "wall-hanging"],
        "description": "Geometric artisanal tapestry with textured crochet fringe and wooden dowel. Creates warm, cozy interior ambiance.",
        "customizable": True,
        "variants": [
            {"sku": "SULO-HOME-WALL-001", "name": "Medium (30x60cm)", "price": 2999, "stock": 8, "attributes": {"size": "Medium"}},
        ],
    },
    {
        "id": 11,
        "name": "Love Letter Crochet Set",
        "slug": "love-letter-crochet-set",
        "price": 3499,
        "rating": 4.9,
        "reviews": 34,
        "image": "products/love-letter-crochet-set/primary.png",
        "images": ["products/love-letter-crochet-set/primary.png"],
        "primary_category_slug": "single-flowers",
        "secondary_category_slugs": ["roses"],
        "collection_slugs": ["anniversary-gifts", "personalized-gifts", "gifts-for-her", "new-arrivals", "gifts"],
        "badge": "New",
        "tags": ["romantic", "valentine", "anniversary", "personalized"],
        "description": "Sentimental gift set featuring a miniature crochet envelope with personal handwritten scroll and red crochet buds.",
        "customizable": True,
        "variants": [
            {"sku": "SULO-GIFT-LOVE-001", "name": "Box Set with Envelope & Flowers", "price": 3499, "stock": 10, "attributes": {"custom_message": True}},
        ],
    },
    {
        "id": 12,
        "name": "Mini Rose Box",
        "slug": "mini-rose-box",
        "price": 1899,
        "rating": 4.8,
        "reviews": 67,
        "image": "products/mini-rose-box/primary.png",
        "images": ["products/mini-rose-box/primary.png"],
        "primary_category_slug": "roses",
        "secondary_category_slugs": ["bouquets"],
        "collection_slugs": ["birthday-gifts", "gifts-for-her", "gifts"],
        "tags": ["romantic", "birthday", "mother", "roses"],
        "description": "Compact acrylic gift box containing 4 hand-stitched tea roses in blush pink and ivory. A sweet, lasting keepsake.",
        "customizable": True,
        "variants": [
            {"sku": "SULO-FLR-ROSE-002", "name": "Compact Gift Box (4 Roses)", "price": 1899, "stock": 16, "attributes": {"count": 4}},
        ],
    },
    {
        "id": 13,
        "name": "Lotus Mala",
        "slug": "lotus-mala",
        "price": 999,
        "rating": 4.7,
        "reviews": 28,
        "image": "products/lotus-mala/primary.png",
        "images": ["products/lotus-mala/primary.png"],
        "primary_category_slug": "garlands",
        "secondary_category_slugs": ["temple-decor"],
        "collection_slugs": ["festival-gifts", "gifts"],
        "tags": ["pooja", "festive", "lotus"],
        "description": "Sacred lotus mala garland handcrafted for Laddu Gopal, pooja altars, and festive devotional adornment.",
        "customizable": False,
        "variants": [
            {"sku": "SULO-POOJA-MALA-001", "name": "1 Metre Single Strand", "price": 999, "stock": 25, "attributes": {"length": "1m"}},
        ],
    },
    {
        "id": 14,
        "name": "Crochet Toran",
        "slug": "crochet-toran",
        "price": 1799,
        "rating": 4.8,
        "reviews": 41,
        "image": "products/crochet-toran/primary.png",
        "images": ["products/crochet-toran/primary.png"],
        "primary_category_slug": "torans",
        "secondary_category_slugs": ["festival-decor"],
        "collection_slugs": ["festival-gifts", "housewarming-gifts", "bestsellers", "gifts"],
        "badge": "Bestseller",
        "tags": ["pooja", "diwali", "housewarming", "toran"],
        "description": "Traditional welcome door hanging with crochet mango leaves and marigold pendants for auspicious entryways.",
        "customizable": True,
        "variants": [
            {"sku": "SULO-POOJA-TORAN-001", "name": "3 Feet Standard Door Frame", "price": 1799, "stock": 14, "attributes": {"length": "3ft"}},
        ],
    },
    {
        "id": 15,
        "name": "Daisy Coaster Set",
        "slug": "daisy-coaster-set",
        "price": 899,
        "rating": 4.5,
        "reviews": 93,
        "image": "products/daisy-coaster-set/primary.png",
        "images": ["products/daisy-coaster-set/primary.png"],
        "primary_category_slug": "coasters",
        "secondary_category_slugs": ["doilies"],
        "collection_slugs": ["housewarming-gifts", "bestsellers", "gifts"],
        "badge": "Bestseller",
        "tags": ["home", "housewarming", "coasters", "daisies"],
        "description": "Set of 4 absorbent cotton table coasters shaped like fresh white daisies with cheerful yellow centers.",
        "customizable": False,
        "variants": [
            {"sku": "SULO-HOME-COASTER-001", "name": "Set of 4 Coasters", "price": 899, "stock": 40, "attributes": {"pack": 4}},
        ],
    },
    {
        "id": 16,
        "name": "Mini Teddy Bear",
        "slug": "mini-teddy-bear",
        "price": 1099,
        "rating": 4.6,
        "reviews": 112,
        "image": "products/mini-teddy-bear/primary.png",
        "images": ["products/mini-teddy-bear/primary.png"],
        "primary_category_slug": "teddy-bear",
        "secondary_category_slugs": ["mini-amigurumi"],
        "collection_slugs": ["gifts-for-kids", "birthday-gifts", "gifts"],
        "tags": ["baby", "birthday", "amigurumi", "teddy"],
        "description": "Pocket-friendly crochet teddy bear companion wearing a cozy red scarf. Perfect stocking stuffer or desk buddy.",
        "customizable": False,
        "variants": [
            {"sku": "SULO-AMI-TEDDY-001", "name": "Standard Mini Bear", "price": 1099, "stock": 22, "attributes": {"size": "Mini"}},
        ],
    },
    {
        "id": 17,
        "name": "Baby Gift Hamper",
        "slug": "baby-gift-hamper",
        "price": 2499,
        "rating": 4.9,
        "reviews": 24,
        "image": "products/baby-gift-hamper/primary.png",
        "images": ["products/baby-gift-hamper/primary.png"],
        "primary_category_slug": "baby-gift-sets",
        "secondary_category_slugs": ["toys"],
        "collection_slugs": ["newborn-gifts", "gifts"],
        "badge": "New",
        "tags": ["baby", "hamper", "gift-set", "newborn", "handmade"],
        "description": "Curated heirloom baby gift hamper featuring handmade crochet keepsakes, rattles, and booties crafted from soft baby-safe organic cotton yarn.",
        "customizable": True,
        "variants": [
            {"sku": "SULO-BABY-HAMPER-001", "name": "Curated Baby Hamper", "price": 2499, "stock": 15, "attributes": {"set": "Standard"}},
        ],
    },
    {
        "id": 18,
        "name": "Crochet Heart Planter",
        "slug": "crochet-heart-planter",
        "price": 899,
        "rating": 4.8,
        "reviews": 19,
        "image": "products/crochet-heart-planter/primary.png",
        "images": ["products/crochet-heart-planter/primary.png"],
        "primary_category_slug": "flower-plant-decor",
        "secondary_category_slugs": ["mini-amigurumi"],
        "collection_slugs": ["housewarming-gifts", "gifts", "gifts-for-her"],
        "badge": "Popular",
        "tags": ["home-decor", "planter", "heart", "amigurumi", "handmade"],
        "description": "Charming handcrafted crochet heart planter pot with sweet amigurumi accents, perfect for small tabletop succulent decor and cozy room accents.",
        "customizable": False,
        "variants": [
            {"sku": "SULO-HOME-HEART-001", "name": "Heart Planter / Standard", "price": 899, "stock": 20, "attributes": {"design": "Heart"}},
        ],
    },
    {
        "id": 19,
        "name": "Handmade Crochet Baby Blanket",
        "slug": "baby-blanket",
        "price": 2199,
        "rating": 4.9,
        "reviews": 16,
        "image": "products/baby-blanket/primary.png",
        "images": ["products/baby-blanket/primary.png"],
        "primary_category_slug": "blankets",
        "secondary_category_slugs": ["baby-gift-sets"],
        "collection_slugs": ["newborn-gifts", "gifts-for-kids", "gifts"],
        "badge": "Heirloom",
        "tags": ["baby", "blanket", "nursery", "heirloom", "cotton"],
        "description": "Luxuriously soft pastel baby blanket meticulously crocheted from breathable hypoallergenic cotton yarn for nursery warmth.",
        "customizable": True,
        "variants": [
            {"sku": "SULO-BABY-BLNK-001", "name": "Standard Pastel Baby Blanket", "price": 2199, "stock": 12, "attributes": {"size": "Standard"}},
        ],
    },
    {
        "id": 20,
        "name": "Pastel Bunny Amigurumi Trio",
        "slug": "bunny-amigurami-set",
        "price": 1999,
        "rating": 4.8,
        "reviews": 22,
        "image": "products/bunny-amigurami-set/primary.png",
        "images": ["products/bunny-amigurami-set/primary.png"],
        "primary_category_slug": "bunny",
        "secondary_category_slugs": ["toys"],
        "collection_slugs": ["gifts-for-kids", "newborn-gifts", "gifts"],
        "badge": "Set",
        "tags": ["bunny", "amigurumi", "baby", "trio", "pastel"],
        "description": "Charming trio of pastel hand-stitched amigurumi bunnies, crafted with delicate overalls and floppy ears.",
        "customizable": False,
        "variants": [
            {"sku": "SULO-AMI-BUNNY-003", "name": "Set of 3 Pastel Bunnies", "price": 1999, "stock": 15, "attributes": {"set": "Trio"}},
        ],
    },
    {
        "id": 21,
        "name": "Amigurumi Floral Bloom Bouquet",
        "slug": "amigurumi-flower-bouquet",
        "price": 1899,
        "rating": 4.9,
        "reviews": 31,
        "image": "products/amigurumi-flower-bouquet/primary.png",
        "images": ["products/amigurumi-flower-bouquet/primary.png"],
        "primary_category_slug": "bouquets",
        "secondary_category_slugs": ["mini-amigurumi"],
        "collection_slugs": ["birthday-gifts", "gifts-for-her", "gifts", "new-arrivals"],
        "badge": "New",
        "tags": ["flowers", "amigurumi", "bouquet", "pastel", "gifts"],
        "description": "Delightful fusion of handcrafted crochet floral stems and whimsical miniature amigurumi companions wrapped in textured paper.",
        "customizable": True,
        "variants": [
            {"sku": "SULO-FLR-AMI-001", "name": "Amigurumi Bloom Bouquet", "price": 1899, "stock": 18, "attributes": {"style": "Hand-tied"}},
        ],
    },
    {
        "id": 22,
        "name": "Octopus Amigurumi Duo Set",
        "slug": "octopus-amigurami-set",
        "price": 1199,
        "rating": 4.7,
        "reviews": 18,
        "image": "products/octopus-amigurami-set/primary.png",
        "images": ["products/octopus-amigurami-set/primary.png"],
        "primary_category_slug": "octopus",
        "secondary_category_slugs": ["mini-amigurumi"],
        "collection_slugs": ["gifts-for-kids", "birthday-gifts", "gifts"],
        "badge": "Duo",
        "tags": ["octopus", "amigurumi", "kids", "baby", "handmade"],
        "description": "Playful pair of tactile spiral-tentacled octopus amigurumi companions crafted from soothing premium cotton yarn.",
        "customizable": False,
        "variants": [
            {"sku": "SULO-AMI-OCTO-001", "name": "Octopus Amigurumi Duo", "price": 1199, "stock": 20, "attributes": {"set": "Pair"}},
        ],
    },
    {
        "id": 23,
        "name": "Handcrafted Deity Poshak (Pooja Dress)",
        "slug": "pooja-dress",
        "price": 799,
        "rating": 5.0,
        "reviews": 27,
        "image": "products/pooja-dress/primary.png",
        "images": [
            "products/pooja-dress/primary.png",
            "products/pooja-dress/gallery-01.png",
            "products/pooja-dress/gallery-02.png",
            "products/pooja-dress/gallery-03.png",
        ],
        "primary_category_slug": "poshak-god-clothes",
        "secondary_category_slugs": ["laddu-gopal-clothes"],
        "collection_slugs": ["festival-gifts", "gifts"],
        "badge": "Devotional",
        "tags": ["pooja", "poshak", "deity", "dress", "festive"],
        "description": "Exquisite hand-crocheted deity poshak outfit set with ornate festive borders, designed with devotion for Laddu Gopal and home mandir idols.",
        "customizable": True,
        "variants": [
            {"sku": "SULO-POOJA-DRESS-001", "name": "Festive Deity Poshak", "price": 799, "stock": 25, "attributes": {"size": "Standard"}},
        ],
    },
    {
        "id": 24,
        "name": "Handcrafted Crochet Potli Bag",
        "slug": "potli-handbag",
        "price": 1299,
        "rating": 4.8,
        "reviews": 15,
        "image": "products/potli-handbag/primary.png",
        "images": [
            "products/potli-handbag/primary.png",
            "products/potli-handbag/gallery-01.png",
        ],
        "primary_category_slug": "other-home-decor",
        "secondary_category_slugs": ["festival-decor"],
        "collection_slugs": ["gifts-for-her", "festival-gifts", "gifts"],
        "badge": "Artisanal",
        "tags": ["potli", "handbag", "accessory", "festive", "traditional"],
        "description": "Elegant traditional drawstring crochet potli handbag adorned with beaded tassels, perfect for weddings, festive occasions, and ethnic ensembles.",
        "customizable": False,
        "variants": [
            {"sku": "SULO-ACC-POTLI-001", "name": "Embellished Crochet Potli", "price": 1299, "stock": 16, "attributes": {"color": "Ivory & Gold"}},
        ],
    },
]

REVIEWS_DATA = [
    {
        "id": 1,
        "product_name": "Forever Crochet Rose Bouquet",
        "name": "Priya Sharma",
        "location": "Mumbai",
        "rating": 5,
        "text": "The roses look so lifelike! My mother was in tears when she opened the package. Anupama's stitching is perfection.",
        "avatar_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=100&h=100&fit=crop&crop=face",
        "date": "Oct 2025",
    },
    {
        "id": 2,
        "product_name": "Crochet Tulip Bouquet",
        "name": "Ananya Roy",
        "location": "Bengaluru",
        "rating": 5,
        "text": "Bought the pastel tulip set for my study desk. It brightens up my work days so much! Beautifully packaged.",
        "avatar_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop&crop=face",
        "date": "Nov 2025",
    },
    {
        "id": 3,
        "product_name": "Heart Bear",
        "name": "Rohan Mehta",
        "location": "Delhi",
        "rating": 5,
        "text": "Gifted the Heart Bear to my fiancée for our anniversary. She absolutely adores it. Truly feels handcrafted with warmth.",
        "avatar_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face",
        "date": "Dec 2025",
    },
    {
        "id": 4,
        "product_name": "Crochet Marigold Garland",
        "name": "Sunita Patel",
        "location": "Ahmedabad",
        "rating": 5,
        "text": "Used these marigold malas for Diwali pooja. Everyone asked where I bought them! So durable and vibrant.",
        "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&h=100&fit=crop&crop=face",
        "date": "Jan 2026",
    },
]


def validate_seed_data(
    taxonomy_tree: list[dict],
    collections_data: list[dict],
    products_data: list[dict],
    image_dir: Path,
) -> None:
    """Validate seed data against the Sulocraft publication gate.

    - Every sellable variant has a non-empty globally unique SKU;
    - Exactly one primary image with non-empty path;
    - Referenced local file exists during local development;
    - Primary image key is not reused across product slugs;
    - Exactly one valid primary leaf category exists;
    - All secondary categories and collections exist;
    - All image records exist on disk.
    """
    category_slugs: set[str] = set()
    root_slugs = [cat["slug"] for cat in taxonomy_tree]
    expected_roots = ["flowers", "amigurumi", "baby", "home-decor", "pooja-devotional"]
    if root_slugs != expected_roots:
        raise ValueError(f"Root categories must follow storefront order {expected_roots}, got {root_slugs}")

    for cat in taxonomy_tree:
        if cat["slug"] in category_slugs:
            raise ValueError(f"Duplicate root category slug: {cat['slug']}")
        category_slugs.add(cat["slug"])
        for child in cat.get("children", []):
            if child["slug"] in category_slugs:
                raise ValueError(f"Duplicate subcategory slug: {child['slug']}")
            category_slugs.add(child["slug"])

    collection_slugs: set[str] = set()
    for col in collections_data:
        if col["slug"] in collection_slugs:
            raise ValueError(f"Duplicate collection slug: {col['slug']}")
        collection_slugs.add(col["slug"])

    product_slugs: set[str] = set()
    seen_skus: set[str] = set()
    seen_primary_images: set[str] = set()

    for p in products_data:
        p_slug = p["slug"]
        if p_slug in product_slugs:
            raise ValueError(f"Duplicate product slug: {p_slug}")
        product_slugs.add(p_slug)

        # Primary category validation
        prim_cat = p.get("primary_category_slug")
        if not prim_cat or prim_cat not in category_slugs:
            raise ValueError(f"Product '{p_slug}' has invalid primary category slug: '{prim_cat}'")

        # Secondary categories validation
        for sec_cat in p.get("secondary_category_slugs", []):
            if sec_cat not in category_slugs:
                raise ValueError(f"Product '{p_slug}' references unknown secondary category slug: '{sec_cat}'")

        # Collections validation
        for col_slug in p.get("collection_slugs", []):
            if col_slug not in collection_slugs:
                raise ValueError(f"Product '{p_slug}' references unknown collection slug: '{col_slug}'")

        # Primary image validation
        prim_img = p.get("image")
        if not prim_img:
            raise ValueError(f"Product '{p_slug}' is missing a primary image")
        if prim_img in seen_primary_images:
            raise ValueError(f"Primary image key '{prim_img}' is reused across multiple product slugs")
        seen_primary_images.add(prim_img)

        # Local image file existence validation
        local_path = image_dir / prim_img
        if not local_path.exists():
            raise ValueError(f"Product '{p_slug}' primary image does not exist on disk: {local_path}")

        for g_img in p.get("images", []):
            g_path = image_dir / g_img
            if not g_path.exists():
                raise ValueError(f"Product '{p_slug}' gallery image does not exist on disk: {g_path}")

        # Variant SKU validation
        variants = p.get("variants", [])
        if not variants:
            raise ValueError(f"Product '{p_slug}' must have at least one variant")
        for v in variants:
            sku = (v.get("sku") or "").strip()
            if not sku:
                raise ValueError(f"Product '{p_slug}' has variant with empty SKU")
            if sku in seen_skus:
                raise ValueError(f"Duplicate SKU '{sku}' found across catalogue")
            seen_skus.add(sku)


def _seed_taxonomy_and_products(db: Session) -> None:
    """Populate Categories, Collections, Products, Variants, and Associations."""
    validate_seed_data(TAXONOMY_TREE, COLLECTIONS_DATA, PRODUCTS_DATA, LOCAL_IMAGE_DIR)

    # 1. Seed Categories
    category_slug_map: dict[str, Category] = {}
    for parent_idx, parent_data in enumerate(TAXONOMY_TREE, start=1):
        parent_cat = db.query(Category).filter_by(slug=parent_data["slug"]).first()
        if not parent_cat:
            parent_cat = Category(
                name=parent_data["name"],
                slug=parent_data["slug"],
                description=parent_data.get("description"),
                image_key=parent_data.get("image_key"),
                image=parent_data.get("image_key"),
                parent_id=None,
                display_order=parent_idx,
                is_active=True,
                show_when_empty=False,
            )
            db.add(parent_cat)
            db.flush()
        else:
            parent_cat.name = parent_data["name"]
            parent_cat.description = parent_data.get("description")
            parent_cat.image_key = parent_data.get("image_key")
            parent_cat.image = parent_data.get("image_key")
            parent_cat.display_order = parent_idx
            parent_cat.show_when_empty = False
        category_slug_map[parent_data["slug"]] = parent_cat

        for child_idx, child_data in enumerate(parent_data.get("children", []), start=1):
            child_cat = db.query(Category).filter_by(slug=child_data["slug"]).first()
            if not child_cat:
                child_cat = Category(
                    name=child_data["name"],
                    slug=child_data["slug"],
                    parent_id=parent_cat.id,
                    display_order=child_idx,
                    is_active=True,
                    show_when_empty=False,
                )
                db.add(child_cat)
                db.flush()
            else:
                child_cat.name = child_data["name"]
                child_cat.parent_id = parent_cat.id
                child_cat.display_order = child_idx
                child_cat.show_when_empty = False
            category_slug_map[child_data["slug"]] = child_cat

    # 2. Seed Collections
    collection_slug_map: dict[str, Collection] = {}
    for col_data in COLLECTIONS_DATA:
        col = db.query(Collection).filter_by(slug=col_data["slug"]).first()
        if not col:
            col = Collection(
                name=col_data["name"],
                slug=col_data["slug"],
                description=col_data.get("description"),
                collection_type=col_data.get("collection_type", "EVERGREEN"),
                display_order=col_data.get("display_order", 0),
                is_active=True,
            )
            db.add(col)
            db.flush()
        else:
            col.name = col_data["name"]
            col.description = col_data.get("description")
            col.collection_type = col_data.get("collection_type", "EVERGREEN")
            col.display_order = col_data.get("display_order", 0)
        collection_slug_map[col_data["slug"]] = col

    # 3. Seed Occasions
    for occ_data in OCCASIONS_DATA:
        occ = db.query(Occasion).filter_by(id=occ_data["id"]).first()
        if not occ:
            occ = Occasion(
                id=occ_data["id"],
                name=occ_data["name"],
                icon=occ_data["icon"],
                image_url=occ_data["image_url"],
            )
            db.add(occ)
        else:
            occ.name = occ_data["name"]
            occ.icon = occ_data["icon"]
            occ.image_url = occ_data["image_url"]

    # 4. Seed Tags
    tag_map: dict[str, Tag] = {}
    for p in PRODUCTS_DATA:
        for t_name in p.get("tags", []):
            if t_name not in tag_map:
                existing = db.query(Tag).filter_by(name=t_name).first()
                if not existing:
                    t = Tag(name=t_name)
                    db.add(t)
                    db.flush()
                    tag_map[t_name] = t
                else:
                    tag_map[t_name] = existing

    # 5. Seed Products, Variants, Images, Categories, and Collections
    for p_data in PRODUCTS_DATA:
        product = db.query(Product).filter_by(id=p_data["id"]).first()
        if not product:
            product = Product(
                id=p_data["id"],
                name=p_data["name"],
                slug=p_data["slug"],
                description=p_data.get("description"),
                short_description=p_data.get("description", "")[:120],
                primary_image=p_data["image"],
                badge=p_data.get("badge"),
                customizable=p_data.get("customizable", False),
                rating=p_data.get("rating", 5.0),
                reviews_count=p_data.get("reviews", 0),
                status="ACTIVE",
                brand="Sulocraft",
                metadata_json={"customizable": p_data.get("customizable", False)},
            )
            db.add(product)
            db.flush()
        else:
            product.name = p_data["name"]
            product.slug = p_data["slug"]
            product.primary_image = p_data["image"]
            product.description = p_data.get("description")
            product.short_description = p_data.get("description", "")[:120]
            product.badge = p_data.get("badge")
            product.customizable = p_data.get("customizable", False)
            product.rating = p_data.get("rating", 5.0)
            product.reviews_count = p_data.get("reviews", 0)

        # Populate ProductCategory with exactly one primary category
        db.query(ProductCategory).filter(ProductCategory.product_id == product.id).delete()
        prim_slug = p_data["primary_category_slug"]
        all_cat_slugs = [prim_slug] + [s for s in p_data.get("secondary_category_slugs", []) if s != prim_slug]
        for idx, c_slug in enumerate(all_cat_slugs):
            if c_slug in category_slug_map:
                db.add(
                    ProductCategory(
                        product_id=product.id,
                        category_id=category_slug_map[c_slug].id,
                        is_primary=(c_slug == prim_slug),
                        display_order=idx,
                    )
                )

        # Populate ProductCollection
        db.query(ProductCollection).filter(ProductCollection.product_id == product.id).delete()
        for idx, col_slug in enumerate(p_data.get("collection_slugs", [])):
            if col_slug in collection_slug_map:
                db.add(
                    ProductCollection(
                        product_id=product.id,
                        collection_id=collection_slug_map[col_slug].id,
                        display_order=idx,
                    )
                )

        # Populate Tags
        product.tags.clear()
        for t_name in p_data.get("tags", []):
            if t_name in tag_map:
                product.tags.append(tag_map[t_name])

        # Populate Gallery Images
        db.query(ProductImage).filter(ProductImage.product_id == product.id).delete()
        for idx, img_url in enumerate(p_data.get("images", [p_data["image"]])):
            db.add(
                ProductImage(
                    product_id=product.id,
                    url=img_url,
                    alt_text=f"{product.name} handcrafted photo {idx + 1}",
                    sort_order=idx,
                    is_primary=(idx == 0),
                )
            )

        # Populate Variants
        db.query(ProductVariant).filter(ProductVariant.product_id == product.id).delete()
        for v_data in p_data.get("variants", []):
            db.add(
                ProductVariant(
                    product_id=product.id,
                    sku=v_data["sku"],
                    name=v_data["name"],
                    price=v_data["price"],
                    stock_quantity=v_data.get("stock", 10),
                    status="ACTIVE",
                    attributes_json=v_data.get("attributes", {}),
                )
            )

    db.flush()

    # 6. Seed Reviews
    for r in REVIEWS_DATA:
        rev = db.query(Review).filter_by(id=r["id"]).first()
        matching_product = db.query(Product).filter(Product.name.ilike(f"%{r['product_name']}%")).first()
        if not rev:
            db.add(
                Review(
                    id=r["id"],
                    product_id=matching_product.id if matching_product else None,
                    product_name=r["product_name"],
                    author_name=r["name"],
                    location=r["location"],
                    rating=r["rating"],
                    text=r["text"],
                    avatar_url=r["avatar_url"],
                    date=r["date"],
                )
            )
        else:
            rev.avatar_url = r["avatar_url"]
            rev.author_name = r["name"]
            rev.text = r["text"]


def seed_storefront_content(db: Session) -> None:
    """Seed BrandSettings, rich hero campaigns, and controlled homepage sections."""
    brand = db.query(BrandSettings).first()
    if not brand:
        brand = BrandSettings(
            name="Sulocraft",
            owner_name="Anupama Sharma",
            instagram_url="https://instagram.com/sulocraft",
            whatsapp_url="https://wa.me/919876543210",
        )
        db.add(brand)
    else:
        brand.name = "Sulocraft"
        brand.owner_name = "Anupama Sharma"

    if db.query(HomepageCampaign).count() == 0:
        campaigns_data = [
            {
                "title": "Rooted in Warmth, Woven by Hand",
                "emphasis": "Every loop tells a story",
                "eyebrow": "Our Heritage",
                "description": "Founded by Anupama Sharma, Sulocraft preserves traditional crochet artistry through modern heirloom designs crafted in small artisanal batches.",
                "image_url": "hero/heritage.png",
                "image_alt": "Artisanal crochet yarn and handmade floral creation",
                "destination": "/about",
                "priority": 1,
                "is_active": True,
            },
            {
                "title": "Thoughtful Gifts for Festive Seasons",
                "emphasis": "Cherished moments",
                "eyebrow": "Festive Collection",
                "description": "Discover handcrafted festive hampers, delicate crochet pooja blooms, and heartwarming gifts crafted to bring joy.",
                "image_url": "hero/festive-gifting.png",
                "image_alt": "Festive handcrafted crochet gift box with ribbon",
                "destination": "/shop?collection=gifts",
                "priority": 2,
                "is_active": True,
            },
            {
                "title": "Fresh Floral Blooms & Modern Accents",
                "emphasis": "Just arrived in store",
                "eyebrow": "New Releases",
                "description": "Explore our latest collection of eternal potted flowers, handcrafted car charms, and pastel botanical bouquets.",
                "image_url": "hero/flower-bouquet.png",
                "image_alt": "Handmade crochet flowers and miniature potted plants",
                "destination": "/shop?category=flowers",
                "priority": 3,
                "is_active": True,
            },
            {
                "title": "Artisanal Accents for Cozy Living",
                "emphasis": "Bespoke elegance",
                "eyebrow": "Home & Living",
                "description": "Elevate your sanctuary with intricate coasters, bohemian wall hangings, and tactile home accents that radiate warmth.",
                "image_url": "hero/home-decor.png",
                "image_alt": "Crochet table coaster and boho wall hanging decor",
                "destination": "/shop?category=home-decor",
                "priority": 4,
                "is_active": True,
            },
            {
                "title": "Made Specially for Your Special Occasions",
                "emphasis": "Personalized for you",
                "eyebrow": "Custom Orders",
                "description": "From personalized initials to custom colorways and bridal bouquets, collaborate directly with our artisans.",
                "image_url": "hero/custom-bouquet.png",
                "image_alt": "Custom colored yarn and bespoke crochet monogram project",
                "destination": "/contact?subject=custom-order",
                "priority": 5,
                "is_active": True,
            },
            {
                "title": "Whimsical Amigurumi & Playful Companions",
                "emphasis": "Stitched with love",
                "eyebrow": "Amigurumi",
                "description": "Delight in hand-stitched amigurumi companions, charming animal keychains, and nursery treasures made with soft baby-safe yarn.",
                "image_url": "hero/amigurumi.png",
                "image_alt": "Handmade crochet amigurumi animals and plush companions",
                "destination": "/shop?category=amigurumi",
                "priority": 6,
                "is_active": True,
            },
        ]
        for c in campaigns_data:
            db.add(HomepageCampaign(**c))

    if db.query(HomepageSection).count() == 0:
        sections_data = [
            {
                "section_type": "category_grid",
                "title": "Shop by Category",
                "eyebrow": "Browse by Collection",
                "display_order": 1,
                "is_enabled": True,
                "item_limit": 4,
                "metadata_json": {"category_slugs": ["flowers", "amigurumi", "home-decor", "pooja-devotional"]},
            },
            {
                "section_type": "product_collection",
                "title": "Most Loved Creations",
                "eyebrow": "Customer Favourites",
                "collection_slug": "bestsellers",
                "display_order": 2,
                "is_enabled": True,
                "item_limit": 4,
            },
            {
                "section_type": "promo_banner",
                "title": "Gift Handcrafted Warmth This Season",
                "description": "Every stitch carries intention. Order early for personalized bouquets and festive keepsakes.",
                "image_url": "sections/gift-handcrafted-warmth.png",
                "image_alt": "Handcrafted crochet gifts and bouquets",
                "cta_text": "Explore Gift Guide",
                "cta_url": "/shop?collection=gifts",
                "display_order": 3,
                "is_enabled": True,
            },
            {
                "section_type": "review_section",
                "title": "Loved by Over 500+ Happy Customers",
                "eyebrow": "Customer Stories",
                "display_order": 4,
                "is_enabled": True,
                "item_limit": 3,
            },
            {
                "section_type": "image_text",
                "title": "Handmade with Love, Thread by Thread",
                "description": "Founded by Anupama Sharma, Sulocraft preserves traditional crochet artistry through modern heirloom designs crafted in small artisanal batches.",
                "image_url": "about/anupama-sharma.png",
                "image_alt": "Sulocraft artisan crocheting flowers",
                "image_position": "left",
                "cta_text": "Our Story",
                "cta_url": "/about",
                "display_order": 5,
                "is_enabled": True,
            },
        ]
        for s in sections_data:
            db.add(HomepageSection(**s))
    else:
        # Repair existing development rows pointing to outdated/missing image keys
        existing_sections = db.query(HomepageSection).all()
        for s in existing_sections:
            if s.section_type == "promo_banner" and (s.image_url == "campaigns/promo-gift-warmth.jpg" or not s.image_url):
                s.image_url = "sections/gift-handcrafted-warmth.png"
            elif s.section_type == "image_text" and (s.image_url == "sections/artisan-story.jpg" or not s.image_url):
                s.image_url = "about/anupama-sharma.png"

    db.commit()


def reseed_catalogue(db: Session) -> None:
    """Clear and freshly re-seed all catalogue, occasion, review, and storefront records."""
    db.query(ProductImage).delete()
    db.query(ProductVariant).delete()
    db.execute(product_categories.delete())
    db.execute(product_collections.delete())
    db.execute(product_tags.delete())
    db.query(Review).delete()
    db.query(Product).delete()
    db.query(Collection).delete()
    db.query(Occasion).delete()
    db.query(Category).delete()
    db.query(Tag).delete()
    db.query(HomepageCampaign).delete()
    db.query(HomepageSection).delete()
    db.commit()
    seed_catalogue(db)


def seed_catalogue(db: Session, force: bool = False) -> None:
    """Populate database with hierarchical taxonomy, collections, products, variants, tags, reviews, admin, and storefront."""
    if force:
        reseed_catalogue(db)
        return

    _seed_taxonomy_and_products(db)

    # Seed Configurable Admin User (Anupama / Production) with verified email identity
    admin_emails = {settings.admin_email.strip().lower(), "admin@sulocraft.com"}
    for a_email in admin_emails:
        admin_user = db.query(User).filter(User.email == a_email).first()
        if not admin_user:
            admin_user = User(
                name=settings.admin_name if a_email == settings.admin_email.strip().lower() else "Store Admin",
                email=a_email,
                phone="9999900000" if a_email == "admin@sulocraft.com" else None,
                role="ADMIN",
                status="ACTIVE",
            )
            db.add(admin_user)
            db.flush()
            db.add(UserIdentity(user_id=admin_user.id, provider="email", provider_subject=a_email))
        else:
            admin_user.role = "ADMIN"
            has_email_id = any(i.provider == "email" for i in (admin_user.identities or []))
            if not has_email_id:
                db.add(UserIdentity(user_id=admin_user.id, provider="email", provider_subject=a_email))

    seed_storefront_content(db)
    db.commit()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    force_reseed = "--force" in sys.argv or "--reseed" in sys.argv
    with SessionLocal() as session:
        seed_catalogue(session, force=force_reseed)
        print("Catalogue database seeded successfully!")

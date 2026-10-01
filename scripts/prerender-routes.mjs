import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repositoryRoot = path.resolve(__dirname, '..');

const BASE_URL = 'https://sulocraft.com';
const IMAGE_BASE_URL = 'https://images.sulocraft.com';

export function getPublicRoutes() {
  const routes = [];

  // 1. Static Core Pages
  routes.push({
    path: '/',
    canonicalPath: '/',
    title: 'Sulocraft | Handcrafted Heirloom Crochet Creations',
    description: 'Discover heirloom-quality handcrafted crochet creations. Permanent blooms, adorable amigurumi toys, puja essentials, and bespoke gifts handmade with love.',
    pageType: 'website',
    breadcrumbs: [{ name: 'Home', path: '/' }],
    heading: 'Handcrafted Heirloom Crochet',
    summary: 'Permanent blooms, adorable amigurumi companions, cozy baby essentials, and devotional decor lovingly hand-crocheted in India.',
  });

  routes.push({
    path: '/shop',
    canonicalPath: '/shop',
    title: 'Shop Handcrafted Crochet Creations | Sulocraft',
    description: 'Browse our complete collection of handmade crochet flowers, amigurumi plushies, baby sets, puja essentials, and artisanal home decor.',
    pageType: 'collection',
    breadcrumbs: [{ name: 'Home', path: '/' }, { name: 'Shop', path: '/shop' }],
    heading: 'All Products',
    summary: 'Handcrafted creations made with pure cotton and hypoallergenic yarn.',
  });

  routes.push({
    path: '/about',
    canonicalPath: '/about',
    title: 'About Our Studio | Sulocraft',
    description: 'Learn the story behind Sulocraft, our founder Anupama, and our dedicated team of Indian women artisans crafting heirloom crochet.',
    pageType: 'website',
    breadcrumbs: [{ name: 'Home', path: '/' }, { name: 'About', path: '/about' }],
    heading: 'About Sulocraft',
    summary: 'Celebrating Indian craftsmanship, empowering women artisans, and preserving the timeless art of crochet.',
  });

  routes.push({
    path: '/contact',
    canonicalPath: '/contact',
    title: 'Contact Us | Sulocraft',
    description: 'Get in touch with Sulocraft for bespoke orders, gifting inquiries, and customer support. We are here to help.',
    pageType: 'website',
    breadcrumbs: [{ name: 'Home', path: '/' }, { name: 'Contact', path: '/contact' }],
    heading: 'Contact Us',
    summary: 'Reach out to our artisan team for custom orders and assistance.',
  });

  routes.push({
    path: '/shipping-policy',
    canonicalPath: '/shipping-policy',
    title: 'Shipping Policy | Sulocraft',
    description: 'Shipping timelines, standard rates, insured courier delivery across India, and tracking policies for Sulocraft handcrafted creations.',
    pageType: 'website',
    breadcrumbs: [{ name: 'Home', path: '/' }, { name: 'Shipping Policy', path: '/shipping-policy' }],
    heading: 'Shipping Policy',
    summary: 'Safe, insured delivery across India with reliable courier partners.',
  });

  routes.push({
    path: '/return-policy',
    canonicalPath: '/return-policy',
    title: 'Return & Refund Policy | Sulocraft',
    description: 'Information regarding returns, transit damage resolution, and refunds for Sulocraft artisanal products.',
    pageType: 'website',
    breadcrumbs: [{ name: 'Home', path: '/' }, { name: 'Return Policy', path: '/return-policy' }],
    heading: 'Return & Refund Policy',
    summary: 'Clear guidelines on artisan returns and transit damage replacements.',
  });

  routes.push({
    path: '/privacy-policy',
    canonicalPath: '/privacy-policy',
    title: 'Privacy Policy | Sulocraft',
    description: 'How Sulocraft collects, protects, and handles your personal information with strict data privacy standards.',
    pageType: 'website',
    breadcrumbs: [{ name: 'Home', path: '/' }, { name: 'Privacy Policy', path: '/privacy-policy' }],
    heading: 'Privacy Policy',
    summary: 'Our commitment to data protection and privacy.',
  });

  routes.push({
    path: '/terms',
    canonicalPath: '/terms',
    title: 'Terms of Service | Sulocraft',
    description: 'Terms and conditions governing purchases, payments, and site usage on Sulocraft.',
    pageType: 'website',
    breadcrumbs: [{ name: 'Home', path: '/' }, { name: 'Terms of Service', path: '/terms' }],
    heading: 'Terms of Service',
    summary: 'Terms and conditions for Sulocraft store.',
  });

  // 2. Canonical Categories
  const categories = [
    { name: 'Flowers', slug: 'flowers', desc: 'Handcrafted permanent blooms, bouquets, and stems', parent: null },
    { name: 'Bouquets', slug: 'bouquets', desc: 'Lush handcrafted crochet bouquets for gifting and milestones', parent: 'Flowers' },
    { name: 'Roses', slug: 'roses', desc: 'Forever crochet roses stitched with romantic deep hues', parent: 'Flowers' },
    { name: 'Tulips', slug: 'tulips', desc: 'Artisanal pastel crochet tulips that celebrate spring forever', parent: 'Flowers' },
    { name: 'Sunflowers', slug: 'sunflowers', desc: 'Bright, cheerful handcrafted sunflowers bringing warmth to any space', parent: 'Flowers' },
    { name: 'Amigurumi', slug: 'amigurumi', desc: 'Hand-stitched plush toys, animals, and miniature keepsakes', parent: null },
    { name: 'Bunny', slug: 'bunny', desc: 'Charming crochet bunnies in artisanal handmade attire', parent: 'Amigurumi' },
    { name: 'Teddy Bear', slug: 'teddy-bear', desc: 'Cuddly amigurumi teddy bears stitched with soft cotton yarn', parent: 'Amigurumi' },
    { name: 'Animals', slug: 'animals', desc: 'Playful handmade amigurumi animals for keepsakes and nurseries', parent: 'Amigurumi' },
    { name: 'Baby', slug: 'baby', desc: 'Soft cotton booties, rattles, blankets, and nursery décor', parent: null },
    { name: 'Toys', slug: 'toys', desc: 'Hypoallergenic baby-safe crochet toys and rattles', parent: 'Baby' },
    { name: 'Home & Decor', slug: 'home-decor', desc: 'Crochet wall hangings, planters, coasters, and festive decor', parent: null },
    { name: 'Coasters', slug: 'coasters', desc: 'Handmade absorbent cotton coasters for warm tea gatherings', parent: 'Home & Decor' },
    { name: 'Pooja & Devotional', slug: 'pooja-devotional', desc: 'Devotional garlands, malas, torans, and temple décor', parent: null },
    { name: 'Garlands', slug: 'garlands', desc: 'Sacred everlasting marigold and lotus malas for festive ceremonies', parent: 'Pooja & Devotional' },
    { name: 'Torans', slug: 'torans', desc: 'Festive handmade door hangings bringing auspicious blessings', parent: 'Pooja & Devotional' },
  ];

  for (const cat of categories) {
    const breadcrumbs = [{ name: 'Home', path: '/' }, { name: 'Shop', path: '/shop' }];
    if (cat.parent) {
      breadcrumbs.push({ name: cat.parent, path: `/categories/${cat.parent.toLowerCase().replace(/[^a-z0-9]+/g, '-')}` });
    }
    breadcrumbs.push({ name: cat.name, path: `/categories/${cat.slug}` });

    routes.push({
      path: `/categories/${cat.slug}`,
      canonicalPath: `/categories/${cat.slug}`,
      title: `${cat.name} | Handcrafted Crochet | Sulocraft`,
      description: cat.desc,
      pageType: 'collection',
      breadcrumbs,
      heading: cat.name,
      summary: cat.desc,
      imageUrl: `${IMAGE_BASE_URL}/categories/${cat.slug}/card.png`,
    });
  }

  // 3. Canonical Collections
  const collections = [
    { name: 'Best Sellers', slug: 'bestsellers', desc: "Sulocraft's most cherished and requested handcrafted creations" },
    { name: 'New Arrivals', slug: 'new-arrivals', desc: 'Fresh designs and newly released artisanal pieces from our studio' },
    { name: 'Gifts', slug: 'gifts', desc: 'Handcrafted crochet gift ideas for every occasion' },
    { name: 'Birthday Gifts', slug: 'birthday-gifts', desc: 'Make birthdays memorable with vibrant handcrafted blooms' },
    { name: 'Anniversary Gifts', slug: 'anniversary-gifts', desc: 'Everlasting crochet flowers and keepsakes celebrating shared milestones' },
    { name: 'Wedding Gifts', slug: 'wedding-gifts', desc: 'Elegant heirloom crochet designs for couples and celebrations' },
    { name: 'Gifts for Her', slug: 'gifts-for-her', desc: 'Delicate floral bouquets, personalized letters, and timeless keepsakes' },
    { name: 'Gifts for Kids', slug: 'gifts-for-kids', desc: 'Playful amigurumi animals and snuggly handmade friends' },
  ];

  for (const col of collections) {
    routes.push({
      path: `/collections/${col.slug}`,
      canonicalPath: `/collections/${col.slug}`,
      title: `${col.name} | Curated Crochet Gifts | Sulocraft`,
      description: col.desc,
      pageType: 'collection',
      breadcrumbs: [{ name: 'Home', path: '/' }, { name: 'Shop', path: '/shop' }, { name: col.name, path: `/collections/${col.slug}` }],
      heading: col.name,
      summary: col.desc,
    });
  }

  // 4. Products (from seed manifest or fallback)
  let seedProducts = [];
  try {
    const seedPath = path.join(repositoryRoot, 'docs', 'product-catalogue-seed.json');
    if (fs.existsSync(seedPath)) {
      const data = JSON.parse(fs.readFileSync(seedPath, 'utf8'));
      seedProducts = data.products || [];
    }
  } catch (err) {
    console.warn('[prerender] Could not load product-catalogue-seed.json, using fallback products');
  }

  const productMeta = {
    'forever-crochet-rose-bouquet': { price: 2599, rating: 4.9, reviews: 128, category: 'Bouquets', desc: 'A timeless bouquet of handcrafted crochet roses that never wilt. Each petal is lovingly stitched by hand, making every bouquet truly one of a kind.' },
    'crochet-tulip-bouquet': { price: 1599, rating: 4.8, reviews: 96, category: 'Tulips', desc: 'Delicate, pastel crochet tulips wrapped in artisanal craft paper. Bring spring into your home forever without watering.' },
    'heart-bear': { price: 1799, rating: 4.9, reviews: 84, category: 'Toys', desc: 'An adorable teddy bear clutching a bright red heart. Stitched with hypoallergenic cotton yarn, perfect for babies and keepsakes.' },
    'couple-bunny-set': { price: 3299, rating: 5.0, reviews: 52, category: 'Bunny', desc: 'A charming pair of groom and bride bunnies in custom bridal outfits. An unforgettable handmade wedding or anniversary gift.' },
    'mini-panda-amigurumi': { price: 1299, rating: 4.7, reviews: 43, category: 'Animals', desc: 'Playful palm-sized amigurumi panda crafted with soft yarn, ideal for gifting or desktop companionship.' },
    'crochet-bunny': { price: 1499, rating: 4.8, reviews: 67, category: 'Bunny', desc: 'Gentle floppy-eared crochet bunny with charming dungarees, handcrafted for nurseries and children.' },
    'crochet-marigold-garland': { price: 1899, rating: 4.9, reviews: 112, category: 'Garlands', desc: 'Vibrant marigold garland hand-crocheted in festive golden-orange hues for temple decor and Diwali celebrations.' },
    'sunflower-bouquet': { price: 1999, rating: 4.9, reviews: 75, category: 'Sunflowers', desc: 'Radiant handcrafted crochet sunflowers radiating joy, optimism, and warmth forever.' },
    'crochet-hanging-planter': { price: 1399, rating: 4.6, reviews: 38, category: 'Home & Decor', desc: 'Boho hanging basket woven with durable cotton cord to display small potted plants or crochet blooms.' },
    'boho-wall-hanging': { price: 2999, rating: 4.8, reviews: 29, category: 'Home & Decor', desc: 'Intricately patterned artisan crochet tapestry suspended from a polished natural wooden dowel.' },
    'love-letter-crochet-set': { price: 3499, rating: 5.0, reviews: 48, category: 'Gifts', desc: 'A bespoke keepsake set featuring an embroidered crochet envelope, handmade flowers, and keepsake charm.' },
    'mini-rose-box': { price: 1699, rating: 4.7, reviews: 56, category: 'Roses', desc: 'A cluster of miniature crochet roses nested in a luxury textured gift box ready for gifting.' },
    'lotus-mala': { price: 999, rating: 4.9, reviews: 62, category: 'Garlands', desc: 'Pure white and sacred pink crochet lotus prayer garland designed for spiritual altars and auspicious ceremonies.' },
    'crochet-toran': { price: 2199, rating: 4.8, reviews: 81, category: 'Torans', desc: 'Traditional handcrafted entrance hanging with floral motifs, beads, and festive colorways welcoming prosperity.' },
    'daisy-coaster-set': { price: 899, rating: 4.8, reviews: 94, category: 'Coasters', desc: 'Set of four cheerful handmade daisy flower coasters, absorbing moisture while brightening coffee tables.' },
    'mini-teddy-bear': { price: 1099, rating: 4.9, reviews: 112, category: 'Teddy Bear', desc: 'Pocket-sized artisan teddy bear clutching a petite daisy blossom, stitched with premium hypoallergenic yarn.' },
  };

  const productSlugs = seedProducts.length > 0
    ? seedProducts.map(p => ({ slug: p.slug, name: p.name, primaryImage: p.media?.find(m => m.role === 'primary')?.key || `products/${p.slug}/primary.png`, sku: p.defaultSku }))
    : Object.keys(productMeta).map(slug => ({
        slug,
        name: slug.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
        primaryImage: `products/${slug}/primary.png`,
        sku: `SULO-${slug.toUpperCase()}-001`,
      }));

  for (const p of productSlugs) {
    const meta = productMeta[p.slug] || { price: 1499, rating: 5.0, reviews: 10, category: 'Crafts', desc: `${p.name} handcrafted by Sulocraft artisans.` };
    const imageUrl = `${IMAGE_BASE_URL}/${p.primaryImage}`;

    routes.push({
      path: `/products/${p.slug}`,
      canonicalPath: `/products/${p.slug}`,
      title: `${p.name} | Sulocraft`,
      description: meta.desc,
      pageType: 'product',
      breadcrumbs: [
        { name: 'Home', path: '/' },
        { name: 'Shop', path: '/shop' },
        { name: meta.category, path: `/categories/${meta.category.toLowerCase().replace(/[^a-z0-9]+/g, '-')}` },
        { name: p.name, path: `/products/${p.slug}` },
      ],
      heading: p.name,
      summary: meta.desc,
      imageUrl,
      price: meta.price,
      currency: 'INR',
      sku: p.sku,
      rating: meta.rating,
      reviews: meta.reviews,
      category: meta.category,
      inStock: true,
    });
  }

  return routes;
}

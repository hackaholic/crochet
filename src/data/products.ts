export interface Product {
  id: number;
  name: string;
  slug?: string;
  price: number;
  originalPrice?: number;
  rating: number;
  reviews: number;
  image: string;
  images?: string[];
  category: string;
  primaryCategory?: TaxonomyReference;
  categories?: TaxonomyReference[];
  collections?: TaxonomyReference[];
  badge?: string;
  tags?: string[];
  occasions?: string[];
  description?: string;
  customizable?: boolean;
  inStock?: boolean;
}

export interface TaxonomyReference {
  name: string;
  slug: string;
}

const IMG = (id: string, w = 600, h = 600) =>
  `https://images.unsplash.com/${id}?w=${w}&h=${h}&fit=crop&auto=format`;

export const products: Product[] = [
  {
    id: 1,
    name: 'Forever Crochet Rose Bouquet',
    price: 2599,
    rating: 4.9,
    reviews: 128,
    image: IMG('photo-1700171518313-5dd219beaaa6'),
    images: [
      IMG('photo-1700171518313-5dd219beaaa6'),
      IMG('photo-1700171394718-2457b1190444'),
      IMG('photo-1700170447159-9d2d0da133a5'),
      IMG('photo-1700171458554-46cfd3f2a87a'),
    ],
    category: 'Flowers',
    badge: 'Bestseller',
    tags: ['romantic', 'anniversary', 'valentine'],
    description: 'A timeless bouquet of handcrafted crochet roses that never wilt. Each petal is lovingly stitched by hand, making every bouquet truly one of a kind.',
    customizable: true,
  },
  {
    id: 2,
    name: 'Crochet Tulip Bouquet',
    price: 1599,
    rating: 4.8,
    reviews: 96,
    image: IMG('photo-1700171394718-2457b1190444'),
    category: 'Flowers',
    badge: 'New',
    tags: ['romantic', 'birthday'],
    customizable: true,
  },
  {
    id: 3,
    name: 'Heart Bear',
    price: 1799,
    rating: 4.9,
    reviews: 84,
    image: IMG('photo-1602773984044-3ecbed81556d'),
    category: 'Gifts',
    badge: 'Bestseller',
    tags: ['romantic', 'valentine', 'birthday'],
    customizable: false,
  },
  {
    id: 4,
    name: 'Couple Bunny Set',
    price: 3299,
    rating: 5.0,
    reviews: 52,
    image: IMG('photo-1629019317873-3f603b269723'),
    category: 'Gifts',
    badge: 'Limited',
    tags: ['romantic', 'anniversary'],
    customizable: true,
  },
  {
    id: 5,
    name: 'Mini Panda Amigurumi',
    price: 1299,
    rating: 4.7,
    reviews: 73,
    image: IMG('photo-1602773974733-b56200c8653f'),
    category: 'Amigurumi',
    badge: 'Handmade',
    tags: ['baby', 'birthday'],
    customizable: false,
  },
  {
    id: 6,
    name: 'Crochet Bunny',
    price: 1199,
    rating: 4.8,
    reviews: 61,
    image: IMG('photo-1753370241607-5d48d8aaa70e'),
    category: 'Amigurumi',
    tags: ['baby', 'birthday'],
    customizable: false,
  },
  {
    id: 7,
    name: 'Crochet Marigold Garland',
    price: 1999,
    rating: 4.9,
    reviews: 45,
    image: IMG('photo-1700170447159-9d2d0da133a5'),
    category: 'Pooja',
    badge: 'Bestseller',
    tags: ['pooja', 'diwali', 'festive'],
    customizable: true,
  },
  {
    id: 8,
    name: 'Sunflower Bouquet',
    price: 2199,
    rating: 4.8,
    reviews: 88,
    image: IMG('photo-1700171458554-46cfd3f2a87a'),
    category: 'Flowers',
    badge: 'Bestseller',
    tags: ['birthday', 'housewarming'],
    customizable: true,
  },
  {
    id: 9,
    name: 'Crochet Hanging Planter',
    price: 1499,
    rating: 4.6,
    reviews: 39,
    image: IMG('photo-1550376026-7375b92bb318'),
    category: 'Home Décor',
    tags: ['housewarming', 'home'],
    customizable: false,
  },
  {
    id: 10,
    name: 'Boho Wall Hanging',
    price: 2999,
    rating: 4.7,
    reviews: 54,
    image: IMG('photo-1618574760337-2750f6251d20'),
    category: 'Home Décor',
    tags: ['housewarming', 'home'],
    customizable: true,
  },
  {
    id: 11,
    name: 'Love Letter Crochet Set',
    price: 3499,
    rating: 4.9,
    reviews: 34,
    image: IMG('photo-1646182504823-a02b768e28b5'),
    category: 'Gifts',
    badge: 'New',
    tags: ['romantic', 'valentine', 'anniversary'],
    customizable: true,
  },
  {
    id: 12,
    name: 'Mini Rose Box',
    price: 1899,
    rating: 4.8,
    reviews: 67,
    image: IMG('photo-1608825154649-2e9bb4cd4211'),
    category: 'Flowers',
    tags: ['romantic', 'birthday', 'mother'],
    customizable: true,
  },
  {
    id: 13,
    name: 'Lotus Mala',
    price: 999,
    rating: 4.7,
    reviews: 28,
    image: IMG('photo-1700171518313-5dd219beaaa6'),
    category: 'Pooja',
    tags: ['pooja', 'festive'],
    customizable: false,
  },
  {
    id: 14,
    name: 'Crochet Toran',
    price: 1799,
    rating: 4.8,
    reviews: 41,
    image: IMG('photo-1700171394718-2457b1190444'),
    category: 'Pooja',
    badge: 'Bestseller',
    tags: ['pooja', 'diwali', 'housewarming'],
    customizable: true,
  },
  {
    id: 15,
    name: 'Daisy Coaster Set',
    price: 899,
    rating: 4.5,
    reviews: 93,
    image: IMG('photo-1700170447159-9d2d0da133a5'),
    category: 'Home Décor',
    badge: 'Bestseller',
    tags: ['home', 'housewarming'],
    customizable: false,
  },
  {
    id: 16,
    name: 'Mini Teddy Bear',
    price: 1099,
    rating: 4.6,
    reviews: 112,
    image: IMG('photo-1602773974733-b56200c8653f'),
    category: 'Amigurumi',
    badge: 'Bestseller',
    tags: ['baby', 'birthday', 'just because'],
    customizable: false,
  },
];

export const reviews = [
  {
    id: 1,
    name: 'Priya Sharma',
    location: 'Mumbai',
    rating: 5,
    text: 'Bought the Forever Rose bouquet for our anniversary and it looked even better than the pictures! My husband was completely surprised. The quality is exceptional.',
    product: 'Forever Rose Bouquet',
    image: 'https://i.pravatar.cc/60?img=47',
    date: '15 Aug 2026',
  },
  {
    id: 2,
    name: 'Ananya Krishnan',
    location: 'Bangalore',
    rating: 5,
    text: 'Ordered the Marigold Garland for Ganesh Chaturthi. It was absolutely stunning on our mandir! Everyone who visited asked where I got it from.',
    product: 'Crochet Marigold Garland',
    image: 'https://i.pravatar.cc/60?img=44',
    date: '2 Sep 2026',
  },
  {
    id: 3,
    name: 'Ritu Agarwal',
    location: 'Delhi',
    rating: 5,
    text: 'The Couple Bunny Set was the perfect wedding gift. The packaging was so beautiful — I almost didn\'t want to give it away! Sulocraft is truly special.',
    product: 'Couple Bunny Set',
    image: 'https://i.pravatar.cc/60?img=41',
    date: '20 Sep 2026',
  },
  {
    id: 4,
    name: 'Meera Pillai',
    location: 'Chennai',
    rating: 5,
    text: 'My daughter absolutely loves her mini panda! The craftsmanship is incredible. You can see the love that goes into every stitch. Will definitely order again.',
    product: 'Mini Panda Amigurumi',
    image: 'https://i.pravatar.cc/60?img=49',
    date: '8 Sep 2026',
  },
];

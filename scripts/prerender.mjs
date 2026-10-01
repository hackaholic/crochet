#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { getPublicRoutes } from './prerender-routes.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repositoryRoot = path.resolve(__dirname, '..');
const distDir = path.join(repositoryRoot, 'dist');
const templatePath = path.join(distDir, 'index.html');

const BASE_URL = 'https://sulocraft.com';

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

export function prerender() {
  if (!fs.existsSync(templatePath)) {
    console.error(`[prerender] Template not found at ${templatePath}. Run 'vite build' first.`);
    process.exit(1);
  }

  const templateHtml = fs.readFileSync(templatePath, 'utf8');
  const routes = getPublicRoutes();

  console.log(`[prerender] Starting pre-render for ${routes.length} public routes...`);

  let generatedCount = 0;

  for (const route of routes) {
    const canonicalUrl = `${BASE_URL}${route.canonicalPath}`;
    
    // 1. Build Meta Tags
    let metaTags = `\n    <title>${escapeHtml(route.title)}</title>`;
    metaTags += `\n    <meta name="description" content="${escapeHtml(route.description)}">`;
    metaTags += `\n    <meta name="robots" content="index,follow">`;
    metaTags += `\n    <link rel="canonical" href="${escapeHtml(canonicalUrl)}">`;
    metaTags += `\n    <meta property="og:title" content="${escapeHtml(route.title)}">`;
    metaTags += `\n    <meta property="og:description" content="${escapeHtml(route.description)}">`;
    metaTags += `\n    <meta property="og:type" content="${escapeHtml(route.pageType)}">`;
    metaTags += `\n    <meta property="og:url" content="${escapeHtml(canonicalUrl)}">`;
    metaTags += `\n    <meta property="og:site_name" content="Sulocraft">`;
    metaTags += `\n    <meta name="twitter:card" content="${route.imageUrl ? 'summary_large_image' : 'summary'}">`;
    metaTags += `\n    <meta name="twitter:title" content="${escapeHtml(route.title)}">`;
    metaTags += `\n    <meta name="twitter:description" content="${escapeHtml(route.description)}">`;

    if (route.imageUrl) {
      metaTags += `\n    <meta property="og:image" content="${escapeHtml(route.imageUrl)}">`;
      metaTags += `\n    <meta property="og:image:alt" content="${escapeHtml(route.heading)}">`;
      metaTags += `\n    <meta name="twitter:image" content="${escapeHtml(route.imageUrl)}">`;
    }

    // 2. Build Schema.org Scripts
    let schemas = '';

    // BreadcrumbList Schema
    if (route.breadcrumbs && route.breadcrumbs.length > 0) {
      const breadcrumbData = {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        itemListElement: route.breadcrumbs.map((b, idx) => ({
          '@type': 'ListItem',
          position: idx + 1,
          name: b.name,
          item: `${BASE_URL}${b.path}`,
        })),
      };
      schemas += `\n    <script type="application/ld+json" id="sulocraft-breadcrumb-schema">${JSON.stringify(breadcrumbData).replace(/</g, '\\u003c')}</script>`;
    }

    // Product Schema (for products)
    if (route.pageType === 'product' && route.price) {
      const productData = {
        '@context': 'https://schema.org',
        '@type': 'Product',
        name: route.heading,
        description: route.summary,
        image: route.imageUrl ? [route.imageUrl] : [],
        sku: route.sku || `SULO-${route.heading.toUpperCase().replace(/[^A-Z0-9]+/g, '-')}`,
        brand: { '@type': 'Brand', name: 'Sulocraft' },
        category: route.category || 'Crochet',
        offers: {
          '@type': 'Offer',
          priceCurrency: route.currency || 'INR',
          price: route.price,
          availability: route.inStock ? 'https://schema.org/InStock' : 'https://schema.org/OutOfStock',
          url: canonicalUrl,
        },
      };
      if (route.rating && route.reviews > 0) {
        productData.aggregateRating = {
          '@type': 'AggregateRating',
          ratingValue: route.rating,
          reviewCount: route.reviews,
        };
      }
      schemas += `\n    <script type="application/ld+json" id="sulocraft-product-schema">${JSON.stringify(productData).replace(/</g, '\\u003c')}</script>`;
    }

    // Organization & WebSite Schema
    if (route.path === '/') {
      const siteData = {
        '@context': 'https://schema.org',
        '@graph': [
          {
            '@type': 'Organization',
            '@id': `${BASE_URL}/#organization`,
            name: 'Sulocraft',
            url: BASE_URL,
            logo: `${BASE_URL}/images/logo.png`,
            sameAs: ['https://www.instagram.com/sulocraft'],
          },
          {
            '@type': 'WebSite',
            '@id': `${BASE_URL}/#website`,
            name: 'Sulocraft',
            url: BASE_URL,
            publisher: { '@id': `${BASE_URL}/#organization` },
          },
        ],
      };
      schemas += `\n    <script type="application/ld+json" id="sulocraft-site-schema">${JSON.stringify(siteData).replace(/</g, '\\u003c')}</script>`;
    }

    // 3. Meaningful Initial Server-Rendered Content for <div id="root">
    const breadcrumbHtml = route.breadcrumbs && route.breadcrumbs.length > 0
      ? `<nav aria-label="Breadcrumb" class="mb-4 text-xs text-[#8B6B4A]"><ol class="flex flex-wrap items-center gap-1">${route.breadcrumbs.map((b, idx) => `<li>${idx > 0 ? '<span class="mx-1">/</span>' : ''}<a href="${escapeHtml(b.path)}" class="hover:underline">${escapeHtml(b.name)}</a></li>`).join('')}</ol></nav>`
      : '';

    const productExtraHtml = route.pageType === 'product' && route.price
      ? `<div class="mt-4"><p class="text-3xl font-semibold text-[#2C1810]">₹${route.price}</p><p class="text-xs text-[#8B6B4A] mt-1">Inclusive of all taxes · Free shipping above ₹999</p>${route.imageUrl ? `<img src="${escapeHtml(route.imageUrl)}" alt="${escapeHtml(route.heading)}" class="mt-6 rounded-2xl w-full max-w-md object-cover shadow-sm" width="600" height="600" loading="eager" />` : ''}</div>`
      : '';

    const initialContent = `
      <div class="min-h-screen bg-[#FAF7F2] text-[#2C1810]">
        <div class="bg-[#2C1810] text-white text-center py-2 text-xs font-medium tracking-wide">
          <span>Free shipping on orders above ₹999</span>
          <span class="mx-3 opacity-40">|</span>
          <span>Handmade with love in India 🇮🇳</span>
        </div>
        <header class="border-b border-[#EDE4D0] bg-[#FAF7F2] py-4 px-4">
          <div class="max-w-7xl mx-auto flex items-center justify-between">
            <a href="/" class="font-bold text-[#2C1810] text-lg tracking-tight">Sulocraft</a>
            <nav class="flex gap-6 text-sm font-medium text-[#5C3D2E]">
              <a href="/" class="hover:text-[#C4622D]">Home</a>
              <a href="/shop" class="hover:text-[#C4622D]">Shop</a>
              <a href="/about" class="hover:text-[#C4622D]">About</a>
              <a href="/contact" class="hover:text-[#C4622D]">Contact</a>
            </nav>
          </div>
        </header>
        <main class="max-w-7xl mx-auto px-4 py-12">
          ${breadcrumbHtml}
          <h1 class="text-4xl font-medium text-[#2C1810] tracking-tight mb-4" style="font-family: var(--font-serif, serif)">${escapeHtml(route.heading)}</h1>
          <p class="text-[#8B6B4A] max-w-2xl leading-relaxed text-base">${escapeHtml(route.summary)}</p>
          ${productExtraHtml}
        </main>
      </div>
    `.trim();

    // 4. Inject into Template HTML
    let outputHtml = templateHtml;

    // Replace <title>
    outputHtml = outputHtml.replace(/<title>.*?<\/title>/i, '');
    
    // Inject Head metadata right before </head>
    outputHtml = outputHtml.replace('</head>', `${metaTags}${schemas}\n  </head>`);

    // Inject Root content inside <div id="root"></div>
    outputHtml = outputHtml.replace(
      /(<div id="root">)(<\/div>)/i,
      `$1${initialContent}$2`
    );

    // 5. Determine Destination File Path
    let targetFile;
    if (route.path === '/') {
      targetFile = path.join(distDir, 'index.html');
    } else {
      const cleanPath = route.path.replace(/^\/+|\/+$/g, '');
      const targetSubDir = path.join(distDir, cleanPath);
      fs.mkdirSync(targetSubDir, { recursive: true });
      targetFile = path.join(targetSubDir, 'index.html');
    }

    fs.writeFileSync(targetFile, outputHtml, 'utf8');
    generatedCount++;
  }

  console.log(`[prerender] Successfully pre-rendered ${generatedCount} static HTML routes into dist/`);
}

// Allow standalone execution
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  prerender();
}

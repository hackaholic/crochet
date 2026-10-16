import fs from 'node:fs';
import path from 'node:path';
import { gzipSync } from 'node:zlib';
import { fileURLToPath } from 'node:url';

export function artifactBudget(root, limits = {}) {
  const jsLimit = Number(limits.jsGzip ?? 120000);
  const cssLimit = Number(limits.cssGzip ?? 20000);
  if (![jsLimit, cssLimit].every(v => Number.isSafeInteger(v) && v > 0)) throw new Error('Positive byte budgets required');
  const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
  const urls = [...html.matchAll(/(?:src|href)="(\/assets\/[^"?#]+\.(?:js|css))"/g)].map(m => m[1].slice(1));
  const manifestPath = path.join(root, '.vite/manifest.json');
  const manifest = fs.existsSync(manifestPath) ? JSON.parse(fs.readFileSync(manifestPath, 'utf8')) : {};
  const assets = new Set(urls);
  const visited = new Set();
  function include(key) {
    if (visited.has(key)) return;
    visited.add(key);
    const chunk = manifest[key];
    if (!chunk) throw new Error(`Missing static manifest dependency ${key}`);
    assets.add(chunk.file);
    for (const css of chunk.css ?? []) assets.add(css);
    for (const dependency of chunk.imports ?? []) include(dependency);
  }
  for (const [key, chunk] of Object.entries(manifest)) if (chunk.isEntry) include(key);
  let jsGzip = 0, cssGzip = 0;
  const files = [...assets].map(file => {
    const filename = path.resolve(root, file);
    if (!filename.startsWith(path.resolve(root) + path.sep)) throw new Error('Unsafe manifest file');
    const body = fs.readFileSync(filename);
    const gzip = gzipSync(body).length;
    if (file.endsWith('.js')) jsGzip += gzip;
    if (file.endsWith('.css')) cssGzip += gzip;
    return { file, bytes: body.length, gzip };
  });
  if (!files.some(f => f.file.endsWith('.js'))) throw new Error('No initial JS found');
  return { files, jsGzip, cssGzip, limits: { jsGzip: jsLimit, cssGzip: cssLimit }, passed: jsGzip <= jsLimit && cssGzip <= cssLimit };
}
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const report = artifactBudget(process.argv[2] || 'dist', { jsGzip: process.env.PERF_INITIAL_JS_GZIP_BUDGET, cssGzip: process.env.PERF_INITIAL_CSS_GZIP_BUDGET });
  console.log(JSON.stringify(report, null, 2));
  if (!report.passed) process.exitCode = 1;
}

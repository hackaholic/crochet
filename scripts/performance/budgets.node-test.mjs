import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { artifactBudget } from './budgets.mjs';

test('initial budget includes static dependencies and excludes unopened lazy chunks', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'sulocraft-budget-'));
  try {
    fs.mkdirSync(path.join(root, 'assets')); fs.mkdirSync(path.join(root, '.vite'));
    fs.writeFileSync(path.join(root, 'index.html'), '<script src="/assets/main.js"></script>');
    for (const file of ['main.js', 'shared.js', 'admin.js', 'site.css']) fs.writeFileSync(path.join(root, 'assets', file), 'fixture'.repeat(100));
    fs.writeFileSync(path.join(root, '.vite/manifest.json'), JSON.stringify({ main: { isEntry: true, file: 'assets/main.js', imports: ['shared'], dynamicImports: ['admin'], css: ['assets/site.css'] }, shared: { file: 'assets/shared.js' }, admin: { file: 'assets/admin.js' } }));
    const result = artifactBudget(root);
    assert.equal(result.files.length, 3); assert.equal(result.passed, true);
    assert.equal(artifactBudget(root, { jsGzip: 1 }).passed, false);
    assert.throws(() => artifactBudget(root, { jsGzip: -1 }), /Positive/);
    fs.writeFileSync(path.join(root, '.vite/manifest.json'), JSON.stringify({ main: { isEntry: true, file: '../outside.js' } }));
    assert.throws(() => artifactBudget(root), /Unsafe/);
  } finally { fs.rmSync(root, { recursive: true }); }
});

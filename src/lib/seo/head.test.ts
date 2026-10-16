import { afterEach, expect, it } from 'vitest';
import { setSchema } from './head';
afterEach(() => { document.head.innerHTML = ''; });
it('serializes untrusted entity text without creating executable markup', () => {
  const text = '</script><script id="injected">alert(1)</script>';
  setSchema('product-schema', { '@type': 'Product', name: text });
  const script = document.getElementById('product-schema')!;
  expect(script.textContent).not.toContain('<');
  expect(JSON.parse(script.textContent!).name).toBe(text);
  expect(document.getElementById('injected')).toBeNull();
  setSchema('product-schema', undefined);
  expect(document.getElementById('product-schema')).toBeNull();
});

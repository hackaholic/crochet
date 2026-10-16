import { StrictMode } from 'react';
import { renderToString } from 'react-dom/server';
import { StaticRouter } from 'react-router';
import StorefrontApplication from './components/StorefrontApplication';
import type { PublicBootstrap } from './lib/seo/bootstrap';
export { toProduct } from './lib/api/catalogue';

export function render(bootstrap: PublicBootstrap): string {
  return renderToString(<StrictMode><StorefrontApplication bootstrap={bootstrap}
    router={children => <StaticRouter location={bootstrap.path}>{children}</StaticRouter>} /></StrictMode>);
}
export { buildProductSchema as productSchema } from './lib/seo/productSchema';

export { buildPageSchemas as pageSchemas } from './lib/seo/pageSchemas';

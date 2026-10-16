import type { PublicSeoPolicy } from '../lib/seo/urlPolicy.mjs';
import type { ReactNode } from 'react';
import App from '../App';
import { CatalogueProvider } from './CatalogueProvider';
import { CartProvider } from './CartProvider';
import { WishlistProvider } from './WishlistProvider';
import { PublicBootstrapContext, SeoPolicyContext, type PublicBootstrap } from '../lib/seo/bootstrap';

/** Shared by browser and build renderer; router is supplied by the caller. */
export default function StorefrontApplication({ bootstrap, router, policy }: {
  bootstrap?: PublicBootstrap;
  policy?: PublicSeoPolicy;
  router: (children: ReactNode) => ReactNode;
}) {
  return <PublicBootstrapContext.Provider value={bootstrap}>
    <SeoPolicyContext.Provider value={policy ?? bootstrap?.policy}>{router(<CatalogueProvider><CartProvider><WishlistProvider><App /></WishlistProvider></CartProvider></CatalogueProvider>)}</SeoPolicyContext.Provider>
  </PublicBootstrapContext.Provider>;
}

import type { PublicSeoPolicy } from './urlPolicy.mjs';
import { createContext, useContext } from 'react';
import type { Product } from '../../data/products';
import type { Category, Collection } from '../api/catalogue';
import type { SeoMetadata } from '../api/seo';
import type { StorefrontHomeContent } from '../api/storefront';

/** Public build data only. Never serialize customer, cart or session state. */
export interface PublicBootstrap {
  policy?: PublicSeoPolicy;
  path: string;
  products: Product[];
  categories: Category[];
  collections: Collection[];
  home: StorefrontHomeContent;
  metadata: SeoMetadata;
}
export const PublicBootstrapContext = createContext<PublicBootstrap | undefined>(undefined);
export const usePublicBootstrap = () => useContext(PublicBootstrapContext);

export const SeoPolicyContext = createContext<PublicSeoPolicy | undefined>(undefined);
export const useSeoPolicy = () => useContext(SeoPolicyContext);

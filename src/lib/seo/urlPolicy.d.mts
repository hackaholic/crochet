import type { SeoMetadata } from '../api/seo';
export interface PublicSeoPolicy {origin?: string; indexing: boolean; apiBase?: string; comingSoon?: boolean;}
export function safePath(value: string): string;
export function isPrivatePath(value: string): boolean;
export function canonicalMetadata(metadata: SeoMetadata, policy?: PublicSeoPolicy): SeoMetadata;
export function routeDecision(url: URL, metadata: SeoMetadata): {status:number;target?:string;location?:string;query?:boolean};
export function loadRouteMetadata(base: string,path: string,fetcher?:typeof fetch):Promise<SeoMetadata>;

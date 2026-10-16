import { usePublicBootstrap } from '../lib/seo/bootstrap';
import { useEffect, useState } from 'react';
import { getStorefrontContent } from '../lib/api/storefront';

let brandRequest: ReturnType<typeof getStorefrontContent> | undefined;

export default function BrandLogo({ size = 40, wordmark = false }: { size?: number; wordmark?: boolean }) {
  const initial = usePublicBootstrap()?.home.brand.logoUrl;
  const [url, setUrl] = useState<string | undefined>(initial ?? undefined);
  const [failed, setFailed] = useState(false);
  useEffect(() => {
    let active = true;
    brandRequest ??= getStorefrontContent();
    brandRequest.then(content => {
      if (active && /^https?:\/\//i.test(content.brand.logoUrl || '')) setUrl(content.brand.logoUrl!);
    }).catch(() => { brandRequest = undefined; });
    return () => { active = false; };
  }, []);

  const width = size * (wordmark ? 5 : 2.5);
  const height = size;
  return (
    <span className="inline-flex shrink-0 items-center justify-center overflow-hidden rounded" style={{ width, height }}>
      {url && !failed ? (
        <img src={url} alt="Sulocraft logo" width={width} height={height}
          style={{ width, height, transform: wordmark ? 'scale(1.5)' : undefined }}
          className="object-contain" onError={() => setFailed(true)} />
      ) : <span aria-label="Sulocraft logo" className="font-serif font-bold">S</span>}
    </span>
  );
}

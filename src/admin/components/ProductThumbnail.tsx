import { useState } from 'react';
import type { AdminProduct } from '../../lib/api/admin';

export default function ProductThumbnail({ product }: { product: Pick<AdminProduct, 'name' | 'primaryImage' | 'primaryImageUrl'> }) {
  const candidate = product.primaryImageUrl || product.primaryImage;
  const src = /^https?:\/\//i.test(candidate || '') ? candidate : undefined;
  const [failedSrc, setFailedSrc] = useState<string>();
  return <div className="grid h-16 w-16 shrink-0 place-items-center overflow-hidden rounded-lg bg-[#F5F0EA]">
    {src && failedSrc !== src ? <img src={src} alt={product.name} width={64} height={64} loading="lazy" style={{ width: 64, height: 64 }} className="object-contain" onError={() => setFailedSrc(src)} />
      : <span role="img" aria-label={`Photo unavailable for ${product.name}`} className="px-1 text-center text-[10px] text-[#6B5B4E]">No photo</span>}
  </div>;
}

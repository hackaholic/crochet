import { useEffect, useState } from 'react';
import { getOrderTracking } from '../../lib/api/tracking';
import type { OrderTracking } from '../../lib/api/orderTrackingTypes';
import ShipmentTracking from './ShipmentTracking';

export default function OrderTrackingPanel({ orderNumber, guestToken }: { orderNumber: string; guestToken?: string }) {
  const [data, setData] = useState<OrderTracking>();
  const [error, setError] = useState(false);
  const [retry, setRetry] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    setData(undefined); setError(false);
    getOrderTracking(orderNumber, controller.signal, guestToken)
      .then(value => { if (!controller.signal.aborted) setData(value); })
      .catch(() => { if (!controller.signal.aborted) setError(true); });
    return () => controller.abort();
  }, [orderNumber, guestToken, retry]);
  if (error) return <div role="alert" className="rounded-xl border border-[#EDE4D0] bg-white p-5 text-sm">Tracking is unavailable. Check your access or try again.<button className="ml-3 underline" onClick={() => setRetry(value => value + 1)}>Try again</button></div>;
  if (!data) return <p role="status" className="p-5 text-sm">Loading shipment details…</p>;
  return <ShipmentTracking tracking={data} />;
}

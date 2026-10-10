import type { OrderTracking } from '../../lib/api/orderTrackingTypes';

function readableStatus(value: string) { return value.replaceAll('_', ' ').toLowerCase(); }
function validDate(value: string | null) {
  if (!value) return null;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
}

/** Presentation only: never fetches or grants access to an order. */
export default function ShipmentTracking({ tracking }: { tracking: OrderTracking }) {
  const delivery = validDate(tracking.estimatedDelivery);
  return <section aria-label="Shipment tracking" className="min-w-0 space-y-5 rounded-2xl border border-[#EDE4D0] bg-white p-5 text-[#2C1810] [overflow-wrap:anywhere]">
    <header><h2 className="font-serif text-2xl">Shipment details</h2><p className="mt-1 text-sm">Order {tracking.orderNumber}</p></header>
    <dl className="grid gap-4 text-sm sm:grid-cols-2">
      <div><dt className="text-[#8B6B4A]">Order status</dt><dd className="capitalize">{readableStatus(tracking.status)}</dd></div>
      <div><dt className="text-[#8B6B4A]">Payment status</dt><dd className="capitalize">{readableStatus(tracking.paymentStatus)}</dd></div>
      <div><dt className="text-[#8B6B4A]">Courier</dt><dd>{tracking.courierName?.trim() || 'Not yet available'}</dd></div>
      <div><dt className="text-[#8B6B4A]">Tracking number</dt><dd>{tracking.trackingNumber?.trim() || 'Not yet available'}</dd></div>
      <div><dt className="text-[#8B6B4A]">Estimated delivery</dt><dd>{delivery ? <time dateTime={tracking.estimatedDelivery!}>{delivery.toLocaleDateString()}</time> : 'Not yet available'}</dd></div>
    </dl>
    <div><h3 className="font-serif text-xl">Order updates</h3>
      {tracking.timeline.length ? <ol className="mt-3 space-y-4">{tracking.timeline.map(event => {
        const date = validDate(event.timestamp);
        return <li key={event.id} className="border-l-2 border-[#EDE4D0] pl-4">
          <p className="font-semibold capitalize">{readableStatus(event.status)}</p>
          {date ? <time className="text-sm text-[#8B6B4A]" dateTime={event.timestamp}>{date.toLocaleString()}</time> : <p className="text-sm text-[#8B6B4A]">Time not recorded</p>}
          {event.note && <p className="mt-1 text-sm">{event.note}</p>}
        </li>;
      })}</ol> : <p className="mt-3 text-sm text-[#8B6B4A]">No order updates yet.</p>}
    </div>
  </section>;
}

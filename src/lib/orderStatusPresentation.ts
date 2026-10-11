/** Shared presentation tokens; business status comes from the API. */
export const ORDER_STATUS_CONFIG: Record<string, { label: string; bg: string; text: string; dot: string }> = {
  PENDING_PAYMENT: { label: 'Pending payment', bg: '#FFFBEB', text: '#92400E', dot: '#F59E0B' },
  PAID: { label: 'Paid', bg: '#DCFCE7', text: '#166534', dot: '#16A34A' },
  CONFIRMED: { label: 'Confirmed', bg: '#EDE9FE', text: '#5B21B6', dot: '#7C3AED' },
  PROCESSING: { label: 'Processing', bg: '#FFFBEB', text: '#92400E', dot: '#F59E0B' },
  READY_TO_SHIP: { label: 'Ready to Ship', bg: '#FDF4FF', text: '#6B21A8', dot: '#A855F7' },
  SHIPPED: { label: 'Shipped', bg: '#E0F2FE', text: '#0C4A6E', dot: '#0EA5E9' },
  OUT_FOR_DELIVERY: { label: 'Out for Delivery', bg: '#F0FDF4', text: '#14532D', dot: '#22C55E' },
  DELIVERED: { label: 'Delivered', bg: '#DCFCE7', text: '#166534', dot: '#16A34A' },
  CANCELLED: { label: 'Cancelled', bg: '#FEF2F2', text: '#991B1B', dot: '#EF4444' },
  REFUNDED: { label: 'Refunded', bg: '#F9FAFB', text: '#374151', dot: '#6B7280' },
};


export function orderStatusPresentation(status: string) {
  return ORDER_STATUS_CONFIG[status] ?? { label: status.replaceAll("_", " ").toLowerCase(), bg: "#F9FAFB", text: "#374151", dot: "#6B7280" };
}

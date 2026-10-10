export interface OrderMilestone {
  code: string;
  label: string;
  state: 'COMPLETED' | 'CURRENT' | 'PENDING';
  timestamp: string | null;
}

export interface OrderTerminalState {
  code: string;
  label: string;
  explanation: string;
  timestamp: string | null;
}

/** Read-only shipment payload from OrderTrackingOut. Access is enforced by the API. */
export interface OrderTracking {
  orderNumber: string;
  status: string;
  paymentStatus: string;
  trackingNumber: string | null;
  courierName: string | null;
  estimatedDelivery: string | null;
  timeline: { id: number; status: string; note: string | null; timestamp: string }[];
  milestones?: OrderMilestone[];
  terminalState?: OrderTerminalState | null;
}

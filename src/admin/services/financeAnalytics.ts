import { apiUrl } from '../../lib/api/client';
export interface ReportingRange { from: string; to: string }
export interface SalesRow { orderCount: number; unitsSold: number; grossSalesPaise: number; salesSharePct: number }
export interface CategorySales { effectiveRange: ReportingRange; totalGrossSalesPaise: number; categories: (SalesRow & { categoryId: number | null; categoryName: string })[] }
export interface DestinationSales { effectiveRange: ReportingRange; totalGrossSalesPaise: number; countries: (SalesRow & { countryCode: string; countryName: string; regions: (SalesRow & { state: string })[] })[] }
export interface ProductSales { effectiveRange: ReportingRange; rankingMetric: string; items: { productId: number | null; productName: string; sku: string | null; variantName: string | null; imageUrl: string | null; unitsSold: number; distinctOrders: number; productRevenuePaise: number }[] }
export interface Comparison { current: number; previous: number; growthPct: number | null; currentPaise?: number; previousPaise?: number }
export interface FinanceTrends { effectiveRange: ReportingRange; previousRange: ReportingRange; grossSales: Comparison; netRevenue: Comparison; orders: Comparison; averageOrderValue: Comparison; refunds: Comparison; operationalIndicators: { pendingPaymentCount: number; pendingPaymentTotalPaise: number; cancelledCount: number; refundedCount: number; fulfillmentStates: Record<string, number> } }
export type RankingMetric = 'revenue' | 'units';
export async function getFinanceAnalytics<T>(endpoint: 'categories' | 'destinations' | 'top-products' | 'trends', range: ReportingRange, options: { metric?: RankingMetric; limit?: number; sortBy?: string } = {}, signal?: AbortSignal): Promise<T> {
  const query = new URLSearchParams({ ...range });
  Object.entries(options).forEach(([key,value]) => { if (value !== undefined) query.set(key,String(value)); });
  const response = await fetch(apiUrl(`/admin/finance/${endpoint}?${query}`), { credentials: 'include', signal });
  if (!response.ok) throw new Error('Analytics unavailable');
  return response.json() as Promise<T>;
}

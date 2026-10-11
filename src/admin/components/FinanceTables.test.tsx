import { cleanup, fireEvent, render, screen, within } from '@testing-library/react';
import { afterEach, expect, it } from 'vitest';
import FinanceProductTable from './FinanceProductTable';
import FinanceTrendsTables from './FinanceTrendsTables';
afterEach(cleanup);
it('keeps product money in paise, escapes names and handles broken photos',()=>{
 const view=render(<FinanceProductTable data={{effectiveRange:{from:'a',to:'b'},rankingMetric:'revenue',items:[{productId:1,productName:'<script>bad</script>',sku:'R1',variantName:null,imageUrl:'https://images.sulocraft.com/product.webp',unitsSold:2,distinctOrders:1,productRevenuePaise:12345}]}}/>);
 expect(screen.getByRole('cell',{name:'₹123.45'})).toBeInTheDocument();
 expect(screen.getByRole('rowheader')).toHaveTextContent('<script>bad</script>');
 expect(view.container.querySelector('script')).toBeNull();
 fireEvent.error(screen.getByRole('img'));expect(screen.getByText('No photo')).toBeVisible();
 view.rerender(<FinanceProductTable data={{effectiveRange:{from:'a',to:'b'},rankingMetric:'revenue',items:[]}}/>);
 expect(screen.getByText('No qualifying sales in this period.')).toBeVisible();
});
it('preserves negative amounts, exact paise, missing growth baseline and separate operations',()=>{
 const comparison={current:-1,previous:0,currentPaise:-123,previousPaise:0,growthPct:null};
 render(<FinanceTrendsTables data={{effectiveRange:{from:'a',to:'b'},previousRange:{from:'c',to:'d'},grossSales:comparison,netRevenue:comparison,refunds:comparison,averageOrderValue:comparison,orders:{current:2,previous:1,growthPct:100},operationalIndicators:{pendingPaymentCount:3,pendingPaymentTotalPaise:80000,cancelledCount:0,refundedCount:1,fulfillmentStates:{SHIPPED:2}}}}/>);
 const tables=screen.getAllByRole('table');
 expect(within(tables[0]).getAllByText('₹-1.23')).toHaveLength(4);
 expect(within(tables[0]).getAllByText('No previous baseline')).toHaveLength(4);
 expect(within(tables[0]).getByText('+100.0%')).toBeInTheDocument();
 expect(within(tables[1]).getByRole('rowheader',{name:'SHIPPED'})).toBeInTheDocument();
 expect(screen.getByText('Pending payment amount: ₹800')).toBeVisible();
});

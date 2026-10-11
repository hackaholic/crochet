import {cleanup,fireEvent,render,screen,waitFor} from '@testing-library/react';
import {afterEach,it,expect,vi} from 'vitest';
import FinancePage from './FinancePage';
const api=vi.hoisted(()=>({getFinanceSummary:vi.fn(),getSalesChartFinance:vi.fn()}));
vi.mock('../services/api',()=>api);
vi.mock('../components/FinanceAnalytics',()=>({default:()=> <div>Finance analytics</div>}));
vi.mock('../components/RevenueChart',()=>({default:()=> <div>Revenue chart</div>}));
afterEach(()=>{cleanup();vi.resetAllMocks();});
it('sends the selected period and shared range to both widgets',async()=>{
 api.getFinanceSummary.mockResolvedValue(null);api.getSalesChartFinance.mockResolvedValue([]);
 const view=render(<FinancePage datePreset="prev_month"/>);
 await waitFor(()=>expect(api.getFinanceSummary).toHaveBeenCalled());
 expect(api.getSalesChartFinance).toHaveBeenCalledWith('prev_month',api.getFinanceSummary.mock.calls[0][1]);
 view.rerender(<FinancePage datePreset="yesterday"/>);
 await waitFor(()=>expect(api.getSalesChartFinance).toHaveBeenLastCalledWith('yesterday',expect.any(Object)));
});
it('shows a safe retry without reflecting raw server errors',async()=>{
 api.getFinanceSummary.mockRejectedValueOnce(new Error('private provider error')).mockResolvedValue(null);api.getSalesChartFinance.mockResolvedValue([]);
 render(<FinancePage datePreset="today"/>);
 const retry=await screen.findByRole('button',{name:'Retry finance'});
 expect(screen.queryByText(/private provider/)).not.toBeInTheDocument();
 fireEvent.click(retry);await waitFor(()=>expect(screen.queryByRole('alert')).not.toBeInTheDocument());
});
const summary={grossSales:100,netRevenue:100,gstCollected:0,refunds:0,discounts:0,shippingCollected:0,taxableSales:100,orderCount:1,refundCount:0,paymentFees:null,gatewayFeesAvailable:false,gatewayFeesNote:null};
it('renders authoritative reporting dates and unavailable fees',async()=>{
 api.getFinanceSummary.mockResolvedValue({...summary,effectiveRange:{from:'2026-10-01',to:'2026-10-11'}});api.getSalesChartFinance.mockResolvedValue([]);
 render(<FinancePage datePreset="this_month"/>);
 expect(await screen.findByLabelText('Reporting period')).toHaveTextContent('2026-10-01 to 2026-10-11 (IST, inclusive)');
 expect(screen.getByText('Not available')).toBeVisible();
});
it('keeps recorded zero fees distinct from missing fees and does not invent dates',async()=>{
 api.getFinanceSummary.mockResolvedValue({...summary,paymentFees:0,gatewayFeesAvailable:true});api.getSalesChartFinance.mockResolvedValue([]);
 render(<FinancePage datePreset="today"/>);
 await screen.findByText('Gateway Fees');
 expect(screen.queryByText('Not available')).not.toBeInTheDocument();
 expect(screen.queryByLabelText('Reporting period')).not.toBeInTheDocument();
});

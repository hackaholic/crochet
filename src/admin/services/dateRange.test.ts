import { expect,it,vi,afterEach } from 'vitest';
import { dateRange } from './dateRange';
import { getFinanceSummary,getSalesChartFinance } from './api';
afterEach(()=>{vi.unstubAllGlobals();vi.useRealTimers();});
it.each([
 ['today','2026-10-11','2026-10-11'],['yesterday','2026-10-10','2026-10-10'],['7d','2026-10-05','2026-10-11'],['30d','2026-09-12','2026-10-11'],['this_month','2026-10-01','2026-10-11'],['prev_month','2026-09-01','2026-09-30'],
] as const)('%s uses exact inclusive IST dates',(preset,from,to)=>expect(dateRange(preset,new Date('2026-10-10T20:00:00Z'))).toEqual({from,to}));
it('handles leap-year previous month',()=>expect(dateRange('prev_month',new Date('2024-03-01T00:00:00Z'))).toEqual({from:'2024-02-01',to:'2024-02-29'}));
it('uses the same supplied range for authenticated summary and chart',async()=>{
 const fetch=vi.fn().mockResolvedValue({ok:true,json:async()=>({buckets:[]})});vi.stubGlobal('fetch',fetch);
 const range={from:'2026-10-01',to:'2026-10-11'};
 await Promise.all([getFinanceSummary('this_month',range),getSalesChartFinance('this_month',range)]);
 for(const [url,options] of fetch.mock.calls){expect(url).toContain('from=2026-10-01&to=2026-10-11');expect(options.credentials).toBe('include');}
});
it('preserves the backend effective reporting range',async()=>{
 const range={from:'2026-10-01',to:'2026-10-11'};vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:true,json:async()=>({effectiveRange:range})}));
 expect((await getFinanceSummary('this_month')).effectiveRange).toEqual(range);
});

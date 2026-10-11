import {afterEach,it,expect,vi} from 'vitest';
import {getFinanceAnalytics} from './financeAnalytics';
vi.mock('../../lib/api/client',()=>({apiUrl:(path:string)=>path}));
afterEach(()=>vi.unstubAllGlobals());
it('sends authenticated bounded filters and abort signal with shared dates',async()=>{const fetch=vi.fn().mockResolvedValue({ok:true,json:async()=>({items:[]})});vi.stubGlobal('fetch',fetch);const signal=new AbortController().signal;await getFinanceAnalytics('top-products',{from:'2026-10-01',to:'2026-10-11'},{metric:'units',limit:20},signal);expect(fetch).toHaveBeenCalledWith('/admin/finance/top-products?from=2026-10-01&to=2026-10-11&metric=units&limit=20',{credentials:'include',signal});});
it('rejects access denial without exposing the response body',async()=>{vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:false,status:403,json:async()=>({detail:'private'})}));await expect(getFinanceAnalytics('trends',{from:'2026-10-01',to:'2026-10-11'})).rejects.toThrow('Analytics unavailable');});

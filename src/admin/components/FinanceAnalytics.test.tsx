import { cleanup,fireEvent,render,screen,waitFor,within } from '@testing-library/react';
import { afterEach,it,expect,vi } from 'vitest';
import FinanceAnalytics from './FinanceAnalytics';
const {get}=vi.hoisted(()=>({get:vi.fn()}));
vi.mock('../services/financeAnalytics',()=>({getFinanceAnalytics:get}));
const range={from:'2026-10-01',to:'2026-10-11'};
const sales={orderCount:1,unitsSold:2,grossSalesPaise:12345,salesSharePct:100};
const comparison={current:123,previous:0,currentPaise:12345,previousPaise:0,growthPct:null};
const fixtures: Record<string,unknown>={categories:{totalGrossSalesPaise:12345,categories:[{...sales,categoryName:'Flowers',categoryId:1}]},destinations:{totalGrossSalesPaise:12345,countries:[{...sales,countryCode:'IN',countryName:'India',regions:[{...sales,state:'Delhi'}]}]},'top-products':{items:[{productId:1,productName:'Rose',sku:'R1',variantName:null,imageUrl:null,unitsSold:2,distinctOrders:1,productRevenuePaise:12345}]},trends:{previousRange:{from:'2026-09-20',to:'2026-09-30'},grossSales:comparison,netRevenue:comparison,averageOrderValue:comparison,refunds:comparison,orders:{...comparison,current:1},operationalIndicators:{pendingPaymentCount:2,pendingPaymentTotalPaise:80000,cancelledCount:1,refundedCount:0,fulfillmentStates:{SHIPPED:1}}}};
afterEach(()=>{cleanup();vi.resetAllMocks();});
function ready(){get.mockImplementation((endpoint:string)=>Promise.resolve(fixtures[endpoint]));}
it('renders API money, destination regions, products and null baseline without estimates',async()=>{ready();render(<FinanceAnalytics range={range}/>);expect(await screen.findByText('Flowers')).toBeVisible();expect(screen.getByText('India')).toBeVisible();expect(screen.getByText('Delhi')).toBeInTheDocument();expect(screen.getByText('Rose')).toBeVisible();expect(screen.getByText('No photo')).toBeVisible();expect(screen.getAllByText(/No previous baseline/)).toHaveLength(5);expect(within(screen.getByRole('region',{name:'Sales by Category'})).getByRole('cell',{name:'₹123.45'})).toBeVisible();expect(get.mock.calls.every(call=>call[1]===range)).toBe(true);});
it('switches ranking and increases the bounded product batch',async()=>{ready();fixtures['top-products']={items:Array.from({length:10},(_,i)=>({productId:i,productName:`Product ${i}`,sku:null,variantName:null,imageUrl:null,unitsSold:1,distinctOrders:1,productRevenuePaise:100}))};render(<FinanceAnalytics range={range}/>);fireEvent.click(await screen.findByRole('button',{name:'Show more products'}));await waitFor(()=>expect(get).toHaveBeenCalledWith('top-products',range,expect.objectContaining({limit:20}),expect.any(AbortSignal)));fireEvent.change(screen.getByLabelText('Product ranking'),{target:{value:'units'}});await waitFor(()=>expect(get).toHaveBeenCalledWith('top-products',range,expect.objectContaining({metric:'units',limit:10}),expect.any(AbortSignal)));});
it('keeps partial failure isolated and retries without server details',async()=>{ready();get.mockImplementation((endpoint:string)=>endpoint==='categories'?Promise.reject(new Error('secret SQL')):Promise.resolve(fixtures[endpoint]));render(<FinanceAnalytics range={range}/>);await screen.findByRole('button',{name:'Retry sales by category'});expect(screen.getByText('India')).toBeVisible();expect(screen.queryByText(/secret SQL/)).not.toBeInTheDocument();ready();fireEvent.click(screen.getByRole('button',{name:'Retry sales by category'}));expect(await screen.findByText('Flowers')).toBeVisible();});
it('ignores late previous-period data and handles empty results',async()=>{let finish:(v:unknown)=>void=()=>{};get.mockImplementation((endpoint:string,r:typeof range)=>endpoint==='categories'&&r.from===range.from?new Promise(resolve=>{finish=resolve;}):Promise.resolve(endpoint==='categories'?{totalGrossSalesPaise:0,categories:[]}:fixtures[endpoint]));const view=render(<FinanceAnalytics range={range}/>);view.rerender(<FinanceAnalytics range={{from:'2026-09-01',to:'2026-09-30'}}/>);await screen.findByText('No qualifying sales in this period.');finish(fixtures.categories);await waitFor(()=>expect(screen.queryByText('Flowers')).not.toBeInTheDocument());});
it('renders valid ISO country flag and neutral globe fallback for unknown country',async()=>{
  const customFixtures = {
    ...fixtures,
    destinations: {
      totalGrossSalesPaise: 25000,
      countries: [
        { ...sales, countryCode: 'IN', countryName: 'India', regions: [] },
        { ...sales, countryCode: 'UNKNOWN', countryName: 'UNKNOWN', regions: [] },
      ],
    },
  };
  get.mockImplementation((endpoint: string) => Promise.resolve(customFixtures[endpoint as keyof typeof customFixtures]));
  render(<FinanceAnalytics range={range}/>);
  expect(await screen.findByTestId('country-flag-emoji')).toHaveTextContent('🇮🇳');
  expect(screen.getByTestId('country-flag-fallback')).toBeInTheDocument();
  expect(screen.getByText('India')).toBeVisible();
  expect(screen.getByText('Unknown destination')).toBeVisible();
});

it('opens product and supported operational cells, preserving range and leaving analytics read-only',async()=>{
  fixtures['top-products']={items:[{productId:1,productName:'Rose',sku:'R1',variantName:null,imageUrl:null,unitsSold:2,distinctOrders:1,productRevenuePaise:12345}]}; ready(); const product=vi.fn(),orders=vi.fn();
  render(<FinanceAnalytics range={range} onSelectProduct={product} onFilterOrders={orders}/>);
  const products=await screen.findByRole('region',{name:'Top-selling Products'});
  const productButton=await within(products).findByRole('button',{name:/Rose/});
  fireEvent.click(productButton);expect(product).toHaveBeenCalledWith(1);
  for(const [label,status] of [['Pending payment','PENDING_PAYMENT'],['Cancelled','CANCELLED'],['Refunded','REFUNDED'],['SHIPPED','SHIPPED']]){
    fireEvent.click(await screen.findByRole('button',{name:label}));
    expect(orders).toHaveBeenLastCalledWith(status,range);
  }
  expect(within(screen.getByRole('region',{name:'Sales by Destination'})).queryByRole('button')).not.toBeInTheDocument();
  expect(screen.getAllByText('Gross product sales').every(e=>e.closest('button')===null)).toBe(true);
  fireEvent.click(productButton.closest('tr')!.querySelector('td')!);expect(product).toHaveBeenCalledTimes(1);
});

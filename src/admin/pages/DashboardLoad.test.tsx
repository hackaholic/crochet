import {cleanup,fireEvent,render,screen,waitFor} from '@testing-library/react';
import {afterEach,beforeEach,expect,it,vi} from 'vitest';
import DashboardPage from './DashboardPage';
import * as api from '../services/api';
vi.mock('../services/api',()=>({getDashboardSummary:vi.fn(),getOrderStatusCountsForPeriod:vi.fn(),getAttentionItems:vi.fn(),getActivityFeed:vi.fn(),getInventoryAlerts:vi.fn(),getSalesChart:vi.fn(),getOrders:vi.fn()}));
vi.mock('../components/RevenueChart',()=>({default:()=> <div>Chart</div>}));
const summary={period:'QA period',totalSales:100,totalRevenue:250,netRevenue:200,orders:1,avgOrderValue:250,refunds:50,statusCounts:{},comparison:null};
const props={datePreset:'30d' as const,onNavigate:vi.fn(),onSelectOrder:vi.fn(),onFilterOrders:vi.fn()};
beforeEach(()=>{vi.resetAllMocks();vi.mocked(api.getDashboardSummary).mockResolvedValue(summary);vi.mocked(api.getOrderStatusCountsForPeriod).mockResolvedValue([]);vi.mocked(api.getAttentionItems).mockResolvedValue([]);vi.mocked(api.getActivityFeed).mockResolvedValue([]);vi.mocked(api.getInventoryAlerts).mockResolvedValue([]);vi.mocked(api.getSalesChart).mockResolvedValue([]);vi.mocked(api.getOrders).mockResolvedValue({orders:[],total:0,page:1,pageSize:10});});afterEach(cleanup);
it('renders API metrics and a genuine empty recent-order state',async()=>{render(<DashboardPage {...props}/>);await screen.findByText('₹200');expect(screen.getByText('Total Sales')).toBeInTheDocument();expect(screen.getByText('No orders yet')).toBeInTheDocument();});
it('hides unavailable metrics on API failure and retries safely',async()=>{
 vi.mocked(api.getDashboardSummary).mockRejectedValueOnce(new Error('private data'));render(<DashboardPage {...props}/>);expect(await screen.findByRole('alert')).toHaveTextContent('Dashboard could not be loaded');expect(screen.queryByText('₹200')).not.toBeInTheDocument();expect(screen.queryByText(/private data/)).not.toBeInTheDocument();fireEvent.click(screen.getByRole('button',{name:'Retry dashboard'}));await screen.findByText('₹200');
});
it('ignores an old response after the reporting period changes',async()=>{
 let resolve!:(v:typeof summary)=>void;vi.mocked(api.getDashboardSummary).mockReturnValueOnce(new Promise(r=>{resolve=r;}));const {rerender}=render(<DashboardPage {...props}/>);rerender(<DashboardPage {...props} datePreset="7d"/>);await screen.findByText('₹200');resolve({...summary,netRevenue:98765});await waitFor(()=>expect(screen.queryByText('₹98,765')).not.toBeInTheDocument());
});

it('recent order opens preview without page navigation, and customer opens its own popup',async()=>{
 vi.mocked(api.getOrders).mockResolvedValue({orders:[{id:'42',orderNumber:'ORDER-42',customer:{name:'QA',email:''},total:100,orderStatus:'CONFIRMED',date:'2026-10-11'} as any],total:1,page:1,pageSize:10});
 render(<DashboardPage {...props}/>);
 fireEvent.click(await screen.findByRole('button',{name:'View order ORDER-42'}));
 expect(props.onSelectOrder).toHaveBeenCalledWith('42');expect(props.onNavigate).not.toHaveBeenCalled();
 fireEvent.click(screen.getByRole('button',{name:'View customer QA'}));expect(screen.getByRole('dialog',{name:'Customer profile'})).toBeInTheDocument();
 expect(screen.getByText('Recent Orders')).toBeInTheDocument();
});

import {afterEach,it,expect,vi} from 'vitest';
import {cleanup,render,screen,fireEvent,waitFor} from '@testing-library/react';
import OrdersPage from './OrdersPage';
import type {Order} from '../types';
const get=vi.hoisted(()=>vi.fn());vi.mock('../services/api',()=>({getOrders:get}));
afterEach(()=>{cleanup();vi.resetAllMocks();});
const order=(id:string):Order=>({id,orderNumber:`Order-${id}`,date:'2026-10-11',customer:{name:'Test Customer',email:'test@example.com',phone:''},shippingAddress:{line1:'',city:'',state:'',pinCode:'',country:'IN'},items:[],subtotal:100,shipping:0,discount:0,gst:0,total:100,paymentStatus:'PAID',paymentMethod:'ONLINE',orderStatus:'CONFIRMED',timeline:[]});
it('shows safe retry and never presents an error as an empty result',async()=>{get.mockRejectedValueOnce(new Error('secret SQL')).mockResolvedValue({orders:[],total:0});render(<OrdersPage onSelectOrder={()=>{}}/>);fireEvent.click(await screen.findByRole('button',{name:'Retry orders'}));expect(screen.queryByText(/secret SQL/)).not.toBeInTheDocument();await screen.findByText('No orders found');expect(screen.queryByRole('alert')).not.toBeInTheDocument();});
it('ignores a late previous-filter response',async()=>{let finish:(value:unknown)=>void=()=>{};get.mockImplementationOnce(()=>new Promise(resolve=>{finish=resolve;})).mockResolvedValue({orders:[order('current')],total:1});render(<OrdersPage onSelectOrder={()=>{}}/>);fireEvent.click(screen.getByRole('button',{name:'Shipped'}));await screen.findByText('Order-current');finish({orders:[order('stale')],total:1});await waitFor(()=>expect(screen.queryByText('Order-stale')).not.toBeInTheDocument());expect(get).toHaveBeenLastCalledWith(expect.objectContaining({status:'SHIPPED',page:1}));});
it('forwards sorting/search and retains order selection',async()=>{get.mockResolvedValue({orders:[order('selected')],total:1});const select=vi.fn();render(<OrdersPage onSelectOrder={select}/>);fireEvent.click(await screen.findByText('Order-selected'));expect(select).toHaveBeenCalledWith('selected');fireEvent.change(screen.getByLabelText('Sort orders'),{target:{value:'total-asc'}});fireEvent.change(screen.getByPlaceholderText('Order number, customer, email, SKU…'),{target:{value:' R1 '}});await waitFor(()=>expect(get).toHaveBeenLastCalledWith(expect.objectContaining({search:'R1',sortBy:'total',sortDir:'asc',page:1,pageSize:20})));});

it('requests pipeline status and dates on every server page and preserves them when switching status',async()=>{
  get.mockResolvedValue({orders:[order('selected')],total:41});
  render(<OrdersPage onSelectOrder={()=>{}} initialStatus="CONFIRMED" reportingRange={{from:'2026-10-01',to:'2026-10-11'}}/>);
  await screen.findByText('Order-selected');
  expect(get).toHaveBeenLastCalledWith(expect.objectContaining({status:'CONFIRMED',dateFrom:'2026-10-01',dateTo:'2026-10-11',page:1,pageSize:20}));
  fireEvent.click(screen.getByRole('button',{name:'→'}));
  await waitFor(()=>expect(get).toHaveBeenLastCalledWith(expect.objectContaining({status:'CONFIRMED',dateFrom:'2026-10-01',dateTo:'2026-10-11',page:2})));
  fireEvent.click(screen.getByRole('button',{name:'Paid'}));
  await waitFor(()=>expect(get).toHaveBeenLastCalledWith(expect.objectContaining({status:'PAID',page:1,dateFrom:'2026-10-01'})));
});

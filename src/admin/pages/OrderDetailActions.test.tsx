import {cleanup,fireEvent,render,screen,waitFor,within} from '@testing-library/react';
import {afterEach,beforeEach,expect,it,vi} from 'vitest';
import OrderDetailPage from './OrderDetailPage';
import * as api from '../services/api';
import type {Order} from '../types';
vi.mock('../services/api',()=>({getOrder:vi.fn(),updateOrderStatus:vi.fn()}));
const order:Order={id:'42',orderNumber:'ORDER-QA',date:'2026-10-01',customer:{name:'QA customer',email:'qa@example.com',phone:'9999999999'},shippingAddress:{line1:'QA address',city:'Delhi',state:'Delhi',pinCode:'110001',country:'IN'},items:[{id:'1',productName:'QA bunny',sku:'QA-SKU',quantity:1,unitPrice:250,discount:0,finalAmount:250}],subtotal:250,shipping:0,discount:0,gst:0,total:250,paymentStatus:'PAID',paymentMethod:'MOCK',orderStatus:'PAID',timeline:[{id:'1',timestamp:'2026-10-01',status:'PAID',label:'Order paid',actor:'QA'}]};
beforeEach(()=>{vi.resetAllMocks();vi.mocked(api.getOrder).mockResolvedValue(order);});afterEach(cleanup);
it('renders customer/items/timeline and cancels status confirmation without mutation',async()=>{
 render(<OrderDetailPage orderId="42" onBack={()=>{}}/>);await screen.findByText('QA bunny');expect(screen.getByText('QA address')).toBeInTheDocument();expect(screen.getByText('Order paid')).toBeInTheDocument();fireEvent.click(screen.getByRole('button',{name:'Confirm Order'}));fireEvent.click(screen.getByRole('button',{name:'Cancel'}));expect(api.updateOrderStatus).not.toHaveBeenCalled();
});
it('keeps details after a denied status update and renders authoritative response on retry',async()=>{
 vi.mocked(api.updateOrderStatus).mockRejectedValueOnce(new Error('403 internal')).mockResolvedValue({...order,orderStatus:'CONFIRMED',timeline:[...order.timeline,{id:'2',status:'CONFIRMED',timestamp:'2026-10-02',label:'Order confirmed by API',actor:'QA'}]});render(<OrderDetailPage orderId="42" onBack={()=>{}}/>);
 fireEvent.click(await screen.findByRole('button',{name:'Confirm Order'}));fireEvent.click(within(screen.getByRole('dialog')).getByRole('button',{name:'Confirm Order'}));expect(await screen.findByRole('alert')).toHaveTextContent('Order could not be updated');expect(screen.getByText('QA bunny')).toBeInTheDocument();
 fireEvent.click(within(screen.getByRole('dialog')).getByRole('button',{name:'Confirm Order'}));await screen.findByText('Order confirmed by API');expect(api.updateOrderStatus).toHaveBeenLastCalledWith('42','CONFIRMED',undefined);
});
it('validates tracking and persists trimmed input instead of only closing the popup',async()=>{
 vi.mocked(api.updateOrderStatus).mockRejectedValueOnce(new Error('offline')).mockResolvedValue({...order,shipment:{id:'shipment',courier:'QA courier',trackingId:'TRACK-42',createdDate:'2026-10-01',currentState:'PAID',history:[]}});render(<OrderDetailPage orderId="42" onBack={()=>{}}/>);fireEvent.click(await screen.findByRole('button',{name:'+ Add Tracking'}));expect(screen.getByRole('button',{name:'Save'})).toBeDisabled();fireEvent.change(screen.getByRole('textbox',{name:'Tracking ID'}),{target:{value:' TRACK-42 '}});fireEvent.click(screen.getByRole('button',{name:'Save'}));await screen.findByRole('alert');expect(screen.getByRole('textbox',{name:'Tracking ID'})).toHaveValue(' TRACK-42 ');fireEvent.click(screen.getByRole('button',{name:'Save'}));await waitFor(()=>expect(screen.queryByRole('textbox',{name:'Tracking ID'})).not.toBeInTheDocument());expect(api.updateOrderStatus).toHaveBeenLastCalledWith('42','PAID',undefined,'TRACK-42');expect(screen.getByText('TRACK-42')).toBeInTheDocument();
});

it('does not advertise unimplemented private-note or shipment creation as functional',async()=>{render(<OrderDetailPage orderId="42" onBack={()=>{}}/>);await screen.findByText('QA bunny');expect(screen.getByRole('button',{name:'Create Shipment'})).toBeDisabled();expect(screen.getByRole('button',{name:'Save Note'})).toBeDisabled();expect(screen.getByRole('textbox',{name:'Internal note'})).toBeDisabled();});

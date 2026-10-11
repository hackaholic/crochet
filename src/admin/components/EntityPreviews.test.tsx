import {cleanup,fireEvent,render,screen,waitFor,within} from '@testing-library/react';
import {afterEach,expect,it,vi} from 'vitest';
import AdminPreviewDialog from './AdminPreviewDialog';
import ProductPreview from './ProductPreview';
import OrderPreview from './OrderPreview';
import {getOrder} from '../services/api';
vi.mock('../services/api',()=>({getOrder:vi.fn()}));
import CustomerPopup from './CustomerPopup';
import * as catalogue from '../services/catalogue';
import * as customers from '../services/customers';
vi.mock('../services/catalogue',()=>({getProduct:vi.fn()}));
vi.mock('../services/customers',()=>({getCustomers:vi.fn(),getCustomer:vi.fn(),getCustomerOrders:vi.fn()}));
afterEach(()=>{cleanup();vi.resetAllMocks();});
it('closes on Escape and restores trigger focus without losing surrounding input',()=>{
 const close=vi.fn();const trigger=document.createElement('button');document.body.append(trigger);trigger.focus();
 const view=render(<AdminPreviewDialog title="Preview" onClose={close}><input aria-label="Example"/></AdminPreviewDialog>);
 const dialog=screen.getByRole('dialog');expect(dialog).toHaveAttribute('open');
 fireEvent(dialog,new Event('cancel',{bubbles:false,cancelable:true}));expect(close).toHaveBeenCalledOnce();
 view.unmount();expect(document.activeElement).toBe(trigger);trigger.remove();
});
it('fetches product by ID and exposes editor plus encoded storefront route',async()=>{
 vi.mocked(catalogue.getProduct).mockResolvedValue({id:42,name:'Bunny',slug:'pink bunny',description:'Cotton',minPrice:100,status:'ACTIVE',categoryNames:['Toys'],primaryImage:'',variants:[]} as any);
 const edit=vi.fn();render(<ProductPreview id={42} onEdit={edit}/>);
 fireEvent.click(await screen.findByRole('button',{name:'Edit product'}));expect(edit).toHaveBeenCalledWith(42);
 expect(screen.getByRole('link',{name:'View storefront product'})).toHaveAttribute('href','/products/pink%20bunny');
});
it('does not guess customer identity from fuzzy matches or expose unrelated profile',async()=>{
 vi.mocked(customers.getCustomers).mockResolvedValue({items:[{id:3,email:'other@example.com'} as any],page:1,pageSize:20,total:1});
 render(<CustomerPopup customer={{name:'Guest',email:'guest@example.com'}} onClose={()=>{}} onSelectOrder={()=>{}}/>);
 expect(await screen.findByText(/No uniquely linked/)).toBeVisible();expect(customers.getCustomer).not.toHaveBeenCalled();
});
it('loads exact customer and allows safe retry without leaked service error',async()=>{
 vi.mocked(customers.getCustomers).mockRejectedValueOnce(new Error('secret')).mockResolvedValue({items:[],page:1,pageSize:20,total:0});
 render(<CustomerPopup customer={{email:'guest@example.com'}} onClose={()=>{}} onSelectOrder={()=>{}}/>);
 const dialog=screen.getByRole('dialog');expect(await within(dialog).findByRole('alert')).not.toHaveTextContent('secret');
 fireEvent.click(screen.getByRole('button',{name:'Retry customer'}));await waitFor(()=>expect(screen.getByText(/No uniquely linked/)).toBeVisible());
});

it('order summary opens full order only through its explicit action',async()=>{
 vi.mocked(getOrder).mockResolvedValue({id:'42',orderNumber:'ORDER-42',customer:{name:'QA',email:'qa@example.com'},orderStatus:'CONFIRMED',paymentStatus:'PAID',total:100,items:[],shippingAddress:{line1:'Street',city:'City',state:'State',pinCode:'123456'}} as any);
 const view=vi.fn();render(<OrderPreview id="42" onView={view}/>);
 expect(await screen.findByText('ORDER-42')).toBeVisible();expect(view).not.toHaveBeenCalled();
 fireEvent.click(screen.getByRole('button',{name:'View full order'}));expect(view).toHaveBeenCalledWith('42');
});
it('retains the same dialog and close control as asynchronous content changes',()=>{
 const close=vi.fn();const view=render(<AdminPreviewDialog title="Preview" onClose={close}><p role="status">Loading…</p></AdminPreviewDialog>);
 const frame=screen.getByRole('dialog');const button=screen.getByRole('button',{name:'Close Preview'});button.focus();
 view.rerender(<AdminPreviewDialog title="Preview" onClose={close}><section><h3>Loaded profile</h3><p>Address details</p></section></AdminPreviewDialog>);
 expect(screen.getByRole('dialog')).toBe(frame);expect(document.activeElement).toBe(button);
 expect(screen.queryByRole('status')).not.toBeInTheDocument();
 fireEvent.click(button);expect(close).toHaveBeenCalledOnce();
});

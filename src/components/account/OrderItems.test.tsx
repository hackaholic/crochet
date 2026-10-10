import {cleanup,render,screen} from '@testing-library/react';
import {afterEach,expect,it,vi} from 'vitest';
import OrderItems from './OrderItems';
const order=vi.hoisted(()=>vi.fn());
vi.mock('../../lib/api/orders',()=>({accountApi:{order}}));
afterEach(()=>{cleanup();vi.resetAllMocks();});
it('loads the selected order items from the authorized API',async()=>{order.mockResolvedValue({items:[{id:1,productName:'Crochet Bunny',quantity:2,lineTotal:900}]});render(<OrderItems orderNumber="TEST-1"/>);expect(await screen.findByText('Crochet Bunny × 2')).toBeVisible();expect(order).toHaveBeenCalledWith('TEST-1');});
it('shows safe error state when access or loading fails',async()=>{order.mockRejectedValue(new Error('404'));render(<OrderItems orderNumber="OTHER"/>);expect(await screen.findByRole('alert')).toHaveTextContent('could not be loaded');});
it('retries a failed load without losing the selected order',async()=>{order.mockRejectedValueOnce(new Error('503')).mockResolvedValueOnce({items:[{id:2,productName:'Retry Bunny',quantity:1,lineTotal:450}]});render(<OrderItems orderNumber="RETRY"/>);const button=await screen.findByRole('button',{name:'Retry order items'});button.click();expect(await screen.findByText('Retry Bunny × 1')).toBeVisible();expect(order).toHaveBeenCalledTimes(2);});

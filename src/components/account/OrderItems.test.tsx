import {cleanup,render,screen,fireEvent} from '@testing-library/react';
import {afterEach,expect,it,vi} from 'vitest';
import { MemoryRouter } from 'react-router';
import OrderItems from './OrderItems';
const order=vi.hoisted(()=>vi.fn());
vi.mock('../../lib/api/orders',()=>({accountApi:{order}}));
afterEach(()=>{cleanup();vi.resetAllMocks();});
it('loads the selected order items from the authorized API',async()=>{order.mockResolvedValue({items:[{id:1,productName:'Crochet Bunny',quantity:2,lineTotal:900}]});render(<OrderItems orderNumber="TEST-1"/>);expect(await screen.findByText('Crochet Bunny')).toBeVisible();expect(order).toHaveBeenCalledWith('TEST-1');});
it('shows safe error state when access or loading fails',async()=>{order.mockRejectedValue(new Error('404'));render(<OrderItems orderNumber="OTHER"/>);expect(await screen.findByRole('alert')).toHaveTextContent('could not be loaded');});
it('retries a failed load without losing the selected order',async()=>{order.mockRejectedValueOnce(new Error('503')).mockResolvedValueOnce({items:[{id:2,productName:'Retry Bunny',quantity:1,lineTotal:450}]});render(<OrderItems orderNumber="RETRY"/>);const button=await screen.findByRole('button',{name:'Retry order items'});button.click();expect(await screen.findByText('Retry Bunny')).toBeVisible();expect(order).toHaveBeenCalledTimes(2);});

it('renders linked product snapshot with thumbnail, quantity and total',async()=>{order.mockResolvedValue({items:[{id:1,productName:'Sunflower Bouquet',productSlug:'sunflower-bouquet',productImage:'https://images.example/sunflower.webp',quantity:2,lineTotal:1000}]});render(<MemoryRouter><OrderItems orderNumber="demo"/></MemoryRouter>);expect(await screen.findByRole('link',{name:/Sunflower Bouquet/})).toHaveAttribute('href','/products/sunflower-bouquet');expect(screen.getByRole('columnheader',{name:'Quantity'})).toBeVisible();expect(screen.getByRole('cell',{name:'2'})).toBeVisible();expect(screen.getByRole('cell',{name:'₹1,000'})).toBeVisible();fireEvent.error(screen.getByRole('img'));expect(screen.getByText('No photo')).toBeVisible();});

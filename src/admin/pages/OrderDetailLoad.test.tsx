import {cleanup,render,screen,fireEvent} from '@testing-library/react';
import {afterEach,it,expect,vi} from 'vitest';
import OrderDetailPage from './OrderDetailPage';
const get=vi.hoisted(()=>vi.fn());vi.mock('../services/api',()=>({getOrder:get}));
afterEach(()=>{cleanup();vi.resetAllMocks();});
it('shows a safe denial/failure state with working Back instead of endless loading',async()=>{get.mockRejectedValue(new Error('403 private backend detail'));const back=vi.fn();render(<OrderDetailPage orderId="denied" onBack={back}/>);expect(await screen.findByRole('alert')).toHaveTextContent('Order unavailable');expect(screen.queryByText(/private backend/)).not.toBeInTheDocument();fireEvent.click(screen.getByRole('button',{name:'← Back to Orders'}));expect(back).toHaveBeenCalledOnce();});
it('shows the existing missing-order state',async()=>{get.mockResolvedValue(null);render(<OrderDetailPage orderId="deleted" onBack={()=>{}}/>);await screen.findByText('Order not found');expect(screen.queryByRole('alert')).not.toBeInTheDocument();});

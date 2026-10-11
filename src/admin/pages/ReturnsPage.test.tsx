import {cleanup,fireEvent,render,screen,waitFor} from '@testing-library/react';
import {afterEach,beforeEach,expect,it,vi} from 'vitest';
import ReturnsPage from './ReturnsPage';
import * as api from '../services/api';
vi.mock('../components/CustomerPopup',()=>({default:({customer,onClose}:any)=><div role="dialog"><span>{customer.email}</span><button onClick={onClose}>Close customer</button></div>}));
vi.mock('../services/api',()=>({getReturns:vi.fn(),approveReturn:vi.fn(),rejectReturn:vi.fn(),processReturnRefund:vi.fn()}));
const item={id:'RET-QA',orderId:'42',orderNumber:'ORDER-QA',customer:{name:'QA customer',email:'qa@example.com'},productName:'Bunny',reason:'Damaged',requestedDate:'2026-10-01',status:'REQUESTED' as const,refundAmount:250};
beforeEach(()=>{vi.resetAllMocks();vi.mocked(api.getReturns).mockResolvedValue([item]);});afterEach(cleanup);
it('renders persisted return, links exact order and filters without invented rows',async()=>{
 const select=vi.fn();render(<ReturnsPage onSelectOrder={select}/>);fireEvent.click(await screen.findByRole('button',{name:'ORDER-QA'}));expect(select).toHaveBeenCalledWith('42');
 fireEvent.click(screen.getByRole('button',{name:'Refunded'}));expect(screen.getByText('No returns')).toBeInTheDocument();expect(screen.queryByText('RET-QA')).not.toBeInTheDocument();
});
it('shows safe load denial and retries instead of hanging',async()=>{
 vi.mocked(api.getReturns).mockRejectedValueOnce(new Error('403 secret detail'));render(<ReturnsPage/>);
 expect(await screen.findByRole('alert')).toHaveTextContent('Returns could not be loaded');expect(screen.queryByText(/secret detail/)).not.toBeInTheDocument();
 fireEvent.click(screen.getByRole('button',{name:'Retry returns'}));expect(await screen.findByText('RET-QA')).toBeInTheDocument();
});
it('retains status on denied mutation and permits a successful retry',async()=>{
 vi.mocked(api.approveReturn).mockRejectedValueOnce(new Error('403')).mockResolvedValue(undefined);render(<ReturnsPage/>);
 fireEvent.click(await screen.findByRole('button',{name:'Approve'}));fireEvent.click(screen.getByRole('button',{name:'Yes, Approve'}));
 expect(await screen.findByRole('alert')).toHaveTextContent('status is unchanged');expect(screen.getByText('Requested',{selector:'span'})).toBeInTheDocument();
 fireEvent.click(screen.getByRole('button',{name:'Yes, Approve'}));await screen.findByText('Awaiting returned items');expect(api.approveReturn).toHaveBeenCalledTimes(2);expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
});
it('prevents duplicate submission while pending and does not mutate on Cancel',async()=>{
 let finish!:()=>void;vi.mocked(api.rejectReturn).mockReturnValue(new Promise<void>(resolve=>{finish=resolve;}));render(<ReturnsPage/>);
 fireEvent.click(await screen.findByRole('button',{name:'Reject'}));fireEvent.click(screen.getByRole('button',{name:'Cancel'}));expect(api.rejectReturn).not.toHaveBeenCalled();
 fireEvent.click(screen.getByRole('button',{name:'Reject'}));fireEvent.click(screen.getByRole('button',{name:'Yes, Reject'}));expect(screen.getByRole('button',{name:'Saving…'})).toBeDisabled();expect(screen.getByRole('button',{name:'Cancel'})).toBeDisabled();
 finish();await waitFor(()=>expect(screen.queryByRole('dialog')).not.toBeInTheDocument());expect(api.rejectReturn).toHaveBeenCalledOnce();
});

it('customer cell opens popup without leaving returns or mutating status',async()=>{
 const select=vi.fn();render(<ReturnsPage onSelectOrder={select}/>);
 fireEvent.click(await screen.findByRole('button',{name:'View customer QA customer'}));
 expect(screen.getByRole('dialog')).toBeInTheDocument();expect(screen.getByText('RET-QA')).toBeInTheDocument();
 expect(select).not.toHaveBeenCalled();expect(api.approveReturn).not.toHaveBeenCalled();
 fireEvent.click(screen.getByRole('button',{name:'Close customer'}));expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
});

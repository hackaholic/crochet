import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import AdminApp from './AdminApp';
vi.mock('./layout/AdminLayout',()=>({default:({children,onNavigate}:any)=><div><button onClick={()=>onNavigate('orders')}>Sidebar orders</button>{children}</div>}));
vi.mock('./pages/DashboardPage',()=>({default:({onFilterOrders}:any)=><button onClick={()=>onFilterOrders('CONFIRMED')}>Pipeline confirmed</button>}));
vi.mock('./pages/OrdersPage',()=>({default:({initialStatus,reportingRange}:any)=><div data-testid="selection">{initialStatus??'ALL'}|{reportingRange?.from??'unbounded'}|{reportingRange?.to??'unbounded'}</div>}));
afterEach(()=>{cleanup();vi.useRealTimers();});
it('passes pipeline status and exact dashboard date range, then resets through normal Orders navigation',()=>{
  vi.useFakeTimers();vi.setSystemTime(new Date('2026-10-11T06:00:00Z'));
  render(<AdminApp onExitAdmin={()=>{}}/>);
  fireEvent.click(screen.getByRole('button',{name:'Pipeline confirmed'}));
  expect(screen.getByTestId('selection')).toHaveTextContent('CONFIRMED|2026-09-12|2026-10-11');
  fireEvent.click(screen.getByRole('button',{name:'Sidebar orders'}));
  expect(screen.getByTestId('selection')).toHaveTextContent('ALL|unbounded|unbounded');
});

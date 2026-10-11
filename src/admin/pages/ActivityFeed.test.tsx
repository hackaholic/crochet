import {cleanup,fireEvent,render,screen} from '@testing-library/react';
import {afterEach,it,expect,vi} from 'vitest';
import {ActivityFeed} from './DashboardPage';
import type {ActivityItem} from '../types';
afterEach(cleanup);
const item:ActivityItem={id:'event',type:'order_updated',orderId:'internal-id',orderNumber:'PUBLIC-1',message:'Status changed',timestamp:'2026-10-11T00:00:00Z'};
it('opens the exact source order through a native keyboard-accessible button',()=>{const view=vi.fn();render(<ActivityFeed items={[item]} onView={view}/>);const button=screen.getByRole('button',{name:'View order PUBLIC-1'});expect(button).toHaveAttribute('type','button');button.focus();expect(button).toHaveFocus();fireEvent.click(button);expect(view).toHaveBeenCalledWith('internal-id');});
it('keeps missing-ID and non-order references as escaped text',()=>{const view=vi.fn();render(<ActivityFeed items={[{...item,orderId:undefined,orderNumber:'<img src=x onerror=alert(1)>'},{...item,id:'stock',type:'low_stock'}]} onView={view}/>);expect(screen.queryByRole('button')).not.toBeInTheDocument();expect(screen.getByText('<img src=x onerror=alert(1)>')).toBeInTheDocument();expect(document.querySelector('img')).toBeNull();expect(view).not.toHaveBeenCalled();});

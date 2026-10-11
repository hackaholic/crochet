import {render,screen,fireEvent,waitFor,cleanup} from '@testing-library/react';
import {it,expect,vi,afterEach} from 'vitest';
import AdminSignOut from './AdminSignOut';
afterEach(cleanup);
it('signs out through the shared handler and prevents repeated requests',async()=>{const logout=vi.fn().mockResolvedValue(undefined);render(<AdminSignOut onLogout={logout} collapsed/>);fireEvent.click(screen.getByRole('button',{name:'Sign out'}));await waitFor(()=>expect(logout).toHaveBeenCalledTimes(1));expect(screen.getByRole('button',{name:'Signing out…'})).toBeDisabled();});
it('allows retry after logout fails',async()=>{const logout=vi.fn().mockRejectedValue(new Error());render(<AdminSignOut onLogout={logout} collapsed={false}/>);fireEvent.click(screen.getByRole('button',{name:'Sign out'}));expect(await screen.findByRole('alert')).toHaveTextContent('Could not sign out');expect(screen.getByRole('button',{name:'Sign out'})).toBeEnabled();});

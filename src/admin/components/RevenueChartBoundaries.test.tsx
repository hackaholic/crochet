import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, it } from 'vitest';
import RevenueChart from './RevenueChart';
afterEach(cleanup);
const point=(revenue:number)=>({label:'Day',revenue,orders:1,avgOrderValue:revenue});
it.each([[100,-50],[-100,-50],[0,0]])('contains plotted values %s and %s', (a,b)=>{
 const view=render(<RevenueChart data={[point(a),point(b)]}/>);
 const coordinates=view.container.querySelector('polyline')!.getAttribute('points')!.split(' ').map(p=>p.split(',').map(Number));
 for(const [x,y] of coordinates){expect(Number.isFinite(x)).toBe(true);expect(y).toBeGreaterThanOrEqual(12);expect(y).toBeLessThanOrEqual(168);}
 expect(view.container.innerHTML).not.toMatch(/NaN|Infinity/);
});
it.each([0,100,-50])('centers a single value %s and keeps hover finite', value=>{
 const view=render(<RevenueChart data={[point(value)]}/>);
 expect(view.container.querySelector('polyline')!.getAttribute('points')!.split(',').map(Number)[0]).toBe(420);
 const zone=view.container.querySelector('rect')!;expect(zone).toHaveAttribute('width','728');
 fireEvent.mouseEnter(zone);expect(screen.getAllByText(`₹${value}`).length).toBeGreaterThan(0);
 fireEvent.click(screen.getByRole('button',{name:'Orders'}));
 expect(view.container.innerHTML).not.toMatch(/NaN|Infinity/);
});

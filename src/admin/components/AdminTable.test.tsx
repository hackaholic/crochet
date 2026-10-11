import { fireEvent, render, screen, cleanup } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import AdminTable from './AdminTable';
import { readFileSync } from 'node:fs';
afterEach(cleanup);
it('keeps shared row presentation separate from selected cell actions', () => {
 const select = vi.fn();
 render(<AdminTable><tbody><tr><td><button onClick={select}>Customer</button></td><td>Active</td></tr></tbody></AdminTable>);
 expect(screen.getByRole('table')).toHaveClass('admin-data-table');
 fireEvent.mouseOver(screen.getByRole('row'));
 fireEvent.click(screen.getByRole('cell', { name: 'Active' }));
 expect(select).not.toHaveBeenCalled();
 fireEvent.click(screen.getByRole('button', { name: 'Customer' }));
 expect(select).toHaveBeenCalledTimes(1);
});
it('applies the shared cell styling to semantic row headers as well as data cells', async () => {
 const css = readFileSync(`${process.cwd()}/src/admin/components/adminTable.css`, 'utf8');
 expect(css).toContain('tr:hover > :is(td, th)');
 expect(css).toContain('tr:has(:focus-visible) > :is(td, th)');
 expect(css).toContain(':is(td, th):first-child');
 expect(css).toContain(':is(td, th):last-child');
 render(<AdminTable><tbody><tr><th scope="row">Product</th><td>2</td></tr></tbody></AdminTable>);
 expect(screen.getByRole('rowheader', {name:'Product'})).toHaveAttribute('scope','row');
});

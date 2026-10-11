import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, expect, it } from 'vitest';
import FinanceTableHeader from './FinanceTableHeader';
afterEach(cleanup);
it('renders semantic highlighted headers without interpreting untrusted labels as HTML',()=>{
 const view=render(<table><FinanceTableHeader columns={['Category','<img src=x onerror=alert(1)>']}/><tbody><tr><td>Flowers</td><td>₹100</td></tr></tbody></table>);
 for(const header of screen.getAllByRole('columnheader')) expect(header).toHaveAttribute('scope','col');
 expect(screen.getByRole('columnheader',{name:'Category'}).closest('thead')).toHaveClass('finance-table-header');
 expect(screen.getByRole('columnheader',{name:'<img src=x onerror=alert(1)>'})).toBeInTheDocument();
 expect(view.container.querySelector('img')).toBeNull();
 expect(screen.getByRole('cell',{name:'₹100'})).toBeInTheDocument();
});

import {render,screen,cleanup} from '@testing-library/react';
import {it,expect,afterEach} from 'vitest';
import SeoBreadcrumbs from './SeoBreadcrumbs';
import type {SeoMetadata} from '../lib/api/seo';
afterEach(cleanup);
it('renders actual API breadcrumb links and an unlinked current page',()=>{
  render(<SeoBreadcrumbs metadata={{canonicalUrl:'https://store.example/products/bunny',breadcrumbs:[{name:'Shop',path:'/shop'},{name:'Animals',path:'/categories/animals'},{name:'Bunny',path:'/products/bunny'}]} as SeoMetadata}/>);
  expect(screen.getByRole('link',{name:'Animals'})).toHaveAttribute('href','/categories/animals');
  expect(screen.getByText('Bunny')).toHaveAttribute('aria-current','page');
  expect(screen.queryByRole('link',{name:'Bunny'})).toBeNull();
});

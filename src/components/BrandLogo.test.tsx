import {render,screen,cleanup,fireEvent} from '@testing-library/react';
import {afterEach,it,expect,vi} from 'vitest';
import BrandLogo from './BrandLogo';
vi.mock('../lib/api/storefront',()=>({getStorefrontContent:vi.fn().mockResolvedValue({brand:{logoUrl:'https://images.example/brand/logo.png'}})}));
afterEach(cleanup);
it('renders the API logo and falls back safely if its image fails',async()=>{render(<BrandLogo/>);const img=await screen.findByRole('img',{name:'Sulocraft logo'});expect(img).toHaveAttribute('src','https://images.example/brand/logo.png');fireEvent.error(img);expect(screen.getByLabelText('Sulocraft logo')).toHaveTextContent('S');});

it('keeps the original height when replacing the separate wordmark',()=>{const {container}=render(<BrandLogo size={38} wordmark/>);expect(container.firstChild).toHaveStyle({width:'190px',height:'38px'});});

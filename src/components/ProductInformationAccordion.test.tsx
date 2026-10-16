import {cleanup,render,screen,fireEvent,waitFor} from '@testing-library/react';
import {afterEach,it,expect,vi} from 'vitest';
import ProductInformationAccordion from './ProductInformationAccordion';
const get=vi.hoisted(()=>vi.fn());vi.mock('../lib/api/catalogue',()=>({getProductInformation:get}));
afterEach(()=>{cleanup();vi.resetAllMocks();});
it('renders saved text safely, omits empty claims and provides accessible disclosure',async()=>{get.mockResolvedValue({handmadeDetails:'<img src=x onerror=alert(1)>\nHandmade',materialsUsed:'Cotton',sizeDimensions:''});render(<ProductInformationAccordion productId="bunny"/>);const button=await screen.findByRole('button',{name:'Handmade Details'});expect(button).toHaveAttribute('aria-expanded','true');expect(document.querySelector('img')).toBeNull();expect(screen.queryByRole('button',{name:'Size & Dimensions'})).toBeNull();fireEvent.click(button);expect(button).toHaveAttribute('aria-expanded','false');fireEvent.click(screen.getByRole('button',{name:'Materials Used'}));expect(screen.getByText('Cotton')).toBeVisible();});
it('loads each product independently and recovers failed requests',async()=>{get.mockRejectedValueOnce(new Error('private')).mockResolvedValueOnce({materialsUsed:'First product'}).mockResolvedValueOnce({materialsUsed:'Second product'});const {rerender}=render(<ProductInformationAccordion productId={1}/>);fireEvent.click(await screen.findByRole('button',{name:'Retry product information'}));await screen.findByText('First product');rerender(<ProductInformationAccordion productId={2}/>);await screen.findByText('Second product');expect(screen.queryByText('First product')).toBeNull();expect(screen.queryByText('private')).toBeNull();await waitFor(()=>expect(get).toHaveBeenLastCalledWith(2,expect.any(AbortSignal)));});
it('renders saved snapshot details in initial HTML and never invents empty fields',async()=>{
 const {renderToString}=await import('react-dom/server');
 const html=renderToString(<ProductInformationAccordion productId="rose" initialInformation={{materialsUsed:'Owner supplied yarn',processingTime:null}}/>);
 expect(html).toContain('Owner supplied yarn');expect(html).not.toContain('Loading product information');expect(html).not.toContain('Processing Time');
});
it('does not leak a previous product snapshot while a new request is pending',async()=>{
 get.mockImplementation(()=>new Promise(()=>{}));
 const {rerender}=render(<ProductInformationAccordion productId="first" initialInformation={{materialsUsed:'First-only yarn'}}/>);
 expect(screen.getByText('First-only yarn')).toBeInTheDocument();
 rerender(<ProductInformationAccordion productId="second"/>);
 expect(screen.queryByText('First-only yarn')).toBeNull();
 expect(screen.getByRole('status')).toHaveTextContent('Loading product information');
});

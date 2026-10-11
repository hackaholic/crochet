import {useState} from 'react';
import {cleanup,fireEvent,render,screen,waitFor} from '@testing-library/react';
import {afterEach,expect,it,vi} from 'vitest';
import ProductPhotos from './ProductPhotos';
import {uploadPhoto} from '../services/catalogue';
vi.mock('../services/catalogue',()=>({uploadPhoto:vi.fn()}));
afterEach(()=>{cleanup();vi.resetAllMocks();});
function Photos(){
 const [value,setValue]=useState({primary:'products/original.webp',gallery:['products/original.webp']});
 return <><ProductPhotos {...value} urls={{'products/original.webp':'https://images.example/original.webp'}} onBusy={()=>{}} onChange={(primary,gallery)=>setValue({primary,gallery})}/><output aria-label="Saved photo selection">{JSON.stringify(value)}</output></>;
}
it('retains the existing gallery after a failed upload and supports retry without duplicate keys',async()=>{
 vi.mocked(uploadPhoto).mockRejectedValueOnce(new Error('offline')).mockResolvedValue({key:'products/new.webp',url:'https://images.example/new.webp'});
 render(<Photos/>);
 const upload=()=>fireEvent.change(screen.getByLabelText('Upload a photo'),{target:{files:[new File(['image'],'new.webp',{type:'image/webp'})]}});
 upload();expect(await screen.findByRole('alert')).toHaveTextContent('existing photos are unchanged');
 expect(screen.getByLabelText('Saved photo selection')).toHaveTextContent('"gallery":["products/original.webp"]');
 upload();await waitFor(()=>expect(screen.getAllByRole('img')).toHaveLength(2));
 expect(screen.queryByRole('alert')).not.toBeInTheDocument();
 upload();await waitFor(()=>expect(uploadPhoto).toHaveBeenCalledTimes(3));
 expect(screen.getAllByRole('img')).toHaveLength(2);
});
it('promotes an uploaded image and selects a remaining primary when that image is removed',async()=>{
 vi.mocked(uploadPhoto).mockResolvedValue({key:'products/new.webp',url:'https://images.example/new.webp'});
 render(<Photos/>);
 fireEvent.change(screen.getByLabelText('Upload a photo'),{target:{files:[new File(['image'],'new.webp',{type:'image/webp'})]}});
 fireEvent.click(await screen.findByRole('button',{name:'Make primary'}));
 expect(screen.getByLabelText('Saved photo selection')).toHaveTextContent('"primary":"products/new.webp"');
 fireEvent.click(screen.getAllByRole('button',{name:'Remove photo'})[0]);
 expect(screen.getByLabelText('Saved photo selection')).toHaveTextContent('"primary":"products/original.webp"');
 expect(screen.getAllByRole('img')).toHaveLength(1);
});

import { describe, it, expect } from 'vitest';
import { accountResponseError } from './validationErrors';
describe('safe account errors',()=>{
 it('maps allowlisted fields without reflecting input or server text',async()=>{
 const error=await accountResponseError(new Response(JSON.stringify({detail:[{loc:['body','postal_code'],msg:'private secret',input:'private'},{loc:['body','role'],msg:'secret'}]}),{status:422}));
 expect(error.fields).toEqual({postalCode:'Please check this value.'});expect(error.message).toBe('422');
 });
 it('handles invalid bodies without leaking them',async()=>{
 expect((await accountResponseError(new Response('secret',{status:422}))).fields).toEqual({});
 });
});

import {it,expect,vi,afterEach} from 'vitest';
import {validateBrand,saveBrandSettings} from './brandSettings';
const request=vi.hoisted(()=>vi.fn());vi.mock('../../lib/api/admin',()=>({adminRequest:request}));
afterEach(()=>vi.resetAllMocks());
const draft={name:' Store ',ownerName:' Owner ',instagramUrl:'',whatsappUrl:''};
it('trims payload and permits blank optional links',async()=>{await saveBrandSettings(draft);expect(request).toHaveBeenCalledWith('/admin/storefront/brand',{method:'PUT',body:JSON.stringify({name:'Store',ownerName:'Owner',instagramUrl:'',whatsappUrl:''})});expect(validateBrand(draft)).toEqual({});});
it.each(['javascript:alert(1)','data:text/html,bad','https://user:pass@example.com','/relative','http://example.com','https://example.com/a b'])('rejects unsafe link %s',(instagramUrl)=>{expect(validateBrand({...draft,instagramUrl})).toHaveProperty('instagramUrl');});
it('rejects oversized and control-character names',()=>{expect(validateBrand({...draft,name:'a'.repeat(101),ownerName:'ab\ncd'})).toHaveProperty('name');expect(validateBrand({...draft,ownerName:'ab\ncd'})).toHaveProperty('ownerName');});

it('matches server URL length limit',()=>{expect(validateBrand({...draft,instagramUrl:"https://example.com/"+"a".repeat(256)})).toHaveProperty("instagramUrl");});

import {expect,it} from 'vitest';
import {renderToStaticMarkup} from 'react-dom/server';
import PersonalizationNote from './PersonalizationNote';
it('renders saved note as inert text and omits absent or invalid values',()=>{
 const html=renderToStaticMarkup(<PersonalizationNote personalization={{note:'<script>hello</script>'}}/>);
 expect(html).toContain('&lt;script&gt;hello&lt;/script&gt;');
 expect(html).not.toContain('<script>');
 for(const value of [undefined,{}, {note:''},{note:{}},{note:42}]) expect(renderToStaticMarkup(<PersonalizationNote personalization={value}/>)).toBe('');
});

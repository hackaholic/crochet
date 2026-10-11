import {informationFields,INFORMATION_LIMIT,type ProductInformation} from '../../lib/products/information';
import {Field,controlClass} from './CatalogueFields';
export default function ProductInformationFields({value,onChange,defaults,disabled=false}:{value:ProductInformation;onChange:(value:ProductInformation)=>void;defaults?:ProductInformation;disabled?:boolean}) {
 return <fieldset disabled={disabled} className="space-y-4"><legend className="mb-3 font-semibold">Product information</legend>
  {informationFields.map(([key,label])=><div key={key}><Field label={label}><textarea rows={3} maxLength={INFORMATION_LIMIT} className={controlClass} value={value[key]??''} onChange={e=>onChange({...value,[key]:e.target.value})}/></Field>
   {defaults && <button type="button" className="text-xs underline" onClick={()=>onChange({...value,[key]:defaults[key]??''})}>Reset {label} to default</button>}
  </div>)}
 </fieldset>;
}

import type { DateRangePreset } from '../types';
/** Finance endpoints interpret inclusive calendar dates in IST. */
export function dateRange(preset: DateRangePreset, now = new Date()) {
  const parts = new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Kolkata', year:'numeric',month:'2-digit',day:'2-digit' }).formatToParts(now);
  const part = (type:string) => Number(parts.find(item=>item.type===type)?.value);
  const end = new Date(Date.UTC(part('year'),part('month')-1,part('day')));
  const start = new Date(end);
  if(preset==='yesterday') {start.setUTCDate(start.getUTCDate()-1);end.setUTCDate(end.getUTCDate()-1);}
  else if(preset==='7d') start.setUTCDate(start.getUTCDate()-6);
  else if(preset==='30d') start.setUTCDate(start.getUTCDate()-29);
  else if(preset==='this_month') start.setUTCDate(1);
  else if(preset==='prev_month') {start.setUTCMonth(start.getUTCMonth()-1,1);end.setUTCDate(0);}
  const iso = (date:Date)=>date.toISOString().slice(0,10);
  return {from:iso(start),to:iso(end)};
}

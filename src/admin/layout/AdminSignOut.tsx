import { useState } from 'react';
export default function AdminSignOut({onLogout,collapsed}:{onLogout:()=>Promise<void>;collapsed:boolean}) {
 const [pending,setPending]=useState(false);
 const [error,setError]=useState('');
 const signOut=async()=>{setPending(true);setError('');try{await onLogout();}catch{setError('Could not sign out. Try again.');setPending(false);}};
 return <div><button type="button" onClick={signOut} disabled={pending} aria-label={pending?'Signing out…':'Sign out'} title="Sign out" className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-white/70 hover:bg-white/10 hover:text-white disabled:opacity-50"><span aria-hidden="true">↪</span>{!collapsed && <span className="hidden md:inline">{pending?'Signing out…':'Sign out'}</span>}</button>{error && <p role="alert" className="px-3 py-2 text-xs text-red-200">{error}</p>}</div>;
}

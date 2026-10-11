import type { ComponentProps } from 'react';
import './adminTable.css';

/** Shared presentation only: each page retains its own native links and actions. */
export default function AdminTable({className='',...props}:ComponentProps<'table'>) {
  return <table {...props} className={`admin-data-table ${className}`}/>;
}

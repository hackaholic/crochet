import './financeTable.css';

/** Shared finance table header; column labels remain accessible and escaped. */
export default function FinanceTableHeader({ columns }: { columns: string[] }) {
  return <thead className="finance-table-header"><tr>{columns.map((label,index) => <th key={`${index}-${label}`} scope="col">{label}</th>)}</tr></thead>;
}

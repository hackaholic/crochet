export default function AdminPagination({ data, onPage, label }: { data: { page: number; pageSize: number; total: number }; onPage: (page: number) => void; label: string }) {
  return <nav aria-label={label} className="mt-4 flex items-center justify-between gap-3 text-sm">
    <button className="underline disabled:opacity-50" disabled={data.page <= 1} onClick={() => onPage(data.page - 1)}>Previous</button>
    <span>Page {data.page} · {data.total} results</span>
    <button className="underline disabled:opacity-50" disabled={data.page * data.pageSize >= data.total} onClick={() => onPage(data.page + 1)}>Next</button>
  </nav>;
}

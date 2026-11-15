// Pagination.tsx - Pagination component
interface PaginationProps {
  page: number;
  pageSize: number;
  total: number;
  onPageChange: (page: number) => void;
  onPageSizeChange: (size: number) => void;
  totalPages?: number;
  ariaLabel?: string;
}

export function Pagination({
  page,
  pageSize,
  total,
  onPageChange,
  onPageSizeChange,
  totalPages,
  ariaLabel = 'Pagination',
}: PaginationProps) {
  const totalPagesCalc = totalPages || Math.ceil(total / pageSize) || 1;
  const start = (page - 1) * pageSize + 1;
  const end = Math.min(page * pageSize, total);

  const goToPage = (p: number) => {
    if (p >= 1 && p <= totalPagesCalc && p !== page) onPageChange(p);
  };

  const goToNext = () => goToPage(page + 1);
  const goToPrev = () => goToPage(page - 1);

  const pageNumbers = [];
  const maxVisible = 5;
  let startPage = Math.max(1, page - Math.floor(maxVisible / 2));
  const endPage = Math.min(totalPagesCalc, startPage + maxVisible - 1);
  if (endPage - startPage < maxVisible - 1) {
    startPage = Math.max(1, endPage - maxVisible + 1);
  }
  for (let i = startPage; i <= endPage; i++) {
    pageNumbers.push(i);
  }

  return (
    <nav className="flex items-center justify-between gap-4 mt-6" aria-label={ariaLabel}>
      <div className="text-sm text-text-muted">
        Showing <span className="font-medium">{start}</span> to{' '}
        <span className="font-medium">{end}</span> of <span className="font-medium">{total}</span>
      </div>

      <div className="flex items-center gap-2">
        <button
          className="px-3 py-1.5 text-sm font-medium rounded-lg border border-border text-text-muted hover:bg-border-subtle disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          onClick={goToPrev}
          disabled={page <= 1}
          aria-label="Previous page"
        >
          Previous
        </button>

        <div className="flex items-center gap-1">
          {pageNumbers.map((p) => (
            <button
              key={p}
              className={`w-9 h-9 rounded-lg text-sm font-semibold transition-colors ${
                p === page
                  ? 'bg-[#175A67] text-[#FAF8F5] shadow-xs'
                  : 'text-text-muted hover:bg-white/80 hover:text-text'
              }`}
              onClick={() => goToPage(p)}
              aria-current={p === page ? 'page' : undefined}
            >
              {p}
            </button>
          ))}
        </div>

        <button
          className="px-3 py-1.5 text-sm font-medium rounded-lg border border-border text-text-muted hover:bg-border-subtle disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          onClick={goToNext}
          disabled={page >= totalPagesCalc}
          aria-label="Next page"
        >
          Next
        </button>
      </div>

      <div className="flex items-center gap-2">
        <label className="text-sm text-text-muted">Rows per page:</label>
        <select
          className="px-2 py-1 rounded border border-border text-sm text-text bg-white"
          value={pageSize}
          onChange={(e) => onPageSizeChange(Number(e.target.value))}
          aria-label="Rows per page"
        >
          {[5, 10, 20, 50].map((size) => (
            <option key={size} value={size}>
              {size}
            </option>
          ))}
        </select>
      </div>
    </nav>
  );
}

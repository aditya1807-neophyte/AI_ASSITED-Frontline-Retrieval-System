// FilterBar.tsx - Filter controls
import React from 'react';

interface FilterOption {
  label: string;
  value: string;
  icon?: React.ReactNode;
}

interface FilterBarProps {
  filters: Record<string, string>;
  onChange: (filters: Record<string, string>) => void;
  options: Record<string, FilterOption[]>;
  className?: string;
}

export function FilterBar({ filters, onChange, options, className = '' }: FilterBarProps) {
  const updateFilter = (key: string, value: string) => {
    const newFilters = { ...filters };
    if (value === '') {
      delete newFilters[key];
    } else {
      newFilters[key] = value;
    }
    onChange(newFilters);
  };

  const clearAll = () => {
    onChange({});
  };

  return (
    <div className={`flex flex-wrap items-center gap-3 ${className}`}>
      {Object.entries(options).map(([key, optionsList]) => (
        <div key={key} className="flex flex-wrap items-center gap-2">
          <label className="text-sm font-medium text-text-muted">{key}:</label>
          <select
            className="px-2 py-1 rounded border border-border text-sm bg-white text-text"
            value={filters[key] || ''}
            onChange={(e) => updateFilter(key, e.target.value)}
            aria-label={`Filter by ${key}`}
          >
            <option value="">All</option>
            {optionsList.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      ))}

      {(Object.values(filters).some((v) => v) || Object.values(options).some((opts) =>
          opts.some((o) => filters[o.value] === o.value)
        )) && (
        <button
          className="text-sm text-accent hover:underline"
          onClick={clearAll}
        >
          Clear all
        </button>
      )}
    </div>
  );
}

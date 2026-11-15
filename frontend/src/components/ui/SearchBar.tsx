// SearchBar.tsx - Reusable search input
import React from 'react';
import { Search, X } from 'lucide-react';

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  onSearch?: (query: string) => void;
  debounceMs?: number;
  showClear?: boolean;
  className?: string;
}

export function SearchBar({
  value,
  onChange,
  placeholder = 'Search knowledge base...',
  onSearch,
  debounceMs = 300,
  showClear = true,
  className = '',
}: SearchBarProps) {


  React.useEffect(() => {
    const timer = setTimeout(() => {
      onSearch?.(value);
    }, debounceMs);
    return () => clearTimeout(timer);
  }, [value, onSearch, debounceMs]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
  };

  const handleClear = () => {
    onChange('');
    onSearch?.('');
  };

  return (
    <div className={`relative ${className}`}>
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-muted" />
      <input
        type="text"
        className="glass-input w-full pl-10 pr-10 py-2.5 rounded-xl text-text placeholder-text-muted/70 focus:outline-none focus:bg-white/90 focus:border-accent focus:ring-2 focus:ring-accent/15 transition-all text-sm"
        placeholder={placeholder}
        value={value}
        onChange={handleChange}
        aria-label="Search"
      />
      {value && showClear && (
        <button
          className="absolute right-2 top-1/2 -translate-y-1/2 p-1 rounded-full hover:bg-border-subtle transition-colors"
          onClick={handleClear}
          aria-label="Clear search"
        >
          <X className="h-4 w-4 text-text-muted" />
        </button>
      )}
    </div>
  );
}

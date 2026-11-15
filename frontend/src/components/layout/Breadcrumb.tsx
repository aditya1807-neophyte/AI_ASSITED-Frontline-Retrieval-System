// Breadcrumb.tsx - Breadcrumb navigation
import React from 'react';
import { NavLink } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';

interface BreadcrumbProps {
  items: { label: string; href?: string; icon?: React.ReactNode }[];
}

export function Breadcrumb({ items }: BreadcrumbProps) {
  return (
    <nav aria-label="Breadcrumb" className="text-sm">
      <ol className="flex items-center gap-1.5 text-text-muted">
        {items.map((item, index) => (
          <li key={index} className="flex items-center gap-1.5">
            {index > 0 && <ChevronRight className="h-3.5 w-3.5" />}
            {item.href ? (
              <NavLink
                to={item.href}
                className="flex items-center gap-1.5 hover:text-text transition-colors"
              >
                {item.icon}
                <span className="truncate">{item.label}</span>
              </NavLink>
            ) : (
              <>
                {item.icon}
                <span className="text-text font-medium">{item.label}</span>
              </>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}

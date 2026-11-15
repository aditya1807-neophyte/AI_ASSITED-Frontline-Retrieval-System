// CitationLink.tsx - Citation link component
import React from 'react';

interface CitationLinkProps {
  text: string;
  href: string;
  icon?: React.ReactNode;
  external?: boolean;
  className?: string;
}

export function CitationLink({ text, href, icon, external = false, className = '' }: CitationLinkProps) {
  return (
    <a
      href={href}
      className={`inline-flex items-center gap-1.5 text-sm font-medium text-accent hover:text-accent-dark transition-colors underline-offset-2 ${className}`}
      target={external ? '_blank' : undefined}
      rel={external ? 'noopener noreferrer' : undefined}
    >
      {icon || <span className="w-4 h-4" />}
      {text}
      {external && (
        <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
        </svg>
      )}
    </a>
  );
}

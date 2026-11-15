// Card.tsx - Reusable frosted glass card container
import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hover?: boolean;
  onClick?: () => void;
}

export function Card({ children, className = '', padding = 'md', hover = false, onClick }: CardProps) {
  const paddingClasses = {
    none: 'p-0',
    sm: 'p-3.5 sm:p-4',
    md: 'p-4 sm:p-5',
    lg: 'p-5 sm:p-6',
  };

  const baseClasses =
    'bg-white/40 backdrop-blur-xl border border-white/60 rounded-2xl text-[#101410] shadow-[inset_0_1px_1px_rgba(255,255,255,0.75),0_8px_30px_0_rgba(23,90,103,0.05),0_2px_8px_rgba(16,20,16,0.02)] transition-all duration-200';

  const hoverClasses = hover
    ? 'hover:bg-white/60 hover:shadow-[inset_0_1px_1px_rgba(255,255,255,0.9),0_14px_40px_0_rgba(23,90,103,0.08)] hover:border-white/80 hover:-translate-y-0.5 cursor-pointer'
    : '';

  return (
    <div onClick={onClick} className={`${baseClasses} ${paddingClasses[padding]} ${hoverClasses} ${className}`}>
      {children}
    </div>
  );
}

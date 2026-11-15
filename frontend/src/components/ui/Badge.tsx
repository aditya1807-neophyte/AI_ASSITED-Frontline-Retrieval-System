// Badge.tsx - Glassmorphic status badge component
import { ReactNode } from 'react';

interface BadgeProps {
  status?: string;
  tone?: 'success' | 'warning' | 'danger' | 'info' | 'neutral';
  size?: 'sm' | 'md';
  className?: string;
  children?: ReactNode;
}

export function Badge({ status, tone = 'neutral', size = 'md', className = '', children }: BadgeProps) {
  const toneMap: Record<string, string> = {
    success: 'bg-[#E2ECED] text-[#175A67] border-[#175A67]/20',
    warning: 'bg-amber-100/75 text-amber-800 border-amber-200/60',
    danger: 'bg-rose-100/75 text-rose-800 border-rose-200/60',
    info: 'bg-blue-100/75 text-blue-800 border-blue-200/60',
    neutral: 'bg-stone-100/75 text-stone-700 border-stone-200/60',
  };

  const sizeClass = size === 'sm' ? 'py-0.5 px-2 text-[10px]' : 'py-1 px-2.5 text-xs';

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-semibold rounded-full border backdrop-blur-xs tracking-wide shadow-2xs ${
        toneMap[tone] || toneMap.neutral
      } ${sizeClass} ${className}`}
    >
      {children || status}
    </span>
  );
}

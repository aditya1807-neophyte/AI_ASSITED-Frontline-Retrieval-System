// CardHeader.tsx - Card header with title and actions
import React from 'react';

interface CardHeaderProps {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  className?: string;
}

export function CardHeader({ title, subtitle, action, className = '' }: CardHeaderProps) {
  return (
    <div className={`flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 ${className}`}>
      <div>
        <h3 className="text-xl font-heading font-bold text-[#101410]">{title}</h3>
        {subtitle && <p className="font-heading italic text-xs sm:text-sm text-[#263B40] mt-0.5 font-medium">{subtitle}</p>}
      </div>
      {action && <div className="flex items-center gap-2">{action}</div>}
    </div>
  );
}

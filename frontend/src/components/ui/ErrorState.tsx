// ErrorState.tsx - Error state component
import React from 'react';

interface ErrorStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
  iconSize?: 'sm' | 'md' | 'lg';
}

export function ErrorState({ icon, title, description, action, iconSize = 'md' }: ErrorStateProps) {
  const iconSizeClasses = {
    sm: 'h-8 w-8',
    md: 'h-12 w-12',
    lg: 'h-16 w-16',
  };

  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
      <div
        className={`${iconSizeClasses[iconSize]} rounded-full bg-status-danger-soft flex items-center justify-center mb-4`}
      >
        {icon || <span className="text-status-danger text-lg">⚠️</span>}
      </div>
      <h3 className="text-lg font-semibold text-text">{title}</h3>
      {description && <p className="text-sm text-text-muted mt-1 max-w-sm">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

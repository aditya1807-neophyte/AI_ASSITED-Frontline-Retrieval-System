// StatusBadge.tsx - Status badge with tone mapping
import { ReactNode } from 'react';
import { Badge } from './Badge';

type StatusTone = 'success' | 'warning' | 'danger' | 'info' | 'neutral';

interface StatusBadgeProps {
  status: string;
  tone?: StatusTone;
  size?: 'sm' | 'md';
  showIcon?: boolean;
  icon?: ReactNode;
}

export function StatusBadge({ status, tone = 'neutral', size = 'md', showIcon = false, icon }: StatusBadgeProps) {
  const lowCaseStatus = status.toLowerCase();

  let resolvedTone: StatusTone = tone;
  if (lowCaseStatus.includes('active') || lowCaseStatus.includes('completed') || lowCaseStatus.includes('verified')) {
    resolvedTone = 'success';
  } else if (lowCaseStatus.includes('review') || lowCaseStatus.includes('pending') || lowCaseStatus.includes('warning')) {
    resolvedTone = 'warning';
  } else if (lowCaseStatus.includes('error') || lowCaseStatus.includes('failed') || lowCaseStatus.includes('critical')) {
    resolvedTone = 'danger';
  } else if (lowCaseStatus.includes('info') || lowCaseStatus.includes('in progress') || lowCaseStatus.includes('processing')) {
    resolvedTone = 'info';
  } else {
    resolvedTone = 'neutral';
  }

  return (
    <Badge
      status={status}
      tone={resolvedTone}
      size={size}
    >
      {showIcon && icon}
      {status}
    </Badge>
  );
}

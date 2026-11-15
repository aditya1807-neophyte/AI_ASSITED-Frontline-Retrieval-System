// LoadingSkeleton.tsx - Loading skeleton component

interface LoadingSkeletonProps {
  className?: string;
  variant?: 'text' | 'card' | 'table' | 'avatar';
  count?: number;
}

export function LoadingSkeleton({ className = '', variant = 'text', count = 1 }: LoadingSkeletonProps) {
  const variantClasses = {
    text: 'h-4 rounded bg-border-color',
    card: 'h-40 rounded-lg bg-border-color',
    table: 'h-10 rounded bg-border-color',
    avatar: 'h-10 w-10 rounded-full bg-border-color',
  };

  const widths = Array.from({ length: count }, (_, i) => (
    <div key={i} className={`${variantClasses[variant]} animate-pulse`} />
  ));

  return <div className={`flex flex-col gap-3 ${className}`}>{widths}</div>;
}

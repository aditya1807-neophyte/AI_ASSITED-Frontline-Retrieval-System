// User.tsx - Avatar placeholder component
import { User as LucideUser } from 'lucide-react';

interface UserProps {
  className?: string;
}

export function User({ className = '' }: UserProps) {
  return <LucideUser className={className} />;
}

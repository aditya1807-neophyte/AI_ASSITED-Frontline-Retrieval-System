// Toast.tsx - Toast notification display
import { Toast } from '@/types';

interface ToastItemProps {
  toast: Toast;
  onDismiss: () => void;
}

const toastIcons = {
  success: '✓',
  info: 'ℹ',
  warning: '⚠',
  error: '✕',
};

export function ToastItem({ toast, onDismiss }: ToastItemProps) {
  const icon = toastIcons[toast.type] || 'i';

  return (
    <div
      className={`toast flex items-start gap-3 ${
        toast.type === 'success' ? 'toast-success' :
        toast.type === 'info' ? 'toast-info' :
        toast.type === 'warning' ? 'toast-warning' :
        'toast-danger'
      }`}
      role="alert"
    >
      <div className="toast-icon mt-0.5">{icon}</div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-text">{toast.title}</p>
        {toast.description && <p className="text-sm text-text-muted mt-0.5">{toast.description}</p>}
      </div>
      <button
        className="flex-shrink-0 p-1 rounded-md hover:bg-border-subtle transition-colors"
        onClick={onDismiss}
        aria-label="Dismiss notification"
      >
        <svg className="h-4 w-4 text-text-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
}

export type { Toast };

// useToast.ts - Toast notification hook
import { useState, useCallback, useEffect } from 'react';
import { Toast } from '../components/ui/types';

interface ToastOptions {
  type: Toast['type'];
  title: string;
  description?: string;
  duration?: number;
}

let toastId = 0;

export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const showToast = useCallback((options: ToastOptions) => {
    const id = `toast-${++toastId}`;
    const { type, title, description, duration = 5000 } = options;

    const toast: Toast = {
      id,
      type,
      title,
      description,
    };

    setToasts((prev) => [...prev, toast]);

    setTimeout(() => {
      removeToast(id);
    }, duration);
  }, [removeToast]);

  useEffect(() => {
    if (toasts.length === 0) return;
    const timer = setTimeout(() => {
      setToasts([]);
    }, 5000);
    return () => clearTimeout(timer);
  }, [toasts.length]);

  return { toasts, showToast, removeToast };
}

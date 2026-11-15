// Modal.tsx - Premium glassmorphic modal dialog component
import React, { useEffect, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { X } from 'lucide-react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  closeOnOverlay?: boolean;
  footer?: React.ReactNode;
  maxWidth?: string;
}

export function Modal({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  closeOnOverlay = true,
  footer,
  maxWidth,
}: ModalProps) {
  const handleEscape = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    },
    [onClose]
  );

  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, handleEscape]);

  if (!isOpen) return null;

  const sizeClasses: Record<string, string> = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
  };

  const handleClickOverlay = (e: React.MouseEvent) => {
    if (closeOnOverlay && e.target === e.currentTarget) {
      onClose();
    }
  };

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 bg-black/40 backdrop-blur-md overflow-y-auto animate-fadeIn"
      onClick={handleClickOverlay}
      role="dialog"
      aria-modal="true"
      aria-label={title}
    >
      <div
        className={`relative w-full max-h-[90vh] flex flex-col rounded-3xl bg-[#FAF8F5]/95 backdrop-blur-2xl border border-white/80 shadow-[0_20px_60px_rgba(23,90,103,0.20)] text-slate-900 overflow-hidden my-auto ${
          sizeClasses[size] || sizeClasses.md
        }`}
        style={maxWidth ? { maxWidth } : undefined}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 sm:px-6 py-4 border-b border-[#175A67]/15 bg-white/70 backdrop-blur-sm">
          <h2 className="text-base sm:text-lg font-heading font-bold text-[#101410] tracking-tight leading-snug line-clamp-1 pr-2">
            {title}
          </h2>
          <button
            type="button"
            className="p-1.5 rounded-xl hover:bg-slate-200/60 text-slate-400 hover:text-slate-800 transition-colors cursor-pointer shrink-0"
            onClick={onClose}
            aria-label="Close modal"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Scrollable Body */}
        <div className="px-5 sm:px-6 py-4 overflow-y-auto flex-1">{children}</div>

        {/* Optional Footer */}
        {footer && (
          <div className="px-5 sm:px-6 py-3.5 border-t border-[#175A67]/15 bg-white/50 backdrop-blur-sm flex items-center justify-end gap-2">
            {footer}
          </div>
        )}
      </div>
    </div>,
    document.body
  );
}

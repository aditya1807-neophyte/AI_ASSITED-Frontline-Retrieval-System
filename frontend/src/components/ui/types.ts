// types.ts - Shared UI types
import React from 'react';

export type ToastType = 'success' | 'info' | 'warning' | 'error';

export interface Toast {
  id: string;
  type: ToastType;
  title: string;
  description?: string;
  duration?: number;
}

export interface Pagination {
  page: number;
  pageSize: number;
  total: number;
  totalPages: number;
  hasPrev: boolean;
  hasNext: boolean;
}

export interface SortOption {
  label: string;
  value: string;
  direction: 'asc' | 'desc';
}

export interface FilterOption {
  label: string;
  value: string;
}

export interface StatusBadgeProps {
  status: string;
  tone?: 'success' | 'warning' | 'danger' | 'info' | 'neutral';
  size?: 'sm' | 'md' | 'lg';
}

export interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
  iconSize?: 'sm' | 'md' | 'lg';
}

export interface LoadingSkeletonProps {
  className?: string;
  variant?: 'text' | 'card' | 'table' | 'avatar';
  width?: string;
  height?: string;
  count?: number;
}

export interface ErrorStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
  iconSize?: 'sm' | 'md' | 'lg';
}

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  maxWidth?: string;
  size?: 'sm' | 'md' | 'lg';
  closeOnOverlay?: boolean;
}

export interface PaginationProps {
  page: number;
  pageSize: number;
  total: number;
  onPageChange: (page: number) => void;
  onPageSizeChange: (size: number) => void;
  totalPages?: number;
  ariaLabel?: string;
}

export interface BreadcrumbItem {
  label: string;
  href?: string;
  icon?: React.ReactNode;
}

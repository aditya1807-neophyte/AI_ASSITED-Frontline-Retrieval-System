// Button.tsx - Soft mint studio & frosted glass button component
import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'mint' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export function Button({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  leftIcon,
  rightIcon,
  className = '',
  disabled,
  children,
  ...props
}: ButtonProps) {
  const baseClasses =
    'inline-flex items-center justify-center gap-2 font-medium transition-all duration-150 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed select-none active:scale-[0.98]';

  const variantClasses = {
    primary:
      'bg-[#175A67] text-[#FAF8F5] border border-[#175A67] hover:bg-[#0F3D47] shadow-sm hover:shadow-[0_4px_20px_rgba(23,90,103,0.35)]',
    secondary:
      'bg-white/80 backdrop-blur-md text-[#101410] border border-white/85 hover:bg-white hover:border-white shadow-2xs font-medium',
    mint:
      'bg-[#E2ECED] text-[#175A67] border border-[#175A67]/25 hover:bg-[#D5E4E6] hover:border-[#175A67]/40 font-semibold shadow-2xs',
    ghost:
      'bg-transparent text-[#4A5B5E] hover:bg-white/60 hover:text-[#101410] backdrop-blur-xs',
    danger:
      'bg-rose-700 text-white border border-rose-600/50 hover:bg-rose-800 shadow-sm',
  };

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-xs rounded-xl',
    md: 'px-4 py-2 text-sm rounded-xl',
    lg: 'px-5 py-2.5 text-base rounded-2xl',
  };

  const loading = isLoading ? (
    <span className="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full" />
  ) : (
    leftIcon || null
  );

  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {loading}
      {children || null}
      {rightIcon}
    </button>
  );
}

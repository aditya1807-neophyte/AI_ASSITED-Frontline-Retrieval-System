// FormField.tsx - Reusable form field with label and error
import React from 'react';

interface FormFieldProps {
  label: string;
  name: string;
  type?: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => void;
  error?: string;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
}

export function FormField({
  label,
  name,
  type = 'text',
  value,
  onChange,
  error,
  placeholder,
  required = false,
  disabled = false,
}: FormFieldProps) {
  const inputId = `field-${name}`;

  return (
    <div className="form-group">
      <label htmlFor={inputId} className="form-label">
        {label} {required && <span className="text-status-danger">*</span>}
      </label>
      <input
        id={inputId}
        name={name}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        disabled={disabled}
        className="form-input"
      />
      {error && <p className="form-error">{error}</p>}
    </div>
  );
}

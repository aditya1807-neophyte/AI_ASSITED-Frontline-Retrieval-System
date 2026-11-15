// FileUpload.tsx - Document upload interface
import React from 'react';
import { Upload, X, Download } from 'lucide-react';

interface FileUploadProps {
  onUpload: (file: File) => void;
  uploadedFiles: { file: File; progress: number; status: 'processing' | 'completed' | 'error' }[];
  onRemoveFile: (index: number) => void;
  multiple?: boolean;
}

export function FileUpload({ onUpload, uploadedFiles = [], onRemoveFile, multiple = false }: FileUploadProps) {
  const [dragOver, setDragOver] = React.useState(false);
  const [inputFiles, setInputFiles] = React.useState<File[]>([]);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const files = Array.from(e.dataTransfer.files).filter((f) => f.type.startsWith('application/') || f.type.startsWith('text/') || f.name.includes('.pdf') || f.name.includes('.docx'));
    if (files.length > 0) {
      const selected = multiple ? files : [files[0]];
      setInputFiles((prev) => (multiple ? [...prev, ...files] : [files[0]]));
      selected.forEach((file) => onUpload(file));
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      const selected = multiple ? files : [files[0]];
      setInputFiles((prev) => (multiple ? [...prev, ...files] : [files[0]]));
      selected.forEach((file) => onUpload(file));
    }
  };

  const handleFileRemove = (index: number) => {
    onRemoveFile(index);
    setInputFiles((prev) => prev.filter((_, i) => i !== index));
  };
  return (
    <div className="space-y-4">
      {/* Upload dropzone */}
      <div
        className={`border-2 border-dashed rounded-xl p-8 text-center transition-all ${
          dragOver
            ? 'border-accent bg-accent-light/30'
            : 'border-border hover:border-accent-light/50'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          type="file"
          multiple={multiple}
          onChange={handleInputChange}
          className="hidden"
          id="file-upload-input"
        />
        <label htmlFor="file-upload-input" className="cursor-pointer">
          <div className="flex flex-col items-center gap-2">
            <div className="h-12 w-12 rounded-full bg-accent-light/50 flex items-center justify-center">
              <Upload className="h-6 w-6 text-accent" />
            </div>
            <p className="text-sm font-medium text-text">
              {inputFiles.length > 0 ? `Selected ${inputFiles.length} file${inputFiles.length > 1 ? 's' : ''}` : 'Drop documents here or click to upload'}
            </p>
            <p className="text-xs text-text-muted">
              {multiple ? 'Supports multiple files' : 'Single file upload'}
            </p>
          </div>
        </label>
      </div>

      {/* Uploaded files */}
      {uploadedFiles.length > 0 && (
        <div className="space-y-2">
          {uploadedFiles.map((file, index) => (
            <div
              key={index}
              className="flex items-center gap-3 p-3 rounded-lg bg-surface border border-border"
            >
              <div className={`h-9 w-9 rounded-lg flex items-center justify-center ${
                file.status === 'completed' ? 'bg-accent-light' : 'bg-border-subtle'
              }`}>
                {file.status === 'completed' ? (
                  <Download className="h-4 w-4 text-accent" />
                ) : file.status === 'processing' ? (
                  <span className="h-4 w-4 border-2 border-accent border-t-transparent rounded-full animate-spin" />
                ) : (
                  <X className="h-4 w-4 text-status-danger" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-text truncate">{file.file.name}</p>
                <p className="text-xs text-text-muted">
                  {(file.file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
              <span className="text-xs text-text-muted">{file.status}</span>
              <button
                className="p-1 rounded hover:bg-border-subtle transition-colors"
                onClick={() => handleFileRemove(index)}
                aria-label={`Remove ${file.file.name}`}
              >
                <X className="h-4 w-4 text-text-muted" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

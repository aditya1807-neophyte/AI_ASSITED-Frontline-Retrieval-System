// AnswerPanel.tsx - Glassmorphic answer display
import { Save, XCircle, Sparkles, BookOpen } from 'lucide-react';
import { Button, Badge } from '@/components/ui';

interface AnswerPanelProps {
  answer: string;
  confidence?: number;
  isLoading?: boolean;
  isEmpty?: boolean;
  isError?: boolean;
  error?: string;
  citations?: any[];
  onCitationClick?: (index: number) => void;
  onSave?: () => void;
  isSaved?: boolean;
  onFeedback?: (rating: number) => void;
  onEscalate?: () => void;
}

export function AnswerPanel({
  answer,
  confidence,
  isLoading = false,
  isEmpty = false,
  isError = false,
  error,
  citations = [],
  onCitationClick,
  onSave,
  isSaved = false,
  onEscalate,
}: AnswerPanelProps) {
  if (isLoading) {
    return (
      <div className="space-y-3.5 p-6 rounded-2xl bg-white/50 backdrop-blur-md border border-white/70 animate-pulse">
        <div className="h-5 w-1/3 rounded-lg bg-[#E2ECED] mb-3"></div>
        <div className="h-4 w-full rounded-md bg-stone-200/60"></div>
        <div className="h-4 w-5/6 rounded-md bg-stone-200/60"></div>
        <div className="h-4 w-3/4 rounded-md bg-stone-200/60"></div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="rounded-2xl border border-rose-200 bg-rose-50/70 backdrop-blur-md p-5 sm:p-6 shadow-glass-sm">
        <h4 className="text-base font-heading font-semibold text-rose-800 mb-1.5">Failed to retrieve answer</h4>
        <p className="text-xs sm:text-sm text-text-muted">{error || 'Unable to generate a response. Please try again.'}</p>
      </div>
    );
  }

  if (isEmpty) {
    return (
      <div className="rounded-2xl border border-white/70 bg-white/40 backdrop-blur-md p-8 text-center shadow-glass-sm">
        <p className="text-sm font-heading text-xl text-text-muted italic">
          Enter a question above to receive a cited, evidence-backed answer.
        </p>
      </div>
    );
  }

  if (answer) {
    return (
      <div className="space-y-4">
        {/* Main Glass Answer Card */}
        <div className="rounded-2xl bg-gradient-to-br from-[#E2ECED]/60 via-white/80 to-[#E2ECED]/40 backdrop-blur-xl p-5 sm:p-6 border border-[#175A67]/20 shadow-glass">
          <div className="flex items-center justify-between gap-3 mb-3 pb-3 border-b border-[#175A67]/15">
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-[#175A67]" />
              <span className="text-xl font-heading font-bold text-[#101410] tracking-tight">Answer</span>
            </div>
            {confidence !== undefined && confidence > 0 && (
              <span className="text-xs text-text-muted bg-white/80 px-2.5 py-1 rounded-full border border-white/90 font-medium">
                {Math.round(confidence * 100)}% confidence
              </span>
            )}
          </div>
          <p className="text-sm sm:text-base text-text leading-relaxed whitespace-pre-line font-normal">
            {answer}
          </p>
        </div>

        {/* Citations List */}
        {citations.length > 0 && (
          <div className="mt-4 pt-3.5 border-t border-border-subtle/80">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-text-muted mb-2.5 flex items-center gap-1.5">
              <BookOpen className="h-3.5 w-3.5 text-accent" />
              Sources & Citations
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {citations.map((cite: any, idx: number) => (
                <div
                  key={idx}
                  className="flex items-center justify-between gap-2.5 p-3 rounded-xl bg-white/60 hover:bg-white/90 backdrop-blur-sm border border-white/70 hover:border-accent/40 shadow-2xs transition-all cursor-pointer group"
                  onClick={() => onCitationClick?.(idx)}
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <span className="text-xs font-mono font-bold text-accent shrink-0">[source_{idx + 1}]</span>
                    <span className="text-xs font-medium text-text truncate group-hover:text-accent transition-colors">
                      {cite.title || cite.citation}
                    </span>
                  </div>
                  {cite.page_reference && (
                    <Badge size="sm" tone="neutral" className="shrink-0 text-[10px]">
                      {cite.page_reference}
                    </Badge>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {(onSave || onEscalate) && (
          <div className="mt-3.5 flex gap-2.5">
            {onSave && (
              <Button
                variant="secondary"
                size="sm"
                onClick={onSave}
                className="flex-1 cursor-pointer"
              >
                <Save className="h-3.5 w-3.5" />
                {isSaved ? 'Saved to Workspace' : 'Save Answer'}
              </Button>
            )}
            {onEscalate && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onEscalate}
                className="flex-1 text-status-danger hover:bg-rose-50/80 cursor-pointer"
              >
                <XCircle className="h-3.5 w-3.5" />
                Escalate to Lead
              </Button>
            )}
          </div>
        )}
      </div>
    );
  }

  return null;
}

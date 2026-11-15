// EvidenceCard.tsx - Evidence/citation card

interface EvidenceCardProps {
  evidence: {
    id: string;
    sourceId: string;
    documentTitle: string;
    snippet: string;
    contentSection: string;
    citationUrl: string;
    confidenceScore: number;
    isPrimary: boolean;
    isConflicting: boolean;
    sourceOrganization: string;
    evidenceStatus: 'verified' | 'partial' | 'missing' | 'conflicting';
  };
  index: number;
}

export function EvidenceCard({ evidence, index }: EvidenceCardProps) {
  const snippetLines = evidence.snippet.split('\n').filter((l) => l.trim());
  const isConflicting = evidence.isConflicting;
  const confidencePercent = Math.round(evidence.confidenceScore * 100);

  return (
    <div
      className={`rounded-lg border p-4 transition-colors ${
        isConflicting
          ? 'bg-amber-50 border-amber-200'
          : 'bg-white border-border'
      }`}
    >
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-2 min-w-0">
          <div
            className={`flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center text-sm font-semibold ${
              isConflicting
                ? 'bg-amber-100 text-amber-800'
                : evidence.isPrimary
                ? 'bg-accent-light text-accent-dark'
                : 'bg-border-subtle text-text-muted'
            }`}
          >
            {index + 1}
          </div>
          <div className="min-w-0">
            <p className="font-medium text-text truncate">{evidence.documentTitle}</p>
            <p className="text-xs text-text-muted truncate">{evidence.sourceOrganization}</p>
          </div>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          {isConflicting && (
            <span className="text-xs font-semibold text-amber-700 bg-amber-100 px-2 py-0.5 rounded-full">
              Conflicting
            </span>
          )}
          <span className="text-xs font-mono text-text-muted">{confidencePercent}%</span>
        </div>
      </div>

      <p className="text-sm text-text-muted leading-relaxed mb-3">{snippetLines.join('\n')}</p>

      <div className="flex flex-wrap items-center gap-3 text-xs text-text-muted">
        <span className="inline-flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-status-neutral-soft"></span>
          {evidence.contentSection}
        </span>
        {evidence.citationUrl && (
          <a
            href={evidence.citationUrl}
            className="text-accent-hover underline underline-offset-2"
            target="_blank"
            rel="noopener noreferrer"
          >
            View source
          </a>
        )}
      </div>
    </div>
  );
}

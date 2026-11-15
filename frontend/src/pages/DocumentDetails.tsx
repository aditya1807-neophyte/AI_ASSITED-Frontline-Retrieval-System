import { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { Clock, Download, ArrowLeft, Star, Sparkles, Database, Layers, CheckCircle } from 'lucide-react';
import { Card, Button, Badge, LoadingSkeleton } from '@/components/ui';
import api from '@/services/api';

// Demo fallback data
const fallbackDoc = {
  id: 'doc-001',
  title: 'Standard Operating Procedure: Field Equipment Calibration',
  content: `This SOP defines the standardized process for calibrating all field measurement equipment. The procedure includes:

1. Pre-calibration checks - verify equipment is clean and undamaged
2. Calibration procedure - use certified reference standards for all measurements
3. Post-calibration verification - confirm accuracy within acceptable tolerances
4. Documentation - record all results and update the calibration log

All equipment must be calibrated quarterly. Equipment requiring immediate calibration must be tagged and removed from service.

Reference standards must be calibrated annually by an ISO 17025 accredited laboratory.`,
  source_organization: 'Field Operations Division',
  document_type: 'SOP',
  topic: 'Operations',
  version: '3.2',
  document_status: 'active',
  effective_date: '2026-06-15',
  file_size: 245000,
  uploaded_at: '2026-06-20T10:30:00Z',
  num_pages: 4,
  word_count: 320,
  chunks: [
    { chunk_sequence: 1, section_heading: 'Section 1: Pre-checks', page_reference: '1', extracted_text: 'Pre-calibration checks - verify equipment is clean and undamaged.' },
    { chunk_sequence: 2, section_heading: 'Section 2: Calibration Process', page_reference: '2', extracted_text: 'Calibration procedure - use certified reference standards for all measurements.' },
  ],
};

export function DocumentDetails() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [document, setDocument] = useState<any | null>(null);
  const [contentData, setContentData] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaved, setIsSaved] = useState<boolean>(false);

  useEffect(() => {
    async function loadDocument() {
      setIsLoading(true);
      try {
        if (!id || id === 'doc-001') {
          setDocument(fallbackDoc);
          setContentData(fallbackDoc);
          setIsLoading(false);
          return;
        }

        // Fetch document metadata & content from SQLite backend
        const [metaRes, contentRes] = await Promise.all([
          api.get(`/documents/${id}`).catch(() => null),
          api.get(`/documents/${id}/content`).catch(() => null),
        ]);

        if (metaRes && metaRes.data) {
          setDocument(metaRes.data);
          setContentData(contentRes?.data || null);
        } else {
          setDocument(fallbackDoc);
          setContentData(fallbackDoc);
        }
      } catch (err) {
        console.warn('Could not load document details:', err);
        setDocument(fallbackDoc);
      } finally {
        setIsLoading(false);
      }
    }

    loadDocument();
  }, [id]);

  const doc = document || fallbackDoc;
  const chunks = contentData?.chunks || doc.chunks || [];
  const fullContent = contentData?.content || doc.content || doc.description || '';

  const handleDownload = () => {
    if (doc.id && typeof doc.id === 'number') {
      window.open(`http://localhost:8000/api/documents/${doc.id}/download`, '_blank');
    } else {
      const blob = new Blob([fullContent], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = window.document.createElement('a');
      a.href = url;
      a.download = doc.original_filename || `${doc.title.toLowerCase().replace(/\s+/g, '_')}.txt`;
      a.click();
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-10 w-48 bg-white/40 rounded-xl animate-pulse" />
        <LoadingSkeleton variant="card" count={3} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Breadcrumb & Header */}
      <div className="flex items-center gap-3">
        <Link
          className="p-2.5 rounded-xl bg-white/60 hover:bg-white/85 backdrop-blur-md border border-white/75 text-slate-700 transition-all cursor-pointer shadow-2xs"
          to="/library"
          aria-label="Back to knowledge library"
        >
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div>
          <h1 className="text-2xl sm:text-3xl font-heading font-bold text-[#101410]">
            Document <span className="font-calligraphy font-normal italic text-[#175A67] text-3xl sm:text-4xl pl-1 inline-block">Details</span>
          </h1>
          <p className="font-heading italic text-xs sm:text-sm text-[#263B40] font-medium truncate max-w-xl">
            {doc.title}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content Column */}
        <div className="lg:col-span-2 space-y-6">
          <Card padding="lg" className="border-white/80 shadow-[0_8px_32px_0_rgba(15,23,42,0.10)]">
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="flex flex-wrap items-center gap-1.5 mb-2">
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-[#175A67] text-[#FAF8F5]">
                    {doc.document_type || 'SOP'}
                  </span>
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-white border border-[#175A67]/30 text-[#175A67]">
                    Role: {doc.intended_role ? doc.intended_role.replace(/_/g, ' ') : 'All Roles'}
                  </span>
                  {doc.topic && (
                    <span className="text-[10px] px-2 py-0.5 rounded-md bg-stone-100 text-stone-700">
                      #{doc.topic}
                    </span>
                  )}
                </div>
                <h2 className="text-xl sm:text-2xl font-heading font-bold text-slate-900 leading-snug">
                  {doc.title}
                </h2>
                <p className="text-xs sm:text-sm text-slate-600 mt-1 font-medium">
                  {doc.source_organization || 'Frontline Operations & Safety'}
                </p>
              </div>
              <Badge tone={doc.document_status === 'active' ? 'success' : 'warning'} size="md">
                {doc.document_status || 'active'}
              </Badge>
            </div>

            {/* Quick Metadata Pill Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3.5 mt-5 p-3.5 rounded-2xl bg-white/50 backdrop-blur-sm border border-white/70">
              <div>
                <p className="text-xs text-slate-500 font-medium">Version</p>
                <p className="text-sm font-semibold text-slate-900 mt-0.5">v{doc.version || '1.0'}</p>
              </div>
              <div>
                <p className="text-xs text-slate-500 font-medium">Document Type</p>
                <p className="text-sm font-semibold text-slate-900 mt-0.5">{doc.document_type || 'SOP'}</p>
              </div>
              <div>
                <p className="text-xs text-slate-500 font-medium">Pages / Words</p>
                <p className="text-sm font-semibold text-slate-900 mt-0.5">
                  {doc.num_pages || 1} pgs &middot; {doc.word_count || 0} w
                </p>
              </div>
              <div>
                <p className="text-xs text-slate-500 font-medium">Database Store</p>
                <p className="text-sm font-semibold text-emerald-800 mt-0.5 flex items-center gap-1">
                  <Database className="h-3 w-3" /> frontline.db
                </p>
              </div>
            </div>

            {/* Timestamps and Actions */}
            <div className="flex flex-wrap items-center justify-between gap-3 mt-4 pt-3 border-t border-slate-200/70 text-xs text-slate-600">
              <div className="flex items-center gap-2">
                <Clock className="h-3.5 w-3.5 text-slate-500" />
                <span>Indexed in DB: {doc.uploaded_at ? new Date(doc.uploaded_at).toLocaleDateString() : 'Active'}</span>
              </div>

              <div className="flex items-center gap-2">
                <Button variant="primary" size="sm" onClick={handleDownload} className="bg-[#175A67] hover:bg-[#0F454F] text-xs">
                  <Download className="h-3.5 w-3.5" />
                  Download File
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setIsSaved(!isSaved)}
                  className={`text-xs ${isSaved ? 'text-emerald-700 bg-emerald-50 border-emerald-200' : ''}`}
                >
                  {isSaved ? <CheckCircle className="h-3.5 w-3.5" /> : <Star className="h-3.5 w-3.5" />}
                  {isSaved ? 'Bookmarked' : 'Save'}
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => navigate(`/ask?q=${encodeURIComponent(`What is the step-by-step procedure in ${doc.title}?`)}`)}
                  className="bg-[#175A67] hover:bg-[#0F454F] text-xs"
                >
                  <Sparkles className="h-3.5 w-3.5" />
                  Ask AI
                </Button>
              </div>
            </div>
          </Card>

          {/* Extracted Document Text */}
          <Card padding="lg" className="border-white/80 shadow-[0_8px_32px_0_rgba(15,23,42,0.10)]">
            <h3 className="section-heading text-xl font-heading font-bold text-[#101410]">
              Document <span className="font-calligraphy font-normal italic text-[#175A67] text-2xl pl-1 inline-block">Content</span>
            </h3>
            <p className="font-heading italic text-xs sm:text-sm text-[#263B40] mb-3">
              Full text extracted and processed into the frontline retrieval repository.
            </p>
            <div className="p-4 rounded-2xl bg-white/70 backdrop-blur-sm border border-white/80 font-sans text-xs leading-relaxed text-slate-800 whitespace-pre-wrap max-h-96 overflow-y-auto">
              {fullContent || 'No extracted text content available for this document.'}
            </div>
          </Card>

          {/* Structured Indexed Chunks */}
          {chunks.length > 0 && (
            <Card padding="lg" className="border-white/80 shadow-[0_8px_32px_0_rgba(15,23,42,0.10)]">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h3 className="section-heading text-xl font-heading font-bold text-[#101410]">
                    Indexed <span className="font-calligraphy font-normal italic text-[#175A67] text-2xl pl-1 inline-block">Chunks</span>
                  </h3>
                  <p className="font-heading italic text-xs sm:text-sm text-[#263B40]">
                    {chunks.length} granular passages indexed for hybrid keyword & semantic RAG retrieval
                  </p>
                </div>
                <Badge tone="neutral" size="sm">
                  <Layers className="h-3 w-3 mr-1" /> {chunks.length} Chunks
                </Badge>
              </div>

              <div className="space-y-2.5">
                {chunks.map((chunk: any, i: number) => (
                  <div
                    key={i}
                    className="p-3 rounded-xl bg-white/60 hover:bg-white/85 border border-white/75 transition-all text-xs"
                  >
                    <div className="flex items-center justify-between gap-2 mb-1 text-[11px] font-semibold text-[#175A67]">
                      <span>{chunk.section_heading || `Chunk #${chunk.chunk_sequence || i + 1}`}</span>
                      <span className="font-mono text-slate-400">Page {chunk.page_reference || '1'}</span>
                    </div>
                    <p className="text-slate-800 leading-relaxed font-mono text-[11px] bg-white/50 p-2 rounded-lg border border-slate-100">
                      {chunk.extracted_text || chunk.content || ''}
                    </p>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>

        {/* Sidebar Metadata Column */}
        <div className="space-y-6">
          <Card padding="lg" className="border-white/80 shadow-[0_8px_32px_0_rgba(15,23,42,0.10)]">
            <h3 className="section-heading text-xl font-heading font-bold text-[#101410] mb-3">
              Document <span className="font-calligraphy font-normal italic text-[#175A67] text-2xl pl-1 inline-block">Metadata</span>
            </h3>
            <dl className="space-y-3 text-xs">
              <div className="flex justify-between items-center py-1.5 border-b border-slate-200/50">
                <dt className="text-slate-500 font-medium">Database ID</dt>
                <dd className="font-mono font-bold text-slate-900">#{doc.id}</dd>
              </div>
              <div className="flex justify-between items-center py-1.5 border-b border-slate-200/50">
                <dt className="text-slate-500 font-medium">Original Filename</dt>
                <dd className="font-mono text-slate-800 truncate max-w-[160px]">{doc.original_filename || 'stored.pdf'}</dd>
              </div>
              <div className="flex justify-between items-center py-1.5 border-b border-slate-200/50">
                <dt className="text-slate-500 font-medium">Organization</dt>
                <dd className="font-semibold text-slate-800 truncate max-w-[160px] text-right">{doc.source_organization || 'Frontline Operations'}</dd>
              </div>
              <div className="flex justify-between items-center py-1.5 border-b border-slate-200/50">
                <dt className="text-slate-500 font-medium">Target Role</dt>
                <dd className="capitalize font-semibold text-[#175A67]">{doc.intended_role?.replace(/_/g, ' ') || 'All Roles'}</dd>
              </div>
              <div className="flex justify-between items-center py-1.5 border-b border-slate-200/50">
                <dt className="text-slate-500 font-medium">Topic / Category</dt>
                <dd className="font-semibold text-slate-800">#{doc.topic || 'operations'}</dd>
              </div>
              <div className="flex justify-between items-center py-1.5 border-b border-slate-200/50">
                <dt className="text-slate-500 font-medium">Version</dt>
                <dd className="font-mono text-slate-800">v{doc.version || '1.0'}</dd>
              </div>
              <div className="flex justify-between items-center py-1.5 border-b border-slate-200/50">
                <dt className="text-slate-500 font-medium">Processing Status</dt>
                <dd className="font-semibold text-emerald-700">{doc.processing_status || 'completed'}</dd>
              </div>
              <div className="flex justify-between items-center py-1.5">
                <dt className="text-slate-500 font-medium">File Size</dt>
                <dd className="font-mono text-slate-800">{doc.file_size ? `${(doc.file_size / 1024).toFixed(1)} KB` : 'N/A'}</dd>
              </div>
            </dl>
          </Card>

          {/* Quick RAG Assistant Card */}
          <Card padding="lg" className="border-white/80 shadow-[0_8px_32px_0_rgba(15,23,42,0.10)] bg-[#E2ECED]/30">
            <h3 className="section-heading text-lg font-heading font-bold text-[#101410] mb-2 flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-[#175A67]" />
              Frontline AI Assistant
            </h3>
            <p className="text-xs text-slate-600 mb-3">
              Need immediate answers regarding tolerances, LOTO rules, or steps in this procedure?
            </p>
            <Button
              variant="primary"
              className="w-full justify-center bg-[#175A67] hover:bg-[#0F454F] text-xs shadow-xs"
              onClick={() => navigate(`/ask?q=${encodeURIComponent(`What are the key safety requirements and procedure in ${doc.title}?`)}`)}
            >
              Ask AI About This Document
            </Button>
          </Card>
        </div>
      </div>
    </div>
  );
}

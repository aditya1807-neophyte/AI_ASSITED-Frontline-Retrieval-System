import React from 'react';
import { Star, Bookmark, FileText } from 'lucide-react';
import { Card, Badge } from '@/components/ui';
import type { Document } from '@/types/app';

// Demo saved items
const demoSavedDocuments: Document[] = [
  {
    id: 'doc-001',
    title: 'Standard Operating Procedure: Field Equipment Calibration',
    content: 'SOP-001 v3.2',
    sourceOrganization: 'Field Operations Division',
    documentType: 'SOP',
    category: 'Operations',
    version: '3.2',
    status: 'active',
    effectiveDate: '2026-06-15',
    size: 245000,
    uploadedAt: '2026-06-20T10:30:00Z',
    url: '#',
    uploadedByName: 'Senior Analyst',
  },
  {
    id: 'doc-002',
    title: 'Safety Protocol for Hazardous Materials Handling',
    content: 'Safety Protocol v2.1',
    sourceOrganization: 'Safety & Compliance Team',
    documentType: 'Policy',
    category: 'Safety',
    version: '2.1',
    status: 'active',
    effectiveDate: '2026-09-01',
    size: 187000,
    uploadedAt: '2026-09-05T08:15:00Z',
    url: '#',
    uploadedByName: 'Field Lead',
  },
  {
    id: 'ans-001',
    title: 'Calibration frequency for field equipment',
    content: 'Quarterly calibration required per SOP-001.',
    sourceOrganization: 'AI Answer',
    documentType: 'Answer',
    category: 'Summary',
    version: 'AI-1',
    status: 'active',
    effectiveDate: '2026-10-15',
    size: 2450,
    uploadedAt: '2026-10-15T09:30:00Z',
    url: '#',
    uploadedByName: 'AI Assistant',
  },
  {
    id: 'ans-002',
    title: 'PPE requirements for hazardous materials',
    content: 'Chemical-resistant gloves, goggles, flame-resistant clothing required.',
    sourceOrganization: 'AI Answer',
    documentType: 'Answer',
    category: 'Summary',
    version: 'AI-2',
    status: 'active',
    effectiveDate: '2026-10-14',
    size: 1870,
    uploadedAt: '2026-10-14T14:20:00Z',
    url: '#',
    uploadedByName: 'AI Assistant',
  },
];

// Demo saved answers
const demoSavedAnswers = [
  {
    id: 'ans-001',
    question: 'What is the calibration frequency for field equipment?',
    answer: 'Quarterly, per SOP-001. All equipment must use certified reference standards.',
    annotation: 'Answer saved by Jordan Diaz on Oct 15, 2026',
    createdAt: '2026-10-15T09:30:00Z',
  },
  {
    id: 'ans-002',
    question: 'What PPE is required for hazardous materials?',
    answer: 'Chemical-resistant gloves, safety goggles, and flame-resistant clothing.',
    annotation: 'Answer saved by Jordan Diaz on Oct 14, 2026',
    createdAt: '2026-10-14T14:20:00Z',
  },
];

export function SavedItems() {
  const [activeTab, setActiveTab] = React.useState<'documents' | 'answers'>('documents');

  return (
    <div className="space-y-6 sm:space-y-7">
      <div className="flex items-center gap-3.5 mb-6">
        <div className="h-12 w-12 rounded-2xl bg-amber-100/80 backdrop-blur-md flex items-center justify-center border border-amber-300 text-amber-800 shadow-2xs">
          <Star className="h-6 w-6" />
        </div>
        <div>
          <h1 className="text-3xl sm:text-4xl font-heading font-bold text-[#101410] tracking-tight leading-tight">
            Saved <span className="font-calligraphy font-normal italic text-[#175A67] text-4xl sm:text-5xl pl-1 inline-block">Items</span>
          </h1>
          <p className="font-heading italic text-sm text-[#263B40] mt-1 font-medium">Quick access to bookmarked documents and verified frontline answers.</p>
        </div>
      </div>

      {/* Tabs */}
      <Card padding="sm" className="border-white/85 shadow-[0_8px_32px_0_rgba(23,90,103,0.06)]">
        <div className="flex gap-2">
          <button
            className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all cursor-pointer ${
              activeTab === 'documents'
                ? 'bg-[#175A67] text-[#FAF8F5] shadow-sm'
                : 'text-[#4A5B5E] hover:text-[#101410] hover:bg-white/60'
            }`}
            onClick={() => setActiveTab('documents')}
          >
            <FileText className="h-4 w-4 inline mr-1.5" />
            Documents ({demoSavedDocuments.length})
          </button>
          <button
            className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all cursor-pointer ${
              activeTab === 'answers'
                ? 'bg-[#175A67] text-[#FAF8F5] shadow-sm'
                : 'text-[#4A5B5E] hover:text-[#101410] hover:bg-white/60'
            }`}
            onClick={() => setActiveTab('answers')}
          >
            <Bookmark className="h-4 w-4 inline mr-1.5" />
            Answers ({demoSavedAnswers.length})
          </button>
        </div>
      </Card>

      {/* Content */}
      <div className="space-y-6">
        {activeTab === 'documents' && (
          <Card padding="lg" className="border-white/85 shadow-[0_8px_32px_0_rgba(23,90,103,0.06)]">
            <div className="space-y-3">
              {demoSavedDocuments.map((doc) => (
                <div
                  key={doc.id}
                  className="flex items-center justify-between gap-4 p-4 rounded-2xl bg-white/55 hover:bg-white/85 backdrop-blur-md border border-white/70 hover:border-white/95 transition-all shadow-2xs"
                >
                  <div className="flex items-center gap-3.5 min-w-0 flex-1">
                    <div className="h-10 w-10 rounded-xl bg-[#E2ECED] flex items-center justify-center shrink-0 border border-[#175A67]/20 text-[#175A67] shadow-2xs">
                      <FileText className="h-5 w-5" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-semibold text-slate-900 truncate">{doc.title}</p>
                      <p className="text-xs text-slate-500 mt-0.5">{doc.documentType} &middot; {doc.sourceOrganization}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <Badge tone="success" size="sm">{doc.status}</Badge>
                    <span className="text-xs font-mono text-slate-500 bg-white/70 px-2 py-0.5 rounded-lg border border-white/80">v{doc.version}</span>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}

        {activeTab === 'answers' && (
          <Card padding="lg" className="border-white/80 shadow-[0_8px_32px_0_rgba(15,23,42,0.10)]">
            <div className="space-y-3">
              {demoSavedAnswers.map((answer) => (
                <div
                  key={answer.id}
                  className="p-4 rounded-2xl bg-white/55 hover:bg-white/85 backdrop-blur-md border border-white/70 hover:border-white/95 transition-all shadow-2xs"
                >
                  <div className="flex items-start gap-3.5">
                    <div className="h-10 w-10 rounded-xl bg-amber-100 flex items-center justify-center shrink-0 border border-amber-300 text-amber-800 shadow-2xs">
                      <Bookmark className="h-5 w-5" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-slate-900">{answer.question}</p>
                      <p className="text-xs sm:text-sm text-slate-700 mt-1 leading-relaxed bg-white/60 p-3 rounded-xl border border-white/80">{answer.answer}</p>
                      <p className="text-[11px] text-slate-500 mt-2 font-mono">{answer.annotation}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}

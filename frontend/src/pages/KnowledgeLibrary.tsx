import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  X,
  FileText,
  Search as SearchIcon,
  BookOpen,
  Sparkles,
  Upload,
  Eye,
  Download,
  ExternalLink,
} from 'lucide-react';
import {
  Card,
  CardHeader,
  SearchBar,
  Button,
  Pagination,
  EmptyState,
  LoadingSkeleton,
  Modal,
} from '@/components/ui';
import api from '@/services/api';

export function KnowledgeLibrary() {
  const navigate = useNavigate();
  const [documents, setDocuments] = useState<any[]>([]);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(true);

  // Filters & Pagination
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRole, setSelectedRole] = useState('');
  const [selectedTopic, setSelectedTopic] = useState('');
  const [selectedDocType, setSelectedDocType] = useState('');
  const [sortBy, setSortBy] = useState('recent');
  const [page, setPage] = useState(1);
  const pageSize = 8;

  // Document Inspection Modal
  const [inspectDoc, setInspectDoc] = useState<any | null>(null);

  const fetchDocuments = async () => {
    setIsLoading(true);
    try {
      const params: any = {
        page,
        page_size: pageSize,
      };
      if (searchQuery.trim()) params.search = searchQuery.trim();
      if (selectedTopic) params.topic = selectedTopic;
      if (selectedDocType) params.doc_type = selectedDocType;

      const res = await api.get('/documents/', { params });
      setDocuments(res.data.items || []);
      setTotalCount(res.data.total || 0);
    } catch (err) {
      console.error('Error fetching documents from backend:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [page, selectedTopic, selectedDocType]);

  const handleSearchSubmit = () => {
    setPage(1);
    fetchDocuments();
  };

  // Client-side role filter for granular refinement
  const displayedDocs = documents.filter((doc) => {
    if (!selectedRole) return true;
    return (
      doc.intended_role === selectedRole ||
      doc.role === selectedRole ||
      (doc.intended_role && doc.intended_role.toLowerCase().includes(selectedRole.toLowerCase()))
    );
  });

  const totalPages = Math.max(1, Math.ceil(totalCount / pageSize));

  return (
    <div className="space-y-6 sm:space-y-7">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="h-12 w-12 rounded-2xl bg-[#E2ECED] backdrop-blur-md flex items-center justify-center border border-[#175A67]/20 text-[#175A67] shadow-2xs">
            <BookOpen className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-3xl sm:text-4xl font-heading font-bold text-[#101410] tracking-tight leading-tight">
              Knowledge <span className="font-calligraphy font-normal italic text-[#175A67] text-4xl sm:text-5xl pl-1 inline-block">Repository</span>
            </h1>
            <p className="font-heading italic text-sm text-[#263B40] mt-1 font-medium">
              Structured frontline SOPs, procedures, and forms with role, topic, and source metadata.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <span className="px-3 py-1.5 rounded-xl bg-white/80 border border-white/90 text-xs font-bold text-[#175A67] shadow-2xs">
            {totalCount} Verified Frontline Docs
          </span>
          <Button
            variant="primary"
            size="sm"
            onClick={() => navigate('/documents?upload=true')}
            className="bg-[#175A67] hover:bg-[#0F454F] shadow-2xs text-xs"
          >
            <Upload className="h-3.5 w-3.5" />
            Upload Document
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Filters Sidebar */}
        <Card padding="lg" className="lg:col-span-1 border-white/80 shadow-[0_8px_32px_0_rgba(15,23,42,0.10)]">
          <CardHeader
            title="Metadata Filters"
            subtitle="Filter by role, topic, or document type"
            action={
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setSearchQuery('');
                  setSelectedRole('');
                  setSelectedTopic('');
                  setSelectedDocType('');
                  setPage(1);
                }}
              >
                <X className="h-4 w-4" />
              </Button>
            }
          />

          <div className="space-y-4">
            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-600 block mb-1.5">
                Keyword Search
              </label>
              <div className="flex gap-1.5">
                <SearchBar
                  value={searchQuery}
                  onChange={setSearchQuery}
                  placeholder="Search titles & tags..."
                  showClear={!!searchQuery}
                />
                <Button variant="secondary" size="sm" onClick={handleSearchSubmit} className="cursor-pointer">
                  Go
                </Button>
              </div>
            </div>

            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-600 block mb-1.5">
                Frontline Role
              </label>
              <select
                className="glass-input w-full px-3.5 py-2.5 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-[#175A67]"
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
              >
                <option value="">All Roles</option>
                <option value="field_technician">Field Technician</option>
                <option value="safety_officer">Safety Officer</option>
                <option value="maintenance_engineer">Maintenance Engineer</option>
                <option value="site_supervisor">Site Supervisor</option>
                <option value="operations_analyst">Operations Analyst</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-600 block mb-1.5">
                Topic
              </label>
              <select
                className="glass-input w-full px-3.5 py-2.5 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-[#175A67]"
                value={selectedTopic}
                onChange={(e) => {
                  setSelectedTopic(e.target.value);
                  setPage(1);
                }}
              >
                <option value="">All Topics</option>
                <option value="calibration">Calibration & Sensors</option>
                <option value="hazardous_materials">Hazardous Materials</option>
                <option value="electrical_safety">Electrical & LOTO</option>
                <option value="confined_space">Confined Space</option>
                <option value="emergency_response">Emergency Response</option>
                <option value="mechanical">Mechanical & Valves</option>
                <option value="telematics">Telematics & Lone Worker</option>
                <option value="operations">Shift & Logs</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-600 block mb-1.5">
                Document Type
              </label>
              <select
                className="glass-input w-full px-3.5 py-2.5 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-[#175A67]"
                value={selectedDocType}
                onChange={(e) => {
                  setSelectedDocType(e.target.value);
                  setPage(1);
                }}
              >
                <option value="">All Types</option>
                <option value="SOP">SOP (Standard Operating Procedure)</option>
                <option value="Policy">Policy</option>
                <option value="Form">Form & Checklist</option>
                <option value="Procedure">Procedure</option>
                <option value="Standard">Standard</option>
              </select>
            </div>

            <Button
              variant="secondary"
              size="sm"
              className="w-full mt-2"
              onClick={() => {
                setSearchQuery('');
                setSelectedRole('');
                setSelectedTopic('');
                setSelectedDocType('');
                setPage(1);
              }}
            >
              Reset Filters
            </Button>
          </div>
        </Card>

        {/* Document list */}
        <Card padding="lg" className="lg:col-span-3 border-white/80 shadow-[0_8px_32px_0_rgba(15,23,42,0.10)]">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-slate-900">
              Showing {displayedDocs.length} documents (Total indexed: {totalCount})
            </h3>
            <div className="flex items-center gap-2">
              <label className="text-xs font-medium text-slate-600">Sort:</label>
              <select
                className="glass-input px-3 py-1.5 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-[#175A67]"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
              >
                <option value="recent">Recently Added</option>
                <option value="title">Title (A-Z)</option>
              </select>
            </div>
          </div>

          {isLoading ? (
            <LoadingSkeleton variant="table" count={6} />
          ) : displayedDocs.length === 0 ? (
            <EmptyState
              icon={<SearchIcon className="h-8 w-8 text-slate-400" />}
              title="No documents found"
              description="No documents match your active role or filter settings."
              action={
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => {
                    setSearchQuery('');
                    setSelectedRole('');
                    setSelectedTopic('');
                    setSelectedDocType('');
                    setPage(1);
                  }}
                >
                  Clear all filters
                </Button>
              }
            />
          ) : (
            <div className="space-y-3">
              {displayedDocs.map((doc: any) => (
                <div
                  key={doc.id}
                  onClick={() => setInspectDoc(doc)}
                  className="w-full flex flex-col sm:flex-row sm:items-start justify-between gap-3 p-4 rounded-2xl bg-white/60 hover:bg-white/90 backdrop-blur-md border border-white/80 hover:border-[#175A67]/30 shadow-2xs hover:shadow-[0_8px_24px_rgba(23,90,103,0.08)] transition-all cursor-pointer group"
                >
                  <div className="flex items-start gap-3.5 min-w-0 flex-1">
                    <div className="h-10 w-10 rounded-xl bg-[#E2ECED] flex items-center justify-center shrink-0 border border-[#175A67]/20 text-[#175A67] shadow-2xs mt-0.5">
                      <FileText className="h-5 w-5" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex flex-wrap items-center gap-1.5 mb-1">
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-[#175A67] text-[#FAF8F5]">
                          {doc.document_type || 'SOP'}
                        </span>
                        {doc.intended_role && (
                          <span className="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-white border border-[#175A67]/30 text-[#175A67]">
                            Role: {doc.intended_role.replace(/_/g, ' ')}
                          </span>
                        )}
                        {doc.topic && (
                          <span className="text-[10px] px-2 py-0.5 rounded-md bg-stone-100 text-stone-700">
                            #{doc.topic}
                          </span>
                        )}
                      </div>
                      <p className="text-sm font-bold text-slate-900 group-hover:text-[#175A67] transition-colors">
                        {doc.title}
                      </p>
                      <p className="text-xs text-slate-600 line-clamp-2 mt-1">
                        {doc.description || 'Verified frontline operating document.'}
                      </p>
                      <p className="text-[11px] text-slate-500 mt-2 font-medium">
                        Org: {doc.source_organization || 'Frontline Operations'} &middot; v{doc.version || '1.0'} &middot; {doc.num_pages ? `${doc.num_pages} pages` : 'Indexed'}
                      </p>
                    </div>
                  </div>

                  <div className="flex sm:flex-col items-end justify-between sm:justify-start gap-2 shrink-0 pt-2 sm:pt-0">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200">
                      {doc.document_status || 'active'}
                    </span>
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/library/${doc.id}`);
                        }}
                        className="inline-flex items-center gap-1 text-xs font-semibold text-slate-700 hover:text-[#175A67] px-2 py-1 rounded-lg hover:bg-white/80 transition-colors"
                        title="View full document"
                      >
                        <Eye className="h-3 w-3" />
                        View
                      </button>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/ask?q=${encodeURIComponent(`What is the procedure in ${doc.title}?`)}`);
                        }}
                        className="inline-flex items-center gap-1 text-xs font-semibold text-[#175A67] hover:underline px-2 py-1"
                      >
                        <Sparkles className="h-3 w-3" />
                        Ask AI
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="mt-5">
            <Pagination
              page={page}
              pageSize={pageSize}
              total={totalCount}
              onPageChange={(p) => setPage(p)}
              onPageSizeChange={() => setPage(1)}
              totalPages={totalPages}
            />
          </div>
        </Card>
      </div>

      {/* Document Inspection Modal */}
      {inspectDoc && (
        <Modal
          isOpen={!!inspectDoc}
          onClose={() => setInspectDoc(null)}
          title={inspectDoc.title}
          size="lg"
        >
          <div className="space-y-4 py-2">
            <div className="p-3.5 rounded-xl bg-[#E2ECED]/50 border border-[#175A67]/20 flex flex-wrap gap-2 text-xs">
              <span className="font-semibold text-slate-700">Type:</span>
              <strong className="text-[#175A67]">{inspectDoc.document_type}</strong>
              <span className="text-slate-400">|</span>
              <span className="font-semibold text-slate-700">Target Role:</span>
              <strong className="text-[#175A67]">{inspectDoc.intended_role || 'All roles'}</strong>
              <span className="text-slate-400">|</span>
              <span className="font-semibold text-slate-700">Topic:</span>
              <strong className="text-[#175A67]">{inspectDoc.topic}</strong>
              <span className="text-slate-400">|</span>
              <span className="font-semibold text-slate-700">Version:</span>
              <strong>v{inspectDoc.version}</strong>
            </div>

            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                Document Description & Scope
              </h4>
              <p className="text-xs sm:text-sm text-slate-800 leading-relaxed bg-white/70 p-3 rounded-xl border border-white/80">
                {inspectDoc.description || 'No extended summary available.'}
              </p>
            </div>

            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                Source Metadata
              </h4>
              <div className="grid grid-cols-2 gap-2 text-xs bg-white/60 p-3 rounded-xl border border-white/80">
                <div>
                  <span className="text-slate-500 block">Organization:</span>
                  <span className="font-semibold text-slate-800">{inspectDoc.source_organization}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Original File:</span>
                  <span className="font-mono text-slate-800">{inspectDoc.original_filename || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Page Count:</span>
                  <span className="text-slate-800">{inspectDoc.num_pages || 'N/A'} pages</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Processing Status:</span>
                  <span className="text-emerald-700 font-semibold">{inspectDoc.processing_status || 'completed'}</span>
                </div>
              </div>
            </div>

            {inspectDoc.tags && inspectDoc.tags.length > 0 && (
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                  Indexed Tags
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {inspectDoc.tags.map((tag: string, i: number) => (
                    <span
                      key={i}
                      className="text-[11px] px-2.5 py-1 rounded-lg bg-white/80 text-[#175A67] border border-[#175A67]/20 font-medium"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="flex flex-wrap justify-between items-center gap-2 pt-3 border-t border-slate-200">
              <Button
                variant="ghost"
                onClick={() => setInspectDoc(null)}
              >
                Close
              </Button>
              <div className="flex items-center gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => {
                    window.open(`http://localhost:8000/api/documents/${inspectDoc.id}/download`, '_blank');
                  }}
                  className="text-xs"
                >
                  <Download className="h-3.5 w-3.5" />
                  Download
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => {
                    const id = inspectDoc.id;
                    setInspectDoc(null);
                    navigate(`/library/${id}`);
                  }}
                  className="text-xs text-[#175A67] border-[#175A67]/30"
                >
                  <ExternalLink className="h-3.5 w-3.5" />
                  Full View
                </Button>
                <Button
                  variant="primary"
                  onClick={() => {
                    const q = `What is the step-by-step procedure in ${inspectDoc.title}?`;
                    setInspectDoc(null);
                    navigate(`/ask?q=${encodeURIComponent(q)}`);
                  }}
                  className="bg-[#175A67] hover:bg-[#0F454F] text-xs"
                >
                  <Sparkles className="h-3.5 w-3.5" />
                  Ask AI
                </Button>
              </div>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}

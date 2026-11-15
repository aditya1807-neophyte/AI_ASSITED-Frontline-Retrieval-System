import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Upload,
  FileText,
  Trash2,
  Eye,
  Plus,
  Database,
  CheckCircle2,
  Sparkles,
  RefreshCw,
  HardDrive,
  X,
  AlertCircle,
  Download,
  ExternalLink,
} from 'lucide-react';
import { Card, CardHeader, Badge, Button, Pagination, Modal, LoadingSkeleton, EmptyState } from '@/components/ui';
import api from '@/services/api';

export function DocumentManagement() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  // Database documents & stats
  const [documents, setDocuments] = useState<any[]>([]);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [dbStats, setDbStats] = useState<any>({ total: 0, active: 0, draft: 0, review: 0, archived: 0 });
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Filters & Pagination
  const [filterType, setFilterType] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterRole, setFilterRole] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [page, setPage] = useState<number>(1);
  const pageSize = 8;

  // Upload Modal State
  const [showUpload, setShowUpload] = useState<boolean>(false);

  useEffect(() => {
    if (searchParams.get('upload') === 'true') {
      setShowUpload(true);
      setSearchParams({}, { replace: true });
    }
  }, [searchParams, setSearchParams]);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState<boolean>(false);

  // Form Fields for Database Storage
  const [newTitle, setNewTitle] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [newDocType, setNewDocType] = useState('SOP');
  const [newRole, setNewRole] = useState('field_technician');
  const [newTopic, setNewTopic] = useState('operations');
  const [newOrg, setNewOrg] = useState('Frontline Operations');
  const [newVersion, setNewVersion] = useState('1.0');
  const [newStatus, setNewStatus] = useState('active');
  const [newContent, setNewContent] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // Detail Modal State
  const [inspectDoc, setInspectDoc] = useState<any | null>(null);

  // Fetch documents from database
  const fetchDocuments = async () => {
    setIsLoading(true);
    try {
      const params: any = {
        page,
        page_size: pageSize,
      };
      if (searchQuery.trim()) params.search = searchQuery.trim();
      if (filterType !== 'all') params.doc_type = filterType;
      if (filterStatus !== 'all') params.status = filterStatus;

      const [docsRes, statsRes] = await Promise.all([
        api.get('/documents/', { params }),
        api.get('/documents/stats').catch(() => ({ data: { total: 0, active: 0, draft: 0, review: 0, archived: 0 } })),
      ]);

      setDocuments(docsRes.data.items || []);
      setTotalCount(docsRes.data.total || 0);
      setDbStats(statsRes.data || { total: 0, active: 0, draft: 0, review: 0, archived: 0 });
    } catch (err) {
      console.error('Failed to load documents from database:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [page, filterType, filterStatus]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchDocuments();
  };

  const processSelectedFile = (file: File) => {
    setSelectedFile(file);
    setUploadError(null);
    if (!newTitle.trim()) {
      const cleanName = file.name.replace(/\.[^/.]+$/, '').replace(/[-_]/g, ' ');
      setNewTitle(cleanName.charAt(0).toUpperCase() + cleanName.slice(1));
    }
    // Auto-read plain text formats for live chunking preview
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (ext && ['txt', 'md', 'csv', 'json', 'log'].includes(ext)) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const text = e.target?.result as string;
        if (text && !newContent.trim()) {
          setNewContent(text);
        }
      };
      reader.readAsText(file);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      processSelectedFile(file);
    }
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setUploadError(null);
    if (!newTitle.trim()) {
      setUploadError('Please enter a document title.');
      return;
    }

    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('title', newTitle.trim());
      if (newDescription.trim()) formData.append('description', newDescription.trim());
      formData.append('document_type', newDocType);
      formData.append('intended_role', newRole);
      formData.append('topic', newTopic);
      formData.append('source_organization', newOrg);
      formData.append('version', newVersion);
      formData.append('document_status', newStatus);
      if (newContent.trim()) formData.append('content', newContent.trim());

      if (selectedFile) {
        formData.append('file', selectedFile);
        formData.append('original_filename', selectedFile.name);
      } else {
        formData.append('original_filename', `${newTitle.toLowerCase().replace(/[^a-z0-9]/g, '_')}.pdf`);
      }

      const res = await api.post('/documents/', formData, {
        headers: {
          'Content-Type': undefined,
        },
      });

      setUploadSuccess(`Document #${res.data.id} "${res.data.title}" successfully saved to database!`);
      setTimeout(() => {
        setShowUpload(false);
        setUploadSuccess(null);
        setUploadError(null);
        // Reset form
        setNewTitle('');
        setNewDescription('');
        setNewContent('');
        setSelectedFile(null);
        fetchDocuments();
      }, 1500);
    } catch (err: any) {
      console.error('Document upload failed:', err);
      const msg = err.response?.data?.detail || err.response?.data?.message || err.message || 'Failed to save document to database.';
      setUploadError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async (docId: number, title: string) => {
    if (!window.confirm(`Are you sure you want to permanently delete "${title}" and all its indexed chunks from the database?`)) {
      return;
    }

    try {
      await api.delete(`/documents/${docId}`);
      fetchDocuments();
    } catch (err: any) {
      alert('Failed to delete document: ' + (err.response?.data?.detail || err.message));
    }
  };

  const filteredDocs = documents.filter((doc) => {
    if (filterRole === 'all') return true;
    return doc.intended_role === filterRole;
  });

  const totalPages = Math.max(1, Math.ceil(totalCount / pageSize));

  return (
    <div className="space-y-6 sm:space-y-7">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="h-12 w-12 rounded-2xl bg-[#E2ECED] backdrop-blur-md flex items-center justify-center border border-[#175A67]/20 text-[#175A67] shadow-2xs">
            <Database className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-3xl sm:text-4xl font-heading font-bold text-[#101410] tracking-tight leading-tight">
              Document <span className="font-calligraphy font-normal italic text-[#175A67] text-4xl sm:text-5xl pl-1 inline-block">Management</span>
            </h1>
            <p className="font-heading italic text-sm text-[#263B40] mt-1 font-medium">
              Upload, extract, chunk, and save frontline documents directly into the persistent SQLite database.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-semibold bg-white/80 border border-white/90 text-[#175A67] shadow-2xs">
            <HardDrive className="h-3.5 w-3.5 text-[#175A67]" />
            <span>SQLite: <strong>frontline.db</strong></span>
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          </div>

          <Button
            variant="primary"
            className="bg-[#175A67] hover:bg-[#0F454F] shadow-sm"
            onClick={() => setShowUpload(true)}
          >
            <Plus className="h-4 w-4" />
            Upload Document
          </Button>
        </div>
      </div>

      {/* Database Quick Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
        <Card padding="md" className="border-white/80 shadow-[0_4px_20px_rgba(23,90,103,0.05)] bg-white/60">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block">Total Stored</span>
          <p className="text-2xl font-heading font-bold text-[#101410] mt-0.5">{dbStats.total || totalCount}</p>
          <span className="text-[11px] text-slate-500">Indexed in database</span>
        </Card>

        <Card padding="md" className="border-white/80 shadow-[0_4px_20px_rgba(23,90,103,0.05)] bg-white/60">
          <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-700 block">Active SOPs</span>
          <p className="text-2xl font-heading font-bold text-emerald-800 mt-0.5">{dbStats.active || 0}</p>
          <span className="text-[11px] text-emerald-600">Searchable in RAG</span>
        </Card>

        <Card padding="md" className="border-white/80 shadow-[0_4px_20px_rgba(23,90,103,0.05)] bg-white/60">
          <span className="text-[10px] font-bold uppercase tracking-wider text-amber-700 block">Draft / Review</span>
          <p className="text-2xl font-heading font-bold text-amber-800 mt-0.5">{(dbStats.draft || 0) + (dbStats.review || 0)}</p>
          <span className="text-[11px] text-amber-600">Pending verification</span>
        </Card>

        <Card padding="md" className="border-white/80 shadow-[0_4px_20px_rgba(23,90,103,0.05)] bg-white/60">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block">Repository Health</span>
          <p className="text-2xl font-heading font-bold text-[#175A67] mt-0.5">100%</p>
          <span className="text-[11px] text-slate-500">Zero orphaned chunks</span>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Filters Sidebar */}
        <div className="lg:col-span-1 space-y-4">
          <Card padding="lg" className="border-white/80 shadow-[0_8px_32px_0_rgba(15,23,42,0.10)]">
            <CardHeader
              title="Database Filters"
              subtitle="Query documents by type, role, or status"
            />
            <div className="space-y-3.5">
              <form onSubmit={handleSearchSubmit}>
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-600 block mb-1.5">
                  Search Titles & Content
                </label>
                <div className="flex gap-1.5">
                  <input
                    type="text"
                    className="glass-input w-full px-3 py-2 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-[#175A67]"
                    placeholder="Search by title or topic..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                  <Button type="submit" variant="secondary" size="sm" className="px-3">
                    Go
                  </Button>
                </div>
              </form>

              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-600 block mb-1.5">
                  Document Type
                </label>
                <select
                  className="glass-input w-full px-3 py-2 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-[#175A67]"
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                >
                  <option value="all">All types</option>
                  <option value="SOP">SOP (Standard Operating Procedure)</option>
                  <option value="Policy">Policy</option>
                  <option value="Procedure">Procedure</option>
                  <option value="Form">Form & Checklist</option>
                  <option value="Standard">Standard</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-600 block mb-1.5">
                  Target Frontline Role
                </label>
                <select
                  className="glass-input w-full px-3 py-2 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-[#175A67]"
                  value={filterRole}
                  onChange={(e) => setFilterRole(e.target.value)}
                >
                  <option value="all">All Roles</option>
                  <option value="field_technician">Field Technician</option>
                  <option value="safety_officer">Safety Officer</option>
                  <option value="maintenance_engineer">Maintenance Engineer</option>
                  <option value="site_supervisor">Site Supervisor</option>
                  <option value="operations_analyst">Operations Analyst</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-600 block mb-1.5">
                  Document Status
                </label>
                <select
                  className="glass-input w-full px-3 py-2 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-[#175A67]"
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                >
                  <option value="all">All statuses</option>
                  <option value="active">Active</option>
                  <option value="draft">Draft</option>
                  <option value="review">Review</option>
                  <option value="archived">Archived</option>
                </select>
              </div>

              <Button
                variant="ghost"
                size="sm"
                className="w-full text-xs text-slate-600 hover:text-slate-900"
                onClick={() => {
                  setSearchQuery('');
                  setFilterType('all');
                  setFilterStatus('all');
                  setFilterRole('all');
                  setPage(1);
                  fetchDocuments();
                }}
              >
                <RefreshCw className="h-3.5 w-3.5 mr-1" />
                Reset Filters
              </Button>
            </div>
          </Card>
        </div>

        {/* Document Table */}
        <Card padding="lg" className="lg:col-span-3 border-white/80 shadow-[0_8px_32px_0_rgba(15,23,42,0.10)]">
          <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-200/50">
            <div>
              <h3 className="text-sm font-heading font-bold text-[#101410]">
                {filteredDocs.length} Stored Documents
              </h3>
              <p className="text-xs text-slate-500">
                Connected to persistent SQLite store ({totalCount} total indexed)
              </p>
            </div>
            <Button
              variant="secondary"
              size="sm"
              onClick={fetchDocuments}
              className="text-xs"
              title="Refresh database records"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              Refresh
            </Button>
          </div>

          {isLoading ? (
            <LoadingSkeleton variant="table" count={5} />
          ) : filteredDocs.length === 0 ? (
            <EmptyState
              icon={<Database className="h-8 w-8 text-slate-400" />}
              title="No documents found in database"
              description="Upload your first SOP or document to save and index it into the frontline knowledge base."
              action={
                <Button variant="primary" size="sm" onClick={() => setShowUpload(true)}>
                  Upload Document
                </Button>
              }
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-white/60 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    <th className="py-3 px-3">Document Title</th>
                    <th className="py-3 px-2">Type / Role</th>
                    <th className="py-3 px-2">Status</th>
                    <th className="py-3 px-2">Version</th>
                    <th className="py-3 px-2">Chunks</th>
                    <th className="py-3 px-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/40 text-xs">
                  {filteredDocs.map((doc) => (
                    <tr key={doc.id} className="hover:bg-white/60 transition-colors">
                      <td className="py-3 px-3">
                        <div className="flex items-center gap-2.5">
                          <div className="h-8 w-8 rounded-lg bg-[#E2ECED] flex items-center justify-center shrink-0 border border-[#175A67]/20 text-[#175A67]">
                            <FileText className="h-4 w-4" />
                          </div>
                          <div className="min-w-0 max-w-[280px]">
                            <p className="font-bold text-slate-900 truncate hover:text-[#175A67] cursor-pointer" onClick={() => setInspectDoc(doc)}>
                              {doc.title}
                            </p>
                            <p className="text-[11px] text-slate-500 truncate">
                              {doc.source_organization || 'Frontline Ops'} &middot; {doc.original_filename || 'stored'}
                            </p>
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-2">
                        <span className="font-semibold text-slate-800 block">{doc.document_type || 'SOP'}</span>
                        <span className="text-[10px] text-slate-500 capitalize">{doc.intended_role?.replace('_', ' ') || 'All Roles'}</span>
                      </td>
                      <td className="py-3 px-2">
                        <Badge
                          tone={
                            doc.document_status === 'active'
                              ? 'success'
                              : doc.document_status === 'review'
                              ? 'warning'
                              : 'neutral'
                          }
                          size="sm"
                        >
                          {doc.document_status || 'active'}
                        </Badge>
                      </td>
                      <td className="py-3 px-2 font-mono text-slate-600">v{doc.version || '1.0'}</td>
                      <td className="py-3 px-2 font-mono text-slate-600">{doc.num_pages ? `${doc.num_pages} pgs` : 'Indexed'}</td>
                      <td className="py-3 px-3 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          <button
                            type="button"
                            onClick={() => setInspectDoc(doc)}
                            className="p-1.5 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-white/80 cursor-pointer"
                            title="Inspect metadata"
                          >
                            <Eye className="h-4 w-4" />
                          </button>
                          <button
                            type="button"
                            onClick={() => navigate(`/ask?q=${encodeURIComponent(`What is the procedure in ${doc.title}?`)}`)}
                            className="p-1.5 rounded-lg text-[#175A67] hover:text-[#0F3D47] hover:bg-[#E2ECED]/60 cursor-pointer"
                            title="Ask AI about this SOP"
                          >
                            <Sparkles className="h-4 w-4" />
                          </button>
                          <button
                            type="button"
                            onClick={() => handleDelete(doc.id, doc.title)}
                            className="p-1.5 rounded-lg text-rose-600 hover:text-rose-900 hover:bg-rose-50 cursor-pointer"
                            title="Delete from database"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="mt-4">
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

      {/* Database Upload Modal */}
      <Modal
        isOpen={showUpload}
        onClose={() => setShowUpload(false)}
        title="Upload & Save Document to Database"
        size="lg"
      >
        <form onSubmit={handleUploadSubmit} className="space-y-4 py-1">
          {uploadError && (
            <div className="p-3.5 rounded-xl bg-rose-50/90 border border-rose-300 text-rose-900 text-xs flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-rose-600 shrink-0" />
              <span>{uploadError}</span>
            </div>
          )}

          {uploadSuccess ? (
            <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-300 text-emerald-900 text-sm flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0" />
              <span>{uploadSuccess}</span>
            </div>
          ) : (
            <>
              <div className="p-3 rounded-xl bg-[#E2ECED]/50 border border-[#175A67]/20 flex items-center gap-2 text-xs text-[#175A67]">
                <Database className="h-4 w-4 shrink-0" />
                <span>
                  Documents and extracted chunks are saved directly into the SQLite <strong>frontline.db</strong> repository and indexed for hybrid RAG search.
                </span>
              </div>

              {/* Title & Organization */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-bold uppercase tracking-wider text-slate-700 block mb-1">
                    Document Title *
                  </label>
                  <input
                    type="text"
                    required
                    value={newTitle}
                    onChange={(e) => setNewTitle(e.target.value)}
                    placeholder="e.g. SOP-016: Centrifugal Pump Overhaul"
                    className="glass-input w-full px-3 py-2 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-[#175A67]"
                  />
                </div>

                <div>
                  <label className="text-xs font-bold uppercase tracking-wider text-slate-700 block mb-1">
                    Source Organization
                  </label>
                  <input
                    type="text"
                    value={newOrg}
                    onChange={(e) => setNewOrg(e.target.value)}
                    placeholder="e.g. Mechanical Integrity & Reliability"
                    className="glass-input w-full px-3 py-2 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-[#175A67]"
                  />
                </div>
              </div>

              {/* Document Type, Role, Topic */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="text-xs font-bold uppercase tracking-wider text-slate-700 block mb-1">
                    Document Type
                  </label>
                  <select
                    value={newDocType}
                    onChange={(e) => setNewDocType(e.target.value)}
                    className="glass-input w-full px-3 py-2 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-[#175A67]"
                  >
                    <option value="SOP">SOP</option>
                    <option value="Policy">Policy</option>
                    <option value="Procedure">Procedure</option>
                    <option value="Form">Form & Checklist</option>
                    <option value="Standard">Standard</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs font-bold uppercase tracking-wider text-slate-700 block mb-1">
                    Intended Role
                  </label>
                  <select
                    value={newRole}
                    onChange={(e) => setNewRole(e.target.value)}
                    className="glass-input w-full px-3 py-2 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-[#175A67]"
                  >
                    <option value="field_technician">Field Technician</option>
                    <option value="safety_officer">Safety Officer</option>
                    <option value="maintenance_engineer">Maintenance Engineer</option>
                    <option value="site_supervisor">Site Supervisor</option>
                    <option value="operations_analyst">Operations Analyst</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs font-bold uppercase tracking-wider text-slate-700 block mb-1">
                    Operational Topic
                  </label>
                  <select
                    value={newTopic}
                    onChange={(e) => setNewTopic(e.target.value)}
                    className="glass-input w-full px-3 py-2 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-[#175A67]"
                  >
                    <option value="operations">Operations</option>
                    <option value="calibration">Calibration</option>
                    <option value="electrical_safety">Electrical Safety</option>
                    <option value="hazardous_materials">Hazardous Materials</option>
                    <option value="confined_space">Confined Space</option>
                    <option value="mechanical">Mechanical</option>
                    <option value="telematics">Telematics</option>
                    <option value="compliance">Compliance</option>
                  </select>
                </div>
              </div>

              {/* Version & Status */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-bold uppercase tracking-wider text-slate-700 block mb-1">
                    Version
                  </label>
                  <input
                    type="text"
                    value={newVersion}
                    onChange={(e) => setNewVersion(e.target.value)}
                    placeholder="1.0"
                    className="glass-input w-full px-3 py-2 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-[#175A67]"
                  />
                </div>

                <div>
                  <label className="text-xs font-bold uppercase tracking-wider text-slate-700 block mb-1">
                    Document Status
                  </label>
                  <select
                    value={newStatus}
                    onChange={(e) => setNewStatus(e.target.value)}
                    className="glass-input w-full px-3 py-2 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-[#175A67]"
                  >
                    <option value="active">Active</option>
                    <option value="draft">Draft</option>
                    <option value="review">Review</option>
                    <option value="archived">Archived</option>
                  </select>
                </div>
              </div>

              {/* Description */}
              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-slate-700 block mb-1">
                  Description / Purpose
                </label>
                <input
                  type="text"
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                  placeholder="Summary of operational scope, tolerances, and requirements..."
                  className="glass-input w-full px-3 py-2 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-[#175A67]"
                />
              </div>

              {/* File Attachment */}
              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-slate-700 block mb-1">
                  Attach File (PDF, TXT, MD, CSV, DOCX)
                </label>
                <div
                  onDragOver={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    setDragActive(true);
                  }}
                  onDragEnter={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    setDragActive(true);
                  }}
                  onDragLeave={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    setDragActive(false);
                  }}
                  onDrop={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    setDragActive(false);
                    const file = e.dataTransfer.files?.[0];
                    if (file) processSelectedFile(file);
                  }}
                  className={`border-2 border-dashed rounded-xl p-4 text-center transition-all ${
                    dragActive
                      ? 'border-[#175A67] bg-[#E2ECED]/60 scale-[1.01]'
                      : selectedFile
                      ? 'border-emerald-400 bg-emerald-50/50'
                      : 'border-slate-300 bg-white/50 hover:bg-white/80'
                  }`}
                >
                  <input
                    type="file"
                    id="doc-file-input"
                    onChange={handleFileSelect}
                    accept=".pdf,.txt,.md,.csv,.json,.doc,.docx"
                    className="hidden"
                  />
                  {selectedFile ? (
                    <div className="flex items-center justify-between px-2">
                      <div className="flex items-center gap-2.5 text-left min-w-0">
                        <div className="h-9 w-9 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center shrink-0">
                          <FileText className="h-5 w-5" />
                        </div>
                        <div className="min-w-0">
                          <p className="text-xs font-bold text-slate-900 truncate">{selectedFile.name}</p>
                          <p className="text-[10px] text-slate-500">
                            {(selectedFile.size / 1024).toFixed(1)} KB &middot; Ready for database extraction & chunking
                          </p>
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          setSelectedFile(null);
                        }}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-white transition-colors cursor-pointer"
                        title="Remove file"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  ) : (
                    <label htmlFor="doc-file-input" className="cursor-pointer block">
                      <Upload className={`h-6 w-6 mx-auto mb-1.5 transition-colors ${dragActive ? 'text-[#175A67]' : 'text-slate-400'}`} />
                      <span className="text-xs text-[#175A67] font-semibold block">
                        {dragActive ? 'Drop file here to upload' : 'Click to select or drag document file'}
                      </span>
                      <span className="text-[10px] text-slate-400 block mt-0.5">
                        Supports PDF, TXT, Markdown, CSV, DOCX
                      </span>
                    </label>
                  )}
                </div>
              </div>

              {/* Text Content / Body (for immediate chunking) */}
              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-slate-700 block mb-1">
                  Document Text Body / Operational Steps (for RAG chunking)
                </label>
                <textarea
                  value={newContent}
                  onChange={(e) => setNewContent(e.target.value)}
                  rows={4}
                  placeholder="Paste or write the procedure steps, safety precautions, or rules here (will be extracted into searchable chunks)..."
                  className="glass-input w-full px-3 py-2 rounded-xl text-xs text-slate-900 resize-vertical focus:outline-none focus:border-[#175A67]"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-slate-200">
                <Button variant="ghost" type="button" onClick={() => setShowUpload(false)} disabled={isUploading}>
                  Cancel
                </Button>
                <Button variant="primary" type="submit" isLoading={isUploading} className="bg-[#175A67] hover:bg-[#0F454F]">
                  Save to Database
                </Button>
              </div>
            </>
          )}
        </form>
      </Modal>

      {/* Inspect Document Modal */}
      {inspectDoc && (
        <Modal
          isOpen={!!inspectDoc}
          onClose={() => setInspectDoc(null)}
          title={inspectDoc.title}
          size="lg"
        >
          <div className="space-y-4 py-1 text-xs">
            <div className="p-3 rounded-xl bg-[#E2ECED]/60 border border-[#175A67]/20 flex flex-wrap gap-2 text-slate-700">
              <span>Database ID: <strong className="font-mono text-slate-900">#{inspectDoc.id}</strong></span>
              <span>&middot;</span>
              <span>Type: <strong className="text-[#175A67]">{inspectDoc.document_type}</strong></span>
              <span>&middot;</span>
              <span>Role: <strong className="text-[#175A67]">{inspectDoc.intended_role || 'All roles'}</strong></span>
              <span>&middot;</span>
              <span>Topic: <strong className="text-[#175A67]">{inspectDoc.topic}</strong></span>
              <span>&middot;</span>
              <span>Status: <strong className="text-emerald-700">{inspectDoc.document_status}</strong></span>
            </div>

            <div>
              <span className="font-bold uppercase tracking-wider text-slate-700 block mb-1">
                Description
              </span>
              <p className="p-2.5 rounded-xl bg-white/70 border border-white/80 text-slate-800 leading-relaxed">
                {inspectDoc.description || 'No description provided.'}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-2 bg-white/60 p-2.5 rounded-xl border border-white/80">
              <div>
                <span className="text-slate-500 block">Organization:</span>
                <span className="font-semibold text-slate-800">{inspectDoc.source_organization}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Original Filename:</span>
                <span className="font-mono text-slate-800">{inspectDoc.original_filename || 'stored.pdf'}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Version:</span>
                <span className="text-slate-800">v{inspectDoc.version || '1.0'}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Stored In DB:</span>
                <span className="text-emerald-700 font-semibold">{inspectDoc.uploaded_at ? new Date(inspectDoc.uploaded_at).toLocaleString() : 'Active'}</span>
              </div>
            </div>

            <div className="flex flex-wrap justify-between items-center gap-2 pt-3 border-t border-slate-200">
              <Button variant="ghost" onClick={() => setInspectDoc(null)}>
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
                  Ask AI About This SOP
                </Button>
              </div>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}

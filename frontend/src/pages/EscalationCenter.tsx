import React, { useState, useEffect } from 'react';
import {
  HelpCircle,
  AlertTriangle,
  Clock,
  Plus,
  CheckCircle2,
} from 'lucide-react';
import { Card, Badge, Button, Modal, LoadingSkeleton, EmptyState } from '@/components/ui';
import api from '@/services/api';

const escalationPriorities: Record<string, { label: string; color: string; icon: any }> = {
  critical: { label: 'Critical', color: 'bg-rose-100 text-rose-900 border-rose-300', icon: AlertTriangle },
  high: { label: 'High', color: 'bg-amber-100 text-amber-900 border-amber-300', icon: AlertTriangle },
  medium: { label: 'Medium', color: 'bg-yellow-100 text-yellow-900 border-yellow-300', icon: AlertTriangle },
  low: { label: 'Low', color: 'bg-slate-100 text-slate-800 border-slate-300', icon: Clock },
};

export function EscalationCenter() {
  const [escalations, setEscalations] = useState<any[]>([]);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(true);

  // Filter
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [priorityFilter, setPriorityFilter] = useState<string>('');

  // Selected item modal
  const [openDetailModal, setOpenDetailModal] = useState(false);
  const [selectedEsc, setSelectedEsc] = useState<any | null>(null);

  // New escalation modal
  const [openCreateModal, setOpenCreateModal] = useState(false);
  const [newQuestion, setNewQuestion] = useState('');
  const [newContext, setNewContext] = useState('');
  const [newEvidence, setNewEvidence] = useState('');
  const [newPriority, setNewPriority] = useState('high');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const fetchEscalations = async () => {
    setIsLoading(true);
    try {
      const params: any = { limit: 50 };
      if (statusFilter) params.status = statusFilter;
      if (priorityFilter) params.priority = priorityFilter;
      const res = await api.get('/escalations/', { params });
      setEscalations(res.data.items || []);
      setTotalCount(res.data.total || 0);
    } catch (err) {
      console.error('Failed to fetch escalations:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchEscalations();
  }, [statusFilter, priorityFilter]);

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newQuestion.trim()) return;

    setIsSubmitting(true);
    try {
      await api.post('/escalations/', {
        question: newQuestion,
        context: newContext,
        evidence_references: newEvidence,
        priority: newPriority,
      });

      setSuccessMsg('Escalation created successfully.');
      setTimeout(() => {
        setOpenCreateModal(false);
        setNewQuestion('');
        setNewContext('');
        setNewEvidence('');
        setSuccessMsg(null);
        fetchEscalations();
      }, 1200);
    } catch (err: any) {
      alert('Failed to create escalation: ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 sm:space-y-7">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="h-12 w-12 rounded-2xl bg-amber-100/80 backdrop-blur-md flex items-center justify-center border border-amber-300 text-amber-800 shadow-2xs">
            <HelpCircle className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-3xl sm:text-4xl font-heading font-bold text-[#101410] tracking-tight leading-tight">
              Escalation <span className="font-calligraphy font-normal italic text-[#175A67] text-4xl sm:text-5xl pl-1 inline-block">Center</span>
            </h1>
            <p className="font-heading italic text-sm text-[#263B40] mt-1 font-medium">
              Human oversight & technical escalation options when required SOP guidance is missing or conflicting.
            </p>
          </div>
        </div>

        <Button
          variant="primary"
          onClick={() => setOpenCreateModal(true)}
          className="bg-[#175A67] hover:bg-[#0F454F] shadow-sm self-start sm:self-auto"
        >
          <Plus className="h-4 w-4" />
          New Escalation
        </Button>
      </div>

      <Card padding="lg" className="border-white/85 shadow-[0_8px_32px_0_rgba(23,90,103,0.06)]">
        {/* Filter Toolbar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5 pb-3 border-b border-slate-200/60">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-heading font-bold text-[#101410]">
              {totalCount} Total Escalation Cases
            </h3>
            <span className="text-xs text-slate-500 font-serif italic">
              ({escalations.filter(e => e.status === 'open').length} requiring review)
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="glass-input px-3 py-1.5 rounded-xl text-xs text-slate-800 focus:outline-none focus:border-[#175A67]"
            >
              <option value="">All Statuses</option>
              <option value="open">Open</option>
              <option value="in_progress">In Progress</option>
              <option value="resolved">Resolved</option>
              <option value="closed">Closed</option>
            </select>

            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="glass-input px-3 py-1.5 rounded-xl text-xs text-slate-800 focus:outline-none focus:border-[#175A67]"
            >
              <option value="">All Priorities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
        </div>

        {/* Escalation List */}
        {isLoading ? (
          <LoadingSkeleton variant="table" count={4} />
        ) : escalations.length === 0 ? (
          <EmptyState
            icon={<CheckCircle2 className="h-8 w-8 text-emerald-500" />}
            title="No active escalations found"
            description="All frontline guidance requests are currently resolved or none match your filters."
          />
        ) : (
          <div className="space-y-3">
            {escalations.map((esc) => {
              const priority = escalationPriorities[esc.priority] || escalationPriorities.medium;
              const PriorityIcon = priority.icon;
              return (
                <div
                  key={esc.id}
                  className="w-full p-4 rounded-2xl bg-white/60 hover:bg-white/90 backdrop-blur-md border border-white/80 hover:border-[#175A67]/30 transition-all shadow-2xs cursor-pointer text-left group"
                  onClick={() => {
                    setSelectedEsc(esc);
                    setOpenDetailModal(true);
                  }}
                >
                  <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1.5">
                        <span className={`inline-flex items-center gap-1 text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${priority.color}`}>
                          <PriorityIcon className="h-3 w-3" />
                          {priority.label}
                        </span>
                        <Badge
                          tone={
                            esc.status === 'resolved'
                              ? 'success'
                              : esc.status === 'open'
                              ? 'danger'
                              : 'warning'
                          }
                          size="sm"
                        >
                          {esc.status}
                        </Badge>
                        <span className="text-[11px] font-mono text-slate-500">
                          #{esc.id} &middot; {new Date(esc.created_at || Date.now()).toLocaleDateString()}
                        </span>
                      </div>

                      <p className="text-sm font-bold text-slate-900 group-hover:text-[#175A67] transition-colors">
                        {esc.question}
                      </p>
                      {esc.context && (
                        <p className="text-xs text-slate-600 mt-1 line-clamp-2">
                          {esc.context}
                        </p>
                      )}
                      {esc.evidence_references && (
                        <p className="text-[11px] text-slate-500 font-mono mt-1.5">
                          Evidence: {esc.evidence_references}
                        </p>
                      )}
                    </div>

                    <div className="flex items-center gap-2 shrink-0 self-start sm:self-center">
                      {esc.review_notes ? (
                        <span className="text-[11px] px-2.5 py-1 rounded-xl bg-amber-50 text-amber-900 border border-amber-200">
                          Reviewer Advisory
                        </span>
                      ) : (
                        <span className="text-[11px] text-slate-500">Pending Review</span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </Card>

      {/* Escalation Detail Modal */}
      {selectedEsc && (
        <Modal
          isOpen={openDetailModal}
          onClose={() => {
            setOpenDetailModal(false);
            setSelectedEsc(null);
          }}
          title={`Escalation Case #${selectedEsc.id}`}
          size="lg"
        >
          <div className="space-y-4 py-1">
            <div className="p-3.5 rounded-2xl bg-amber-50/90 border border-amber-200">
              <span className="text-[10px] font-bold uppercase tracking-wider text-amber-800 block mb-1">
                Discrepancy / Question
              </span>
              <p className="font-bold text-slate-900 text-sm">{selectedEsc.question}</p>
            </div>

            {selectedEsc.context && (
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                  Operational Context & Task State
                </h4>
                <p className="text-xs text-slate-800 bg-white/70 p-3 rounded-xl border border-white/80 whitespace-pre-wrap leading-relaxed">
                  {selectedEsc.context}
                </p>
              </div>
            )}

            {selectedEsc.evidence_references && (
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                  Conflicting or Missing Evidence
                </h4>
                <p className="text-xs font-mono text-slate-800 bg-white/70 p-2.5 rounded-xl border border-white/80">
                  {selectedEsc.evidence_references}
                </p>
              </div>
            )}

            {selectedEsc.review_notes && (
              <div className="p-3.5 rounded-xl bg-emerald-50/90 border border-emerald-200">
                <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-800 block mb-1">
                  Reviewer Notes & Resolution Actions
                </span>
                <p className="text-xs text-emerald-950 font-medium leading-relaxed">
                  {selectedEsc.review_notes}
                </p>
              </div>
            )}

            <div className="grid grid-cols-3 gap-2.5 p-3 rounded-xl bg-white/60 border border-white/80 text-xs">
              <div>
                <span className="text-slate-500 block text-[10px] uppercase font-bold">Priority</span>
                <span className="font-bold uppercase text-slate-900">{selectedEsc.priority}</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px] uppercase font-bold">Status</span>
                <span className="font-bold uppercase text-[#175A67]">{selectedEsc.status}</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px] uppercase font-bold">User ID</span>
                <span className="font-mono text-slate-900">User #{selectedEsc.user_id}</span>
              </div>
            </div>

            <div className="flex justify-end gap-2.5 pt-2 border-t border-slate-200">
              <Button
                variant="ghost"
                onClick={() => {
                  setOpenDetailModal(false);
                  setSelectedEsc(null);
                }}
              >
                Close
              </Button>
            </div>
          </div>
        </Modal>
      )}

      {/* Create New Escalation Modal */}
      <Modal
        isOpen={openCreateModal}
        onClose={() => setOpenCreateModal(false)}
        title="Submit Frontline Guidance Escalation"
        size="md"
      >
        <form onSubmit={handleCreateSubmit} className="space-y-4 py-1">
          {successMsg ? (
            <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-300 text-emerald-900 text-sm flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0" />
              <span>{successMsg}</span>
            </div>
          ) : (
            <>
              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-slate-700 block mb-1">
                  Discrepancy / Question *
                </label>
                <input
                  type="text"
                  required
                  value={newQuestion}
                  onChange={(e) => setNewQuestion(e.target.value)}
                  placeholder="e.g. Missing calibration offset table for high-temp pressure transmitter"
                  className="glass-input w-full px-3.5 py-2.5 rounded-xl text-sm text-slate-900 focus:outline-none focus:border-[#175A67]"
                />
              </div>

              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-slate-700 block mb-1">
                  Severity & Priority
                </label>
                <div className="grid grid-cols-4 gap-2">
                  {['low', 'medium', 'high', 'critical'].map((p) => (
                    <button
                      key={p}
                      type="button"
                      onClick={() => setNewPriority(p)}
                      className={`py-2 px-2.5 rounded-xl text-xs font-bold uppercase tracking-wider border cursor-pointer ${
                        newPriority === p
                          ? p === 'critical'
                            ? 'bg-rose-700 text-white border-rose-800'
                            : p === 'high'
                            ? 'bg-amber-600 text-white border-amber-700'
                            : 'bg-[#175A67] text-white border-[#175A67]'
                          : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-50'
                      }`}
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-slate-700 block mb-1">
                  Operational Context & Observations
                </label>
                <textarea
                  value={newContext}
                  onChange={(e) => setNewContext(e.target.value)}
                  rows={3}
                  placeholder="Describe location, equipment serial, or step where instructions conflicted..."
                  className="glass-input w-full px-3.5 py-2.5 rounded-xl text-xs text-slate-900 resize-vertical leading-relaxed focus:outline-none focus:border-[#175A67]"
                />
              </div>

              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-slate-700 block mb-1">
                  Evidence / SOP Citations
                </label>
                <input
                  type="text"
                  value={newEvidence}
                  onChange={(e) => setNewEvidence(e.target.value)}
                  placeholder="e.g. SOP-001 §2.3 vs OEM Manual p.44"
                  className="glass-input w-full px-3.5 py-2.5 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-[#175A67]"
                />
              </div>

              <div className="flex justify-end gap-2.5 pt-2 border-t border-slate-200">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => setOpenCreateModal(false)}
                  disabled={isSubmitting}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  isLoading={isSubmitting}
                  className="bg-[#175A67] hover:bg-[#0F454F]"
                >
                  Submit Case
                </Button>
              </div>
            </>
          )}
        </form>
      </Modal>
    </div>
  );
}

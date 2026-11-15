import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  Search,
  MessageSquare,
  XCircle,
  Save,
  Bot,
  ChevronUp,
  ChevronDown,
  BookOpen,
  AlertCircle,
  Cpu,
  ShieldAlert,
  CheckCircle2,
  Sliders,
  ExternalLink,
  Key,
  Eye,
  EyeOff,
} from 'lucide-react';
import { Card, Badge, Button, LoadingSkeleton, EmptyState, AnswerPanel, Modal } from '@/components/ui';
import api from '@/services/api';

const FRONTLINE_ROLES = [
  { id: 'field_technician', label: 'Field Technician', icon: '🔧', tag: 'Calibration & Sensors' },
  { id: 'safety_officer', label: 'Safety Officer', icon: '🛡️', tag: 'LOTO & Hazmat' },
  { id: 'maintenance_engineer', label: 'Maintenance Eng', icon: '⚙️', tag: 'Mechanical & PRVs' },
  { id: 'site_supervisor', label: 'Site Supervisor', icon: '📋', tag: 'Permits & Shifts' },
  { id: 'operations_analyst', label: 'Operations Analyst', icon: '📊', tag: 'Logs & OEE' },
];

const SUGGESTED_QUERIES = [
  {
    role: 'field_technician',
    query: 'How often must field pressure transmitters be calibrated and what is the maximum permissible drift?',
    tag: 'SOP-001 Sensor Drift',
  },
  {
    role: 'safety_officer',
    query: 'What are the Level B PPE requirements for anhydrous ammonia leaks and respirator limits?',
    tag: 'SOP-002 Hazmat PPE',
  },
  {
    role: 'safety_officer',
    query: 'What is the zero-energy verification sequence before 480V breaker racking?',
    tag: 'SOP-003 LOTO 480V',
  },
  {
    role: 'safety_officer',
    query: 'What are the 4 atmospheric gas test limits and order before entering a confined tank?',
    tag: 'SOP-004 Confined Space',
  },
  {
    role: 'field_technician',
    query: 'What is the procedure for ultrasonic quantum hyperdrive warp phase realignment?',
    tag: 'Missing Guidance Test (Escalation)',
  },
];

import { useUser } from '@/context/UserContext';

export function AskKnowledge() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { user } = useUser();

  // Active frontline role & inputs (defaults to active user profile role)
  const [selectedRole, setSelectedRole] = useState<string>(user?.role || 'field_technician');
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState<string | null>(null);
  const [answerConfidence, setAnswerConfidence] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [retrievedPassages, setRetrievedPassages] = useState<any[]>([]);
  const [citations, setCitations] = useState<any[]>([]);
  const [importantConditions, setImportantConditions] = useState<string[]>([]);
  const [limitations, setLimitations] = useState<string[]>([]);
  const [recommendedNextAction, setRecommendedNextAction] = useState<string>('');
  const [evidenceStatus, setEvidenceStatus] = useState<string>('');
  const [showEvidence, setShowEvidence] = useState(true);
  const [saved, setSaved] = useState(false);

  // ML Intent & Escalation state
  const [mlModelInfo, setMlModelInfo] = useState<any>(null);
  const [mlIntentResult, setMlIntentResult] = useState<any>(null);
  const [escalationRecommended, setEscalationRecommended] = useState(false);
  const [escalationReason, setEscalationReason] = useState<string>('');

  // Optional Custom Gemini API key (persists across sessions)
  const [customApiKey, setCustomApiKey] = useState<string>(() => {
    try {
      return localStorage.getItem('frontline_custom_api_key') || '';
    } catch {
      return '';
    }
  });
  const [showKeyPassword, setShowKeyPassword] = useState<boolean>(false);

  const handleApiKeyChange = (val: string) => {
    setCustomApiKey(val);
    try {
      if (val.trim()) {
        localStorage.setItem('frontline_custom_api_key', val.trim());
      } else {
        localStorage.removeItem('frontline_custom_api_key');
      }
    } catch (e) {
      console.warn('localStorage error:', e);
    }
  };

  // Escalation Modal state
  const [showEscalateModal, setShowEscalateModal] = useState(false);
  const [escalatePriority, setEscalatePriority] = useState<string>('high');
  const [escalateContext, setEscalateContext] = useState<string>('');
  const [isEscalating, setIsEscalating] = useState(false);
  const [escalateSuccess, setEscalateSuccess] = useState<string | null>(null);

  // Load trained ML model metadata on mount
  useEffect(() => {
    api.get('/rag/ml-model')
      .then((res) => setMlModelInfo(res.data))
      .catch((err) => console.warn('ML model metadata:', err));
  }, []);

  const executeSearch = async (queryText: string, roleOverride?: string) => {
    if (!queryText.trim()) return;

    const roleToUse = roleOverride || selectedRole;
    setIsLoading(true);
    setError(null);
    setAnswer(null);
    setAnswerConfidence(null);
    setRetrievedPassages([]);
    setCitations([]);
    setImportantConditions([]);
    setLimitations([]);
    setRecommendedNextAction('');
    setEvidenceStatus('');
    setMlIntentResult(null);
    setEscalationRecommended(false);
    setEscalationReason('');
    setEscalateSuccess(null);

    try {
      const response = await api.post('/rag/query', {
        query: queryText,
        role: roleToUse,
        top_k: 5,
        api_key: customApiKey.trim() || undefined,
      });

      setAnswer(response.data.direct_answer);
      setRetrievedPassages(response.data.retrieved_passages || []);
      setCitations(response.data.supporting_citations || []);
      setImportantConditions(response.data.important_conditions || []);
      setLimitations(response.data.limitations || []);
      setRecommendedNextAction(response.data.recommended_next_action || '');
      setEvidenceStatus(response.data.evidence_status || '');
      setAnswerConfidence(response.data.confidence_score ?? response.data.ml_confidence ?? 0.75);
      const intentName = typeof response.data.ml_intent === 'string'
        ? response.data.ml_intent
        : response.data.ml_intent?.primary_intent;
      if (intentName) {
        setMlIntentResult({
          primary_intent: intentName,
          calibrated_confidence: response.data.ml_confidence ?? response.data.ml_intent?.calibrated_confidence ?? 0.5,
          predicted_role: response.data.ml_predicted_role ?? response.data.ml_intent?.predicted_role ?? roleToUse,
          model_version: response.data.model_info?.architecture || 'TF-IDF Calibrated Linear',
        });
      } else {
        setMlIntentResult(null);
      }
      setEscalationRecommended(Boolean(response.data.escalation_recommended));
      setEscalationReason(response.data.escalation_reason || '');
      setShowEvidence(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to retrieve answer. Please try again.');
      console.error('RAG query error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const q = searchParams.get('q');
    if (q) {
      setQuestion(q);
      executeSearch(q);
    }
  }, [searchParams]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    executeSearch(question);
  };

  const handleCitationClick = () => {
    setShowEvidence(true);
  };

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const handleOpenEscalateModal = () => {
    setEscalateContext(
      `Query: "${question}"\nActive Role: ${selectedRole}\n` +
      (escalationReason ? `Reason: ${escalationReason}\n` : '') +
      (retrievedPassages.length === 0 ? 'No matching SOP chunks found in knowledge base.' : `Retrieved ${retrievedPassages.length} passages with low semantic relevance.`)
    );
    setShowEscalateModal(true);
  };

  const handleConfirmEscalation = async () => {
    setIsEscalating(true);
    try {
      const payload = {
        question: question || 'Operational SOP discrepancy report',
        context: escalateContext,
        evidence_references: citations.length > 0
          ? citations.map((c) => c.citation || c.title).join('; ')
          : 'None / Missing Guidance',
        priority: escalatePriority,
      };

      const res = await api.post('/escalations/', payload);
      setEscalateSuccess(`Escalation #${res.data.id} submitted successfully to supervisor queue!`);
      setTimeout(() => {
        setShowEscalateModal(false);
      }, 1800);
    } catch (err: any) {
      console.error('Failed to submit escalation:', err);
      alert('Failed to submit escalation: ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsEscalating(false);
    }
  };

  return (
    <div className="space-y-6 sm:space-y-7">
      {/* Header with Calligraphy & Display fonts */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="h-12 w-12 rounded-2xl bg-[#E2ECED] backdrop-blur-md flex items-center justify-center border border-[#175A67]/20 text-[#175A67] shadow-2xs">
            <MessageSquare className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-3xl sm:text-4xl font-heading font-bold text-[#101410] tracking-tight leading-tight">
              Frontline <span className="font-calligraphy font-normal italic text-[#175A67] text-4xl sm:text-5xl pl-1 inline-block">Workspace</span>
            </h1>
            <p className="font-heading italic text-sm text-[#263B40] mt-1 font-medium">
              Role-guided retrieval, calibrated ML intent classification, and controlled source-grounded summaries.
            </p>
          </div>
        </div>

        {/* Live ML Model Status Indicator */}
        <div className="flex flex-wrap items-center gap-2.5 self-start md:self-auto p-2 rounded-2xl bg-white/75 backdrop-blur-xl border border-white/85 shadow-[0_4px_20px_rgba(23,90,103,0.06)]">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-semibold bg-[#E2ECED] text-[#175A67] border border-[#175A67]/20">
            <Cpu className="h-3.5 w-3.5 text-[#175A67]" />
            <span>ML Intent Classifier</span>
            <span className="w-2 h-2 rounded-full bg-[#175A67] animate-pulse"></span>
          </div>
          <span className="text-xs px-2.5 py-1 rounded-xl bg-white/90 text-[#175A67] font-bold border border-[#175A67]/20">
            {mlModelInfo?.model_type ? 'Calibrated Linear' : 'Active'}
          </span>
          {customApiKey ? (
            <span className="inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-xl bg-emerald-50 text-emerald-800 font-bold border border-emerald-300">
              <Key className="h-3 w-3 text-emerald-700" />
              Custom Key Active
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-xl bg-slate-100 text-slate-700 font-semibold border border-slate-200">
              <Key className="h-3 w-3 text-slate-500" />
              Backend Key
            </span>
          )}
        </div>
      </div>

      {/* Role-Specific Workspace Selector */}
      <Card padding="md" className="border-white/85 shadow-[0_8px_32px_0_rgba(23,90,103,0.06)] bg-white/60">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3 pb-2 border-b border-slate-200/60">
          <div className="flex items-center gap-2">
            <Sliders className="h-4 w-4 text-[#175A67]" />
            <span className="text-xs font-bold uppercase tracking-wider text-[#175A67]">Active Frontline Role</span>
            <span className="text-xs text-slate-500 font-serif italic">— Controls prompt constraints & relevance ranking</span>
          </div>
          <span className="text-xs text-slate-600 font-mono">
            Selected: <strong className="text-[#175A67]">{FRONTLINE_ROLES.find(r => r.id === selectedRole)?.label}</strong>
          </span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2.5">
          {FRONTLINE_ROLES.map((r) => {
            const isSelected = selectedRole === r.id;
            return (
              <button
                key={r.id}
                onClick={() => setSelectedRole(r.id)}
                className={`p-3 rounded-xl text-left transition-all border cursor-pointer ${
                  isSelected
                    ? 'bg-[#175A67] text-[#FAF8F5] border-[#175A67] shadow-md shadow-[#175A67]/20 scale-[1.01]'
                    : 'bg-white/70 hover:bg-white/95 text-slate-800 border-white/80 hover:border-[#175A67]/30'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-base">{r.icon}</span>
                  <span className={`text-xs font-bold leading-tight ${isSelected ? 'text-[#FAF8F5]' : 'text-slate-900'}`}>
                    {r.label}
                  </span>
                </div>
                <p className={`text-[11px] truncate ${isSelected ? 'text-[#FAF8F5]/80' : 'text-slate-500'}`}>
                  {r.tag}
                </p>
              </button>
            );
          })}
        </div>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main input & answer area (2 cols) */}
        <div className="lg:col-span-2 space-y-5">
          {/* Query Input Card */}
          <Card padding="lg" className="border-white/85 shadow-[0_8px_32px_0_rgba(23,90,103,0.06)]">
            <form onSubmit={handleSubmit}>
              <div className="relative">
                <Search className="absolute left-4 top-4 h-5 w-5 text-slate-500 pointer-events-none" />
                <textarea
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder={`Ask a question as a ${FRONTLINE_ROLES.find(r => r.id === selectedRole)?.label} (e.g. calibration, safety lockout, gas testing, PPE)...`}
                  className="glass-input w-full min-h-[130px] pl-11 pr-28 py-3.5 rounded-2xl text-base sm:text-sm text-[#101410] placeholder-[#4A5B5E]/70 focus:outline-none focus:bg-white/95 focus:border-[#175A67] resize-vertical leading-relaxed"
                  aria-label="Your frontline question"
                />
                <div className="absolute right-3.5 bottom-3.5 flex gap-2">
                  <Button
                    type="submit"
                    variant="primary"
                    className="h-10 px-5 rounded-xl font-bold shadow-sm hover:shadow-[0_4px_16px_rgba(23,90,103,0.25)] cursor-pointer"
                    isLoading={isLoading}
                  >
                    Run Retrieval
                  </Button>
                </div>
              </div>
            </form>

            {/* Custom API Key Input Bar (Optional Fallback) */}
            <div className="mt-4 pt-3.5 border-t border-slate-200/60">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1.5 mb-2">
                <div className="flex items-center gap-1.5">
                  <Key className="h-3.5 w-3.5 text-[#175A67]" />
                  <span className="text-xs font-bold uppercase tracking-wider text-[#175A67]">
                    Gemini API Key (Optional)
                  </span>
                  <span className="text-[11px] text-slate-500 font-serif italic">
                    — Used if backend default API key is rate-limited or fails
                  </span>
                </div>
                {customApiKey ? (
                  <span className="text-[10px] font-semibold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-300 flex items-center gap-1 self-start sm:self-auto">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                    Active
                  </span>
                ) : (
                  <span className="text-[10px] text-slate-500 bg-white/70 px-2 py-0.5 rounded-md border border-slate-200 self-start sm:self-auto">
                    Using Backend Default Key
                  </span>
                )}
              </div>

              <div className="relative flex items-center gap-2">
                <div className="relative flex-1">
                  <Key className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 pointer-events-none" />
                  <input
                    type={showKeyPassword ? 'text' : 'password'}
                    value={customApiKey}
                    onChange={(e) => handleApiKeyChange(e.target.value)}
                    placeholder="Enter Gemini API key (optional — e.g. AIzaSy... if backend key doesn't work)"
                    className="glass-input w-full pl-10 pr-20 py-2.5 rounded-xl text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-[#175A67]"
                    aria-label="Optional Gemini API Key"
                  />
                  <div className="absolute right-2.5 top-1/2 -translate-y-1/2 flex items-center gap-1">
                    {customApiKey && (
                      <button
                        type="button"
                        onClick={() => handleApiKeyChange('')}
                        className="text-[11px] text-slate-400 hover:text-rose-600 px-1.5 py-0.5 cursor-pointer font-medium"
                        title="Clear custom API key"
                      >
                        Clear
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={() => setShowKeyPassword(!showKeyPassword)}
                      className="p-1 text-slate-400 hover:text-slate-700 cursor-pointer"
                      title={showKeyPassword ? 'Hide API key' : 'Show API key'}
                    >
                      {showKeyPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Suggested Scenarios */}
            <div className="mt-4 pt-3.5 border-t border-slate-200/60">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-600 block mb-2">
                Operational Scenarios:
              </span>
              <div className="flex flex-wrap gap-2">
                {SUGGESTED_QUERIES.map((sq, i) => (
                  <button
                    key={i}
                    className="text-xs px-3 py-1.5 rounded-xl bg-white/70 hover:bg-white/95 text-slate-800 hover:text-slate-950 border border-white/80 hover:border-[#175A67]/40 backdrop-blur-xs transition-all cursor-pointer shadow-2xs font-medium flex items-center gap-1.5"
                    onClick={() => {
                      setSelectedRole(sq.role);
                      setQuestion(sq.query);
                      executeSearch(sq.query, sq.role);
                    }}
                  >
                    <span className="text-[#175A67] font-semibold">[{sq.tag}]</span>
                    <span className="max-w-[280px] truncate">{sq.query}</span>
                  </button>
                ))}
              </div>
            </div>
          </Card>

          {/* Real-Time ML Intent & Telemetry Badge */}
          {mlIntentResult && (
            <Card padding="md" className="border-[#175A67]/20 shadow-[0_4px_24px_rgba(23,90,103,0.06)] bg-gradient-to-r from-white/90 via-[#E2ECED]/40 to-white/90">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-2.5">
                  <div className="h-9 w-9 rounded-xl bg-[#175A67] text-[#FAF8F5] flex items-center justify-center font-bold text-xs shadow-xs">
                    ML
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-[#175A67] uppercase tracking-wide">
                        Intent: {mlIntentResult.primary_intent?.replace(/_/g, ' ')}
                      </span>
                      <Badge
                        tone={
                          (mlIntentResult.calibrated_confidence || 0) >= 0.7
                            ? 'success'
                            : (mlIntentResult.calibrated_confidence || 0) >= 0.35
                            ? 'warning'
                            : 'danger'
                        }
                        size="sm"
                      >
                        {Math.round((mlIntentResult.calibrated_confidence || 0) * 100)}% calibrated confidence
                      </Badge>
                    </div>
                    <p className="text-[11px] text-slate-600 mt-0.5">
                      Predicted Role: <span className="font-semibold text-slate-800">{mlIntentResult.predicted_role}</span> • Model: {mlIntentResult.model_version || 'TF-IDF Calibrated'}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2 self-start sm:self-center">
                  <span className="text-xs text-slate-500 font-mono">
                    RAG Grounding: <strong>{evidenceStatus || 'Evaluated'}</strong>
                  </span>
                </div>
              </div>
            </Card>
          )}

          {/* Missing Guidance Alert Banner */}
          {escalationRecommended && (
            <div className="p-4 sm:p-5 rounded-2xl bg-amber-50/95 border border-amber-300 shadow-md backdrop-blur-md flex flex-col sm:flex-row sm:items-center justify-between gap-3.5">
              <div className="flex items-start gap-3">
                <ShieldAlert className="h-6 w-6 text-amber-700 shrink-0 mt-0.5" />
                <div>
                  <h4 className="text-sm font-bold text-amber-950 font-heading">
                    Missing or Insufficient Operational Guidance Detected
                  </h4>
                  <p className="text-xs text-amber-900 mt-1 leading-relaxed">
                    {escalationReason || 'The knowledge repository lacks verified high-confidence SOPs for this task. Frontline personnel should not guess.'}
                  </p>
                </div>
              </div>
              <Button
                variant="primary"
                onClick={handleOpenEscalateModal}
                className="shrink-0 bg-amber-700 hover:bg-amber-800 text-white border-amber-800 text-xs py-2 px-4 shadow-sm"
              >
                <XCircle className="h-4 w-4" />
                Escalate to Lead
              </Button>
            </div>
          )}

          {/* Synthesized Response Area */}
          <Card padding="lg" className="border-white/85 shadow-[0_8px_32px_0_rgba(23,90,103,0.06)]">
            <div className="flex items-center justify-between gap-3 mb-4">
              <div className="flex items-center gap-2.5">
                <div className="h-8 w-8 rounded-xl bg-[#E2ECED] flex items-center justify-center text-[#175A67] border border-[#175A67]/20">
                  <Bot className="h-4 w-4" />
                </div>
                <h3 className="text-2xl font-heading font-bold text-[#101410]">
                  Grounded <span className="font-calligraphy font-normal italic text-[#175A67] text-2xl pl-1 inline-block">Summary</span>
                </h3>
              </div>
              {evidenceStatus && (
                <Badge tone={evidenceStatus.includes('supported') ? 'success' : 'neutral'} size="sm">
                  {evidenceStatus.replace(/_/g, ' ')}
                </Badge>
              )}
            </div>

            <AnswerPanel
              answer={answer || ''}
              confidence={answerConfidence ?? 0}
              isLoading={isLoading}
              isEmpty={!question && !isLoading}
              isError={error !== null}
              error={error || undefined}
              citations={citations}
              onCitationClick={handleCitationClick}
              onSave={handleSave}
              isSaved={saved}
              onEscalate={handleOpenEscalateModal}
            />

            {/* Conditions & Notes */}
            {importantConditions.length > 0 && (
              <div className="mt-4 p-4 bg-amber-50/80 backdrop-blur-sm border border-amber-200 rounded-2xl">
                <h4 className="text-xs font-bold uppercase tracking-wider text-amber-900 mb-1.5 flex items-center gap-1.5">
                  <AlertCircle className="h-4 w-4 text-amber-700" />
                  Mandatory Operational Conditions
                </h4>
                <ul className="list-disc list-inside text-xs sm:text-sm text-amber-950 space-y-1 pl-1">
                  {importantConditions.map((cond, i) => (
                    <li key={i}>{cond}</li>
                  ))}
                </ul>
              </div>
            )}

            {limitations.length > 0 && (
              <div className="mt-3 p-3.5 bg-white/60 backdrop-blur-sm border border-white/70 rounded-2xl">
                <h4 className="text-xs font-semibold text-slate-600 mb-1">Scope & Policy Limitations</h4>
                <ul className="list-disc list-inside text-xs text-slate-600 space-y-0.5 pl-1">
                  {limitations.map((lim, i) => (
                    <li key={i}>{lim}</li>
                  ))}
                </ul>
              </div>
            )}

            {recommendedNextAction && recommendedNextAction !== 'None' && (
              <div className="mt-3.5 p-3 rounded-xl bg-white/60 backdrop-blur-xs border border-white/70 text-xs text-slate-700 flex items-center gap-2">
                <span className="font-semibold text-slate-900">Recommended Next Action:</span>
                <span>{recommendedNextAction}</span>
              </div>
            )}
          </Card>
        </div>

        {/* Right sidebar: Retrieved Evidence Passages (1 col) */}
        <div className="space-y-4">
          <Card padding="lg" className="border-white/80 shadow-[0_8px_32px_0_rgba(15,23,42,0.10)]">
            <div className="flex items-center justify-between mb-3.5">
              <div>
                <h3 className="text-xl font-heading font-bold text-[#101410]">
                  Retrieved <span className="font-calligraphy font-normal italic text-[#175A67] text-2xl pl-1 inline-block">Evidence</span>
                </h3>
                <p className="font-heading italic text-xs text-[#263B40]">
                  {retrievedPassages.length} verified passages from SQLite repository
                </p>
              </div>
              <button
                className="p-1 rounded-lg hover:bg-white/70 transition-colors text-slate-600 hover:text-slate-950 cursor-pointer"
                onClick={() => setShowEvidence(!showEvidence)}
                aria-label="Toggle evidence view"
              >
                {showEvidence ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              </button>
            </div>

            {showEvidence && (
              <div className="space-y-3 max-h-[640px] overflow-y-auto pr-1">
                {isLoading ? (
                  <LoadingSkeleton variant="text" count={3} />
                ) : retrievedPassages.length > 0 ? (
                  retrievedPassages.map((passage, idx) => (
                    <div
                      key={idx}
                      className="p-3.5 rounded-xl bg-white/60 hover:bg-white/90 backdrop-blur-sm border border-white/80 shadow-2xs transition-all"
                    >
                      <div className="flex items-center justify-between gap-1 mb-1.5 pb-1 border-b border-slate-200/50">
                        <span className="text-[11px] font-bold text-[#175A67] truncate">
                          {passage.title}
                        </span>
                        {passage.page_reference && (
                          <span className="text-[10px] font-mono px-2 py-0.5 rounded-md bg-[#E2ECED] text-[#175A67] font-semibold shrink-0">
                            {passage.page_reference}
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-slate-800 leading-relaxed font-normal">
                        {passage.content}
                      </p>
                      {passage.section_heading && (
                        <div className="mt-2 text-[10px] text-slate-500 font-medium">
                          Section: <span className="text-slate-700">{passage.section_heading}</span>
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <EmptyState
                    icon={<BookOpen className="h-8 w-8 text-slate-400" />}
                    title="No evidence passages"
                    description="Run a frontline query to retrieve cited passages with section citations and page references."
                  />
                )}
              </div>
            )}
          </Card>

          {/* Quick Actions & Escalation Hub */}
          <Card padding="md" className="border-white/80 shadow-[0_8px_32px_0_rgba(15,23,42,0.10)] bg-white/70">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600 mb-2.5">
              Workspace Actions
            </h4>
            <div className="flex flex-col gap-2">
              <Button
                variant="secondary"
                onClick={handleSave}
                disabled={!answer || isLoading}
                className="w-full justify-center cursor-pointer text-xs"
              >
                <Save className="h-3.5 w-3.5" />
                {saved ? 'Saved to Knowledge Workspace' : 'Save Answer to Workspace'}
              </Button>
              <Button
                variant="ghost"
                onClick={handleOpenEscalateModal}
                disabled={!question || isLoading}
                className="w-full justify-center text-rose-800 hover:bg-rose-50/80 cursor-pointer text-xs border border-rose-200/60"
              >
                <XCircle className="h-3.5 w-3.5" />
                Escalate Guidance Gap
              </Button>
              <Button
                variant="ghost"
                onClick={() => navigate('/escalation')}
                className="w-full justify-center text-slate-700 hover:bg-slate-100 cursor-pointer text-xs"
              >
                <ExternalLink className="h-3.5 w-3.5" />
                Open Escalation Center
              </Button>
            </div>
          </Card>
        </div>
      </div>

      {/* Escalation Modal Dialog */}
      <Modal
        isOpen={showEscalateModal}
        onClose={() => setShowEscalateModal(false)}
        title="Escalate Frontline Knowledge Discrepancy"
        size="md"
      >
        <div className="space-y-4 py-1">
          {escalateSuccess ? (
            <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-300 text-emerald-900 text-sm flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0" />
              <span>{escalateSuccess}</span>
            </div>
          ) : (
            <>
              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-slate-700 block mb-1">
                  Query / Discrepancy Description
                </label>
                <input
                  type="text"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  className="glass-input w-full px-3.5 py-2.5 rounded-xl text-sm text-slate-900"
                  placeholder="Describe the missing guidance or conflict..."
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
                      onClick={() => setEscalatePriority(p)}
                      className={`py-2 px-2.5 rounded-xl text-xs font-bold uppercase tracking-wider border cursor-pointer ${
                        escalatePriority === p
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
                  Context / Missing Evidence Details
                </label>
                <textarea
                  value={escalateContext}
                  onChange={(e) => setEscalateContext(e.target.value)}
                  rows={4}
                  className="glass-input w-full px-3.5 py-2.5 rounded-xl text-xs text-slate-900 resize-vertical leading-relaxed"
                  placeholder="Provide operational circumstances, equipment IDs, or missing SOP sections..."
                />
              </div>

              <div className="flex justify-end gap-2.5 pt-2 border-t border-slate-200">
                <Button
                  variant="ghost"
                  onClick={() => setShowEscalateModal(false)}
                  disabled={isEscalating}
                >
                  Cancel
                </Button>
                <Button
                  variant="primary"
                  onClick={handleConfirmEscalation}
                  isLoading={isEscalating}
                  className="bg-[#175A67] hover:bg-[#0F454F]"
                >
                  Submit Escalation
                </Button>
              </div>
            </>
          )}
        </div>
      </Modal>
    </div>
  );
}

import React, { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Search,
  FileText,
  BookOpen,
  Star,
  Clock,
  ArrowRight,
  CheckCircle,
  AlertCircle,
  Bell,
  Users,
  HelpCircle,
  ShieldAlert,
} from 'lucide-react';
import { Card, Button } from '@/components/ui';
import { useUser } from '@/context/UserContext';
import type { Document, ActivityItem } from '@/types/app';

// Demo data for recently accessed documents
const demoDocuments: Document[] = [
  {
    id: 'doc-001',
    title: 'Standard Operating Procedure: Field Equipment Calibration',
    content: 'This SOP defines standardized quarterly calibration for all field measurement equipment using certified standards.',
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
    downloadedCount: 142,
    viewCount: 289,
  },
  {
    id: 'doc-002',
    title: 'Safety Protocol for Hazardous Materials Handling',
    content: 'Outlines mandatory safety procedures and personal protective equipment for hazardous chemical handling.',
    sourceOrganization: 'Safety & Compliance Team',
    documentType: 'Policy',
    category: 'Safety',
    version: '2.1',
    status: 'active',
    effectiveDate: '2026-09-01',
    size: 187000,
    uploadedAt: '2026-09-05T14:15:00Z',
    url: '#',
    uploadedByName: 'Safety Director',
    downloadedCount: 98,
    viewCount: 412,
  },
  {
    id: 'doc-003',
    title: 'Field Teams Quick Reference & Emergency Contacts',
    content: 'Quick reference guide with emergency contacts, regional dispatchers, and evacuation triage routes.',
    sourceOrganization: 'Operations Support',
    documentType: 'Standard',
    category: 'Operations',
    version: '1.4',
    status: 'active',
    effectiveDate: '2026-04-10',
    size: 142000,
    uploadedAt: '2026-04-12T09:00:00Z',
    url: '#',
    uploadedByName: 'Operations Lead',
    downloadedCount: 215,
    viewCount: 560,
  },
];

const demoActivity: ActivityItem[] = [
  {
    id: 'act-001',
    type: 'upload',
    title: 'New SOP Uploaded',
    description: 'Field Equipment Calibration v3.2 added to library',
    timestamp: '2026-11-03T16:30:00Z',
    userId: 'u-001',
  },
  {
    id: 'act-002',
    type: 'search',
    title: 'High-Volume Search Query',
    description: '14 field engineers queried Hazardous Chemical PPE in last 24h',
    timestamp: '2026-11-03T15:10:00Z',
    userId: 'u-002',
  },
  {
    id: 'act-003',
    type: 'escalation',
    title: 'Policy Ambiguity Escalated',
    description: 'Discrepancy reported between Confined Space protocols',
    timestamp: '2026-11-03T12:45:00Z',
    userId: 'u-003',
  },
  {
    id: 'act-004',
    type: 'answer',
    title: 'Verified Answer Grounded',
    description: 'Automated citation verified for Pressure Gauge Zeroing Protocol',
    timestamp: '2026-11-03T11:20:00Z',
    userId: 'u-004',
  },
];

export function OverviewDashboard() {
  const navigate = useNavigate();
  const { user } = useUser();
  const [searchQuery, setSearchQuery] = useState('');
  const [recentDocuments] = useState<Document[]>(demoDocuments);
  const [savedItemsCount] = useState<number>(12);
  const [openEscalationsCount] = useState<number>(3);
  const [warningsCount] = useState<number>(1);
  const searchInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === '/' && document.activeElement !== searchInputRef.current) {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleAsk = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/ask?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const handleQuickQuery = (query: string) => {
    navigate(`/ask?q=${encodeURIComponent(query)}`);
  };

  const widgets = [
    {
      label: 'Documents Retrieved',
      value: '472',
      change: '+12.5%',
      icon: FileText,
      color: 'bg-[#E2ECED] text-[#175A67] border-[#175A67]/20',
    },
    {
      label: 'Active Educators',
      value: '23',
      change: '+3.1%',
      icon: Users,
      color: 'bg-[#E2ECED] text-[#175A67] border-[#175A67]/20',
    },
    {
      label: 'Answers Saved',
      value: '1,204',
      change: '+8.7%',
      icon: Star,
      color: 'bg-[#E2ECED] text-[#175A67] border-[#175A67]/20',
    },
    {
      label: 'Accessed Today',
      value: '68',
      change: '-2.4%',
      icon: Clock,
      color: 'bg-[#E2ECED] text-[#175A67] border-[#175A67]/20',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Top Welcome Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pt-1">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#E2ECED]/90 border border-[#175A67]/20 text-[#175A67] text-xs font-semibold tracking-wide mb-2 backdrop-blur-xs">
            <span>✦ Frontline Knowledge & SOP Retrieval Workspace</span>
          </div>
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-heading font-bold text-[#101410] tracking-tight leading-tight">
            Welcome back,{' '}
            <span className="font-calligraphy font-normal italic text-[#175A67] text-4xl sm:text-5xl md:text-6xl pl-1 inline-block">
              {user.name.split(' ')[0] || user.name}
            </span>
          </h1>

          <p className="font-heading italic text-base sm:text-lg text-[#263B40] mt-1 font-medium leading-relaxed max-w-2xl">
            Here's what's happening in your knowledge workspace today. Instant, cited answers from 4,800+ operational SOPs.
          </p>
          <p className="font-caveat text-base sm:text-lg text-[#175A67] mt-1 font-semibold tracking-wide">
            // Zero hallucinations · Direct page citations
          </p>
        </div>

        {/* User Card Pill */}
        <div
          onClick={() => navigate('/settings')}
          className="flex items-center gap-3 self-start md:self-auto p-2 sm:p-2.5 rounded-2xl bg-white/45 backdrop-blur-xl border border-white/70 shadow-[inset_0_1px_1px_rgba(255,255,255,0.8),0_4px_20px_rgba(23,90,103,0.05)] cursor-pointer hover:bg-white/60 transition-all"
          title="Click to manage profile and workspace settings"
        >
          <div className="h-10 w-10 rounded-full bg-[#E2ECED]/90 flex items-center justify-center text-sm font-bold text-[#175A67] border border-[#175A67]/25 shadow-2xs">
            {user.initials}
          </div>
          <div className="text-left pr-2">
            <p className="text-sm font-bold text-[#101410] leading-tight">{user.name}</p>
            <p className="text-xs text-[#263B40] leading-tight mt-0.5">{user.formattedRole}</p>
          </div>
          <div className="h-9 w-9 rounded-xl bg-white/60 backdrop-blur-sm border border-white/75 flex items-center justify-center text-[#263B40] hover:text-[#101410] cursor-pointer transition-colors shadow-2xs">
            <Bell className="h-4 w-4" />
          </div>
        </div>
      </div>

      {/* Main Search Panel */}
      <Card padding="lg" className="relative shadow-[inset_0_1px_1px_rgba(255,255,255,0.85),0_8px_30px_0_rgba(23,90,103,0.06)]">
        <form onSubmit={handleAsk} className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 sm:gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-[#263B40] pointer-events-none" />
            <input
              ref={searchInputRef}
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="glass-input w-full pl-11 pr-12 py-3.5 rounded-xl text-base sm:text-sm text-[#101410] placeholder-[#263B40]/70 focus:outline-none focus:border-[#175A67]"
              placeholder="Ask anything about your knowledge base..."
            />
            <kbd className="absolute right-3.5 top-1/2 -translate-y-1/2 text-xs font-mono text-[#263B40] bg-[#EAE3DE]/90 px-2 py-0.5 rounded-lg border border-[#175A67]/20 shadow-2xs pointer-events-none">
              /
            </kbd>
          </div>

          <div className="flex gap-3 shrink-0 items-center">
            <Button
              type="submit"
              variant="primary"
              className="h-11 sm:h-12 px-6 rounded-xl font-bold shadow-sm hover:shadow-[0_4px_16px_rgba(23,90,103,0.25)] cursor-pointer"
            >
              <Search className="h-4 w-4" />
              <span>Ask</span>
            </Button>

            <Button
              type="button"
              variant="mint"
              onClick={() => navigate('/library')}
              className="h-11 sm:h-12 px-5 rounded-xl font-semibold cursor-pointer"
            >
              <BookOpen className="h-4 w-4" />
              <span>Browse</span>
            </Button>
          </div>
        </form>
      </Card>

      {/* Quick Access Categories */}
      <Card padding="lg">
        <div className="mb-4">
          <h2 className="section-heading text-2xl sm:text-3xl font-heading font-bold text-[#101410]">
            Quick <span className="font-calligraphy font-normal italic text-[#175A67] text-2xl sm:text-3xl pl-1 inline-block">Access</span>
          </h2>
          <p className="section-subheading font-heading italic text-sm text-[#263B40]">
            Frequently used documents and operational topics
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
          {[
            {
              label: 'Calibration SOP',
              icon: FileText,
              count: '38 items',
              query: 'What is the standard calibration procedure and schedule for field sensors?',
            },
            {
              label: 'Safety Protocol',
              icon: AlertCircle,
              count: '24 items',
              query: 'What are the safety requirements and PPE for hazardous materials?',
            },
            {
              label: 'Field Teams',
              icon: Users,
              count: '19 items',
              query: 'What standard operating procedures apply to field operations teams?',
            },
            {
              label: 'Incident Reports',
              icon: ShieldAlert,
              count: '12 items',
              query: 'What are the emergency incident reporting and escalation procedures?',
            },
          ].map((item, i) => (
            <div
              key={i}
              onClick={() => handleQuickQuery(item.query)}
              className="group flex items-center justify-between p-3.5 sm:p-4 rounded-xl bg-white/35 backdrop-blur-md border border-white/55 hover:bg-white/65 hover:border-white/85 shadow-[inset_0_1px_1px_rgba(255,255,255,0.7),0_4px_16px_rgba(23,90,103,0.03)] hover:shadow-[0_8px_24px_rgba(23,90,103,0.07)] hover:-translate-y-0.5 transition-all duration-200 cursor-pointer"
            >
              <div className="flex items-center gap-3.5 min-w-0 flex-1">
                <div className="h-11 w-11 shrink-0 rounded-xl flex items-center justify-center bg-[#E2ECED]/85 text-[#175A67] border border-[#175A67]/20 shadow-2xs transition-transform group-hover:scale-105">
                  <item.icon className="h-5 w-5" />
                </div>
                <div className="min-w-0 flex-1 text-left">
                  <p className="text-sm font-bold text-[#101410] truncate group-hover:text-[#175A67] transition-colors">
                    {item.label}
                  </p>
                  <p className="text-xs text-[#263B40] mt-0.5 font-medium">
                    {item.count}
                  </p>
                </div>
              </div>
              <ArrowRight className="h-4 w-4 shrink-0 text-[#263B40] group-hover:text-[#175A67] group-hover:translate-x-1 transition-all ml-2" />
            </div>
          ))}
        </div>
      </Card>

      {/* 4 Metric Stat Boxes - Aligned & Responsive Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {widgets.map((widget, i) => (
          <Card
            key={i}
            padding="md"
            hover
            className="flex flex-col justify-between border-white/85 shadow-[0_8px_24px_0_rgba(23,90,103,0.06)]"
          >
            <div className="flex items-center justify-between gap-3">
              <div className="min-w-0 flex-1">
                <p className="text-xs font-semibold uppercase tracking-wider text-[#4A5B5E]">
                  {widget.label}
                </p>
                <p className="text-3xl sm:text-4xl font-extrabold font-display text-[#101410] mt-1 tracking-tight">
                  {widget.value}
                </p>
              </div>
              <div className={`h-12 w-12 shrink-0 rounded-2xl flex items-center justify-center ${widget.color} backdrop-blur-sm border shadow-2xs`}>
                <widget.icon className="h-6 w-6" />
              </div>
            </div>

            <div className="mt-3.5 pt-2.5 border-t border-[#175A67]/15 flex items-center gap-1.5 text-xs">
              <span className={`font-bold ${widget.change.startsWith('+') ? 'text-[#175A67]' : 'text-[#4A5B5E]'}`}>
                {widget.change}
              </span>
              <span className="font-heading italic text-[#4A5B5E]">vs last month</span>
            </div>
          </Card>
        ))}
      </div>

      {/* Two Column Section: Recently Accessed SOPs & Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recently Accessed Documents - 2 Cols */}
        <div className="lg:col-span-2">
          <Card padding="lg" className="h-full border-white/85 shadow-[0_8px_32px_0_rgba(23,90,103,0.06)]">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="section-heading text-2xl sm:text-3xl font-heading font-bold text-[#101410]">
                  Recently <span className="font-calligraphy font-normal italic text-[#175A67] text-2xl sm:text-3xl pl-1 inline-block">Accessed</span>
                </h2>
                <p className="section-subheading font-heading italic text-xs sm:text-sm text-[#263B40]">
                  Your verified field documents and operational manuals
                </p>
              </div>
              <Link
                to="/library"
                className="text-xs font-bold text-[#175A67] hover:underline inline-flex items-center gap-1 font-heading italic"
              >
                View all <ArrowRight className="h-3 w-3" />
              </Link>
            </div>

            <div className="space-y-3">
              {recentDocuments.map((doc) => (
                <div
                  key={doc.id}
                  onClick={() => navigate(`/library/${doc.id}`)}
                  className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3.5 rounded-2xl bg-white/35 hover:bg-white/65 backdrop-blur-md border border-white/55 hover:border-white/85 shadow-[inset_0_1px_1px_rgba(255,255,255,0.7),0_4px_16px_rgba(23,90,103,0.03)] hover:shadow-[0_8px_24px_rgba(23,90,103,0.07)] transition-all cursor-pointer group"
                >
                  <div className="flex items-center gap-3.5 min-w-0 flex-1">
                    <div className="h-10 w-10 shrink-0 rounded-xl bg-[#E2ECED]/85 flex items-center justify-center border border-[#175A67]/20 text-[#175A67] shadow-2xs">
                      <FileText className="h-5 w-5" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-bold text-[#101410] truncate group-hover:text-[#175A67] transition-colors">
                        {doc.title}
                      </p>
                      <p className="text-xs text-[#263B40] mt-0.5">{doc.sourceOrganization}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 text-xs text-[#263B40] shrink-0 pl-13 sm:pl-0">
                    <span className="inline-flex items-center gap-1.5 bg-white/55 backdrop-blur-xs px-2.5 py-1 rounded-lg border border-white/70 shadow-2xs font-semibold">
                      <FileText className="h-3.5 w-3.5 text-[#263B40]" /> {doc.downloadedCount}
                    </span>
                    <span className="inline-flex items-center gap-1.5 bg-white/55 backdrop-blur-xs px-2.5 py-1 rounded-lg border border-white/70 shadow-2xs font-semibold">
                      <Clock className="h-3.5 w-3.5 text-[#263B40]" /> {doc.viewCount}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Recent Activity Feed - 1 Col */}
        <div className="lg:col-span-1">
          <Card padding="lg" className="h-full">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="section-heading text-2xl sm:text-3xl font-heading font-bold text-[#101410]">
                  Live <span className="font-calligraphy font-normal italic text-[#175A67] text-2xl sm:text-3xl pl-1 inline-block">Activity</span>
                </h2>
                <p className="section-subheading font-heading italic text-xs sm:text-sm text-[#263B40]">Real-time knowledge events</p>
              </div>
              <Link to="/activity" className="text-xs font-bold text-[#175A67] hover:underline font-heading italic">
                View all
              </Link>
            </div>

            <div className="space-y-3">
              {demoActivity.slice(0, 4).map((activity) => (
                <div
                  key={activity.id}
                  className="flex items-start gap-3 p-3 rounded-2xl bg-white/40 border border-white/60 backdrop-blur-sm shadow-2xs"
                >
                  <div
                    className={`shrink-0 h-8 w-8 rounded-xl flex items-center justify-center mt-0.5 ${
                      activity.type === 'upload'
                        ? 'bg-[#E2ECED] text-[#175A67] border border-[#175A67]/25'
                        : activity.type === 'search'
                        ? 'bg-blue-100/90 text-blue-900 border border-blue-300'
                        : activity.type === 'escalation'
                        ? 'bg-amber-100/90 text-amber-900 border border-amber-300'
                        : 'bg-slate-100/90 text-slate-900 border border-slate-300'
                    }`}
                  >
                    {activity.type === 'upload' && <FileText className="h-4 w-4" />}
                    {activity.type === 'search' && <Search className="h-4 w-4" />}
                    {activity.type === 'escalation' && <HelpCircle className="h-4 w-4" />}
                    {activity.type === 'answer' && <CheckCircle className="h-4 w-4" />}
                    {activity.type === 'download' && <FileText className="h-4 w-4" />}
                  </div>

                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-bold text-[#101410] truncate">{activity.title}</p>
                    <p className="text-[11px] text-[#263B40] truncate mt-0.5">{activity.description}</p>
                    <p className="text-[10px] text-[#263B40] mt-1 font-mono">
                      {new Date(activity.timestamp).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>

      {/* Saved Items & Escalations Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card padding="lg" hover className="border-white/85 shadow-[0_8px_32px_0_rgba(23,90,103,0.06)]">
          <div className="flex items-center justify-between mb-4">
            <h2 className="section-heading text-xl sm:text-2xl font-heading font-bold text-[#101410]">
              Saved <span className="font-calligraphy font-normal italic text-[#175A67] text-2xl sm:text-3xl pl-1 inline-block">Items</span>
            </h2>
            <Link to="/saved" className="text-xs font-bold text-[#175A67] hover:underline font-heading italic">
              View all
            </Link>
          </div>
          <div className="flex items-center gap-4 p-3.5 rounded-2xl bg-white/45 backdrop-blur-md border border-white/65 shadow-[inset_0_1px_1px_rgba(255,255,255,0.7),0_4px_16px_rgba(23,90,103,0.04)]">
            <div className="h-12 w-12 rounded-2xl bg-[#E2ECED]/85 flex items-center justify-center text-[#175A67] border border-[#175A67]/25 shadow-2xs">
              <Star className="h-6 w-6" />
            </div>
            <div>
              <p className="text-3xl font-extrabold font-display text-[#101410]">{savedItemsCount}</p>
              <p className="font-heading italic text-xs sm:text-sm text-[#263B40] mt-0.5 font-medium">Bookmarked answers & key SOPs</p>
            </div>
          </div>
        </Card>

        <Card padding="lg" hover>
          <div className="flex items-center justify-between mb-4">
            <h2 className="section-heading text-xl sm:text-2xl font-heading font-bold text-[#101410]">
              Active <span className="font-calligraphy font-normal italic text-[#175A67] text-2xl sm:text-3xl pl-1 inline-block">Escalations</span>
            </h2>
            <Link to="/escalation" className="text-xs font-bold text-[#175A67] hover:underline font-heading italic">
              View all
            </Link>
          </div>
          <div className="grid grid-cols-2 gap-3.5">
            <div className="flex items-center gap-3 p-3.5 rounded-2xl bg-amber-50/50 backdrop-blur-md border border-amber-200/60 shadow-2xs">
              <div className="h-10 w-10 shrink-0 rounded-xl bg-amber-100/80 flex items-center justify-center text-amber-800 border border-amber-300">
                <AlertCircle className="h-5 w-5" />
              </div>
              <div className="min-w-0">
                <p className="text-2xl font-extrabold font-display text-[#101410]">{openEscalationsCount}</p>
                <p className="font-heading italic text-xs text-[#263B40] mt-0.5 truncate font-medium">Open cases</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3.5 rounded-2xl bg-rose-50/50 backdrop-blur-md border border-rose-200/60 shadow-2xs">
              <div className="h-10 w-10 shrink-0 rounded-xl bg-rose-100/80 flex items-center justify-center text-rose-800 border border-rose-300">
                <ShieldAlert className="h-5 w-5" />
              </div>
              <div className="min-w-0">
                <p className="text-2xl font-extrabold font-display text-[#101410]">{warningsCount}</p>
                <p className="font-heading italic text-xs text-[#263B40] mt-0.5 truncate font-medium">Active warnings</p>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}

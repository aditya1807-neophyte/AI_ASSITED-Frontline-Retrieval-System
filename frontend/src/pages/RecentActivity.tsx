import { Link } from 'react-router-dom';
import { Clock, FileText, Search, Activity, AlertTriangle, ArrowRight } from 'lucide-react';
import { Card } from '@/components/ui';
import type { ActivityItem } from '@/types/app';

const demoActivity: ActivityItem[] = [
  { id: 'act-001', type: 'upload', title: 'Field Equipment SOP uploaded', description: 'SOP-001 v3.2 by Jordan Diaz', timestamp: '2026-10-20T14:30:00Z', userId: 'u-001', documentId: 'doc-001' },
  { id: 'act-002', type: 'search', title: 'Search: "calibration frequency"', description: '2 answers generated from 3 documents', timestamp: '2026-10-20T11:15:00Z', userId: 'u-002' },
  { id: 'act-003', type: 'escalation', title: 'Escalation: HVAC calibration', description: 'Priority high, assigned to Engineering Lead', timestamp: '2026-10-19T09:20:00Z', userId: 'u-003' },
  { id: 'act-004', type: 'download', title: 'Safety Protocol downloaded', description: 'Safety & Compliance Team', timestamp: '2026-10-19T08:00:00Z', userId: 'u-004', documentId: 'doc-002' },
  { id: 'act-005', type: 'answer', title: 'Answer saved: Calibration schedule', description: 'Answer with 2 cited sources', timestamp: '2026-10-18T16:45:00Z', userId: 'u-005' },
  { id: 'act-006', type: 'view', title: 'Field Equipment Guide viewed', description: 'Document 42 views this month', timestamp: '2026-10-18T10:15:00Z', userId: 'u-006', documentId: 'doc-003' },
  { id: 'act-007', type: 'upload', title: 'Incident Reporting Protocol uploaded', description: 'Risk Management', timestamp: '2026-10-17T13:00:00Z', userId: 'u-007', documentId: 'doc-004' },
  { id: 'act-008', type: 'search', title: 'Search: "safety training"', description: '1 answer generated', timestamp: '2026-10-17T09:30:00Z', userId: 'u-008' },
];

const activityIcons = {
  upload: <FileText className="h-5 w-5 text-[#175A67]" />,
  download: <FileText className="h-5 w-5 text-slate-600" />,
  view: <FileText className="h-5 w-5 text-slate-600" />,
  search: <Search className="h-5 w-5 text-blue-800" />,
  answer: <Activity className="h-5 w-5 text-[#175A67]" />,
  escalation: <AlertTriangle className="h-5 w-5 text-amber-800" />,
};

const activityColors = {
  upload: 'bg-[#E2ECED] border-[#175A67]/20',
  download: 'bg-slate-100 border-slate-300',
  view: 'bg-slate-100 border-slate-300',
  search: 'bg-blue-100 border-blue-300',
  answer: 'bg-[#E2ECED] border-[#175A67]/20',
  escalation: 'bg-amber-100 border-amber-300',
};

export function RecentActivity() {
  return (
    <div className="space-y-6 sm:space-y-7">
      <div className="flex items-center gap-3.5 mb-6">
        <div className="h-12 w-12 rounded-2xl bg-[#E2ECED] backdrop-blur-md flex items-center justify-center border border-[#175A67]/20 text-[#175A67] shadow-2xs">
          <Clock className="h-6 w-6" />
        </div>
        <div>
          <h1 className="text-3xl sm:text-4xl font-heading font-bold text-[#101410] tracking-tight leading-tight">
            Recent <span className="font-calligraphy font-normal italic text-[#175A67] text-4xl sm:text-5xl pl-1 inline-block">Activity</span>
          </h1>
          <p className="font-heading italic text-sm text-[#263B40] mt-1 font-medium">Audit log and live operational events across your frontline knowledge workspace.</p>
        </div>
      </div>

      <Card padding="lg" className="border-white/85 shadow-[0_8px_32px_0_rgba(23,90,103,0.06)]">
        <div className="space-y-3">
          {demoActivity.map((activity) => (
            <div
              key={activity.id}
              className="flex items-center justify-between gap-4 p-4 rounded-2xl bg-white/55 hover:bg-white/85 backdrop-blur-md border border-white/70 hover:border-white/95 transition-all shadow-2xs group"
            >
              <div className="flex items-center gap-3.5 min-w-0 flex-1">
                <div
                  className={`h-10 w-10 rounded-xl flex items-center justify-center shrink-0 border shadow-2xs ${activityColors[activity.type]}`}
                >
                  {activityIcons[activity.type]}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-semibold text-slate-900 truncate group-hover:text-[#175A67] transition-colors">
                    {activity.title}
                  </p>
                  <p className="text-xs text-slate-600 mt-0.5 truncate">{activity.description}</p>
                </div>
              </div>
              <div className="flex items-center gap-4 shrink-0 text-xs text-slate-500 font-mono">
                <span>{new Date(activity.timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>
                {activity.documentId && (
                  <Link
                    to={`/library/${activity.documentId}`}
                    className="p-1.5 rounded-lg bg-white/70 hover:bg-white text-[#175A67] border border-white/80"
                  >
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                )}
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

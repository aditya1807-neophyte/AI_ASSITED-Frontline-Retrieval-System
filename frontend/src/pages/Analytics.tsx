import { BarChart3, Clock, AlertTriangle, CheckCircle, FileText } from 'lucide-react';
import { Card, Badge } from '@/components/ui';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

// Mock data for charts
const usageData = [
  { month: 'Jan', value: 45 },
  { month: 'Feb', value: 52 },
  { month: 'Mar', value: 48 },
  { month: 'Apr', value: 62 },
  { month: 'May', value: 71 },
  { month: 'Jun', value: 68 },
  { month: 'Jul', value: 85 },
  { month: 'Aug', value: 92 },
];

const answerDistribution = [
  { name: 'Q&A', value: 45 },
  { name: 'Count', value: 24 },
  { name: 'Recommendation', value: 22 },
  { name: 'Comparison', value: 9 },
];

const chartColors = ['#175A67', '#D97706', '#2563EB', '#64748B'];

export function Analytics() {
  return (
    <div className="space-y-6 sm:space-y-7">
      <div className="flex items-center gap-3.5 mb-6">
        <div className="h-12 w-12 rounded-2xl bg-[#E2ECED] backdrop-blur-md flex items-center justify-center border border-[#175A67]/20 text-[#175A67] shadow-2xs">
          <BarChart3 className="h-6 w-6" />
        </div>
        <div>
          <h1 className="text-3xl sm:text-4xl font-heading font-bold text-[#101410] tracking-tight leading-tight">
            Knowledge <span className="font-calligraphy font-normal italic text-[#175A67] text-4xl sm:text-5xl pl-1 inline-block">Analytics</span>
          </h1>
          <p className="font-heading italic text-sm text-[#263B40] mt-1 font-medium">Telemetry, retrieval efficiency, and field user interaction metrics.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Usage over time - line chart */}
        <Card padding="lg" className="border-white/80 shadow-[0_8px_32px_0_rgba(15,23,42,0.10)]">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="section-heading text-xl font-heading font-bold text-[#101410]">
                Knowledge <span className="font-calligraphy font-normal italic text-[#175A67] text-2xl pl-1 inline-block">Usage</span>
              </h3>
              <p className="font-heading italic text-xs text-[#263B40]">Documents accessed per month</p>
            </div>
            <Badge tone="info" size="sm">8 Months</Badge>
          </div>
          <div className="h-64">
            <ResponsiveContainer>
              <LineChart data={usageData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.6)" />
                <XAxis dataKey="month" stroke="#64748B" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="#64748B" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip
                  contentStyle={{
                    background: 'rgba(255, 255, 255, 0.92)',
                    backdropFilter: 'blur(12px)',
                    border: '1px solid rgba(255, 255, 255, 0.8)',
                    borderRadius: '0.75rem',
                    fontSize: '12px',
                    boxShadow: '0 8px 24px rgba(15,23,42,0.12)',
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#175A67"
                  strokeWidth={2.5}
                  dot={{ fill: '#15803D', strokeWidth: 2, r: 4 }}
                  activeDot={{ r: 6, stroke: '#15803D', strokeWidth: 2 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Answer distribution - donut chart */}
        <Card padding="lg" className="border-white/80 shadow-[0_8px_32px_0_rgba(15,23,42,0.10)]">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="section-heading text-xl font-heading font-bold text-[#101410]">
                Answer <span className="font-calligraphy font-normal italic text-[#175A67] text-2xl pl-1 inline-block">Types</span>
              </h3>
              <p className="font-heading italic text-xs text-[#263B40]">Distribution of generated answers</p>
            </div>
            <Badge tone="info" size="sm">122</Badge>
          </div>
          <div className="h-64 flex items-center justify-center">
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  data={answerDistribution}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={95}
                  fill="#15803D"
                  label
                  labelLine={true}
                >
                  {answerDistribution.map((_, i) => (
                    <Cell key={i} fill={chartColors[i % chartColors.length]} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Activity summary - cards */}
        <Card padding="lg" className="lg:col-span-2 border-white/80 shadow-[0_8px_32px_0_rgba(15,23,42,0.10)]">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Documents Retrieved', value: '472', icon: FileText, color: 'bg-[#E2ECED] text-[#175A67] border-[#175A67]/20', prefix: 'Total' },
              { label: 'Answers Generated', value: '891', icon: FileText, color: 'bg-blue-100 text-blue-800 border-blue-300', prefix: 'This month' },
              { label: 'Escalations', value: '12', icon: AlertTriangle, color: 'bg-amber-100 text-amber-800 border-amber-300', prefix: 'Open' },
              { label: 'Satisfaction', value: '94%', icon: CheckCircle, color: 'bg-[#E2ECED] text-[#175A67] border-[#175A67]/20', prefix: 'Satisfaction' },
            ].map((stat, i) => {
              const Icon = stat.icon;
              return (
                <div key={i} className="text-center p-3.5 rounded-2xl bg-white/50 backdrop-blur-sm border border-white/70 shadow-2xs">
                  <div className={`h-11 w-11 rounded-xl ${stat.color} flex items-center justify-center mx-auto mb-2.5 border shadow-2xs`}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <p className="text-2xl sm:text-3xl font-extrabold font-display text-[#101410]">{stat.value}</p>
                  <p className="text-xs text-slate-600 font-medium mt-0.5">{stat.label}</p>
                </div>
              );
            })}
          </div>
        </Card>
      </div>

      {/* Telemetry info */}
      <Card padding="lg" className="border-white/80 shadow-[0_8px_32px_0_rgba(15,23,42,0.10)]">
        <div className="flex items-start gap-3">
          <div className="h-9 w-9 rounded-xl bg-[#E2ECED] flex items-center justify-center shrink-0 border border-[#175A67]/20 text-[#175A67]">
            <Clock className="h-4 w-4" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-900">Live Analytics Telemetry</h4>
            <p className="text-xs text-slate-600 mt-0.5">
              Metrics are synced with real-time vector search and RAG retrieval pipelines. All latency logs and retrieval traces are stored in the telemetry audit store.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}

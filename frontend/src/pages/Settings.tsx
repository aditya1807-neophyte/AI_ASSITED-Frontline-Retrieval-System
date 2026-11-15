import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Settings as SettingsIcon, Save, CheckCircle2, AlertCircle } from 'lucide-react';
import { Card, CardHeader, Button, FormField, Badge } from '@/components/ui';
import { useUser, getInitials, formatRole } from '@/context/UserContext';

export function Settings() {
  const { user, updateProfile } = useUser();

  const [formData, setFormData] = useState({
    name: user.name,
    email: user.email,
    role: user.role,
    language: user.language,
    notifications: user.notifications,
    weeklyDigest: user.weeklyDigest,
    autoSaveAnswers: user.autoSaveAnswers,
  });

  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);

  // Sync form when user profile changes
  useEffect(() => {
    setFormData({
      name: user.name,
      email: user.email,
      role: user.role,
      language: user.language,
      notifications: user.notifications,
      weeklyDigest: user.weeklyDigest,
      autoSaveAnswers: user.autoSaveAnswers,
    });
  }, [user]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSave = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!formData.name.trim()) {
      setSaveError('Full Name cannot be empty.');
      return;
    }

    setIsSaving(true);
    setSaveError(null);
    setSaveSuccess(null);

    try {
      await updateProfile({
        name: formData.name.trim(),
        email: formData.email.trim(),
        role: formData.role,
        language: formData.language,
        notifications: formData.notifications,
        weeklyDigest: formData.weeklyDigest,
        autoSaveAnswers: formData.autoSaveAnswers,
      });

      setSaveSuccess('Profile and preferences successfully saved and synced across workspace!');
      setTimeout(() => {
        setSaveSuccess(null);
      }, 4000);
    } catch (err: any) {
      console.error('Failed to save settings:', err);
      setSaveError(err.message || 'Failed to save changes to profile.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6 sm:space-y-7">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div className="flex items-center gap-3.5">
          <div className="h-12 w-12 rounded-2xl bg-[#E2ECED] backdrop-blur-md flex items-center justify-center border border-[#175A67]/20 text-[#175A67] shadow-2xs">
            <SettingsIcon className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-3xl sm:text-4xl font-heading font-bold text-[#101410] tracking-tight leading-tight">
              Workspace <span className="font-calligraphy font-normal italic text-[#175A67] text-4xl sm:text-5xl pl-1 inline-block">Settings</span>
            </h1>
            <p className="font-heading italic text-sm text-[#263B40] mt-1 font-medium">
              Manage user profile identity, role context, and frontline application preferences.
            </p>
          </div>
        </div>

        {/* Live sync status pill */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-semibold bg-white/80 border border-white/90 text-[#175A67] shadow-2xs self-start sm:self-auto">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>Profile Synced: <strong>{user.name}</strong></span>
        </div>
      </div>

      {/* Success & Error Banners */}
      {saveSuccess && (
        <div className="p-4 rounded-2xl bg-emerald-50/90 border border-emerald-300 text-emerald-900 text-sm flex items-center gap-3 shadow-2xs animate-fadeIn">
          <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0" />
          <span className="font-medium">{saveSuccess}</span>
        </div>
      )}

      {saveError && (
        <div className="p-4 rounded-2xl bg-rose-50/90 border border-rose-300 text-rose-900 text-sm flex items-center gap-3 shadow-2xs animate-fadeIn">
          <AlertCircle className="h-5 w-5 text-rose-600 shrink-0" />
          <span className="font-medium">{saveError}</span>
        </div>
      )}

      <form onSubmit={handleSave}>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Profile Card */}
          <Card padding="lg" className="lg:col-span-2 border-white/85 shadow-[0_8px_32px_0_rgba(23,90,103,0.06)]">
            <CardHeader
              title="Profile Identity"
              subtitle="Your frontline account information and display identity"
              action={
                <Link to="/" className="text-xs font-semibold text-[#175A67] hover:underline">
                  View dashboard
                </Link>
              }
            />

            {/* Live Profile Badge Preview */}
            <div className="flex items-center gap-4 mb-6 p-4 rounded-2xl bg-white/50 backdrop-blur-sm border border-white/70 shadow-2xs">
              <div className="h-14 w-14 rounded-full bg-[#E2ECED] flex items-center justify-center border border-[#175A67]/25 text-[#175A67] font-bold text-lg shadow-2xs shrink-0 transition-transform">
                {getInitials(formData.name)}
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-base font-bold text-slate-900 truncate">
                  {formData.name || 'Anonymous User'}
                </p>
                <p className="text-xs text-slate-600 truncate mt-0.5">
                  {formData.email || `${user.login_identifier}@fieldguide.ai`}
                </p>
                <div className="mt-1.5 flex items-center gap-2">
                  <Badge tone="success" size="sm">
                    {formatRole(formData.role)}
                  </Badge>
                  <span className="text-[10px] text-slate-400 font-mono">ID #{user.id}</span>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <FormField
                label="Full Name *"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="e.g. Jordan Diaz"
              />
              <FormField
                label="Email Address"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="e.g. jordan.diaz@fieldguide.ai"
              />
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-600 block mb-1.5">
                  Frontline Role Context
                </label>
                <select
                  name="role"
                  className="glass-input w-full px-3.5 py-2.5 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-[#175A67]"
                  value={formData.role}
                  onChange={handleChange}
                >
                  <option value="analyst">Analyst</option>
                  <option value="manager">Manager</option>
                  <option value="field_technician">Field Technician</option>
                  <option value="safety_officer">Safety Officer</option>
                  <option value="maintenance_engineer">Maintenance Engineer</option>
                  <option value="site_supervisor">Site Supervisor</option>
                  <option value="admin">Administrator</option>
                </select>
                <p className="text-[11px] text-slate-500 mt-1">
                  Adjusting your frontline role tunes RAG retrieval priority and procedural context filters.
                </p>
              </div>
            </div>
          </Card>

          {/* Notification preferences */}
          <Card padding="lg" className="border-white/85 shadow-[0_8px_32px_0_rgba(23,90,103,0.06)]">
            <CardHeader
              title="Notifications"
              subtitle="Configure automated frontline alerts"
            />
            <div className="space-y-3.5">
              {[
                {
                  name: 'notifications',
                  label: 'Answer received alerts',
                  desc: 'Get notified when an AI answer is synthesized',
                  checked: formData.notifications,
                },
                {
                  name: 'weeklyDigest',
                  label: 'Weekly knowledge digest',
                  desc: 'Receive a weekly summary of SOP changes',
                  checked: formData.weeklyDigest,
                },
                {
                  name: 'autoSaveAnswers',
                  label: 'Auto-save answers',
                  desc: 'Automatically bookmark generated answers',
                  checked: formData.autoSaveAnswers,
                },
              ].map((item, i) => (
                <div key={i} className="flex items-center justify-between py-2.5 border-b border-white/60 last:border-0">
                  <div className="pr-2">
                    <p className="text-xs font-semibold text-slate-900">{item.label}</p>
                    <p className="text-[11px] text-slate-500">{item.desc}</p>
                  </div>
                  <input
                    type="checkbox"
                    name={item.name}
                    id={`notify-${i}`}
                    className="h-4 w-4 rounded border-slate-300 text-[#175A67] focus:ring-[#175A67] cursor-pointer"
                    checked={item.checked}
                    onChange={handleChange}
                  />
                </div>
              ))}
            </div>
          </Card>

          {/* Workspace settings */}
          <Card padding="lg" className="lg:col-span-3 border-white/85 shadow-[0_8px_32px_0_rgba(23,90,103,0.06)]">
            <CardHeader
              title="Workspace Localization"
              subtitle="Workspace defaults, languages, and regional settings"
            />
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-600 block mb-1.5">
                  Language
                </label>
                <select
                  name="language"
                  className="glass-input w-full px-3.5 py-2.5 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-[#175A67]"
                  value={formData.language}
                  onChange={handleChange}
                >
                  <option value="en">English (US)</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                </select>
              </div>
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-600 block mb-1.5">
                  Default Landing View
                </label>
                <select
                  className="glass-input w-full px-3.5 py-2.5 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-[#175A67]"
                  defaultValue="overview"
                >
                  <option value="overview">Overview Dashboard</option>
                  <option value="library">Knowledge Library</option>
                  <option value="ask">Ask Knowledge</option>
                  <option value="documents">Document Management</option>
                  <option value="activity">Recent Activity</option>
                </select>
              </div>
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-600 block mb-1.5">
                  Time Zone
                </label>
                <select
                  className="glass-input w-full px-3.5 py-2.5 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-[#175A67]"
                  defaultValue="utc-5"
                >
                  <option value="utc-8">Pacific Time (UTC-8)</option>
                  <option value="utc-5">Eastern Time (UTC-5)</option>
                  <option value="utc-0">UTC / GMT</option>
                  <option value="utc+5.5">India Standard Time (UTC+5:30)</option>
                </select>
              </div>
            </div>
          </Card>
        </div>

        {/* Save changes action */}
        <div className="flex justify-end pt-5">
          <Button
            variant="primary"
            type="submit"
            isLoading={isSaving}
            className="bg-[#175A67] hover:bg-[#0F454F] px-6 py-2.5 shadow-sm"
          >
            <Save className="h-4 w-4" />
            Save Changes
          </Button>
        </div>
      </form>
    </div>
  );
}

// Sidebar.tsx - Soft mint studio & frosted glass application sidebar
import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  BookOpen,
  Home,
  Search,
  Save,
  Clock,
  HelpCircle,
  BarChart3,
  Upload,
  Settings,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { useUser } from '@/context/UserContext';

interface NavItem {
  label: string;
  path: string;
  icon: React.ComponentType<{ className?: string }>;
}

const navigationItems: NavItem[] = [
  { label: 'Overview', path: '/', icon: Home },
  { label: 'Ask Knowledge', path: '/ask', icon: Search },
  { label: 'Knowledge Library', path: '/library', icon: BookOpen },
  { label: 'Saved Items', path: '/saved', icon: Save },
  { label: 'Recent Activity', path: '/activity', icon: Clock },
  { label: 'Escalation Center', path: '/escalation', icon: HelpCircle },
  { label: 'Analytics', path: '/analytics', icon: BarChart3 },
  { label: 'Document Management', path: '/documents', icon: Upload },
  { label: 'Settings', path: '/settings', icon: Settings },
];

interface SidebarProps {
  isExpanded: boolean;
  onToggle: () => void;
}

export function Sidebar({ isExpanded, onToggle }: SidebarProps) {
  const { user } = useUser();
  const navigate = useNavigate();
  return (
    <>
      {/* Mobile overlay */}
      {!isExpanded && (
        <div
          className="fixed inset-0 bg-black/40 backdrop-blur-sm z-30 lg:hidden"
          onClick={onToggle}
          aria-hidden="true"
        />
      )}

      <aside
        className={`${
          isExpanded ? 'w-64' : 'w-20'
        } bg-white/45 backdrop-blur-2xl border-r border-white/60 shadow-[4px_0_30px_rgba(23,90,103,0.04)] transition-all duration-200 flex flex-col py-4 px-3.5 z-20`}
        aria-label="Sidebar navigation"
      >
        {/* Brand Logo */}
        <div className="flex items-center justify-between mb-5 px-1.5 pt-1">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 bg-[#175A67] rounded-xl flex items-center justify-center shadow-md shadow-[#175A67]/20 border border-white/40">
              <svg className="w-5 h-5 text-[#FAF8F5]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
              </svg>
            </div>
            {isExpanded && (
              <div className="flex flex-col">
                <span className="text-xl font-heading font-bold text-[#101410] tracking-tight leading-none">
                  FieldGuide <span className="font-calligraphy text-2xl text-[#175A67] font-normal italic pl-0.5">AI</span>
                </span>
                <span className="text-[10px] uppercase font-semibold tracking-widest text-[#4A5B5E] mt-0.5">
                  Frontline Workspace
                </span>
              </div>
            )}
          </div>
          <button
            className="p-1.5 rounded-lg hover:bg-white/60 transition-colors lg:hidden text-[#4A5B5E] hover:text-[#101410] cursor-pointer"
            onClick={onToggle}
            aria-label={isExpanded ? 'Collapse sidebar' : 'Expand sidebar'}
          >
            {isExpanded ? (
              <ChevronLeft className="h-5 w-5" />
            ) : (
              <ChevronRight className="h-5 w-5" />
            )}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex flex-col gap-1.5 flex-1 overflow-y-auto">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-150 cursor-pointer ${
                    isActive
                      ? 'bg-[#E2ECED]/85 text-[#175A67] font-semibold border border-[#175A67]/25 shadow-2xs backdrop-blur-xs'
                      : 'text-[#263B40] hover:bg-white/55 hover:text-[#101410] hover:border hover:border-white/60'
                  } ${isExpanded ? 'justify-start' : 'justify-center'}`
                }
              >
                <Icon className="h-5 w-5 shrink-0" />
                {isExpanded && <span className="text-sm font-medium">{item.label}</span>}
              </NavLink>
            );
          })}
        </nav>

        {/* Bottom Profile Chip */}
        <div className="mt-auto pt-3 border-t border-white/50">
          {isExpanded ? (
            <button
              onClick={() => navigate('/settings')}
              className="w-full flex items-center gap-3 p-2 rounded-xl bg-white/45 backdrop-blur-md border border-white/60 hover:bg-white/70 shadow-2xs transition-all text-left cursor-pointer"
              title="View & edit profile settings"
            >
              <div className="h-9 w-9 rounded-full bg-[#E2ECED] flex items-center justify-center text-[#175A67] font-bold text-xs border border-[#175A67]/25 shrink-0">
                {user.initials}
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-semibold text-[#101410] truncate">{user.name}</p>
                <p className="text-[11px] text-[#263B40] truncate">{user.formattedRole}</p>
              </div>
            </button>
          ) : (
            <button
              onClick={() => navigate('/settings')}
              className="w-full flex justify-center p-1 cursor-pointer"
              title={`${user.name} (${user.formattedRole})`}
            >
              <div className="h-9 w-9 rounded-full bg-[#E2ECED] flex items-center justify-center text-[#175A67] font-bold text-xs border border-[#175A67]/25">
                {user.initials}
              </div>
            </button>
          )}
        </div>
      </aside>
    </>
  );
}

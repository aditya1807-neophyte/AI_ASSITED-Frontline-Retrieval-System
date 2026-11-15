// Header.tsx - Soft mint studio & frosted glass application header
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Bell, Menu } from 'lucide-react';
import { useUser } from '@/context/UserContext';

interface HeaderProps {
  onMenuClick: () => void;
  isSidebarExpanded: boolean;
  onToggleSidebar: () => void;
}

export function Header({ onMenuClick, isSidebarExpanded: _isSidebarExpanded }: HeaderProps) {
  const navigate = useNavigate();
  const { user } = useUser();
  const [query, setQuery] = useState('');

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/ask?q=${encodeURIComponent(query.trim())}`);
    }
  };

  return (
    <header className="bg-white/45 backdrop-blur-2xl border-b border-white/60 sticky top-0 z-20 shadow-[0_4px_20px_rgba(23,90,103,0.03)] transition-all">
      <div className="flex items-center justify-between h-16 px-4 sm:px-6">
        <div className="flex items-center gap-3">
          <button
            className="p-2 rounded-xl hover:bg-white/60 backdrop-blur-sm transition-colors lg:hidden text-[#263B40] hover:text-[#101410] cursor-pointer"
            onClick={onMenuClick}
            aria-label="Toggle sidebar"
          >
            <Menu className="h-5 w-5" />
          </button>
          <div className="flex items-center gap-2.5 lg:hidden">
            <div className="h-8 w-8 bg-[#175A67] rounded-lg flex items-center justify-center text-[#FAF8F5]">
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
              </svg>
            </div>
            <span className="text-base font-heading font-bold text-[#101410]">
              FieldGuide <span className="font-calligraphy text-lg text-[#175A67] font-normal italic pl-0.5">AI</span>
            </span>
          </div>
        </div>

        {/* Search bar */}
        <div className="flex-1 max-w-xl mx-2 sm:mx-6">
          <form onSubmit={handleSearchSubmit} className="relative">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-[#263B40] pointer-events-none" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="glass-input w-full pl-10 pr-10 py-2 rounded-xl text-sm text-[#101410] placeholder-[#263B40]/70 focus:outline-none focus:border-[#175A67] focus:ring-2 focus:ring-[#175A67]/15 transition-all"
              placeholder="Search... (Press / to search)"
            />
            <kbd className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] text-[#263B40] bg-[#EAE3DE] px-1.5 py-0.5 rounded border border-[#175A67]/20 shadow-2xs pointer-events-none hidden sm:inline-block font-mono">
              /
            </kbd>
          </form>
        </div>

        {/* Right profile & notifications */}
        <div className="flex items-center gap-2.5">
          <button
            className="p-2 rounded-xl bg-white/45 backdrop-blur-md border border-white/60 hover:bg-white/75 text-[#263B40] hover:text-[#101410] transition-all relative cursor-pointer"
            aria-label="Notifications"
          >
            <Bell className="h-4 w-4" />
            <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-[#175A67] ring-2 ring-white"></span>
          </button>

          <button
            onClick={() => navigate('/settings')}
            className="flex items-center gap-2.5 px-3 py-1.5 rounded-xl bg-white/45 backdrop-blur-md border border-white/60 hover:bg-white/75 transition-all cursor-pointer"
            aria-label="Profile menu"
            title="Open workspace settings"
          >
            <div className="h-7 w-7 rounded-full bg-[#E2ECED] flex items-center justify-center text-xs font-bold text-[#175A67] border border-[#175A67]/25">
              {user.initials}
            </div>
            <div className="text-left hidden sm:block">
              <p className="text-xs font-semibold text-[#101410] leading-tight">{user.name}</p>
              <p className="text-[10px] text-[#263B40] leading-tight">{user.formattedRole}</p>
            </div>
          </button>
        </div>
      </div>
    </header>
  );
}

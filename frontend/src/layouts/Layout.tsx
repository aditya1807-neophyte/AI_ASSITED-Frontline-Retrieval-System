import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';
import { LoadingScreen } from '@/components/ui';

const BG_VIDEO_URL =
  'https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260901_122529_931c22c8-8d2d-47c0-ad51-b97f56a91e42.mp4';
const BG_POSTER_URL = '/landscape-poster.png';

export function Layout({ children }: { children: React.ReactNode }) {
  const [sidebarExpanded, setSidebarExpanded] = React.useState(true);

  const toggleSidebar = () => {
    setSidebarExpanded((prev) => !prev);
  };

  return (
    <div className="flex h-screen overflow-hidden relative bg-transparent text-[#101410] isolate">
      {/* Background Media Layer - 1080p Hand-Drawn Teal Ink Landscape Loop */}
      <div className="bg-media-layer" aria-hidden="true">
        <video
          className="bg-video-art"
          autoPlay
          muted
          loop
          playsInline
          preload="auto"
          poster={BG_POSTER_URL}
        >
          <source src={BG_VIDEO_URL} type="video/mp4" />
        </video>
        <div className="bg-media-seam" />
      </div>

      <Sidebar
        isExpanded={sidebarExpanded}
        onToggle={toggleSidebar}
      />
      <div className="flex-1 flex flex-col overflow-hidden relative z-10">
        <Header
          onMenuClick={toggleSidebar}
          isSidebarExpanded={sidebarExpanded}
          onToggleSidebar={toggleSidebar}
        />
        <main className="flex-1 overflow-auto p-4 sm:p-6 lg:p-8">
          <div className="max-w-7xl mx-auto space-y-6">
            {children}
            <Outlet />
          </div>
        </main>
      </div>

      {/* Cinematic Glassmorphic Startup Loading Screen */}
      <LoadingScreen />
    </div>
  );
}

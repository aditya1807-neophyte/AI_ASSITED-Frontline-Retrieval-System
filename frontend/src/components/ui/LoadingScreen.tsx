import { useState, useEffect } from 'react';

interface LoadingScreenProps {
  onComplete?: () => void;
}

export function LoadingScreen({ onComplete }: LoadingScreenProps) {
  const [isVisible, setIsVisible] = useState(true);
  const [isExiting, setIsExiting] = useState(false);
  const [isMounted, setIsMounted] = useState(false);
  const [progress, setProgress] = useState(18);
  const [statusMessage, setStatusMessage] = useState('Initializing workspace...');

  useEffect(() => {
    // Trigger entrance animation on next frame
    const enterTimer = requestAnimationFrame(() => {
      setIsMounted(true);
    });

    // Check for reduced-motion preference
    const prefersReducedMotion =
      typeof window !== 'undefined' &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (prefersReducedMotion) {
      setProgress(100);
      setIsExiting(true);
      const dismissTimer = setTimeout(() => {
        setIsVisible(false);
        onComplete?.();
      }, 150);
      return () => {
        cancelAnimationFrame(enterTimer);
        clearTimeout(dismissTimer);
      };
    }

    let isCancelled = false;
    const startTime = Date.now();
    const MIN_DISPLAY_MS = 850; // brief graceful presentation
    const MAX_TIMEOUT_MS = 2400; // safety ceiling to prevent hanging

    // Step 1: Wait for web fonts & DOM
    const checkReadiness = async () => {
      try {
        if (typeof document !== 'undefined' && document.fonts) {
          await document.fonts.ready;
        }
      } catch {
        // Fallback gracefully if document.fonts is unsupported
      }

      if (isCancelled) return;
      setProgress(55);
      setStatusMessage('Loading verified SOP index & ML classifier...');

      // Step 2: Ensure minimum display threshold for smooth perception
      const elapsed = Date.now() - startTime;
      const remainingTime = Math.max(0, MIN_DISPLAY_MS - elapsed);

      setTimeout(() => {
        if (isCancelled) return;
        setProgress(100);
        setStatusMessage('Workspace ready.');

        // Step 3: Trigger exit transition
        setTimeout(() => {
          if (isCancelled) return;
          setIsExiting(true);

          // Step 4: Unmount after exit animation finishes
          setTimeout(() => {
            if (isCancelled) return;
            setIsVisible(false);
            onComplete?.();
          }, 700); // matches transition-opacity duration-700
        }, 180);
      }, remainingTime);
    };

    checkReadiness();

    // Absolute fallback safety ceiling
    const fallbackTimer = setTimeout(() => {
      if (!isCancelled && isVisible) {
        setProgress(100);
        setIsExiting(true);
        setTimeout(() => {
          setIsVisible(false);
          onComplete?.();
        }, 600);
      }
    }, MAX_TIMEOUT_MS);

    return () => {
      isCancelled = true;
      cancelAnimationFrame(enterTimer);
      clearTimeout(fallbackTimer);
    };
  }, [onComplete]);

  if (!isVisible) return null;

  return (
    <div
      className={`fixed inset-0 z-50 flex items-center justify-center p-4 select-none transition-all duration-700 ease-out ${
        isExiting
          ? 'opacity-0 backdrop-blur-none pointer-events-none'
          : 'opacity-100 backdrop-blur-md bg-[#EAE3DE]/45'
      }`}
      aria-live="polite"
      aria-busy={!isExiting}
      role="status"
    >
      {/* Centered Glassmorphic Loading Card */}
      <div
        className={`w-full max-w-[440px] p-8 sm:p-10 rounded-[28px] bg-white/70 backdrop-blur-2xl border border-white/85 shadow-[inset_0_1px_1px_rgba(255,255,255,0.95),_0_24px_64px_-12px_rgba(23,90,103,0.14),_0_4px_16px_rgba(16,20,16,0.03)] flex flex-col items-center text-center transform transition-all duration-700 ease-out ${
          isMounted && !isExiting
            ? 'opacity-100 translate-y-0 scale-100'
            : isExiting
            ? 'opacity-0 -translate-y-2 scale-[0.98]'
            : 'opacity-0 translate-y-4 scale-[0.98]'
        }`}
      >
        {/* Brand Icon Mark */}
        <div className="relative mb-5">
          <div className="h-14 w-14 rounded-2xl bg-[#175A67] text-[#FAF8F5] flex items-center justify-center shadow-lg shadow-[#175A67]/25 border border-white/60">
            <svg
              className="w-7 h-7 text-[#FAF8F5]"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
            </svg>
          </div>
          {/* Subtle petrol glow wave */}
          <div
            className="absolute -inset-1 rounded-2xl bg-[#175A67]/15 blur-sm animate-pulse pointer-events-none"
            aria-hidden="true"
          />
        </div>

        {/* Brand Wordmark */}
        <div className="flex flex-col items-center">
          <h1 className="text-2xl sm:text-3xl font-heading font-bold text-[#101410] tracking-tight leading-none">
            FieldGuide{' '}
            <span className="font-calligraphy text-3xl sm:text-4xl text-[#175A67] font-normal italic pl-0.5 inline-block">
              AI
            </span>
          </h1>
          <span className="text-[10px] sm:text-[11px] uppercase font-semibold tracking-[0.24em] text-[#4A5B5E] mt-1.5">
            Frontline Workspace
          </span>
        </div>

        {/* Elegant hairline accent */}
        <div
          className="w-16 h-px bg-gradient-to-r from-transparent via-[#175A67]/35 to-transparent my-5"
          aria-hidden="true"
        />

        {/* Narrative Statement */}
        <p className="font-heading italic text-base sm:text-[1.125rem] text-[#101410] font-medium leading-relaxed max-w-[340px]">
          Preparing your frontline knowledge workspace.
        </p>

        {/* Minimal Refined Progress Bar */}
        <div className="w-full mt-6">
          <div
            className="w-full h-1.5 rounded-full bg-[#175A67]/12 overflow-hidden relative shadow-inner"
            role="progressbar"
            aria-valuenow={Math.round(progress)}
            aria-valuemin={0}
            aria-valuemax={100}
          >
            <div
              className="h-full rounded-full bg-gradient-to-r from-[#175A67] via-[#2A707C] to-[#175A67] transition-all duration-300 ease-out shadow-[0_0_8px_rgba(23,90,103,0.3)]"
              style={{ width: `${progress}%` }}
            />
          </div>

          {/* Micro Status & Assurance Footer */}
          <div className="flex items-center justify-between text-[11px] text-[#4A5B5E]/80 mt-2.5 font-sans">
            <span className="truncate max-w-[240px] text-left font-serif italic text-[#263B40]">
              {statusMessage}
            </span>
            <span className="font-mono font-semibold text-[#175A67] pl-2 shrink-0">
              {Math.round(progress)}%
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

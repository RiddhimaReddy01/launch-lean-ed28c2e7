import { useState, useEffect, useRef, lazy, Suspense } from 'react';
import { useIdea } from '@/context/IdeaContext';
import SectionSkeleton from './SectionSkeleton';

const OpportunitySizing = lazy(() => import('./OpportunitySizing'));
const CustomerSegments = lazy(() => import('./CustomerSegments'));
const Competitors = lazy(() => import('./Competitors'));
const RootCauses = lazy(() => import('./RootCauses'));
const StartupCostsPreview = lazy(() => import('./StartupCostsPreview'));

const TABS = [
  { key: 'sizing', label: 'Opportunity sizing' },
  { key: 'segments', label: 'Customer segments' },
  { key: 'competitors', label: 'Competitors' },
  { key: 'rootcause', label: 'Why it still exists' },
  { key: 'costs', label: 'Startup costs' },
] as const;

type TabKey = typeof TABS[number]['key'];

export default function AnalyzeModule() {
  const { idea, selectedInsight } = useIdea();
  const [activeTab, setActiveTab] = useState<TabKey>('sizing');
  const [loaded, setLoaded] = useState<Set<TabKey>>(new Set(['sizing']));
  const [ready, setReady] = useState<Set<TabKey>>(new Set());
  const containerRef = useRef<HTMLDivElement>(null);

  // Simulate lazy load delay on first visit
  useEffect(() => {
    if (!loaded.has(activeTab)) {
      setLoaded((prev) => new Set(prev).add(activeTab));
    }
    if (!ready.has(activeTab)) {
      const timer = setTimeout(() => {
        setReady((prev) => new Set(prev).add(activeTab));
      }, 800);
      return () => clearTimeout(timer);
    }
  }, [activeTab, loaded, ready]);

  useEffect(() => {
    const el = containerRef.current;
    if (el) requestAnimationFrame(() => el.classList.add('visible'));
  }, []);

  const showSkeleton = !ready.has(activeTab);

  // Mock data for the sticky strip
  const insightTitle = selectedInsight || 'Existing juice bars are overpriced for basic smoothies';
  const insightScore = 93;

  return (
    <div ref={containerRef} className="scroll-reveal" style={{ maxWidth: 800, margin: '0 auto', padding: '0 24px' }}>
      {/* Sticky context strip */}
      <div
        className="sticky z-30 rounded-[12px] mb-12 p-5"
        style={{
          top: 80,
          backgroundColor: 'rgba(255,255,255,0.85)',
          backdropFilter: 'blur(16px)',
          boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
        }}
      >
        <div className="flex flex-wrap items-start gap-x-10 gap-y-3">
          <div className="min-w-0 flex-1">
            <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.04em', marginBottom: 4 }}>IDEA</p>
            <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 400, color: 'var(--text-primary)', lineHeight: 1.4 }}>
              {idea}
            </p>
          </div>
          <div className="min-w-0 flex-1">
            <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.04em', marginBottom: 4 }}>SELECTED OPPORTUNITY</p>
            <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 400, color: 'var(--text-primary)', lineHeight: 1.4 }}>
              {insightTitle}
            </p>
          </div>
          <div>
            <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.04em', marginBottom: 4 }}>SIGNAL</p>
            <div
              className="flex items-center justify-center rounded-[8px]"
              style={{
                width: 40,
                height: 40,
                backgroundColor: 'rgba(108,92,231,0.06)',
                fontFamily: "'Inter', sans-serif",
                fontSize: 15,
                fontWeight: 400,
                color: 'var(--accent-purple)',
              }}
            >
              {insightScore}
            </div>
          </div>
        </div>
      </div>

      {/* Intro */}
      <div className="mb-16">
        <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 10 }}>
          MARKET INTELLIGENCE
        </p>
        <p className="font-heading" style={{ fontSize: 26, marginBottom: 12 }}>
          Is this a real opportunity?
        </p>
        <p
          style={{
            fontFamily: "'Inter', sans-serif",
            fontSize: 15,
            fontWeight: 300,
            lineHeight: 1.75,
            color: 'var(--text-secondary)',
            maxWidth: 540,
          }}
        >
          We analyzed market size, customer demand, competitors, structural barriers, and startup feasibility for this specific gap.
        </p>
      </div>

      {/* Tab switcher */}
      <div
        className="flex flex-wrap gap-1 mb-12"
        style={{ borderBottom: '1px solid var(--divider)' }}
      >
        {TABS.map((tab) => {
          const isActive = activeTab === tab.key;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className="transition-all duration-200 active:scale-[0.97]"
              style={{
                fontFamily: "'Inter', sans-serif",
                fontSize: 13,
                fontWeight: isActive ? 400 : 300,
                color: isActive ? 'var(--text-primary)' : 'var(--text-muted)',
                background: 'none',
                border: 'none',
                borderBottom: isActive ? '2px solid var(--accent-purple)' : '2px solid transparent',
                padding: '10px 14px',
                cursor: 'pointer',
                whiteSpace: 'nowrap',
              }}
            >
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Section content */}
      <div style={{ minHeight: 300 }}>
        {showSkeleton ? (
          <SectionSkeleton />
        ) : (
          <Suspense fallback={<SectionSkeleton />}>
            {activeTab === 'sizing' && <OpportunitySizing />}
            {activeTab === 'segments' && <CustomerSegments />}
            {activeTab === 'competitors' && <Competitors />}
            {activeTab === 'rootcause' && <RootCauses />}
            {activeTab === 'costs' && <StartupCostsPreview />}
          </Suspense>
        )}
      </div>

      {/* Bottom actions */}
      <div
        className="flex flex-wrap items-center gap-3 mt-20 pt-8"
        style={{ borderTop: '1px solid var(--divider)' }}
      >
        <button
          className="rounded-[12px] px-6 py-3 transition-all duration-200 active:scale-[0.97]"
          style={{
            fontFamily: "'Inter', sans-serif",
            fontSize: 14,
            fontWeight: 400,
            backgroundColor: 'var(--accent-purple)',
            color: '#FFFFFF',
            border: 'none',
            cursor: 'pointer',
          }}
        >
          View setup plan →
        </button>
        <button
          className="rounded-[12px] px-5 py-3 transition-all duration-200 active:scale-[0.97]"
          style={{
            fontFamily: "'Inter', sans-serif",
            fontSize: 14,
            fontWeight: 400,
            backgroundColor: 'rgba(108,92,231,0.06)',
            color: 'var(--accent-purple)',
            border: 'none',
            cursor: 'pointer',
          }}
        >
          Save analysis
        </button>
        <button
          className="rounded-[12px] px-5 py-3 transition-all duration-200 active:scale-[0.97]"
          style={{
            fontFamily: "'Inter', sans-serif",
            fontSize: 14,
            fontWeight: 300,
            backgroundColor: 'transparent',
            color: 'var(--text-secondary)',
            border: '1px solid var(--divider-light)',
            cursor: 'pointer',
          }}
        >
          Export report
        </button>
      </div>
    </div>
  );
}

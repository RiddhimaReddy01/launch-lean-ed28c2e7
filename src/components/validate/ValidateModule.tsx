import { useState, useEffect, useRef } from 'react';
import { useIdea } from '@/context/IdeaContext';
import MethodSelector from './MethodSelector';
import GeneratedAssets from './GeneratedAssets';
import CommunityGrid from './CommunityGrid';
import ExperimentDashboard from './ExperimentDashboard';
import ValidationSummary from './ValidationSummary';

const TABS = [
  { key: 'methods', label: 'Methods' },
  { key: 'assets', label: 'Assets' },
  { key: 'channels', label: 'Channels' },
  { key: 'dashboard', label: 'Dashboard' },
  { key: 'summary', label: 'Summary' },
] as const;

type TabKey = typeof TABS[number]['key'];

const TAB_QUESTIONS: Record<TabKey, string> = {
  methods: 'How do you want to test demand?',
  assets: 'What will you put in front of people?',
  channels: 'Where should you share this?',
  dashboard: 'Are people actually interested?',
  summary: 'What did you learn?',
};

export default function ValidateModule() {
  const { idea, selectedInsight } = useIdea();
  const containerRef = useRef<HTMLDivElement>(null);
  const [activeTab, setActiveTab] = useState<TabKey>('methods');
  const [selectedMethods, setSelectedMethods] = useState<Set<string>>(new Set());
  const [hoveredTab, setHoveredTab] = useState<string | null>(null);

  useEffect(() => {
    const el = containerRef.current;
    if (el) requestAnimationFrame(() => el.classList.add('visible'));
  }, []);

  const toggleMethod = (id: string) => {
    setSelectedMethods((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const renderTab = () => {
    switch (activeTab) {
      case 'methods': return <MethodSelector selected={selectedMethods} onToggle={toggleMethod} />;
      case 'assets': return <GeneratedAssets selectedMethods={selectedMethods} />;
      case 'channels': return <CommunityGrid />;
      case 'dashboard': return <ExperimentDashboard />;
      case 'summary': return <ValidationSummary selectedMethods={selectedMethods} />;
    }
  };

  return (
    <div ref={containerRef} className="scroll-reveal">
      {/* Context strip */}
      <div style={{
        position: 'sticky', top: 64, zIndex: 30,
        backdropFilter: 'blur(16px)', backgroundColor: 'rgba(250,250,248,0.85)',
        padding: '16px 0', marginBottom: 48, borderBottom: '1px solid var(--divider-light)',
      }}>
        <div className="flex items-center justify-between flex-wrap" style={{ gap: 24 }}>
          <div>
            <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 11, fontWeight: 300, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Idea
            </span>
            <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 400, color: 'var(--text-primary)', marginTop: 2 }}>
              {idea || 'A juice bar near Plano'}
            </p>
          </div>
          {selectedInsight && (
            <div>
              <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 11, fontWeight: 300, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Testing
              </span>
              <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 400, color: 'var(--text-primary)', marginTop: 2 }}>
                {selectedInsight}
              </p>
            </div>
          )}
          <div style={{
            padding: '6px 14px', borderRadius: 8,
            backgroundColor: 'rgba(108,92,231,0.06)',
          }}>
            <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 12, fontWeight: 400, color: 'var(--accent-purple)' }}>
              {selectedMethods.size} method{selectedMethods.size !== 1 ? 's' : ''} selected
            </span>
          </div>
        </div>
      </div>

      {/* Intro */}
      <div style={{ marginBottom: 48 }}>
        <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 12, fontWeight: 300, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
          Demand validation
        </span>
        <h2 className="font-heading" style={{ fontSize: 26, letterSpacing: '-0.02em', lineHeight: 1.25, marginTop: 12, marginBottom: 12 }}>
          Will people actually pay for this?
        </h2>
        <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 15, fontWeight: 300, color: 'var(--text-secondary)', lineHeight: 1.75, maxWidth: 600 }}>
          Pick how you want to test demand, launch it, and track real responses.
        </p>
      </div>

      {/* Tab switcher */}
      <div style={{ marginBottom: 40 }}>
        <div className="flex items-center flex-wrap" style={{ gap: 8, borderBottom: '1px solid var(--divider-light)', paddingBottom: 0 }}>
          {TABS.map((tab) => {
            const isActive = tab.key === activeTab;
            const isHov = hoveredTab === tab.key;
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                onMouseEnter={() => setHoveredTab(tab.key)}
                onMouseLeave={() => setHoveredTab(null)}
                style={{
                  fontFamily: "'Inter', sans-serif", fontSize: 13,
                  fontWeight: isActive ? 400 : 300,
                  color: isActive ? 'var(--accent-purple)' : isHov ? 'var(--text-primary)' : 'var(--text-muted)',
                  background: 'none', border: 'none', cursor: 'pointer',
                  padding: '10px 16px',
                  borderBottom: isActive ? '2px solid var(--accent-purple)' : '2px solid transparent',
                  transition: 'all 200ms ease-out',
                  marginBottom: -1,
                }}
              >
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Tab question */}
        <p className="font-heading" style={{ fontSize: 26, letterSpacing: '-0.02em', lineHeight: 1.25, marginTop: 32, marginBottom: 32 }}>
          {TAB_QUESTIONS[activeTab]}
        </p>
      </div>

      {/* Content */}
      {renderTab()}

      {/* Bottom actions */}
      <div style={{ marginTop: 64, paddingTop: 32, borderTop: '1px solid var(--divider-light)' }}>
        <div className="flex items-center flex-wrap" style={{ gap: 12 }}>
          <button style={{
            fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 400,
            color: '#FFFFFF', backgroundColor: 'var(--accent-purple)',
            border: 'none', borderRadius: 12, padding: '12px 24px', cursor: 'pointer',
            transition: 'opacity 200ms ease-out',
          }}>
            Save validation results
          </button>
          <button style={{
            fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 400,
            color: 'var(--accent-purple)', backgroundColor: 'rgba(108,92,231,0.06)',
            border: 'none', borderRadius: 12, padding: '12px 24px', cursor: 'pointer',
            transition: 'all 200ms ease-out',
          }}>
            Export report
          </button>
          <button style={{
            fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 400,
            color: 'var(--text-muted)', backgroundColor: 'transparent',
            border: '1px solid var(--divider-light)', borderRadius: 12, padding: '12px 24px', cursor: 'pointer',
            transition: 'all 200ms ease-out',
          }}>
            Start new idea
          </button>
        </div>
      </div>
    </div>
  );
}

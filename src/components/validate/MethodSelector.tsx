import { useState } from 'react';
import { MOCK_METHODS, type ValidationMethod } from '@/data/validate-mock';

const EFFORT_COLORS: Record<string, string> = {
  low: '#2D8B75',
  medium: '#D4880F',
  high: '#E05252',
};

const SPEED_LABELS: Record<string, string> = {
  fast: '⚡ Fast',
  medium: '⏱ Medium',
  slow: '🐢 Slow',
};

interface Props {
  selected: Set<string>;
  onToggle: (id: string) => void;
}

export default function MethodSelector({ selected, onToggle }: Props) {
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 16 }}>
      {MOCK_METHODS.map((m) => {
        const isSelected = selected.has(m.id);
        const isHovered = hoveredId === m.id;

        return (
          <div
            key={m.id}
            onClick={() => onToggle(m.id)}
            onMouseEnter={() => setHoveredId(m.id)}
            onMouseLeave={() => setHoveredId(null)}
            style={{
              padding: 24,
              borderRadius: 14,
              backgroundColor: isSelected ? 'rgba(108,92,231,0.04)' : '#FFFFFF',
              border: isSelected ? '1.5px solid var(--accent-purple)' : '1px solid var(--divider-light)',
              cursor: 'pointer',
              transition: 'all 200ms ease-out',
              transform: isHovered ? 'translateY(-2px)' : 'translateY(0)',
              boxShadow: isHovered
                ? '0 4px 16px rgba(0,0,0,0.06)'
                : '0 1px 3px rgba(0,0,0,0.04)',
            }}
          >
            <div className="flex items-center justify-between" style={{ marginBottom: 12 }}>
              <span
                style={{
                  fontFamily: "'Inter', sans-serif",
                  fontSize: 15,
                  fontWeight: 400,
                  color: 'var(--text-primary)',
                }}
              >
                {m.name}
              </span>
              <div
                style={{
                  width: 20,
                  height: 20,
                  borderRadius: 6,
                  border: isSelected ? '2px solid var(--accent-purple)' : '2px solid var(--divider-light)',
                  backgroundColor: isSelected ? 'var(--accent-purple)' : 'transparent',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  transition: 'all 200ms ease-out',
                }}
              >
                {isSelected && (
                  <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                    <path d="M2.5 6L5 8.5L9.5 3.5" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                )}
              </div>
            </div>

            <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 300, color: 'var(--text-muted)', lineHeight: 1.6, marginBottom: 16 }}>
              {m.description}
            </p>

            <div className="flex items-center" style={{ gap: 12 }}>
              <span
                style={{
                  fontFamily: "'Inter', sans-serif",
                  fontSize: 12,
                  fontWeight: 400,
                  color: EFFORT_COLORS[m.effort],
                  padding: '3px 8px',
                  borderRadius: 6,
                  backgroundColor: `${EFFORT_COLORS[m.effort]}10`,
                }}
              >
                {m.effort} effort
              </span>
              <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 12, fontWeight: 300, color: 'var(--text-muted)' }}>
                {SPEED_LABELS[m.speed]}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}

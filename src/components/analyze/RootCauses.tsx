import { useState } from 'react';
import { MOCK_ROOT_CAUSES } from '@/data/analyze-mock';

export default function RootCauses() {
  const [hoveredCause, setHoveredCause] = useState<number | null>(null);

  return (
    <div
      className="rounded-[14px] p-6 md:p-8"
      style={{
        backgroundColor: 'rgba(212,136,15,0.03)',
        border: '1px solid rgba(212,136,15,0.08)',
      }}
    >
      <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 8, color: 'var(--accent-amber)' }}>
        STRUCTURAL ANALYSIS
      </p>
      <p className="font-heading" style={{ fontSize: 26, marginBottom: 8 }}>
        Why this gap still exists
      </p>
      <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 300, color: 'var(--text-secondary)', lineHeight: 1.7, marginBottom: 40, maxWidth: 520 }}>
        These aren't random market failures. Each has a structural reason — and a specific opening for you.
      </p>

      <div className="flex flex-col gap-10">
        {MOCK_ROOT_CAUSES.map((cause, i) => {
          const isHovered = hoveredCause === i;
          return (
            <div
              key={i}
              className="rounded-[12px] p-4 -m-4 transition-all duration-200"
              style={{
                backgroundColor: isHovered ? 'rgba(212,136,15,0.04)' : 'transparent',
                cursor: 'default',
              }}
              onMouseEnter={() => setHoveredCause(i)}
              onMouseLeave={() => setHoveredCause(null)}
            >
              <div className="flex items-start gap-4">
                <div
                  className="flex-shrink-0 flex items-center justify-center rounded-[8px] transition-all duration-200"
                  style={{
                    width: 32,
                    height: 32,
                    backgroundColor: isHovered ? 'rgba(212,136,15,0.14)' : 'rgba(212,136,15,0.08)',
                    fontFamily: "'Inter', sans-serif",
                    fontSize: 14,
                    fontWeight: 400,
                    color: 'var(--accent-amber)',
                    transform: isHovered ? 'scale(1.1)' : 'scale(1)',
                  }}
                >
                  {i + 1}
                </div>
                <div className="flex-1">
                  <p
                    className="transition-colors duration-200"
                    style={{
                      fontFamily: "'Inter', sans-serif",
                      fontSize: 15,
                      fontWeight: 400,
                      color: isHovered ? 'var(--accent-amber)' : 'var(--text-primary)',
                      marginBottom: 10,
                      lineHeight: 1.4,
                    }}
                  >
                    {cause.title}
                  </p>
                  <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 300, color: 'var(--text-secondary)', lineHeight: 1.75, marginBottom: 16 }}>
                    {cause.explanation}
                  </p>

                  {/* Your move */}
                  <div
                    className="rounded-[10px] p-4 transition-all duration-200"
                    style={{
                      backgroundColor: isHovered ? 'rgba(212,136,15,0.09)' : 'rgba(212,136,15,0.06)',
                      borderLeft: `3px solid var(--accent-amber)`,
                      transform: isHovered ? 'translateX(4px)' : 'translateX(0)',
                    }}
                  >
                    <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', color: 'var(--accent-amber)', marginBottom: 6 }}>
                      YOUR MOVE
                    </p>
                    <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 400, color: 'var(--text-primary)', lineHeight: 1.6 }}>
                      {cause.yourMove}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

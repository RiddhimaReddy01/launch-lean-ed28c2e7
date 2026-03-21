import { useState } from 'react';
import { MOCK_MARKET_SIZE } from '@/data/analyze-mock';

export default function OpportunitySizing() {
  const [methodOpen, setMethodOpen] = useState(false);
  const [hoveredBar, setHoveredBar] = useState<string | null>(null);
  const [hoveredMetric, setHoveredMetric] = useState<string | null>(null);
  const maxRaw = MOCK_MARKET_SIZE[0].rawValue;

  return (
    <div>
      {/* Metric blocks */}
      <div className="flex flex-col gap-8">
        {MOCK_MARKET_SIZE.map((m) => (
          <div
            key={m.acronym}
            className="rounded-[12px] p-5 transition-all duration-200"
            style={{
              backgroundColor: hoveredMetric === m.acronym ? 'var(--surface-card)' : 'transparent',
              boxShadow: hoveredMetric === m.acronym ? '0 2px 8px rgba(0,0,0,0.06)' : 'none',
              cursor: 'default',
            }}
            onMouseEnter={() => setHoveredMetric(m.acronym)}
            onMouseLeave={() => setHoveredMetric(null)}
          >
            <p
              className="font-caption"
              style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 6 }}
            >
              {m.acronym} — {m.label}
            </p>
            <p
              className="font-heading"
              style={{ fontSize: 26, lineHeight: 1.25, letterSpacing: '-0.02em' }}
            >
              {m.value}
            </p>
            <p
              className="font-caption transition-all duration-200"
              style={{
                fontSize: 12,
                marginTop: 4,
                maxWidth: 420,
                maxHeight: hoveredMetric === m.acronym ? 60 : 20,
                overflow: 'hidden',
              }}
            >
              {m.methodology}
            </p>
          </div>
        ))}
      </div>

      {/* Funnel */}
      <div style={{ marginTop: 56 }}>
        <p
          className="font-caption"
          style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 16 }}
        >
          MARKET FUNNEL
        </p>
        <div className="flex flex-col gap-3">
          {MOCK_MARKET_SIZE.map((m) => {
            const pct = Math.max((m.rawValue / maxRaw) * 100, 4);
            const isHovered = hoveredBar === m.acronym;
            return (
              <div
                key={m.acronym}
                className="flex items-center gap-3 group"
                onMouseEnter={() => setHoveredBar(m.acronym)}
                onMouseLeave={() => setHoveredBar(null)}
                style={{ cursor: 'pointer' }}
              >
                <span
                  className="transition-colors duration-200"
                  style={{
                    fontFamily: "'Inter', sans-serif",
                    fontSize: 12,
                    fontWeight: 400,
                    color: isHovered ? 'var(--accent-purple)' : 'var(--text-muted)',
                    width: 36,
                    textAlign: 'right',
                  }}
                >
                  {m.acronym}
                </span>
                <div style={{ flex: 1, height: 28, position: 'relative' }}>
                  <div
                    className="rounded-[6px] transition-all duration-300 ease-out"
                    style={{
                      width: `${pct}%`,
                      height: isHovered ? 34 : 28,
                      marginTop: isHovered ? -3 : 0,
                      backgroundColor: isHovered ? 'rgba(108,92,231,0.14)' : 'rgba(108,92,231,0.08)',
                      display: 'flex',
                      alignItems: 'center',
                      paddingLeft: 10,
                    }}
                  >
                    <span
                      className="transition-all duration-200"
                      style={{
                        fontFamily: "'Inter', sans-serif",
                        fontSize: isHovered ? 13 : 12,
                        fontWeight: 400,
                        color: 'var(--accent-purple)',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {m.value}
                    </span>
                  </div>

                  {/* Tooltip on hover */}
                  <div
                    className="transition-all duration-200 pointer-events-none"
                    style={{
                      position: 'absolute',
                      top: -36,
                      left: `${Math.min(pct, 80)}%`,
                      opacity: isHovered ? 1 : 0,
                      transform: isHovered ? 'translateY(0)' : 'translateY(4px)',
                    }}
                  >
                    <div
                      className="rounded-[8px] px-3 py-1.5"
                      style={{
                        backgroundColor: 'var(--text-primary)',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 11, color: '#fff' }}>
                        {m.label}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Collapsible methodology */}
      <div style={{ marginTop: 48 }}>
        <button
          onClick={() => setMethodOpen(!methodOpen)}
          className="transition-colors duration-200 active:scale-[0.98] group flex items-center gap-2"
          style={{
            fontFamily: "'Inter', sans-serif",
            fontSize: 13,
            fontWeight: 400,
            color: 'var(--accent-purple)',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            padding: 0,
          }}
        >
          <span>{methodOpen ? 'Hide methodology' : 'How we estimated this'}</span>
          <span
            className="transition-transform duration-200"
            style={{ transform: methodOpen ? 'rotate(180deg)' : 'rotate(0deg)', display: 'inline-block' }}
          >
            ↓
          </span>
        </button>
        <div
          style={{
            maxHeight: methodOpen ? 300 : 0,
            overflow: 'hidden',
            transition: 'max-height 300ms ease-out',
          }}
        >
          <div
            className="rounded-[10px] mt-3 p-4"
            style={{ backgroundColor: 'var(--surface-input)' }}
          >
            {MOCK_MARKET_SIZE.map((m) => (
              <p key={m.acronym} className="font-caption" style={{ fontSize: 12, marginBottom: 8 }}>
                <span style={{ fontWeight: 400, color: 'var(--text-primary)' }}>{m.acronym}:</span>{' '}
                {m.methodology}
              </p>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

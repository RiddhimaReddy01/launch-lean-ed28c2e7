import { useState } from 'react';
import { MOCK_MARKET_SIZE } from '@/data/analyze-mock';

export default function OpportunitySizing() {
  const [methodOpen, setMethodOpen] = useState(false);
  const maxRaw = MOCK_MARKET_SIZE[0].rawValue;

  return (
    <div>
      {/* Metric blocks */}
      <div className="flex flex-col gap-8">
        {MOCK_MARKET_SIZE.map((m) => (
          <div key={m.acronym}>
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
              className="font-caption"
              style={{ fontSize: 12, marginTop: 4, maxWidth: 420 }}
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
            return (
              <div key={m.acronym} className="flex items-center gap-3">
                <span
                  style={{
                    fontFamily: "'Inter', sans-serif",
                    fontSize: 12,
                    fontWeight: 400,
                    color: 'var(--text-muted)',
                    width: 36,
                    textAlign: 'right',
                  }}
                >
                  {m.acronym}
                </span>
                <div style={{ flex: 1, height: 28, position: 'relative' }}>
                  <div
                    className="rounded-[6px]"
                    style={{
                      width: `${pct}%`,
                      height: '100%',
                      backgroundColor: 'rgba(108,92,231,0.08)',
                      transition: 'width 600ms ease-out',
                      display: 'flex',
                      alignItems: 'center',
                      paddingLeft: 10,
                    }}
                  >
                    <span
                      style={{
                        fontFamily: "'Inter', sans-serif",
                        fontSize: 12,
                        fontWeight: 400,
                        color: 'var(--accent-purple)',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {m.value}
                    </span>
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
          className="transition-colors duration-200 active:scale-[0.98]"
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
          {methodOpen ? 'Hide' : 'How we estimated this'} {methodOpen ? '↑' : '↓'}
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

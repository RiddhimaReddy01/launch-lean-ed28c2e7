import { useState } from 'react';
import { MOCK_COMPETITORS } from '@/data/analyze-mock';
import type { Competitor } from '@/data/analyze-mock';

function CompetitorRow({ comp }: { comp: Competitor }) {
  const [open, setOpen] = useState(false);

  return (
    <div
      className="rounded-[12px] transition-shadow duration-200"
      style={{
        backgroundColor: 'var(--surface-card)',
        boxShadow: open ? '0 4px 16px rgba(0,0,0,0.06)' : '0 1px 3px rgba(0,0,0,0.04)',
      }}
    >
      <button
        onClick={() => setOpen(!open)}
        className="w-full text-left p-5 flex items-center gap-4 active:scale-[0.995] transition-transform duration-150"
        style={{ cursor: 'pointer', border: 'none', background: 'none' }}
      >
        <div className="flex-1 min-w-0">
          <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 15, fontWeight: 400, color: 'var(--text-primary)' }}>
            {comp.name}
          </p>
          <p className="font-caption mt-1" style={{ fontSize: 12 }}>
            {comp.location} · ★ {comp.rating} · {comp.priceRange}
          </p>
        </div>
        <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 300, color: 'var(--text-secondary)', maxWidth: 260, textAlign: 'right' }}>
          {comp.keyGap}
        </p>
        <span style={{ fontSize: 14, color: 'var(--text-muted)', transition: 'transform 200ms ease-out', transform: open ? 'rotate(180deg)' : 'rotate(0deg)' }}>
          ↓
        </span>
      </button>

      <div style={{ maxHeight: open ? 600 : 0, overflow: 'hidden', transition: 'max-height 300ms ease-out' }}>
        <div className="px-5 pb-5">
          <div style={{ height: 1, backgroundColor: 'var(--divider)', marginBottom: 20 }} />

          <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 300, lineHeight: 1.7, color: 'var(--text-secondary)', marginBottom: 20 }}>
            {comp.description}
          </p>

          {/* Source link */}
          {comp.url && (
            <a
              href={comp.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block mb-5 transition-colors duration-200"
              style={{
                fontFamily: "'Inter', sans-serif",
                fontSize: 13,
                fontWeight: 400,
                color: 'var(--accent-purple)',
                textDecoration: 'none',
              }}
              onMouseEnter={(e) => (e.currentTarget.style.textDecoration = 'underline')}
              onMouseLeave={(e) => (e.currentTarget.style.textDecoration = 'none')}
            >
              Visit website →
            </a>
          )}

          {/* Review excerpts */}
          <div className="mb-5">
            <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.04em', marginBottom: 10 }}>
              REVIEW EXCERPTS
            </p>
            <div className="flex flex-col gap-2">
              {comp.reviewExcerpts.map((r, i) => (
                <p
                  key={i}
                  className="rounded-[8px] p-3"
                  style={{
                    backgroundColor: 'var(--surface-input)',
                    fontFamily: "'Instrument Serif', serif",
                    fontStyle: 'italic',
                    fontSize: 14,
                    lineHeight: 1.55,
                    color: 'var(--text-primary)',
                  }}
                >
                  {r}
                </p>
              ))}
            </div>
          </div>

          {/* Why it matters */}
          <div className="mb-5">
            <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.04em', marginBottom: 8 }}>
              WHY THIS GAP MATTERS
            </p>
            <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 300, color: 'var(--text-secondary)', lineHeight: 1.65 }}>
              {comp.keyGap}
            </p>
          </div>

          {/* Strengths & weaknesses */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.04em', marginBottom: 8 }}>
                WHAT THEY DO WELL
              </p>
              {comp.strengths.map((s) => (
                <p key={s} style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 300, color: 'var(--accent-teal)', marginBottom: 4 }}>
                  + {s}
                </p>
              ))}
            </div>
            <div>
              <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.04em', marginBottom: 8 }}>
                WHAT THEY MISS
              </p>
              {comp.weaknesses.map((w) => (
                <p key={w} style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 300, color: 'var(--accent-amber)', marginBottom: 4 }}>
                  − {w}
                </p>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Competitors() {
  return (
    <div className="flex flex-col gap-3">
      {MOCK_COMPETITORS.map((c) => (
        <CompetitorRow key={c.name} comp={c} />
      ))}
    </div>
  );
}

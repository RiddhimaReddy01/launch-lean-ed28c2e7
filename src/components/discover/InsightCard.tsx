import { useState, useRef, useEffect } from 'react';
import type { Insight, Source } from '@/data/discover-mock';
import { useIdea } from '@/context/IdeaContext';

const TYPE_CONFIG: Record<Insight['type'], { label: string; color: string; bg: string }> = {
  pain: { label: 'PAIN POINT', color: 'var(--accent-purple)', bg: 'rgba(108,92,231,0.06)' },
  want: { label: 'UNMET WANT', color: 'var(--accent-teal)', bg: 'rgba(45,139,117,0.06)' },
  gap: { label: 'MARKET GAP', color: 'var(--accent-blue)', bg: 'rgba(59,130,246,0.06)' },
};

function intensityLabel(val: number): string {
  if (val >= 8) return 'high intensity';
  if (val >= 5) return 'medium intensity';
  return 'low intensity';
}

function monetizationLabel(val: number): string {
  if (val >= 7) return 'strong pay signal';
  if (val >= 4) return 'moderate pay signal';
  return 'weak pay signal';
}

interface InsightCardProps {
  insight: Insight;
  sources: Source[];
  onSeeMentions: (insight: Insight) => void;
}

export default function InsightCard({ insight, sources, onSeeMentions }: InsightCardProps) {
  const [expanded, setExpanded] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);
  const [contentHeight, setContentHeight] = useState(0);
  const { setSelectedInsight, setCurrentStep } = useIdea();
  const config = TYPE_CONFIG[insight.type];

  useEffect(() => {
    if (contentRef.current) {
      setContentHeight(contentRef.current.scrollHeight);
    }
  }, [expanded]);

  return (
    <div
      className="rounded-[12px] transition-shadow duration-200 cursor-pointer"
      style={{
        backgroundColor: 'var(--surface-card)',
        boxShadow: expanded
          ? '0 4px 16px rgba(0,0,0,0.06)'
          : '0 1px 3px rgba(0,0,0,0.04)',
      }}
      onClick={() => setExpanded(!expanded)}
    >
      {/* Collapsed header — always visible */}
      <div className="flex items-start gap-4 p-5">
        {/* Score badge */}
        <div
          className="flex-shrink-0 flex items-center justify-center rounded-[8px]"
          style={{
            width: 40,
            height: 40,
            backgroundColor: config.bg,
            fontFamily: "'Inter', sans-serif",
            fontSize: 15,
            fontWeight: 400,
            color: config.color,
          }}
        >
          {insight.score}
        </div>

        <div className="flex-1 min-w-0">
          {/* Type label */}
          <span
            style={{
              fontFamily: "'Inter', sans-serif",
              fontSize: 11,
              fontWeight: 400,
              letterSpacing: '0.06em',
              color: config.color,
            }}
          >
            {config.label}
          </span>

          {/* Title */}
          <p
            style={{
              fontFamily: "'Inter', sans-serif",
              fontSize: 15,
              fontWeight: 400,
              color: 'var(--text-primary)',
              marginTop: 4,
              lineHeight: 1.45,
            }}
          >
            {insight.title}
          </p>

          {/* Meta */}
          <p
            className="font-caption"
            style={{ marginTop: 6, fontSize: 12 }}
          >
            {insight.mentionCount} mentions · {intensityLabel(insight.intensity)} · {monetizationLabel(insight.monetization)}
          </p>
        </div>
      </div>

      {/* Expanded content */}
      <div
        style={{
          height: expanded ? contentHeight : 0,
          overflow: 'hidden',
          transition: 'height 300ms ease-out',
        }}
      >
        <div ref={contentRef} className="px-5 pb-5">
          {/* Divider */}
          <div style={{ height: 1, backgroundColor: 'var(--divider)', marginBottom: 20 }} />

          {/* Evidence quotes */}
          <div className="flex flex-col gap-4">
            {insight.evidence.map((ev, i) => (
              <div
                key={i}
                className="rounded-[10px] p-4"
                style={{ backgroundColor: 'var(--surface-input)' }}
              >
                <p
                  style={{
                    fontFamily: "'Instrument Serif', serif",
                    fontStyle: 'italic',
                    fontSize: 15,
                    lineHeight: 1.6,
                    color: 'var(--text-primary)',
                  }}
                >
                  "{ev.quote}"
                </p>
                <div className="flex items-center gap-3 mt-3">
                  <a
                    href={ev.url || '#'}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    className="transition-colors duration-200"
                    style={{
                      fontFamily: "'Inter', sans-serif",
                      fontSize: 12,
                      fontWeight: 400,
                      color: 'var(--accent-purple)',
                    }}
                  >
                    {ev.sourceName}
                  </a>
                  {ev.upvotes !== null && (
                    <span className="font-caption" style={{ fontSize: 12 }}>
                      ↑ {ev.upvotes}
                    </span>
                  )}
                  <span className="font-caption" style={{ fontSize: 12 }}>
                    {ev.date}
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* Score breakdown */}
          <div className="mt-5 flex gap-6">
            {[
              { label: 'Frequency', value: insight.frequency },
              { label: 'Intensity', value: insight.intensity },
              { label: 'Monetization', value: insight.monetization },
            ].map((s) => (
              <div key={s.label}>
                <span className="font-caption" style={{ fontSize: 11 }}>{s.label}</span>
                <div className="flex items-center gap-1.5 mt-1">
                  {Array.from({ length: 10 }).map((_, i) => (
                    <div
                      key={i}
                      style={{
                        width: 6,
                        height: 6,
                        borderRadius: '50%',
                        backgroundColor: i < s.value ? config.color : 'var(--divider-light)',
                        opacity: i < s.value ? 0.8 : 0.4,
                      }}
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Audience estimate */}
          <p className="font-caption mt-4" style={{ fontSize: 12 }}>
            Audience: {insight.audienceEstimate}
          </p>

          {/* Actions */}
          <div className="flex items-center gap-3 mt-5 flex-wrap">
            <button
              onClick={(e) => {
                e.stopPropagation();
                setSelectedInsight(insight.title);
                setCurrentStep('analyze');
              }}
              className="rounded-[10px] px-4 py-2 transition-all duration-200 active:scale-[0.97]"
              style={{
                fontSize: 13,
                fontFamily: "'Inter', sans-serif",
                fontWeight: 400,
                backgroundColor: 'var(--accent-purple)',
                color: '#FFFFFF',
              }}
            >
              Deep dive this opportunity
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onSeeMentions(insight);
              }}
              className="rounded-[10px] px-4 py-2 transition-all duration-200 active:scale-[0.97]"
              style={{
                fontSize: 13,
                fontFamily: "'Inter', sans-serif",
                fontWeight: 400,
                backgroundColor: config.bg,
                color: config.color,
              }}
            >
              See all {insight.mentionCount} mentions
            </button>
            <button
              onClick={(e) => e.stopPropagation()}
              className="rounded-[10px] px-4 py-2 transition-all duration-200 active:scale-[0.97]"
              style={{
                fontSize: 13,
                fontFamily: "'Inter', sans-serif",
                fontWeight: 300,
                backgroundColor: 'var(--surface-input)',
                color: 'var(--text-secondary)',
              }}
            >
              Save
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

import type { Insight } from '@/data/discover-mock';

interface MentionsPanelProps {
  insight: Insight;
  onClose: () => void;
}

export default function MentionsPanel({ insight, onClose }: MentionsPanelProps) {
  return (
    <div
      className="fixed inset-0 z-50 flex justify-end"
      onClick={onClose}
    >
      {/* Overlay */}
      <div
        className="absolute inset-0"
        style={{ backgroundColor: 'rgba(0,0,0,0.15)', transition: 'opacity 200ms ease-out' }}
      />

      {/* Panel */}
      <div
        className="relative w-full max-w-md h-full overflow-y-auto"
        style={{
          backgroundColor: 'var(--surface-bg)',
          boxShadow: '-8px 0 32px rgba(0,0,0,0.06)',
          animation: 'slideInRight 250ms ease-out',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-6">
          {/* Close button */}
          <button
            onClick={onClose}
            className="mb-6 transition-colors duration-200 active:scale-[0.96]"
            style={{
              fontFamily: "'Inter', sans-serif",
              fontSize: 13,
              fontWeight: 300,
              color: 'var(--text-muted)',
            }}
          >
            ← Back
          </button>

          {/* Title */}
          <p
            className="font-heading"
            style={{ fontSize: 26, maxWidth: 360 }}
          >
            {insight.title}
          </p>

          <p className="font-caption mt-3">
            {insight.mentionCount} mentions across {insight.sourcePlatforms.join(', ')}
          </p>

          {/* All evidence */}
          <div className="flex flex-col gap-4 mt-8">
            {insight.evidence.map((ev, i) => (
              <div
                key={i}
                className="rounded-[10px] p-4"
                style={{ backgroundColor: 'var(--surface-card)', boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}
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
                    className="transition-colors duration-200"
                    style={{
                      fontFamily: "'Inter', sans-serif",
                      fontSize: 12,
                      fontWeight: 400,
                      color: 'var(--accent-purple)',
                    }}
                  >
                    {ev.sourceName} ↗
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

          {/* Placeholder for more mentions */}
          <div
            className="mt-6 rounded-[10px] p-4 text-center"
            style={{ backgroundColor: 'var(--surface-input)' }}
          >
            <p className="font-caption" style={{ fontSize: 13 }}>
              Showing {insight.evidence.length} of {insight.mentionCount} mentions
            </p>
            <p className="font-caption mt-1" style={{ fontSize: 12 }}>
              Full data available in the complete report
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

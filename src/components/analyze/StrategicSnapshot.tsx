import { MOCK_STRATEGIC_SNAPSHOT } from '@/data/analyze-mock';

function SwotQuadrant({ label, items, accentBg, accentText }: { label: string; items: string[]; accentBg: string; accentText: string }) {
  return (
    <div className="rounded-[12px] p-5" style={{ backgroundColor: accentBg }}>
      <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 12, color: accentText }}>
        {label}
      </p>
      <ul className="flex flex-col gap-2.5">
        {items.map((item, i) => (
          <li
            key={i}
            style={{
              fontFamily: "'Inter', sans-serif",
              fontSize: 13,
              fontWeight: 300,
              color: 'var(--text-secondary)',
              lineHeight: 1.55,
              paddingLeft: 12,
              position: 'relative',
            }}
          >
            <span
              style={{
                position: 'absolute',
                left: 0,
                top: 8,
                width: 4,
                height: 4,
                borderRadius: '50%',
                backgroundColor: accentText,
                opacity: 0.5,
              }}
            />
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function StrategicSnapshot() {
  const { swot, takeaways, decision, decisionReasoning } = MOCK_STRATEGIC_SNAPSHOT;

  const decisionConfig = {
    go: { label: 'GO', color: 'var(--accent-teal)', bg: 'rgba(45,139,117,0.06)', border: 'rgba(45,139,117,0.15)' },
    pivot: { label: 'PIVOT', color: 'var(--accent-amber)', bg: 'rgba(212,136,15,0.06)', border: 'rgba(212,136,15,0.15)' },
    stop: { label: 'NOT WORTH IT', color: '#dc5050', bg: 'rgba(220,80,80,0.06)', border: 'rgba(220,80,80,0.15)' },
  };
  const d = decisionConfig[decision];

  return (
    <div>
      {/* SWOT */}
      <div className="mb-16">
        <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 20 }}>
          SWOT ANALYSIS
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <SwotQuadrant
            label="STRENGTHS"
            items={swot.strengths}
            accentBg="rgba(45,139,117,0.04)"
            accentText="var(--accent-teal)"
          />
          <SwotQuadrant
            label="WEAKNESSES"
            items={swot.weaknesses}
            accentBg="rgba(212,136,15,0.04)"
            accentText="var(--accent-amber)"
          />
          <SwotQuadrant
            label="OPPORTUNITIES"
            items={swot.opportunities}
            accentBg="rgba(59,130,246,0.04)"
            accentText="var(--accent-blue)"
          />
          <SwotQuadrant
            label="THREATS"
            items={swot.threats}
            accentBg="rgba(220,80,80,0.04)"
            accentText="#dc5050"
          />
        </div>
      </div>

      {/* Key takeaways */}
      <div className="mb-16">
        <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 20 }}>
          KEY TAKEAWAYS
        </p>
        <div className="flex flex-col gap-4">
          {takeaways.map((t, i) => (
            <div key={i} className="flex items-start gap-3">
              <div
                className="flex-shrink-0 mt-1 rounded-full"
                style={{ width: 6, height: 6, backgroundColor: 'var(--accent-purple)', opacity: 0.5 }}
              />
              <p
                style={{
                  fontFamily: "'Inter', sans-serif",
                  fontSize: 14,
                  fontWeight: 300,
                  color: 'var(--text-secondary)',
                  lineHeight: 1.7,
                }}
              >
                {t}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Decision indicator */}
      <div
        className="rounded-[14px] p-6 md:p-8"
        style={{
          backgroundColor: d.bg,
          border: `1px solid ${d.border}`,
        }}
      >
        <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 12, color: d.color }}>
          RECOMMENDATION
        </p>
        <p
          className="font-heading"
          style={{ fontSize: 26, color: d.color, marginBottom: 12 }}
        >
          {d.label}
        </p>
        <p
          style={{
            fontFamily: "'Inter', sans-serif",
            fontSize: 14,
            fontWeight: 300,
            color: 'var(--text-secondary)',
            lineHeight: 1.75,
            maxWidth: 540,
          }}
        >
          {decisionReasoning}
        </p>
      </div>
    </div>
  );
}

import { useState } from 'react';
import { MOCK_STRATEGIC_SNAPSHOT } from '@/data/analyze-mock';

function SwotQuadrant({ label, items, accentBg, accentHoverBg, accentText }: { label: string; items: string[]; accentBg: string; accentHoverBg: string; accentText: string }) {
  const [hovered, setHovered] = useState(false);
  const [hoveredItem, setHoveredItem] = useState<number | null>(null);

  return (
    <div
      className="rounded-[12px] p-5 transition-all duration-200"
      style={{
        backgroundColor: hovered ? accentHoverBg : accentBg,
        transform: hovered ? 'translateY(-2px)' : 'translateY(0)',
        boxShadow: hovered ? '0 4px 12px rgba(0,0,0,0.04)' : 'none',
        cursor: 'default',
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => { setHovered(false); setHoveredItem(null); }}
    >
      <p className="font-caption transition-all duration-200" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 12, color: accentText, opacity: hovered ? 1 : 0.8 }}>
        {label}
      </p>
      <ul className="flex flex-col gap-2.5">
        {items.map((item, i) => (
          <li
            key={i}
            className="transition-all duration-150 rounded-[4px] px-1"
            style={{
              fontFamily: "'Inter', sans-serif",
              fontSize: 13,
              fontWeight: hoveredItem === i ? 400 : 300,
              color: hoveredItem === i ? 'var(--text-primary)' : 'var(--text-secondary)',
              lineHeight: 1.55,
              paddingLeft: 12,
              position: 'relative',
              cursor: 'default',
            }}
            onMouseEnter={() => setHoveredItem(i)}
            onMouseLeave={() => setHoveredItem(null)}
          >
            <span
              className="transition-all duration-200"
              style={{
                position: 'absolute',
                left: 0,
                top: 8,
                width: hoveredItem === i ? 6 : 4,
                height: hoveredItem === i ? 6 : 4,
                borderRadius: '50%',
                backgroundColor: accentText,
                opacity: hoveredItem === i ? 0.8 : 0.5,
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
  const [hoveredTakeaway, setHoveredTakeaway] = useState<number | null>(null);
  const [decisionHovered, setDecisionHovered] = useState(false);

  const decisionConfig = {
    go: { label: 'GO', color: 'var(--accent-teal)', bg: 'rgba(45,139,117,0.06)', hoverBg: 'rgba(45,139,117,0.10)', border: 'rgba(45,139,117,0.15)', hoverBorder: 'rgba(45,139,117,0.25)' },
    pivot: { label: 'PIVOT', color: 'var(--accent-amber)', bg: 'rgba(212,136,15,0.06)', hoverBg: 'rgba(212,136,15,0.10)', border: 'rgba(212,136,15,0.15)', hoverBorder: 'rgba(212,136,15,0.25)' },
    stop: { label: 'NOT WORTH IT', color: '#dc5050', bg: 'rgba(220,80,80,0.06)', hoverBg: 'rgba(220,80,80,0.10)', border: 'rgba(220,80,80,0.15)', hoverBorder: 'rgba(220,80,80,0.25)' },
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
          <SwotQuadrant label="STRENGTHS" items={swot.strengths} accentBg="rgba(45,139,117,0.04)" accentHoverBg="rgba(45,139,117,0.07)" accentText="var(--accent-teal)" />
          <SwotQuadrant label="WEAKNESSES" items={swot.weaknesses} accentBg="rgba(212,136,15,0.04)" accentHoverBg="rgba(212,136,15,0.07)" accentText="var(--accent-amber)" />
          <SwotQuadrant label="OPPORTUNITIES" items={swot.opportunities} accentBg="rgba(59,130,246,0.04)" accentHoverBg="rgba(59,130,246,0.07)" accentText="var(--accent-blue)" />
          <SwotQuadrant label="THREATS" items={swot.threats} accentBg="rgba(220,80,80,0.04)" accentHoverBg="rgba(220,80,80,0.07)" accentText="#dc5050" />
        </div>
      </div>

      {/* Key takeaways */}
      <div className="mb-16">
        <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 20 }}>
          KEY TAKEAWAYS
        </p>
        <div className="flex flex-col gap-2">
          {takeaways.map((t, i) => (
            <div
              key={i}
              className="flex items-start gap-3 rounded-[8px] p-3 transition-all duration-200"
              style={{
                backgroundColor: hoveredTakeaway === i ? 'rgba(108,92,231,0.04)' : 'transparent',
                cursor: 'default',
              }}
              onMouseEnter={() => setHoveredTakeaway(i)}
              onMouseLeave={() => setHoveredTakeaway(null)}
            >
              <div
                className="flex-shrink-0 mt-1.5 rounded-full transition-all duration-200"
                style={{
                  width: hoveredTakeaway === i ? 8 : 6,
                  height: hoveredTakeaway === i ? 8 : 6,
                  backgroundColor: 'var(--accent-purple)',
                  opacity: hoveredTakeaway === i ? 0.8 : 0.5,
                }}
              />
              <p
                className="transition-colors duration-200"
                style={{
                  fontFamily: "'Inter', sans-serif",
                  fontSize: 14,
                  fontWeight: hoveredTakeaway === i ? 400 : 300,
                  color: hoveredTakeaway === i ? 'var(--text-primary)' : 'var(--text-secondary)',
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
        className="rounded-[14px] p-6 md:p-8 transition-all duration-200"
        style={{
          backgroundColor: decisionHovered ? d.hoverBg : d.bg,
          border: `1px solid ${decisionHovered ? d.hoverBorder : d.border}`,
          transform: decisionHovered ? 'translateY(-2px)' : 'translateY(0)',
          boxShadow: decisionHovered ? '0 6px 20px rgba(0,0,0,0.06)' : 'none',
          cursor: 'default',
        }}
        onMouseEnter={() => setDecisionHovered(true)}
        onMouseLeave={() => setDecisionHovered(false)}
      >
        <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 12, color: d.color }}>
          RECOMMENDATION
        </p>
        <p
          className="font-heading transition-all duration-200"
          style={{ fontSize: 26, color: d.color, marginBottom: 12, letterSpacing: decisionHovered ? '0.02em' : '-0.02em' }}
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

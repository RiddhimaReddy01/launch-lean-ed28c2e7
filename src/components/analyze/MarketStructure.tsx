import { useState } from 'react';
import { MOCK_MARKET_STRUCTURE } from '@/data/analyze-mock';

function StructureIndicator({ label, value, tooltip }: { label: string; value: string; tooltip?: string }) {
  const [hovered, setHovered] = useState(false);
  const colors: Record<string, { bg: string; hoverBg: string; text: string }> = {
    low: { bg: 'rgba(45,139,117,0.06)', hoverBg: 'rgba(45,139,117,0.12)', text: 'var(--accent-teal)' },
    medium: { bg: 'rgba(212,136,15,0.06)', hoverBg: 'rgba(212,136,15,0.12)', text: 'var(--accent-amber)' },
    high: { bg: 'rgba(220,80,80,0.06)', hoverBg: 'rgba(220,80,80,0.12)', text: '#dc5050' },
  };
  const c = colors[value] || colors.medium;

  return (
    <div
      className="rounded-[12px] p-5 transition-all duration-200"
      style={{
        backgroundColor: 'var(--surface-card)',
        boxShadow: hovered ? '0 4px 12px rgba(0,0,0,0.06)' : '0 1px 3px rgba(0,0,0,0.04)',
        transform: hovered ? 'translateY(-2px)' : 'translateY(0)',
        cursor: 'default',
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.04em', marginBottom: 10 }}>
        {label}
      </p>
      <span
        className="rounded-[6px] px-3 py-1.5 transition-all duration-200"
        style={{
          fontFamily: "'Inter', sans-serif",
          fontSize: 14,
          fontWeight: 400,
          backgroundColor: hovered ? c.hoverBg : c.bg,
          color: c.text,
          display: 'inline-block',
        }}
      >
        {value}
      </span>
      {/* Tooltip */}
      {tooltip && (
        <div
          className="transition-all duration-200 overflow-hidden"
          style={{ maxHeight: hovered ? 40 : 0, opacity: hovered ? 1 : 0, marginTop: hovered ? 10 : 0 }}
        >
          <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 12, fontWeight: 300, color: 'var(--text-muted)' }}>
            {tooltip}
          </p>
        </div>
      )}
    </div>
  );
}

export default function MarketStructure() {
  const [fragHovered, setFragHovered] = useState(false);
  const data = MOCK_MARKET_STRUCTURE;

  return (
    <div>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-12">
        <StructureIndicator label="SATURATION" value={data.saturation} tooltip="Moderate presence of competitors in the area" />
        <StructureIndicator label="DIFFERENTIATION" value={data.differentiation} tooltip="Competitors offer similar products — room to stand out" />
        <div
          className="rounded-[12px] p-5 sm:col-span-1 transition-all duration-200"
          style={{
            backgroundColor: 'var(--surface-card)',
            boxShadow: fragHovered ? '0 4px 12px rgba(0,0,0,0.06)' : '0 1px 3px rgba(0,0,0,0.04)',
            transform: fragHovered ? 'translateY(-2px)' : 'translateY(0)',
            cursor: 'default',
          }}
          onMouseEnter={() => setFragHovered(true)}
          onMouseLeave={() => setFragHovered(false)}
        >
          <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.04em', marginBottom: 10 }}>
            FRAGMENTATION
          </p>
          <p
            className="transition-colors duration-200"
            style={{
              fontFamily: "'Inter', sans-serif",
              fontSize: 13,
              fontWeight: 400,
              color: fragHovered ? 'var(--accent-purple)' : 'var(--text-primary)',
              lineHeight: 1.5,
            }}
          >
            {data.fragmentation}
          </p>
        </div>
      </div>

      {/* Explanation */}
      <div
        className="rounded-[14px] p-6 transition-all duration-200 group"
        style={{
          backgroundColor: 'rgba(59,130,246,0.03)',
          border: '1px solid rgba(59,130,246,0.08)',
          cursor: 'default',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = 'rgba(59,130,246,0.06)';
          e.currentTarget.style.borderColor = 'rgba(59,130,246,0.14)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = 'rgba(59,130,246,0.03)';
          e.currentTarget.style.borderColor = 'rgba(59,130,246,0.08)';
        }}
      >
        <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 10, color: 'var(--accent-blue)' }}>
          MARKET READING
        </p>
        <p
          style={{
            fontFamily: "'Instrument Serif', serif",
            fontSize: 18,
            fontStyle: 'italic',
            color: 'var(--text-primary)',
            lineHeight: 1.6,
          }}
        >
          {data.explanation}
        </p>
      </div>
    </div>
  );
}

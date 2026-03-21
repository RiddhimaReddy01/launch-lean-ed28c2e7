import { useState } from 'react';
import { MOCK_COSTS } from '@/data/analyze-mock';

export default function StartupCostsPreview() {
  const [hoveredCat, setHoveredCat] = useState<string | null>(null);
  const [summaryHovered, setSummaryHovered] = useState(false);

  return (
    <div>
      {/* Summary */}
      <div
        className="rounded-[12px] p-6 transition-all duration-200"
        style={{
          backgroundColor: 'var(--surface-card)',
          boxShadow: summaryHovered ? '0 4px 16px rgba(0,0,0,0.07)' : '0 1px 3px rgba(0,0,0,0.04)',
          transform: summaryHovered ? 'translateY(-2px)' : 'translateY(0)',
          marginBottom: 32,
          cursor: 'default',
        }}
        onMouseEnter={() => setSummaryHovered(true)}
        onMouseLeave={() => setSummaryHovered(false)}
      >
        <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 12 }}>
          ESTIMATED STARTUP RANGE
        </p>
        <div className="flex items-baseline gap-3">
          <span className="font-heading transition-colors duration-200" style={{ fontSize: 26, color: summaryHovered ? 'var(--accent-purple)' : undefined }}>{MOCK_COSTS.minTotal}</span>
          <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 300, color: 'var(--text-muted)' }}>to</span>
          <span className="font-heading transition-colors duration-200" style={{ fontSize: 26, color: summaryHovered ? 'var(--accent-purple)' : undefined }}>{MOCK_COSTS.maxTotal}</span>
        </div>
        <p className="font-caption mt-2" style={{ fontSize: 12 }}>
          Based on Plano, TX market rates — food hall kiosk to standalone 600 sq ft location
        </p>
      </div>

      {/* Breakdown */}
      <div className="flex flex-col gap-1">
        {MOCK_COSTS.categories.map((cat) => {
          const isHovered = hoveredCat === cat.label;
          return (
            <div
              key={cat.label}
              className="flex items-center justify-between py-3 px-3 rounded-[8px] transition-all duration-200"
              style={{
                borderBottom: '1px solid var(--divider)',
                backgroundColor: isHovered ? 'rgba(108,92,231,0.03)' : 'transparent',
                cursor: 'default',
              }}
              onMouseEnter={() => setHoveredCat(cat.label)}
              onMouseLeave={() => setHoveredCat(null)}
            >
              <p
                className="transition-colors duration-200"
                style={{
                  fontFamily: "'Inter', sans-serif",
                  fontSize: 14,
                  fontWeight: isHovered ? 400 : 300,
                  color: isHovered ? 'var(--text-primary)' : 'var(--text-secondary)',
                }}
              >
                {cat.label}
              </p>
              <p
                className="transition-colors duration-200"
                style={{
                  fontFamily: "'Inter', sans-serif",
                  fontSize: 14,
                  fontWeight: 400,
                  color: isHovered ? 'var(--accent-purple)' : 'var(--text-primary)',
                }}
              >
                {cat.min} – {cat.max}
              </p>
            </div>
          );
        })}
      </div>

    </div>
  );
}

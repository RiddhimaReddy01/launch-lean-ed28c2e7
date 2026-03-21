import { MOCK_COSTS } from '@/data/analyze-mock';

export default function StartupCostsPreview() {
  return (
    <div>
      {/* Summary */}
      <div
        className="rounded-[12px] p-6"
        style={{
          backgroundColor: 'var(--surface-card)',
          boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
          marginBottom: 32,
        }}
      >
        <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 12 }}>
          ESTIMATED STARTUP RANGE
        </p>
        <div className="flex items-baseline gap-3">
          <span className="font-heading" style={{ fontSize: 26 }}>{MOCK_COSTS.minTotal}</span>
          <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 300, color: 'var(--text-muted)' }}>to</span>
          <span className="font-heading" style={{ fontSize: 26 }}>{MOCK_COSTS.maxTotal}</span>
        </div>
        <p className="font-caption mt-2" style={{ fontSize: 12 }}>
          Based on Plano, TX market rates — food hall kiosk to standalone 600 sq ft location
        </p>
      </div>

      {/* Breakdown */}
      <div className="flex flex-col gap-4">
        {MOCK_COSTS.categories.map((cat) => (
          <div
            key={cat.label}
            className="flex items-center justify-between py-3"
            style={{ borderBottom: '1px solid var(--divider)' }}
          >
            <p
              style={{
                fontFamily: "'Inter', sans-serif",
                fontSize: 14,
                fontWeight: 300,
                color: 'var(--text-secondary)',
              }}
            >
              {cat.label}
            </p>
            <p
              style={{
                fontFamily: "'Inter', sans-serif",
                fontSize: 14,
                fontWeight: 400,
                color: 'var(--text-primary)',
              }}
            >
              {cat.min} – {cat.max}
            </p>
          </div>
        ))}
      </div>

      {/* CTA */}
      <div className="mt-8">
        <button
          className="rounded-[12px] px-5 py-3 transition-all duration-200 active:scale-[0.97]"
          style={{
            fontFamily: "'Inter', sans-serif",
            fontSize: 14,
            fontWeight: 400,
            backgroundColor: 'rgba(108,92,231,0.06)',
            color: 'var(--accent-purple)',
            border: 'none',
            cursor: 'pointer',
          }}
        >
          View full setup plan →
        </button>
      </div>
    </div>
  );
}

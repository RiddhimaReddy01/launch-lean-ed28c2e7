import { MOCK_DEMAND_BEHAVIOR } from '@/data/analyze-mock';

function BarIndicator({ value, max = 10, label }: { value: number; max?: number; label: string }) {
  return (
    <div className="mb-5">
      <div className="flex items-center justify-between mb-2">
        <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 300, color: 'var(--text-secondary)' }}>
          {label}
        </p>
        <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 400, color: 'var(--text-primary)' }}>
          {value}/{max}
        </span>
      </div>
      <div style={{ height: 6, borderRadius: 3, backgroundColor: 'var(--divider)' }}>
        <div
          className="transition-all duration-500 ease-out cursor-pointer hover:opacity-80"
          style={{
            height: '100%',
            borderRadius: 3,
            width: `${(value / max) * 100}%`,
            backgroundColor: 'var(--accent-purple)',
            opacity: 0.7,
          }}
          title={`${label}: ${value}/${max}`}
        />
      </div>
    </div>
  );
}

function LevelBadge({ level }: { level: 'low' | 'medium' | 'high' }) {
  const colors = {
    low: { bg: 'rgba(45,139,117,0.06)', text: 'var(--accent-teal)' },
    medium: { bg: 'rgba(212,136,15,0.06)', text: 'var(--accent-amber)' },
    high: { bg: 'rgba(220,80,80,0.06)', text: '#dc5050' },
  };
  const c = colors[level];
  return (
    <span
      className="rounded-[6px] px-2.5 py-1 cursor-default"
      style={{
        fontFamily: "'Inter', sans-serif",
        fontSize: 12,
        fontWeight: 400,
        backgroundColor: c.bg,
        color: c.text,
      }}
      title={`Level: ${level}`}
    >
      {level}
    </span>
  );
}

function MetricRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-start justify-between py-3" style={{ borderBottom: '1px solid var(--divider)' }}>
      <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 300, color: 'var(--text-muted)' }}>
        {label}
      </p>
      <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 400, color: 'var(--text-primary)', textAlign: 'right', maxWidth: 280 }}>
        {value}
      </p>
    </div>
  );
}

export default function DemandBehavior() {
  const { demand, usage, pricing, friction } = MOCK_DEMAND_BEHAVIOR;

  return (
    <div>
      {/* Demand signals */}
      <div className="mb-14">
        <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 20 }}>
          DEMAND SIGNALS
        </p>
        <BarIndicator label="Pain intensity" value={demand.painIntensity} />
        <BarIndicator label="Frequency of mentions" value={demand.frequencyOfMentions} />
        <BarIndicator label="Willingness to pay" value={demand.willingnessToPay} />
      </div>

      {/* Usage pattern */}
      <div className="mb-14">
        <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 16 }}>
          USAGE PATTERN
        </p>
        <MetricRow label="Frequency of use" value={usage.frequencyOfUse} />
        <MetricRow label="Retention potential" value={usage.retentionPotential} />
        <MetricRow label="Revenue type" value={usage.revenueType} />
      </div>

      {/* Pricing dynamics */}
      <div className="mb-14">
        <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 16 }}>
          PRICING DYNAMICS
        </p>
        <MetricRow label="Typical range" value={pricing.typicalRange} />
        <MetricRow label="Premium ceiling" value={pricing.premiumCeiling} />
        <MetricRow label="Price sensitivity" value={pricing.priceSensitivity} />
      </div>

      {/* Adoption friction */}
      <div>
        <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 16 }}>
          ADOPTION FRICTION
        </p>
        <div className="flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 300, color: 'var(--text-muted)' }}>
              Trust barrier
            </p>
            <LevelBadge level={friction.trustBarrier} />
          </div>
          <div className="flex items-center justify-between">
            <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 300, color: 'var(--text-muted)' }}>
              Switching friction
            </p>
            <LevelBadge level={friction.switchingFriction} />
          </div>
          <div className="flex items-center justify-between">
            <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 300, color: 'var(--text-muted)' }}>
              Risk perception
            </p>
            <LevelBadge level={friction.riskPerception} />
          </div>
        </div>
      </div>
    </div>
  );
}

import { useState } from 'react';
import { MOCK_DEMAND_BEHAVIOR } from '@/data/analyze-mock';

function BarIndicator({ value, max = 10, label, description }: { value: number; max?: number; label: string; description?: string }) {
  const [hovered, setHovered] = useState(false);

  return (
    <div
      className="mb-5 rounded-[10px] p-3 transition-all duration-200"
      style={{
        backgroundColor: hovered ? 'rgba(108,92,231,0.03)' : 'transparent',
        cursor: 'default',
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <div className="flex items-center justify-between mb-2">
        <p className="transition-colors duration-200" style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: hovered ? 400 : 300, color: hovered ? 'var(--text-primary)' : 'var(--text-secondary)' }}>
          {label}
        </p>
        <span className="transition-all duration-200" style={{ fontFamily: "'Inter', sans-serif", fontSize: hovered ? 14 : 13, fontWeight: 400, color: hovered ? 'var(--accent-purple)' : 'var(--text-primary)' }}>
          {value}/{max}
        </span>
      </div>
      <div style={{ height: hovered ? 8 : 6, borderRadius: 4, backgroundColor: 'var(--divider)', transition: 'height 200ms ease-out' }}>
        <div
          className="transition-all duration-300 ease-out"
          style={{
            height: '100%',
            borderRadius: 4,
            width: `${(value / max) * 100}%`,
            backgroundColor: 'var(--accent-purple)',
            opacity: hovered ? 0.85 : 0.6,
          }}
        />
      </div>
      {/* Tooltip description on hover */}
      {description && (
        <div
          className="transition-all duration-200 overflow-hidden"
          style={{ maxHeight: hovered ? 40 : 0, opacity: hovered ? 1 : 0 }}
        >
          <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 12, fontWeight: 300, color: 'var(--text-muted)', marginTop: 6 }}>
            {description}
          </p>
        </div>
      )}
    </div>
  );
}

function LevelBadge({ level, tooltip }: { level: 'low' | 'medium' | 'high'; tooltip?: string }) {
  const [hovered, setHovered] = useState(false);
  const colors = {
    low: { bg: 'rgba(45,139,117,0.06)', hoverBg: 'rgba(45,139,117,0.12)', text: 'var(--accent-teal)' },
    medium: { bg: 'rgba(212,136,15,0.06)', hoverBg: 'rgba(212,136,15,0.12)', text: 'var(--accent-amber)' },
    high: { bg: 'rgba(220,80,80,0.06)', hoverBg: 'rgba(220,80,80,0.12)', text: '#dc5050' },
  };
  const c = colors[level];
  return (
    <div className="relative" onMouseEnter={() => setHovered(true)} onMouseLeave={() => setHovered(false)}>
      <span
        className="rounded-[6px] px-2.5 py-1 cursor-default transition-all duration-200"
        style={{
          fontFamily: "'Inter', sans-serif",
          fontSize: 12,
          fontWeight: 400,
          backgroundColor: hovered ? c.hoverBg : c.bg,
          color: c.text,
          display: 'inline-block',
          transform: hovered ? 'scale(1.05)' : 'scale(1)',
        }}
      >
        {level}
      </span>
      {tooltip && (
        <div
          className="absolute right-0 top-full mt-2 rounded-[8px] px-3 py-2 pointer-events-none transition-all duration-200 z-10"
          style={{
            backgroundColor: 'var(--text-primary)',
            opacity: hovered ? 1 : 0,
            transform: hovered ? 'translateY(0)' : 'translateY(-4px)',
            whiteSpace: 'nowrap',
          }}
        >
          <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 11, color: '#fff' }}>{tooltip}</span>
        </div>
      )}
    </div>
  );
}

function MetricRow({ label, value }: { label: string; value: string }) {
  const [hovered, setHovered] = useState(false);
  return (
    <div
      className="flex items-start justify-between py-3 px-2 rounded-[8px] transition-all duration-200"
      style={{
        borderBottom: '1px solid var(--divider)',
        backgroundColor: hovered ? 'rgba(108,92,231,0.02)' : 'transparent',
        cursor: 'default',
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <p className="transition-colors duration-200" style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 300, color: hovered ? 'var(--text-secondary)' : 'var(--text-muted)' }}>
        {label}
      </p>
      <p className="transition-colors duration-200" style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 400, color: hovered ? 'var(--accent-purple)' : 'var(--text-primary)', textAlign: 'right', maxWidth: 280 }}>
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
        <BarIndicator label="Pain intensity" value={demand.painIntensity} description="How strongly customers feel about this problem" />
        <BarIndicator label="Frequency of mentions" value={demand.frequencyOfMentions} description="How often this topic appears in community conversations" />
        <BarIndicator label="Willingness to pay" value={demand.willingnessToPay} description="Evidence of customers ready to spend on a solution" />
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
            <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 300, color: 'var(--text-muted)' }}>Trust barrier</p>
            <LevelBadge level={friction.trustBarrier} tooltip="New food brands face moderate skepticism" />
          </div>
          <div className="flex items-center justify-between">
            <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 300, color: 'var(--text-muted)' }}>Switching friction</p>
            <LevelBadge level={friction.switchingFriction} tooltip="No contracts or commitments to break" />
          </div>
          <div className="flex items-center justify-between">
            <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 300, color: 'var(--text-muted)' }}>Risk perception</p>
            <LevelBadge level={friction.riskPerception} tooltip="Low-cost, low-risk purchase decision" />
          </div>
        </div>
      </div>
    </div>
  );
}

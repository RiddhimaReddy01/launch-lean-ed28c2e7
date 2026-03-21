import { useState, useMemo } from 'react';
import { MOCK_TIERS, MOCK_TIER_COSTS } from '@/data/setup-mock';
import type { LaunchTier } from '@/data/setup-mock';

type Estimate = 'low' | 'mid' | 'high';

function TierCard({ tier, selected, onSelect }: { tier: LaunchTier; selected: boolean; onSelect: () => void }) {
  const [hovered, setHovered] = useState(false);
  const active = selected || hovered;

  return (
    <button
      onClick={onSelect}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      className="text-left rounded-[14px] p-5 flex-1 min-w-[180px] transition-all duration-200 active:scale-[0.97]"
      style={{
        backgroundColor: selected ? 'rgba(108,92,231,0.06)' : 'var(--surface-card)',
        border: selected ? '1.5px solid var(--accent-purple)' : '1.5px solid transparent',
        boxShadow: active ? '0 4px 16px rgba(0,0,0,0.06)' : '0 1px 3px rgba(0,0,0,0.04)',
        transform: active && !selected ? 'translateY(-2px)' : 'translateY(0)',
        opacity: 1,
        cursor: 'pointer',
      }}
    >
      <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.04em', marginBottom: 8, color: selected ? 'var(--accent-purple)' : undefined }}>
        {tier.id === 'recommended' ? '★ RECOMMENDED' : tier.title.toUpperCase()}
      </p>
      <p className="font-heading" style={{ fontSize: 26, marginBottom: 4 }}>
        {tier.costRange}
      </p>
      <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 400, color: 'var(--text-primary)', marginBottom: 8 }}>
        {tier.model}
      </p>
      <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 300, color: 'var(--text-muted)', lineHeight: 1.55 }}>
        {tier.whenToChoose}
      </p>
    </button>
  );
}

function EstimateToggle({ value, onChange }: { value: Estimate; onChange: (v: Estimate) => void }) {
  const opts: { key: Estimate; label: string }[] = [
    { key: 'low', label: 'Low' },
    { key: 'mid', label: 'Mid' },
    { key: 'high', label: 'High' },
  ];
  return (
    <div className="flex gap-0.5 rounded-[8px] p-0.5" style={{ backgroundColor: 'var(--surface-input)' }}>
      {opts.map((o) => (
        <button
          key={o.key}
          onClick={(e) => { e.stopPropagation(); onChange(o.key); }}
          className="rounded-[6px] px-3 py-1 transition-all duration-150 active:scale-[0.95]"
          style={{
            fontFamily: "'Inter', sans-serif",
            fontSize: 11,
            fontWeight: value === o.key ? 400 : 300,
            color: value === o.key ? 'var(--accent-purple)' : 'var(--text-muted)',
            backgroundColor: value === o.key ? 'var(--surface-card)' : 'transparent',
            boxShadow: value === o.key ? '0 1px 3px rgba(0,0,0,0.06)' : 'none',
            border: 'none',
            cursor: 'pointer',
          }}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}

function formatCurrency(n: number): string {
  if (n >= 1000) return `$${(n / 1000).toFixed(n % 1000 === 0 ? 0 : 1)}K`;
  return `$${n.toLocaleString()}`;
}

export default function CostBuilder({
  selectedTier,
  onSelectTier,
  estimates,
  onEstimateChange,
}: {
  selectedTier: string;
  onSelectTier: (id: string) => void;
  estimates: Record<string, Estimate>;
  onEstimateChange: (itemLabel: string, est: Estimate) => void;
}) {
  const [expandedCats, setExpandedCats] = useState<Set<string>>(new Set());
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());
  const [hoveredItem, setHoveredItem] = useState<string | null>(null);

  const categories = MOCK_TIER_COSTS[selectedTier] || [];

  const totalRange = useMemo(() => {
    let min = 0;
    let max = 0;
    categories.forEach((cat) =>
      cat.items.forEach((item) => {
        const est = estimates[item.label] || 'mid';
        const val = item[est];
        min += item.low;
        max += item.high;
        // We just use min/max for range but could use est for "current"
      })
    );
    return { min, max };
  }, [categories, estimates]);

  const currentTotal = useMemo(() => {
    let total = 0;
    categories.forEach((cat) =>
      cat.items.forEach((item) => {
        const est = estimates[item.label] || 'mid';
        total += item[est];
      })
    );
    return total;
  }, [categories, estimates]);

  const toggleCat = (label: string) => {
    setExpandedCats((prev) => {
      const next = new Set(prev);
      next.has(label) ? next.delete(label) : next.add(label);
      return next;
    });
  };

  const toggleItem = (label: string) => {
    setExpandedItems((prev) => {
      const next = new Set(prev);
      next.has(label) ? next.delete(label) : next.add(label);
      return next;
    });
  };

  return (
    <div>
      {/* Tier selection */}
      <div className="mb-12">
        <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 16 }}>
          SELECT YOUR LAUNCH MODEL
        </p>
        <div className="flex flex-col sm:flex-row gap-3">
          {MOCK_TIERS.map((tier) => (
            <TierCard
              key={tier.id}
              tier={tier}
              selected={selectedTier === tier.id}
              onSelect={() => onSelectTier(tier.id)}
            />
          ))}
        </div>
      </div>

      {/* Cost breakdown */}
      <div className="mb-8">
        <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 16 }}>
          COST BREAKDOWN
        </p>
        <div className="flex flex-col gap-2">
          {categories.map((cat) => {
            const isOpen = expandedCats.has(cat.label);
            const catTotal = cat.items.reduce((sum, item) => sum + item[estimates[item.label] || 'mid'], 0);
            return (
              <div key={cat.label} className="rounded-[12px] transition-shadow duration-200" style={{ backgroundColor: 'var(--surface-card)', boxShadow: isOpen ? '0 2px 8px rgba(0,0,0,0.05)' : '0 1px 3px rgba(0,0,0,0.04)' }}>
                <button
                  onClick={() => toggleCat(cat.label)}
                  className="w-full text-left p-4 flex items-center justify-between active:scale-[0.995] transition-transform duration-150"
                  style={{ border: 'none', background: 'none', cursor: 'pointer' }}
                >
                  <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 400, color: 'var(--text-primary)' }}>
                    {cat.label}
                  </p>
                  <div className="flex items-center gap-3">
                    <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 400, color: 'var(--accent-purple)' }}>
                      {formatCurrency(catTotal)}
                    </span>
                    <span className="transition-transform duration-200" style={{ fontSize: 14, color: 'var(--text-muted)', transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)', display: 'inline-block' }}>↓</span>
                  </div>
                </button>

                <div style={{ maxHeight: isOpen ? 1000 : 0, overflow: 'hidden', transition: 'max-height 300ms ease-out' }}>
                  <div className="px-4 pb-4">
                    <div style={{ height: 1, backgroundColor: 'var(--divider)', marginBottom: 12 }} />
                    {cat.items.map((item) => {
                      const itemOpen = expandedItems.has(item.label);
                      const isItemHovered = hoveredItem === item.label;
                      const est = estimates[item.label] || 'mid';
                      return (
                        <div
                          key={item.label}
                          className="rounded-[8px] mb-1 transition-all duration-150"
                          style={{ backgroundColor: isItemHovered ? 'rgba(108,92,231,0.03)' : 'transparent' }}
                          onMouseEnter={() => setHoveredItem(item.label)}
                          onMouseLeave={() => setHoveredItem(null)}
                        >
                          <div
                            className="flex items-center justify-between py-2.5 px-3 cursor-pointer"
                            onClick={() => toggleItem(item.label)}
                          >
                            <p className="transition-colors duration-150" style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: isItemHovered ? 400 : 300, color: isItemHovered ? 'var(--text-primary)' : 'var(--text-secondary)' }}>
                              {item.label}
                            </p>
                            <div className="flex items-center gap-3">
                              <EstimateToggle value={est} onChange={(v) => onEstimateChange(item.label, v)} />
                              <span className="transition-colors duration-150" style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 400, color: isItemHovered ? 'var(--accent-purple)' : 'var(--text-primary)', minWidth: 50, textAlign: 'right' }}>
                                {formatCurrency(item[est])}
                              </span>
                            </div>
                          </div>
                          <div style={{ maxHeight: itemOpen ? 80 : 0, overflow: 'hidden', transition: 'max-height 200ms ease-out' }}>
                            <p className="px-3 pb-2" style={{ fontFamily: "'Inter', sans-serif", fontSize: 12, fontWeight: 300, color: 'var(--text-muted)', lineHeight: 1.6 }}>
                              {item.explanation}
                            </p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Total cost meter */}
      <div
        className="sticky bottom-4 z-20 rounded-[14px] p-5 transition-all duration-200"
        style={{
          backgroundColor: 'rgba(255,255,255,0.92)',
          backdropFilter: 'blur(16px)',
          boxShadow: '0 -2px 16px rgba(0,0,0,0.06)',
        }}
      >
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div>
            <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.04em', marginBottom: 4 }}>ESTIMATED TOTAL</p>
            <div className="flex items-baseline gap-2">
              <span className="font-heading" style={{ fontSize: 26 }}>{formatCurrency(currentTotal)}</span>
              <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 12, fontWeight: 300, color: 'var(--text-muted)' }}>
                (range: {formatCurrency(totalRange.min)} – {formatCurrency(totalRange.max)})
              </span>
            </div>
          </div>
          <div className="text-right">
            <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.04em', marginBottom: 4 }}>SELECTED MODEL</p>
            <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 400, color: 'var(--accent-purple)' }}>
              {MOCK_TIERS.find((t) => t.id === selectedTier)?.title}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

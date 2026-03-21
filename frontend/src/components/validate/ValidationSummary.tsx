import { useState } from 'react';

interface Props {
  selectedMethods: Set<string>;
}

const METHOD_LABELS: Record<string, string> = {
  landing: 'landing page waitlist',
  survey: 'customer discovery survey',
  social: 'social outreach',
  marketplace: 'marketplace listing',
  direct: 'direct outreach',
};

export default function ValidationSummary({ selectedMethods }: Props) {
  const [hovered, setHovered] = useState<string | null>(null);
  const methods = Array.from(selectedMethods);

  const channelText = methods.length > 0
    ? methods.map((m) => METHOD_LABELS[m] || m).join(', ')
    : 'no channels selected yet';

  return (
    <div>
      {/* Summary */}
      <div style={{ padding: 32, borderRadius: 16, backgroundColor: '#FFFFFF', boxShadow: '0 1px 3px rgba(0,0,0,0.04)', marginBottom: 32 }}>
        <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 12, fontWeight: 300, color: 'var(--text-muted)', marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Validation plan
        </p>
        <p style={{ fontFamily: "'Instrument Serif', serif", fontSize: 26, fontWeight: 400, color: 'var(--text-primary)', lineHeight: 1.25, letterSpacing: '-0.02em', marginBottom: 20 }}>
          Your experiment at a glance
        </p>
        <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 15, fontWeight: 300, color: 'var(--text-secondary)', lineHeight: 1.75 }}>
          You plan to validate demand through <span style={{ fontWeight: 400, color: 'var(--text-primary)' }}>{methods.length} channel{methods.length !== 1 ? 's' : ''}</span> — {channelText}. Track your results in the Dashboard tab to get a data-driven go/no-go recommendation.
        </p>
      </div>

      {/* Iteration */}
      <div style={{ padding: 28, borderRadius: 14, backgroundColor: 'var(--surface-bg)', marginBottom: 32 }}>
        <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 400, color: 'var(--text-primary)', marginBottom: 16 }}>
          What's next?
        </p>
        {[
          { label: 'Run another test', desc: 'Try a different channel or message to compare results' },
          { label: 'Adjust assumptions', desc: 'Change your targets or pricing to refine the experiment' },
          { label: 'Refine targeting', desc: 'Focus on the segment showing strongest response' },
        ].map((item) => (
          <div
            key={item.label}
            onMouseEnter={() => setHovered(item.label)}
            onMouseLeave={() => setHovered(null)}
            style={{
              padding: '14px 18px', borderRadius: 10, marginBottom: 8,
              backgroundColor: hovered === item.label ? '#FFFFFF' : 'transparent',
              boxShadow: hovered === item.label ? '0 2px 8px rgba(0,0,0,0.04)' : 'none',
              cursor: 'pointer', transition: 'all 200ms ease-out',
            }}
          >
            <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 400, color: 'var(--accent-purple)', marginBottom: 4 }}>
              {item.label}
            </p>
            <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 12, fontWeight: 300, color: 'var(--text-muted)' }}>
              {item.desc}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

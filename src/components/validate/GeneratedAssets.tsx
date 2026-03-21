import { useState } from 'react';
import {
  MOCK_LANDING_PAGE,
  MOCK_SURVEY,
  MOCK_SOCIAL_OUTREACH,
  MOCK_MARKETPLACE,
  MOCK_DIRECT_OUTREACH,
} from '@/data/validate-mock';

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      onClick={() => { navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 1500); }}
      style={{
        fontFamily: "'Inter', sans-serif", fontSize: 12, fontWeight: 400,
        color: copied ? '#2D8B75' : 'var(--accent-purple)',
        background: 'none', border: 'none', cursor: 'pointer',
        transition: 'color 200ms ease-out',
      }}
    >
      {copied ? '✓ Copied' : 'Copy'}
    </button>
  );
}

function SectionBlock({ title, children, copyText }: { title: string; children: React.ReactNode; copyText?: string }) {
  const [hovered, setHovered] = useState(false);
  return (
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        padding: 28,
        borderRadius: 14,
        backgroundColor: '#FFFFFF',
        boxShadow: hovered ? '0 4px 16px rgba(0,0,0,0.06)' : '0 1px 3px rgba(0,0,0,0.04)',
        transition: 'box-shadow 200ms ease-out',
        marginBottom: 20,
      }}
    >
      <div className="flex items-center justify-between" style={{ marginBottom: 20 }}>
        <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 15, fontWeight: 400, color: 'var(--text-primary)' }}>{title}</span>
        <div className="flex items-center" style={{ gap: 12 }}>
          {copyText && <CopyButton text={copyText} />}
          <button style={{ fontFamily: "'Inter', sans-serif", fontSize: 12, fontWeight: 300, color: 'var(--text-muted)', background: 'none', border: 'none', cursor: 'pointer' }}>
            Regenerate
          </button>
        </div>
      </div>
      {children}
    </div>
  );
}

function LandingPageAsset() {
  const lp = MOCK_LANDING_PAGE;
  const allText = `${lp.headline}\n${lp.subheadline}\n\n${lp.benefits.join('\n')}\n\n${lp.cta}\n\n${lp.socialProof}`;

  return (
    <SectionBlock title="Landing page preview" copyText={allText}>
      <div style={{ borderRadius: 12, border: '1px solid var(--divider-light)', overflow: 'hidden' }}>
        <div style={{ padding: '40px 32px', textAlign: 'center', backgroundColor: 'var(--surface-bg)' }}>
          <h3 className="font-heading" style={{ fontSize: 26, letterSpacing: '-0.02em', lineHeight: 1.25, marginBottom: 12 }}>{lp.headline}</h3>
          <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 15, fontWeight: 300, color: 'var(--text-secondary)', marginBottom: 28 }}>{lp.subheadline}</p>
          <div style={{ maxWidth: 340, margin: '0 auto', textAlign: 'left', marginBottom: 28 }}>
            {lp.benefits.map((b, i) => (
              <div key={i} className="flex items-start" style={{ gap: 10, marginBottom: 10 }}>
                <span style={{ color: '#2D8B75', fontSize: 14, marginTop: 2 }}>✓</span>
                <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 300, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{b}</span>
              </div>
            ))}
          </div>
          <button style={{
            fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 400,
            color: '#FFFFFF', backgroundColor: 'var(--accent-purple)',
            border: 'none', borderRadius: 12, padding: '12px 28px', cursor: 'pointer',
          }}>
            {lp.cta}
          </button>
          <p style={{ fontFamily: "'Instrument Serif', serif", fontStyle: 'italic', fontSize: 13, color: 'var(--text-muted)', marginTop: 20 }}>{lp.socialProof}</p>
        </div>
      </div>
    </SectionBlock>
  );
}

function SurveyAsset() {
  const allText = MOCK_SURVEY.map((q) => `${q.question}${q.options ? '\n  ' + q.options.join(' / ') : ''}`).join('\n\n');

  return (
    <SectionBlock title="Customer discovery survey" copyText={allText}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {MOCK_SURVEY.map((q, i) => (
          <div key={q.id} style={{ padding: '16px 20px', borderRadius: 10, backgroundColor: 'var(--surface-bg)' }}>
            <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 400, color: 'var(--text-primary)', marginBottom: q.options ? 10 : 0 }}>
              <span style={{ color: 'var(--text-muted)', marginRight: 8 }}>{i + 1}.</span>
              {q.question}
            </p>
            {q.options && (
              <div className="flex flex-wrap" style={{ gap: 8 }}>
                {q.options.map((o) => (
                  <span key={o} style={{
                    fontFamily: "'Inter', sans-serif", fontSize: 12, fontWeight: 300,
                    color: 'var(--text-secondary)', padding: '4px 10px',
                    borderRadius: 6, border: '1px solid var(--divider-light)',
                  }}>
                    {o}
                  </span>
                ))}
              </div>
            )}
            {q.type === 'email' && (
              <div style={{ marginTop: 8, padding: '8px 12px', borderRadius: 8, border: '1px solid var(--divider-light)', backgroundColor: '#FFFFFF' }}>
                <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 12, color: 'var(--text-muted)' }}>email@example.com</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </SectionBlock>
  );
}

function SocialAsset() {
  const so = MOCK_SOCIAL_OUTREACH;
  return (
    <SectionBlock title="Social outreach message" copyText={so.message}>
      <div style={{ padding: 20, borderRadius: 14, backgroundColor: 'var(--surface-bg)', position: 'relative' }}>
        <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 11, fontWeight: 300, color: 'var(--text-muted)', marginBottom: 8, display: 'block' }}>
          Tone: {so.tone}
        </span>
        <div style={{
          padding: '16px 20px', borderRadius: '14px 14px 14px 4px',
          backgroundColor: '#FFFFFF', boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
        }}>
          <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 300, color: 'var(--text-secondary)', lineHeight: 1.75, whiteSpace: 'pre-line' }}>
            {so.message}
          </p>
        </div>
      </div>
    </SectionBlock>
  );
}

function MarketplaceAsset() {
  const ml = MOCK_MARKETPLACE;
  const allText = `${ml.title}\n\n${ml.hook}\n\n${ml.description}\n\nPrice: ${ml.pricing}`;
  return (
    <SectionBlock title="Marketplace listing" copyText={allText}>
      <div style={{ padding: 20, borderRadius: 12, border: '1px solid var(--divider-light)' }}>
        <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 400, color: 'var(--accent-purple)', marginBottom: 8 }}>{ml.hook}</p>
        <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 15, fontWeight: 400, color: 'var(--text-primary)', marginBottom: 12 }}>{ml.title}</p>
        <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 300, color: 'var(--text-secondary)', lineHeight: 1.75, marginBottom: 16 }}>{ml.description}</p>
        <span style={{
          fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 400,
          color: '#2D8B75', padding: '4px 10px', borderRadius: 6, backgroundColor: 'rgba(45,139,117,0.06)',
        }}>
          {ml.pricing}
        </span>
      </div>
    </SectionBlock>
  );
}

function DirectOutreachAsset() {
  const d = MOCK_DIRECT_OUTREACH;
  const allText = `Pitch:\n${d.pitchMessage}\n\nIntro Script:\n${d.introScript}\n\nValue Proposition:\n${d.valueProp}`;
  return (
    <SectionBlock title="Direct outreach kit" copyText={allText}>
      {[
        { label: 'Pitch message', text: d.pitchMessage },
        { label: 'Intro script', text: d.introScript },
        { label: 'Value proposition', text: d.valueProp },
      ].map((item) => (
        <div key={item.label} style={{ marginBottom: 16, padding: '16px 20px', borderRadius: 10, backgroundColor: 'var(--surface-bg)' }}>
          <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 11, fontWeight: 400, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', display: 'block', marginBottom: 8 }}>
            {item.label}
          </span>
          <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 300, color: 'var(--text-secondary)', lineHeight: 1.75 }}>{item.text}</p>
        </div>
      ))}
    </SectionBlock>
  );
}

const METHOD_COMPONENTS: Record<string, React.ComponentType> = {
  landing: LandingPageAsset,
  survey: SurveyAsset,
  social: SocialAsset,
  marketplace: MarketplaceAsset,
  direct: DirectOutreachAsset,
};

const METHOD_LABELS: Record<string, string> = {
  landing: 'Landing page',
  survey: 'Survey',
  social: 'Social outreach',
  marketplace: 'Marketplace listing',
  direct: 'Direct outreach',
};

interface Props {
  selectedMethods: Set<string>;
}

export default function GeneratedAssets({ selectedMethods }: Props) {
  const methods = Array.from(selectedMethods);

  if (methods.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 0' }}>
        <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 15, fontWeight: 300, color: 'var(--text-muted)' }}>
          Select validation methods in the Methods tab to generate assets.
        </p>
      </div>
    );
  }

  return (
    <div>
      {methods.map((id) => {
        const Comp = METHOD_COMPONENTS[id];
        if (!Comp) return null;
        return <Comp key={id} />;
      })}
    </div>
  );
}

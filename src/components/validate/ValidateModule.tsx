import { useState, useEffect, useRef } from 'react';
import { useIdea } from '@/context/IdeaContext';
import type { CommunityChannel, ValidationMethod } from '@/types/research-ui';
import { VALIDATION_METHODS } from '@/lib/research-ui-config';
import { useValidationPlan } from '@/hooks/use-research';
import { mapValidateCommunities } from '@/lib/transform';
import { useToast } from '@/hooks/use-toast';

/* ── Template generators per method ── */
function generateTemplate(method: ValidationMethod, idea: string, insight: string | undefined): { title: string; body: string; url: string } {
  const ideaText = idea || 'my business idea';
  const insightText = insight || '';
  const context = insightText ? `${ideaText} — specifically addressing: ${insightText}` : ideaText;

  switch (method.id) {
    case 'website':
      return {
        title: 'Landing page prompt',
        body: `Create a modern landing page for: ${context}.\n\nInclude:\n• A clear headline and value proposition\n• 3 key benefits section\n• Waitlist signup form with email capture\n• Social proof / testimonial placeholders\n• Clean, conversion-focused design`,
        url: `https://lovable.dev/projects/create?prompt=${encodeURIComponent(`Create a landing page for: ${context}. Include a waitlist signup form, headline, value proposition, benefits section, and social proof.`)}`,
      };
    case 'form':
      return {
        title: 'Survey questions',
        body: `Discovery survey for: ${ideaText}\n\n1. What's your biggest frustration with [current solution]?\n2. How often do you experience this problem? (Daily / Weekly / Monthly / Rarely)\n3. What do you currently pay to solve this? ($0 / $1-10 / $10-50 / $50+)\n4. If a solution like "${ideaText}" existed, would you switch? (Definitely / Probably / Maybe / No)\n5. What's the maximum you'd pay monthly for this? (Open-ended)\n6. What features matter most to you? (Rank: Ease of use / Price / Speed / Quality / Support)`,
        url: `https://docs.google.com/forms/u/0/create`,
      };
    case 'whatsapp':
      return {
        title: 'WhatsApp message',
        body: `Hey! 👋 I'm working on something new and would love your honest opinion.\n\nThe idea: ${ideaText}\n${insightText ? `\nIt solves: ${insightText}\n` : ''}\nQuick questions:\n1. Is this something you'd actually use?\n2. What would you pay for it?\n3. What's missing that would make it a must-have?\n\nThanks! 🙏`,
        url: `https://wa.me/?text=${encodeURIComponent(`Hey! I'm working on "${ideaText}" and would love your opinion. Would you use something like this? What would you pay?`)}`,
      };
    case 'reddit':
      return {
        title: 'Reddit post',
        body: `Title: Would you use a [solution] for [problem]?\n\nHey everyone,\n\nI've been researching "${ideaText}" and noticed that ${insightText || 'there seems to be demand for this'}.\n\nBefore I build anything, I want to validate:\n• Would you actually pay for this?\n• What's missing from current solutions?\n• What would make you switch?\n\nHonest feedback appreciated — trying to figure out if this is worth pursuing or not.`,
        url: `https://www.reddit.com/submit?type=self&title=${encodeURIComponent(`Would you use: ${ideaText}?`)}`,
      };
    case 'twitter':
      return {
        title: 'Tweet / thread',
        body: `🧵 I'm validating a new idea and want your brutally honest take:\n\n"${ideaText}"\n${insightText ? `\nThe problem: ${insightText}\n` : ''}\nWould you:\n→ Use this? (Yes / Maybe / No)\n→ Pay for it? (How much?)\n→ What's the #1 feature you'd need?\n\nDMs open for deeper feedback 🙏`,
        url: `https://twitter.com/intent/tweet?text=${encodeURIComponent(`I'm validating: "${ideaText}" — would you use this? What would you pay? Reply or DM me 🙏`)}`,
      };
    case 'linkedin':
      return {
        title: 'LinkedIn post',
        body: `I'm exploring a new venture and would love feedback from my network.\n\nThe idea: ${ideaText}\n${insightText ? `\nThe insight: ${insightText}\n` : ''}\nBefore investing time building, I want to understand:\n• Is this a real pain point for you or your team?\n• What would you expect to pay for a solution?\n• Who else should I talk to about this?\n\nAll feedback welcome — the more honest, the better.`,
        url: `https://www.linkedin.com/feed/?shareActive=true`,
      };
    case 'google_ads':
      return {
        title: 'Google Ads setup',
        body: `Campaign type: Search\nGoal: Website traffic / Lead generation\n\nSuggested keywords:\n• "${ideaText}"\n• "${ideaText} alternative"\n• "${ideaText} near me"\n• "best ${ideaText}"\n• "${ideaText} pricing"\n\nHeadline 1: ${ideaText} — Try It Free\nHeadline 2: The Smarter Way to [Solve Problem]\nDescription: ${insightText || 'Discover a better solution'}. Sign up for early access today.\n\nBudget: Start with $10-20/day for 7 days to test demand.`,
        url: `https://ads.google.com/home/`,
      };
    case 'meta_ads':
      return {
        title: 'Meta Ads setup',
        body: `Campaign objective: Lead generation\nPlatform: Facebook + Instagram\n\nAudience targeting:\n• Interest-based: [related interests to ${ideaText}]\n• Age: 25-45\n• Location: [your target market]\n\nAd copy:\n"Tired of [problem]? We're building ${ideaText} — a better way to [benefit].\n${insightText ? insightText + '.\n' : ''}Sign up for early access."\n\nBudget: Start with $15/day for 5-7 days.`,
        url: `https://business.facebook.com/adsmanager/create`,
      };
    default:
      return { title: method.name, body: `Use ${method.name} to validate: ${ideaText}`, url: '#' };
  }
}

export default function ValidateModule() {
  const { idea, selectedInsight } = useIdea();
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedMethod, setSelectedMethod] = useState<string>('');
  const [copiedField, setCopiedField] = useState(false);
  const [activeChannels, setActiveChannels] = useState<Set<string>>(new Set());
  const { toast } = useToast();
  const validationQuery = useValidationPlan();

  const communities: CommunityChannel[] = mapValidateCommunities(validationQuery.data) || [];

  useEffect(() => {
    if (validationQuery.error) {
      toast({
        title: 'Validation plan unavailable',
        description: validationQuery.error instanceof Error ? validationQuery.error.message : 'Unexpected error',
        variant: 'destructive',
      });
    }
  }, [validationQuery.error, toast]);

  useEffect(() => {
    const el = containerRef.current;
    if (el) requestAnimationFrame(() => el.classList.add('visible'));
  }, []);

  const toggleChannel = (id: string) => {
    setActiveChannels((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const currentMethod = VALIDATION_METHODS.find((m) => m.id === selectedMethod);
  const template = currentMethod ? generateTemplate(currentMethod, idea, selectedInsight?.title) : null;

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedField(true);
    setTimeout(() => setCopiedField(false), 2000);
    toast({ title: 'Copied to clipboard' });
  };

  return (
    <div ref={containerRef} className="scroll-reveal" style={{ maxWidth: 800, margin: '0 auto', padding: '0 24px' }}>

      {/* ── HEADER ── */}
      <div style={{ marginBottom: 40 }}>
        <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 10 }}>
          DEMAND VALIDATION
        </p>
        <p className="font-heading" style={{ fontSize: 26, marginBottom: 8 }}>
          Will people actually pay for this?
        </p>
        <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 300, lineHeight: 1.7, color: 'var(--text-secondary)', maxWidth: 520 }}>
          Pick a validation method, get a ready-to-use template, and share it with the right audience.
        </p>
      </div>

      {/* ── METHOD SELECTOR ── */}
      <div style={{ marginBottom: 16 }}>
        <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 14 }}>
          CHOOSE YOUR METHOD
        </p>
        <select
          value={selectedMethod}
          onChange={(e) => { setSelectedMethod(e.target.value); setCopiedField(false); }}
          style={{
            width: '100%',
            maxWidth: 420,
            padding: '12px 16px',
            borderRadius: 12,
            border: '1px solid var(--divider-light)',
            backgroundColor: 'var(--surface-card)',
            fontFamily: "'Inter', sans-serif",
            fontSize: 14,
            fontWeight: 400,
            color: selectedMethod ? 'var(--text-primary)' : 'var(--text-muted)',
            outline: 'none',
            cursor: 'pointer',
            appearance: 'none',
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='12' height='8' viewBox='0 0 12 8' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1.5L6 6.5L11 1.5' stroke='%239B9B9B' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E")`,
            backgroundRepeat: 'no-repeat',
            backgroundPosition: 'right 14px center',
            paddingRight: 40,
          }}
        >
          <option value="">Select a validation method…</option>
          <optgroup label="Build">
            {VALIDATION_METHODS.filter((m) => m.category === 'build').map((m) => (
              <option key={m.id} value={m.id}>{m.name}</option>
            ))}
          </optgroup>
          <optgroup label="Outreach">
            {VALIDATION_METHODS.filter((m) => m.category === 'outreach').map((m) => (
              <option key={m.id} value={m.id}>{m.name}</option>
            ))}
          </optgroup>
          <optgroup label="Social">
            {VALIDATION_METHODS.filter((m) => m.category === 'social').map((m) => (
              <option key={m.id} value={m.id}>{m.name}</option>
            ))}
          </optgroup>
          <optgroup label="Paid Ads">
            {VALIDATION_METHODS.filter((m) => m.category === 'paid').map((m) => (
              <option key={m.id} value={m.id}>{m.name}</option>
            ))}
          </optgroup>
        </select>
      </div>

      {/* ── TEMPLATE PREVIEW ── */}
      {template && currentMethod && (
        <div
          className="rounded-2xl mb-12"
          style={{
            backgroundColor: 'var(--surface-card)',
            border: '1px solid var(--divider-light)',
            overflow: 'hidden',
          }}
        >
          {/* Template header */}
          <div
            className="flex items-center justify-between px-5 py-3"
            style={{ borderBottom: '1px solid var(--divider-light)', backgroundColor: 'var(--surface-input)' }}
          >
            <div className="flex items-center gap-2">
              <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 500, color: 'var(--text-primary)' }}>
                {template.title}
              </span>
              <span
                className="rounded-md px-2 py-0.5"
                style={{
                  fontSize: 10,
                  fontFamily: "'Inter', sans-serif",
                  fontWeight: 400,
                  color: currentMethod.effort === 'low' ? '#1a7a63' : currentMethod.effort === 'medium' ? '#b87a0a' : '#c43c3c',
                  backgroundColor: currentMethod.effort === 'low' ? 'rgba(45,139,117,0.08)' : currentMethod.effort === 'medium' ? 'rgba(212,136,15,0.08)' : 'rgba(224,82,82,0.08)',
                }}
              >
                {currentMethod.effort} effort
              </span>
            </div>
            <button
              onClick={() => handleCopy(template.body)}
              className="rounded-lg px-3 py-1.5 transition-all duration-200 active:scale-[0.96]"
              style={{
                fontSize: 12,
                fontFamily: "'Inter', sans-serif",
                fontWeight: 400,
                backgroundColor: copiedField ? 'rgba(45,139,117,0.08)' : 'var(--surface-bg)',
                color: copiedField ? '#1a7a63' : 'var(--text-secondary)',
                border: '1px solid var(--divider-light)',
                cursor: 'pointer',
              }}
            >
              {copiedField ? '✓ Copied' : 'Copy'}
            </button>
          </div>

          {/* Template body */}
          <div className="px-5 py-4">
            <pre
              style={{
                fontFamily: "'Inter', sans-serif",
                fontSize: 13,
                fontWeight: 300,
                color: 'var(--text-secondary)',
                lineHeight: 1.7,
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
                margin: 0,
              }}
            >
              {template.body}
            </pre>
          </div>

          {/* Go to platform */}
          <div
            className="flex items-center justify-between px-5 py-3"
            style={{ borderTop: '1px solid var(--divider-light)', backgroundColor: 'var(--surface-input)' }}
          >
            <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 12, fontWeight: 300, color: 'var(--text-muted)' }}>
              {currentMethod.description}
            </span>
            <a
              href={template.url}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-xl px-4 py-2 transition-all duration-200 active:scale-[0.97] inline-flex items-center gap-1.5"
              style={{
                fontSize: 13,
                fontFamily: "'Inter', sans-serif",
                fontWeight: 500,
                backgroundColor: 'var(--accent-purple)',
                color: '#fff',
                textDecoration: 'none',
                whiteSpace: 'nowrap',
              }}
            >
              Open {currentMethod.name} →
            </a>
          </div>
        </div>
      )}

      {!selectedMethod && (
        <div
          className="rounded-2xl p-8 text-center mb-12"
          style={{ backgroundColor: 'var(--surface-input)', border: '1px dashed var(--divider-light)' }}
        >
          <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 300, color: 'var(--text-muted)' }}>
            Select a method above to see a ready-to-use template
          </p>
        </div>
      )}

      {/* ── DISTRIBUTION CHANNELS ── */}
      <div style={{ marginBottom: 48 }}>
        <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 6 }}>
          DISTRIBUTION CHANNELS
        </p>
        <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 300, color: 'var(--text-muted)', marginBottom: 14 }}>
          Relevant communities to share your validation experiment.
        </p>

        {communities.length === 0 && !validationQuery.isFetching ? (
          <div className="rounded-xl p-6 text-center" style={{ backgroundColor: 'var(--surface-input)' }}>
            <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, color: 'var(--text-muted)' }}>
              No community channels found for this idea yet.
            </p>
          </div>
        ) : validationQuery.isFetching ? (
          <div className="rounded-xl p-6 text-center" style={{ backgroundColor: 'var(--surface-input)' }}>
            <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, color: 'var(--text-muted)' }}>Loading channels…</p>
          </div>
        ) : (
          <div className="rounded-xl overflow-hidden" style={{ border: '1px solid var(--divider-light)' }}>
            <div
              className="grid items-center px-4 py-2.5"
              style={{
                gridTemplateColumns: '1fr 90px 90px 100px',
                backgroundColor: 'var(--surface-input)',
                borderBottom: '1px solid var(--divider-light)',
              }}
            >
              <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 11, fontWeight: 400, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Channel</span>
              <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 11, fontWeight: 400, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Platform</span>
              <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 11, fontWeight: 400, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Members</span>
              <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 11, fontWeight: 400, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', textAlign: 'center' }}>Status</span>
            </div>
            {communities.map((c) => {
              const isActive = activeChannels.has(c.id);
              return (
                <div
                  key={c.id}
                  className="grid items-center px-4 py-3 transition-colors duration-150"
                  style={{
                    gridTemplateColumns: '1fr 90px 90px 100px',
                    borderBottom: '1px solid var(--divider-light)',
                    backgroundColor: isActive ? 'rgba(45,139,117,0.03)' : 'var(--surface-card)',
                  }}
                >
                  <div>
                    <a
                      href={c.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 400, color: 'var(--text-primary)', textDecoration: 'none' }}
                    >
                      {c.name} <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>↗</span>
                    </a>
                    <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 11, fontWeight: 300, color: 'var(--text-muted)', marginTop: 2, lineHeight: 1.4 }}>
                      {c.rationale}
                    </p>
                  </div>
                  <span className="rounded-full px-2 py-0.5 text-center" style={{ fontSize: 10, fontWeight: 500, backgroundColor: c.platformColor, color: '#fff', width: 'fit-content' }}>
                    {c.platform}
                  </span>
                  <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 12, color: 'var(--text-secondary)', fontVariantNumeric: 'tabular-nums' }}>
                    {c.members}
                  </span>
                  <div style={{ textAlign: 'center' }}>
                    <button
                      onClick={() => toggleChannel(c.id)}
                      className="rounded-lg px-3 py-1 transition-all duration-200 active:scale-[0.96]"
                      style={{
                        fontSize: 11,
                        fontFamily: "'Inter', sans-serif",
                        fontWeight: 400,
                        backgroundColor: isActive ? 'rgba(45,139,117,0.1)' : 'var(--surface-input)',
                        color: isActive ? '#1a7a63' : 'var(--text-muted)',
                        border: 'none',
                        cursor: 'pointer',
                      }}
                    >
                      {isActive ? '✓ Shared' : 'Mark shared'}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

import { useScrollReveal } from '@/hooks/use-scroll-reveal';

const steps = [
  {
    num: 1,
    title: 'Customer signals',
    desc: 'Real complaints, wishes, and gaps from Reddit, Yelp, and local forums. Not guesses — direct quotes from people who want what you\'re building.',
    sample: '"Every juice bar in Plano is overpriced franchise garbage. I\'d pay more for something real." — r/plano',
    bg: 'rgba(108,92,231,0.06)',
    color: '#6C5CE7',
  },
  {
    num: 2,
    title: 'Market reality',
    desc: 'Competitors, opportunity size, customer segments — and why this gap still exists. The root cause nobody else tells you.',
    sample: 'Root cause: Franchise chains hold exclusive strip-center leases. Your opening: the Legacy West food hall has open vendor slots.',
    bg: 'rgba(45,139,117,0.06)',
    color: '#2D8B75',
  },
  {
    num: 3,
    title: 'Launch costs',
    desc: 'Not generic advice. Specific: kiosk vs. storefront pricing, local suppliers, who to hire and what they earn in your city.',
    sample: 'Minimum viable: $47K (food hall kiosk). Recommended: $95K (600 sq ft near Legacy). Supplier: Profound Foods, Lucas TX.',
    bg: 'rgba(59,130,246,0.06)',
    color: '#3B82F6',
  },
  {
    num: 4,
    title: 'Validation toolkit',
    desc: 'A landing page headline, a 7-question survey, and the exact communities to test in. Plus a scorecard: go, pivot, or walk away.',
    sample: 'Headline: "Plano deserves a real juice bar." Test in: r/plano (42K), Dallas Foodies (89K), Nextdoor Frisco.',
    bg: 'rgba(212,136,15,0.06)',
    color: '#D4880F',
  },
];

export default function WhatYouGet() {
  const headingRef = useScrollReveal();

  return (
    <section className="px-6 mx-auto" style={{ maxWidth: 500 }}>
      <div ref={headingRef} className="scroll-reveal text-center">
        <h2 className="font-heading">What you get</h2>
        <p className="font-caption" style={{ marginTop: 8 }}>
          One sentence in. A complete plan out.
        </p>
      </div>

      <div style={{ marginTop: 40 }}>
        {steps.map((step, i) => {
          const ref = useScrollReveal(i * 100);
          return (
            <div
              key={step.num}
              ref={ref}
              className="scroll-reveal flex gap-4"
              style={{
                padding: '24px 0',
                borderBottom: i < steps.length - 1 ? '1px solid var(--divider)' : 'none',
              }}
            >
              <div
                className="shrink-0 flex items-center justify-center font-button"
                style={{
                  width: 30,
                  height: 30,
                  borderRadius: 8,
                  backgroundColor: step.bg,
                  color: step.color,
                  fontSize: 14,
                }}
              >
                {step.num}
              </div>
              <div className="flex-1 min-w-0">
                <p style={{ fontSize: 15, fontWeight: 400, color: 'var(--text-primary)' }}>
                  {step.title}
                </p>
                <p style={{ fontSize: 13, fontWeight: 300, color: '#6B6B6B', marginTop: 4, lineHeight: 1.6 }}>
                  {step.desc}
                </p>
                <div
                  style={{
                    marginTop: 12,
                    padding: '12px 14px',
                    backgroundColor: 'var(--surface-input)',
                    borderRadius: 10,
                    fontSize: 12,
                    fontWeight: 300,
                    fontStyle: 'italic',
                    color: 'var(--text-secondary)',
                    lineHeight: 1.6,
                  }}
                >
                  {step.sample}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

import { useScrollReveal } from '@/hooks/use-scroll-reveal';

export default function Story() {
  const p1 = useScrollReveal();
  const p2 = useScrollReveal(80);
  const p3 = useScrollReveal(160);
  const quote = useScrollReveal(240);
  const p4 = useScrollReveal(320);

  return (
    <section className="px-6 mx-auto" style={{ maxWidth: 500 }}>
      <p ref={p1} className="scroll-reveal font-body">
        The number one reason startups fail isn't money, timing, or competition.{' '}
        <span className="font-body-strong">It's building something nobody wants.</span>
      </p>

      <p ref={p2} className="scroll-reveal font-body" style={{ marginTop: 40 }}>
        The Lean Startup  framework solved this twenty years ago: get out of the building. Talk to customers. Test before you build.
      </p>

      <p ref={p3} className="scroll-reveal font-body" style={{ marginTop: 40 }}>
        The problem is, that takes <span className="font-body-strong">weeks</span>. You're reading Reddit threads at midnight. You're Googling competitors one by one. You're guessing at costs. By the time you have answers, you've lost momentum — or worse, you've talked yourself out of it.
      </p>

      <blockquote
        ref={quote}
        className="scroll-reveal"
        style={{
          marginTop: 40,
          padding: '24px 0',
          borderTop: '1px solid var(--divider)',
          borderBottom: '1px solid var(--divider)'
        }}>
        
        <p
          style={{
            fontFamily: "'Instrument Serif', serif",
            fontSize: 18,
            fontStyle: 'italic',
            color: 'var(--text-primary)',
            lineHeight: 1.5
          }}>
          
          "I spent three weeks researching my restaurant concept. By the time I finished, I was too exhausted to actually start."
        </p>
        <p className="font-caption" style={{ marginTop: 12 }}>
          r/Entrepreneur
        </p>
      </blockquote>

      <p ref={p4} className="scroll-reveal font-body" style={{ marginTop: 40 }}>
        LaunchLens does the legwork. You type one sentence about your idea. We scan the places where your future customers{' '}
        <span className="font-body-strong">already talk</span> — Reddit, Yelp, local forums — and come back with the four things you need before you spend a dollar.
      </p>
    </section>);

}
import { useNavigate } from 'react-router-dom';
import { useScrollReveal } from '@/hooks/use-scroll-reveal';

export default function FinalCTA() {
  const ref = useScrollReveal();
  const navigate = useNavigate();

  return (
    <section ref={ref} className="scroll-reveal px-6 mx-auto text-center" style={{ maxWidth: 500 }}>
      <h2 className="font-heading">Stop researching. Start validating.</h2>

      <button
        onClick={() => navigate('/auth')}
        className="font-button transition-all duration-200"
        style={{
          marginTop: 28,
          backgroundColor: 'var(--accent-purple)',
          color: '#FFFFFF',
          fontSize: 15,
          borderRadius: 14,
          padding: '14px 28px',
          border: 'none',
          cursor: 'pointer',
        }}
        onMouseDown={(e) => (e.currentTarget.style.transform = 'scale(0.97)')}
        onMouseUp={(e) => (e.currentTarget.style.transform = 'scale(1)')}
        onMouseLeave={(e) => (e.currentTarget.style.transform = 'scale(1)')}
      >
        Get started →
      </button>

      <p className="font-caption" style={{ marginTop: 12 }}>
        Free to explore. Signup only to save results.
      </p>
    </section>
  );
}

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useScrollReveal } from '@/hooks/use-scroll-reveal';
import { useIdea } from '@/context/IdeaContext';

const suggestions = [
  { label: 'Juice bar in Plano', value: 'A fresh-pressed juice bar in Plano, Texas' },
  { label: 'AI tutor app', value: 'An AI-powered tutoring app for high school students' },
  { label: 'Thai food Dallas', value: 'An authentic Thai street food restaurant in Dallas' },
];

export default function Hero() {
  const [idea, setIdea] = useState('');
  const { setIdea: setGlobalIdea } = useIdea();
  const navigate = useNavigate();
  const headlineRef = useScrollReveal();

  const handleStart = () => {
    if (!idea.trim()) return;
    setGlobalIdea(idea.trim());
    navigate('/research');
  };
  const subtitleRef = useScrollReveal(80);
  const inputRef = useScrollReveal(160);

  return (
    <section className="flex flex-col items-center px-6" style={{ paddingTop: 160 }}>
      <h1 ref={headlineRef} className="scroll-reveal font-heading text-center" style={{ maxWidth: 520 }}>
        Don't build something nobody wants.
      </h1>

      <p
        ref={subtitleRef}
        className="scroll-reveal font-body text-center"
        style={{ maxWidth: 440, marginTop: 16 }}
      >
        Describe your idea. Get real customer signals, market gaps, launch costs, and a validation plan — in ten minutes.
      </p>

      <div ref={inputRef} className="scroll-reveal w-full flex flex-col items-center" style={{ marginTop: 44, maxWidth: 500 }}>
        <textarea
          value={idea}
          onChange={(e) => setIdea(e.target.value)}
          placeholder="Describe your idea in one sentence..."
          rows={1}
          className="w-full resize-none outline-none transition-all duration-200"
          style={{
            minHeight: 52,
            padding: '16px 18px',
            border: '1px solid var(--divider-light)',
            borderRadius: 14,
            backgroundColor: 'var(--surface-card)',
            fontFamily: "'Inter', sans-serif",
            fontSize: 15,
            fontWeight: 300,
            lineHeight: 1.75,
            color: 'var(--text-primary)',
          }}
          onFocus={(e) => {
            e.currentTarget.style.borderColor = 'var(--accent-purple)';
            e.currentTarget.style.boxShadow = '0 0 0 3px rgba(108,92,231,0.08)';
          }}
          onBlur={(e) => {
            e.currentTarget.style.borderColor = 'var(--divider-light)';
            e.currentTarget.style.boxShadow = 'none';
          }}
        />

        <div className="w-full flex items-center justify-between" style={{ marginTop: 10 }}>
          <p style={{ fontSize: 13, color: '#6B6B6B', fontWeight: 300 }}>
            Try:{' '}
            {suggestions.map((s, i) => (
              <span key={s.label}>
                <span
                  className="cursor-pointer transition-colors duration-200"
                  style={{ color: '#6B6B6B' }}
                  onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--accent-purple)')}
                  onMouseLeave={(e) => (e.currentTarget.style.color = '#6B6B6B')}
                  onClick={() => setIdea(s.value)}
                >
                  {s.label}
                </span>
                {i < suggestions.length - 1 && ' · '}
              </span>
            ))}
          </p>

          <button
            className="font-button shrink-0 transition-all duration-200"
            style={{
              backgroundColor: 'var(--accent-purple)',
              color: '#FFFFFF',
              fontSize: 14,
              borderRadius: 12,
              padding: '10px 20px',
              opacity: idea.trim() ? 1 : 0.5,
              cursor: idea.trim() ? 'pointer' : 'default',
            }}
            onClick={handleStart}
            onMouseDown={(e) => (e.currentTarget.style.transform = 'scale(0.97)')}
            onMouseUp={(e) => (e.currentTarget.style.transform = 'scale(1)')}
            onMouseLeave={(e) => (e.currentTarget.style.transform = 'scale(1)')}
          >
            Research this idea →
          </button>
        </div>
      </div>
    </section>
  );
}

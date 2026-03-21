import { useIdea, type Step } from '@/context/IdeaContext';
import { useNavigate } from 'react-router-dom';
import { useEffect, useRef } from 'react';

const STEPS: { key: Step; label: string; placeholder: string }[] = [
  { key: 'discover', label: 'Discover', placeholder: 'Scanning real conversations...' },
  { key: 'analyze', label: 'Analyze', placeholder: 'Understanding the opportunity...' },
  { key: 'setup', label: 'Setup', placeholder: 'Designing your launch plan...' },
  { key: 'validate', label: 'Validate', placeholder: 'Testing real demand...' },
];

function StepperDot({ step, index, currentIndex }: { step: typeof STEPS[number]; index: number; currentIndex: number }) {
  const isActive = index === currentIndex;
  const isCompleted = index < currentIndex;
  const isFuture = index > currentIndex;

  const dotColor = isCompleted
    ? 'var(--accent-purple)'
    : isActive
      ? 'var(--accent-purple)'
      : 'var(--divider-light)';

  return (
    <div className="flex flex-col items-center" style={{ opacity: isFuture ? 0.35 : 1, transition: 'opacity 300ms ease-out' }}>
      <div
        style={{
          width: 10,
          height: 10,
          borderRadius: '50%',
          backgroundColor: isCompleted ? 'var(--accent-purple)' : 'transparent',
          border: `2px solid ${dotColor}`,
          transition: 'all 300ms ease-out',
        }}
      />
      <span
        style={{
          marginTop: 8,
          fontFamily: "'Inter', sans-serif",
          fontSize: 13,
          fontWeight: isActive ? 400 : 300,
          color: isActive ? 'var(--text-primary)' : 'var(--text-muted)',
          transition: 'all 300ms ease-out',
        }}
      >
        {step.label}
      </span>
    </div>
  );
}

export default function Research() {
  const { idea, currentStep } = useIdea();
  const navigate = useNavigate();
  const contentRef = useRef<HTMLDivElement>(null);

  const currentIndex = STEPS.findIndex((s) => s.key === currentStep);
  const activeStep = STEPS[currentIndex];

  useEffect(() => {
    if (!idea) navigate('/', { replace: true });
  }, [idea, navigate]);

  // Fade-in on mount
  useEffect(() => {
    const el = contentRef.current;
    if (el) {
      requestAnimationFrame(() => el.classList.add('visible'));
    }
  }, [currentStep]);

  if (!idea) return null;

  return (
    <div style={{ minHeight: '100vh', backgroundColor: 'var(--surface-bg)' }}>
      {/* Top bar */}
      <header
        className="flex items-center justify-between px-6"
        style={{ height: 64 }}
      >
        <span
          className="cursor-pointer"
          style={{ fontSize: 18 }}
          onClick={() => navigate('/')}
        >
          <span style={{ fontFamily: "'Inter', sans-serif", fontWeight: 400 }}>Launch</span>
          <span style={{ fontFamily: "'Instrument Serif', serif", fontStyle: 'italic', fontWeight: 400 }}>{'\u200B'}Lens</span>
        </span>

        <div className="flex items-center" style={{ gap: 24 }}>
          <span
            className="cursor-pointer transition-colors duration-200"
            style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 300, color: 'var(--text-muted)' }}
            onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--accent-purple)')}
            onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-muted)')}
            onClick={() => navigate('/')}
          >
            New idea
          </span>
          <span
            className="cursor-pointer"
            style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 300, color: 'var(--text-muted)' }}
          >
            Saved
          </span>
          <div
            style={{
              width: 28,
              height: 28,
              borderRadius: '50%',
              backgroundColor: 'rgba(108,92,231,0.08)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontFamily: "'Inter', sans-serif",
              fontSize: 12,
              fontWeight: 400,
              color: 'var(--accent-purple)',
            }}
          >
            R
          </div>
        </div>
      </header>

      {/* Context strip */}
      <div
        className="sticky z-40"
        style={{
          top: 0,
          backdropFilter: 'blur(16px)',
          backgroundColor: 'rgba(250,250,248,0.85)',
          padding: '20px 24px',
          textAlign: 'center',
        }}
      >
        <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 12, fontWeight: 300, color: 'var(--text-muted)', marginBottom: 6 }}>
          Your idea
        </p>
        <p
          className="font-heading"
          style={{
            fontSize: 26,
            maxWidth: 600,
            margin: '0 auto',
            lineHeight: 1.25,
            letterSpacing: '-0.02em',
          }}
        >
          {idea}
        </p>
      </div>

      {/* Stepper */}
      <div style={{ maxWidth: 420, margin: '48px auto 0', padding: '0 24px', position: 'relative' }}>
        {/* Connecting line */}
        <div
          style={{
            position: 'absolute',
            top: 5,
            left: '15%',
            right: '15%',
            height: 1,
            backgroundColor: 'var(--divider-light)',
          }}
        />
        {/* Progress line */}
        <div
          style={{
            position: 'absolute',
            top: 5,
            left: '15%',
            width: `${(currentIndex / (STEPS.length - 1)) * 70}%`,
            height: 1,
            backgroundColor: 'var(--accent-purple)',
            transition: 'width 500ms ease-out',
          }}
        />

        <div className="relative flex items-start justify-between">
          {STEPS.map((step, i) => (
            <StepperDot key={step.key} step={step} index={i} currentIndex={currentIndex} />
          ))}
        </div>
      </div>

      {/* Content area */}
      <div
        ref={contentRef}
        key={currentStep}
        className="scroll-reveal"
        style={{
          maxWidth: 1100,
          margin: '0 auto',
          padding: '120px 24px 160px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: 'calc(100vh - 300px)',
        }}
      >
        <p
          className="font-heading"
          style={{
            fontSize: 26,
            textAlign: 'center',
            lineHeight: 1.25,
            letterSpacing: '-0.02em',
            maxWidth: 440,
          }}
        >
          {activeStep.placeholder}
        </p>
        <div
          style={{
            marginTop: 32,
            width: 36,
            height: 1,
            backgroundColor: 'var(--divider-section)',
          }}
        />
        <p
          style={{
            marginTop: 24,
            fontFamily: "'Inter', sans-serif",
            fontSize: 13,
            fontWeight: 300,
            color: 'var(--text-muted)',
            textAlign: 'center',
          }}
        >
          {currentIndex < STEPS.length - 1
            ? `Step ${currentIndex + 1} of ${STEPS.length}`
            : 'Final step'}
        </p>
      </div>
    </div>
  );
}

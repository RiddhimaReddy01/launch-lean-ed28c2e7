import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { listIdeas } from '@/api';
import EmptyState from '@/components/common/EmptyState';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import { Skeleton } from '@/components/ui/skeleton';
import { formatDistanceToNow } from 'date-fns';

export default function Dashboard() {
  const navigate = useNavigate();

  // Auth guard
  useEffect(() => {
    if (!localStorage.getItem('auth_token')) {
      navigate('/auth', { replace: true });
    }
  }, [navigate]);

  // Fetch all saved ideas
  const { data: ideas, isLoading, isError, error } = useQuery({
    queryKey: ['ideas'],
    queryFn: () => listIdeas(),
    staleTime: 1000 * 60 * 5,
  });

  // Handle logout
  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_email');
    navigate('/auth', { replace: true });
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: 'var(--surface-bg)' }}>
      {/* Header */}
      <header className="flex items-center justify-between px-6" style={{ height: 64 }}>
        <span
          className="cursor-pointer"
          style={{ fontSize: 18 }}
          onClick={() => navigate('/')}
        >
          <span style={{ fontFamily: "'Inter', sans-serif", fontWeight: 400 }}>Launch</span>
          <span style={{ fontFamily: "'Instrument Serif', serif", fontStyle: 'italic', fontWeight: 400 }}>
            {'\u200B'}Lens
          </span>
        </span>

        <div className="flex items-center" style={{ gap: 24 }}>
          <button
            onClick={() => navigate('/research')}
            style={{
              fontFamily: "'Inter', sans-serif",
              fontSize: 13,
              fontWeight: 300,
              color: 'var(--accent-purple)',
              cursor: 'pointer',
              border: 'none',
              backgroundColor: 'transparent',
              padding: 0,
            }}
          >
            New Analysis
          </button>
          <button
            onClick={handleLogout}
            style={{
              fontFamily: "'Inter', sans-serif",
              fontSize: 13,
              fontWeight: 300,
              color: 'var(--text-muted)',
              cursor: 'pointer',
              border: 'none',
              backgroundColor: 'transparent',
              padding: 0,
            }}
          >
            Logout
          </button>
        </div>
      </header>

      {/* Content */}
      <div style={{ maxWidth: 1100, margin: '0 auto', padding: '80px 24px 160px' }}>
        {/* Section title */}
        <div style={{ marginBottom: 48 }}>
          <p
            style={{
              fontFamily: "'Instrument Serif', serif",
              fontSize: 26,
              fontWeight: 400,
              color: 'var(--text-primary)',
              letterSpacing: '-0.02em',
              marginBottom: 8,
            }}
          >
            Your Research
          </p>
          <p
            style={{
              fontFamily: "'Inter', sans-serif",
              fontSize: 13,
              fontWeight: 300,
              color: 'var(--text-muted)',
            }}
          >
            {!isLoading && ideas ? `${ideas.length} saved idea${ideas.length !== 1 ? 's' : ''}` : 'Loading...'}
          </p>
        </div>

        {/* Error state */}
        {isError && (
          <div
            style={{
              padding: 24,
              backgroundColor: 'rgba(224, 82, 82, 0.05)',
              borderRadius: 12,
              textAlign: 'center',
            }}
          >
            <p style={{ color: 'var(--text-primary)', fontWeight: 500 }}>Failed to load ideas</p>
            <p style={{ color: 'var(--text-muted)', fontSize: 14, marginTop: 8 }}>
              {error instanceof Error ? error.message : 'Unknown error'}
            </p>
          </div>
        )}

        {/* Loading state */}
        {isLoading && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 16 }}>
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} style={{ height: 200, borderRadius: 14 }} />
            ))}
          </div>
        )}

        {/* Empty state */}
        {!isLoading && !isError && ideas && ideas.length === 0 && (
          <div style={{ maxWidth: 400, margin: '0 auto' }}>
            <EmptyState title="No ideas yet" message="Analyze an idea to save it here." />
            <button
              onClick={() => navigate('/research')}
              style={{
                display: 'block',
                margin: '32px auto 0',
                padding: '12px 24px',
                backgroundColor: 'var(--accent-purple)',
                color: 'white',
                border: 'none',
                borderRadius: 8,
                fontFamily: "'Inter', sans-serif",
                fontSize: 14,
                fontWeight: 400,
                cursor: 'pointer',
              }}
            >
              Start Analyzing
            </button>
          </div>
        )}

        {/* Ideas grid */}
        {!isLoading && !isError && ideas && ideas.length > 0 && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 16 }}>
            {ideas.map((idea) => (
              <IdeaCard key={idea.id} idea={idea} navigate={navigate} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function IdeaCard({
  idea,
  navigate,
}: {
  idea: any;
  navigate: ReturnType<typeof useNavigate>;
}) {
  const [hovered, setHovered] = React.useState(false);

  const moduleIndicators = [
    { name: 'decompose', done: idea.has_decompose },
    { name: 'discover', done: idea.has_discover },
    { name: 'analyze', done: idea.has_analyze },
    { name: 'setup', done: idea.has_setup },
    { name: 'validate', done: idea.has_validate },
  ];

  const formatDate = (dateStr: string) => {
    try {
      return formatDistanceToNow(new Date(dateStr), { addSuffix: true });
    } catch {
      return dateStr;
    }
  };

  return (
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onClick={() => navigate(`/ideas/${idea.id}`)}
      style={{
        padding: 24,
        borderRadius: 14,
        backgroundColor: '#FFFFFF',
        boxShadow: hovered ? '0 4px 16px rgba(0,0,0,0.06)' : '0 1px 3px rgba(0,0,0,0.04)',
        border: '1px solid var(--divider-light)',
        cursor: 'pointer',
        transition: 'all 200ms ease-out',
        transform: hovered ? 'translateY(-2px)' : 'translateY(0)',
      }}
    >
      {/* Title */}
      <p
        style={{
          fontFamily: "'Instrument Serif', serif",
          fontSize: 18,
          fontWeight: 400,
          color: 'var(--text-primary)',
          marginBottom: 12,
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
        }}
      >
        {idea.title}
      </p>

      {/* Date */}
      <p
        style={{
          fontFamily: "'Inter', sans-serif",
          fontSize: 12,
          fontWeight: 300,
          color: 'var(--text-muted)',
          marginBottom: 16,
        }}
      >
        {formatDate(idea.updated_at)}
      </p>

      {/* Module indicators (5 dots) */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        {moduleIndicators.map((mod) => (
          <div
            key={mod.name}
            style={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              backgroundColor: mod.done ? 'var(--accent-purple)' : '#D1D1D1',
              transition: 'background-color 200ms ease-out',
            }}
            title={mod.name}
          />
        ))}
      </div>

      {/* Status badge + Tags */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          flexWrap: 'wrap',
        }}
      >
        <span
          style={{
            fontSize: 12,
            fontWeight: 400,
            color: '#2D8B75',
            padding: '3px 8px',
            borderRadius: 6,
            backgroundColor: 'rgba(45,139,117,0.06)',
          }}
        >
          {idea.status}
        </span>
        {idea.tags && idea.tags.slice(0, 2).map((tag: string) => (
          <span
            key={tag}
            style={{
              fontSize: 11,
              fontWeight: 300,
              color: 'var(--text-muted)',
              padding: '2px 6px',
              borderRadius: 4,
              backgroundColor: 'var(--surface-input)',
            }}
          >
            {tag}
          </span>
        ))}
        {idea.tags && idea.tags.length > 2 && (
          <span
            style={{
              fontSize: 11,
              fontWeight: 300,
              color: 'var(--text-muted)',
            }}
          >
            +{idea.tags.length - 2}
          </span>
        )}
      </div>
    </div>
  );
}

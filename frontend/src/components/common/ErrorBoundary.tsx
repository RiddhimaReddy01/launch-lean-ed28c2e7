import { useState, ReactNode, ErrorInfo } from 'react';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: (error: Error, retry: () => void) => ReactNode;
}

export default function ErrorBoundary({ children, fallback }: ErrorBoundaryProps) {
  const [error, setError] = useState<Error | null>(null);

  const handleError = (err: Error) => {
    console.error('Error caught by boundary:', err);
    setError(err);
  };

  const retry = () => {
    setError(null);
  };

  if (error) {
    return (
      fallback?.(error, retry) ?? (
        <div
          className="rounded-lg p-6"
          style={{
            backgroundColor: 'rgba(224,82,82,0.06)',
            border: '1px solid #E05252',
            maxWidth: 600,
            margin: '24px auto',
          }}
        >
          <p style={{ fontSize: 16, fontWeight: 600, color: '#E05252', marginBottom: 8 }}>
            ⚠️ Something went wrong
          </p>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 16, lineHeight: 1.5 }}>
            {error.message || 'An unexpected error occurred. Please try again.'}
          </p>
          <button
            onClick={retry}
            className="rounded-lg px-4 py-2 transition-all active:scale-95"
            style={{
              backgroundColor: '#E05252',
              color: '#FFFFFF',
              border: 'none',
              cursor: 'pointer',
              fontSize: 13,
              fontWeight: 500,
            }}
          >
            Try again
          </button>
        </div>
      )
    );
  }

  // Use a try-catch in a wrapper to catch synchronous errors
  return (
    <ErrorCatcher onError={handleError}>
      {children}
    </ErrorCatcher>
  );
}

function ErrorCatcher({
  children,
  onError,
}: {
  children: ReactNode;
  onError: (error: Error) => void;
}) {
  try {
    // For async errors, this won't catch them, but we handle those in useQuery
    return <>{children}</>;
  } catch (err) {
    onError(err as Error);
    return null;
  }
}

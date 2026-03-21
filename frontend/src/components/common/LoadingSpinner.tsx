export default function LoadingSpinner({
  message = "Loading...",
  size = 40,
}: {
  message?: string;
  size?: number;
}) {
  return (
    <div
      className="flex flex-col items-center justify-center py-12"
      style={{ gap: 12 }}
    >
      <div
        className="animate-spin"
        style={{
          width: size,
          height: size,
          border: `3px solid rgba(108,92,231,0.1)`,
          borderTop: `3px solid var(--accent-purple)`,
          borderRadius: '50%',
        }}
      />
      <p style={{ color: 'var(--text-muted)', fontSize: 14, textAlign: 'center' }}>
        {message}
      </p>
    </div>
  );
}

interface EmptyStateProps {
  title?: string;
  message: string;
}

export default function EmptyState({ title = 'Nothing yet', message }: EmptyStateProps) {
  return (
    <div className="text-center py-14 px-6 rounded-[12px]" style={{ background: 'var(--surface-card)' }}>
      <p className="font-heading mb-2" style={{ fontSize: 18, color: 'var(--text-primary)' }}>
        {title}
      </p>
      <p className="font-caption" style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
        {message}
      </p>
    </div>
  );
}

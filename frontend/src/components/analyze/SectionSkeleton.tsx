export default function SectionSkeleton() {
  return (
    <div style={{ padding: '48px 0' }}>
      {[260, 180, 220].map((w, i) => (
        <div
          key={i}
          className="animate-pulse"
          style={{
            height: 14,
            width: w,
            maxWidth: '100%',
            borderRadius: 6,
            backgroundColor: 'var(--divider)',
            marginBottom: i < 2 ? 20 : 0,
          }}
        />
      ))}
      <div
        className="animate-pulse"
        style={{
          height: 120,
          borderRadius: 12,
          backgroundColor: 'var(--surface-input)',
          marginTop: 32,
        }}
      />
    </div>
  );
}

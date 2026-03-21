import { useState } from 'react';
import { MOCK_COMMUNITIES } from '@/data/validate-mock';

export default function CommunityGrid() {
  const [usedIds, setUsedIds] = useState<Set<string>>(new Set());
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  const toggleUsed = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setUsedIds((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 16 }}>
      {MOCK_COMMUNITIES.map((ch) => {
        const isUsed = usedIds.has(ch.id);
        const isHovered = hoveredId === ch.id;

        return (
          <a
            key={ch.id}
            href={ch.url}
            target="_blank"
            rel="noopener noreferrer"
            onMouseEnter={() => setHoveredId(ch.id)}
            onMouseLeave={() => setHoveredId(null)}
            style={{
              display: 'block',
              padding: 24,
              borderRadius: 14,
              backgroundColor: isUsed ? 'rgba(45,139,117,0.03)' : '#FFFFFF',
              border: isUsed ? '1px solid rgba(45,139,117,0.2)' : '1px solid var(--divider-light)',
              textDecoration: 'none',
              transition: 'all 200ms ease-out',
              transform: isHovered ? 'translateY(-2px)' : 'translateY(0)',
              boxShadow: isHovered ? '0 4px 16px rgba(0,0,0,0.06)' : '0 1px 3px rgba(0,0,0,0.04)',
            }}
          >
            <div className="flex items-center justify-between" style={{ marginBottom: 12 }}>
              <div className="flex items-center" style={{ gap: 10 }}>
                <span style={{
                  fontFamily: "'Inter', sans-serif", fontSize: 15, fontWeight: 400, color: 'var(--text-primary)',
                }}>
                  {ch.name}
                </span>
                <span style={{
                  fontFamily: "'Inter', sans-serif", fontSize: 11, fontWeight: 400,
                  color: ch.platformColor, padding: '2px 8px', borderRadius: 6,
                  backgroundColor: `${ch.platformColor}10`,
                }}>
                  {ch.platform}
                </span>
              </div>
              <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 12, fontWeight: 300, color: 'var(--text-muted)' }}>
                {ch.members} members
              </span>
            </div>

            <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 300, color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: 14 }}>
              {ch.rationale}
            </p>

            <button
              onClick={(e) => toggleUsed(ch.id, e)}
              style={{
                fontFamily: "'Inter', sans-serif", fontSize: 12, fontWeight: 400,
                color: isUsed ? '#2D8B75' : 'var(--text-muted)',
                background: 'none', border: 'none', cursor: 'pointer',
                transition: 'color 200ms ease-out',
              }}
            >
              {isUsed ? '✓ Shared here' : 'Mark as shared'}
            </button>
          </a>
        );
      })}
    </div>
  );
}

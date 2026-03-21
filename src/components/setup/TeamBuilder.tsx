import { useState } from 'react';
import { MOCK_TEAM } from '@/data/setup-mock';

export default function TeamBuilder({ includedRoles, onToggleRole }: { includedRoles: Set<string>; onToggleRole: (id: string) => void }) {
  const [hoveredRole, setHoveredRole] = useState<string | null>(null);

  const teamCount = includedRoles.size;

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em' }}>
          TEAM COMPOSITION
        </p>
        <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 400, color: 'var(--accent-purple)' }}>
          {teamCount} role{teamCount !== 1 ? 's' : ''} selected
        </p>
      </div>

      <div className="flex flex-col gap-3">
        {MOCK_TEAM.map((role) => {
          const included = includedRoles.has(role.id);
          const hovered = hoveredRole === role.id;

          return (
            <div
              key={role.id}
              className="rounded-[12px] p-5 transition-all duration-200"
              style={{
                backgroundColor: included ? 'rgba(108,92,231,0.04)' : 'var(--surface-card)',
                boxShadow: hovered ? '0 4px 12px rgba(0,0,0,0.06)' : '0 1px 3px rgba(0,0,0,0.04)',
                border: included ? '1px solid rgba(108,92,231,0.15)' : '1px solid transparent',
                transform: hovered ? 'translateY(-2px)' : 'translateY(0)',
              }}
              onMouseEnter={() => setHoveredRole(role.id)}
              onMouseLeave={() => setHoveredRole(null)}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2 flex-wrap">
                    <p
                      className="transition-colors duration-150"
                      style={{
                        fontFamily: "'Inter', sans-serif",
                        fontSize: 15,
                        fontWeight: 400,
                        color: hovered ? 'var(--accent-purple)' : 'var(--text-primary)',
                      }}
                    >
                      {role.title}
                    </p>
                    <span
                      className="rounded-[6px] px-2 py-0.5"
                      style={{
                        fontFamily: "'Inter', sans-serif",
                        fontSize: 11,
                        fontWeight: 400,
                        backgroundColor: role.type === 'full-time' ? 'rgba(45,139,117,0.06)' : role.type === 'part-time' ? 'rgba(59,130,246,0.06)' : 'rgba(212,136,15,0.06)',
                        color: role.type === 'full-time' ? 'var(--accent-teal)' : role.type === 'part-time' ? 'var(--accent-blue)' : 'var(--accent-amber)',
                      }}
                    >
                      {role.type}
                    </span>
                  </div>
                  <p className="font-heading" style={{ fontSize: 26, marginBottom: 6, lineHeight: 1.25 }}>
                    {role.salaryRange}
                  </p>
                  <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 300, color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: 12 }}>
                    {role.description}
                  </p>
                  <a
                    href={role.linkedinSearch}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="transition-colors duration-150"
                    style={{
                      fontFamily: "'Inter', sans-serif",
                      fontSize: 12,
                      fontWeight: 400,
                      color: 'var(--accent-purple)',
                      textDecoration: 'none',
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.textDecoration = 'underline')}
                    onMouseLeave={(e) => (e.currentTarget.style.textDecoration = 'none')}
                  >
                    Search LinkedIn →
                  </a>
                </div>

                {/* Include toggle */}
                <button
                  onClick={() => onToggleRole(role.id)}
                  className="flex-shrink-0 rounded-[10px] px-4 py-2 transition-all duration-200 active:scale-[0.95]"
                  style={{
                    fontFamily: "'Inter', sans-serif",
                    fontSize: 12,
                    fontWeight: 400,
                    backgroundColor: included ? 'var(--accent-purple)' : 'rgba(108,92,231,0.06)',
                    color: included ? '#fff' : 'var(--accent-purple)',
                    border: 'none',
                    cursor: 'pointer',
                  }}
                >
                  {included ? '✓ In plan' : 'Add to plan'}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

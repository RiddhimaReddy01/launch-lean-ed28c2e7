import { MOCK_TIERS, MOCK_TEAM } from '@/data/setup-mock';
import type { TimelinePhase } from '@/data/setup-mock';

interface PlanSummaryProps {
  selectedTier: string;
  currentTotal: number;
  includedRoles: Set<string>;
  phases: TimelinePhase[];
}

function formatCurrency(n: number): string {
  if (n >= 1000) return `$${(n / 1000).toFixed(n % 1000 === 0 ? 0 : 1)}K`;
  return `$${n.toLocaleString()}`;
}

export default function PlanSummary({ selectedTier, currentTotal, includedRoles, phases }: PlanSummaryProps) {
  const tier = MOCK_TIERS.find((t) => t.id === selectedTier);
  const teamCount = includedRoles.size;
  const completedTasks = phases.reduce((sum, p) => sum + p.tasks.filter((t) => t.completed).length, 0);
  const totalTasks = phases.reduce((sum, p) => sum + p.tasks.length, 0);

  const teamRoles = MOCK_TEAM.filter((r) => includedRoles.has(r.id));
  const teamLabel = teamRoles.length > 0
    ? teamRoles.map((r) => r.title).join(', ')
    : 'No roles selected yet';

  return (
    <div
      className="rounded-[14px] p-6 md:p-8"
      style={{
        backgroundColor: 'rgba(108,92,231,0.03)',
        border: '1px solid rgba(108,92,231,0.08)',
      }}
    >
      <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em', marginBottom: 12, color: 'var(--accent-purple)' }}>
        YOUR PLAN SUMMARY
      </p>

      <p
        style={{
          fontFamily: "'Instrument Serif', serif",
          fontSize: 18,
          fontStyle: 'italic',
          color: 'var(--text-primary)',
          lineHeight: 1.6,
          marginBottom: 24,
        }}
      >
        You can launch this as a <span style={{ fontWeight: 400 }}>{tier?.title}</span> model in ~10–12 weeks with an estimated investment of{' '}
        <span style={{ fontWeight: 400 }}>{formatCurrency(currentTotal)}</span> and a team of{' '}
        <span style={{ fontWeight: 400 }}>{teamCount} {teamCount === 1 ? 'person' : 'people'}</span>.
      </p>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div>
          <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.04em', marginBottom: 4 }}>MODEL</p>
          <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 400, color: 'var(--text-primary)' }}>
            {tier?.model}
          </p>
        </div>
        <div>
          <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.04em', marginBottom: 4 }}>INVESTMENT</p>
          <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 400, color: 'var(--accent-purple)' }}>
            {formatCurrency(currentTotal)}
          </p>
        </div>
        <div>
          <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.04em', marginBottom: 4 }}>TEAM</p>
          <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 400, color: 'var(--text-primary)' }}>
            {teamLabel}
          </p>
        </div>
        <div>
          <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.04em', marginBottom: 4 }}>PROGRESS</p>
          <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 400, color: 'var(--text-primary)' }}>
            {completedTasks}/{totalTasks} tasks
          </p>
        </div>
      </div>
    </div>
  );
}

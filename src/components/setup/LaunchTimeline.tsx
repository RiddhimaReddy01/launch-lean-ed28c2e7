import { useState } from 'react';
import type { TimelinePhase } from '@/data/setup-mock';

export default function LaunchTimeline({ phases, onToggleTask }: { phases: TimelinePhase[]; onToggleTask: (phaseId: string, taskId: string) => void }) {
  const [expandedPhase, setExpandedPhase] = useState<string | null>(null);
  const [hoveredPhase, setHoveredPhase] = useState<string | null>(null);

  const totalTasks = phases.reduce((sum, p) => sum + p.tasks.length, 0);
  const completedTasks = phases.reduce((sum, p) => sum + p.tasks.filter((t) => t.completed).length, 0);
  const progress = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;

  return (
    <div>
      {/* Progress bar */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <p className="font-caption" style={{ fontSize: 11, letterSpacing: '0.06em' }}>LAUNCH PROGRESS</p>
          <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 12, fontWeight: 400, color: 'var(--accent-purple)' }}>
            {completedTasks}/{totalTasks} tasks
          </span>
        </div>
        <div style={{ height: 4, borderRadius: 2, backgroundColor: 'var(--divider)' }}>
          <div
            className="transition-all duration-500 ease-out"
            style={{ height: '100%', borderRadius: 2, width: `${progress}%`, backgroundColor: 'var(--accent-purple)', opacity: 0.7 }}
          />
        </div>
      </div>

      {/* Horizontal phase indicators */}
      <div className="flex items-start justify-between mb-10 relative" style={{ paddingTop: 4 }}>
        {/* Connecting line */}
        <div style={{ position: 'absolute', top: 9, left: '8%', right: '8%', height: 1, backgroundColor: 'var(--divider-light)' }} />
        <div
          className="transition-all duration-500 ease-out"
          style={{
            position: 'absolute',
            top: 9,
            left: '8%',
            height: 1,
            backgroundColor: 'var(--accent-purple)',
            opacity: 0.5,
            width: `${progress * 0.84}%`,
          }}
        />

        {phases.map((phase, i) => {
          const phaseComplete = phase.tasks.every((t) => t.completed);
          const phaseStarted = phase.tasks.some((t) => t.completed);
          const isActive = expandedPhase === phase.id;
          const isHovered = hoveredPhase === phase.id;

          return (
            <button
              key={phase.id}
              onClick={() => setExpandedPhase(expandedPhase === phase.id ? null : phase.id)}
              onMouseEnter={() => setHoveredPhase(phase.id)}
              onMouseLeave={() => setHoveredPhase(null)}
              className="flex flex-col items-center relative z-10 transition-all duration-200 active:scale-[0.97]"
              style={{ border: 'none', background: 'none', cursor: 'pointer', flex: 1 }}
            >
              <div
                className="transition-all duration-200"
                style={{
                  width: isHovered || isActive ? 14 : 10,
                  height: isHovered || isActive ? 14 : 10,
                  borderRadius: '50%',
                  backgroundColor: phaseComplete ? 'var(--accent-purple)' : phaseStarted ? 'rgba(108,92,231,0.4)' : 'var(--surface-card)',
                  border: `2px solid ${phaseComplete || phaseStarted ? 'var(--accent-purple)' : 'var(--divider-light)'}`,
                  marginBottom: 8,
                }}
              />
              <span
                className="transition-colors duration-150"
                style={{
                  fontFamily: "'Inter', sans-serif",
                  fontSize: 12,
                  fontWeight: isActive ? 400 : 300,
                  color: isActive || isHovered ? 'var(--text-primary)' : 'var(--text-muted)',
                  textAlign: 'center',
                  lineHeight: 1.3,
                }}
              >
                {phase.title}
              </span>
              <span className="font-caption mt-1" style={{ fontSize: 11 }}>{phase.weeks}</span>
            </button>
          );
        })}
      </div>

      {/* Expanded phase */}
      {expandedPhase && (() => {
        const phase = phases.find((p) => p.id === expandedPhase);
        if (!phase) return null;
        return (
          <div
            className="rounded-[14px] p-6"
            style={{ backgroundColor: 'var(--surface-card)', boxShadow: '0 2px 8px rgba(0,0,0,0.04)', animation: 'fade-in 0.3s ease-out' }}
          >
            <div className="flex items-center justify-between mb-4">
              <div>
                <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 15, fontWeight: 400, color: 'var(--text-primary)' }}>
                  {phase.title}
                </p>
                <p className="font-caption mt-1" style={{ fontSize: 12 }}>{phase.weeks}</p>
              </div>
              <span style={{ fontFamily: "'Inter', sans-serif", fontSize: 12, fontWeight: 400, color: 'var(--accent-purple)' }}>
                {phase.tasks.filter((t) => t.completed).length}/{phase.tasks.length} done
              </span>
            </div>
            <div className="flex flex-col gap-1">
              {phase.tasks.map((task) => (
                <button
                  key={task.id}
                  onClick={() => onToggleTask(phase.id, task.id)}
                  className="flex items-center gap-3 p-3 rounded-[8px] text-left transition-all duration-150 active:scale-[0.98] w-full"
                  style={{
                    border: 'none',
                    background: 'none',
                    cursor: 'pointer',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'rgba(108,92,231,0.03)')}
                  onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                >
                  <div
                    className="flex-shrink-0 rounded-[4px] flex items-center justify-center transition-all duration-200"
                    style={{
                      width: 20,
                      height: 20,
                      border: task.completed ? 'none' : '1.5px solid var(--divider-section)',
                      backgroundColor: task.completed ? 'var(--accent-purple)' : 'transparent',
                      color: '#fff',
                      fontSize: 11,
                    }}
                  >
                    {task.completed && '✓'}
                  </div>
                  <span
                    className="transition-all duration-150"
                    style={{
                      fontFamily: "'Inter', sans-serif",
                      fontSize: 13,
                      fontWeight: 300,
                      color: task.completed ? 'var(--text-muted)' : 'var(--text-secondary)',
                      textDecoration: task.completed ? 'line-through' : 'none',
                    }}
                  >
                    {task.label}
                  </span>
                </button>
              ))}
            </div>
          </div>
        );
      })()}
    </div>
  );
}

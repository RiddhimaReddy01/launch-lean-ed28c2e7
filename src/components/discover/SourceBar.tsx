import type { Source } from '@/data/discover-mock';

interface SourceBarProps {
  sources: Source[];
  selectedSourceId: string | null;
  onSelectSource: (id: string | null) => void;
}

export default function SourceBar({ sources, selectedSourceId, onSelectSource }: SourceBarProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {sources.map((source) => {
        const isSelected = selectedSourceId === source.id;
        return (
          <button
            key={source.id}
            onClick={() => onSelectSource(isSelected ? null : source.id)}
            className="group flex items-center gap-2 rounded-[10px] px-3 py-2 transition-all duration-200"
            style={{
              backgroundColor: isSelected ? 'rgba(108,92,231,0.07)' : 'var(--surface-card)',
              boxShadow: isSelected
                ? '0 0 0 1px rgba(108,92,231,0.2)'
                : '0 1px 3px rgba(0,0,0,0.04)',
            }}
          >
            <span
              className="font-caption transition-colors duration-200"
              style={{
                color: isSelected ? 'var(--accent-purple)' : 'var(--text-primary)',
                fontWeight: 400,
                fontSize: 13,
              }}
            >
              {source.name}
            </span>
            <span
              className="font-caption"
              style={{
                fontSize: 12,
                color: isSelected ? 'var(--accent-purple)' : 'var(--text-muted)',
              }}
            >
              {source.postCount}
            </span>
          </button>
        );
      })}
    </div>
  );
}

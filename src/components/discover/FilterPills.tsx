import { FILTER_CATEGORIES } from '@/data/discover-mock';

interface FilterPillsProps {
  selected: string;
  onSelect: (key: string) => void;
}

export default function FilterPills({ selected, onSelect }: FilterPillsProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {FILTER_CATEGORIES.map((cat) => {
        const isActive = selected === cat.key;
        return (
          <button
            key={cat.key}
            onClick={() => onSelect(cat.key)}
            className="rounded-full px-4 py-1.5 transition-all duration-200"
            style={{
              fontSize: 13,
              fontFamily: "'Inter', sans-serif",
              fontWeight: isActive ? 400 : 300,
              backgroundColor: isActive ? 'var(--accent-purple)' : 'var(--surface-input)',
              color: isActive ? '#FFFFFF' : 'var(--text-secondary)',
            }}
          >
            {cat.label}
          </button>
        );
      })}
    </div>
  );
}

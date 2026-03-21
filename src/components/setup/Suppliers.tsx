import { useState } from 'react';
import { MOCK_SUPPLIERS } from '@/data/setup-mock';

export default function Suppliers() {
  const [expanded, setExpanded] = useState(false);
  const [expandedCats, setExpandedCats] = useState<Set<string>>(new Set());
  const [bookmarked, setBookmarked] = useState<Set<string>>(new Set());
  const [hoveredCard, setHoveredCard] = useState<string | null>(null);

  const categories = Object.keys(MOCK_SUPPLIERS);

  const toggleCat = (cat: string) => {
    setExpandedCats((prev) => {
      const next = new Set(prev);
      next.has(cat) ? next.delete(cat) : next.add(cat);
      return next;
    });
  };

  const toggleBookmark = (name: string) => {
    setBookmarked((prev) => {
      const next = new Set(prev);
      next.has(name) ? next.delete(name) : next.add(name);
      return next;
    });
  };

  return (
    <div>
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full text-left flex items-center justify-between rounded-[12px] p-5 transition-all duration-200 active:scale-[0.995]"
        style={{
          backgroundColor: 'var(--surface-card)',
          boxShadow: expanded ? '0 2px 8px rgba(0,0,0,0.05)' : '0 1px 3px rgba(0,0,0,0.04)',
          border: 'none',
          cursor: 'pointer',
        }}
      >
        <div>
          <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 15, fontWeight: 400, color: 'var(--text-primary)' }}>
            Local suppliers & partners
          </p>
          <p className="font-caption mt-1" style={{ fontSize: 12 }}>
            {categories.length} categories · {Object.values(MOCK_SUPPLIERS).flat().length} suppliers found
          </p>
        </div>
        <span className="transition-transform duration-200" style={{ fontSize: 14, color: 'var(--text-muted)', transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)', display: 'inline-block' }}>↓</span>
      </button>

      <div style={{ maxHeight: expanded ? 2000 : 0, overflow: 'hidden', transition: 'max-height 400ms ease-out' }}>
        <div className="mt-4 flex flex-col gap-2">
          {categories.map((cat) => {
            const isOpen = expandedCats.has(cat);
            const suppliers = MOCK_SUPPLIERS[cat];
            return (
              <div key={cat} className="rounded-[12px]" style={{ backgroundColor: 'var(--surface-card)', boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}>
                <button
                  onClick={() => toggleCat(cat)}
                  className="w-full text-left p-4 flex items-center justify-between active:scale-[0.995] transition-transform duration-150"
                  style={{ border: 'none', background: 'none', cursor: 'pointer' }}
                >
                  <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 400, color: 'var(--text-primary)' }}>
                    {cat}
                  </p>
                  <div className="flex items-center gap-2">
                    <span className="font-caption" style={{ fontSize: 12 }}>{suppliers.length}</span>
                    <span className="transition-transform duration-200" style={{ fontSize: 13, color: 'var(--text-muted)', transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)', display: 'inline-block' }}>↓</span>
                  </div>
                </button>

                <div style={{ maxHeight: isOpen ? 800 : 0, overflow: 'hidden', transition: 'max-height 300ms ease-out' }}>
                  <div className="px-4 pb-4 flex flex-col gap-3">
                    <div style={{ height: 1, backgroundColor: 'var(--divider)' }} />
                    {suppliers.map((s) => {
                      const isHovered = hoveredCard === s.name;
                      const isSaved = bookmarked.has(s.name);
                      return (
                        <div
                          key={s.name}
                          className="rounded-[10px] p-4 transition-all duration-200"
                          style={{
                            backgroundColor: isHovered ? 'rgba(108,92,231,0.03)' : 'var(--surface-input)',
                            transform: isHovered ? 'translateY(-1px)' : 'translateY(0)',
                          }}
                          onMouseEnter={() => setHoveredCard(s.name)}
                          onMouseLeave={() => setHoveredCard(null)}
                        >
                          <div className="flex items-start justify-between gap-3">
                            <div className="flex-1 min-w-0">
                              <p className="transition-colors duration-150" style={{ fontFamily: "'Inter', sans-serif", fontSize: 14, fontWeight: 400, color: isHovered ? 'var(--accent-purple)' : 'var(--text-primary)', marginBottom: 2 }}>
                                {s.name}
                              </p>
                              <p className="font-caption" style={{ fontSize: 12, marginBottom: 6 }}>
                                {s.type} · {s.distance}
                              </p>
                              <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, fontWeight: 300, color: 'var(--text-secondary)', lineHeight: 1.55 }}>
                                {s.description}
                              </p>
                            </div>
                            <button
                              onClick={(e) => { e.stopPropagation(); toggleBookmark(s.name); }}
                              className="flex-shrink-0 transition-all duration-200 active:scale-[0.9]"
                              style={{
                                width: 28,
                                height: 28,
                                borderRadius: 8,
                                border: 'none',
                                backgroundColor: isSaved ? 'rgba(108,92,231,0.12)' : 'transparent',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontSize: 14,
                              }}
                              title={isSaved ? 'Remove bookmark' : 'Bookmark supplier'}
                            >
                              {isSaved ? '★' : '☆'}
                            </button>
                          </div>
                          <div className="mt-3">
                            <a
                              href={s.url}
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
                              Visit website →
                            </a>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

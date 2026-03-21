import { useState, useRef, useEffect } from 'react';
import { MOCK_SOURCES, MOCK_INSIGHTS, MOCK_SUMMARY } from '@/data/discover-mock';
import type { Insight } from '@/data/discover-mock';
import SourceBar from './SourceBar';
import FilterPills from './FilterPills';
import InsightCard from './InsightCard';
import MentionsPanel from './MentionsPanel';

export default function DiscoverModule() {
  const [selectedSource, setSelectedSource] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [mentionsInsight, setMentionsInsight] = useState<Insight | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = containerRef.current;
    if (el) requestAnimationFrame(() => el.classList.add('visible'));
  }, []);

  const filtered = MOCK_INSIGHTS.filter((insight) => {
    if (selectedCategory !== 'all' && insight.type !== selectedCategory) return false;
    if (selectedSource && !insight.sourceIds.includes(selectedSource)) return false;
    return true;
  });

  return (
    <>
      <div
        ref={containerRef}
        className="scroll-reveal"
        style={{ maxWidth: 700, margin: '0 auto', padding: '0 24px' }}
      >
        {/* Section 1 — Status */}
        <div className="text-center mb-12">
          <p
            className="font-heading"
            style={{ fontSize: 26 }}
          >
            Community signals
          </p>
          <p
            className="font-caption mt-3"
            style={{ fontSize: 13 }}
          >
            We scanned {MOCK_SUMMARY.totalSources} sources and analyzed {MOCK_SUMMARY.totalSignals} community signals
          </p>
        </div>

        {/* Section 2 — Source bar */}
        <div className="mb-6">
          <p
            className="font-caption mb-3"
            style={{ fontSize: 12, letterSpacing: '0.04em' }}
          >
            SOURCES
          </p>
          <SourceBar
            sources={MOCK_SOURCES}
            selectedSourceId={selectedSource}
            onSelectSource={setSelectedSource}
          />
        </div>

        {/* Section 3 — Filter pills */}
        <div className="mb-10">
          <FilterPills selected={selectedCategory} onSelect={setSelectedCategory} />
        </div>

        {/* Section 4 — Insight list */}
        <div className="flex flex-col gap-3">
          {filtered.map((insight, i) => (
            <div
              key={insight.id}
              className="scroll-reveal"
              style={{ animationDelay: `${i * 80}ms` }}
              ref={(el) => {
                if (el) setTimeout(() => el.classList.add('visible'), 100 + i * 80);
              }}
            >
              <InsightCard
                insight={insight}
                sources={MOCK_SOURCES}
                onSeeMentions={setMentionsInsight}
              />
            </div>
          ))}

          {filtered.length === 0 && (
            <div className="text-center py-16">
              <p className="font-caption" style={{ fontSize: 13 }}>
                No insights match this filter combination
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Section 5 — Mentions side panel */}
      {mentionsInsight && (
        <MentionsPanel
          insight={mentionsInsight}
          onClose={() => setMentionsInsight(null)}
        />
      )}
    </>
  );
}

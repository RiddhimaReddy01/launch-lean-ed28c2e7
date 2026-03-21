import { useMemo, useState, useRef, useEffect } from 'react';
import type { Insight } from '@/test/__mocks__/discover';
import SourceBar from './SourceBar';
import FilterPills from './FilterPills';
import InsightCard from './InsightCard';
import MentionsPanel from './MentionsPanel';
import { useResearchCore } from '@/hooks/use-research';
import { mapDiscoverInsights, mapDiscoverSources, summarizeDiscover } from '@/lib/transform';
import { useToast } from '@/hooks/use-toast';
import EmptyState from '../common/EmptyState';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorBoundary from '../common/ErrorBoundary';

export default function DiscoverModule() {
  const [selectedSource, setSelectedSource] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [mentionsInsight, setMentionsInsight] = useState<Insight | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();
  const { discoverQuery, decomposeQuery, idea } = useResearchCore();

  useEffect(() => {
    const el = containerRef.current;
    if (el) requestAnimationFrame(() => el.classList.add('visible'));
  }, []);

  useEffect(() => {
    if (discoverQuery.error) {
      toast({
        title: 'Could not load insights',
        description: discoverQuery.error instanceof Error ? discoverQuery.error.message : 'Unknown error',
        variant: 'destructive',
      });
    }
  }, [discoverQuery.error, toast]);

  const sources = useMemo(() => {
    if (discoverQuery.data) return mapDiscoverSources(discoverQuery.data.sources);
    return [];
  }, [discoverQuery.data]);

  const insights = useMemo(() => {
    if (discoverQuery.data) return mapDiscoverInsights(discoverQuery.data.insights, sources);
    return [];
  }, [discoverQuery.data, sources]);

  const summary = useMemo(() => {
    if (discoverQuery.data) return summarizeDiscover(insights, sources);
    return { totalSources: 0, totalSignals: 0 };
  }, [discoverQuery.data, insights, sources]);

  const filtered = insights.filter((insight) => {
    if (selectedCategory !== 'all' && insight.type !== selectedCategory) return false;
    if (selectedSource && !insight.sourceIds.includes(selectedSource)) return false;
    return true;
  });

  return (
    <ErrorBoundary>
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
              We scanned {summary.totalSources} sources and analyzed {summary.totalSignals} community signals
            </p>
          </div>

          {/* Loading state */}
          {discoverQuery.isPending && (
            <LoadingSpinner message="Discovering market insights..." />
          )}

          {/* Error state */}
          {discoverQuery.isError && (
            <EmptyState
              title="Insights unavailable"
              message={
                discoverQuery.error instanceof Error
                  ? discoverQuery.error.message
                  : 'Failed to fetch insights. Please try again.'
              }
            />
          )}

          {/* Success state */}
          {discoverQuery.isSuccess && (
            <>
              {/* Section 2 — Source bar */}
              <div className="mb-6">
                <p
                  className="font-caption mb-3"
                  style={{ fontSize: 12, letterSpacing: '0.04em' }}
                >
                  SOURCES
                </p>
                <SourceBar
                  sources={sources}
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
                      sources={sources}
                      onSeeMentions={setMentionsInsight}
                    />
                  </div>
                ))}

                {filtered.length === 0 && (
                  <EmptyState
                    title={idea ? 'No insights yet' : 'Enter an idea to start'}
                    message={
                      idea
                        ? 'The API returned no insights for this idea. Try re-running or adjusting the query.'
                        : 'Type a business idea and we will fetch fresh signals.'
                    }
                  />
                )}
              </div>
            </>
          )}
        </div>

        {/* Section 5 — Mentions side panel */}
        {mentionsInsight && (
          <MentionsPanel
            insight={mentionsInsight}
            onClose={() => setMentionsInsight(null)}
          />
        )}
      </>
    </ErrorBoundary>
  );
}

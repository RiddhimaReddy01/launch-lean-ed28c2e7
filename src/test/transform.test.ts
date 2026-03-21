import { describe, expect, it } from 'vitest';
import { mapDiscoverInsights, summarizeDiscover, mapOpportunity, mapSetupTiers, mapValidateCommunities } from '@/lib/transform';
import type { DiscoverInsight, DiscoverSource, AnalyzeResponse, SetupResponse, ValidateResponse } from '@/types/api';

const sampleSources: DiscoverSource[] = [
  { name: 'Reddit', type: 'reddit', post_count: 10 },
];

const sampleInsights: DiscoverInsight[] = [
  {
    id: 'ins_1',
    type: 'pain_point',
    title: 'Sample pain',
    score: 0.9,
    frequency_score: 3,
    intensity_score: 4,
    willingness_to_pay_score: 5,
    mention_count: 12,
    evidence: [{ quote: 'hi', source: 'Reddit', score: 1 }],
    source_platforms: ['Reddit'],
    audience_estimate: 'People',
  },
];

describe('transform helpers', () => {
  it('maps discover insights and carries raw payload', () => {
    const mapped = mapDiscoverInsights(sampleInsights, [{ id: 'reddit', name: 'Reddit', type: 'reddit', postCount: 10, url: '#', active: false }]);
    expect(mapped[0].raw).toBeDefined();
    expect(mapped[0].sourceIds.length).toBeGreaterThan(0);
  });

  it('summarizes discover signals', () => {
    const mapped = mapDiscoverInsights(sampleInsights, sampleSources.map((s) => ({ id: s.type, name: s.name, type: s.type, postCount: s.post_count, url: '#', active: false })));
    const summary = summarizeDiscover(mapped, mapped.map((m) => ({ id: m.id, name: m.id, type: 'reddit', postCount: 1, url: '#', active: false })));
    expect(summary.totalSources).toBeGreaterThan(0);
  });

  it('maps opportunity sizing into market sizes', () => {
    const resp: AnalyzeResponse = {
      section: 'opportunity',
      data: {
        tam: { value: 1000000, formatted: '$1,000,000', methodology: 'test' },
        sam: { value: 100000, formatted: '$100,000', methodology: 'test' },
        som: { value: 10000, formatted: '$10,000', methodology: 'test' },
      },
    };
    const sizes = mapOpportunity(resp)!;
    expect(sizes[0].value).toContain('$1,000,000');
  });

  it('maps setup tiers into UI tiers/costs', () => {
    const resp: SetupResponse = {
      cost_tiers: [
        { tier: 'minimum', total_range: { min: 1000, max: 2000 }, notes: '', line_items: [] },
        { tier: 'recommended', total_range: { min: 2000, max: 4000 }, notes: '', line_items: [{ category: 'rent', name: 'Rent', min_cost: 500, max_cost: 800 }] },
        { tier: 'full', total_range: { min: 4000, max: 8000 }, notes: '', line_items: [] },
      ],
      suppliers: [],
      team: [],
      timeline: [],
    };
    const mapped = mapSetupTiers(resp);
    expect(mapped?.tiers.length).toBe(3);
    expect(mapped?.costs.recommended[0].items[0].label).toBe('Rent');
  });

  it('maps validate communities', () => {
    const resp: ValidateResponse = {
      communities: [
        { name: 'Test Group', platform: 'yelp', member_count: '1k', rationale: 'good fit', link: 'https://example.com' },
      ],
    };
    const mapped = mapValidateCommunities(resp);
    expect(mapped?.[0].url).toContain('example.com');
  });
});

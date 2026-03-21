import type { DiscoverResponse, DiscoverInsight, DiscoverSource, AnalyzeResponse, SetupResponse, ValidateResponse } from '@/types/api';
import type { Insight, Source } from '@/test/__mocks__/discover';
import type {
  MarketSize, DemandBehaviorData, CustomerSegment,
  Competitor, MarketStructureData, RootCause, StrategicSnapshotData, StartupCosts,
} from '@/test/__mocks__/analyze';
import type { LaunchTier, CostCategory, Supplier as UiSupplier, TeamRole as UiTeamRole, TimelinePhase as UiTimelinePhase } from '@/test/__mocks__/setup';

const slug = (val: string) => val.toLowerCase().replace(/[^a-z0-9]+/g, '-');

function mapType(t: string): Insight['type'] {
  const normalized = t.replace(/\s+/g, '_').toLowerCase();
  if (normalized.includes('gap')) return 'gap';
  if (normalized.includes('want')) return 'want';
  if (normalized.includes('trend')) return 'want';
  return 'pain';
}

export function mapDiscoverSources(sources: DiscoverSource[]): Source[] {
  return sources.map((s) => ({
    id: slug(s.name || s.type),
    name: s.name || s.type,
    type: s.type,
    postCount: s.post_count,
    url: '#',
    active: false,
  }));
}

export function mapDiscoverInsights(insights: DiscoverInsight[], sources: Source[]): Insight[] {
  return insights.map((ins) => {
    const sourceIds = sources.map((s) => s.id);
    return {
      id: ins.id,
      type: mapType(ins.type),
      title: ins.title,
      score: Math.round((ins.score || 0) * 10),
      frequency: Math.round(ins.frequency_score || 0),
      intensity: Math.round(ins.intensity_score || 0),
      monetization: Math.round(ins.willingness_to_pay_score || 0),
      mentionCount: ins.mention_count || 0,
      sourceIds,
      sourcePlatforms: ins.source_platforms || [],
      audienceEstimate: ins.audience_estimate || '',
      evidence: (ins.evidence || []).map((ev, idx) => ({
        quote: ev.quote,
        sourceId: sourceIds[idx] || sourceIds[0] || 'source',
        sourceName: ev.source || 'Source',
        upvotes: typeof ev.upvotes === 'number' ? ev.upvotes : null,
        date: ev.date || '',
        url: '#',
      })),
      raw: ins,
    };
  });
}

export function summarizeDiscover(insights: Insight[], sources: Source[]) {
  const totalSignals = insights.reduce((sum, i) => sum + (i.mentionCount || 0), 0) || insights.length;
  return { totalSources: sources.length, totalSignals };
}

// â€”â€” Analyze mappings â€”â€” //
export function mapOpportunity(raw: AnalyzeResponse | undefined): MarketSize[] | undefined {
  if (!raw?.data) return undefined;
  const { tam, sam, som } = raw.data;
  const pick = (obj: any) => ({
    value: obj?.formatted || obj?.value?.toLocaleString?.() || 'N/A',
    rawValue: obj?.value || 0,
    methodology: obj?.methodology || '',
  });
  return [
    { acronym: 'TAM', label: 'Total Addressable Market', ...pick(tam) },
    { acronym: 'SAM', label: 'Serviceable Addressable Market', ...pick(sam) },
    { acronym: 'SOM', label: 'Serviceable Obtainable Market', ...pick(som) },
  ];
}

export function mapDemandBehavior(raw: AnalyzeResponse | undefined): DemandBehaviorData | undefined {
  if (!raw?.data) return undefined;
  const d = raw.data;
  return {
    demand: {
      painIntensity: d?.pain_intensity || 0,
      frequencyOfMentions: d?.frequency || d?.frequency_score || 0,
      willingnessToPay: d?.willingness_to_pay || 0,
    },
    usage: {
      frequencyOfUse: d?.usage_pattern || d?.frequency_of_use || 'N/A',
      retentionPotential: d?.retention || d?.retention_potential || 'N/A',
      revenueType: d?.revenue_type || 'N/A',
    },
    pricing: {
      typicalRange: d?.typical_range || d?.price_range || 'N/A',
      premiumCeiling: d?.premium_ceiling || 'N/A',
      priceSensitivity: d?.price_sensitivity || 'N/A',
    },
    friction: {
      trustBarrier: d?.trust_barrier || 'medium',
      switchingFriction: d?.switching_friction || 'medium',
      riskPerception: d?.risk_perception || 'medium',
    },
  };
}

export function mapSegments(raw: AnalyzeResponse | undefined): CustomerSegment[] | undefined {
  const segs = raw?.data?.segments;
  if (!Array.isArray(segs)) return undefined;
  return segs.map((s: any) => ({
    name: s.name,
    description: s.description,
    estimatedSize: s.estimated_size?.toString?.() || s.estimated_size || '',
    painIntensity: s.pain_intensity || 0,
    caresMostAbout: s.cares_most_about || s.primary_need ? [s.primary_need] : [],
  }));
}

export function mapCompetitors(raw: AnalyzeResponse | undefined): Competitor[] | undefined {
  const comps = raw?.data?.competitors;
  if (!Array.isArray(comps)) return undefined;
  return comps.map((c: any) => ({
    name: c.name,
    location: c.location || '',
    rating: c.rating || 0,
    priceRange: c.price_range || '',
    keyGap: c.key_gap || '',
    description: c.description || '',
    reviewExcerpts: c.review_excerpts || [],
    strengths: c.strengths || [],
    weaknesses: c.weaknesses || [],
    url: c.url,
  }));
}

export function mapMarketStructure(raw: AnalyzeResponse | undefined): MarketStructureData | undefined {
  const m = raw?.data;
  if (!m) return undefined;
  return {
    saturation: m.saturation || 'medium',
    fragmentation: m.fragmentation || '',
    differentiation: m.differentiation || 'medium',
    explanation: m.explanation || '',
  };
}

export function mapRootCauses(raw: AnalyzeResponse | undefined): RootCause[] | undefined {
  const causes = raw?.data?.root_causes;
  if (!Array.isArray(causes)) return undefined;
  return causes.map((c: any) => ({
    title: c.title,
    explanation: c.explanation,
    yourMove: c.your_move,
  }));
}

export function mapStrategic(raw: AnalyzeResponse | undefined): StrategicSnapshotData | undefined {
  const d = raw?.data;
  if (!d) return undefined;
  return {
    swot: d.swot || { strengths: [], weaknesses: [], opportunities: [], threats: [] },
    takeaways: d.takeaways || [],
    decision: d.decision || 'go',
    decisionReasoning: d.decision_reasoning || '',
  };
}

export function mapCostsPreview(raw: AnalyzeResponse | undefined): StartupCosts | undefined {
  const d = raw?.data;
  if (!d) return undefined;
  const total = d.total_range || {};
  return {
    minTotal: total.min ? `$${Math.round(total.min).toLocaleString()}` : '',
    maxTotal: total.max ? `$${Math.round(total.max).toLocaleString()}` : '',
    categories: (d.breakdown || []).map((b: any) => ({
      label: b.category,
      min: b.min ? `$${b.min.toLocaleString()}` : '',
      max: b.max ? `$${b.max.toLocaleString()}` : '',
    })),
  };
}

// â€”â€” Setup mappings â€”â€” //
export function mapSetupTiers(raw: SetupResponse | undefined): { tiers: LaunchTier[]; costs: Record<string, CostCategory[]> } | undefined {
  if (!raw) return undefined;
  const tiers: LaunchTier[] = raw.cost_tiers.map((t, idx) => ({
    id: (['minimum', 'recommended', 'full'] as LaunchTier['id'][])[idx] || 'recommended',
    title: t.tier?.replace(/_/g, ' ') || 'Tier',
    model: t.model || '',
    costRange: t.total_range ? `$${Math.round(t.total_range.min).toLocaleString()} – $${Math.round(t.total_range.max).toLocaleString()}` : '',
    costMin: t.total_range?.min || 0,
    costMax: t.total_range?.max || 0,
    whenToChoose: t.notes || 'Use when the economics fit your risk tolerance.',
  }));
  const costs: Record<string, CostCategory[]> = {};
  raw.cost_tiers.forEach((t, idx) => {
    const key = (['minimum', 'recommended', 'full'] as const)[idx] || 'recommended';
    costs[key] = (t.line_items || []).map((li: any) => ({
      label: li.category || li.name,
      items: [
        {
          label: li.name || li.category,
          low: li.min_cost || 0,
          mid: Math.round(((li.min_cost || 0) + (li.max_cost || 0)) / 2),
          high: li.max_cost || 0,
          explanation: li.notes || '',
        },
      ],
    }));
  });
  return { tiers, costs };
}

export function mapSetupSuppliers(raw: SetupResponse | undefined): Record<string, UiSupplier[]> | undefined {
  if (!raw) return undefined;
  const grouped: Record<string, UiSupplier[]> = {};
  for (const s of raw.suppliers) {
    const cat = s.category || 'Other';
    if (!grouped[cat]) grouped[cat] = [];
    grouped[cat].push({
      name: s.name,
      type: s.category,
      description: s.description,
      location: s.location,
      distance: '',
      url: s.website,
      category: s.category,
    });
  }
  return grouped;
}

export function mapSetupTeam(raw: SetupResponse | undefined): UiTeamRole[] | undefined {
  if (!raw) return undefined;
  return raw.team.map((r) => ({
    id: r.title.toLowerCase().replace(/\s+/g, '-'),
    title: r.title,
    type: r.type as UiTeamRole['type'],
    salaryRange: r.salary_range ? `$${r.salary_range.min?.toLocaleString?.() || 0} – $${r.salary_range.max?.toLocaleString?.() || 0}` : '',
    salaryLow: r.salary_range?.min || 0,
    salaryHigh: r.salary_range?.max || 0,
    description: r.description || '',
    linkedinSearch: '',
  }));
}

export function mapSetupTimeline(raw: SetupResponse | undefined): UiTimelinePhase[] | undefined {
  if (!raw) return undefined;
  return raw.timeline.map((p, idx) => ({
    id: p.phase?.toLowerCase().replace(/\s+/g, '-') || `phase-${idx}`,
    title: p.phase,
    weeks: p.weeks,
    tasks: (p.milestones || p.tasks || []).map((m: string, i: number) => ({
      id: `${idx}-${i}`,
      label: m,
      completed: false,
    })),
  }));
}

// â€”â€” Validate mappings â€”â€” //
export function mapValidateCommunities(raw: ValidateResponse | undefined) {
  return raw?.communities?.map((c) => ({
    id: c.name.toLowerCase().replace(/\s+/g, '-'),
    name: c.name,
    platform: c.platform,
    members: c.member_count || '',
    rationale: c.rationale,
    url: c.link,
    platformColor: '#6c5ce7',
  }));
}

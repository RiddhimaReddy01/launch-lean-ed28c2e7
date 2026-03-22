export interface Source {
  id: string;
  name: string;
  type: string;
  postCount: number;
  url: string;
  active: boolean;
}

export interface Evidence {
  quote: string;
  sourceId: string;
  sourceName: string;
  upvotes: number | null;
  date: string;
  url?: string;
}

export interface Insight {
  id: string;
  type: 'pain' | 'want' | 'gap';
  title: string;
  score: number;
  frequency: number;
  intensity: number;
  monetization: number;
  mentionCount: number;
  sourceIds: string[];
  sourcePlatforms: string[];
  audienceEstimate: string;
  evidence: Evidence[];
  raw?: unknown;
}

export interface MarketSize {
  label: string;
  acronym: string;
  value: string;
  rawValue: number;
  methodology: string;
}

export interface DemandSignals {
  painIntensity: number;
  frequencyOfMentions: number;
  willingnessToPay: number;
}

export interface UsagePattern {
  frequencyOfUse: string;
  retentionPotential: string;
  revenueType: string;
}

export interface PricingDynamics {
  typicalRange: string;
  premiumCeiling: string;
  priceSensitivity: string;
}

export interface AdoptionFriction {
  trustBarrier: 'low' | 'medium' | 'high';
  switchingFriction: 'low' | 'medium' | 'high';
  riskPerception: 'low' | 'medium' | 'high';
}

export interface DemandBehaviorData {
  demand: DemandSignals;
  usage: UsagePattern;
  pricing: PricingDynamics;
  friction: AdoptionFriction;
}

export interface CustomerSegment {
  name: string;
  description: string;
  estimatedSize: string;
  painIntensity: number;
  caresMostAbout: string[];
}

export interface Competitor {
  name: string;
  location: string;
  rating: number;
  priceRange: string;
  keyGap: string;
  description: string;
  reviewExcerpts: string[];
  strengths: string[];
  weaknesses: string[];
  url?: string;
}

export interface MarketStructureData {
  saturation: 'low' | 'medium' | 'high';
  fragmentation: string;
  differentiation: 'low' | 'medium' | 'high';
  explanation: string;
}

export interface RootCause {
  title: string;
  explanation: string;
  yourMove: string;
}

export interface SwotData {
  strengths: string[];
  weaknesses: string[];
  opportunities: string[];
  threats: string[];
}

export interface StrategicSnapshotData {
  swot: SwotData;
  takeaways: string[];
  decision: 'go' | 'pivot' | 'stop';
  decisionReasoning: string;
}

export interface CostRangeCategory {
  label: string;
  min: string;
  max: string;
}

export interface StartupCosts {
  minTotal: string;
  maxTotal: string;
  categories: CostRangeCategory[];
}

export interface LaunchTier {
  id: string;
  title: string;
  model: string;
  costRange: string;
  costMin: number;
  costMax: number;
  whenToChoose: string;
}

export interface CostLineItem {
  label: string;
  low: number;
  mid: number;
  high: number;
  explanation: string;
}

export interface SetupCostCategory {
  label: string;
  items: CostLineItem[];
}

export interface Supplier {
  name: string;
  type: string;
  description: string;
  location: string;
  distance: string;
  url: string;
  category: string;
}

export interface TeamRole {
  id: string;
  title: string;
  type: 'full-time' | 'part-time' | 'contract';
  salaryRange: string;
  salaryLow: number;
  salaryHigh: number;
  description: string;
  linkedinSearch: string;
}

export interface TimelineTask {
  id: string;
  label: string;
  completed: boolean;
}

export interface TimelinePhase {
  id: string;
  title: string;
  weeks: string;
  tasks: TimelineTask[];
}

export interface ValidationMethod {
  id: string;
  name: string;
  description: string;
  effort: 'low' | 'medium' | 'high';
  speed: 'fast' | 'medium' | 'slow';
}

export interface CommunityChannel {
  id: string;
  name: string;
  platform: string;
  platformColor: string;
  members: string;
  rationale: string;
  url: string;
}

export interface MetricTarget {
  id: string;
  label: string;
  target: number;
  targetLabel: string;
  unit: string;
  actual: number;
}

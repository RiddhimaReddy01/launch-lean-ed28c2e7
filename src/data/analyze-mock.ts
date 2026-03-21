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

export interface CostCategory {
  label: string;
  min: string;
  max: string;
}

export interface StartupCosts {
  minTotal: string;
  maxTotal: string;
  categories: CostCategory[];
}

export const MOCK_MARKET_SIZE: MarketSize[] = [
  {
    acronym: 'TAM',
    label: 'Total Addressable Market',
    value: '$2.4B',
    rawValue: 2400000000,
    methodology: 'US cold-pressed juice & smoothie market, IBIS World 2026 estimate.',
  },
  {
    acronym: 'SAM',
    label: 'Serviceable Addressable Market',
    value: '$86M',
    rawValue: 86000000,
    methodology: 'DFW metro health-focused beverage spend among target demographics.',
  },
  {
    acronym: 'SOM',
    label: 'Serviceable Obtainable Market',
    value: '$1.8M',
    rawValue: 1800000,
    methodology: 'Realistic year-one capture: single Plano location, 3-mile radius, 2.1% penetration.',
  },
];

export const MOCK_DEMAND_BEHAVIOR: DemandBehaviorData = {
  demand: {
    painIntensity: 8,
    frequencyOfMentions: 7,
    willingnessToPay: 7,
  },
  usage: {
    frequencyOfUse: '2–3× per week',
    retentionPotential: 'High — habitual purchase pattern',
    revenueType: 'Recurring (daily consumable)',
  },
  pricing: {
    typicalRange: '$8 – $14 per drink',
    premiumCeiling: '$18 for cold-pressed specialty',
    priceSensitivity: 'Moderate — quality justifies premium',
  },
  friction: {
    trustBarrier: 'medium',
    switchingFriction: 'low',
    riskPerception: 'low',
  },
};

export const MOCK_SEGMENTS: CustomerSegment[] = [
  {
    name: 'Post-workout crowd',
    description: 'Gym-goers and fitness enthusiasts who want clean fuel within 10 minutes of their workout. Price-tolerant if quality is visible.',
    estimatedSize: '~14,200 in 3-mile radius',
    painIntensity: 8,
    caresMostAbout: ['Protein content transparency', 'Speed of service', 'No artificial sweeteners'],
  },
  {
    name: 'Health-conscious parents',
    description: 'Families seeking alternatives to sugary drinks for kids. Often discovered through school events and local Facebook groups.',
    estimatedSize: '~9,800 households',
    painIntensity: 6,
    caresMostAbout: ['Kid-friendly options', 'Organic ingredients', 'Convenient location near schools'],
  },
  {
    name: 'Remote workers & freelancers',
    description: 'Work-from-home professionals looking for a "third place" that isn\'t Starbucks. Value ambiance and Wi-Fi as much as the menu.',
    estimatedSize: '~7,400 in West Plano',
    painIntensity: 5,
    caresMostAbout: ['Seating and atmosphere', 'Consistent quality', 'Loyalty rewards'],
  },
  {
    name: 'Corporate wellness buyers',
    description: 'Office managers and HR teams ordering catering for team events. High-volume, recurring revenue potential.',
    estimatedSize: '~320 offices in Legacy corridor',
    painIntensity: 7,
    caresMostAbout: ['Bulk ordering ease', 'Delivery reliability', 'Dietary accommodation'],
  },
];

export const MOCK_COMPETITORS: Competitor[] = [
  {
    name: 'Smoothie King',
    location: '3 locations within 5 mi',
    rating: 3.8,
    priceRange: '$$',
    keyGap: 'Perceived as "fast food smoothies" — artificial taste complaints',
    description: 'National chain with heavy franchise presence in DFW. Strong brand recognition but declining trust among health-focused consumers.',
    reviewExcerpts: [
      '"Tastes like a milkshake with protein powder dumped in."',
      '"Used to go weekly but switched to making my own — can\'t trust the sugar content."',
    ],
    strengths: ['Brand recognition', 'Drive-through convenience', 'Loyalty app'],
    weaknesses: ['Artificial ingredient perception', 'No local sourcing story', 'Generic menu across all locations'],
    url: 'https://www.smoothieking.com/',
  },
  {
    name: 'Juiceland',
    location: 'Nearest in Dallas (12 mi)',
    rating: 4.4,
    priceRange: '$$$',
    keyGap: 'No Plano presence — fans have to drive 25+ minutes',
    description: 'Austin-based craft juice chain beloved for quality. Slow DFW expansion leaves a loyalty vacuum in the suburbs.',
    reviewExcerpts: [
      '"Best juice in Texas but I wish they\'d open in Plano already."',
      '"Worth the drive from Frisco but I can only go on weekends."',
    ],
    strengths: ['Cult following', 'Transparent sourcing', 'Unique flavor combinations'],
    weaknesses: ['No suburban DFW locations', 'Higher price point', 'Long wait times'],
    url: 'https://www.juiceland.com/',
  },
  {
    name: 'Nekter Juice Bar',
    location: '1 location in Frisco',
    rating: 4.1,
    priceRange: '$$',
    keyGap: 'Formulaic menu — customers describe it as "fine but forgettable"',
    description: 'California import with a clean aesthetic. Functional but lacks the soul and community feel that drives word-of-mouth.',
    reviewExcerpts: [
      '"It\'s fine. Nothing special. I go because there\'s nothing better nearby."',
      '"Clean looking store but the juice tastes like every other chain."',
    ],
    strengths: ['Clean brand aesthetic', 'Reasonable pricing', 'Consistent experience'],
    weaknesses: ['No local identity', 'Limited customization', 'Weak community engagement'],
    url: 'https://www.nekterjuicebar.com/',
  },
];

export const MOCK_MARKET_STRUCTURE: MarketStructureData = {
  saturation: 'medium',
  fragmentation: 'Highly fragmented — many independent providers, few dominant brands in suburbs',
  differentiation: 'low',
  explanation: 'The Plano health beverage market is moderately saturated with national chains but highly fragmented among independents. Brand trust is low across the board — consumers default to chains out of convenience, not loyalty. This creates a clear opening for a reliability-focused, locally-rooted entrant that can build genuine community trust.',
};

export const MOCK_ROOT_CAUSES: RootCause[] = [
  {
    title: 'Franchise economics prevent quality differentiation',
    explanation: 'National chains optimize for unit economics and supply chain consistency, not local sourcing or ingredient quality. Their margins depend on standardized products that taste the same in Phoenix and Plano. This structurally prevents them from offering what health-conscious consumers increasingly want: transparency and locality.',
    yourMove: 'Lead with radical ingredient transparency — name the farm, show the receipt, publish your margins. This is something no franchise can replicate.',
  },
  {
    title: 'Craft juice brands are urban-first by design',
    explanation: 'Companies like Juiceland expand from dense urban cores outward. Suburban markets are last on their roadmap because foot traffic density is lower. Plano\'s car-centric layout makes it a poor fit for their walk-in model — which is exactly why the gap persists.',
    yourMove: 'Design for the suburban customer: parking-friendly location, mobile ordering for pickup, and catering to office parks. Beat urban brands by being native to suburban behavior.',
  },
  {
    title: 'Strip-center lease structures favor incumbents',
    explanation: 'Commercial real estate in Plano\'s prime corridors (Legacy, Preston) is dominated by long-term leases held by national tenants. New entrants face 18-24 month waitlists for preferred locations. But food halls and mixed-use developments have created new inventory that incumbents haven\'t claimed.',
    yourMove: 'Target Legacy West food hall or the new Boardwalk at Granite Park. These spaces offer lower upfront commitment and built-in foot traffic from adjacent tenants.',
  },
];

export const MOCK_STRATEGIC_SNAPSHOT: StrategicSnapshotData = {
  swot: {
    strengths: [
      'Strong unmet demand signals (8/10 pain intensity)',
      'Recurring purchase pattern drives retention',
      'Low switching friction from existing options',
    ],
    weaknesses: [
      'Medium trust barrier for new food brands',
      'Higher startup costs vs. digital businesses',
      'Dependent on physical location quality',
    ],
    opportunities: [
      'No craft juice presence in Plano suburbs',
      'Food hall inventory opening in Legacy corridor',
      'Corporate wellness catering is underserved',
    ],
    threats: [
      'Juiceland may expand to DFW suburbs within 2 years',
      'Economic downturn could compress premium spending',
      'Health trend fatigue among mainstream consumers',
    ],
  },
  takeaways: [
    'Trust is the main differentiator, not price — lead with transparency',
    'Recurring demand makes customer retention the critical metric',
    'Fragmented competition leaves room for brand-building before consolidation',
    'Suburban-native design (parking, mobile order, catering) is the structural advantage',
  ],
  decision: 'go',
  decisionReasoning: 'Strong demand signals, fragmented competition with no dominant local player, and available commercial inventory create a favorable entry window. The key risk — trust barrier — is addressable through transparency and community engagement.',
};

export const MOCK_COSTS: StartupCosts = {
  minTotal: '$47,000',
  maxTotal: '$95,000',
  categories: [
    { label: 'Real estate (first + last + buildout)', min: '$18,000', max: '$42,000' },
    { label: 'Equipment & supplies', min: '$14,000', max: '$26,000' },
    { label: 'Permits, licensing & legal', min: '$3,000', max: '$5,000' },
    { label: 'Operating runway (3 months)', min: '$12,000', max: '$22,000' },
  ],
};

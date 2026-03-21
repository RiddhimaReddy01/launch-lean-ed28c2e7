export interface LaunchTier {
  id: 'minimum' | 'recommended' | 'full';
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

export interface CostCategory {
  label: string;
  items: CostLineItem[];
}

export interface TierCostData {
  tierId: string;
  categories: CostCategory[];
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

export const MOCK_TIERS: LaunchTier[] = [
  {
    id: 'minimum',
    title: 'Minimum viable',
    model: 'Food hall kiosk or pop-up',
    costRange: '$47K – $68K',
    costMin: 47000,
    costMax: 68000,
    whenToChoose: 'You want to test the concept with minimal risk before committing to a permanent location.',
  },
  {
    id: 'recommended',
    title: 'Recommended',
    model: '400–600 sq ft standalone',
    costRange: '$85K – $120K',
    costMin: 85000,
    costMax: 120000,
    whenToChoose: 'You have conviction in the opportunity and want a proper brand presence from day one.',
  },
  {
    id: 'full',
    title: 'Full build-out',
    model: '800+ sq ft flagship with seating',
    costRange: '$140K – $195K',
    costMin: 140000,
    costMax: 195000,
    whenToChoose: 'You want to build a destination brand with dine-in experience and catering capacity.',
  },
];

export const MOCK_TIER_COSTS: Record<string, CostCategory[]> = {
  minimum: [
    {
      label: 'Real estate',
      items: [
        { label: 'Food hall vendor slot (deposit + first month)', low: 4000, mid: 6000, high: 8000, explanation: 'Legacy West food hall slots range $3K–$8K/mo. Deposit typically equals one month.' },
        { label: 'Basic buildout & signage', low: 3000, mid: 5000, high: 7000, explanation: 'Counter setup, menu boards, basic branding. Food halls often provide shell infrastructure.' },
      ],
    },
    {
      label: 'Equipment',
      items: [
        { label: 'Commercial blenders (×2)', low: 1800, mid: 2400, high: 3200, explanation: 'Vitamix or BlendTec commercial units. Refurbished options available at 40% discount.' },
        { label: 'Cold-press juicer', low: 3000, mid: 4500, high: 6000, explanation: 'Goodnature M-1 or equivalent. The core production unit for cold-pressed offerings.' },
        { label: 'Refrigeration & storage', low: 2000, mid: 3000, high: 4000, explanation: 'Under-counter fridge units and ingredient storage. Compact options for kiosk format.' },
      ],
    },
    {
      label: 'Permits & legal',
      items: [
        { label: 'Food service permit', low: 800, mid: 1200, high: 1500, explanation: 'City of Plano food establishment permit. Processing takes 2–4 weeks.' },
        { label: 'Business registration & LLC', low: 500, mid: 800, high: 1200, explanation: 'Texas LLC filing ($300) plus registered agent and operating agreement.' },
        { label: 'Health department inspection', low: 200, mid: 400, high: 600, explanation: 'Initial inspection fee. Budget for potential re-inspection costs.' },
      ],
    },
    {
      label: 'Initial operations',
      items: [
        { label: 'Initial inventory & produce', low: 1500, mid: 2500, high: 3500, explanation: 'First two weeks of produce, supplements, and packaging materials.' },
        { label: 'POS system & payment processing', low: 500, mid: 800, high: 1200, explanation: 'Square or Toast setup. Includes hardware, software subscription, and merchant fees setup.' },
        { label: 'Branding & packaging', low: 1000, mid: 2000, high: 3000, explanation: 'Logo, menu design, cups, labels, bags. Sets the visual identity for launch.' },
      ],
    },
    {
      label: 'Operating runway (3 months)',
      items: [
        { label: 'Rent & utilities', low: 9000, mid: 12000, high: 15000, explanation: 'Three months of venue costs to cover the ramp-up period before breakeven.' },
        { label: 'Staff wages', low: 6000, mid: 9000, high: 12000, explanation: 'One full-time employee plus part-time help. Covers the initial operating period.' },
        { label: 'Marketing & launch', low: 2000, mid: 3000, high: 4000, explanation: 'Social media ads, influencer collaborations, grand opening event costs.' },
      ],
    },
  ],
  recommended: [
    {
      label: 'Real estate',
      items: [
        { label: 'Lease deposit + first/last month', low: 10000, mid: 15000, high: 20000, explanation: 'Standalone 400–600 sq ft space in Legacy or Preston corridor. $18–$28/sq ft NNN.' },
        { label: 'Buildout & interior design', low: 12000, mid: 18000, high: 25000, explanation: 'Full interior buildout including plumbing, electrical, counter, and brand-consistent design.' },
      ],
    },
    {
      label: 'Equipment',
      items: [
        { label: 'Commercial blenders (×3)', low: 3000, mid: 4200, high: 5400, explanation: 'Three Vitamix commercial units for peak-hour throughput.' },
        { label: 'Cold-press juicer (production grade)', low: 5000, mid: 7000, high: 9000, explanation: 'Goodnature M-1 or X-1. Higher throughput for both in-store and bottled products.' },
        { label: 'Full refrigeration suite', low: 4000, mid: 6000, high: 8000, explanation: 'Walk-in cooler or multiple reach-in units plus display fridge for grab-and-go.' },
        { label: 'Prep & dishwashing equipment', low: 2000, mid: 3000, high: 4500, explanation: 'Commercial sink, prep tables, cutting boards, and small dishwasher.' },
      ],
    },
    {
      label: 'Permits & legal',
      items: [
        { label: 'Food service permit + liquor (optional)', low: 1200, mid: 2000, high: 3000, explanation: 'Full food establishment permit. Optional beer/wine license adds $1K–$2K.' },
        { label: 'Business registration, LLC & insurance', low: 1500, mid: 2500, high: 3500, explanation: 'LLC, commercial liability insurance ($1M minimum), and workers comp setup.' },
        { label: 'Health & fire inspections', low: 500, mid: 800, high: 1200, explanation: 'Initial inspections plus ADA compliance review for standalone space.' },
      ],
    },
    {
      label: 'Initial operations',
      items: [
        { label: 'Initial inventory & produce', low: 3000, mid: 4500, high: 6000, explanation: 'Two weeks of premium produce, supplements, superfoods, and packaging.' },
        { label: 'POS, online ordering & delivery setup', low: 1000, mid: 2000, high: 3000, explanation: 'Full POS with online ordering integration, delivery platform setup, and loyalty system.' },
        { label: 'Branding, packaging & signage', low: 3000, mid: 5000, high: 7000, explanation: 'Professional brand identity, exterior signage, packaging design, and merchandise.' },
      ],
    },
    {
      label: 'Operating runway (3 months)',
      items: [
        { label: 'Rent & utilities', low: 15000, mid: 20000, high: 27000, explanation: 'Three months of lease payments plus water, electric, and waste management.' },
        { label: 'Staff wages (2–3 people)', low: 14000, mid: 18000, high: 24000, explanation: 'Manager plus 1–2 team members. Covers payroll taxes and benefits setup.' },
        { label: 'Marketing & community launch', low: 4000, mid: 6000, high: 8000, explanation: 'Pre-launch campaign, grand opening, local partnerships, and first 90 days of marketing.' },
      ],
    },
  ],
  full: [
    {
      label: 'Real estate',
      items: [
        { label: 'Lease deposit + first/last month', low: 18000, mid: 25000, high: 35000, explanation: 'Premium 800+ sq ft location with seating area. High-traffic corner or end-cap preferred.' },
        { label: 'Full architectural buildout', low: 25000, mid: 35000, high: 45000, explanation: 'Custom interior design, seating for 15–20, outdoor patio option, premium finishes.' },
      ],
    },
    {
      label: 'Equipment',
      items: [
        { label: 'Commercial blenders (×4)', low: 4000, mid: 5600, high: 7200, explanation: 'Four high-performance units including one dedicated to acai bowls and frozen blends.' },
        { label: 'Production-grade cold-press system', low: 8000, mid: 12000, high: 16000, explanation: 'Goodnature X-1 with bottling capability for wholesale and retail bottle sales.' },
        { label: 'Full kitchen equipment suite', low: 8000, mid: 12000, high: 16000, explanation: 'Walk-in cooler, display cases, prep stations, commercial dishwasher, and storage.' },
      ],
    },
    {
      label: 'Permits & legal',
      items: [
        { label: 'Full licensing package', low: 2500, mid: 4000, high: 5500, explanation: 'Food service, beer/wine, catering permit, and outdoor seating permit.' },
        { label: 'Business entity, insurance & compliance', low: 3000, mid: 4500, high: 6000, explanation: 'LLC, comprehensive insurance, trademark filing, and employment compliance.' },
      ],
    },
    {
      label: 'Initial operations',
      items: [
        { label: 'Premium inventory launch', low: 5000, mid: 7000, high: 9000, explanation: 'Full product line including bottled juice, smoothies, bowls, and health shots.' },
        { label: 'Full tech stack', low: 3000, mid: 5000, high: 7000, explanation: 'Enterprise POS, app-based ordering, delivery integration, CRM, and analytics.' },
        { label: 'Brand identity & launch campaign', low: 6000, mid: 9000, high: 12000, explanation: 'Full brand system, professional photography, influencer program, and PR launch.' },
      ],
    },
    {
      label: 'Operating runway (3 months)',
      items: [
        { label: 'Rent & utilities', low: 21000, mid: 28000, high: 36000, explanation: 'Three months for premium location with higher square footage and utility demands.' },
        { label: 'Staff wages (4–5 people)', low: 24000, mid: 30000, high: 38000, explanation: 'Manager, assistant manager, 2–3 team members. Full payroll and benefits.' },
        { label: 'Marketing & brand building', low: 8000, mid: 12000, high: 16000, explanation: 'Aggressive launch marketing, community events, partnerships, and ongoing content.' },
      ],
    },
  ],
};

export const MOCK_SUPPLIERS: Record<string, Supplier[]> = {
  Produce: [
    { name: 'Profound Foods', type: 'Organic produce farm', description: 'Family-owned organic farm specializing in leafy greens and seasonal produce.', location: 'Lucas, TX', distance: '18 mi', url: 'https://profoundfoods.com', category: 'Produce' },
    { name: 'Lemley Farms', type: 'Local fruit supplier', description: 'Third-generation farm growing berries, melons, and stone fruit for DFW restaurants.', location: 'Celina, TX', distance: '24 mi', url: 'https://www.facebook.com/lemleyfarms', category: 'Produce' },
  ],
  Equipment: [
    { name: 'Goodnature', type: 'Cold-press juicer manufacturer', description: 'Industry-leading commercial cold-press juice equipment with full support and training.', location: 'Buffalo, NY (ships nationwide)', distance: 'Ships to DFW', url: 'https://www.goodnature.com', category: 'Equipment' },
    { name: 'Restaurant Depot', type: 'Commercial kitchen supplier', description: 'Wholesale commercial kitchen equipment, smallwares, and supplies.', location: 'Dallas, TX', distance: '12 mi', url: 'https://www.restaurantdepot.com', category: 'Equipment' },
  ],
  Packaging: [
    { name: 'World Centric', type: 'Sustainable packaging', description: 'Compostable cups, lids, straws, and containers. B-Corp certified.', location: 'Rohnert Park, CA (ships nationwide)', distance: 'Ships to DFW', url: 'https://www.worldcentric.com', category: 'Packaging' },
    { name: 'Stalkmarket', type: 'Eco-friendly packaging', description: 'Plant-based foodservice packaging with custom printing options.', location: 'Portland, OR (ships nationwide)', distance: 'Ships to DFW', url: 'https://www.stalkmarketproducts.com', category: 'Packaging' },
  ],
  Services: [
    { name: 'SCORE Dallas', type: 'Free business mentoring', description: 'Volunteer mentors with food service and franchise experience. Free workshops monthly.', location: 'Dallas, TX', distance: '15 mi', url: 'https://www.score.org/dallas', category: 'Services' },
    { name: 'Brewed Creative', type: 'Brand & design agency', description: 'DFW-based agency specializing in food & beverage branding and packaging design.', location: 'Plano, TX', distance: '3 mi', url: 'https://brewedcreative.com', category: 'Services' },
  ],
};

export const MOCK_TEAM: TeamRole[] = [
  {
    id: 'manager',
    title: 'Store Manager',
    type: 'full-time',
    salaryRange: '$42K – $55K/yr',
    salaryLow: 42000,
    salaryHigh: 55000,
    description: 'Oversees daily operations, inventory management, and customer experience. Previous food service management experience required.',
    linkedinSearch: 'https://www.linkedin.com/search/results/people/?keywords=juice%20bar%20manager%20plano%20TX',
  },
  {
    id: 'barista',
    title: 'Lead Juice Barista',
    type: 'full-time',
    salaryRange: '$32K – $38K/yr',
    salaryLow: 32000,
    salaryHigh: 38000,
    description: 'Handles juice preparation, quality control, and trains new staff. Should have experience with commercial blending equipment.',
    linkedinSearch: 'https://www.linkedin.com/search/results/people/?keywords=barista%20plano%20TX',
  },
  {
    id: 'parttime',
    title: 'Part-time Team Member',
    type: 'part-time',
    salaryRange: '$14 – $17/hr',
    salaryLow: 14560,
    salaryHigh: 17680,
    description: 'Customer-facing role handling orders, prep, and cleaning. Ideal for students or flexible-schedule workers.',
    linkedinSearch: 'https://www.linkedin.com/search/results/people/?keywords=food%20service%20plano%20TX',
  },
  {
    id: 'marketing',
    title: 'Marketing & Social Media',
    type: 'contract',
    salaryRange: '$1.5K – $3K/mo',
    salaryLow: 18000,
    salaryHigh: 36000,
    description: 'Content creation, social media management, influencer partnerships, and community engagement. Can be freelance or agency.',
    linkedinSearch: 'https://www.linkedin.com/search/results/people/?keywords=social%20media%20manager%20DFW',
  },
];

export const MOCK_TIMELINE: TimelinePhase[] = [
  {
    id: 'validate',
    title: 'Validate demand',
    weeks: 'Weeks 1–2',
    tasks: [
      { id: 'v1', label: 'Finalize concept and brand positioning', completed: false },
      { id: 'v2', label: 'Launch landing page with waitlist', completed: false },
      { id: 'v3', label: 'Run targeted ads to test interest ($200 budget)', completed: false },
      { id: 'v4', label: 'Secure first 50 waitlist signups', completed: false },
    ],
  },
  {
    id: 'location',
    title: 'Secure location',
    weeks: 'Weeks 3–6',
    tasks: [
      { id: 'l1', label: 'Tour 3–5 potential locations', completed: false },
      { id: 'l2', label: 'Negotiate lease terms and sign LOI', completed: false },
      { id: 'l3', label: 'File permits and business registration', completed: false },
      { id: 'l4', label: 'Finalize supplier agreements', completed: false },
    ],
  },
  {
    id: 'buildout',
    title: 'Build out',
    weeks: 'Weeks 7–10',
    tasks: [
      { id: 'b1', label: 'Complete interior buildout and signage', completed: false },
      { id: 'b2', label: 'Install and test all equipment', completed: false },
      { id: 'b3', label: 'Hire and train initial team', completed: false },
      { id: 'b4', label: 'Finalize menu and pricing', completed: false },
    ],
  },
  {
    id: 'launch',
    title: 'Soft launch',
    weeks: 'Weeks 11–12',
    tasks: [
      { id: 's1', label: 'Friends & family soft opening', completed: false },
      { id: 's2', label: 'Collect feedback and iterate menu', completed: false },
      { id: 's3', label: 'Grand opening event with influencer invites', completed: false },
      { id: 's4', label: 'Activate social media and review generation', completed: false },
    ],
  },
];

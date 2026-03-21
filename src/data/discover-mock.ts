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
}

export const MOCK_SUMMARY = {
  totalSources: 6,
  totalSignals: 409,
};

export const MOCK_SOURCES: Source[] = [
  { id: 'reddit_plano', name: 'r/plano', type: 'reddit_local', postCount: 42, url: 'https://www.reddit.com/r/plano/', active: false },
  { id: 'reddit_dallas', name: 'r/Dallas', type: 'reddit_local', postCount: 87, url: 'https://www.reddit.com/r/Dallas/', active: false },
  { id: 'yelp', name: 'Yelp', type: 'reviews', postCount: 156, url: 'https://www.yelp.com/', active: false },
  { id: 'google_reviews', name: 'Google Reviews', type: 'reviews', postCount: 89, url: 'https://maps.google.com/', active: false },
  { id: 'craigslist_dfw', name: 'Craigslist DFW', type: 'listings', postCount: 12, url: 'https://dallas.craigslist.org/', active: false },
  { id: 'nextdoor_plano', name: 'Nextdoor Plano', type: 'community', postCount: 23, url: 'https://nextdoor.com/', active: false },
];

export const FILTER_CATEGORIES = [
  { key: 'all', label: 'All' },
  { key: 'pain', label: 'Pain Points' },
  { key: 'want', label: 'Unmet Wants' },
  { key: 'gap', label: 'Market Gaps' },
] as const;

export const MOCK_INSIGHTS: Insight[] = [
  {
    id: 'insight_001',
    type: 'pain',
    title: 'Existing juice bars are overpriced for basic smoothies',
    score: 93,
    frequency: 9,
    intensity: 8,
    monetization: 7,
    mentionCount: 38,
    sourceIds: ['reddit_plano', 'reddit_dallas', 'yelp', 'google_reviews'],
    sourcePlatforms: ['Reddit', 'Yelp', 'Google Reviews'],
    audienceEstimate: 'Health-conscious office workers and gym-goers in Plano',
    evidence: [
      {
        quote: 'I paid $14 for a smoothie that tasted watered down.',
        sourceId: 'reddit_plano',
        sourceName: 'r/plano',
        upvotes: 31,
        date: '2026-03-02',
        url: 'https://www.reddit.com/r/plano/',
      },
      {
        quote: 'Most places here charge premium prices but the ingredients feel cheap.',
        sourceId: 'yelp',
        sourceName: 'Yelp',
        upvotes: null,
        date: '2026-02-18',
        url: 'https://www.yelp.com/',
      },
      {
        quote: 'Spent $12 on a green juice that was mostly apple filler. Never again.',
        sourceId: 'google_reviews',
        sourceName: 'Google Reviews',
        upvotes: null,
        date: '2026-01-29',
        url: 'https://maps.google.com/',
      },
    ],
  },
  {
    id: 'insight_002',
    type: 'want',
    title: 'Demand for cold-pressed juice with transparent sourcing',
    score: 81,
    frequency: 7,
    intensity: 8,
    monetization: 8,
    mentionCount: 24,
    sourceIds: ['reddit_plano', 'nextdoor_plano', 'google_reviews'],
    sourcePlatforms: ['Reddit', 'Nextdoor', 'Google Reviews'],
    audienceEstimate: 'Higher-income wellness-oriented consumers in West Plano',
    evidence: [
      {
        quote: "I'd pay more if I knew where the produce came from.",
        sourceId: 'nextdoor_plano',
        sourceName: 'Nextdoor Plano',
        upvotes: null,
        date: '2026-03-01',
        url: 'https://nextdoor.com/',
      },
      {
        quote: "Cold-pressed is worth the markup if it's actually fresh and local.",
        sourceId: 'reddit_plano',
        sourceName: 'r/plano',
        upvotes: 18,
        date: '2026-02-14',
        url: 'https://www.reddit.com/r/plano/',
      },
    ],
  },
  {
    id: 'insight_003',
    type: 'gap',
    title: 'No local juice bar offers a subscription or loyalty program',
    score: 74,
    frequency: 5,
    intensity: 7,
    monetization: 9,
    mentionCount: 17,
    sourceIds: ['reddit_dallas', 'yelp', 'nextdoor_plano'],
    sourcePlatforms: ['Reddit', 'Yelp', 'Nextdoor'],
    audienceEstimate: 'Repeat-purchase consumers who buy juice 3+ times per week',
    evidence: [
      {
        quote: 'I go through 4-5 juices a week. Would love a punch card or subscription.',
        sourceId: 'reddit_dallas',
        sourceName: 'r/Dallas',
        upvotes: 22,
        date: '2026-02-22',
        url: 'https://www.reddit.com/r/Dallas/',
      },
      {
        quote: "None of the juice places around here reward regulars. It's all one-off transactions.",
        sourceId: 'yelp',
        sourceName: 'Yelp',
        upvotes: null,
        date: '2026-01-30',
        url: 'https://www.yelp.com/',
      },
    ],
  },
  {
    id: 'insight_004',
    type: 'want',
    title: 'Growing interest in adaptogen and functional add-ins',
    score: 68,
    frequency: 6,
    intensity: 6,
    monetization: 7,
    mentionCount: 14,
    sourceIds: ['reddit_plano', 'reddit_dallas', 'google_reviews'],
    sourcePlatforms: ['Reddit', 'Google Reviews'],
    audienceEstimate: 'Wellness-focused millennials and Gen Z in DFW',
    evidence: [
      {
        quote: 'I started adding ashwagandha to everything. Wish a local place offered functional shots.',
        sourceId: 'reddit_dallas',
        sourceName: 'r/Dallas',
        upvotes: 47,
        date: '2026-03-10',
        url: 'https://www.reddit.com/r/Dallas/',
      },
    ],
  },
  {
    id: 'insight_005',
    type: 'pain',
    title: 'Long wait times during morning and lunch rush',
    score: 62,
    frequency: 7,
    intensity: 6,
    monetization: 4,
    mentionCount: 21,
    sourceIds: ['yelp', 'google_reviews', 'craigslist_dfw'],
    sourcePlatforms: ['Yelp', 'Google Reviews'],
    audienceEstimate: 'Office workers near Legacy West and Shops at Legacy',
    evidence: [
      {
        quote: "Waited 20 minutes for a smoothie. I don't have that kind of time on my lunch break.",
        sourceId: 'yelp',
        sourceName: 'Yelp',
        upvotes: null,
        date: '2026-02-28',
        url: 'https://www.yelp.com/',
      },
      {
        quote: 'The line at the counter was insane at 8am. Need a pre-order option.',
        sourceId: 'google_reviews',
        sourceName: 'Google Reviews',
        upvotes: null,
        date: '2026-03-05',
        url: 'https://maps.google.com/',
      },
    ],
  },
];

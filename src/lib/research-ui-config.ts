import type { MetricTarget, ValidationMethod } from '@/types/research-ui';

export const FILTER_CATEGORIES = [
  { key: 'all', label: 'All' },
  { key: 'pain', label: 'Pain points' },
  { key: 'want', label: 'Unmet wants' },
  { key: 'gap', label: 'Market gaps' },
] as const;

export type FilterCategoryKey = (typeof FILTER_CATEGORIES)[number]['key'];

export const VALIDATION_METHODS: ValidationMethod[] = [
  {
    id: 'landing',
    name: 'Landing page',
    description: 'Build a waitlist page and measure signups',
    effort: 'medium',
    speed: 'fast',
  },
  {
    id: 'survey',
    name: 'Survey',
    description: 'Run a customer discovery survey with targeted questions',
    effort: 'low',
    speed: 'fast',
  },
  {
    id: 'social',
    name: 'Social outreach',
    description: 'Post in relevant communities and groups',
    effort: 'low',
    speed: 'fast',
  },
  {
    id: 'marketplace',
    name: 'Marketplace listing',
    description: 'List on Craigslist, Facebook Marketplace, or Thumbtack',
    effort: 'medium',
    speed: 'medium',
  },
  {
    id: 'direct',
    name: 'Direct outreach',
    description: 'Reach out to gyms, offices, and apartment communities',
    effort: 'high',
    speed: 'slow',
  },
];

export function createDefaultValidationMetrics(): MetricTarget[] {
  return [
    { id: 'signups', label: 'Waitlist signups', target: 150, targetLabel: '150+', unit: 'people', actual: 0 },
    { id: 'surveys', label: 'Survey completions', target: 50, targetLabel: '50+', unit: 'responses', actual: 0 },
    { id: 'switch', label: '"Would switch" rate', target: 60, targetLabel: '60%+', unit: '%', actual: 0 },
    { id: 'price', label: 'Avg price tolerance', target: 8, targetLabel: '≥ $8', unit: '$', actual: 0 },
  ];
}

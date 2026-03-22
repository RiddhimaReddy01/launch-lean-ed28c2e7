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
    id: 'website',
    name: 'Generate a website',
    description: 'Create a landing page with Lovable to capture signups',
    effort: 'low',
    speed: 'fast',
    category: 'build',
    action: 'lovable',
  },
  {
    id: 'form',
    name: 'Survey / Form',
    description: 'Run a discovery survey via Google Forms or Typeform',
    effort: 'low',
    speed: 'fast',
    category: 'build',
  },
  {
    id: 'whatsapp',
    name: 'WhatsApp outreach',
    description: 'Share with contacts and groups on WhatsApp',
    effort: 'low',
    speed: 'fast',
    category: 'outreach',
  },
  {
    id: 'reddit',
    name: 'Reddit',
    description: 'Post in relevant subreddits for feedback',
    effort: 'low',
    speed: 'fast',
    category: 'social',
  },
  {
    id: 'twitter',
    name: 'Twitter / X',
    description: 'Tweet your idea and track engagement',
    effort: 'low',
    speed: 'fast',
    category: 'social',
  },
  {
    id: 'linkedin',
    name: 'LinkedIn',
    description: 'Post to your professional network',
    effort: 'low',
    speed: 'medium',
    category: 'social',
  },
  {
    id: 'google_ads',
    name: 'Google Ads',
    description: 'Run search ads to test keyword demand',
    effort: 'high',
    speed: 'fast',
    category: 'paid',
  },
  {
    id: 'meta_ads',
    name: 'Meta Ads',
    description: 'Run Facebook/Instagram ads to test audience interest',
    effort: 'high',
    speed: 'fast',
    category: 'paid',
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

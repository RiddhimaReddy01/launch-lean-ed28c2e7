export interface ValidationMethod {
  id: string;
  name: string;
  description: string;
  effort: 'low' | 'medium' | 'high';
  speed: 'fast' | 'medium' | 'slow';
}

export interface LandingPageAsset {
  headline: string;
  subheadline: string;
  benefits: string[];
  cta: string;
  socialProof: string;
}

export interface SurveyQuestion {
  id: string;
  question: string;
  type: 'multiple_choice' | 'scale' | 'open' | 'email';
  options?: string[];
}

export interface OutreachMessage {
  tone: string;
  message: string;
}

export interface MarketplaceListing {
  title: string;
  description: string;
  pricing: string;
  hook: string;
}

export interface DirectOutreach {
  pitchMessage: string;
  introScript: string;
  valueProp: string;
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

export const MOCK_METHODS: ValidationMethod[] = [
  { id: 'landing', name: 'Landing page', description: 'Build a waitlist page and measure signups', effort: 'medium', speed: 'fast' },
  { id: 'survey', name: 'Survey', description: 'Run a customer discovery survey with targeted questions', effort: 'low', speed: 'fast' },
  { id: 'social', name: 'Social outreach', description: 'Post in relevant communities and groups', effort: 'low', speed: 'fast' },
  { id: 'marketplace', name: 'Marketplace listing', description: 'List on Craigslist, Facebook Marketplace, or Thumbtack', effort: 'medium', speed: 'medium' },
  { id: 'direct', name: 'Direct outreach', description: 'Reach out to gyms, offices, and apartment communities', effort: 'high', speed: 'slow' },
];

export const MOCK_LANDING_PAGE: LandingPageAsset = {
  headline: 'Plano deserves a real juice bar.',
  subheadline: 'Fresh, cold-pressed, locally sourced. Not another franchise smoothie.',
  benefits: [
    'Cold-pressed daily from local Texas farms',
    "Transparent ingredients — see exactly what's in every bottle",
    'Affordable without the franchise markup',
    'Opening in West Plano — walk-in or subscribe for weekly delivery',
  ],
  cta: 'Join the waitlist →',
  socialProof: '"I paid $14 for a smoothie that tasted watered down." — real Plano resident',
};

export const MOCK_SURVEY: SurveyQuestion[] = [
  { id: 'q1', question: 'How often do you buy juice or smoothies?', type: 'multiple_choice', options: ['Daily', '2–3x per week', 'Weekly', 'Rarely'] },
  { id: 'q2', question: 'Where do you currently buy them?', type: 'multiple_choice', options: ['Juice bar / smoothie shop', 'Grocery store', 'Make at home', "I don't"] },
  { id: 'q3', question: 'What frustrates you about current options?', type: 'open' },
  { id: 'q4', question: 'How important is knowing where ingredients come from?', type: 'scale', options: ['1', '2', '3', '4', '5'] },
  { id: 'q5', question: 'Would you switch to a new local juice bar if it was transparent about sourcing?', type: 'multiple_choice', options: ['Definitely', 'Probably', 'Maybe', 'No'] },
  { id: 'q6', question: "What is the most you would pay for a 16oz cold-pressed juice?", type: 'multiple_choice', options: ['$6-8', '$8-10', '$10-12', '$12+'] },
  { id: 'q7', question: 'Which Plano area is most convenient for you?', type: 'multiple_choice', options: ['Legacy West', 'Downtown Plano', 'West Plano', 'Other'] },
  { id: 'q8', question: 'Would you be interested in a weekly juice subscription?', type: 'multiple_choice', options: ['Yes', 'Maybe', 'No'] },
  { id: 'q9', question: 'Leave your email for launch updates', type: 'email' },
];

export const MOCK_SOCIAL_OUTREACH: OutreachMessage = {
  tone: 'Casual & conversational',
  message: "Hey everyone! I am exploring opening a cold-pressed juice bar in Plano -- real ingredients, transparent sourcing, no franchise markup.\n\nBefore I invest a single dollar, I want to hear from you: Would you actually want this? What is missing from the current options?\n\nI put together a quick 2-min survey -- would love your honest thoughts: [survey link]\n\nThanks!",
};

export const MOCK_MARKETPLACE: MarketplaceListing = {
  title: 'Fresh Cold-Pressed Juice — Plano/West Plano (Pre-Launch)',
  description: "Testing interest for a new locally-sourced cold-pressed juice concept in the Plano area. Made fresh daily with produce from Texas farms. Not a franchise -- a real local business focused on quality and transparency. Reply if you would be interested in trying samples or joining our waitlist.",
  pricing: '$7–10 per 16oz bottle',
  hook: 'Tired of paying $14 for watered-down franchise smoothies?',
};

export const MOCK_DIRECT_OUTREACH: DirectOutreach = {
  pitchMessage: "Hi -- I am launching a cold-pressed juice concept in West Plano and looking for partners. Would your community be interested in a weekly fresh juice delivery or pop-up?",
  introScript: "My name is [Your Name]. I noticed your gym / apartment community / office does not have a healthy beverage option nearby. I am starting a locally-sourced juice bar and would love to explore a partnership -- maybe a small fridge or weekly delivery.",
  valueProp: "We source from Texas farms, press daily, and price 20-30% below franchise competitors. Your members get better juice, and you get a wellness amenity at zero cost.",
};

export const MOCK_COMMUNITIES: CommunityChannel[] = [
  { id: 'ch1', name: 'r/plano', platform: 'Reddit', platformColor: '#FF4500', members: '42K', rationale: 'Ground zero for local complaints about overpriced food', url: 'https://www.reddit.com/r/plano/' },
  { id: 'ch2', name: 'r/Dallas', platform: 'Reddit', platformColor: '#FF4500', members: '287K', rationale: 'Broader DFW audience with active food discussion', url: 'https://www.reddit.com/r/Dallas/' },
  { id: 'ch3', name: 'Dallas Foodies', platform: 'Facebook', platformColor: '#1877F2', members: '89K', rationale: 'Highly engaged food enthusiasts who drive word-of-mouth', url: 'https://www.facebook.com/groups/dallasfoodies/' },
  { id: 'ch4', name: 'Nextdoor Plano', platform: 'Nextdoor', platformColor: '#00B246', members: '15K', rationale: 'Hyper-local, high trust — ideal for neighborhood businesses', url: 'https://nextdoor.com/' },
  { id: 'ch5', name: 'Plano Moms', platform: 'Facebook', platformColor: '#1877F2', members: '34K', rationale: 'Health-conscious parents seeking quality food options', url: 'https://www.facebook.com/groups/planomoms/' },
  { id: 'ch6', name: 'DFW Fitness', platform: 'Reddit', platformColor: '#FF4500', members: '18K', rationale: 'Fitness crowd actively seeking post-workout nutrition', url: 'https://www.reddit.com/r/dfwfitness/' },
];

export const MOCK_METRICS: MetricTarget[] = [
  { id: 'signups', label: 'Waitlist signups', target: 150, targetLabel: '150+', unit: 'people', actual: 0 },
  { id: 'surveys', label: 'Survey completions', target: 50, targetLabel: '50+', unit: 'responses', actual: 0 },
  { id: 'switch', label: '"Would switch" rate', target: 60, targetLabel: '60%+', unit: '%', actual: 0 },
  { id: 'price', label: 'Avg price tolerance', target: 8, targetLabel: '≥ $8', unit: '$', actual: 0 },
];

export interface DecomposeResponse {
  business_type: string;
  location: {
    city: string;
    state: string;
    county: string;
    metro: string;
  };
  target_customers: string[];
  price_tier: string;
  source_domains: string[];
  subreddits: string[];
  review_platforms: string[];
  search_queries: string[];
}

export interface DiscoverEvidence {
  quote: string;
  source: string;
  score: number;
  upvotes?: number | null;
  date?: string | null;
}

export interface DiscoverInsight {
  id: string;
  type: string;
  title: string;
  score: number;
  frequency_score: number;
  intensity_score: number;
  willingness_to_pay_score: number;
  mention_count: number;
  evidence: DiscoverEvidence[];
  source_platforms: string[];
  audience_estimate: string;
}

export interface DiscoverSource {
  name: string;
  type: string;
  post_count: number;
}

export interface DiscoverResponse {
  sources: DiscoverSource[];
  insights: DiscoverInsight[];
}

// Analyze
export interface AnalyzeResponse {
  section: string;
  data: Record<string, any>;
}

// Setup
export interface SetupResponse {
  cost_tiers: Array<{
    tier: string;
    model?: string;
    total_range: { min: number; max: number };
    notes?: string;
    line_items: Array<{
      category: string;
      name: string;
      min_cost: number;
      max_cost: number;
      notes?: string;
    }>;
  }>;
  suppliers: Array<{
    category: string;
    name: string;
    description: string;
    location: string;
    website: string;
  }>;
  team: Array<{
    title: string;
    type: string;
    salary_range?: { min: number; max: number };
    description?: string;
  }>;
  timeline: Array<{
    phase: string;
    weeks: string;
    milestones?: string[];
    tasks?: string[];
  }>;
}

// Validate
export interface ValidateResponse {
  landing_page?: Record<string, any>;
  survey?: Record<string, any>;
  whatsapp_message?: Record<string, any>;
  communities: Array<{
    name: string;
    platform: string;
    member_count?: string;
    rationale: string;
    link: string;
  }>;
  scorecard?: Record<string, any>;
}

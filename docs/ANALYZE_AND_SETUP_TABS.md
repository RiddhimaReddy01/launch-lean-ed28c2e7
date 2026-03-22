# TAB 3: ANALYZE & TAB 4: SETUP - Complete Output & Working

---

# TAB 3: ANALYZE - Deep Dive on Opportunity

## What ANALYZE Does

Takes the **best insight from DISCOVER** and conducts 5 deep analyses:
1. **OPPORTUNITY** - Market sizing (TAM, SAM, SOM)
2. **CUSTOMERS** - Segment analysis and targeting
3. **COMPETITORS** - Competitive landscape & gaps
4. **ROOT CAUSE** - Why does the problem exist? (strategic insight)
5. **COSTS** - Preview of startup costs (detailed in SETUP)

**Goal**: Validate the market opportunity is real, sized, and actionable.

---

## Input

```json
{
  "section": "opportunity",  // Which analysis to run
  "insight": {
    "id": "insight_001",
    "type": "pain_point",
    "title": "Busy professionals struggle to maintain healthy eating",
    "score": 92.5,
    "evidence": [
      {
        "quote": "I spend 3+ hours/week on meal prep",
        "source": "reddit",
        "upvotes": 145
      }
    ],
    "audience_estimate": "15K+ professionals in Austin metro"
  },
  "decomposition": {
    "business_type": "meal prep delivery service",
    "location": {
      "city": "Austin",
      "state": "TX"
    },
    "target_customers": ["busy professionals", "health-conscious"],
    "price_tier": "mid-market"
  }
}
```

---

## ANALYZE Section 1: OPPORTUNITY

### Output Schema

```json
{
  "section": "opportunity",
  "data": {
    "tam": {
      "value": 120000000,
      "formatted": "$120M",
      "methodology": "200K professionals × $15/meal × 40 meals/month = $120M TAM",
      "confidence": "high"
    },

    "sam": {
      "value": 25000000,
      "formatted": "$25M",
      "methodology": "Austin metro (200K) × 20% interested in delivery × $15/meal × 40 meals = $24M SAM",
      "confidence": "medium"
    },

    "som": {
      "value": 500000,
      "formatted": "$500K",
      "methodology": "Year 1 target: 500 customers × $15/meal × 40 meals/month × 12 months = $500K",
      "confidence": "medium"
    },

    "funnel": {
      "total_addressable": {
        "count": 200000,
        "description": "Professionals in Austin metro"
      },
      "serviceable_addressable": {
        "count": 40000,
        "description": "20% interested + aware of meal delivery",
        "percentage": "20%"
      },
      "serviceable_obtainable": {
        "count": 500,
        "description": "Year 1 target customers",
        "percentage": "1.25% of SAM"
      },
      "conversion_rates": {
        "awareness_to_consideration": "15%",
        "consideration_to_trial": "25%",
        "trial_to_retained": "40%"
      }
    },

    "sanity_check": {
      "market_growing": true,
      "growth_rate": "25% YoY",
      "price_point_validated": true,
      "customer_pain_validated": true,
      "competitive_gap_identified": true,
      "business_viability": "STRONG"
    }
  }
}
```

### Explanation

**TAM (Total Addressable Market)**
- All professionals in Austin metro
- Value: $120M
- Calculation: 200K people × $15/meal × 40 meals/month
- Reality check: HUGE market

**SAM (Serviceable Addressable Market)**
- Professionals actually aware of + interested in meal delivery
- Value: $25M
- Calculation: TAM × 20% penetration rate
- Reality check: Still large, realistic segment

**SOM (Serviceable Obtainable Market)**
- What you can realistically capture in Year 1
- Value: $500K
- Calculation: 500 customers × $15/meal × 40 meals × 12 months
- Reality check: Achievable, ambitious

**Funnel**
```
200K Professionals (TAM)
    ↓ (20% interested in delivery)
40K Aware & Considering (SAM)
    ↓ (1.25% trial in Year 1)
500 Customers (SOM/Target)
```

---

## ANALYZE Section 2: CUSTOMERS

### Output Schema

```json
{
  "section": "customers",
  "data": {
    "segments": [
      {
        "name": "Remote Workers",
        "description": "Knowledge workers fully remote, high income, health-conscious",
        "estimated_size": 15000,
        "pain_intensity": 9.2,
        "primary_need": "Time savings + health maintenance",
        "spending_pattern": "$300-500/month on food",
        "where_to_find": "LinkedIn, r/RemoteWork, remote job boards",
        "market_coverage_percent": 37.5  // 15K of 40K SAM
      },

      {
        "name": "Busy Professionals (In-Office)",
        "description": "Corporate employees, 40+ hour weeks, limited lunch break",
        "estimated_size": 12000,
        "pain_intensity": 8.5,
        "primary_need": "Convenience, nutritional balance",
        "spending_pattern": "$250-400/month takeout",
        "where_to_find": "LinkedIn, corporate wellness programs, local FB groups",
        "market_coverage_percent": 30.0
      },

      {
        "name": "Health-Conscious Millennials",
        "description": "25-35 age group, fitness enthusiasts, social media active",
        "estimated_size": 8000,
        "pain_intensity": 7.8,
        "primary_need": "Macro tracking, ingredient transparency",
        "spending_pattern": "$200-350/month on fitness nutrition",
        "where_to_find": "Instagram, TikTok, r/HealthyFood, fitness communities",
        "market_coverage_percent": 20.0
      },

      {
        "name": "Corporate Wellness Programs",
        "description": "B2B opportunity: Companies providing wellness benefits",
        "estimated_size": 5000,
        "pain_intensity": 7.0,
        "primary_need": "Employee wellness, retention, productivity",
        "spending_pattern": "$5-15/meal company subsidy",
        "where_to_find": "HR conferences, corporate outreach, LinkedIn Sales Navigator",
        "market_coverage_percent": 12.5
      }
    ],

    "segment_insights": {
      "primary_segment": "Remote Workers",
      "highest_pain": "Remote Workers (9.2/10)",
      "easiest_to_reach": "Remote Workers (online, communities)",
      "highest_spend": "In-Office Professionals ($250-400/month)",
      "recommendation": "Start with Remote Workers (easiest), expand to In-Office as you scale"
    }
  }
}
```

### Explanation

**Segment 1: Remote Workers** (37.5% of market)
- **Pain**: 9.2/10 (highest - no time to cook)
- **Size**: 15K in Austin metro
- **Spending**: $300-500/month on food
- **How to reach**: r/RemoteWork, LinkedIn, Slack communities
- **Why valuable**: Online-first, high income, health-conscious, willing to adopt new solutions

**Segment 2: In-Office Professionals** (30% of market)
- **Pain**: 8.5/10 (busy schedules)
- **Size**: 12K in Austin metro
- **Spending**: $250-400/month on takeout
- **How to reach**: LinkedIn, corporate wellness programs, local groups
- **Why valuable**: Larger companies, potential for B2B partnerships

**Segment 3: Health-Conscious Millennials** (20% of market)
- **Pain**: 7.8/10 (want transparency)
- **Size**: 8K in Austin metro
- **Spending**: $200-350/month on fitness nutrition
- **How to reach**: Instagram, TikTok, fitness communities
- **Why valuable**: Influencers, word-of-mouth potential, brand ambassadors

**Segment 4: Corporate Wellness** (12.5% of market)
- **Pain**: 7.0/10 (employee retention, wellness)
- **Size**: 5K (actually 100-200 companies)
- **Spending**: $5-15/meal company subsidy
- **How to reach**: HR conferences, LinkedIn, corporate outreach
- **Why valuable**: High LTV, recurring revenue, larger deal sizes

---

## ANALYZE Section 3: COMPETITORS

### Output Schema

```json
{
  "section": "competitors",
  "data": {
    "competitors": [
      {
        "name": "Freshly",
        "location": "National",
        "rating": 2.8,
        "price_range": "$10-14/meal",
        "key_strength": "National scale, consistent branding",
        "key_gap": "Quality issues, meals arrive warm (2.8 stars)",
        "threat_level": "high",
        "url": "https://www.freshly.com"
      },

      {
        "name": "Factor",
        "location": "National",
        "rating": 3.5,
        "price_range": "$12-15/meal",
        "key_strength": "Macro-balanced meals, fitness focus",
        "key_gap": "Limited meal variety, delivery timing issues",
        "threat_level": "medium",
        "url": "https://www.factor.com"
      },

      {
        "name": "Gobble",
        "location": "National",
        "rating": 3.8,
        "price_range": "$11-16/meal",
        "key_strength": "Fast prep (15-min meals), healthy",
        "key_gap": "Only serves major metros, limited customization",
        "threat_level": "high",
        "url": "https://www.gobble.com"
      },

      {
        "name": "Green Snap Meals",
        "location": "Austin local",
        "rating": 4.1,
        "price_range": "$12-16/meal",
        "key_strength": "Local, fresh, strong reviews",
        "key_gap": "Small scale, limited menu, no online ordering yet",
        "threat_level": "medium",
        "url": "https://greenSnapmeals.com"
      },

      {
        "name": "Local Takeout (Chipotle, etc)",
        "location": "Austin local",
        "rating": 4.2,
        "price_range": "$10-14/meal",
        "key_strength": "Convenient, familiar, immediate",
        "key_gap": "Not nutritionally optimized, inconsistent health claims",
        "threat_level": "low",
        "url": "https://www.chipotle.com"
      }
    ],

    "competitive_landscape": {
      "direct_competitors": 3,  // Freshly, Factor, Gobble
      "indirect_competitors": 2,  // Green Snap, Takeout
      "intensity": "MEDIUM-HIGH",
      "market_leader": "Freshly (by scale, but weak reviews)"
    },

    "unfilled_gaps": [
      "No meal service with 4.5+ star reviews AND $15 price point",
      "No service with local sourcing + transparency + delivery",
      "No B2B corporate wellness meal program in Austin",
      "No customization for macros + local ingredients + delivery",
      "No service focused exclusively on remote workers"
    ],

    "opportunity_assessment": {
      "competition_level": "Moderate",
      "why_you_can_win": [
        "Local sourcing (differentiation)",
        "Superior quality (4.5+ star target)",
        "Transparency (ingredient sourcing)",
        "Customer service focus",
        "Community-building (remote workers)"
      ]
    }
  }
}
```

### Explanation

**Direct Competitors** (3)
1. **Freshly** - National scale, but quality issues (2.8⭐)
2. **Factor** - Macro-focused, but limited menu (3.5⭐)
3. **Gobble** - Fast prep, but limited customization (3.8⭐)

**Indirect Competitors** (2)
1. **Green Snap Meals** - Local Austin competitor (4.1⭐)
2. **Chipotle/Takeout** - Convenient, but not optimized (4.2⭐)

**Key Insight**: Market leader (Freshly) has **2.8⭐** rating!
- "Meals arrive warm"
- "Quality inconsistent"
- "Limited variety"

**Your Opportunity**: **4.5⭐ service** at competitive price
- Local sourcing
- Quality guarantee
- Transparency
- Remote worker focus

---

## ANALYZE Section 4: ROOT CAUSE

### Output Schema

```json
{
  "section": "rootcause",
  "data": {
    "root_causes": [
      {
        "cause_number": 1,
        "title": "Time Scarcity for Knowledge Workers",
        "explanation": "Remote & in-office professionals work 40+ hours/week. Meal prep (shopping, cooking, cleanup = 5 hours/week) competes with work, family, personal time. Result: convenience takes priority over health.",
        "your_move": "Position as time-RETURN solution: 'Get 5 hours/week back'",
        "difficulty": "hard"
      },

      {
        "cause_number": 2,
        "title": "Fragmentation of Meal Solutions",
        "explanation": "No single solution addresses ALL needs: convenience + nutrition + taste + sustainability + local sourcing + price. Customers compromise on something.",
        "your_move": "Integrate all 5 factors: 'Have your macro targets AND local ingredients AND it tastes good'",
        "difficulty": "very_hard"
      },

      {
        "cause_number": 3,
        "title": "Trust Gap with Scale",
        "explanation": "National meal services (Freshly, Factor) optimize for cost, lose on quality. Local services (Green Snap) can't scale. Nobody bridges local quality + national convenience.",
        "your_move": "Build local-first, then expand regionally: Quality proof → Scale → Expand",
        "difficulty": "medium"
      },

      {
        "cause_number": 4,
        "title": "Corporate Wellness Gap",
        "explanation": "Employers want employee wellness but current solutions are: generic (health insurance), or expensive (on-site cafeterias), or low-touch (gym subsidies). No meal-based corporate wellness exists.",
        "your_move": "B2B play: Approach companies as 'employee wellness + retention tool'. $5-10/meal subsidy.",
        "difficulty": "hard"
      }
    ],

    "strategic_insights": {
      "core_problem": "Time scarcity creates willingness to pay, but no solution fully addresses quality + convenience",
      "competitive_moat": "Local sourcing + quality + remote-worker community",
      "long_term_position": "Become the 'trusted meal brand for busy professionals'"
    }
  }
}
```

### Explanation

**Root Cause 1: Time Scarcity**
- Why it matters: Explains the $15/meal willingness to pay
- Your move: "Save 5 hours/week by not cooking"
- Risk: Time-saving alone doesn't sustain (anyone can deliver)

**Root Cause 2: Solution Fragmentation**
- Why it matters: Customers forced to choose between health & taste & cost
- Your move: Solve all 5 at once (hardest to execute, biggest differentiation)
- Risk: Very difficult to execute well

**Root Cause 3: Trust Gap**
- Why it matters: People distrust national services (low quality), but local services can't scale
- Your move: Start local (build trust), then scale (leverage trust)
- Risk: Scaling is harder than starting

**Root Cause 4: Corporate Gap**
- Why it matters: B2B opportunity if you position as "wellness tool"
- Your move: Approach HR teams, not individuals
- Risk: Longer sales cycle, but higher LTV

---

## ANALYZE Section 5: COSTS (Preview)

### Output Schema

```json
{
  "section": "costs",
  "data": {
    "total_range": {
      "min": 75000,
      "max": 100000,
      "formatted": "$75K-$100K"
    },

    "breakdown": [
      {
        "category": "Kitchen/Operations",
        "min": 35000,
        "max": 45000,
        "description": "Shared kitchen rental, equipment, licenses"
      },

      {
        "category": "Delivery/Logistics",
        "min": 15000,
        "max": 20000,
        "description": "Initial delivery setup, vehicle/logistics"
      },

      {
        "category": "Marketing/Customer Acquisition",
        "min": 15000,
        "max": 20000,
        "description": "Landing page, ads, community outreach"
      },

      {
        "category": "Tech/Software",
        "min": 5000,
        "max": 8000,
        "description": "Ordering platform, payments, inventory"
      },

      {
        "category": "Legal/Admin",
        "min": 3000,
        "max": 5000,
        "description": "LLC formation, food license, insurance"
      },

      {
        "category": "Initial Inventory",
        "min": 2000,
        "max": 2000,
        "description": "First batch of ingredients"
      }
    ],

    "note": "MID tier. For detailed breakdown, see SETUP tab."
  }
}
```

---

---

# TAB 4: SETUP - Operational Plan

## What SETUP Does

Creates a detailed **startup launch plan** with:
1. **Cost Tiers** - 3 different budget scenarios (LEAN, MID, PREMIUM)
2. **Suppliers** - Specific vendors to work with
3. **Team** - Roles needed and hiring timeline
4. **Timeline** - Week-by-week launch schedule

**Goal**: Founder can execute immediately with concrete next steps.

---

## Input

```json
{
  "business_type": "meal prep delivery service",
  "location": {
    "city": "Austin",
    "state": "TX"
  },
  "target_customers": ["busy professionals"],
  "price_tier": "mid-market",
  "selected_tier": "MID"  // User selects which scenario
}
```

---

## SETUP Output: Complete Schema

```json
{
  "cost_tiers": [
    {
      "tier": "LEAN",
      "model": "MVP: Local delivery only, single meal type",
      "total_range": {
        "min": 30000,
        "max": 50000,
        "formatted": "$30K-$50K"
      },
      "line_items": [
        {
          "category": "Kitchen",
          "name": "Shared Kitchen Rental (3 months)",
          "min_cost": 9000,
          "max_cost": 12000,
          "notes": "Use existing commercial kitchen (e.g., church, catering)"
        },
        {
          "category": "Delivery",
          "name": "Personal vehicle + setup",
          "min_cost": 2000,
          "max_cost": 3000,
          "notes": "Use your car, insulated containers"
        },
        {
          "category": "Marketing",
          "name": "Landing page + social media",
          "min_cost": 3000,
          "max_cost": 5000,
          "notes": "DIY or freelancer, focus on organic reach"
        }
      ]
    },

    {
      "tier": "MID",
      "model": "Phase 1: 3-neighborhood service, 5 meal options, professional operations",
      "total_range": {
        "min": 75000,
        "max": 100000,
        "formatted": "$75K-$100K"
      },
      "line_items": [
        {
          "category": "Kitchen",
          "name": "Dedicated commercial kitchen space",
          "min_cost": 35000,
          "max_cost": 45000,
          "notes": "6-month lease on small commercial kitchen in Austin"
        },
        {
          "category": "Delivery",
          "name": "Delivery logistics setup",
          "min_cost": 15000,
          "max_cost": 20000,
          "notes": "Van lease + insulated containers + GrubHub integration"
        },
        {
          "category": "Marketing",
          "name": "Marketing & customer acquisition",
          "min_cost": 15000,
          "max_cost": 20000,
          "notes": "Google Ads, Instagram, influencer partnerships"
        },
        {
          "category": "Tech",
          "name": "Ordering system + payments",
          "min_cost": 5000,
          "max_cost": 8000,
          "notes": "Custom platform or WooCommerce + Stripe"
        },
        {
          "category": "Legal",
          "name": "Licensing and insurance",
          "min_cost": 3000,
          "max_cost": 5000,
          "notes": "Food handling license, liability insurance, LLC"
        },
        {
          "category": "Inventory",
          "name": "Initial ingredient purchase",
          "min_cost": 2000,
          "max_cost": 2000,
          "notes": "First batch, supplier relationships"
        }
      ]
    },

    {
      "tier": "PREMIUM",
      "model": "Full launch: Multi-neighborhood, 15+ meals, branded delivery",
      "total_range": {
        "min": 150000,
        "max": 200000,
        "formatted": "$150K-$200K"
      },
      "line_items": [
        {
          "category": "Kitchen",
          "name": "Full commercial kitchen + test lab",
          "min_cost": 75000,
          "max_cost": 90000,
          "notes": "Year-long lease, own branding, R&D space"
        },
        {
          "category": "Delivery",
          "name": "Full delivery fleet",
          "min_cost": 30000,
          "max_cost": 40000,
          "notes": "2-3 branded vehicles, professional driver"
        },
        {
          "category": "Marketing",
          "name": "Comprehensive marketing campaign",
          "min_cost": 30000,
          "max_cost": 40000,
          "notes": "TV/podcast ads, Instagram influencers, event sponsorships"
        },
        {
          "category": "Tech",
          "name": "Custom mobile app + advanced features",
          "min_cost": 20000,
          "max_cost": 25000,
          "notes": "iOS/Android native app, macro tracking, subscriptions"
        }
      ]
    }
  ],

  "suppliers": [
    {
      "category": "Kitchen",
      "name": "Austin Food Incubator",
      "description": "Shared commercial kitchen with health certification",
      "location": "East Austin",
      "website": "https://austinfoodincubator.com",
      "why_recommended": "LEAN & MID option, low upfront cost, great for testing"
    },

    {
      "category": "Kitchen",
      "name": "The Kitchen, Incubator",
      "description": "Dedicated commercial kitchen space rental",
      "location": "North Austin",
      "website": "https://thekitchenincubator.com",
      "why_recommended": "MID option, move when you scale, monthly lease flexibility"
    },

    {
      "category": "Produce Sourcing",
      "name": "Good Earth Farms (Austin Farmers Market)",
      "description": "Local organic produce, bulk pricing available",
      "location": "Multiple locations",
      "website": "https://goodearth.farm",
      "why_recommended": "Supports 'local' positioning, connects to farmer network"
    },

    {
      "category": "Protein Sourcing",
      "name": "Grass Nomads Beef (Local Texas Ranch)",
      "description": "Grass-fed beef, sustainable, bulk wholesale available",
      "location": "Texas",
      "website": "https://grassnomads.com",
      "why_recommended": "Premium positioning, transparency, local story"
    },

    {
      "category": "Delivery",
      "name": "GrubHub Integration for B2C",
      "description": "Order aggregation, payment processing, delivery logistics",
      "location": "National",
      "website": "https://grubhub.com",
      "why_recommended": "MID/PREMIUM: 30% commission but massive reach"
    },

    {
      "category": "Delivery",
      "name": "Driver.com (Delivery Fleet Management)",
      "description": "Logistics coordination for own delivery fleet",
      "location": "National",
      "website": "https://driver.com",
      "why_recommended": "PREMIUM: Track deliveries, optimize routes"
    },

    {
      "category": "Tech",
      "name": "Shopify + Local Fulfillment App",
      "description": "E-commerce platform for orders",
      "location": "Online",
      "website": "https://shopify.com",
      "why_recommended": "LEAN/MID: Simple setup, good templates"
    },

    {
      "category": "Packaging",
      "name": "Eco-Friendly Packaging Co",
      "description": "Compostable meal containers, sustainable",
      "location": "Austin",
      "website": "https://ecofriendlypackaging.com",
      "why_recommended": "Sustainability angle, local supply"
    }
  ],

  "team": [
    {
      "title": "Founder/Operations Lead",
      "type": "Full-time",
      "salary_range": {
        "min": 0,
        "max": 36000
      },
      "description": "You. No salary in LEAN, small salary in MID as you scale."
    },

    {
      "title": "Chef/Head Meal Prep",
      "type": "Contract (Part-time 20 hrs/week initially)",
      "salary_range": {
        "min": 6000,
        "max": 10000
      },
      "description": "Month 1-3: Part-time culinary expertise. Month 4+: Full-time as volume grows."
    },

    {
      "title": "Delivery Driver",
      "type": "Independent Contractor/Gig",
      "salary_range": {
        "min": 3000,
        "max": 5000
      },
      "description": "Month 1: You deliver. Month 2+: Hire contractor as volume grows."
    },

    {
      "title": "Marketing/Customer Outreach",
      "type": "Freelance or Part-time 10 hrs/week",
      "salary_range": {
        "min": 2000,
        "max": 4000
      },
      "description": "Social media, email campaigns, community outreach to r/RemoteWork"
    },

    {
      "title": "Admin/Accounting",
      "type": "Freelance bookkeeper",
      "salary_range": {
        "min": 500,
        "max": 1000
      },
      "description": "QuickBooks, tax filing, invoicing"
    }
  ],

  "timeline": [
    {
      "phase": "WEEK 1-2: Foundation",
      "weeks": "2",
      "milestones": [
        "Form LLC, get FEIN",
        "Research commercial kitchen options",
        "Develop 3 signature meal recipes",
        "Create landing page (Webflow)"
      ],
      "tasks": [
        "LLC formation ($200 filing fee)",
        "Secure kitchen space commitment",
        "Recipe testing & costing",
        "Landing page setup"
      ]
    },

    {
      "phase": "WEEK 3-4: Legal & Logistics",
      "weeks": "2",
      "milestones": [
        "Food handler certification obtained",
        "Kitchen space contract signed",
        "Business liability insurance active",
        "Supplier contracts negotiated"
      ],
      "tasks": [
        "Food safety training ($150, online)",
        "Kitchen lease signed ($3K/mo)",
        "Insurance policy effective ($300/mo)",
        "Order initial equipment"
      ]
    },

    {
      "phase": "WEEK 5-6: MVP Build",
      "weeks": "2",
      "milestones": [
        "Kitchen operational (test production)",
        "Shopify store live",
        "Chef on board",
        "Delivery logistics planned"
      ],
      "tasks": [
        "Kitchen setup complete",
        "Shopify + payment setup",
        "Hire chef (contract)",
        "Test first 50 meals"
      ]
    },

    {
      "phase": "WEEK 7-8: Beta Launch",
      "weeks": "2",
      "milestones": [
        "First 50 paying customers",
        "Operational flows refined",
        "Customer feedback collected",
        "CAC metrics tracked"
      ],
      "tasks": [
        "Soft launch to email list (100 people)",
        "r/RemoteWork post + outreach",
        "Facebook local Austin groups",
        "Track CAC, retention, NPS"
      ]
    },

    {
      "phase": "WEEK 9-12: Scale Testing",
      "weeks": "4",
      "milestones": [
        "200+ active customers",
        "Unit economics validated",
        "Operational issues resolved",
        "Ready for Phase 2 expansion"
      ],
      "tasks": [
        "Google Ads launch ($2K/month budget)",
        "Influencer partnerships (micro-influencers in r/RemoteWork)",
        "Referral program setup",
        "Analyze LTV vs CAC"
      ]
    }
  ]
}
```

---

## SETUP Cost Tiers Explained

### **LEAN** ($30K-$50K) - MVP
**When to use**: Validating concept, personal investment, high risk tolerance

```
Shared kitchen............$9-12K (3 months rental)
Personal car delivery....$2-3K (containers, insulation)
DIY marketing............$3-5K (Webflow, social, organic)
Licenses/admin..........$3-5K
Supplier relationships...$2K initial orders
─────────────────────────────
Total: $30-50K
```

**What you can do**:
- 1 meal type
- 1-2 neighborhoods
- You as delivery driver
- 50-100 customers/month target
- Monthly revenue: $6-10K
- Break-even: 4-6 months

---

### **MID** ($75K-$100K) - Phase 1 Professional
**When to use**: Funded ($50K from friends/family), MVP validated, ready to scale

```
Commercial kitchen.......$35-45K (6 months lease)
Delivery fleet/setup.....$15-20K (van, containers, GrubHub API)
Marketing................$15-20K (Google Ads, Instagram, influencers)
Tech platform............$5-8K (Shopify, payments, inventory system)
Legal/licenses...........$3-5K (food handling, liability, accounting)
Initial inventory........$2K (supplier relationships)
─────────────────────────────
Total: $75-100K
```

**What you can do**:
- 5+ meal varieties
- 3-5 neighborhoods
- 1 part-time chef
- Contractor delivery driver
- 500-800 customers/month target
- Monthly revenue: $25-40K
- Break-even: 3-4 months
- Path to profitability clear

---

### **PREMIUM** ($150K-$200K) - Full Launch
**When to use**: Raised funding ($100K+), competitive market, need market share

```
Professional kitchen....$75-90K (full year lease, own space)
Branded delivery fleet...$30-40K (2-3 vehicles, professional drivers)
Comprehensive marketing.$30-40K (TV/podcast/influencers/sponsorships)
Custom mobile app.......$20-25K (iOS/Android development)
Legal/admin.............$5-10K
Inventory/operations...$10K
─────────────────────────────
Total: $150-200K
```

**What you can do**:
- 15+ meal varieties
- 8-10 neighborhoods (city-wide)
- 2+ full-time chef/kitchen staff
- 2-3 dedicated delivery drivers
- 2,000-3,000 customers/month target
- Monthly revenue: $100-150K
- Break-even: 2-3 months

---

## SETUP Suppliers Explained

### **Kitchen Options**

**LEAN**: Austin Food Incubator
- Shared commercial kitchen
- Month-to-month lease
- $3,000/month
- Health certified

**MID**: The Kitchen Incubator
- Private kitchen space (small)
- 6-month lease
- $6,000-7,000/month
- Move when you scale

**PREMIUM**: Build or lease your own
- Full commercial kitchen
- Year-long lease
- $10,000-15,000/month
- Your branding

### **Sourcing Options**

**Vegetables**: Good Earth Farms (local Austin farmers)
**Protein**: Grass Nomads (grass-fed beef, local Texas)
**Packaging**: Eco-Friendly Packaging (compostable, local Austin)

Why local?
- Supports "local" positioning ($15/meal premium)
- Better quality control
- Vendor relationships (flexibility, bulk discounts)
- Marketing story ("Austin-sourced, fresh daily")

### **Delivery Options**

**LEAN/MID**: GrubHub Integration
- Cost: 30% commission per order
- You: Focus on product
- They: Marketing, logistics, payments

**MID/PREMIUM**: Own fleet
- Cost: Fixed ($3K-5K/month vehicles + drivers)
- Control: Speed, quality, branding
- Profit: Keep 100% order value

### **Tech Options**

**LEAN**: Shopify
- Cost: $29-300/month
- Setup: 2-3 hours
- Payments: Stripe (2.9% + $0.30)

**MID**: Shopify + Custom App
- Cost: $500-1000/month
- Features: Subscription orders, macro tracking, delivery status

**PREMIUM**: Custom Platform
- Cost: $20-25K development
- Features: Everything + integrations, branding, scalability

---

## SETUP Team Explained

### **Founder/Operations**
- You don't pay yourself (bootstrap)
- As you scale: $3,000-$4,000/month (MID tier)
- Eventually: $5,000-$8,000/month (PREMIUM)

### **Chef/Head Meal Prep**
- Month 1-3: Part-time contractor ($6K-10K total)
- Month 4+: Full-time ($3,000-$4,000/month)
- Responsibility: Recipe development, quality control, training

### **Delivery Driver**
- Month 1: You deliver (included in operations time)
- Month 2: Gig contractor ($20-25/delivery)
- Month 4+: Full-time driver if needed ($3,500/month)

### **Marketing/Outreach**
- Freelancer: $2,000-4,000/month
- Responsibilities: Social media, email, community engagement
- Focus: r/RemoteWork, local Austin Facebook groups, LinkedIn

### **Admin/Bookkeeper**
- Freelancer: $500-1,000/month
- Responsibilities: QuickBooks, invoicing, tax filing
- Can often be outsourced to virtual assistant

---

## SETUP Timeline Explained

### **Phase 1: Foundation (Week 1-2)**
**Goal**: Legal setup + recipes ready
- Form LLC
- Research kitchens
- Develop 3 signature meals
- Create landing page
- **Cost**: $200 LLC + $100 landing page domain

### **Phase 2: Legal & Logistics (Week 3-4)**
**Goal**: Operational capability
- Get food handler certification
- Sign kitchen lease
- Arrange insurance
- Negotiate supplier contracts
- **Cost**: $150 training + $3K kitchen deposit

### **Phase 3: MVP Build (Week 5-6)**
**Goal**: Ready to produce and deliver
- Set up kitchen
- Shopify store live
- Hire part-time chef
- Test first 50 meals
- **Cost**: Shopify $29 + chef $500-1K test meals

### **Phase 4: Beta Launch (Week 7-8)**
**Goal**: Real paying customers
- Soft launch to 100-person email list
- Post in r/RemoteWork
- Join local Austin Facebook groups
- Track metrics: CAC, retention, NPS
- **Target**: 50 customers in week 7, 100 by week 8

### **Phase 5: Scale Testing (Week 9-12)**
**Goal**: Validate unit economics
- Launch Google Ads ($2K/month budget)
- Micro-influencer partnerships
- Set up referral program
- Analyze LTV vs CAC
- **Target**: 200+ active customers, CAC/LTV ratio 1:3+

---

## How ANALYZE & SETUP Connect to VALIDATE

```
ANALYZE OUTPUT:
├─ Market is $25M SAM
├─ 15K remote workers primary segment
├─ Competitors have 2.8-3.8 star ratings
├─ You can win with 4.5+ stars + local sourcing
└─ People willing to pay $15/meal

↓

SETUP PLAN:
├─ LEAN: Test with 50 customers
├─ MID: Launch with 500 customers
├─ PREMIUM: Scale to 2000+ customers
└─ Timeline: 12 weeks to operational

↓

VALIDATE TESTING:
├─ Recruit 50-100 early testers
├─ Measure: Signups (80+ target)
├─ Measure: Paid conversions (5+ target)
├─ Measure: Revenue (collect feedback on CAC/LTV)
└─ Verdict: GO/PIVOT/KILL
```

---

## Key Metrics by Phase

| Phase | Customers | Monthly Revenue | Profitability |
|-------|-----------|-----------------|---|
| Week 8 (Beta) | 50-100 | $3-6K | -$3-5K (still losing) |
| Week 12 (Testing) | 200-300 | $12-18K | -$1-2K (almost there) |
| Month 4-5 | 400-600 | $24-36K | **BREAK-EVEN** |
| Month 6-12 | 800-1,200 | $48-72K | **PROFITABLE** |

---

## Documentation

**Full reference files**:
- `docs/ANALYZE_TAB_OUTPUT.md` (market sizing, customers, competitors)
- `docs/SETUP_TAB_OUTPUT.md` (cost tiers, suppliers, team, timeline)

Both committed to GitHub.


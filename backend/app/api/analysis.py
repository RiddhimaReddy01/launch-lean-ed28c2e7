"""
Advanced analysis endpoints
POST /api/analyze-risks - Risk Assessment
POST /api/analyze-pricing - Pricing Strategy
POST /api/analyze-financials - Financial Projections
POST /api/analyze-customer-acquisition - Customer Acquisition Strategy
"""

import logging
import re
from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.config import settings
from app.core.auth import optional_user, get_current_user
from app.core.supabase import get_supabase

logger = logging.getLogger(__name__)
router = APIRouter()


def cache_analysis(user_id: str, idea_id: str, analysis_type: str, result: dict, assumptions: dict):
    """Store analysis result in database for caching."""
    try:
        supabase = get_supabase()
        update_data = {
            analysis_type: result,
            f"{analysis_type}_calculated_at": datetime.now(timezone.utc).isoformat(),
            f"{analysis_type}_assumptions": assumptions,
        }

        supabase.table("ideas")\
            .update(update_data)\
            .eq("id", idea_id)\
            .eq("user_id", user_id)\
            .execute()

        logger.info(f"Cached {analysis_type} analysis for idea {idea_id}")
    except Exception as e:
        logger.error(f"Failed to cache {analysis_type}: {e}")


# ═══════════════════════════════════════════════════════════════
# RISK ASSESSMENT
# ═══════════════════════════════════════════════════════════════

class RiskAssessmentRequest(BaseModel):
    decomposition: dict
    analyze: dict
    idea_id: Optional[str] = None  # If provided, cache result


class RiskAssessmentResponse(BaseModel):
    risks: list[dict]
    top_3_risks: list[dict]
    cached: bool = False
    calculated_at: Optional[str] = None


@router.get("/api/ideas/{idea_id}/risks")
async def get_cached_risks(
    idea_id: str,
    user: dict = Depends(get_current_user),
):
    """Retrieve cached risk assessment for an idea."""

    logger.info(f"User {user['id']} retrieving cached risks for idea {idea_id}")

    supabase = get_supabase()

    try:
        response = supabase.table("ideas")\
            .select("risks, risks_calculated_at, risks_assumptions")\
            .eq("id", idea_id)\
            .eq("user_id", user["id"])\
            .single()\
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Idea not found")

        data = response.data

        if not data.get("risks"):
            raise HTTPException(status_code=404, detail="No cached risks found. Run analysis first.")

        return {
            "idea_id": idea_id,
            "risks": data["risks"].get("risks", []),
            "top_3_risks": data["risks"].get("top_3_risks", []),
            "cached": True,
            "calculated_at": data.get("risks_calculated_at"),
            "assumptions": data.get("risks_assumptions"),
        }

    except Exception as e:
        logger.error(f"Error retrieving risks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/analyze-risks", response_model=RiskAssessmentResponse)
async def assess_risks(
    req: RiskAssessmentRequest,
    user: dict = Depends(get_current_user),
):
    """Identify and score key business risks. Optionally cache results."""

    logger.info("Assessing risks")

    risks = []
    analyze = req.analyze
    decomp = req.decomposition

    # ═══ MARKET RISKS ═══
    som = analyze.get("opportunity", {}).get("som", {}).get("value", 0)
    if som < 10_000_000:  # Market < $10M
        risks.append({
            "risk": "Market may be too small",
            "likelihood": "medium",
            "impact": "high",
            "severity_score": 7.5,
            "mitigation": "Validate with 50+ customer interviews",
            "owner": "founder",
            "category": "market"
        })

    # ═══ COMPETITIVE RISKS ═══
    competitors = analyze.get("competitors", {}).get("competitors", [])
    high_threat = sum(1 for c in competitors if c.get("threat_level") == "high")

    if high_threat >= 2:
        risks.append({
            "risk": "Strong established competitors",
            "likelihood": "high",
            "impact": "high",
            "severity_score": 8.0,
            "mitigation": "Build strong differentiation and community lock-in",
            "owner": "product",
            "category": "competitive"
        })

    # ═══ OPERATIONAL RISKS ═══
    team_needs = len(analyze.get("setup", {}).get("team", []))

    if team_needs > 5:
        risks.append({
            "risk": "Need large team immediately",
            "likelihood": "medium",
            "impact": "high",
            "severity_score": 7.0,
            "mitigation": "Start with contractors; convert to FTE at profitability",
            "owner": "operations",
            "category": "operational"
        })

    # ═══ CUSTOMER RISKS ═══
    root_causes = analyze.get("rootcause", {}).get("root_causes", [])
    hard_causes = [rc for rc in root_causes if "hard" in str(rc.get("difficulty", "")).lower()]

    if len(hard_causes) >= 2:
        risks.append({
            "risk": "Complex root causes to solve",
            "likelihood": "high",
            "impact": "medium",
            "severity_score": 6.5,
            "mitigation": "Prioritize causes; focus on easy wins first",
            "owner": "product",
            "category": "customer"
        })

    # ═══ FINANCIAL RISKS ═══
    setup = analyze.get("setup", {})
    if setup:
        cost_tiers = setup.get("cost_tiers", [])
        if cost_tiers:
            max_cost = cost_tiers[0].get("total_range", {}).get("max", 0)
            if max_cost > 100_000:
                risks.append({
                    "risk": "High capital requirement",
                    "likelihood": "low",
                    "impact": "high",
                    "severity_score": 6.0,
                    "mitigation": "Seek funding or start with MVP (lower tier)",
                    "owner": "finance",
                    "category": "financial"
                })

    # Sort by severity
    risks.sort(key=lambda x: x.get("severity_score", 0), reverse=True)

    logger.info(f"Identified {len(risks)} risks")

    response = RiskAssessmentResponse(
        risks=risks,
        top_3_risks=risks[:3],
        cached=False,
        calculated_at=datetime.now(timezone.utc).isoformat() if req.idea_id else None,
    )

    # Cache result if idea_id provided and user authenticated
    if req.idea_id and user:
        cache_analysis(
            user["id"],
            req.idea_id,
            "risks",
            response.model_dump(),
            {"decomposition_provided": True, "analyze_provided": True}
        )
        response.cached = True

    return response


# ═══════════════════════════════════════════════════════════════
# PRICING ANALYSIS
# ═══════════════════════════════════════════════════════════════

class PricingAnalysisRequest(BaseModel):
    analyze: dict
    idea_id: Optional[str] = None


class PricingAnalysisResponse(BaseModel):
    market_segments: list[dict]
    recommended_tiers: list[dict]
    revenue_impact: dict
    cached: bool = False
    calculated_at: Optional[str] = None


@router.get("/api/ideas/{idea_id}/pricing")
async def get_cached_pricing(
    idea_id: str,
    user: dict = Depends(get_current_user),
):
    """Retrieve cached pricing analysis for an idea."""

    logger.info(f"User {user['id']} retrieving cached pricing for idea {idea_id}")

    supabase = get_supabase()

    try:
        response = supabase.table("ideas")\
            .select("pricing, pricing_calculated_at, pricing_assumptions")\
            .eq("id", idea_id)\
            .eq("user_id", user["id"])\
            .single()\
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Idea not found")

        data = response.data

        if not data.get("pricing"):
            raise HTTPException(status_code=404, detail="No cached pricing found. Run analysis first.")

        return {
            "idea_id": idea_id,
            **data["pricing"],
            "cached": True,
            "calculated_at": data.get("pricing_calculated_at"),
            "assumptions": data.get("pricing_assumptions"),
        }

    except Exception as e:
        logger.error(f"Error retrieving pricing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/analyze-pricing", response_model=PricingAnalysisResponse)
async def analyze_pricing(
    req: PricingAnalysisRequest,
    user: dict = Depends(optional_user),
):
    """Determine optimal pricing based on customer WTP and competitors. Optionally cache results."""

    logger.info("Analyzing pricing")

    analyze = req.analyze

    # Extract customer segments
    customers = analyze.get("customers", {})
    segments = customers.get("segments", [])

    market_segments = []

    # Price each segment based on spending pattern
    for segment in segments:
        spending_pattern = segment.get("spending_pattern", "$100-150")

        # Extract price range: e.g., "$150-250" → [150, 250]
        prices = re.findall(r'\$(\d+)', spending_pattern)

        if len(prices) >= 2:
            min_price = int(prices[0])
            max_price = int(prices[1])
        elif len(prices) == 1:
            base_price = int(prices[0])
            min_price = base_price - 50
            max_price = base_price + 50
        else:
            min_price = 100
            max_price = 200

        recommended = (min_price + max_price) // 2

        market_segments.append({
            "segment": segment.get("name", "Unknown"),
            "willingness_to_pay_min": min_price,
            "willingness_to_pay_max": max_price,
            "recommended_price": recommended,
            "market_size": segment.get("estimated_size", 0),
            "pain_intensity": segment.get("pain_intensity", 5),
        })

    # Recommend tiered pricing
    recommended_tiers = []

    if len(market_segments) >= 2:
        # Standard tier: middle segment
        standard_price = market_segments[1]["recommended_price"] if len(market_segments) > 1 else 120

        recommended_tiers.append({
            "tier": "Standard",
            "price": standard_price,
            "target_segment": market_segments[1].get("segment", "Mid-Market") if len(market_segments) > 1 else "All",
            "features": "Core service",
            "expected_monthly_revenue_at_100_customers": standard_price * 100,
        })

        # Premium tier: highest segment (safe because we're in >= 2 check)
        if market_segments:  # Extra safety check
            premium_price = market_segments[0]["recommended_price"]

            recommended_tiers.append({
                "tier": "Premium",
                "price": premium_price,
                "target_segment": market_segments[0].get("segment", "Premium"),
                "features": "Core + premium add-ons",
                "expected_monthly_revenue_at_100_customers": premium_price * 100,
            })

    # Revenue impact scenarios
    revenue_impact = {}
    for price in [100, 120, 150, 180, 200]:
        revenue_impact[f"${price}"] = {
            "monthly_revenue_at_100_customers": price * 100,
            "annual_revenue_at_100_customers": price * 100 * 12,
        }

    logger.info(f"Pricing analysis complete: {len(recommended_tiers)} tiers recommended")

    response = PricingAnalysisResponse(
        market_segments=market_segments,
        recommended_tiers=recommended_tiers,
        revenue_impact=revenue_impact,
        cached=False,
        calculated_at=datetime.now(timezone.utc).isoformat() if req.idea_id else None,
    )

    # Cache result if idea_id provided and user authenticated
    if req.idea_id and user:
        cache_analysis(
            user["id"],
            req.idea_id,
            "pricing",
            response.model_dump(),
            {"segments_analyzed": len(market_segments)}
        )
        response.cached = True

    return response


# ═══════════════════════════════════════════════════════════════
# FINANCIAL PROJECTIONS
# ═══════════════════════════════════════════════════════════════

class FinancialProjectionsRequest(BaseModel):
    analyze: dict
    assumptions: Optional[dict] = None
    idea_id: Optional[str] = None


class FinancialProjectionsResponse(BaseModel):
    assumptions: dict
    year_1: dict
    year_2: dict
    year_3: dict
    breakeven_analysis: dict
    cached: bool = False
    calculated_at: Optional[str] = None


@router.get("/api/ideas/{idea_id}/financials")
async def get_cached_financials(
    idea_id: str,
    user: dict = Depends(get_current_user),
):
    """Retrieve cached financial projections for an idea."""

    logger.info(f"User {user['id']} retrieving cached financials for idea {idea_id}")

    supabase = get_supabase()

    try:
        response = supabase.table("ideas")\
            .select("financials, financials_calculated_at, financials_assumptions")\
            .eq("id", idea_id)\
            .eq("user_id", user["id"])\
            .single()\
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Idea not found")

        data = response.data

        if not data.get("financials"):
            raise HTTPException(status_code=404, detail="No cached financials found. Run analysis first.")

        return {
            "idea_id": idea_id,
            **data["financials"],
            "cached": True,
            "calculated_at": data.get("financials_calculated_at"),
            "assumptions_used": data.get("financials_assumptions"),
        }

    except Exception as e:
        logger.error(f"Error retrieving financials: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _project_year(year: int, acq_rate: float, arpu: float, churn: float, growth: float, monthly_opex: float):
    """Project financials for one year."""

    months = {}
    customers = 0
    cumulative_profit = 0

    for month in range(1, 13):
        # Acquire new customers
        customers += acq_rate * 4.33  # weeks per month

        # Apply churn
        customers *= (1 - churn)

        # Apply growth
        customers *= (1 + growth) ** 4.33

        revenue = customers * arpu
        net_profit = revenue - monthly_opex
        cumulative_profit += net_profit

        months[f"month_{month}"] = {
            "active_customers": int(customers),
            "monthly_revenue": int(revenue),
            "monthly_expenses": int(monthly_opex),
            "monthly_net_profit": int(net_profit),
            "cumulative_profit": int(cumulative_profit),
        }

    return {
        "months": months,
        "total_revenue": int(sum(m["monthly_revenue"] for m in months.values())),
        "total_expenses": int(sum(m["monthly_expenses"] for m in months.values())),
        "net_profit": int(cumulative_profit),
        "ending_customers": int(customers),
        "profitability_status": "profitable" if cumulative_profit > 0 else "not_yet_profitable",
    }


def _analyze_breakeven(acq_rate: float, arpu: float, churn: float, growth: float, monthly_opex: float):
    """Calculate breakeven month."""

    customers = 0
    cumulative = 0

    for month in range(1, 37):  # Up to 3 years
        customers += acq_rate * 4.33
        customers *= (1 - churn)
        customers *= (1 + growth) ** 4.33

        revenue = customers * arpu
        net = revenue - monthly_opex
        cumulative += net

        if cumulative >= 0:
            year = (month - 1) // 12 + 1
            return {
                "breakeven_month": month,
                "breakeven_timeframe": f"Month {month} (Year {year})",
                "customers_at_breakeven": int(customers),
                "monthly_revenue_at_breakeven": int(revenue),
            }

    return {
        "breakeven_month": None,
        "breakeven_timeframe": "Beyond 3 years",
        "note": "Adjust assumptions or reduce expenses",
    }


@router.post("/api/analyze-financials", response_model=FinancialProjectionsResponse)
async def project_financials(
    req: FinancialProjectionsRequest,
    user: dict = Depends(optional_user),
):
    """Generate 3-year financial projections. Optionally cache results."""

    logger.info("Generating financial projections")

    analyze = req.analyze

    # Extract costs
    costs = analyze.get("costs", {})
    monthly_opex = 3000  # Default

    # Parse from cost breakdown if available
    if costs.get("breakdown"):
        monthly_opex = sum(item.get("min", 0) for item in costs.get("breakdown", []))

    # Use assumptions or defaults
    assumptions = req.assumptions or {}
    acq_rate = assumptions.get("customer_acquisition_rate", 3)
    arpu = assumptions.get("average_revenue_per_customer", 150)
    churn = assumptions.get("churn_rate", 0.05)
    growth = assumptions.get("growth_rate", 0.02)

    # Project 3 years
    year_1 = _project_year(1, acq_rate, arpu, churn, growth, monthly_opex)
    year_2 = _project_year(2, acq_rate, arpu, churn, growth, monthly_opex)
    year_3 = _project_year(3, acq_rate, arpu, churn, growth, monthly_opex)

    # Breakeven analysis
    breakeven = _analyze_breakeven(acq_rate, arpu, churn, growth, monthly_opex)

    logger.info(f"Projections complete: Breakeven at {breakeven.get('breakeven_timeframe')}")

    response = FinancialProjectionsResponse(
        assumptions={
            "customer_acquisition_rate": f"{acq_rate} per week",
            "average_revenue_per_customer": f"${arpu}/month",
            "monthly_churn_rate": f"{churn*100:.1f}%",
            "weekly_growth_rate": f"{growth*100:.1f}%",
            "monthly_operating_expenses": f"${monthly_opex:,.0f}",
        },
        year_1=year_1,
        year_2=year_2,
        year_3=year_3,
        breakeven_analysis=breakeven,
        cached=False,
        calculated_at=datetime.now(timezone.utc).isoformat() if req.idea_id else None,
    )

    # Cache result if idea_id provided and user authenticated
    if req.idea_id and user:
        cache_analysis(
            user["id"],
            req.idea_id,
            "financials",
            response.model_dump(),
            {
                "customer_acquisition_rate": acq_rate,
                "average_revenue_per_customer": arpu,
                "churn_rate": churn,
                "growth_rate": growth,
                "monthly_operating_expenses": monthly_opex,
            }
        )
        response.cached = True

    return response


# ═══════════════════════════════════════════════════════════════
# CUSTOMER ACQUISITION STRATEGY
# ═══════════════════════════════════════════════════════════════

class CustomerAcquisitionRequest(BaseModel):
    decomposition: dict
    analyze: dict
    idea_id: Optional[str] = None


class CustomerAcquisitionResponse(BaseModel):
    channels: list[dict]
    phase_1_strategy: dict
    phase_2_strategy: dict
    cached: bool = False
    calculated_at: Optional[str] = None


@router.get("/api/ideas/{idea_id}/acquisition")
async def get_cached_acquisition(
    idea_id: str,
    user: dict = Depends(get_current_user),
):
    """Retrieve cached customer acquisition strategy for an idea."""

    logger.info(f"User {user['id']} retrieving cached acquisition for idea {idea_id}")

    supabase = get_supabase()

    try:
        response = supabase.table("ideas")\
            .select("acquisition, acquisition_calculated_at, acquisition_assumptions")\
            .eq("id", idea_id)\
            .eq("user_id", user["id"])\
            .single()\
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Idea not found")

        data = response.data

        if not data.get("acquisition"):
            raise HTTPException(status_code=404, detail="No cached acquisition found. Run analysis first.")

        return {
            "idea_id": idea_id,
            **data["acquisition"],
            "cached": True,
            "calculated_at": data.get("acquisition_calculated_at"),
            "assumptions": data.get("acquisition_assumptions"),
        }

    except Exception as e:
        logger.error(f"Error retrieving acquisition: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/analyze-customer-acquisition", response_model=CustomerAcquisitionResponse)
async def analyze_acquisition(
    req: CustomerAcquisitionRequest,
    user: dict = Depends(optional_user),
):
    """Generate customer acquisition strategy. Optionally cache results."""

    logger.info("Analyzing customer acquisition")

    decomp = req.decomposition
    business_type = decomp.get("business_type", "").lower()
    city = decomp.get("location", {}).get("city", "Unknown")

    # Determine best channels
    channels = []

    # Nextdoor (for local services)
    if "service" in business_type or "grooming" in business_type:
        channels.append({
            "channel": "Nextdoor",
            "priority": 1,
            "estimated_cac": 12,
            "estimated_conversion": 0.05,
            "timeline": "Week 1",
            "effort": "low",
            "actions": [
                "Post in neighborhood groups",
                "Offer first-time discount ($20 off)",
                "Encourage reviews"
            ],
            "expected_leads_per_month": 100,
        })

    # Google Local Services
    channels.append({
        "channel": "Google Local Services Ads",
        "priority": 2,
        "estimated_cac": 25,
        "estimated_conversion": 0.03,
        "timeline": "Week 2",
        "effort": "medium",
        "actions": [
            "Create Google Local Services profile",
            "Set daily budget: $20-30",
            "Encourage 5-star reviews"
        ],
        "expected_leads_per_month": 30,
    })

    # Facebook/Instagram
    channels.append({
        "channel": "Facebook/Instagram Ads",
        "priority": 3,
        "estimated_cac": 45,
        "estimated_conversion": 0.02,
        "timeline": "Week 3",
        "effort": "medium",
        "actions": [
            "Target: Busy professionals, pet owners",
            "Budget: $300-500/month",
            "Focus on testimonials and before/after"
        ],
        "expected_leads_per_month": 20,
    })

    # Yelp (organic)
    channels.append({
        "channel": "Yelp Reviews",
        "priority": 4,
        "estimated_cac": 8,
        "estimated_conversion": 0.02,
        "timeline": "Ongoing",
        "effort": "low",
        "actions": [
            "Ask satisfied customers to review",
            "Respond to all reviews",
            "Build review velocity"
        ],
        "expected_leads_per_month": 10,
    })

    # Phase 1: First 100 customers
    phase_1 = {
        "goal": "Acquire first 100 customers in 4 weeks",
        "primary_channel": channels[0]["channel"] if channels else "Unknown",
        "total_budget": 550,
        "timeline": [
            {
                "week": 1,
                "goal": "10 customers",
                "actions": ["Nextdoor blitz", "Build testimonials"],
                "budget": 100,
            },
            {
                "week": 2,
                "goal": "25 customers (15 new)",
                "actions": ["Add Google LSA", "Optimize messaging"],
                "budget": 150,
            },
            {
                "week": 3,
                "goal": "50 customers (25 new)",
                "actions": ["Launch Facebook ads", "Increase Google budget"],
                "budget": 200,
            },
            {
                "week": 4,
                "goal": "100 customers (50 new)",
                "actions": ["Full channel push", "Leverage referrals"],
                "budget": 100,
            }
        ]
    }

    # Phase 2: Scale
    phase_2 = {
        "goal": "Scale from 100 → 500 customers",
        "focus": "Optimize CAC + leverage organic",
        "budget_allocation": {
            "facebook_instagram": "40%",
            "google_local": "30%",
            "referral_incentives": "20%",
            "organic": "10%",
        },
        "expected_cac": 30,
        "expected_payback_period_months": 3,
    }

    logger.info(f"Customer acquisition strategy complete")

    response = CustomerAcquisitionResponse(
        channels=channels,
        phase_1_strategy=phase_1,
        phase_2_strategy=phase_2,
        cached=False,
        calculated_at=datetime.now(timezone.utc).isoformat() if req.idea_id else None,
    )

    # Cache result if idea_id provided and user authenticated
    if req.idea_id and user:
        cache_analysis(
            user["id"],
            req.idea_id,
            "acquisition",
            response.model_dump(),
            {
                "business_type": business_type,
                "location": city,
                "channels_identified": len(channels),
            }
        )
        response.cached = True

    return response

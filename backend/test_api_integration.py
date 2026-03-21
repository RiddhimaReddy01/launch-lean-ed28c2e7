"""
API Integration Tests - Tests actual FastAPI endpoints with mocked external services.
This tests the full request/response cycle for each module.
Run: pytest test_api_integration.py -v
Or: python test_api_integration.py
"""

import json
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
import pytest
from fastapi.testclient import TestClient

# Import the FastAPI app
from app.main import app


# ═══ TEST CLIENT ═══

@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


# ═══ FIXTURES: MOCK DATA ═══

@pytest.fixture
def sample_idea():
    return "A mobile pet grooming service that comes to your house for busy pet owners in Austin"


@pytest.fixture
def mock_decompose_response():
    return {
        "business_type": "mobile pet grooming service",
        "location": {
            "city": "Austin",
            "state": "TX",
            "county": "Travis",
            "metro": "Austin-Round Rock"
        },
        "target_customers": ["busy professionals", "pet owners"],
        "price_tier": "premium",
        "subreddits": ["Austin", "Entrepreneur", "smallbusiness", "dogs"],
        "review_platforms": ["yelp", "google"],
        "search_queries": ["pet grooming Austin", "mobile dog grooming"]
    }


@pytest.fixture
def mock_discover_response():
    return {
        "insights": [
            {
                "type": "pain_point",
                "title": "Finding trustworthy pet groomers",
                "pain_score": 8.5,
                "frequency_score": 7.2,
                "intensity_score": 8.1,
                "willingness_to_pay_score": 7.8,
                "evidence": [
                    {"quote": "Hard to find good groomers", "source": "r/Austin", "score": 85}
                ],
                "source_platforms": ["reddit"],
                "audience_estimate": "2.5M"
            }
        ]
    }


# ═══ ENDPOINT TESTS ═══

class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_root_endpoint(self, client):
        """Test GET / returns service info."""
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "LaunchLens AI API" in data["service"]
        assert len(data["endpoints"]) == 5

    def test_health_endpoint(self, client):
        """Test GET /health returns provider status."""
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "providers" in data


class TestDecomposeEndpoint:
    """Test POST /api/decompose-idea"""

    def test_valid_request(self, client):
        """Test valid decompose request."""
        payload = {
            "idea": "A mobile pet grooming service for busy Austin professionals"
        }

        with patch("app.services.llm_client.call_llm") as mock_llm:
            mock_llm.return_value = {
                "business_type": "mobile pet grooming",
                "location": {"city": "Austin", "state": "TX", "county": "", "metro": ""},
                "target_customers": ["busy professionals"],
                "price_tier": "premium",
                "subreddits": ["Austin", "smallbusiness", "Entrepreneur", "dogs"],
                "review_platforms": ["yelp", "google"],
                "search_queries": ["pet grooming Austin", "mobile grooming"]
            }

            resp = client.post("/api/decompose-idea", json=payload)
            assert resp.status_code == 200
            data = resp.json()
            assert data["business_type"] == "mobile pet grooming"
            assert data["location"]["city"] == "Austin"
            assert data["location"]["state"] == "TX"
            assert len(data["subreddits"]) >= 4

    def test_idea_too_short(self, client):
        """Test rejection of ideas with < 3 words."""
        payload = {"idea": "Pet"}
        resp = client.post("/api/decompose-idea", json=payload)
        assert resp.status_code == 400
        assert "at least 3 words" in resp.json()["detail"]

    def test_idea_too_long(self, client):
        """Test rejection of ideas > 500 chars."""
        long_idea = "a" * 501
        payload = {"idea": long_idea}
        resp = client.post("/api/decompose-idea", json=payload)
        assert resp.status_code == 422  # Pydantic validation error

    def test_llm_provider_exhausted(self, client):
        """Test handling when all LLM providers fail."""
        payload = {"idea": "A pet grooming service"}

        with patch("app.services.llm_client.call_llm") as mock_llm:
            from app.services.llm_client import AllProvidersExhaustedError
            mock_llm.side_effect = AllProvidersExhaustedError("All providers failed")

            resp = client.post("/api/decompose-idea", json=payload)
            assert resp.status_code == 503
            assert "unavailable" in resp.json()["detail"].lower()


class TestDiscoverEndpoint:
    """Test POST /api/discover-insights"""

    def test_valid_request(self, client, mock_decompose_response):
        """Test valid discover request."""
        payload = {"decomposition": mock_decompose_response}

        with patch("app.services.reddit_scraper.fetch_all_subreddits") as mock_reddit, \
             patch("app.services.google_search.run_search_queries") as mock_search, \
             patch("app.services.llm_client.call_llm") as mock_llm:

            # Mock Reddit
            mock_reddit.return_value = [
                {
                    "subreddit": "Austin",
                    "title": "Need pet grooming",
                    "selftext": "Can't find good groomers",
                    "score": 100,
                    "num_comments": 10,
                    "created_utc": 1709900000
                }
            ]

            # Mock Serper
            mock_search.return_value = [
                {
                    "title": "Pet Grooming Market",
                    "snippet": "Market worth $31.8B",
                    "link": "https://example.com",
                    "rating": 4.8
                }
            ]

            # Mock LLM calls (2 calls: categorize, score)
            mock_llm.side_effect = [
                {
                    "insights": [
                        {
                            "type": "pain_point",
                            "title": "Finding trustworthy groomers",
                            "pain_score": 8.5,
                            "frequency_score": 7.2,
                            "intensity_score": 8.1,
                            "willingness_to_pay_score": 7.8,
                            "evidence": [{"quote": "Need good groomer", "source": "r/Austin", "score": 85}],
                            "source_platforms": ["reddit"],
                            "audience_estimate": "2.5M"
                        }
                    ]
                },
                {
                    "insights": [
                        {
                            "type": "pain_point",
                            "title": "Finding trustworthy groomers",
                            "pain_score": 8.5,
                            "frequency_score": 7.2,
                            "intensity_score": 8.1,
                            "willingness_to_pay_score": 7.8,
                            "evidence": [{"quote": "Need good groomer", "source": "r/Austin", "score": 85}],
                            "source_platforms": ["reddit"],
                            "audience_estimate": "2.5M"
                        }
                    ]
                }
            ]

            resp = client.post("/api/discover-insights", json=payload)
            assert resp.status_code == 200
            data = resp.json()
            assert "insights" in data
            assert "sources" in data
            assert len(data["insights"]) > 0

    def test_invalid_decomposition(self, client):
        """Test with invalid decomposition."""
        payload = {"decomposition": {}}  # Missing required fields
        resp = client.post("/api/discover-insights", json=payload)
        # Should still work because fields have defaults
        assert resp.status_code in [200, 500]


class TestAnalyzeEndpoint:
    """Test POST /api/analyze-section"""

    def setup_analyze_mocks(self):
        """Helper to set up common mocks for analyze tests."""
        patches = {
            "google_search": patch("app.services.google_search.run_search_queries"),
            "llm": patch("app.services.llm_client.call_llm"),
            "cleaner": patch("app.services.data_cleaner.clean_search_results")
        }
        return patches

    def test_opportunity_section(self, client, mock_decompose_response, mock_discover_response):
        """Test opportunity analysis section."""
        payload = {
            "section": "opportunity",
            "insight": mock_discover_response["insights"][0],
            "decomposition": mock_decompose_response
        }

        with patch("app.services.google_search.run_search_queries") as mock_search, \
             patch("app.services.llm_client.call_llm") as mock_llm, \
             patch("app.services.data_cleaner.clean_search_results") as mock_clean:

            mock_search.return_value = [{"title": "Market", "snippet": "Data"}]
            mock_clean.return_value = [{"title": "Market", "snippet": "Data"}]
            mock_llm.return_value = {
                "tam": {"value": 31800000000, "formatted": "$31.8B", "methodology": "", "confidence": "high"},
                "sam": {"value": 2400000000, "formatted": "$2.4B", "methodology": "", "confidence": "high"},
                "som": {"value": 75000000, "formatted": "$75M", "methodology": "", "confidence": "medium"}
            }

            resp = client.post("/api/analyze-section", json=payload)
            assert resp.status_code == 200
            data = resp.json()
            assert data["section"] == "opportunity"
            assert "tam" in data["data"]
            assert "sam" in data["data"]
            assert "som" in data["data"]

    def test_customers_section(self, client, mock_decompose_response, mock_discover_response):
        """Test customers analysis section."""
        payload = {
            "section": "customers",
            "insight": mock_discover_response["insights"][0],
            "decomposition": mock_decompose_response
        }

        with patch("app.services.llm_client.call_llm") as mock_llm:
            mock_llm.return_value = {
                "segments": [
                    {
                        "name": "Premium Pet Owners",
                        "description": "High-income professionals",
                        "estimated_size": 45000,
                        "pain_intensity": 9,
                        "primary_need": "Premium grooming",
                        "spending_pattern": "$150-250",
                        "where_to_find": "Instagram"
                    }
                ]
            }

            resp = client.post("/api/analyze-section", json=payload)
            assert resp.status_code == 200
            data = resp.json()
            assert data["section"] == "customers"
            assert "segments" in data["data"]

    def test_competitors_section(self, client, mock_decompose_response, mock_discover_response):
        """Test competitors analysis section."""
        payload = {
            "section": "competitors",
            "insight": mock_discover_response["insights"][0],
            "decomposition": mock_decompose_response
        }

        with patch("app.services.google_search.run_search_queries") as mock_search, \
             patch("app.services.llm_client.call_llm") as mock_llm, \
             patch("app.services.data_cleaner.clean_search_results") as mock_clean:

            mock_search.return_value = [{"title": "Competitor", "snippet": "Data"}]
            mock_clean.return_value = [{"title": "Competitor", "snippet": "Data"}]
            mock_llm.return_value = {
                "competitors": [
                    {
                        "name": "Petco Grooming",
                        "location": "Austin",
                        "rating": 3.8,
                        "price_range": "$40-80",
                        "key_strength": "Locations",
                        "key_gap": "Turnover",
                        "threat_level": "high",
                        "url": "https://petco.com"
                    }
                ],
                "unfilled_gaps": ["Premium subscription model"]
            }

            resp = client.post("/api/analyze-section", json=payload)
            assert resp.status_code == 200
            data = resp.json()
            assert data["section"] == "competitors"
            assert "competitors" in data["data"]

    def test_invalid_section(self, client, mock_decompose_response, mock_discover_response):
        """Test invalid section rejection."""
        payload = {
            "section": "invalid_section",
            "insight": mock_discover_response["insights"][0],
            "decomposition": mock_decompose_response
        }

        resp = client.post("/api/analyze-section", json=payload)
        assert resp.status_code == 400
        assert "Invalid section" in resp.json()["detail"]


class TestSetupEndpoint:
    """Test POST /api/generate-setup"""

    def test_valid_request(self, client, mock_decompose_response, mock_discover_response):
        """Test valid setup request."""
        payload = {
            "insight": mock_discover_response["insights"][0],
            "decomposition": mock_decompose_response
        }

        with patch("app.services.google_search.run_search_queries") as mock_search, \
             patch("app.services.llm_client.call_llm") as mock_llm, \
             patch("app.services.data_cleaner.clean_search_results") as mock_clean:

            mock_search.return_value = [{"title": "Supplier", "snippet": "Data"}]
            mock_clean.return_value = [{"title": "Supplier", "snippet": "Data"}]
            mock_llm.return_value = {
                "cost_tiers": [
                    {
                        "tier": "minimum_viable",
                        "model": "Solo groomer",
                        "total_range": {"min": 15000, "max": 25000},
                        "line_items": [
                            {"category": "Vehicle", "name": "Van", "min_cost": 8000, "max_cost": 12000, "notes": ""}
                        ]
                    }
                ],
                "suppliers": [
                    {
                        "category": "equipment",
                        "name": "Grooming Co",
                        "description": "Supplies",
                        "location": "Austin",
                        "website": "https://example.com",
                        "why_recommended": "Local"
                    }
                ],
                "team": [],
                "timeline": [
                    {
                        "phase": "Foundation",
                        "weeks": "2-4",
                        "milestones": ["Setup"]
                    }
                ]
            }

            resp = client.post("/api/generate-setup", json=payload)
            assert resp.status_code == 200
            data = resp.json()
            assert "cost_tiers" in data
            assert len(data["cost_tiers"]) > 0


class TestValidateEndpoint:
    """Test POST /api/generate-validation"""

    def test_valid_request(self, client, mock_decompose_response, mock_discover_response):
        """Test valid validate request."""
        payload = {
            "channels": ["landing_page", "survey"],
            "insight": mock_discover_response["insights"][0],
            "decomposition": mock_decompose_response
        }

        with patch("app.services.google_search.run_search_queries") as mock_search, \
             patch("app.services.llm_client.call_llm") as mock_llm, \
             patch("app.services.data_cleaner.clean_search_results") as mock_clean:

            mock_search.return_value = [{"title": "Community", "snippet": "Data"}]
            mock_clean.return_value = [{"title": "Community", "snippet": "Data"}]
            mock_llm.return_value = {
                "landing_page": {
                    "headline": "Premium Grooming",
                    "subheadline": "Best service",
                    "benefits": ["Convenient", "Professional"],
                    "cta_text": "Get Started",
                    "social_proof_quote": "Great service!"
                },
                "survey": {
                    "title": "Quick Survey",
                    "questions": [
                        {
                            "number": 1,
                            "question": "What's your issue?",
                            "type": "open_text",
                            "options": None
                        }
                    ]
                },
                "whatsapp_message": {
                    "message": "Check us out! [SURVEY_LINK]",
                    "tone_note": "Friendly"
                },
                "communities": [
                    {
                        "name": "Austin Pets",
                        "platform": "facebook",
                        "member_count": "50K",
                        "rationale": "Pet owners",
                        "link": "https://facebook.com"
                    }
                ],
                "scorecard": {
                    "waitlist_target": 150,
                    "survey_target": 50,
                    "switch_pct_target": 60,
                    "price_tolerance_target": "$150"
                }
            }

            resp = client.post("/api/generate-validation", json=payload)
            assert resp.status_code == 200
            data = resp.json()
            assert "landing_page" in data
            assert "survey" in data
            assert "communities" in data


# ═══ DOCS ENDPOINT ═══

class TestDocumentation:
    """Test OpenAPI documentation."""

    def test_docs_available(self, client):
        """Test OpenAPI docs are available."""
        resp = client.get("/docs")
        assert resp.status_code == 200
        assert "swagger" in resp.text.lower() or "openapi" in resp.text.lower()

    def test_redoc_available(self, client):
        """Test ReDoc documentation is available."""
        resp = client.get("/redoc")
        assert resp.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

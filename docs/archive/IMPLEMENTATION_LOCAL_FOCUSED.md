# 4-Fix Implementation Plan (LOCAL Business Focus)

**Timeline: 90 minutes**
**Outcome: User gets survival timeline + market validation + confidence signals**

---

## Fix 1: DISCOVER - Add Confidence Reason (15 mins)

**File:** `backend/app/schemas/models.py`

Find `class Insight` and add:
```python
class Insight(BaseModel):
    # ... existing fields ...
    confidence: str = "medium"  # ADD
    confidence_reason: str = ""  # ADD
```

**File:** `backend/app/api/discover.py`

Find `_post_process()`, in the Insight creation loop add:
```python
# Before: insight.score = calculate_composite_score(raw)
insight.confidence = raw.get("confidence", "medium")
mention_count = raw.get("mention_count", 0)
platform_count = len(set(raw.get("source_platforms", [])))
insight.confidence_reason = f"{mention_count} mentions across {platform_count} sources"
```

**Test:**
```bash
curl -X POST http://localhost:8000/api/discover-insights \
  -d '{"decomposition": {"business_type": "plumber", "location": {"city": "Austin", "state": "TX"}}}'
# Verify each insight has: "confidence": "high|medium|low", "confidence_reason": "12 mentions across 2 sources"
```

---

## Fix 2: CUSTOMERS - Link Market Coverage to SAM (20 mins)

**File:** `backend/app/api/analyze.py`

Find where CUSTOMERS response is returned. After segments formatted, add:
```python
if section == "customers":
    segments = response.get("segments", [])

    # Get SAM from opportunity (passed in prior_context)
    sam_value = 1
    if prior_context and "opportunity" in prior_context:
        sam_value = prior_context["opportunity"].get("sam", {}).get("value", 1)

    # Calculate coverage
    total_size = sum(seg.get("estimated_size", 0) for seg in segments)

    for i, seg in enumerate(segments):
        coverage = (seg.get("estimated_size", 0) / sam_value * 100) if sam_value > 0 else 0
        seg["market_coverage_percent"] = round(coverage, 1)

    response["total_addressable"] = {
        "segment_size": total_size,
        "sam_value": int(sam_value),
        "coverage_percent": round((total_size / sam_value * 100), 1) if sam_value > 0 else 0
    }
```

**Test:**
```bash
curl -X POST http://localhost:8000/api/analyze \
  -d '{
    "section": "customers",
    "decomposition": {...},
    "prior_context": {
      "opportunity": {"sam": {"value": 5000000}}
    }
  }'
# Verify: each segment shows "market_coverage_percent": X, response shows "total_addressable"
```

---

## Fix 3: OPPORTUNITY - Validate with CUSTOMERS (20 mins)

**File:** `backend/app/api/analyze.py`

Find OPPORTUNITY section. After response built, add:
```python
if section == "opportunity":
    som_value = response.get("som", {}).get("value", 0)

    # Get customers from prior_context
    customer_total = 0
    if prior_context and "customers" in prior_context:
        segments = prior_context["customers"].get("segments", [])
        customer_total = sum(seg.get("estimated_size", 0) for seg in segments)

    # SOM implies X customers at Y revenue per customer
    # For local: assume $5k-10k annual revenue per customer (conservative)
    avg_revenue_per_customer = 7500
    som_implied_customers = int(som_value / avg_revenue_per_customer) if avg_revenue_per_customer > 0 else 0

    # Check if reasonable
    if customer_total > 0:
        ratio = som_implied_customers / customer_total
        if 0.7 < ratio < 1.3:
            alignment = "GOOD"
        elif 0.5 < ratio < 1.5:
            alignment = "ACCEPTABLE"
        else:
            alignment = "MISMATCH - Review assumptions"
    else:
        alignment = "PENDING - Need CUSTOMERS data"

    response["sanity_check"] = {
        "som_value": int(som_value),
        "som_implies_customers": som_implied_customers,
        "customers_segment_size": customer_total,
        "alignment": alignment,
        "note": f"SOM of ${som_value:,} at ~${avg_revenue_per_customer:,}/customer implies {som_implied_customers:,} target customers"
    }
```

**Test:**
```bash
curl -X POST http://localhost:8000/api/analyze \
  -d '{
    "section": "opportunity",
    "decomposition": {...},
    "prior_context": {
      "customers": {"segments": [{"estimated_size": 50000}]}
    }
  }'
# Verify: "sanity_check" shows alignment status
```

---

## Fix 4: DECOMPOSE - Add Business Model (For LOCAL, Keep Simple) (15 mins)

**File:** `backend/app/prompts/templates.py`

Find `decompose_stage2_system()`. Add to JSON schema:
```python
"business_model": "LOCAL | ONLINE | HYBRID"  # Simplified for local focus
```

Add guidance to prompt:
```python
# Add this line to the prompt text:
"""
Business model:
- LOCAL: Physical location, customers come to you (restaurant, salon, gym, plumber local)
- ONLINE: Digital service, no physical location needed
- HYBRID: Both online + physical (local with delivery/online booking)

For local business: probably LOCAL."""
```

**File:** `backend/app/api/decompose.py`

Find stage2 response processing, add validation:
```python
# DECOMPOSE stage 2
business_model = stage2_response.get('business_model', 'LOCAL')

valid_models = ['LOCAL', 'ONLINE', 'HYBRID']
if business_model not in valid_models:
    # Default to LOCAL (platform focus)
    business_model = 'LOCAL'

stage2_response['business_model'] = business_model
```

**Test:**
```bash
curl -X POST http://localhost:8000/api/decompose \
  -d '{"idea": "Plumbing marketplace in Austin"}'
# Verify: business_model field present (should be LOCAL or HYBRID)
```

---

## Implementation: Copy-Paste Checklist

### Step 1: Update Schema (5 mins)
- [ ] Add `confidence: str` to Insight class
- [ ] Add `confidence_reason: str` to Insight class

### Step 2: Update DISCOVER (10 mins)
- [ ] Add confidence logic to `_post_process()` in discover.py

### Step 3: Update CUSTOMERS (10 mins)
- [ ] Add market_coverage calculation in analyze.py CUSTOMERS section

### Step 4: Update OPPORTUNITY (10 mins)
- [ ] Add sanity_check logic in analyze.py OPPORTUNITY section

### Step 5: Update DECOMPOSE (8 mins)
- [ ] Add business_model to prompt in templates.py
- [ ] Add validation in decompose.py

### Step 6: Test (20 mins)
- [ ] Test DISCOVER: confidence shows
- [ ] Test CUSTOMERS: market_coverage_percent shows
- [ ] Test OPPORTUNITY: sanity_check alignment shows
- [ ] Test DECOMPOSE: business_model shows

### Step 7: Deploy (5 mins)
- [ ] `git add -A && git commit -m "feat: add validation + confidence to tabs"`
- [ ] `git push origin main`

---

## What Each Fix Solves

### DISCOVER Confidence (15 mins)
```
Before: "Wait times is high intensity" (founder: how confident is this?)
After:  "Wait times intensity 7, high confidence (12 mentions across 2 platforms)"
```

### CUSTOMERS SAM Link (20 mins)
```
Before: "Busy plumbers = 5000 people" (founder: is this real?)
After:  "Busy plumbers = 5000 people = 8% of addressable market ($62.5M)"
        (founder: now knows if segments are too small/big)
```

### OPPORTUNITY Validation (20 mins)
```
Before: "SOM = $5M" (founder: where does this come from?)
After:  "SOM = $5M implies ~670 customers. You identified 5000 customers.
         Alignment: MISMATCH - Review assumptions"
        (founder: knows to question the math or find more customers)
```

### DECOMPOSE Business Model (15 mins)
```
Before: Inferred from keywords (plumber + Austin = local)
After:  "business_model": "LOCAL" (explicit, downstream sections can use)
```

---

## Why These 4 (Not the Others)

✅ **These 4 directly answer founder questions:**
1. "Is this insight reliable?" (DISCOVER confidence)
2. "Does my market size make sense?" (CUSTOMERS + OPPORTUNITY validation)
3. "Am I local or online?" (DECOMPOSE model)

❌ **Skip these for now (over-engineering for local):**
- ROOT CAUSES effort weeks (local services simpler, less relevant)
- COMPETITORS beat sheet (local markets don't have direct competitors usually)
- COSTS runway (local services have different burn than SaaS)

---

## Time Tracker

```
Start:                    ___:00
DISCOVER (10m):          ___:10
CUSTOMERS (10m):         ___:20
OPPORTUNITY (10m):       ___:30
DECOMPOSE (10m):         ___:40
Testing (20m):           ___:00
Deploy (5m):             ___:05

Total: 65 mins (leaves 25 min buffer)
```

---

## Success = Founder Now Sees

✅ "My insights are based on 12 mentions (high confidence)"
✅ "My customer segment = 8% of addressable market"
✅ "My market sizing aligns with customer count"
✅ "This is a LOCAL business (not online)"

That's it. Simple. Useful. Focused.


with open('discover.py', 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

# Find _fallback_insights function and replace it
output = []
i = 0
while i < len(lines):
    if 'def _fallback_insights(posts: list[dict]) -> dict:' in lines[i]:
        # Found the function, skip to next def
        output.append(lines[i])
        i += 1
        # Collect until next function
        func_lines = []
        while i < len(lines) and not lines[i].startswith('def '):
            func_lines.append(lines[i])
            i += 1
        
        # Replace the function body
        output.append('    """Heuristic insights when LLM unavailable."""\n')
        output.append('    # Simple bag of words by source; pick top terms\n')
        output.append('    texts = []\n')
        output.append('    for p in posts:\n')
        output.append('        texts.append(p.get("title", ""))\n')
        output.append('        texts.append(p.get("body", p.get("snippet", "")))\n')
        output.append('    full = " ".join(texts).lower()\n')
        output.append('    keywords = []\n')
        output.append('    for term in ["price", "wait", "quality", "service", "trust", "location", "app", "support", "feature"]:\n')
        output.append('        if term in full:\n')
        output.append('            keywords.append(term)\n')
        output.append('    \n')
        output.append('    # Cycle through insight types\n')
        output.append('    types = ["pain_point", "unmet_want", "market_gap"]\n')
        output.append('    insights = []\n')
        output.append('    for i, term in enumerate(keywords[:5]):\n')
        output.append('        # Calculate mention count from posts\n')
        output.append('        mention_count = sum(1 for p in posts if term in p.get("title", "").lower() or term in p.get("body", p.get("snippet", "")).lower())\n')
        output.append('        \n')
        output.append('        insights.append({\n')
        output.append('            "id": f"fallback_{i+1}",\n')
        output.append('            "type": types[i % len(types)],  # Cycle through types\n')
        output.append('            "title": f"Frequent mention of {term}",\n')
        output.append('            "score": 5,\n')
        output.append('            "frequency_score": 5,\n')
        output.append('            "intensity_score": 4,\n')
        output.append('            "willingness_to_pay_score": 3,\n')
        output.append('            "mention_count": mention_count,  # Use actual count\n')
        output.append('            "evidence": [],\n')
        output.append('            "source_platforms": ["reddit", "search"],\n')
        output.append('            "audience_estimate": "",  # Empty string instead of "unknown"\n')
        output.append('        })\n')
        output.append('    return {"insights": insights}\n')
        output.append('\n')
    else:
        output.append(lines[i])
        i += 1

with open('discover.py', 'w', encoding='utf-8') as f:
    f.writelines(output)

print("Fixed discover.py")

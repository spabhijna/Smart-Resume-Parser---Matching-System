from typing import List

def normalize_list(items: List[str]) -> set[str]:
    return {item.strip().lower() for item in items}

def match_level(score: float) -> str:
    """
    Categorizes the candidate based on the weighted scoring logic.
    Note: Since we use penalties for missing required skills, 
    scores above 0.80 are rare and represent top-tier talent.
    """
    if score >= 0.85:
        return "Top Talent"  # Perfect or near-perfect match
    
    if score >= 0.70:
        return "Strong Match" # Likely has all required skills, maybe missing preferred
    
    if score >= 0.40:
        return "Potential Fit" # Good candidate, but likely missing a key requirement
    
    if score > 0.15:
        return "Low Relevance" # Significant gaps in experience or skills
        
    return "Not Recommended"
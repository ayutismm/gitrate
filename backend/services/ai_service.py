"""
AI Service - Qualitative Analysis
The AI receives raw GitHub data + pre-calculated base scores.
It returns qualitative analysis and a context multiplier (0.8 - 1.2).
"""
import json
from typing import Dict, Any
from config import settings
import re
import sys
import time
import os
from pydantic import BaseModel, Field
from typing import List

# Check if mock mode is enabled
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"


class QualitativeAnalysis(BaseModel):
    """Detailed qualitative analysis for each category"""
    contribution_notes: str = ""
    pr_quality_notes: str = ""
    impact_notes: str = ""
    code_quality_notes: str = ""


class AIQualitativeResponse(BaseModel):
    """Strict schema for AI response validation"""
    context_multiplier: float = Field(default=1.0, ge=0.8, le=1.2)
    qualitative_analysis: QualitativeAnalysis = Field(default_factory=QualitativeAnalysis)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    summary: str = ""


def generate_qualitative_prompt(github_data: Dict[str, Any], base_scores: Dict[str, Any]) -> str:
    """
    Generate a prompt for qualitative AI analysis.
    The AI receives both raw stats AND pre-calculated scores.
    """
    profile = github_data.get("profile", {})
    repos_summary = github_data.get("repos_summary", {})
    pull_requests = github_data.get("pull_requests", {})
    activity = github_data.get("activity", {})
    
    prompt = f"""You are a senior developer evaluating a GitHub profile. I have already calculated the BASE SCORES using a deterministic formula. Your job is to:

1. Analyze the QUALITATIVE aspects that numbers can't capture.
2. Provide a CONTEXT MULTIPLIER (0.8 to 1.2) to adjust the final score based on your analysis.

## Pre-Calculated Base Scores (Deterministic)
- Contribution Score: {base_scores.get('contribution_score', 0)}/100
- PR Quality Score: {base_scores.get('pr_quality_score', 0)}/100
- Impact Score: {base_scores.get('impact_score', 0)}/100
- Code Quality Score: {base_scores.get('code_quality_score', 0)}/100
- **Base Score: {base_scores.get('base_score', 0)}/100**
- **Base Tier: {base_scores.get('base_tier', 'Unknown')}**

## Raw GitHub Data for Qualitative Analysis

### Developer Profile
- Username: {github_data.get("username", "Unknown")}
- Name: {profile.get("name", "N/A")}
- Bio: {profile.get("bio", "N/A")}
- Company: {profile.get("company", "N/A")}
- Location: {profile.get("location", "N/A")}
- Account Created: {profile.get("created_at", "N/A")}
- Followers: {profile.get("followers", 0)}
- Following: {profile.get("following", 0)}

### Repository Statistics
- Total Repositories: {repos_summary.get("total", 0)}
- Original Repos: {repos_summary.get("original", 0)}
- Forked Repos: {repos_summary.get("forked", 0)}
- Total Stars Earned: {repos_summary.get("total_stars", 0)}
- Total Forks by Others: {repos_summary.get("total_forks", 0)}
- Top Languages: {json.dumps(repos_summary.get("top_languages", []))}
- Complex Repos (50+ contributors): {repos_summary.get("complex_repos", 0)}
- Documented Repos: {repos_summary.get("documented_repos", 0)}
- Avg Contributors/Repo: {repos_summary.get("avg_contributors_per_repo", 0)}

### Pull Request Statistics
- Merged PRs: {pull_requests.get("merged", 0)}
- Rejected/Closed PRs: {pull_requests.get("rejected", 0)}
- Open PRs: {pull_requests.get("open", 0)}
- Total PRs: {pull_requests.get("total", 0)}
- Merge Rate: {pull_requests.get("merge_rate", 0)}%
- **Reviews Given (Seniority Indicator)**: {pull_requests.get("reviews_given", 0)}
- **PRs Linked to Issues**: {pull_requests.get("prs_with_issue_links", 0)}
- **Review-to-PR Ratio**: {pull_requests.get("review_to_pr_ratio", 0)}

### Activity Metrics (Last 12 Months)
- Total Commits: {activity.get("total_commits_year", 0)}
- Active Months: {activity.get("active_months", 0)}/{activity.get("max_possible_months", 12)} (relative to account age)
- Consistency Index: {activity.get("consistency_index", 0)}%
- Avg Commits/Month: {activity.get("avg_commits_per_month", 0)}

## Your Analysis Task

Analyze the SOFT SIGNALS:
1. **Activity Consistency**: Note if low active months is due to a **new account** (check Active Months denominator). Do NOT penalize new accounts for low total months if consistency is high (e.g. 2/2).
2. Does the bio/company suggest professional experience?
1. Does the bio/company suggest professional experience?
2. Is there evidence of mentorship (high review-to-PR ratio)?
3. Are they working on complex, multi-contributor projects?
4. Do their PRs follow good practices (linked to issues)?
5. Is there diversity in their language usage?

## Response Format

Return ONLY valid JSON with this exact structure:
{{"context_multiplier": 1.0, "qualitative_analysis": {{"contribution_notes": "text", "pr_quality_notes": "text", "impact_notes": "text", "code_quality_notes": "text"}}, "strengths": ["strength1", "strength2", "strength3"], "weaknesses": ["weakness1", "weakness2"], "summary": "2-3 sentence executive summary"}}

IMPORTANT:
- context_multiplier MUST be between 0.8 and 1.2
- Use 1.0 if neutral, >1.0 if qualitative signals are positive, <1.0 if concerning
- Keep notes concise (1-2 sentences each)
- Provide exactly 3 strengths and 2 weaknesses
"""
    return prompt


def generate_mock_qualitative_response(github_data: Dict[str, Any], base_scores: Dict[str, Any]) -> AIQualitativeResponse:
    """Generate mock AI response for testing"""
    profile = github_data.get("profile", {})
    repos_summary = github_data.get("repos_summary", {})
    pull_requests = github_data.get("pull_requests", {})
    
    username = github_data.get("username", "developer")
    reviews = pull_requests.get("reviews_given", 0)
    
    # Simple heuristic for context multiplier
    multiplier = 1.0
    if reviews > 10:
        multiplier = 1.1
    if profile.get("company"):
        multiplier = min(1.2, multiplier + 0.05)
    
    return AIQualitativeResponse(
        context_multiplier=multiplier,
        qualitative_analysis=QualitativeAnalysis(
            contribution_notes=f"{username} shows {'strong' if base_scores.get('contribution_score', 0) > 50 else 'moderate'} contribution patterns.",
            pr_quality_notes=f"Review ratio of {pull_requests.get('review_to_pr_ratio', 0)} indicates {'mentorship behavior' if reviews > 5 else 'growing collaboration'}.",
            impact_notes=f"Community reach is {'significant' if repos_summary.get('total_stars', 0) > 100 else 'developing'}.",
            code_quality_notes=f"Works across {len(repos_summary.get('languages', {}))} languages."
        ),
        strengths=[
            f"Active contributor with {repos_summary.get('original', 0)} original repos",
            f"Given {reviews} code reviews to other developers",
            f"Uses {len(repos_summary.get('languages', {}))} different programming languages"
        ],
        weaknesses=[
            "Could increase PR-to-issue linkage for traceability",
            "Consider contributing to more multi-contributor projects"
        ],
        summary=f"{username} is a {base_scores.get('base_tier', 'Intermediate').lower()}-level developer with solid fundamentals. The qualitative signals {'enhance' if multiplier > 1 else 'support'} the base score assessment."
    )


def analyze_qualitative_sync(github_data: Dict[str, Any], base_scores: Dict[str, Any]) -> AIQualitativeResponse:
    """
    Get qualitative AI analysis. Receives raw GitHub data + base scores.
    Returns context multiplier and qualitative notes.
    """
    if MOCK_MODE:
        print("[AI] MOCK MODE - Returning sample qualitative analysis", file=sys.stderr, flush=True)
        return generate_mock_qualitative_response(github_data, base_scores)
    
    prompt = generate_qualitative_prompt(github_data, base_scores)
    
    # Configure OpenRouter Client
    from openai import OpenAI
    
    api_key = settings.OPENROUTER_API_KEY
    if not api_key:
        print("[AI ERROR] No OpenRouter API key found.", file=sys.stderr, flush=True)
        return AIQualitativeResponse(summary="API key missing.")
    
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        default_headers={
            "HTTP-Referer": "http://localhost:5173",
            "X-Title": "GitRate",
        }
    )
    
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            print(f"[AI] Sending qualitative analysis request to {settings.OPENROUTER_MODEL} (Attempt {attempt+1})", file=sys.stderr, flush=True)
            
            completion = client.chat.completions.create(
                model=settings.OPENROUTER_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,  # Deterministic output
                response_format={"type": "json_object"}
            )
            
            response_text = completion.choices[0].message.content.strip()
            print(f"[AI] Got response, length: {len(response_text)}", file=sys.stderr, flush=True)
            
            # Clean up response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1]
            if "```" in response_text:
                response_text = response_text.split("```")[0]
            
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                response_text = json_match.group()
            
            # Parse and validate with Pydantic
            raw_data = json.loads(response_text)
            validated = AIQualitativeResponse(**raw_data)
            
            print(f"[AI] Parsed successfully, context_multiplier: {validated.context_multiplier}", file=sys.stderr, flush=True)
            return validated
            
        except json.JSONDecodeError as e:
            print(f"[AI ERROR] JSON parsing failed: {e}", file=sys.stderr, flush=True)
            return AIQualitativeResponse(summary=f"JSON parsing error: {str(e)}")
        except Exception as e:
            print(f"[AI ERROR] Request failed: {e}", file=sys.stderr, flush=True)
            if attempt < max_retries - 1:
                print(f"[AI] Retrying in {retry_delay}s...", file=sys.stderr, flush=True)
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            else:
                return AIQualitativeResponse(summary=f"AI analysis failed: {str(e)}")
    
    return AIQualitativeResponse(summary="Failed after multiple retries")


async def analyze_developer(github_data: Dict[str, Any], base_scores: Dict[str, Any]) -> AIQualitativeResponse:
    """Async wrapper for qualitative analysis"""
    return analyze_qualitative_sync(github_data, base_scores)


def combine_scores(base_scores: Dict[str, Any], ai_response: AIQualitativeResponse, github_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Combine deterministic base scores with AI qualitative analysis.
    Final Score = Base Score * Context Multiplier
    """
    base_score = base_scores.get("base_score", 0)
    multiplier = ai_response.context_multiplier
    
    final_score = round(base_score * multiplier, 1)
    final_score = min(100, max(0, final_score))  # Clamp to 0-100
    
    # Determine final tier
    if final_score >= 85:
        tier = "Elite"
    elif final_score >= 70:
        tier = "Advanced"
    elif final_score >= 50:
        tier = "Intermediate"
    else:
        tier = "Beginner"
    
    result = {
        "contribution_score": base_scores.get("contribution_score", 0),
        "pr_quality_score": base_scores.get("pr_quality_score", 0),
        "impact_score": base_scores.get("impact_score", 0),
        "code_quality_score": base_scores.get("code_quality_score", 0),
        "base_score": base_score,
        "context_multiplier": multiplier,
        "final_score": final_score,
        "tier": tier,
        "strengths": ai_response.strengths,
        "weaknesses": ai_response.weaknesses,
        "detailed_analysis": {
            "contribution_analysis": ai_response.qualitative_analysis.contribution_notes,
            "pr_analysis": ai_response.qualitative_analysis.pr_quality_notes,
            "impact_analysis": ai_response.qualitative_analysis.impact_notes,
            "code_quality_analysis": ai_response.qualitative_analysis.code_quality_notes
        },
        "summary": ai_response.summary
    }
    
    # Add profile and stats if github_data available
    if github_data:
        profile = github_data.get("profile", {})
        repos_summary = github_data.get("repos_summary", {})
        pull_requests = github_data.get("pull_requests", {})
        activity = github_data.get("activity", {})
        
        result["profile"] = {
            "username": github_data.get("username", ""),
            "name": profile.get("name"),
            "avatar_url": profile.get("avatar_url"),
            "bio": profile.get("bio"),
            "followers": profile.get("followers", 0),
            "public_repos": profile.get("public_repos", 0)
        }
        
        # Tech stack (top languages)
        result["tech_stack"] = repos_summary.get("top_languages", [])
        
        # Numerical stats
        result["stats"] = {
            "total_stars": repos_summary.get("total_stars", 0),
            "total_forks": repos_summary.get("total_forks", 0),
            "total_repos": repos_summary.get("total", 0),
            "original_repos": repos_summary.get("original", 0),
            "total_commits": activity.get("total_commits_year", 0),
            "total_prs": pull_requests.get("total", 0),
            "merged_prs": pull_requests.get("merged", 0),
            "merge_rate": pull_requests.get("merge_rate", 0),
            "reviews_given": pull_requests.get("reviews_given", 0),
            "followers": profile.get("followers", 0)
        }
    
    return result


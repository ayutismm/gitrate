"""
Vercel Serverless Function - GitRate API
This combines all backend functionality into a single serverless endpoint.
"""
import os
import sys
import json
import math
import re
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import httpx

from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# ============== CONFIG ==============
class Settings:
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")
    GITHUB_API_BASE: str = "https://api.github.com"

settings = Settings()
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"

# ============== SCHEMAS ==============
class DetailedAnalysis(BaseModel):
    contribution_analysis: str
    pr_analysis: str
    impact_analysis: str
    code_quality_analysis: str

class UserProfile(BaseModel):
    username: str = ""
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    followers: int = 0
    public_repos: int = 0

class UserStats(BaseModel):
    total_stars: int = 0
    total_forks: int = 0
    total_repos: int = 0
    original_repos: int = 0
    total_commits: int = 0
    total_prs: int = 0
    merged_prs: int = 0
    merge_rate: float = 0
    reviews_given: int = 0
    followers: int = 0

class DeveloperRating(BaseModel):
    contribution_score: float
    pr_quality_score: float
    impact_score: float
    code_quality_score: float
    base_score: float = 0
    context_multiplier: float = 1.0
    final_score: float
    tier: str
    strengths: List[str]
    weaknesses: List[str]
    detailed_analysis: DetailedAnalysis
    summary: str
    profile: Optional[UserProfile] = None
    tech_stack: Optional[List] = None
    stats: Optional[UserStats] = None

class QualitativeAnalysis(BaseModel):
    contribution_notes: str = ""
    pr_quality_notes: str = ""
    impact_notes: str = ""
    code_quality_notes: str = ""

class AIQualitativeResponse(BaseModel):
    context_multiplier: float = Field(default=1.0, ge=0.8, le=1.2)
    qualitative_analysis: QualitativeAnalysis = Field(default_factory=QualitativeAnalysis)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    summary: str = ""

# ============== GITHUB SERVICE ==============
class GitHubService:
    def __init__(self):
        self.base_url = settings.GITHUB_API_BASE
        self.headers = {
            "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    
    async def get_user_profile(self, username: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/users/{username}", headers=self.headers)
            if response.status_code == 404:
                raise ValueError(f"User '{username}' not found")
            response.raise_for_status()
            return response.json()
    
    async def get_user_repos(self, username: str) -> List[Dict[str, Any]]:
        repos = []
        page = 1
        async with httpx.AsyncClient() as client:
            while True:
                response = await client.get(
                    f"{self.base_url}/users/{username}/repos",
                    headers=self.headers,
                    params={"per_page": 100, "page": page, "sort": "updated", "type": "owner"}
                )
                response.raise_for_status()
                page_repos = response.json()
                if not page_repos:
                    break
                for repo in page_repos:
                    repos.append({
                        "name": repo["name"], "stars": repo["stargazers_count"],
                        "forks": repo["forks_count"], "language": repo["language"],
                        "description": repo.get("description", ""), "is_fork": repo["fork"],
                        "created_at": repo["created_at"], "updated_at": repo["updated_at"],
                        "size": repo["size"], "topics": repo.get("topics", [])
                    })
                page += 1
                if len(page_repos) < 100:
                    break
        return repos
    
    async def get_pull_requests(self, username: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            merged = (await client.get(f"{self.base_url}/search/issues", headers=self.headers,
                params={"q": f"author:{username} type:pr is:merged", "per_page": 1})).json()["total_count"]
            rejected = (await client.get(f"{self.base_url}/search/issues", headers=self.headers,
                params={"q": f"author:{username} type:pr is:closed is:unmerged", "per_page": 1})).json()["total_count"]
            open_prs = (await client.get(f"{self.base_url}/search/issues", headers=self.headers,
                params={"q": f"author:{username} type:pr is:open", "per_page": 1})).json()["total_count"]
            reviews = (await client.get(f"{self.base_url}/search/issues", headers=self.headers,
                params={"q": f"reviewed-by:{username} type:pr", "per_page": 1})).json()["total_count"]
            total = merged + rejected + open_prs
            return {
                "merged": merged, "rejected": rejected, "open": open_prs, "total": total,
                "merge_rate": round((merged / total * 100) if total > 0 else 0, 2),
                "reviews_given": reviews, "prs_with_issue_links": 0,
                "review_to_pr_ratio": round(reviews / max(total, 1), 2)
            }
    
    async def get_commit_activity(self, username: str, account_created_at: str = None) -> Dict[str, Any]:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(f"{self.base_url}/search/commits",
                    headers={**self.headers, "Accept": "application/vnd.github.cloak-preview+json"},
                    params={"q": f"author:{username} author-date:>{start_date.strftime('%Y-%m-%d')}", "per_page": 100})
                data = response.json() if response.status_code == 200 else {"total_count": 0, "items": []}
            except:
                data = {"total_count": 0, "items": []}
            
            total_commits = data.get("total_count", 0)
            max_months = 12
            if account_created_at:
                try:
                    created = datetime.fromisoformat(account_created_at.replace("Z", "+00:00"))
                    max_months = min(12, max(1, math.ceil((datetime.now(created.tzinfo) - created).days / 30)))
                except:
                    pass
            
            return {
                "total_commits_year": total_commits, "quality_commits_year": total_commits,
                "active_months": min(max_months, max(1, total_commits // 10)),
                "max_possible_months": max_months,
                "consistency_index": min(100, (min(max_months, max(1, total_commits // 10)) / max_months) * 100),
                "avg_commits_per_month": round(total_commits / max(1, max_months), 2)
            }
    
    async def aggregate_data(self, username: str) -> Dict[str, Any]:
        profile = await self.get_user_profile(username)
        repos = await self.get_user_repos(username)
        prs = await self.get_pull_requests(username)
        activity = await self.get_commit_activity(username, profile.get("created_at"))
        
        total_stars = sum(r["stars"] for r in repos)
        total_forks = sum(r["forks"] for r in repos)
        original = [r for r in repos if not r["is_fork"]]
        languages = {}
        for r in repos:
            if r["language"]:
                languages[r["language"]] = languages.get(r["language"], 0) + 1
        
        return {
            "username": username,
            "profile": {
                "name": profile.get("name", username), "bio": profile.get("bio", ""),
                "company": profile.get("company", ""), "followers": profile.get("followers", 0),
                "public_repos": profile.get("public_repos", 0), "created_at": profile.get("created_at", ""),
                "avatar_url": profile.get("avatar_url", "")
            },
            "repos": repos,
            "repos_summary": {
                "total": len(repos), "original": len(original), "total_stars": total_stars,
                "total_forks": total_forks, "languages": languages,
                "top_languages": sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5],
                "code_repos": len([r for r in repos if r["language"]]),
                "doc_repos": len([r for r in repos if not r["language"]]),
                "sample_size": min(5, len(repos)), "readme_count": min(5, len(original)),
                "license_count": 0, "tests_count": 0, "ci_cd_count": 0
            },
            "pull_requests": prs, "activity": activity
        }

github_service = GitHubService()

# ============== SCORING SERVICE ==============
def calculate_contribution_score(data: Dict) -> float:
    repos = data.get("repos_summary", {})
    activity = data.get("activity", {})
    original = repos.get("original", 0)
    commits = activity.get("quality_commits_year", activity.get("total_commits_year", 0))
    consistency = activity.get("consistency_index", 0)
    base = 30 if original > 0 or commits > 0 else 0
    return round(min(100, base + min(20, original * 2) + min(25, math.log(commits + 1) * 6.5) + consistency * 0.15), 1)

def calculate_pr_quality_score(data: Dict) -> float:
    prs = data.get("pull_requests", {})
    if prs.get("total", 0) == 0:
        return 40.0
    merged, total, reviews = prs.get("merged", 0), prs.get("total", 1), prs.get("reviews_given", 0)
    return round(min(100, (merged / total * 35) + min(30, reviews * 3) + min(15, total * 1.5)), 1)

def calculate_impact_score(data: Dict) -> float:
    repos = data.get("repos_summary", {})
    profile = data.get("profile", {})
    stars, forks, followers = repos.get("total_stars", 0), repos.get("total_forks", 0), profile.get("followers", 0)
    base = 25 if stars > 0 or followers > 0 else 10
    return round(min(100, base + min(30, math.log(stars + 1) * 8) + min(20, math.log(forks + 1) * 6) + min(15, math.log(followers + 1) * 5)), 1)

def calculate_code_quality_score(data: Dict) -> float:
    repos = data.get("repos_summary", {})
    langs = len(repos.get("languages", {}))
    base = 20 if repos.get("total", 0) > 0 else 0
    return round(min(100, base + min(20, langs * 5) + (repos.get("readme_count", 0) / max(repos.get("sample_size", 1), 1)) * 15), 1)

def calculate_base_scores(data: Dict) -> Dict:
    c, p, i, q = calculate_contribution_score(data), calculate_pr_quality_score(data), calculate_impact_score(data), calculate_code_quality_score(data)
    base = 0.30 * c + 0.25 * p + 0.15 * i + 0.30 * q
    tier = "Elite" if base >= 80 else "Advanced" if base >= 60 else "Intermediate" if base >= 40 else "Beginner"
    return {"contribution_score": c, "pr_quality_score": p, "impact_score": i, "code_quality_score": q, "base_score": round(base, 1), "base_tier": tier}

# ============== AI SERVICE ==============
def generate_mock_response(data: Dict, scores: Dict) -> AIQualitativeResponse:
    username = data.get('username', 'Developer')
    repos = data.get('repos_summary', {})
    prs = data.get('pull_requests', {})
    activity = data.get('activity', {})
    tier = scores.get('base_tier', 'Intermediate')
    
    return AIQualitativeResponse(
        context_multiplier=1.0,
        qualitative_analysis=QualitativeAnalysis(
            contribution_notes=f"{username} demonstrates {tier.lower()}-level contribution patterns with {repos.get('original', 0)} original repositories and {activity.get('total_commits_year', 0)} commits in the past year. Activity consistency shows dedicated engagement with open source.",
            pr_quality_notes=f"Pull request metrics show {prs.get('merged', 0)} merged PRs with a {prs.get('merge_rate', 0)}% merge rate. {prs.get('reviews_given', 0)} code reviews given indicates collaborative development practices.",
            impact_notes=f"Community impact is reflected through {repos.get('total_stars', 0)} stars earned across projects and {data.get('profile', {}).get('followers', 0)} followers. Repository engagement suggests growing influence in the developer community.",
            code_quality_notes=f"Technical diversity spans {len(repos.get('languages', {}))} programming languages. Top technologies include expertise in {', '.join([l[0] for l in repos.get('top_languages', [])[:3]]) or 'various languages'}."
        ),
        strengths=[
            f"Active contributor with {repos.get('original', 0)} original repositories",
            f"Consistent activity with {activity.get('total_commits_year', 0)} commits this year",
            f"Diverse tech stack spanning {len(repos.get('languages', {}))} languages"
        ],
        weaknesses=[
            "Could increase engagement in code reviews and PR discussions",
            "Adding more documentation would improve project accessibility"
        ],
        summary=f"{username} is a {tier.lower()}-level developer demonstrating solid technical skills and consistent contribution patterns. Their GitHub profile reflects growing expertise and community engagement."
    )

async def analyze_developer(data: Dict, scores: Dict) -> AIQualitativeResponse:
    if MOCK_MODE:
        return generate_mock_response(data, scores)
    
    try:
        from openai import OpenAI
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=settings.OPENROUTER_API_KEY)
        
        repos = data.get('repos_summary', {})
        prs = data.get('pull_requests', {})
        activity = data.get('activity', {})
        profile = data.get('profile', {})
        
        prompt = f"""You are a senior developer evaluating a GitHub profile. Analyze and return JSON.

## GitHub Data
- Username: {data.get('username')}
- Base Score: {scores.get('base_score')}/100
- Repos: {repos.get('total', 0)} (Original: {repos.get('original', 0)})
- Stars: {repos.get('total_stars', 0)}, Forks: {repos.get('total_forks', 0)}
- PRs: {prs.get('total', 0)} (Merged: {prs.get('merged', 0)}, Rate: {prs.get('merge_rate', 0)}%)
- Reviews Given: {prs.get('reviews_given', 0)}
- Commits (Year): {activity.get('total_commits_year', 0)}
- Languages: {', '.join([l[0] for l in repos.get('top_languages', [])[:5]])}
- Followers: {profile.get('followers', 0)}

## Return JSON with this exact structure:
{{"context_multiplier": 1.0, "qualitative_analysis": {{"contribution_notes": "2-3 sentences about contribution patterns", "pr_quality_notes": "2-3 sentences about PR quality and collaboration", "impact_notes": "2-3 sentences about community impact", "code_quality_notes": "2-3 sentences about code quality and tech diversity"}}, "strengths": ["strength1", "strength2", "strength3"], "weaknesses": ["area1", "area2"], "summary": "2-3 sentence executive summary"}}

IMPORTANT: context_multiplier must be 0.8-1.2. Return ONLY valid JSON."""
        
        completion = client.chat.completions.create(model=settings.OPENROUTER_MODEL, 
            messages=[{"role": "user", "content": prompt}], temperature=0, response_format={"type": "json_object"})
        result = json.loads(completion.choices[0].message.content)
        return AIQualitativeResponse(**result)
    except Exception as e:
        print(f"AI Error: {e}")
        return generate_mock_response(data, scores)

def combine_scores(base: Dict, ai: AIQualitativeResponse, data: Dict) -> Dict:
    final = round(min(100, max(0, base["base_score"] * ai.context_multiplier)), 1)
    tier = "Elite" if final >= 85 else "Advanced" if final >= 70 else "Intermediate" if final >= 50 else "Beginner"
    
    result = {**base, "context_multiplier": ai.context_multiplier, "final_score": final, "tier": tier,
        "strengths": ai.strengths, "weaknesses": ai.weaknesses,
        "detailed_analysis": {"contribution_analysis": ai.qualitative_analysis.contribution_notes,
            "pr_analysis": ai.qualitative_analysis.pr_quality_notes,
            "impact_analysis": ai.qualitative_analysis.impact_notes,
            "code_quality_analysis": ai.qualitative_analysis.code_quality_notes},
        "summary": ai.summary}
    
    if data:
        profile = data.get("profile", {})
        result["profile"] = {"username": data.get("username", ""), "name": profile.get("name"),
            "avatar_url": profile.get("avatar_url"), "bio": profile.get("bio"),
            "followers": profile.get("followers", 0), "public_repos": profile.get("public_repos", 0)}
        result["tech_stack"] = data.get("repos_summary", {}).get("top_languages", [])
        result["stats"] = {"total_stars": data.get("repos_summary", {}).get("total_stars", 0),
            "total_forks": data.get("repos_summary", {}).get("total_forks", 0),
            "total_repos": data.get("repos_summary", {}).get("total", 0),
            "total_commits": data.get("activity", {}).get("total_commits_year", 0),
            "total_prs": data.get("pull_requests", {}).get("total", 0),
            "merged_prs": data.get("pull_requests", {}).get("merged", 0),
            "merge_rate": data.get("pull_requests", {}).get("merge_rate", 0),
            "reviews_given": data.get("pull_requests", {}).get("reviews_given", 0),
            "followers": profile.get("followers", 0)}
    return result

# ============== FASTAPI APP ==============
app = FastAPI(title="GitRate", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/")
async def root():
    return {"status": "healthy", "service": "GitRate", "version": "2.0.0"}

@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.post("/api/rate/{username}")
async def rate(username: str):
    try:
        data = await github_service.aggregate_data(username)
        scores = calculate_base_scores(data)
        ai = await analyze_developer(data, scores)
        return combine_scores(scores, ai, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user/{username}/data")
async def user_data(username: str):
    try:
        return await github_service.aggregate_data(username)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

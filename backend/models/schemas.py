from pydantic import BaseModel
from typing import List, Optional

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
    base_score: float = 0  # Deterministic score before AI multiplier
    context_multiplier: float = 1.0  # AI-determined multiplier (0.8-1.2)
    final_score: float
    tier: str  # "Beginner" | "Intermediate" | "Advanced" | "Elite"
    strengths: List[str]
    weaknesses: List[str]
    detailed_analysis: DetailedAnalysis
    summary: str
    profile: Optional[UserProfile] = None
    tech_stack: Optional[List] = None
    stats: Optional[UserStats] = None

class GitHubData(BaseModel):
    username: str
    repos: List[dict]
    pull_requests: dict
    activity: dict
    profile: Optional[dict] = None

class ErrorResponse(BaseModel):
    error: str
    detail: str

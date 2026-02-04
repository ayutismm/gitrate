"""
Deterministic Scoring Service
Calculates base scores from raw GitHub metrics using weighted formulas.
The AI will later apply a context multiplier based on qualitative analysis.

v2.1 - More lenient scoring curves for fairer evaluation
"""
from typing import Dict, Any
import math


def calculate_contribution_score(github_data: Dict[str, Any]) -> float:
    """
    Contribution Score (0-100) based on activity volume and consistency.
    
    LENIENT VERSION: Even moderate activity gets decent scores.
    """
    repos_summary = github_data.get("repos_summary", {})
    activity = github_data.get("activity", {})
    
    # Core metrics
    # Anti-gaming: Use explicit code vs doc repo counts if available
    if "code_repos" in repos_summary:
        code_repos = repos_summary.get("code_repos", 0)
        doc_repos = repos_summary.get("doc_repos", 0)
        # 100% credit for code repos, 50% for doc repos
        adjusted_repos = code_repos + (doc_repos * 0.5)
    else:
        # Fallback for old data structure
        adjusted_repos = repos_summary.get("original", 0)
        
    original_repos = repos_summary.get("original", 0)
    # Use quality-adjusted commit count (anti-gaming)
    total_commits = activity.get("quality_commits_year", activity.get("total_commits_year", 0))
    consistency = activity.get("consistency_index", 0)  # 0-100
    active_months = activity.get("active_months", 0)
    max_months = activity.get("max_possible_months", 12)
    
    # Base score of 30 for having ANY activity
    base = 30 if original_repos > 0 or total_commits > 0 else 0
    
    # Repo score (0-20) - more generous, 10 repos = full points
    # Use adjusted_repos to penalize empty/doc-only repos
    repo_score = min(20, adjusted_repos * 2)
    
    # Commit score (0-25) - more generous logarithmic curve
    # 50 commits = ~20 points, 200 commits = ~25 points
    commit_score = min(25, math.log(total_commits + 1) * 6.5)
    
    # Consistency bonus (0-15)
    consistency_score = consistency * 0.15
    
    # Activity bonus (0-10) - proportionate to account existence
    activity_score = (active_months / max(1, max_months)) * 10
    
    raw_score = base + repo_score + commit_score + consistency_score + activity_score
    return round(min(100, max(0, raw_score)), 1)


def calculate_pr_quality_score(github_data: Dict[str, Any]) -> float:
    """
    PR Quality Score (0-100) based on collaboration effectiveness.
    
    LENIENT VERSION: Solo developers who don't do PRs still get baseline score.
    """
    pull_requests = github_data.get("pull_requests", {})
    
    merged = pull_requests.get("merged", 0)
    total = pull_requests.get("total", 0)
    reviews_given = pull_requests.get("reviews_given", 0)
    prs_with_issues = pull_requests.get("prs_with_issue_links", 0)
    
    # Baseline score of 40 for developers who work solo (no PRs is okay)
    if total == 0:
        return 40.0
    
    # Merge rate (0-35 points)
    merge_rate = (merged / total * 100) if total > 0 else 0
    merge_score = merge_rate * 0.35
    
    # Review bonus (0-30 points) - any reviews are good
    review_score = min(30, reviews_given * 3)
    
    # Issue linkage bonus (0-20 points)
    linkage_ratio = (prs_with_issues / max(total, 1)) if total > 0 else 0
    linkage_score = linkage_ratio * 20
    
    # Base participation score (0-15)
    participation_score = min(15, total * 1.5)
    
    raw_score = merge_score + review_score + linkage_score + participation_score
    return round(min(100, max(0, raw_score)), 1)


def calculate_impact_score(github_data: Dict[str, Any]) -> float:
    """
    Impact Score (0-100) based on community reach and influence.
    
    LENIENT VERSION: Any stars/followers count more.
    """
    repos_summary = github_data.get("repos_summary", {})
    profile = github_data.get("profile", {})
    
    total_stars = repos_summary.get("total_stars", 0)
    total_forks = repos_summary.get("total_forks", 0)
    followers = profile.get("followers", 0)
    avg_contributors = repos_summary.get("avg_contributors_per_repo", 1)
    
    # Base score of 25 for having any public presence
    base = 25 if (total_stars > 0 or followers > 0) else 10
    
    # Star score (0-30) - more generous curve
    # 10 stars = ~15 points, 100 stars = ~28 points
    star_score = min(30, math.log(total_stars + 1) * 8)
    
    # Fork score (0-20)
    fork_score = min(20, math.log(total_forks + 1) * 6)
    
    # Follower score (0-15)
    follower_score = min(15, math.log(followers + 1) * 5)
    
    # Collaboration bonus (0-10)
    collab_score = min(10, avg_contributors * 2)
    
    raw_score = base + star_score + fork_score + follower_score + collab_score
    return round(min(100, max(0, raw_score)), 1)


def calculate_code_quality_score(github_data: Dict[str, Any]) -> float:
    """
    Code Quality Score (0-100) based on technical diversity and best practices.
    
    ENHANCED VERSION: 
    - Language diversity (20pts)
    - Project complexity (15pts)
    - Documentation/READMEs (15pts)
    - Testing practices (15pts)
    - CI/CD adoption (10pts)
    - Licensing (5pts)
    - Base score (20pts)
    """
    repos_summary = github_data.get("repos_summary", {})
    
    languages = repos_summary.get("languages", {})
    top_languages = repos_summary.get("top_languages", [])
    total_repos = repos_summary.get("total", 1)
    complex_repos = repos_summary.get("complex_repos", 0)
    
    # New metrics from sample
    sample_size = repos_summary.get("sample_size", 5)
    readme_count = repos_summary.get("readme_count", 0)
    license_count = repos_summary.get("license_count", 0)
    tests_count = repos_summary.get("tests_count", 0)
    ci_cd_count = repos_summary.get("ci_cd_count", 0)
    
    # Base score of 20 for having any code
    base = 20 if total_repos > 0 else 0
    
    # Language diversity (0-20)
    lang_count = len(languages) if isinstance(languages, dict) else len(top_languages)
    diversity_score = min(20, lang_count * 5)
    
    # Complexity bonus (0-15)
    complexity_score = min(15, complex_repos * 7.5)
    
    # Documentation bonus (0-15) - Combined repo descriptions and actual READMEs
    # Scale up from sample size to projected total for READMEs
    readme_ratio = readme_count / max(sample_size, 1)
    doc_score = min(15, (readme_ratio * 15))
    
    # Testing bonus (0-15)
    test_ratio = tests_count / max(sample_size, 1)
    test_score = test_ratio * 15
    
    # CI/CD bonus (0-10)
    ci_ratio = ci_cd_count / max(sample_size, 1)
    ci_score = ci_ratio * 10
    
    # License bonus (0-5)
    license_ratio = license_count / max(sample_size, 1)
    license_score = license_ratio * 5
    
    raw_score = base + diversity_score + complexity_score + doc_score + test_score + ci_score + license_score
    return round(min(100, max(0, raw_score)), 1)


def calculate_base_scores(github_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate all base scores and the weighted final score.
    
    Returns a dictionary with individual scores and the final base score.
    """
    contribution = calculate_contribution_score(github_data)
    pr_quality = calculate_pr_quality_score(github_data)
    impact = calculate_impact_score(github_data)
    code_quality = calculate_code_quality_score(github_data)
    
    # Weighted formula
    # Weighted formula
    base_score = (
        0.30 * contribution +
        0.25 * pr_quality +
        0.15 * impact +
        0.30 * code_quality
    )
    
    # Determine tier based on base score (adjusted thresholds)
    if base_score >= 80:
        tier = "Elite"
    elif base_score >= 60:
        tier = "Advanced"
    elif base_score >= 40:
        tier = "Intermediate"
    else:
        tier = "Beginner"
    
    return {
        "contribution_score": contribution,
        "pr_quality_score": pr_quality,
        "impact_score": impact,
        "code_quality_score": code_quality,
        "base_score": round(base_score, 1),
        "base_tier": tier
    }

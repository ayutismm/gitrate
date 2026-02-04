import httpx
from datetime import datetime, timedelta
import asyncio
import math
from typing import List, Dict, Any
from config import settings

class GitHubService:
    def __init__(self):
        self.base_url = settings.GITHUB_API_BASE
        self.headers = {
            "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    
    async def get_user_profile(self, username: str) -> Dict[str, Any]:
        """Fetch basic user profile information"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/users/{username}",
                headers=self.headers
            )
            if response.status_code == 404:
                raise ValueError(f"User '{username}' not found")
            response.raise_for_status()
            return response.json()
    
    async def get_user_repos(self, username: str) -> List[Dict[str, Any]]:
        """Fetch all public repositories with stars, forks, and languages"""
        repos = []
        page = 1
        per_page = 100
        
        async with httpx.AsyncClient() as client:
            while True:
                response = await client.get(
                    f"{self.base_url}/users/{username}/repos",
                    headers=self.headers,
                    params={
                        "per_page": per_page,
                        "page": page,
                        "sort": "updated",
                        "type": "owner"  # Only repos owned by the user
                    }
                )
                response.raise_for_status()
                page_repos = response.json()
                
                if not page_repos:
                    break
                
                for repo in page_repos:
                    repos.append({
                        "name": repo["name"],
                        "stars": repo["stargazers_count"],
                        "forks": repo["forks_count"],
                        "language": repo["language"],
                        "description": repo.get("description", ""),
                        "is_fork": repo["fork"],
                        "created_at": repo["created_at"],
                        "updated_at": repo["updated_at"],
                        "size": repo["size"],
                        "open_issues": repo["open_issues_count"],
                        "watchers": repo["watchers_count"],
                        "topics": repo.get("topics", [])
                    })
                
                page += 1
                if len(page_repos) < per_page:
                    break
        
        return repos
    
    async def get_pull_requests(self, username: str) -> Dict[str, Any]:
        """Fetch PR statistics - merged vs closed/rejected"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get merged PRs
            merged_response = await client.get(
                f"{self.base_url}/search/issues",
                headers=self.headers,
                params={
                    "q": f"author:{username} type:pr is:merged",
                    "per_page": 1
                }
            )
            merged_response.raise_for_status()
            merged_count = merged_response.json()["total_count"]
            
            # Get closed but not merged PRs (rejected/closed)
            closed_response = await client.get(
                f"{self.base_url}/search/issues",
                headers=self.headers,
                params={
                    "q": f"author:{username} type:pr is:closed is:unmerged",
                    "per_page": 1
                }
            )
            closed_response.raise_for_status()
            rejected_count = closed_response.json()["total_count"]
            
            # Get open PRs
            open_response = await client.get(
                f"{self.base_url}/search/issues",
                headers=self.headers,
                params={
                    "q": f"author:{username} type:pr is:open",
                    "per_page": 1
                }
            )
            open_response.raise_for_status()
            open_count = open_response.json()["total_count"]
            
            total_prs = merged_count + rejected_count + open_count
            merge_rate = (merged_count / total_prs * 100) if total_prs > 0 else 0
            
            # Get reviews given by this user (indicates seniority)
            reviews_response = await client.get(
                f"{self.base_url}/search/issues",
                headers=self.headers,
                params={
                    "q": f"reviewed-by:{username} type:pr",
                    "per_page": 1
                }
            )
            reviews_response.raise_for_status()
            reviews_given = reviews_response.json()["total_count"]
            
            # Get PRs with issue links (indicates structured development)
            prs_with_issues_response = await client.get(
                f"{self.base_url}/search/issues",
                headers=self.headers,
                params={
                    "q": f"author:{username} type:pr linked:issue",
                    "per_page": 1
                }
            )
            prs_with_issues_response.raise_for_status()
            prs_with_issue_links = prs_with_issues_response.json()["total_count"]
            
            return {
                "merged": merged_count,
                "rejected": rejected_count,
                "open": open_count,
                "total": total_prs,
                "merge_rate": round(merge_rate, 2),
                "reviews_given": reviews_given,
                "prs_with_issue_links": prs_with_issue_links,
                "review_to_pr_ratio": round(reviews_given / max(total_prs, 1), 2)
            }
    
    async def get_commit_activity(self, username: str, account_created_at: str = None) -> Dict[str, Any]:
        """Get commit activity for the last 12 months, adjusted for account age"""
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            all_commits = []
            page = 1
            max_pages = 5  # Fetch up to 500 commits to cover history better
            
            while page <= max_pages:
                try:
                    # Add small delay to respect secondary rate limits
                    if page > 1:
                        await asyncio.sleep(0.5)

                    response = await client.get(
                        f"{self.base_url}/search/commits",
                        headers={
                            **self.headers,
                            "Accept": "application/vnd.github.cloak-preview+json"
                        },
                        params={
                            "q": f"author:{username} author-date:>{start_date.strftime('%Y-%m-%d')}",
                            "per_page": 100,
                            "sort": "author-date",
                            "order": "desc",
                            "page": page
                        }
                    )
                    
                    if response.status_code == 403:
                        # Rate limit exceeded or forbidden
                        print(f"Warning: GitHub Search API rate limit hit for {username}. Stopped at page {page-1}.", flush=True)
                        break
                        
                    if response.status_code == 422: # Pagination limit exceeded
                        break
                        
                    response.raise_for_status()
                    data = response.json()
                    
                    items = data.get("items", [])
                    if not items:
                        break
                        
                    all_commits.extend(items)
                    
                    if len(items) < 100:
                        break
                        
                    page += 1
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 403:
                        print(f"Warning: GitHub API 403 for {username}. Partial data used.", flush=True)
                        break
                    raise e
                except Exception as e:
                    print(f"Warning: Error fetching commits page {page}: {e}", flush=True)
                    break
            
            total_commits = data.get("total_count", len(all_commits)) if 'data' in locals() else len(all_commits)
            commits = all_commits
            
            # Anti-gaming: Analyze commit quality
            trivial_patterns = [
                "update readme", "readme", "update md", "typo", "fix typo",
                "minor", "small fix", "formatting", "whitespace", "docs only",
                "readme.md", "documentation", "update doc", "bump version"
            ]
            
            quality_commits = 0
            trivial_commits = 0
            commit_dates = []
            
            for commit in commits:
                commit_msg = commit.get("commit", {}).get("message", "").lower()
                commit_date = commit.get("commit", {}).get("author", {}).get("date")
                
                if commit_date:
                    commit_dates.append(commit_date)
                
                # Check if commit message matches trivial patterns
                is_trivial = any(pattern in commit_msg for pattern in trivial_patterns)
                
                if is_trivial:
                    trivial_commits += 1
                else:
                    quality_commits += 1
            
            # Calculate quality ratio
            quality_ratio = quality_commits / max(len(commits), 1)
            
            # Adjusted total: discount trivial commits by 50%
            adjusted_commits = quality_commits + (trivial_commits * 0.5)
            # Scale back to estimated total
            if len(commits) > 0:
                adjusted_total = int(total_commits * (adjusted_commits / len(commits)))
            else:
                adjusted_total = total_commits
            
            # Calculate monthly distribution
            monthly_commits = {}
            for date_str in commit_dates:
                try:
                    date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    month_key = date.strftime("%Y-%m")
                    monthly_commits[month_key] = monthly_commits.get(month_key, 0) + 1
                except:
                    pass
            
            # Calculate consistency index (0-100)
            # Adjust denom based on account age (don't penalize new accounts)
            max_months = 12
            if account_created_at:
                try:
                    created_date = datetime.fromisoformat(account_created_at.replace("Z", "+00:00"))
                    days_exist = (datetime.now(created_date.tzinfo) - created_date).days
                    months_exist = max(1, math.ceil(days_exist / 30))
                    max_months = min(12, months_exist)
                except:
                    pass
            
            active_months = len(monthly_commits)
            consistency_index = min(100, (active_months / max_months) * 100)
            
            # Calculate average commits per active month (using adjusted total)
            avg_commits_per_month = adjusted_total / max(1, active_months) if active_months > 0 else 0
            
            return {
                "total_commits_year": total_commits,
                "quality_commits_year": adjusted_total,  # Anti-gaming adjusted count
                "trivial_commit_ratio": round(1 - quality_ratio, 2),  # % of trivial commits
                "monthly_distribution": monthly_commits,
                "active_months": active_months,
                "max_possible_months": max_months, # Return this for context
                "consistency_index": round(consistency_index, 2),
                "avg_commits_per_month": round(avg_commits_per_month, 2)
            }
    
    async def get_repo_contributors(self, username: str, repo_name: str) -> int:
        """Get contributor count for a specific repo"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/repos/{username}/{repo_name}/contributors",
                    headers=self.headers,
                    params={"per_page": 1, "anon": "false"}
                )
                if response.status_code == 200:
                    # Check Link header for total count
                    link_header = response.headers.get("Link", "")
                    if 'rel="last"' in link_header:
                        import re
                        match = re.search(r'page=(\d+)>; rel="last"', link_header)
                        if match:
                            return int(match.group(1))
                    return len(response.json())
        except:
            pass
        return 1
    
    async def get_repo_quality_indicators(self, username: str, repo_name: str) -> Dict[str, Any]:
        """
        Check repository for quality indicators:
        - README presence and quality
        - LICENSE presence
        - Tests directory
        - CI/CD configuration
        - .gitignore presence
        """
        indicators = {
            "has_readme": False,
            "readme_length": 0,
            "has_license": False,
            "license_type": None,
            "has_tests": False,
            "has_ci_cd": False,
            "has_gitignore": False,
            "ci_cd_type": None
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Get repo root contents
                response = await client.get(
                    f"{self.base_url}/repos/{username}/{repo_name}/contents",
                    headers=self.headers
                )
                
                if response.status_code != 200:
                    return indicators
                
                contents = response.json()
                file_names = [item["name"].lower() for item in contents if item["type"] == "file"]
                dir_names = [item["name"].lower() for item in contents if item["type"] == "dir"]
                
                # Check README
                readme_files = ["readme.md", "readme.txt", "readme", "readme.rst"]
                for rf in readme_files:
                    if rf in file_names:
                        indicators["has_readme"] = True
                        # Get README size as quality indicator
                        for item in contents:
                            if item["name"].lower() == rf:
                                indicators["readme_length"] = item.get("size", 0)
                        break
                
                # Check LICENSE
                license_files = ["license", "license.md", "license.txt", "licence", "copying"]
                for lf in license_files:
                    if lf in file_names:
                        indicators["has_license"] = True
                        break
                
                # Check .gitignore
                if ".gitignore" in file_names:
                    indicators["has_gitignore"] = True
                
                # Check for tests directory
                test_dirs = ["test", "tests", "__tests__", "spec", "specs", "_tests_"]
                for td in test_dirs:
                    if td in dir_names:
                        indicators["has_tests"] = True
                        break
                # Also check for test files in root
                test_files = ["test.py", "tests.py", "test.js", "pytest.ini", "jest.config.js"]
                for tf in test_files:
                    if tf in file_names:
                        indicators["has_tests"] = True
                        break
                
                # Check for CI/CD
                if ".github" in dir_names:
                    # Check for workflows
                    wf_response = await client.get(
                        f"{self.base_url}/repos/{username}/{repo_name}/contents/.github/workflows",
                        headers=self.headers
                    )
                    if wf_response.status_code == 200:
                        indicators["has_ci_cd"] = True
                        indicators["ci_cd_type"] = "github_actions"
                
                # Check other CI files
                ci_files = {
                    ".travis.yml": "travis",
                    "jenkinsfile": "jenkins",
                    ".circleci": "circleci",
                    "azure-pipelines.yml": "azure",
                    ".gitlab-ci.yml": "gitlab"
                }
                for ci_file, ci_type in ci_files.items():
                    if ci_file in file_names or ci_file in dir_names:
                        indicators["has_ci_cd"] = True
                        indicators["ci_cd_type"] = ci_type
                        break
                        
        except Exception as e:
            print(f"Error checking quality indicators for {repo_name}: {e}")
        
        return indicators
    
    async def aggregate_data(self, username: str) -> Dict[str, Any]:
        """Aggregate all GitHub data for a user with enhanced metrics"""
        profile = await self.get_user_profile(username)
        repos = await self.get_user_repos(username)
        pull_requests = await self.get_pull_requests(username)
        
        # Pass created_at for accurate consistency calc
        created_at = profile.get("created_at")
        activity = await self.get_commit_activity(username, created_at)
        
        # Calculate additional metrics
        total_stars = sum(repo["stars"] for repo in repos)
        total_forks = sum(repo["forks"] for repo in repos)
        original_repos = [r for r in repos if not r["is_fork"]]
        
        # Anti-gaming: Explicit filtering for code vs doc repos
        # List of languages that count as "Code"
        code_languages = [
            'Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'C', 'C#', 
            'Go', 'Rust', 'Ruby', 'PHP', 'Swift', 'Kotlin', 'Dart', 'Shell',
            'HTML', 'CSS', 'Vue', 'Svelte', 'Lua', 'Perl', 'Scala', 'Elixir'
        ]
        
        languages = {}
        code_repo_count = 0
        doc_repo_count = 0
        
        for repo in repos:
            lang = repo["language"]
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
                # Check if it's a code language
                if lang in code_languages:
                    code_repo_count += 1
                else:
                    doc_repo_count += 1
            else:
                # No language detected usually means Markdown/Text only or empty
                doc_repo_count += 1
        
        # Enhanced metrics
        # Get contributor counts and quality indicators for top repos (sample up to 5 for performance)
        complex_repos = 0
        documented_repos = 0
        total_contributors = 0
        
        # Quality indicators counters
        real_readme_count = 0
        license_count = 0
        tests_count = 0
        ci_cd_count = 0
        
        sample_repos = sorted(repos, key=lambda x: x["stars"], reverse=True)[:5]
        
        for repo in sample_repos:
            # Check if repo has description/topics (basic documentation)
            if repo.get("description") or repo.get("topics"):
                documented_repos += 1
            
            # Get contributor count
            contributors = await self.get_repo_contributors(username, repo["name"])
            total_contributors += contributors
            if contributors >= 50:
                complex_repos += 1
                
            # Get detailed quality indicators
            indicators = await self.get_repo_quality_indicators(username, repo["name"])
            if indicators["has_readme"]:
                real_readme_count += 1
            if indicators["has_license"]:
                license_count += 1
            if indicators["has_tests"]:
                tests_count += 1
            if indicators["has_ci_cd"]:
                ci_cd_count += 1
        
        avg_contributors = total_contributors / max(len(sample_repos), 1)
        
        return {
            "username": username,
            "profile": {
                "name": profile.get("name", username),
                "bio": profile.get("bio", ""),
                "company": profile.get("company", ""),
                "location": profile.get("location", ""),
                "followers": profile.get("followers", 0),
                "following": profile.get("following", 0),
                "public_repos": profile.get("public_repos", 0),
                "created_at": profile.get("created_at", ""),
                "avatar_url": profile.get("avatar_url", "")
            },
            "repos": repos,
            "repos_summary": {
                "total": len(repos),
                "original": len(original_repos),
                "forked": len(repos) - len(original_repos),
                "code_repos": code_repo_count,
                "doc_repos": doc_repo_count,
                "total_stars": total_stars,
                "total_forks": total_forks,
                "languages": languages,
                "top_languages": sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5],
                "complex_repos": complex_repos,
                "documented_repos": documented_repos,
                "avg_contributors_per_repo": round(avg_contributors, 1),
                # New enhanced metrics
                "readme_count": real_readme_count,
                "license_count": license_count,
                "tests_count": tests_count,
                "ci_cd_count": ci_cd_count,
                "sample_size": len(sample_repos)
            },
            "pull_requests": pull_requests,
            "activity": activity
        }

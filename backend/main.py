from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.github_service import GitHubService
from services.scoring_service import calculate_base_scores
from services.ai_service import analyze_developer, combine_scores
from models.schemas import DeveloperRating, ErrorResponse
import traceback

app = FastAPI(
    title="GitRate",
    description="Evaluate a developer's GitHub profile based on Fairness-Oriented metrics",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

github_service = GitHubService()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "GitRate",
        "version": "2.0.0",
        "scoring_mode": "hybrid"
    }


@app.get("/api/health")
async def health_check():
    """API health check"""
    return {"status": "ok"}


@app.post("/api/rate/{username}", response_model=DeveloperRating)
async def rate_developer(username: str):
    """
    Rate a GitHub developer using HYBRID scoring:
    1. Fetch GitHub data
    2. Calculate deterministic BASE SCORES 
    3. Get AI QUALITATIVE analysis with context multiplier
    4. Combine for FINAL SCORE
    
    Args:
        username: GitHub username to analyze
        
    Returns:
        DeveloperRating: Comprehensive rating with scores, tier, and analysis
    """
    try:
        print(f"[API] Starting hybrid analysis for: {username}")
        
        # Step 1: Fetch GitHub data
        github_data = await github_service.aggregate_data(username)
        print(f"[API] GitHub data fetched for {username}")
        
        # Step 2: Calculate deterministic base scores
        base_scores = calculate_base_scores(github_data)
        print(f"[API] Base scores calculated: {base_scores.get('base_score')}")
        
        # Step 3: Get AI qualitative analysis (receives both raw data and base scores)
        ai_response = await analyze_developer(github_data, base_scores)
        print(f"[API] AI analysis complete, multiplier: {ai_response.context_multiplier}")
        
        # Step 4: Combine base scores with AI analysis (include profile and stats for frontend display)
        final_rating = combine_scores(base_scores, ai_response, github_data)
        print(f"[API] Final score: {final_rating.get('final_score')}, Tier: {final_rating.get('tier')}")
        
        return final_rating
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Error analyzing {username}: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to analyze user: {str(e)}"
        )


@app.get("/api/user/{username}/data")
async def get_user_data(username: str):
    """
    Get raw GitHub data for a user (useful for debugging)
    
    Args:
        username: GitHub username
        
    Returns:
        Raw aggregated GitHub data
    """
    try:
        github_data = await github_service.aggregate_data(username)
        return github_data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

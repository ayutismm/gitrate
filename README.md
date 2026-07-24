# GitRate

GitRate is an AI-powered developer evaluation platform that analyzes GitHub profiles using a hybrid scoring model. By combining deterministic statistical metrics with qualitative AI analysis, GitRate provides fair, objective, and multi-dimensional ratings for developers.

---

## Overview

Traditional developer evaluation methods often rely purely on vanity metrics such as star counts or commit heatmaps, which can easily be gamified or misrepresent developer skill. GitRate addresses this by implementing a two-pass Hybrid Scoring Architecture:

1. **Deterministic Base Scoring**: Calculates a foundational score (0 to 100) using weighted formulas applied directly to quantitative GitHub API metrics.
2. **AI Qualitative Contextual Analysis**: Evaluates soft signals (e.g., mentorship behavior, bio/company indicators, project complexity, and repository quality) using an LLM via OpenRouter. The AI generates a clamped Context Multiplier (0.8 to 1.2) that adjusts the final score.

---

## Key Features

- **Hybrid Evaluation Model**: Combines algorithmic math with contextual AI assessment to ensure balanced and fair profile ratings.
- **Four Core Assessment Dimensions**:
  - **Contribution Score**: Tracks repository creation, commit volume, activity consistency, and active months relative to account age.
  - **PR Quality & Collaboration Score**: Analyzes pull request merge rates, reviews given to peers, and issue-linkage practices. Solo developers are protected with a fair baseline score.
  - **Impact & Community Reach**: Measures project stars, forks, followers, and average contributor engagement.
  - **Code & Repository Quality**: Evaluates language diversity, project complexity, documentation (README presence), testing, licensing, and CI/CD adoption.
- **Anti-Gaming Protections**: Differentiates between actual code repositories and documentation/empty repos. Uses quality-adjusted commit tracking.
- **Developer Tier Classification**: Groups developer scores into four distinct tiers: Beginner, Intermediate, Advanced, and Elite.
- **Side-by-Side Profile Comparison**: Allows users to save developer profiles locally and compare their metrics side by side.
- **Mock Mode Support**: Runs full evaluations offline without requiring external GitHub or AI API keys for local development and UI testing.
- **Vercel Serverless Ready**: Architected for lightweight deployment on Vercel as a serverless Python FastAPI backend paired with a Vite React frontend.

---

## Architecture & System Design

```
+-----------------------------------------------------------------------+
|                             React Frontend                            |
|                  (Vite + TailwindCSS + Lucide Icons)                  |
+-----------------------------------------------------------------------+
                                   |
                                   | HTTP POST /api/rate/{username}
                                   v
+-----------------------------------------------------------------------+
|                            FastAPI Backend                            |
+-----------------------------------------------------------------------+
          |                                             |
          | 1. Fetch User Data                          | 3. Send Metrics + Base Score
          v                                             v
+------------------------+                     +------------------------+
|     GitHub API v3      |                     |    OpenRouter AI API   |
| (REST / Search Params) |                     | (Gemini / LLM Service) |
+------------------------+                     +------------------------+
          |                                             |
          | 2. Raw Metrics                              | 4. Context Multiplier
          +---------------------> + <-------------------+    (0.8 - 1.2 Range)
                                  |
                                  v
                       +--------------------+
                       |  Final Score &     |
                       |  Tier Generation   |
                       +--------------------+
```

---

## Scoring Methodology

### Base Score Formula

The deterministic base score is calculated from four primary weighted categories:

`Base Score = (0.30 * Contribution) + (0.25 * PR Quality) + (0.15 * Impact) + (0.30 * Code Quality)`

| Metric Category | Weight | Key Factors Evaluated |
|---|---|---|
| Contribution | 30% | Code vs. doc repo ratio, quality commit count (logarithmic curve), activity consistency index, active months ratio |
| PR Quality | 25% | Merge rate, code reviews given (seniority indicator), issue linkage ratio, participation volume |
| Impact | 15% | Star count (logarithmic), fork count, follower count, average contributor count per repository |
| Code Quality | 30% | Programming language diversity, repository complexity, README presence, unit test detection, CI/CD setup, license inclusion |

### Final Score Formula

The AI model evaluates qualitative indicators and outputs a **Context Multiplier** bounded strictly between `0.8` and `1.2`.

`Final Score = min(100.0, max(0.0, Base Score * Context Multiplier))`

### Tier Classifications

- **Elite**: 85.0 to 100.0
- **Advanced**: 70.0 to 84.9
- **Intermediate**: 50.0 to 69.9
- **Beginner**: 0.0 to 49.9

---

## Repository Structure

```
GITRATE/
|-- api/
|   |-- index.py             # Vercel Serverless Function entry point
|   `-- requirements.txt     # Python requirements for Vercel deployment
|-- backend/
|   |-- main.py              # FastAPI application server
|   |-- config.py            # Environment configuration loader
|   |-- requirements.txt     # Backend dependencies
|   |-- models/
|   |   `-- schemas.py       # Pydantic data schemas for API responses
|   `-- services/
|       |-- github_service.py # GitHub REST API aggregation service
|       |-- scoring_service.py# Deterministic scoring calculation engine
|       `-- ai_service.py    # OpenRouter LLM qualitative evaluation service
|-- frontend2/
|   |-- src/
|   |   |-- components/
|   |   |   |-- Dashboard.jsx     # Main evaluation visualization board
|   |   |   |-- CompareView.jsx   # Side-by-side developer comparison view
|   |   |   |-- SavedProfiles.jsx # Saved profiles manager
|   |   |   |-- SearchBar.jsx     # Profile search input component
|   |   |   |-- AnalysisCards.jsx # Detailed breakdown cards
|   |   |   `-- LoadingState.jsx  # Skeletal loading spinner state
|   |   |-- services/
|   |   |   |-- api.js            # Frontend HTTP client service
|   |   |   `-- storage.js        # LocalStorage state management
|   |   |-- App.jsx               # Main React Application component
|   |   |-- main.jsx              # React DOM entry point
|   |   `-- index.css             # Tailwind CSS configuration
|   |-- package.json         # Frontend dependencies and scripts
|   |-- vite.config.js       # Vite bundler configuration
|   `-- tailwind.config.js   # Tailwind framework setup
|-- vercel.json              # Vercel deployment routing and configuration
|-- PROJECT_DOCS.md          # Internal project specifications
`-- README.md                # Project documentation
```

---

## Environment Variables

Create a `.env` file in the `backend/` directory or root environment with the following keys:

```env
GITHUB_TOKEN=your_github_personal_access_token
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=google/gemini-2.0-flash-001
MOCK_MODE=false
```

| Variable Name | Required | Default Value | Description |
|---|---|---|---|
| `GITHUB_TOKEN` | Optional | `""` | GitHub Personal Access Token to increase API rate limits from 60 to 5000 requests/hr. |
| `OPENROUTER_API_KEY` | Optional | `""` | OpenRouter API Key used for qualitative AI profile analysis. |
| `OPENROUTER_MODEL` | Optional | `google/gemini-2.0-flash-001` | LLM model identifier on OpenRouter. |
| `MOCK_MODE` | Optional | `false` | Set to `true` to return simulated API data without making external network calls. |

---

## Local Development Setup

### Prerequisites

- **Python**: Version 3.9 or higher
- **Node.js**: Version 18.0 or higher
- **npm**: Package manager (comes with Node.js)

### Step 1: Clone the Repository

```bash
git clone https://github.com/ayutismm/gitrate.git
cd gitrate
```

### Step 2: Set Up Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the backend development server:
   ```bash
   python main.py
   ```
   The FastAPI backend will be available at `http://localhost:8000`.

### Step 3: Set Up Frontend

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend2
   ```
2. Install Node modules:
   ```bash
   npm install
   ```
3. Launch the Vite development server:
   ```bash
   npm run dev
   ```
   The React application will be available at `http://localhost:5173`.

---

## API Reference

### Health Check

```http
GET /api/health
```

**Response:**
```json
{
  "status": "ok"
}
```

---

### Rate Developer

```http
POST /api/rate/{username}
```

**Parameters:**
- `username` *(path parameter, string, required)*: GitHub username to evaluate.

**Response Example:**
```json
{
  "contribution_score": 78.5,
  "pr_quality_score": 65.0,
  "impact_score": 42.0,
  "code_quality_score": 80.0,
  "base_score": 70.3,
  "context_multiplier": 1.05,
  "final_score": 73.8,
  "tier": "Advanced",
  "strengths": [
    "Active contributor with 14 original repositories",
    "Given 12 code reviews to other developers",
    "Uses 6 different programming languages"
  ],
  "weaknesses": [
    "Could increase PR-to-issue linkage for traceability",
    "Consider contributing to more multi-contributor projects"
  ],
  "detailed_analysis": {
    "contribution_analysis": "Demonstrates consistent contribution patterns with high activity across code repositories.",
    "pr_analysis": "Shows collaborative behavior with active pull request submissions and peer reviews.",
    "impact_analysis": "Maintains a steady community presence with growing repository stars and forks.",
    "code_quality_analysis": "Maintains clean project organization with good documentation and multi-language usage."
  },
  "summary": "Solid developer demonstrating reliable coding practices and steady community involvement."
}
```

---

### Raw User Data

```http
GET /api/user/{username}/data
```

**Parameters:**
- `username` *(path parameter, string, required)*: GitHub username.

**Response:**
Returns raw aggregated GitHub statistics including repository counts, commit activity, pull requests, and languages.

---

## Deployment Guide

GitRate is structured to be deployed directly to Vercel.

1. Install the Vercel CLI or connect your repository to Vercel via GitHub integration.
2. Ensure `vercel.json` in the root directory specifies:
   - Python runtime (`api/index.py`) for backend serverless routes (`/api/*`).
   - Static build (`frontend2/package.json`) for client routes.
3. Configure the environment variables (`GITHUB_TOKEN`, `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`) in the Vercel Project Settings.
4. Trigger the deployment.

---

## Tech Stack Summary

- **Frontend**: React 19, Vite, Tailwind CSS, Lucide Icons, LocalStorage API
- **Backend**: FastAPI, Uvicorn, HTTPX Async Client, Pydantic v2
- **AI Integration**: OpenRouter API (Gemini / Custom LLM models)
- **Deployment**: Vercel Serverless Functions

---

## License

This project is open source and available under the [MIT License](LICENSE).

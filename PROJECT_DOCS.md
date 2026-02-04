# GitRate - Project Documentation

## 🚀 Overview
**GitRate** is an AI-powered application that evaluates developer profiles on GitHub. It uses a **Hybrid Scoring System** combining:
- **Deterministic Base Scores**: Calculated in Python from real metrics.
- **AI Qualitative Analysis**: Provides a context multiplier based on soft signals.

---

## 🏗️ Architecture (v2.0 - Hybrid Scoring)

### 1. **Frontend (Client)**
- **Tech Stack**: React.js (Vite), TailwindCSS.
- **Role**: Handles user interaction, displays the dashboard.
- **Design**: Minimalist dark theme.

### 2. **Backend (Server)**
- **Tech Stack**: Python (FastAPI), Uvicorn.
- **Key Services**:
  - `github_service.py`: Fetches data from GitHub API.
  - `scoring_service.py`: **[NEW]** Calculates deterministic base scores.
  - `ai_service.py`: Gets qualitative analysis + context multiplier from AI.

---

## 🔄 How It Works (Hybrid Scoring Flow)

### Step 1: Fetch GitHub Data
`github_service.py` queries multiple endpoints:
- Profile, Repos, Commits, PRs
- **NEW**: Reviews given, PR-to-Issue linkage, Contributor counts

### Step 2: Calculate Base Scores (Deterministic)
`scoring_service.py` uses weighted formulas:

| Score | Weight | Factors |
|-------|--------|---------|
| Contribution | 40% | Repos, Commits, Consistency |
| PR Quality | 30% | Merge Rate, Reviews Given, Issue Linkage |
| Impact | 20% | Stars, Forks, Followers |
| Code Quality | 10% | Language Diversity, Complexity |

```
Base Score = 0.4(Contribution) + 0.3(PR Quality) + 0.2(Impact) + 0.1(Code Quality)
```

### Step 3: AI Qualitative Analysis
`ai_service.py` sends both **raw data AND base scores** to the AI.
The AI provides:
- **Context Multiplier** (0.8 to 1.2): Adjusts based on soft signals.
- **Qualitative Notes**: Analysis of bio, company, mentorship indicators.
- **Strengths/Weaknesses**: Based on qualitative observation.

### Step 4: Final Score Calculation
```
Final Score = Base Score × Context Multiplier
```

Example:
- Base Score: 72
- Context Multiplier: 1.1 (positive soft signals)
- **Final Score: 79.2**

---

## ⚙️ Configuration (`.env`)

| Variable | Purpose |
|----------|---------|
| `GITHUB_TOKEN` | Access to GitHub API. |
| `OPENROUTER_API_KEY` | Access to AI models via OpenRouter. |
| `OPENROUTER_MODEL` | AI model to use (e.g., `tngtech/deepseek-r1t-chimera:free`). |
| `MOCK_MODE` | If `true`, bypasses APIs for UI testing. |

---

## �️ Guardrails

1. **Temperature 0**: AI responses are deterministic.
2. **Pydantic Validation**: Strict schema for AI response parsing.
3. **Context Multiplier Bounds**: Clamped to 0.8–1.2 range.
4. **Retry Logic**: Exponential backoff on API failures.

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `services/scoring_service.py` | Deterministic score calculation |
| `services/github_service.py` | GitHub API data fetching |
| `services/ai_service.py` | Qualitative AI analysis |
| `main.py` | API orchestration |
| `models/schemas.py` | Pydantic response models |

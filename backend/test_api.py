import asyncio
import json
import re
from dotenv import load_dotenv
import os

load_dotenv()

import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Test prompt
prompt = """Analyze this GitHub profile and return ONLY a JSON response:

Username: octocat
Followers: 5000
Repos: 8
Stars: 1000
PRs Merged: 50

Return this EXACT JSON format (numbers can vary):
{
  "contribution_score": 50,
  "pr_quality_score": 60,
  "impact_score": 70,
  "code_quality_score": 55,
  "final_score": 58,
  "tier": "Intermediate",
  "strengths": ["Good activity", "Popular repos"],
  "weaknesses": ["Could contribute more"],
  "detailed_analysis": {
    "contribution_analysis": "The developer has moderate activity",
    "pr_analysis": "Good PR history",
    "impact_analysis": "Significant community impact",
    "code_quality_analysis": "Decent code quality"
  },
  "summary": "A solid intermediate developer with good community impact."
}"""

print("Sending request to Gemini...")
model = genai.GenerativeModel('gemini-2.5-flash')
response = model.generate_content(prompt)

print("\n=== RAW RESPONSE ===")
print(response.text)
print("\n=== END RAW RESPONSE ===")

# Try to parse
response_text = response.text.strip()
if "```json" in response_text:
    response_text = response_text.split("```json")[1]
if "```" in response_text:
    response_text = response_text.split("```")[0]

json_match = re.search(r'\{[\s\S]*\}', response_text)
if json_match:
    response_text = json_match.group()

print("\n=== CLEANED FOR JSON ===")
print(response_text[:500])
print("\n=== PARSE ATTEMPT ===")
try:
    data = json.loads(response_text)
    print("SUCCESS!")
    print(f"Final Score: {data.get('final_score')}")
except Exception as e:
    print(f"FAILED: {e}")

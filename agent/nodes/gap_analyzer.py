import os
import json
import anthropic
from dotenv import load_dotenv
from agent.state import AgentState

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def run(state: AgentState) -> AgentState:
    print("[gap_analyzer] Analyzing skill gap...")
    prompt = f"""You are a technical recruiter AI. Compare this job description with the candidate resume.

Job Description:
{state.job_description[:3000]}

Candidate Resume:
{state.resume_text[:3000]}

Return ONLY valid JSON in this exact structure, no markdown, no explanation:
{{
  "match_score": <number 0-100>,
  "matched_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "strong_points": ["point1", "point2"],
  "improvement_areas": ["area1", "area2"]
}}"""

    try:
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = message.content[0].text.strip()
        clean = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean)

        state.skill_gap_score = float(result.get("match_score", 0))
        state.missing_skills = result.get("missing_skills", [])
        state.matched_skills = result.get("matched_skills", [])
        state.gap_analysis = result
        print(f"[gap_analyzer] Match score: {state.skill_gap_score}%")
    except Exception as e:
        print(f"[gap_analyzer] Exception: {e}")
        state.skill_gap_score = 0.0
        state.gap_analysis = {"error": str(e)}
    return state
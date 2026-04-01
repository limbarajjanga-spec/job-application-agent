import os
import anthropic
from dotenv import load_dotenv
from agent.state import AgentState

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def run(state: AgentState) -> AgentState:
    print("[cover_letter] Writing cover letter...")
    prompt = f"""Write a compelling, concise cover letter for this job application.

Rules:
- Exactly 3 paragraphs
- Paragraph 1: specific hook — reference the company or role directly, do NOT start with "I am applying"
- Paragraph 2: connect top 2-3 candidate achievements to the role's core needs
- Paragraph 3: confident, specific call to action
- Tone: professional but human, not robotic
- Do NOT mention skills the candidate is missing
- Do NOT include address block or date

Job Description:
{state.job_description[:2000]}

Candidate Strengths:
{state.gap_analysis.get("strong_points", [])}

Matched Skills:
{state.matched_skills}

Tailored Resume Summary:
{state.tailored_resume[:1500] if state.tailored_resume else "Not available"}

Output only the cover letter text:"""

    try:
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        state.cover_letter = message.content[0].text.strip()
        print(f"[cover_letter] Done. {len(state.cover_letter)} chars")
    except Exception as e:
        state.cover_letter = f"Cover letter error: {str(e)}"
        print(f"[cover_letter] Exception: {e}")
    return state
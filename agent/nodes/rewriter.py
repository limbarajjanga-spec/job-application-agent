import os
import anthropic
from dotenv import load_dotenv
from agent.state import AgentState

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def run(state: AgentState) -> AgentState:
    print("[rewriter] Rewriting resume...")
    prompt = f"""You are an expert resume writer. Rewrite the candidate's resume to better match this job.

Rules:
- Keep all real experience — do NOT invent anything
- Rewrite bullet points to use keywords from the job description
- Emphasize skills that match: {state.matched_skills}
- Naturally address gaps where possible: {state.missing_skills}
- Output clean markdown resume only, no commentary

Job Description:
{state.job_description[:2000]}

Current Resume:
{state.resume_text[:3000]}

Output the full tailored resume in markdown:"""

    try:
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        state.tailored_resume = message.content[0].text.strip()
        print(f"[rewriter] Done. {len(state.tailored_resume)} chars")
    except Exception as e:
        state.tailored_resume = f"Rewrite error: {str(e)}"
        print(f"[rewriter] Exception: {e}")
    return state
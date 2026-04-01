import fitz
from agent.state import AgentState

def run(state: AgentState) -> AgentState:
    print(f"[parser] Parsing resume: {state.resume_path}")
    try:
        doc = fitz.open(state.resume_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        state.resume_text = text.strip()
        print(f"[parser] Extracted {len(state.resume_text)} chars")
    except Exception as e:
        state.resume_text = f"Parse error: {str(e)}"
        print(f"[parser] Exception: {e}")
    return state
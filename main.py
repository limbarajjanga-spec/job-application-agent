import os
import sys
from dotenv import load_dotenv
from agent.orchestrator import build_graph
from agent.state import AgentState

load_dotenv()

def main():
    print("\n=== AI Job Application Agent ===\n")

    job_url = input("Paste job posting URL: ").strip()
    resume_path = input("Paste path to your resume PDF: ").strip()

    if not os.path.exists(resume_path):
        print(f"ERROR: Resume file not found at: {resume_path}")
        sys.exit(1)

    state = AgentState(job_url=job_url, resume_path=resume_path)
    graph = build_graph()

    print("\nRunning agent pipeline...\n")
    final_state = graph.invoke(state)

    print("\n=== AGENT COMPLETE ===")
    print(f"Match Score    : {final_state.skill_gap_score}%")
    print(f"Matched Skills : {final_state.matched_skills}")
    print(f"Missing Skills : {final_state.missing_skills}")
    print(f"Submit Status  : {final_state.submit_status}")

    with open("output_resume.md", "w") as f:
        f.write(final_state.tailored_resume or "")
    with open("output_cover_letter.txt", "w") as f:
        f.write(final_state.cover_letter or "")

    print("\nSaved: output_resume.md + output_cover_letter.txt")

if __name__ == "__main__":
    main()
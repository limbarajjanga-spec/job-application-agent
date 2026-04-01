import os
import sys
import shutil
import tempfile
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent.orchestrator import build_graph
from agent.state import AgentState

st.set_page_config(page_title="AI Job Application Agent", layout="wide")

st.title("AI Job Application Agent")
st.caption("Claude + LangGraph + Firecrawl MCP + Browser MCP")

with st.sidebar:
    st.header("Pipeline steps")
    for step in [
        "1. Scrape job posting (Firecrawl)",
        "2. Parse your resume (PyMuPDF)",
        "3. Score skill gap (Claude)",
        "4. Rewrite resume bullets (Claude)",
        "5. Write cover letter (Claude)",
        "6. You approve",
        "7. Auto-fill form (Browser MCP)",
    ]:
        st.markdown(f"- {step}")
    st.divider()
    st.markdown("**Get API keys:**")
    st.markdown("[Anthropic Console](https://console.anthropic.com)")
    st.markdown("[Firecrawl](https://firecrawl.dev)")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("Input")
    job_url = st.text_input(
        "Job posting URL",
        placeholder="https://boards.greenhouse.io/company/jobs/123456"
    )

    st.markdown("**Paste job description** *(required for LinkedIn / Indeed — they block scrapers)*")
    manual_jd = st.text_area(
        "Job description text",
        placeholder="Copy and paste the full job description here...",
        height=200,
        label_visibility="collapsed"
    )

    resume_file = st.file_uploader("Upload resume PDF", type=["pdf"])
    run_btn = st.button("Run Agent", type="primary", use_container_width=True)

if "final_state" not in st.session_state:
    st.session_state.final_state = None
if "resume_stable_path" not in st.session_state:
    st.session_state.resume_stable_path = None

if run_btn:
    if not job_url:
        st.error("Please provide a job posting URL.")
        st.stop()
    if not resume_file:
        st.error("Please upload your resume PDF.")
        st.stop()
    if not manual_jd.strip():
        st.warning("No job description pasted. Will attempt to scrape the URL (may fail for LinkedIn/Indeed).")

    # Save resume to a stable path that survives the full session
    stable_dir = tempfile.mkdtemp()
    stable_path = os.path.join(stable_dir, "resume.pdf")
    resume_bytes = resume_file.read()
    with open(stable_path, "wb") as f:
        f.write(resume_bytes)
    st.session_state.resume_stable_path = stable_path

    initial_jd = manual_jd.strip() if manual_jd.strip() else None
    state = AgentState(
        job_url=job_url,
        resume_path=stable_path,
        job_description=initial_jd
    )
    graph = build_graph()

    with col2:
        st.subheader("Progress")
        steps = [
            ("scrape_jd",      "Loading job description..."),
            ("parse_resume",   "Parsing resume PDF..."),
            ("analyze_gap",    "Scoring skill gap with Claude..."),
            ("rewrite_resume", "Rewriting resume bullets..."),
            ("write_cover",    "Writing cover letter..."),
            ("human_gate",     "Finalizing..."),
        ]
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Keep a running merged state dict across all events
            running_dict = state.model_dump()

            for event in graph.stream(state):
                node_name = list(event.keys())[0]
                node_output = list(event.values())[0]

                # Update progress bar
                for i, (n, label) in enumerate(steps):
                    if n == node_name:
                        progress_bar.progress(int((i + 1) / len(steps) * 100))
                        status_text.info(f"Step {i+1}/{len(steps)}: {label}")

                # Merge node output into running state
                if isinstance(node_output, dict):
                    running_dict.update(node_output)
                elif isinstance(node_output, AgentState):
                    running_dict.update(node_output.model_dump())

            # Build final AgentState from merged dict
            # Remove any keys not in AgentState to avoid Pydantic errors
            valid_keys = AgentState.model_fields.keys()
            clean_dict = {k: v for k, v in running_dict.items() if k in valid_keys}
            final_state = AgentState(**clean_dict)

            if final_state.job_description == "__MANUAL_REQUIRED__":
                progress_bar.empty()
                status_text.error(
                    "Could not scrape this URL. "
                    "Please paste the job description text and run again."
                )
            else:
                progress_bar.progress(100)
                status_text.success("Pipeline complete!")
                st.session_state.final_state = final_state

        except Exception as e:
            st.error(f"Agent error: {str(e)}")
            st.exception(e)


if st.session_state.final_state:
    fs = st.session_state.final_state
    st.divider()

    # Match score banner
    score = fs.skill_gap_score or 0
    if score >= 70:
        st.success(f"Strong match: {score:.0f}% — Great fit for this role.")
    elif score >= 50:
        st.warning(f"Moderate match: {score:.0f}% — Consider upskilling in missing areas.")
    else:
        st.error(
            f"Low match: {score:.0f}% — Significant gaps detected. "
            "You can still apply but tailor your narrative carefully."
        )

    tab1, tab2, tab3 = st.tabs(["Skill gap analysis", "Tailored resume", "Cover letter"])

    with tab1:
        color = "green" if score >= 70 else "orange" if score >= 50 else "red"
        st.markdown(f"### Match score: :{color}[{score:.0f}%]")
        st.progress(int(score) / 100)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Matched skills**")
            matched = fs.gap_analysis.get("matched_skills", [])
            if matched:
                for s in matched:
                    st.markdown(f"- {s}")
            else:
                st.caption("None detected")
        with c2:
            st.markdown("**Missing skills**")
            missing = fs.gap_analysis.get("missing_skills", [])
            if missing:
                for s in missing:
                    st.markdown(f"- {s}")
            else:
                st.caption("No gaps found")

        strong = fs.gap_analysis.get("strong_points", [])
        if strong:
            st.markdown("**Strong points to highlight**")
            for p in strong:
                st.markdown(f"- {p}")

        improve = fs.gap_analysis.get("improvement_areas", [])
        if improve:
            st.markdown("**Areas to address in your narrative**")
            for a in improve:
                st.markdown(f"- {a}")

    with tab2:
        st.markdown(fs.tailored_resume or "")
        st.download_button(
            "Download tailored resume (.md)",
            fs.tailored_resume or "",
            file_name="tailored_resume.md",
            mime="text/markdown",
            use_container_width=True
        )

    with tab3:
        st.markdown(fs.cover_letter or "")
        st.download_button(
            "Download cover letter (.txt)",
            fs.cover_letter or "",
            file_name="cover_letter.txt",
            mime="text/plain",
            use_container_width=True
        )

    st.divider()
    st.subheader("Submit application")

    if score < 40:
        st.error(
            "Match score below 40%. Strongly recommend improving skills before submitting. "
            "You can still proceed if you wish."
        )

    st.info(
        "The browser will open and auto-fill the form using your details. "
        "You review and click Submit manually — the agent never submits without you."
    )

    if st.button("Approve and auto-fill form", type="primary", use_container_width=True):
        with st.spinner("Opening browser and filling form..."):
            try:
                from agent.nodes.submitter import run
                fs.resume_path = st.session_state.resume_stable_path or fs.resume_path
                fs.human_approved = True
                updated = run(fs)
                st.session_state.final_state = updated
                st.success(updated.submit_status or "Form filled!")
                st.info("Check the browser window — review and click Submit when ready.")
            except Exception as e:
                st.error(f"Submitter error: {str(e)}")
                st.exception(e)
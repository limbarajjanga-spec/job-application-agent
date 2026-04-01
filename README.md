# AI Job Application Agent

Agentic AI pipeline that scrapes job postings, scores your resume match,
rewrites it for the role, and auto-fills the application form.

**Stack:** Claude API · LangGraph · Firecrawl · Browser MCP · Streamlit

## Setup
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

Add your keys to `.env`:
```
ANTHROPIC_API_KEY=...
FIRECRAWL_API_KEY=...
```

## Run

CLI mode:
```bash
python main.py
```

Streamlit UI:
```bash
streamlit run ui/app.py
```

## Architecture

User Input → Orchestrator (LangGraph) → Firecrawl MCP (scrape JD)
→ PyMuPDF (parse resume) → Claude (skill gap score)
→ Claude (rewrite resume) → Claude (cover letter)
→ Human approval gate → Browser MCP (auto-fill form)
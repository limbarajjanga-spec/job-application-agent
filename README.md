# 🤖 AI Job Application Agent

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python" />
  <img src="https://img.shields.io/badge/Claude-API-orange?logo=anthropic" />
  <img src="https://img.shields.io/badge/LangGraph-Agentic-green" />
  <img src="https://img.shields.io/badge/Streamlit-UI-red?logo=streamlit" />
  <img src="https://img.shields.io/badge/Playwright-Browser-teal?logo=playwright" />
</p>

> An end-to-end agentic AI pipeline that scrapes job postings, scores your resume match, rewrites your resume for the role, generates a tailored cover letter, and auto-fills the application form — all in one click.

---

## 🎯 What It Does

| Step | Agent Node | What Happens |
|------|-----------|--------------|
| 1 | **Scraper** | Fetches job description from a URL via Firecrawl (or accepts pasted JD) |
| 2 | **Resume Parser** | Extracts full text from your uploaded PDF using PyMuPDF |
| 3 | **Gap Analyzer** | Scores your resume-to-job match (0–100%) using Claude |
| 4 | **Rewriter** | Rewrites your resume to align with the job requirements |
| 5 | **Cover Letter** | Generates a personalized, role-specific cover letter |
| 6 | **Submitter** | Opens a browser, navigates to the job URL, and auto-fills the form |

---

## 🧠 Tech Stack

| Layer | Technology |
|-------|------------|
| LLM | [Claude API](https://www.anthropic.com/) (Anthropic) |
| Agent Orchestration | [LangGraph](https://www.langchain.com/langgraph) |
| Job Scraping | [Firecrawl](https://www.firecrawl.dev/) |
| Resume Parsing | PyMuPDF |
| Browser Automation | [Playwright](https://playwright.dev/) (Sync API) |
| Frontend UI | [Streamlit](https://streamlit.io/) |
| Language | Python 3.11 |

---

## 🗂️ Project Structure

```
job-application-agent/
├── agent/
│   ├── nodes/
│   │   ├── scraper.py          # Scrapes job description from URL via Firecrawl
│   │   ├── resume_parser.py    # Extracts text from uploaded PDF (PyMuPDF)
│   │   ├── gap_analyzer.py     # Scores resume-job match % with Claude
│   │   ├── rewriter.py         # Rewrites resume tailored to job with Claude
│   │   ├── cover_letter.py     # Generates personalized cover letter with Claude
│   │   └── submitter.py        # Playwright browser auto-fill agent
│   ├── orchestrator.py         # LangGraph pipeline definition
│   └── state.py                # Shared AgentState dataclass
├── mcp/                        # MCP server integrations
├── prompts/                    # Claude prompt templates
├── ui/
│   └── app.py                  # Streamlit frontend
├── main.py                     # CLI entry point
├── requirements.txt
├── .env.example                # Environment variable template
└── README.md
```

---

## ⚙️ Agent Pipeline

```
  Job URL / Pasted JD
          │
          ▼
    ┌─────────────┐
    │   Scraper   │  ◄── Firecrawl MCP
    └──────┬──────┘
           │
           ▼
    ┌──────────────────┐
    │  Resume Parser   │  ◄── PyMuPDF (PDF → text)
    └──────┬───────────┘
           │
           ▼
    ┌──────────────────┐
    │  Gap Analyzer    │  ──► Match Score %
    └──────┬───────────┘
           │
           ▼
    ┌──────────────────┐
    │    Rewriter      │  ──► Tailored Resume
    └──────┬───────────┘
           │
           ▼
    ┌──────────────────┐
    │  Cover Letter    │  ──► Personalized Letter
    └──────┬───────────┘
           │
           ▼
    ┌──────────────────┐
    │    Submitter     │  ──► Browser Auto-fill (Playwright)
    └──────────────────┘
           │
           ▼
    👤 Human reviews & submits
```

---

## 🚀 Setup & Installation

### 1. Clone the repo
```bash
git clone https://github.com/limbarajjanga-spec/job-application-agent.git
cd job-application-agent
```

### 2. Create and activate virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Configure environment variables

Copy the example and fill in your keys:
```bash
cp .env.example .env
```

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
```

Get your keys here:
- Anthropic API → https://console.anthropic.com/
- Firecrawl API → https://www.firecrawl.dev/

---

## ▶️ Running the App

### Streamlit UI (recommended)
```bash
streamlit run ui/app.py
```
Open [http://localhost:8501](http://localhost:8501)

### CLI mode
```bash
python main.py
```

---

## 🖥️ How to Use

1. Paste a **job posting URL** or paste the **job description** text directly
2. Upload your **resume as a PDF**
3. Click **Run Agent**
4. Watch the pipeline execute — match score, rewritten resume, and cover letter appear in the UI
5. A browser window opens and **auto-fills** the application form
6. **Review the filled fields**, make any edits, and submit manually

---

## 🔒 Security Notes

- `.env` is excluded from version control via `.gitignore` — your API keys are never committed
- The browser agent does **not** auto-submit — you always review and submit manually
- Resume files are handled as temporary files and not stored permanently

---

## 🛠️ Windows Compatibility

Playwright's async API conflicts with Streamlit's event loop on Windows. This project uses **Playwright's sync API** inside a dedicated thread to work reliably on all platforms including Windows.

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 👤 Author

**Limba Raj Janga**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://www.linkedin.com/in/limbarajjanga)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?logo=github)](https://github.com/limbarajjanga-spec)
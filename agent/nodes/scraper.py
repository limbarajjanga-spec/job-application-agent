import os
import httpx
from dotenv import load_dotenv
from agent.state import AgentState

load_dotenv()

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

BLOCKED_DOMAINS = ["linkedin.com", "indeed.com", "naukri.com", "monster.com"]

def is_blocked(url: str) -> bool:
    return any(domain in url for domain in BLOCKED_DOMAINS)

def run(state: AgentState) -> AgentState:
    if getattr(state, "job_description", None) and len(state.job_description) > 100:
        print("[scraper] Using manually provided job description — skipping scrape")
        return state

    if is_blocked(state.job_url):
        print(f"[scraper] Blocked domain detected — cannot scrape {state.job_url}")
        state.job_description = "__MANUAL_REQUIRED__"
        return state

    print(f"[scraper] Scraping: {state.job_url}")
    try:
        response = httpx.post(
            "https://api.firecrawl.dev/v1/scrape",
            headers={
                "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
                "Content-Type": "application/json"
            },
            json={"url": state.job_url, "formats": ["markdown"]},
            timeout=30
        )
        data = response.json()
        if data.get("success"):
            state.job_description = data["data"]["markdown"]
            print(f"[scraper] Got {len(state.job_description)} chars")
        else:
            state.job_description = "__MANUAL_REQUIRED__"
            print(f"[scraper] Failed: {data.get('error')}")
    except Exception as e:
        state.job_description = "__MANUAL_REQUIRED__"
        print(f"[scraper] Exception: {e}")
    return state
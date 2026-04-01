import re
import threading
from agent.state import AgentState


def extract_name(text: str) -> tuple:
    lines = text.strip().split("\n")
    for line in lines[:5]:
        line = line.strip().lstrip("#").strip()
        parts = line.split()
        if 2 <= len(parts) <= 4 and all(p[0].isupper() for p in parts if p):
            return parts[0], " ".join(parts[1:])
    return "Candidate", ""


def extract_email(text: str) -> str:
    match = re.search(r"[\w.+-]+@[\w-]+\.[a-z]{2,}", text)
    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    match = re.search(r"[\+\d][\d\s\-\(\)]{8,15}", text)
    return match.group(0).strip() if match else ""


def run_playwright_in_thread(state: AgentState) -> str:
    """
    Uses Playwright's SYNC API inside a plain thread.
    This completely avoids the Windows asyncio/ProactorEventLoop issue
    that breaks async Playwright when called from Streamlit threads.
    """
    result = {"status": "", "error": ""}

    def thread_target():
        from playwright.sync_api import sync_playwright

        first_name, last_name = extract_name(state.resume_text or "")
        email = extract_email(state.resume_text or "")
        phone = extract_phone(state.resume_text or "")

        print(f"[submitter] {first_name} {last_name} | {email} | {phone}")

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False, slow_mo=600)
                page = browser.new_page()

                try:
                    page.goto(state.job_url, wait_until="domcontentloaded", timeout=30000)
                except Exception as e:
                    print(f"[submitter] Page load warning: {e}")

                fill_map = {
                    "first_name": first_name,
                    "last_name":  last_name,
                    "email":      email,
                    "phone":      phone,
                }
                selectors = {
                    "first_name": [
                        'input[name="first_name"]',
                        'input[id*="first"]',
                        'input[placeholder*="First"]',
                        'input[autocomplete="given-name"]',
                    ],
                    "last_name": [
                        'input[name="last_name"]',
                        'input[id*="last"]',
                        'input[placeholder*="Last"]',
                        'input[autocomplete="family-name"]',
                    ],
                    "email": [
                        'input[name="email"]',
                        'input[type="email"]',
                        'input[autocomplete="email"]',
                    ],
                    "phone": [
                        'input[name="phone"]',
                        'input[type="tel"]',
                        'input[autocomplete="tel"]',
                    ],
                }

                filled = []
                for field, sel_list in selectors.items():
                    for sel in sel_list:
                        try:
                            el = page.locator(sel).first
                            if el.count() > 0:
                                el.fill(fill_map[field])
                                filled.append(field)
                                print(f"[submitter] Filled: {field}")
                                break
                        except Exception:
                            continue

                # Upload resume
                try:
                    file_input = page.locator('input[type="file"]').first
                    if file_input.count() > 0:
                        file_input.set_input_files(state.resume_path)
                        filled.append("resume_file")
                        print("[submitter] Resume uploaded")
                except Exception as e:
                    print(f"[submitter] File upload skipped: {e}")

                # Cover letter
                try:
                    cl_selectors = [
                        'textarea[name="cover_letter"]',
                        'textarea[id*="cover"]',
                        'textarea[placeholder*="cover"]',
                        'textarea[placeholder*="Cover"]',
                    ]
                    for sel in cl_selectors:
                        el = page.locator(sel).first
                        if el.count() > 0:
                            el.fill(state.cover_letter or "")
                            filled.append("cover_letter")
                            print("[submitter] Cover letter filled")
                            break
                except Exception as e:
                    print(f"[submitter] Cover letter skipped: {e}")

                summary = (
                    f"Filled fields: {', '.join(filled) if filled else 'none found on this page'}. "
                    "Browser stays open — please review and submit manually."
                )
                result["status"] = summary
                print(f"[submitter] {summary}")
                print("[submitter] Keeping browser open for 30s...")
                page.wait_for_timeout(30000)
                browser.close()

        except Exception as e:
            result["error"] = str(e)
            print(f"[submitter] Thread error: {e}")

    t = threading.Thread(target=thread_target, daemon=True)
    t.start()
    t.join(timeout=60)

    if result["error"]:
        return f"Error: {result['error']}"
    return result["status"] or "Browser closed."


def run(state: AgentState) -> AgentState:
    print("[submitter] Starting browser in separate thread...")
    state.submit_status = run_playwright_in_thread(state)
    return state
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

**DrugStore Assistant AI** — a Streamlit prototype that helps store employees answer customer questions instantly by searching across local product, promotion, and policy data. The AI uses a structured triage protocol (who is it for, what complaints, since when, what's been tried) before recommending products, and generates two views: an employee-detail view with sources and internal context, and a clean customer-facing view. The Anthropic API key lives server-side in `.env` — it never ships to the browser.

## Operating Assumptions (Non-Negotiable)

- **Local dev only.** Everything runs on your laptop. No cloud deployment, no Docker, no hosted database.
- **Minimal setup.** One `pip install` + one `streamlit run` command and you're live.
- **VS Code as the workbench.** Claude Code extension is your AI pair-programmer.

## Repo State

This folder is a **starter kit**: docs, `.claude/` helpers, and synthetic data templates — no application code yet. Your first action is `/scaffold` to generate the Streamlit app structure.

## Stack

- **Frontend + Backend:** Streamlit (Python) — handles UI and server logic in one process
- **AI Provider:** Anthropic Claude API (`claude-3-5-sonnet` or `claude-3-haiku`) via the `anthropic` Python package
- **Data Layer:** Local JSON files for products, promotions, and store policies (synthetic drugstore data)
- **Session State:** Streamlit `st.session_state` for conversation history and triage flow tracking
- **Navigation:** `st.navigation` with page files for the four screens

## Target Layout

```
drugstore-assistant/
├── CLAUDE.md
├── README.md
├── .env.example
├── .env                        # ← you create (cp .env.example .env)
├── requirements.txt
├── app.py                      # Streamlit entrypoint with st.navigation
├── pages/
│   ├── 1_ask.py                # Ask screen — type or speak a question
│   ├── 2_employee_answer.py    # Employee view — detailed answer + sources
│   ├── 3_customer_view.py      # Customer-facing — clean visual layout
│   └── 4_history.py            # History/FAQ — recent questions, trending
├── services/
│   ├── ai_service.py           # Anthropic API calls, triage logic, prompt
│   ├── data_service.py         # Loads & searches product/promo/policy JSON
│   └── session_service.py      # Session state helpers, conversation history
├── data/
│   ├── products.json           # Synthetic drugstore product catalog
│   ├── promotions.json         # Active promotions with date ranges
│   └── policies.json           # Store policies (age limits, disclaimers)
├── tests/
│   ├── test_ai_service.py
│   └── test_data_service.py
├── docs/
│   ├── architecture.md
│   ├── build-guide.md
│   └── claude-code-tips.md
└── .claude/
    ├── settings.json
    ├── commands/
    │   ├── scaffold.md
    │   ├── tour.md
    │   ├── next.md
    │   └── tip.md
    └── agents/
        ├── answer-quality-reviewer.md
        └── triage-flow-reviewer.md
```

## Run Commands (Target — after `/scaffold`)

```bash
pip install -r requirements.txt
cp .env.example .env            # paste your ANTHROPIC_API_KEY
streamlit run app.py
```

## Architecture (Big Picture)

```
Employee types/speaks question
        │
        ▼
   ┌─────────┐     ┌──────────────┐     ┌──────────────┐
   │ Ask Page │────▶│  AI Service  │────▶│ Anthropic API│
   └─────────┘     │  (triage +   │     └──────┬───────┘
                    │   compose)   │◀───────────┘
                    └──────┬───────┘
                           │ searches
                    ┌──────▼───────┐
                    │ Data Service │
                    │ (JSON files) │
                    └──────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        Employee View  Customer View  History
        (sources,      (product img,  (recent Qs,
         context)       price, promo)  trending)
```

**Shared data shapes** (Python dataclasses / TypedDicts):

```python
class TriageState:
    intended_for: str | None       # Who is the product for?
    complaints: str | None         # Nature of complaints/questions
    duration: str | None           # Since when?
    prior_remedies: str | None     # Already tried something?
    complete: bool                 # All 4 answered?

class QueryResult:
    question: str
    triage: TriageState
    employee_answer: str           # Detailed with sources
    customer_answer: str           # Clean, visual-ready
    matched_products: list[dict]
    matched_promotions: list[dict]
    applicable_policies: list[dict]
    timestamp: str
```

## First-Time Setup Protocol

On startup, check for `.claude/.tour-completed`. If it does not exist, say:

> "Welcome to DrugStore Assistant AI! It looks like this is your first time here. Want me to give you a quick tour of the project? I can walk you through the docs and helpers — just say yes or run `/tour`."

After the tour, create `.claude/.tour-completed`.

## How Claude Should Help While I Build

- **Suggest plan mode** for anything non-trivial — e.g. "This touches the triage flow and the AI prompt; want me to draft a plan first?"
- **Offer the right sub-agent at the right moment:**
  - After writing or modifying the system prompt or answer-generation logic → suggest running `answer-quality-reviewer`
  - After implementing or changing the triage question flow → suggest running `triage-flow-reviewer`
- **Point at `/next`** when I seem unsure what to do next
- **State the exact run command** after any change: `streamlit run app.py`
- **Keys are server-side** — `ANTHROPIC_API_KEY` is read from `.env` via `os.environ` or `python-dotenv`, never hardcoded or exposed in Streamlit's frontend

## Working Style

- Use **type hints** on all function signatures — `def search_products(query: str) -> list[dict]:`
- **No silent errors** — catch exceptions, log them with `st.error()`, never swallow silently
- **One concern per edit** — don't mix UI changes with data-layer changes in a single step
- **Ask before deleting** — never remove a file or function without confirmation
- **Streamlit idioms** — use `st.session_state` for persistence across reruns; use `st.cache_data` for loading JSON files; use `st.columns` and `st.container` for layout
- **Keep pages thin** — pages call into `services/`; they don't contain business logic themselves
- **Synthetic data stays realistic** — Dutch drugstore products (vitamins, pain relief, skincare) with realistic prices in EUR

## Scope Boundaries (Non-Negotiable)

- **No cloud deployment** — no Streamlit Cloud, no AWS, no Docker
- **No real database** — JSON files only, no SQLite, no Postgres
- **No authentication** — no login screen, no user roles
- **No real voice input** — if we add speech, it's a stretch goal using browser audio; text input is the default
- **No real product images** — use placeholder URLs or emoji icons in the customer view

## Known Gotchas

- **Streamlit reruns the entire script on every interaction** — use `st.session_state` to persist the triage conversation state across reruns
- **Anthropic API can be slow on first call** — use `st.spinner()` to show loading state
- **JSON files must be valid** — a trailing comma will crash `json.load()`; validate after editing
- **`st.navigation` requires Streamlit ≥ 1.36** — pin the version in `requirements.txt`

## Helpers Available

- `/tour` — guided walkthrough of the project structure and key files
- `/scaffold` — generates the full app structure (pages, services, data, tests)
- `/next` — tells you the next milestone from `docs/build-guide.md`
- `/tip` — gives a Claude Code productivity tip
- `answer-quality-reviewer` — audits AI responses for data accuracy, compliance, and promo prioritization
- `triage-flow-reviewer` — audits that the four-step triage protocol is correctly implemented
- `docs/build-guide.md` — your milestone ladder
- `docs/claude-code-tips.md` — Claude Code feature cheatsheet

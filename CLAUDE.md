# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

**DrugStore Assistant AI**: a Streamlit prototype that helps store employees answer customer questions instantly by searching local product, promotion, and policy data. For symptom questions the assistant runs a triage protocol (who is it for, what complaints, since when, what has been tried) before recommending anything, applies hard safety rules in code, and produces two views: an employee view with reasoning, sources and internal context, and a clean customer-facing view. The Anthropic API key lives server-side in `.env`; it never ships to the browser.

## Operating Assumptions (Non-Negotiable)

- **Local dev only.** Everything runs on your laptop. No cloud deployment, no Docker, no hosted database.
- **Minimal setup.** One `pip install` + one `streamlit run` command and you're live.
- **VS Code as the workbench.** Claude Code extension is your AI pair-programmer.

## Repo State

Starter kit plus a working reference demo:

- `demo/index.html` is a self-contained browser demo of the intended behaviour. Open it directly, no install, no account. Its engine (question classification, triage extraction, catalog search, safety rules, promotion dates, dual-view composition) is the reference for what the Streamlit app must do. Source is `demo/template.html`; `python demo/build_demo.py` inlines `data/*.json` into it.
- No Streamlit application code yet. Run `/scaffold` to generate it, porting the demo's logic into `services/`.

## Stack

- **Frontend + Backend:** Streamlit (Python), UI and server logic in one process
- **AI Provider:** Anthropic Claude API via the `anthropic` Python package. Default model `claude-opus-5`; `claude-haiku-4-5` if a cheaper model is wanted. The model writes answer text only; it never decides what is safe to sell.
- **Data Layer:** Local JSON files for products, promotions, and store policies (synthetic drugstore data)
- **Session State:** Streamlit `st.session_state` for conversation history and triage flow tracking
- **Navigation:** `st.navigation` with page files for the four screens

## Target Layout

```
drugstore-assistant/
├── CLAUDE.md
├── README.md
├── .env.example
├── .env                        # you create (cp .env.example .env)
├── requirements.txt
├── app.py                      # Streamlit entrypoint with st.navigation
├── pages/
│   ├── 1_ask.py                # Ask screen: free-text question, then only the missing triage fields
│   ├── 2_employee_answer.py    # Employee view: answer, reasoning, safety checks, sources
│   ├── 3_customer_view.py      # Customer-facing: clean, large type, presentation mode
│   └── 4_history.py            # History: recent questions (reopenable), most asked
├── services/
│   ├── ai_service.py           # Anthropic API calls, prompt, dual-view composition
│   ├── triage_service.py       # Classification, extraction from free text, gap questions
│   ├── safety_service.py       # Age / pregnancy / tried-before blocks, escalation rules
│   ├── data_service.py         # Loads & searches product/promo/policy JSON
│   └── session_service.py      # Session state helpers, conversation history
├── data/
│   ├── products.json           # Synthetic catalog with safety fields and symptom tags
│   ├── promotions.json         # Promotions with date ranges and type
│   └── policies.json           # Store policies with keywords and customer wording
├── demo/
│   ├── index.html              # Built, shareable browser demo (reference behaviour)
│   ├── template.html           # Demo source; data placeholder inlined by build
│   └── build_demo.py           # python demo/build_demo.py
├── tests/
│   ├── test_triage_service.py
│   ├── test_safety_service.py
│   ├── test_ai_service.py
│   └── test_data_service.py
├── docs/
│   ├── architecture.md
│   ├── build-guide.md
│   └── claude-code-tips.md
└── .claude/
    ├── settings.json
    ├── commands/               # scaffold, tour, next, tip
    └── agents/                 # answer-quality-reviewer, triage-flow-reviewer
```

## Run Commands (Target, after `/scaffold`)

```bash
pip install -r requirements.txt
cp .env.example .env            # paste your ANTHROPIC_API_KEY
streamlit run app.py
python demo/build_demo.py       # rebuild the demo after editing data/*.json
```

## Triage Protocol (parse first, ask only the gaps)

1. **Classify** the question: `symptom`, `policy`, `promo`, `lookup`, or `unknown`. Only `symptom` runs triage; the others answer immediately from data.
2. **Extract** from the free text whatever is already there: `intended_for` (plus an age bucket for children), `complaints` (symptom tags from the catalog vocabulary), `duration`, `prior_remedies` (plus whether it failed and which active ingredient), pregnancy or breastfeeding.
3. **No match, no questions.** If the complaint matches nothing in the catalog, answer honestly at once: nothing suitable in the assortment, ask the pharmacist. Do not walk the customer through triage first.
4. **Ask only the missing fields**, one at a time, in this order: who, child's age, complaints, duration, prior remedies. Quick-pick chips plus free text.
5. `complete` is true when all four fields are filled. Only then search and recommend.

## Safety Rules (Non-Negotiable, enforced in code)

- **Age:** block a product when `min_age` is above the person's age, or `age_restriction` applies to a minor. Blocked means not recommended; the employee sees the reason.
- **Pregnancy or breastfeeding mentioned:** block `pregnancy_safe == false`; flag `pregnancy_safe == null` as "consult the pharmacist first". If not mentioned and the recommended product is not `pregnancy_safe == true`, remind the employee to ask.
- **Tried without effect:** never recommend the same active ingredient again.
- **Escalate before selling:** child under 6 with fever, diarrhoea or vomiting = doctor today. Complaints "al langere tijd" = doctor. Prescription medication in use = pharmacist. Failed OTC attempt = pharmacist. Fever for a week or longer = doctor.
- **Honesty:** if nothing in the data fits, say so. Never invent a product, price or promotion. A promotion never makes a product match a question it does not fit.
- The model only writes text. Search, filtering, blocking and escalation are deterministic and unit-tested.

## Architecture (Big Picture)

```
Employee types the question (free text)
        │
        ▼
 ┌──────────────┐ classify + extract   ┌──────────────┐
 │ Ask Page     │─────────────────────▶│ Triage Svc   │──▶ missing fields? ask one at a time
 └──────────────┘                      └──────┬───────┘
                                              │ complete
                                       ┌──────▼───────┐     ┌──────────────┐
                                       │ Data Service │────▶│ Safety Svc   │ block / flag / escalate
                                       │ (search)     │     └──────┬───────┘
                                       └──────────────┘            │ allowed, blocked, escalation
                                                            ┌──────▼───────┐     ┌──────────────┐
                                                            │ AI Service   │────▶│ Anthropic API│ writes text only
                                                            └──────┬───────┘     └──────────────┘
                                              ┌────────────────────┼────────────────────┐
                                              ▼                    ▼                    ▼
                                        Employee View        Customer View          History
                                   (reasoning, checks,   (short, large type,    (reopen, most asked)
                                    blocked, sources)     presentation mode)
```

**Shared data shapes** (Python dataclasses / TypedDicts):

```python
class TriageState:
    intended_for: str | None       # "mezelf" | "partner" | "kind" | "ander"
    age_bucket: str | None         # "0-5" | "6-11" | "12-17" | "volwassen"
    pregnant: bool                 # pregnancy or breastfeeding mentioned
    complaints: list[str]          # symptom tags from the catalog vocabulary
    complaint_raw: str             # free text when no tag matched
    duration: str | None           # "vandaag" | "een paar dagen" | "een week of langer" | "al langere tijd"
    prior_remedies: str | None     # "nog niets" | "iets zonder recept" | "iets op recept" | "weet niet"
    prior_failed: bool
    tried_ingredient: str | None
    complete: bool                 # all four fields answered

class QueryResult:
    question: str
    question_type: str             # symptom | policy | promo | lookup | unknown
    triage: TriageState
    recommended: dict | None
    alternatives: list[dict]       # product + why
    blocked: list[dict]            # product + reason
    checks: list[dict]             # safety checks shown to the employee
    escalation: dict               # level: none | pharmacist | doctor | urgent, reason
    matched_promotions: list[dict]
    applicable_policies: list[dict]
    employee_answer: str
    customer_answer: str
    sources: list[str]             # record ids: p001, promo002, policy003
    timestamp: str
```

## First-Time Setup Protocol

On startup, check for `.claude/.tour-completed`. If it does not exist, say:

> "Welcome to DrugStore Assistant AI! It looks like this is your first time here. Want me to give you a quick tour of the project? I can walk you through the docs and helpers, just say yes or run `/tour`."

After the tour, create `.claude/.tour-completed`.

## How Claude Should Help While I Build

- **Suggest plan mode** for anything non-trivial, e.g. "This touches the triage flow and the AI prompt; want me to draft a plan first?"
- **Offer the right sub-agent at the right moment:**
  - After writing or modifying the system prompt, answer composition or safety rules: suggest running `answer-quality-reviewer`
  - After implementing or changing classification, extraction or the gap questions: suggest running `triage-flow-reviewer`
- **Use the demo as the oracle.** When unsure how a case should behave, run it in `demo/index.html` first; the Streamlit app must match.
- **Point at `/next`** when I seem unsure what to do next
- **State the exact run command** after any change: `streamlit run app.py`
- **Keys are server-side.** `ANTHROPIC_API_KEY` is read from `.env` via `os.environ` or `python-dotenv`, never hardcoded or exposed in Streamlit's frontend

## Working Style

- Use **type hints** on all function signatures: `def search_products(query: str) -> list[dict]:`
- **No silent errors.** Catch exceptions, log them with `st.error()`, never swallow silently
- **One concern per edit.** Don't mix UI changes with data-layer changes in a single step
- **Ask before deleting.** Never remove a file or function without confirmation
- **Streamlit idioms.** Use `st.session_state` for persistence across reruns; `st.cache_data` for loading JSON files; `st.columns` and `st.container` for layout
- **Keep pages thin.** Pages call into `services/`; they don't contain business logic themselves
- **Synthetic data stays realistic.** Dutch drugstore products (vitamins, pain relief, skincare) with realistic prices in EUR, and every product carries `min_age`, `pregnancy_safe`, `active_ingredient`, `symptoms`, `usage`
- **Dutch UI.** The employees and the data are Dutch; keep all user-facing text in Dutch

## Scope Boundaries (Non-Negotiable)

- **No cloud deployment.** No Streamlit Cloud, no AWS, no Docker
- **No real database.** JSON files only, no SQLite, no Postgres
- **No authentication.** No login screen, no user roles
- **No real voice input.** If we add speech, it's a stretch goal using browser audio; text input is the default
- **No real product images.** Use placeholder URLs or emoji icons in the customer view

## Known Gotchas

- **Streamlit reruns the entire script on every interaction.** Use `st.session_state` to persist the triage conversation state across reruns
- **Anthropic API can be slow on first call.** Use `st.spinner()` to show loading state
- **JSON files must be valid.** A trailing comma will crash `json.load()`; validate after editing, then run `python demo/build_demo.py` so the demo stays in sync
- **`st.navigation` requires Streamlit >= 1.36.** Pin the version in `requirements.txt`
- **Promotions expire.** Active status is computed from `start_date` / `end_date` against today; never hardcode "valid until"

## Helpers Available

- `/tour`: guided walkthrough of the project structure and key files
- `/scaffold`: generates the full app structure (pages, services, tests), porting the demo engine
- `/next`: tells you the next milestone from `docs/build-guide.md`
- `/tip`: gives a Claude Code productivity tip
- `answer-quality-reviewer`: audits answer composition for data accuracy, hard safety blocks, promo handling and hallucination guard
- `triage-flow-reviewer`: audits classification, extraction and the gap questions
- `demo/index.html`: the reference behaviour, shareable as a single file
- `docs/build-guide.md`: your milestone ladder
- `docs/claude-code-tips.md`: Claude Code feature cheatsheet

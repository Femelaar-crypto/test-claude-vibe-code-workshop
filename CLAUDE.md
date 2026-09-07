# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

**DrugStore Assistant AI**: a Streamlit prototype that helps store employees answer customer questions instantly by searching local product, promotion, and policy data. For symptom questions the assistant runs a triage protocol (who is it for, what complaints, since when, what has been tried) before recommending anything, applies hard safety rules in code, and produces two views: an employee view with reasoning, sources and internal context, and a clean customer-facing view. Every answer is also logged as an anonymous, structured row so the store learns what customers ask, for whom, and what happened. The Anthropic API key lives server-side in `.env`; it never ships to the browser.

## Operating Assumptions (Non-Negotiable)

- **Local dev only.** Everything runs on your laptop. No cloud deployment, no Docker, no hosted database.
- **Minimal setup.** One `pip install` + one `streamlit run` command and you're live.
- **VS Code as the workbench.** Claude Code extension is your AI pair-programmer.

## Repo State

Starter kit plus a working reference demo:

- `demo/index.html` is a self-contained browser demo of the intended behaviour. Open it directly, no install, no account. Its engine (question classification, triage extraction, catalog search, safety rules, promotion dates, dual-view composition, analytics) is the reference for what the Streamlit app must do. Source is `demo/template.html`; `python demo/build_demo.py` inlines `data/*.json` into it.
- No Streamlit application code yet. Run `/scaffold` to generate it, porting the demo's logic into `services/`.

## Stack

- **Frontend + Backend:** Streamlit (Python), UI and server logic in one process
- **AI Provider:** Anthropic Claude API via the `anthropic` Python package. Default model `claude-opus-5`; `claude-haiku-4-5` if a cheaper model is wanted. The model writes answer text only; it never decides what is safe to sell. Put the system prompt and the catalog context first in the request with `cache_control` so repeated questions hit the prompt cache.
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
│   ├── 1_ask.py                # Ask: free-text question, then only the missing triage fields
│   ├── 2_employee_answer.py    # Employee view: answer, reasoning, safety checks, sources
│   ├── 3_customer_view.py      # Customer-facing: clean, large type, presentation mode
│   └── 4_history.py            # History: reopenable questions + Inzichten (analytics sub-tabs)
├── services/
│   ├── ai_service.py           # Anthropic API calls, prompt, dual-view composition, degraded mode
│   ├── triage_service.py       # Classification, extraction from free text, gap questions
│   ├── safety_service.py       # Age / pregnancy / tried-before blocks, escalation rules
│   ├── analytics_service.py    # Structured log rows, standard categories, aggregations, CSV export
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
│   ├── test_analytics_service.py
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

**Targets:** a typical typed question needs at most two follow-up questions. Simulated answers appear within a second; live answers within five seconds, with a visible loading state.

## Safety Rules (Non-Negotiable, enforced in code)

- **Age:** block a product when `min_age` is above the person's age, or `age_restriction` applies to a minor. Blocked means not recommended; the employee sees the reason.
- **Pregnancy or breastfeeding mentioned:** block `pregnancy_safe == false`; flag `pregnancy_safe == null` as "consult the pharmacist first". If not mentioned and the recommended product is not `pregnancy_safe == true`, remind the employee to ask.
- **Tried without effect:** never recommend the same active ingredient again.
- **Escalate before selling:** child under 6 with fever, diarrhoea or vomiting = doctor today. Complaints "al langere tijd" = doctor. Prescription medication in use = pharmacist. Failed OTC attempt = pharmacist. Fever for a week or longer = doctor.
- **Honesty:** if nothing in the data fits, say so. Never invent a product, price or promotion. A promotion never makes a product match a question it does not fit.
- The model only writes text. Search, filtering, blocking and escalation are deterministic and unit-tested.

## Degraded Mode

If the Anthropic API is unavailable, slow, or refuses, the app composes both answers from templates (as the demo's simulated mode does) and labels them as such. The employee is never left without an answer because the model is down. Log the failure with `st.error()`; do not retry silently more than once.

## Analytics ("Inzichten" on the History page)

Purpose: the store learns what customers ask, for whom, and what happened, without storing personal data. Every `QueryResult` produces one structured **log row**:

| Field | Values |
|---|---|
| `at` | ISO timestamp |
| `store_id` | from config, optional |
| `question_type` | `symptom`, `policy`, `promo`, `lookup`, `unknown` |
| `category` | one **standard category** (below) |
| `complaints` | symptom tags |
| `audience` | `intended_for` + `age_bucket`; `pregnant` flag |
| `duration`, `prior_remedies` | as in `TriageState` |
| `outcome` | `recommended`, `blocked` (no safe product), `no_match` (not in assortment), `answered` (policy/promo/lookup), `unknown` |
| `escalation` | `none`, `pharmacist`, `doctor`, `urgent` |
| `recommended_id`, `blocked_ids`, `promo_id` | record ids |
| `assortment_gap` | the complaint term when `outcome == no_match` (purchasing signal) |

`assortment_gap` is the only field derived from free text, because purchasing needs the word the customer used. Bound it: lowercase, letters and digits only, at most four words and 40 characters, otherwise write `overig`. A sentence must never reach the log.

**Standard categories** are the product categories in `products.json` (Pijnstillers, Vitamines & Supplementen, Verkoudheid & Griep, Slaap, Stoppen met Roken, Huidverzorging, Eerste Hulp, Maag & Darm) plus four fixed ones for non-product questions: Beleid, Acties, Product opzoeken, Overig. A symptom question gets the category of the recommended product, else of the best candidate, else Overig.

**The dashboard is one linked view, not separate tabs.** Every panel filters every other panel, so a question like "who are the people asking about hoofdpijn" is answered by clicking, not by reading two lists side by side.

- **Period control**: 7 / 30 / 60 days, applied before anything else.
- **Filter bar**: the active selection as removable chips, plus "Alles wissen". Filters combine with AND across dimensions.
- **KPI strip**: questions in the selection, referral rate, not-in-assortment rate, promotion rate. When a filter is active each rate also shows its difference in percentage points against the period average, so the selection is always read against a baseline.
- **Klacht × doelgroep matrix**: the cross-reference centrepiece. Cell intensity is one green ramp (light to dark) on count; the number is always printed, so colour never carries meaning alone. Clicking a cell sets both filters at once. Row totals on the right.
- **"Opvallend aan deze selectie"**: over-representation (lift) of every attribute in the selection against the period average, ranked, e.g. "2.3× Klant zelf, 61% van deze selectie". Only shown at eight or more rows and three or more occurrences, so a handful of questions never produces a confident-looking claim.
- **Linked panels**: Klachten, Doelgroep, Uitkomst, Doorverwijzing, Categorie, Sinds wanneer. Each bar shows the selection as a filled portion inside the period total, so subset and baseline are visible at once. A panel never filters itself, so switching value within a dimension stays possible.
- **Gevraagd, niet in assortiment**: the assortment gaps, framed as the purchasing list.

CSV export always exports exactly the current filtered selection, not everything.

**Charts follow one rule set:** one hue for magnitude, count printed next to every bar, no pie charts, no second y-axis, and the whole dashboard readable as text if colour is unavailable.

**Demo data.** The demo ships ~330 generated log rows across 60 days so the dashboard is meaningful on open. They are produced by running the real engine (search, safety, escalation), never by writing outcome fields directly, so no combination appears that the rules could not produce. Audience and complaint are deliberately correlated (acne skews to teenagers, koorts to under-fives, gewrichtspijn to older adults). The Streamlit app reads real rows instead; the generator is demo scaffolding.

**Data policy (AVG):** the raw question text stays in the session only and is never exported. The log holds structured fields, never names, contact details or free text. Nothing identifies a person; age is a bucket. This is what `policies.json` `policy004` promises the customer.

## Product Roadmap (proposed, not built)

Ordered by value to a store; each one should get its own milestone and reviewer pass before it is built.

1. **Stock and shelf location per product** (`stock`, `location` fields). "Waar ligt X" is the most common counter question and the data cannot answer it today.
2. **Employee feedback on every answer**: one tap "klopt" / "klopt niet" with a reason. Creates the quality dataset needed to tune prompts and vocabulary.
3. **Assortment gap report**: weekly list of `no_match` terms, so purchasing sees what customers asked for that the store does not carry.
4. **Multi-store comparison** once `store_id` is set: same categories, different stores.
5. **Seasonality view**: complaints per week (hooikoorts in spring, verkoudheid in autumn) once enough rows exist.
6. **Interaction checks** (medication combinations) only with a pharmacist-approved table in `data/`; never guessed by the model.
7. **English answers** for tourists, as a toggle on the customer view (stretch).
8. **Voice input** (stretch, unchanged: browser audio, text stays the default).

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
                                                                   │ QueryResult ──▶ Analytics Svc (log row)
                                              ┌────────────────────┼────────────────────┐
                                              ▼                    ▼                    ▼
                                        Employee View        Customer View          History
                                   (reasoning, checks,   (short, large type,    (reopen, Inzichten)
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
    category: str                  # one standard category
    triage: TriageState
    recommended: dict | None
    alternatives: list[dict]       # product + why
    blocked: list[dict]            # product + reason
    checks: list[dict]             # safety checks shown to the employee
    escalation: dict               # level: none | pharmacist | doctor | urgent, reason
    outcome: str                   # recommended | blocked | no_match | answered | unknown
    matched_promotions: list[dict]
    applicable_policies: list[dict]
    employee_answer: str
    customer_answer: str
    sources: list[str]             # record ids: p001, promo002, policy003
    timestamp: str                 # ISO
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
- **Green is the brand colour.** One green accent for navigation, primary actions and prices; blue for promotions; amber for "consult"; red for blocked and referrals. Semantic colours never double as the accent

## Scope Boundaries (Non-Negotiable)

- **No cloud deployment.** No Streamlit Cloud, no AWS, no Docker. One documented exception: a small relay that holds the API key so the demo can be shared by link, if the owner chooses to set one up. It is demo tooling, not part of the product.
- **No real database.** JSON files only, no SQLite, no Postgres
- **No authentication.** No login screen, no user roles. `store_id` comes from config, not from a login
- **No real voice input.** If we add speech, it's a stretch goal using browser audio; text input is the default
- **No real product images.** Use placeholder URLs or emoji icons in the customer view
- **No personal data.** The analytics log stores buckets and categories, never names, contact details or free text

## Known Gotchas

- **Streamlit reruns the entire script on every interaction.** Use `st.session_state` to persist the triage conversation state across reruns
- **Anthropic API can be slow on first call.** Use `st.spinner()` to show loading state
- **JSON files must be valid.** A trailing comma will crash `json.load()`; validate after editing, then run `python demo/build_demo.py` so the demo stays in sync
- **`st.navigation` requires Streamlit >= 1.36.** Pin the version in `requirements.txt`
- **Promotions expire.** Active status is computed from `start_date` / `end_date` against today; never hardcode "valid until"
- **Categories are a closed list.** Adding a product category means adding it to the standard categories too, or it falls under Overig in the analytics

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

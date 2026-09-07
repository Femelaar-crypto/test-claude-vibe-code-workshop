# Build Guide

Work through these in order. Run `/next` at any point to see where you are. Before each milestone, run the same case in `demo/index.html`: the app must behave the same.

## Milestone 1: Scaffold
Run `/scaffold` to generate `requirements.txt`, `app.py`, `pages/`, `services/`, `tests/`.
**Done when:** `streamlit run app.py` launches and navigates between four empty pages.

## Milestone 2: Data layer
Implement `services/data_service.py`: load the three JSON files with `st.cache_data`, expose `search_products(tags, text)`, `active_promotions(today)`, `match_policies(text)`.
**Done when:** `tests/test_data_service.py` passes; a promotion never makes a non-matching product appear.

## Milestone 3: Classification and extraction
Port `analyze`, `matchSymptoms`, `detectWho`, `detectDuration`, `detectPrior` and `computeGaps` from `demo/template.html` into `services/triage_service.py`.
**Done when:** "Mijn dochter van 8 heeft sinds gisteren keelpijn, nog niets geprobeerd" produces a complete `TriageState` with zero gap questions, and "Kan ik dit retourneren?" is classified `policy`. Run `triage-flow-reviewer`.

## Milestone 4: Ask page with gap questions
Build `pages/1_ask.py`: free-text input, then only the missing fields one at a time, backed by `st.session_state`. Include the no-match short-circuit.
**Done when:** "Mijn vrouw heeft keelpijn" asks exactly two questions (since when, tried anything) and "iets tegen een kater" asks none.

## Milestone 5: Safety rules
Port `applySafety` and `decideEscalation` into `services/safety_service.py` with unit tests for every rule in CLAUDE.md.
**Done when:** a child of 9 with sleep problems gets no product and a doctor referral; a pregnant customer with a headache gets paracetamol and never ibuprofen. Run `answer-quality-reviewer`.

## Milestone 6: AI composition
Implement `services/ai_service.py`: send the structured outcome to Claude (see the demo's `LIVE_SYSTEM` and JSON-schema output), receive `employee_answer` and `customer_answer`. Keep a templated fallback for when the API fails.
**Done when:** both views come back in Dutch, the customer view contains no record ids, and a blocked product is never recommended. Run `answer-quality-reviewer` again.

## Milestone 7: Employee and customer pages
Build `pages/2_employee_answer.py` (escalation banner, checks, blocked, alternatives, sources) and `pages/3_customer_view.py` (large type, presentation mode).
**Done when:** the employee can turn the screen to the customer without any internal information visible.

## Milestone 8: History and analytics
Implement `services/analytics_service.py` (log row per `QueryResult`, standard categories, aggregations, CSV export) and `pages/4_history.py`: reopenable questions, summary strip, and the five Inzichten sub-tabs (Klachten, Categorieën, Doelgroep, Uitkomsten, Producten).
**Done when:** ten seeded questions produce the same counts as `demo/index.html`, the export contains no question text or personal data, and every category falls in the standard list.

## Milestone 9: Polish
Loading state with `st.spinner`, cancel and restart, keyboard flow (Enter sends), Dutch everywhere.
**Done when:** both reviewer subagents come back PASS and the test suite is green.

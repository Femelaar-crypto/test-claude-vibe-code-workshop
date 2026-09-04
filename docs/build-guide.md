# Build Guide

Work through these in order. Run `/next` at any point to see where you are.

## Milestone 1 — Scaffold
Run `/scaffold` to generate `requirements.txt`, `app.py`, `pages/`, `services/`, `tests/`.
**Done when:** `streamlit run app.py` launches and navigates between four empty pages.

## Milestone 2 — Data layer
Implement `services/data_service.py`: load the three JSON files with `st.cache_data`, expose search functions.
**Done when:** `tests/test_data_service.py` passes and searching returns real products/promotions/policies.

## Milestone 3 — Triage flow
Implement the four-question triage state machine in `services/ai_service.py` / `pages/1_ask.py`, backed by `TriageState` in `st.session_state`.
**Done when:** asking a question walks through all four triage questions in order, one at a time, before accepting the actual question. Run `triage-flow-reviewer`.

## Milestone 4 — AI service & prompt
Implement the system prompt and Anthropic API call in `services/ai_service.py`: use the triage answers and matched data, produce `employee_answer` and `customer_answer`, prioritize promotions, attach compliance disclaimers, refuse to invent products outside the dataset.
**Done when:** a real question returns both views with correct sources. Run `answer-quality-reviewer`.

## Milestone 5 — Employee & customer views
Build `pages/2_employee_answer.py` (sources, context) and `pages/3_customer_view.py` (clean, no jargon, no internal context).
**Done when:** the two views clearly diverge — a customer never sees internal notes or source citations.

## Milestone 6 — History
Build `pages/4_history.py`: recent questions and trending topics from session history.
**Done when:** asking multiple questions in a session populates a visible history.

## Milestone 7 — Tests & polish
Fill out `tests/test_ai_service.py` and `tests/test_data_service.py`: full triage progression, at least one edge case (vague answer, restart, off-topic question), data search correctness.
**Done when:** both reviewer subagents come back PASS and the test suite is green.

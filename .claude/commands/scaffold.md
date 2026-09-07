---
description: Generate the full Streamlit app structure (pages, services, tests) from the CLAUDE.md spec, porting the demo engine
---

# Scaffold

Read `CLAUDE.md` in full before writing anything: it is the spec (stack, target layout, triage protocol, safety rules, data shapes, working style, scope boundaries). Then read `demo/template.html`: its JavaScript engine is the reference implementation you are porting to Python. Do not redesign the logic; port it, then improve it only where the spec asks.

Generate the application code, matching the **Target Layout** in `CLAUDE.md`:

1. `requirements.txt`: `streamlit>=1.36`, `anthropic`, `python-dotenv`, `pytest`
2. `app.py`: entrypoint using `st.navigation` across the four pages
3. `services/data_service.py`: loads `data/*.json` with `st.cache_data`; `search_products`, `active_promotions`, `match_policies`, `promo_for`
4. `services/triage_service.py`: port `analyze`, `classify`, `matchSymptoms`, `rawComplaint`, `detectWho`, `detectDuration`, `detectPrior`, `computeGaps` (keep the synonym vocabulary as data)
5. `services/safety_service.py`: port `applySafety` and `decideEscalation`
6. `services/ai_service.py`: `resolve` into a `QueryResult`, then compose the two answers with the Anthropic API (system prompt from the demo's `LIVE_SYSTEM`, JSON-schema output with `employee_answer` and `customer_answer`, model `claude-opus-5`), with the demo's templated composition as fallback when the API fails
7. `services/session_service.py`: `st.session_state` helpers for `TriageState`, the current result and history
8. `pages/1_ask.py`: free-text question, then only the missing fields one at a time, no-match short-circuit, cancel
9. `pages/2_employee_answer.py`: escalation banner, answer, triage summary, safety checks, recommendation, alternatives, blocked, policies, sources
10. `pages/3_customer_view.py`: short answer, large type, presentation mode
11. `pages/4_history.py`: reopenable history, most asked from the session
12. `tests/`: `test_triage_service.py`, `test_safety_service.py`, `test_ai_service.py`, `test_data_service.py`, covering at least the cases named in `docs/build-guide.md`

Follow the **Working Style** section of `CLAUDE.md` exactly (type hints, no silent errors, thin pages, Dutch UI) and respect the **Scope Boundaries** (no cloud deployment, no database, no auth, no real voice input, no real images).

When done:
- Tell me to run `cp .env.example .env`, add my API key, `pip install -r requirements.txt`, then `streamlit run app.py`
- Suggest running `triage-flow-reviewer` and `answer-quality-reviewer` before I consider it done

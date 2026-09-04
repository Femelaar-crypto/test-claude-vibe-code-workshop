---
description: Generate the full Streamlit app structure (pages, services, tests) from the CLAUDE.md spec
---

# Scaffold

Read `CLAUDE.md` in full before writing anything — it is the spec for this project (stack, target layout, data shapes, working style, scope boundaries).

Generate the application code for the DrugStore Assistant AI, matching the **Target Layout** in `CLAUDE.md` exactly:

1. `requirements.txt` — `streamlit>=1.36`, `anthropic`, `python-dotenv`, `pytest`
2. `app.py` — entrypoint using `st.navigation` across the four pages
3. `services/data_service.py` — loads and searches `data/products.json`, `data/promotions.json`, `data/policies.json`; wrap loaders in `st.cache_data`
4. `services/session_service.py` — `st.session_state` helpers for `TriageState` and conversation history
5. `services/ai_service.py` — Anthropic API calls, the triage state machine, the system prompt, and dual-view (employee/customer) answer generation, using the `TriageState` and `QueryResult` shapes from `CLAUDE.md`
6. `pages/1_ask.py` — presents triage questions one at a time, then the free-text question
7. `pages/2_employee_answer.py` — detailed answer with sources/matched data
8. `pages/3_customer_view.py` — clean, jargon-free answer
9. `pages/4_history.py` — recent questions, trending topics
10. `tests/test_ai_service.py`, `tests/test_data_service.py` — cover the triage progression and data search

Follow the **Working Style** section of `CLAUDE.md` exactly (type hints, no silent errors, thin pages, `st.cache_data`/`st.session_state` idioms) and respect the **Scope Boundaries** (no cloud deployment, no database, no auth, no real voice input, no real images).

When done:
- Tell me to run `cp .env.example .env`, add my API key, `pip install -r requirements.txt`, then `streamlit run app.py`
- Suggest running `triage-flow-reviewer` and `answer-quality-reviewer` before I consider it done

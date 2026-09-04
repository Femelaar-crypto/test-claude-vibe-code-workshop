# Architecture

## Request Flow

1. **Ask** (`pages/1_ask.py`) — employee opens the Ask screen. If `TriageState.complete` is `False`, the page asks only the next unanswered triage question, in fixed order:
   1. Who is the product for? → `intended_for`
   2. What's the nature of the complaints? → `complaints`
   3. Since when? → `duration`
   4. Already tried something? → `prior_remedies`
2. Once all four fields are set, `TriageState.complete = True` and the page accepts the free-text question.
3. **AI Service** (`services/ai_service.py`) builds a `QueryResult`:
   - Calls `services/data_service.py` to search `products.json` / `promotions.json` / `policies.json` for matches
   - Composes a system prompt containing the triage answers, matched products/promotions/policies, and instructions to produce two outputs
   - Calls the Anthropic API
   - Parses the response into `employee_answer` and `customer_answer`
4. **Employee View** (`pages/2_employee_answer.py`) renders `employee_answer` plus `matched_products`, `matched_promotions`, `applicable_policies` as sources.
5. **Customer View** (`pages/3_customer_view.py`) renders `customer_answer` only — no internal context, no source citations, no employee-only language.
6. **History** (`pages/4_history.py`) reads past `QueryResult`s from `services/session_service.py` and lists recent and trending questions.

## Data Layer

`services/data_service.py` loads the three JSON files with `st.cache_data` and exposes search functions (e.g. `search_products(query: str) -> list[dict]`). No database, no writes back to disk — the JSON files are read-only reference data.

## Promotion Prioritization

When a matched product also has an active promotion (its date range covers today), the AI service surfaces it ahead of non-promoted matches and mentions the promotion explicitly in both views.

## Compliance

Any matched product with a non-null `age_restriction` or `disclaimer` field must carry that warning into both the employee and customer answers. This is checked by `answer-quality-reviewer`.

## Session State

Everything — triage progress, conversation history, the current `QueryResult` — lives in `st.session_state` via `services/session_service.py`, since Streamlit reruns the whole script on every interaction.

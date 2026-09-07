# Architecture

The reference implementation of everything below is `demo/template.html`. When the Streamlit app and the demo disagree, the demo is right until someone changes it deliberately.

## Request Flow

1. **Ask** (`pages/1_ask.py`): the employee types the customer's question in plain Dutch.
2. **Classify** (`services/triage_service.py`): `symptom`, `policy`, `promo`, `lookup` or `unknown`.
   - `policy`: match `policies.json` keywords, answer with `description` (employee) and `customer_text` (customer).
   - `promo`: list promotions active today, filtered by product or category if one was named.
   - `lookup`: product named without a complaint ("hebben jullie pleisters?"): answer with the product, price, active promotion and any age restriction.
   - `unknown`: say honestly that there is no information, suggest rephrasing.
   - `symptom`: continue below.
3. **Extract** what the sentence already contains: the age of the person who will use the product (exact, or from a life stage), complaint tags, duration, prior remedies (and whether they failed, and which active ingredient), pregnancy.
4. **Short-circuit on no match**: if the complaint matches no product's `symptoms`, answer at once that nothing suitable is in the assortment. No triage questions for a question that has no product answer.
5. **Ask only the gaps**, one at a time: age, complaints, duration, prior remedies. Age is asked as a band or an exact number; the relationship to the customer is never asked, because it constrains nothing. Chips plus free text; free text runs through the same extractor.
6. **Search** (`services/data_service.py`): score products by symptom-tag overlap, product name match, category match. A promotion adds a small tie-break bonus only to products that already match.
7. **Safety** (`services/safety_service.py`): split candidates into allowed and blocked with reasons (age, sales restriction, pregnancy, tried without effect); flag "consult the pharmacist" cases; decide escalation (`none`, `pharmacist`, `doctor`, `urgent`).
8. **Compose** (`services/ai_service.py`): the model receives the structured outcome (recommended, alternatives, blocked with reasons, promotions, policies, escalation) and writes `employee_answer` and `customer_answer` in Dutch. It cannot add products. The demo's `LIVE_SYSTEM` prompt and JSON-schema output are the template.
9. **Employee View**: escalation banner first, then answer, triage summary, safety checks (passed and blocked), recommendation with usage, promotion and disclaimer, alternatives, policies, sources as record ids.
10. **Customer View**: product, price (promo price when `type == percent_off`), short answer, promotion, age note. Presentation mode fills the screen and hides all employee chrome.
11. **Log** (`services/analytics_service.py`): every `QueryResult` becomes one structured row (category, complaints, age band, outcome, escalation, record ids, assortment gap). Never the question text, never personal data.
12. **Inzichten**: one linked dashboard over the log rows, grouped into five named sections so the page reads in the order an analyst would think about it: **Kruisverband** (klacht × leeftijd matrix + "Opvallend" over-representation panel), **Demografie** (Leeftijd, and Zwangerschap & borstvoeding as its own clickable stat rather than something buried in the lift panel), **Klacht** (Klachten, Categorie, Sinds wanneer), **Uitkomst** (Uitkomst, Doorverwijzing), **Assortiment** (the gap list). A period control and KPI strip with deltas sit above all five. Every panel filters every other; a panel never filters itself. The reopenable session questions sit below the dashboard. CSV export covers the current selection only.

## Categories

One closed list, so counts stay comparable over time: the product categories in `products.json` plus Beleid, Acties, Product opzoeken and Overig. A symptom question takes the category of the recommended product, else of the best blocked candidate, else Overig. Adding a product category means adding it here too.

## Analytics forms

Counts are ranked lists with a proportional bar, one hue, count on the right and the share in the row's tooltip. The bar shows the filtered subset as a fill inside the period total, so selection and baseline read together. The matrix uses one light-to-dark green ramp for count and always prints the number. Never a pie, never a second y-axis. Every row is readable as text (label plus number), so colour carries no information on its own.

Small numbers are handled explicitly: the over-representation panel stays silent below eight rows in the selection or three occurrences of a value, rather than presenting a ratio built on two questions.

A binary fact (pregnancy or breastfeeding mentioned) is not a ranked list, so it does not use the multi-row bar-row grid: one full-width label, then the bar and percentage below it. Cramming a single stat into a layout built for many requires either a column too narrow for the label or an implicit assumption that the label is short -- neither held once the label was decided by content rather than by the grid.

## Data Layer

`services/data_service.py` loads the three JSON files with `st.cache_data`. Read-only reference data; no writes back to disk.

Product fields that drive behaviour:

| Field | Used for |
|---|---|
| `symptoms` | search (tag overlap) |
| `min_age` | block below this age; a band is judged at its lower bound, unknown age at zero |
| `age_restriction` | sales restriction (ID check), block for minors |
| `pregnancy_safe` | `true` allowed, `false` blocked, `null` flagged "consult" |
| `active_ingredient` | "tried without effect" exclusion, alternatives with a different ingredient |
| `usage` | dosage line in both views |
| `disclaimer` | verbatim in the employee view, plain in the customer view |

## Session State

Triage progress, the current `QueryResult` and history live in `st.session_state` via `services/session_service.py`, because Streamlit reruns the whole script on every interaction.

## The demo and the app

`demo/index.html` runs the same pipeline in the browser with a deterministic composition step (templated Dutch) and an optional live step that calls Claude with the presenter's own key. The app keeps the key server-side and uses the `anthropic` package; the pipeline stays the same.

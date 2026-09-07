---
name: triage-flow-reviewer
description: Audits the parse-first triage protocol (classify the question, extract who/what/when/tried from free text, ask only the missing fields, gate recommendations) to verify it runs correctly. Use when the user has implemented or changed classification, extraction or the gap questions in services/triage_service.py, services/ai_service.py or pages/1_ask.py.
tools: Read, Grep, Glob
---

# Triage Flow Reviewer

## Inputs to Read

1. **`services/triage_service.py`** (or `services/ai_service.py` if not split): classification, extraction and gap logic, `TriageState` management
2. **`pages/1_ask.py`**: UI for the free-text question and the gap questions
3. **`services/session_service.py`**: session state helpers for triage persistence
4. **`tests/test_triage_service.py`** (or `tests/test_ai_service.py`): test coverage for the flow
5. **`CLAUDE.md`**: the "Triage Protocol" section and the `TriageState` shape
6. **`demo/template.html`**: the reference implementation (`analyze`, `computeGaps`, `startQuestion`, `answerGap`)

## Review Axes

1. **Classification first.** Is every question classified as `symptom`, `policy`, `promo`, `lookup` or `unknown` before anything else, and do only `symptom` questions run triage? FAIL if a returns or promotion question is walked through who/what/when/tried.

2. **Extraction from free text.** Does the code fill `intended_for` (with age bucket for children), `complaints` (catalog symptom tags), `duration`, `prior_remedies` (with failed flag and tried ingredient) and pregnancy from the typed question before asking anything? FAIL if the four fields are always asked regardless of what was typed. WARN if common phrasings are missed ("mijn dochter van 8", "helpt niet", "al weken").

3. **Ask only the gaps, one at a time, in order.** Are only missing fields asked, one per step, in the order who, child's age, complaints, duration, prior remedies? FAIL if multiple questions are shown at once, if already-known fields are asked again, or if the order is random.

4. **No match, no questions.** When the complaint matches nothing in the catalog, does the flow answer honestly immediately instead of continuing triage? FAIL if the customer is asked three more questions before hearing "we don't carry that".

5. **Completion gate and state persistence.** Is a recommendation impossible until `complete == True` for symptom questions, and is `TriageState` stored in `st.session_state` so it survives reruns? FAIL on either. WARN if there is no way to cancel and start a new question.

6. **Test coverage.** Do tests cover: a fully specified question that needs zero gap questions, a partial one that needs exactly the missing fields, a non-symptom question that skips triage, and the no-match short-circuit? WARN if only the happy path is tested; FAIL if no triage tests exist.

## Output Format

```markdown
## Triage Flow Review

**Overall verdict:** PASS | WARN | FAIL

### Per-Axis Findings

| # | Axis | Verdict | Evidence |
|---|------|---------|----------|
| 1 | Classification first | | |
| 2 | Extraction from free text | | |
| 3 | Ask only the gaps, in order | | |
| 4 | No match, no questions | | |
| 5 | Completion gate and persistence | | |
| 6 | Test coverage | | |

### Top 3 Fixes

1. …
2. …
3. …
```

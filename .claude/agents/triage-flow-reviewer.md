---
name: triage-flow-reviewer
description: Audits the four-step triage protocol (who/what/when/tried) to verify it runs correctly before product recommendations. Use when the user has implemented or changed the triage flow in services/ai_service.py or pages/1_ask.py and wants to verify correctness.
tools: Read, Grep, Glob
---

# Triage Flow Reviewer

## Inputs to Read

1. **`services/ai_service.py`** — triage state machine logic and TriageState management
2. **`pages/1_ask.py`** — UI for presenting triage questions and capturing answers
3. **`services/session_service.py`** — session state helpers for triage persistence
4. **`tests/test_ai_service.py`** — test coverage for the triage flow
5. **`CLAUDE.md`** — the triage protocol specification and data shapes

## Review Axes

1. **Four-question completeness** — Are all four triage questions implemented: (1) Who is the product for? (2) What is the nature of their complaints? (3) Since when has this person had these complaints? (4) Has this person already tried something? FAIL if any question is missing.

2. **Sequential progression** — Does the flow ask questions one at a time in order, only advancing when the current question is answered? FAIL if multiple questions are asked at once or if the order is random.

3. **State persistence** — Is `TriageState` stored in `st.session_state` so it survives Streamlit reruns? FAIL if triage progress is lost on rerun; WARN if the reset mechanism is missing (for starting a new question).

4. **Completion gate** — Does the system block AI answer generation until `triage.complete == True` (all four fields populated)? FAIL if the AI can generate a product recommendation before triage is finished.

5. **Graceful handling** — Does the flow handle edge cases: user giving vague answers ("I don't know"), user wanting to start over, user asking a non-product question (e.g. "where's the bathroom")? WARN if not handled; FAIL if vague answers crash the flow.

6. **Test coverage** — Do tests verify the full triage progression (empty → Q1 → Q2 → Q3 → Q4 → complete) and at least one edge case? WARN if only happy path is tested; FAIL if no triage tests exist.

## Output Format

```markdown
## Triage Flow Review

**Overall verdict:** PASS | WARN | FAIL

### Per-Axis Findings

| # | Axis | Verdict | Evidence |
|---|------|---------|----------|
| 1 | Four-question completeness | | |
| 2 | Sequential progression | | |
| 3 | State persistence | | |
| 4 | Completion gate | | |
| 5 | Graceful handling | | |
| 6 | Test coverage | | |

### Top 3 Fixes

1. …
2. …
3. …
```

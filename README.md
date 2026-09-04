# DrugStore Assistant AI

Streamlit prototype that lets store employees ask a question and get two things back: a detailed employee-facing answer with sources, and a clean customer-facing answer — grounded in local product, promotion, and policy data, gated behind a four-question triage flow.

**Status: starter kit.** No application code yet — see `CLAUDE.md` for the full spec. Run `/scaffold` in Claude Code to generate it.

## Quickstart

```bash
cp .env.example .env       # paste your ANTHROPIC_API_KEY
```

Open this folder in VS Code with the Claude Code extension, then in Claude Code:

```
/tour       # walkthrough of the project
/scaffold   # generates app.py, pages/, services/, tests/
```

Once scaffolded:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## What's here

- `CLAUDE.md` — full spec: stack, architecture, data shapes, working style, scope boundaries
- `data/` — synthetic Dutch drugstore product, promotion, and policy data
- `docs/build-guide.md` — milestone ladder for building the app
- `docs/architecture.md` — data flow and component breakdown
- `docs/claude-code-tips.md` — Claude Code cheatsheet
- `.claude/agents/` — `answer-quality-reviewer`, `triage-flow-reviewer`
- `.claude/commands/` — `/tour`, `/scaffold`, `/next`, `/tip`

## Scope

Local dev only. No cloud deployment, no Docker, no database, no auth. Full boundaries in `CLAUDE.md`.

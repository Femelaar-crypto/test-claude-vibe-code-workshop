# DrugStore Assistant AI

Streamlit prototype that lets store employees ask a customer's question in plain Dutch and get two things back: a detailed employee answer with reasoning, safety checks and sources, and a clean customer-facing answer. Grounded in local product, promotion and policy data; triage and hard safety rules run before anything is recommended.

## Try the demo (nothing to install)

Open `demo/index.html` in any browser. That's it: double-click the file, or send the file to someone. It works offline and needs no account.

- Type a question or click one of the examples. The assistant reads what it already knows from the sentence and asks only for what is missing.
- Try the cases that matter: a child with sleep problems (blocked, doctor referral), a pregnant customer with a headache (paracetamol yes, ibuprofen no), "iets tegen een kater" (honest no-match), a returns question (no triage at all).
- "Toon aan klant" opens the customer answer full screen.

**Live Claude mode (optional):** the gear icon lets the presenter switch from simulated answer text to text written by Claude, using their own Anthropic API key. The key stays in the tab's memory only. Search, safety rules and promotions still run locally; Claude only writes the two answers. Use this on your own laptop only; the real product keeps the key server-side.

After editing anything in `data/`, rebuild the demo:

```bash
python demo/build_demo.py
```

## Build the Streamlit app

**Status:** starter kit plus the reference demo. No Streamlit code yet; `CLAUDE.md` is the spec and `demo/template.html` is the reference implementation of the logic.

```bash
cp .env.example .env       # paste your ANTHROPIC_API_KEY
```

Open this folder in VS Code with the Claude Code extension, then:

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

- `CLAUDE.md`: full spec: stack, triage protocol, safety rules, data shapes, working style, scope boundaries
- `demo/`: shareable browser demo (`index.html`), its source (`template.html`) and the build script
- `data/`: synthetic Dutch drugstore products (with `min_age`, `pregnancy_safe`, `active_ingredient`, `symptoms`), promotions with dates, policies with customer wording
- `docs/build-guide.md`: milestone ladder for building the app
- `docs/architecture.md`: the pipeline, step by step
- `docs/claude-code-tips.md`: Claude Code cheatsheet
- `.claude/agents/`: `answer-quality-reviewer`, `triage-flow-reviewer`
- `.claude/commands/`: `/tour`, `/scaffold`, `/next`, `/tip`

## Scope

Local dev only. No cloud deployment, no Docker, no database, no auth. Full boundaries in `CLAUDE.md`.

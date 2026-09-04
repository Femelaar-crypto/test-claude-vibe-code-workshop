# Claude Code Tips

A handful of things worth knowing while building this project.

1. **Plan mode for anything touching triage or the prompt.** Changes to `services/ai_service.py` span state machine, prompt, and two output views — ask for a plan first instead of a direct edit.
2. **Run the subagents after, not instead of, reading the diff.** `triage-flow-reviewer` and `answer-quality-reviewer` catch missed axes; they don't replace looking at what changed.
3. **CLAUDE.md is the contract.** When a suggestion conflicts with a Scope Boundary (auth, database, cloud deploy), point back at `CLAUDE.md` rather than arguing the merits each time.
4. **Custom commands live in `.claude/commands/`.** `/scaffold`, `/tour`, `/next`, `/tip` are just markdown files — read them if a command isn't doing what you expect, and edit them directly.
5. **`st.session_state` survives reruns, nothing else does.** Any bug where triage "forgets" an answer is almost always state not being written back to `st.session_state`.
6. **One concern per edit.** Don't let a UI tweak in `pages/1_ask.py` ride along with a prompt change in `ai_service.py` — separate diffs are easier to review and to revert.
7. **Ask before deleting.** If a change proposes removing a file or function, make it justify why first — especially in `services/`.
8. **Validate JSON after editing `data/*.json` by hand.** A trailing comma silently crashes `json.load()` on the next run.

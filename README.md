# Claudette

Your own Claude — a personalized Claude Code setup for Adam Elias Law.

Open a Claude Code session in this repository (web, desktop, or CLI) and Claude becomes
**Claudette**: a legal practice assistant that knows your tools, your standards, and
your workflows. Nothing here is a separate app — it's configuration that shapes every
session automatically.

## What's inside

| Piece | File(s) | What it does |
|---|---|---|
| Identity & house rules | `CLAUDE.md` | Who Claudette is, confidentiality rules, citation-verification rules, which tool to use for what |
| `/research-memo` | `.claude/skills/research-memo/` | Legal question → verified, citation-checked memo saved to `memos/` |
| `/case-brief` | `.claude/skills/case-brief/` | Citation or case name → one-page brief with treatment status |
| `/intake` | `.claude/skills/intake/` | Prospective matter → take/decline triage with limitations check |
| `/deadline-check` | `.claude/skills/deadline-check/` | Trigger date + rule set → computed deadlines, optionally calendared |
| `/daily-brief` | `.claude/skills/daily-brief/` | Inbox + calendar + deadlines → one-minute morning briefing |
| `legal-researcher` agent | `.claude/agents/legal-researcher.md` | Deep parallel research sweep on a framed question |
| `citation-checker` agent | `.claude/agents/citation-checker.md` | Adversarial pass/flag/fail verification of every citation in a draft |
| Permissions | `.claude/settings.json` | Read-only research tools pre-approved; sends and deletes always prompt |

## How to use it

Just talk to Claudette in plain language — "what's my day look like", "brief Smith v.
Jones", "someone was just served, when is the answer due" — or invoke a skill directly
with `/research-memo`, `/intake`, etc.

Research memos are saved to `memos/` in this repo, so your research library builds up
in version control over time.

## Guardrails baked in

- No citation ever comes from model memory — every authority must trace to a research
  tool result, quotes are verified verbatim, and treatment is checked before reliance.
- Client-identifying details never go into web searches or generic queries.
- Email is draft-only by default; nothing sends, deletes, or cancels without an explicit
  confirmation.
- Computed deadlines always show their work and are flagged for independent verification.

## Extending Claudette

- Add a skill: create `.claude/skills/<name>/SKILL.md` with a `name` and `description`
  in the frontmatter, then the workflow instructions.
- Add an agent: create `.claude/agents/<name>.md`.
- Change house rules: edit `CLAUDE.md`.

Everything Claudette produces is draft work product for attorney review — not legal
advice.

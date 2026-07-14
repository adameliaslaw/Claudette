# Claudette

Your own Claude, three ways — from a working AI assistant for your practice, to an
actual language model trained from scratch that you own outright.

| Layer | Where | What it is |
|---|---|---|
| **Claudette the assistant** | this directory | A personalized Claude Code setup: open a session in this repo and Claude becomes your legal practice assistant |
| **Claudette-1, your own LLM** | [`claudette-1/`](claudette-1/) | A real GPT-style model trained from scratch on the Federalist Papers — ~820k parameters, your weights, ~350 lines of readable code |
| **Fine-tuning pipeline** | [`finetune/`](finetune/) | LoRA fine-tune an open-weight 7–8B model on your own writing: a genuinely useful private model that drafts in your voice |

## Layer 1: Claudette the assistant

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

## Layer 2: Claudette-1 — your own model, from scratch

`claudette-1/` contains a complete decoder-only transformer (the same architecture
family as Claude) that pretrains from randomly initialized weights on public-domain
founding legal texts, on a laptop CPU, in about 20 minutes. It exists to teach: read
`model.py` and you have read what a GPT literally is. See
[`claudette-1/README.md`](claudette-1/README.md) for the scale comparison against
frontier models and honest expectations (it writes 1787-flavored prose, not answers).

## Layer 3: Fine-tune a real open model on your writing

`finetune/` is the practical "own model" path: QLoRA fine-tuning of an open-weight
model (default Qwen2.5-7B-Instruct, Apache 2.0) on your own letters, memos, and
curated prompt→draft pairs. Output is a private model that runs on your hardware via
Ollama and drafts in your voice. Costs a few dollars of rented GPU time or runs free
on a good Mac. See [`finetune/README.md`](finetune/README.md) for the full guide,
including the confidentiality-first data-handling notes. **On an Apple Silicon Mac,
start with [`finetune/MAC_GUIDE.md`](finetune/MAC_GUIDE.md)** — a complete
plain-English walkthrough for non-technical users, from opening Terminal for the
first time to chatting with your finished model.

## Extending Claudette

- Add a skill: create `.claude/skills/<name>/SKILL.md` with a `name` and `description`
  in the frontmatter, then the workflow instructions.
- Add an agent: create `.claude/agents/<name>.md`.
- Change house rules: edit `CLAUDE.md`.

Everything Claudette produces is draft work product for attorney review — not legal
advice.

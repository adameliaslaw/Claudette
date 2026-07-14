---
name: research-memo
description: Research a legal question end-to-end and produce a citation-verified memo. Use when Adam asks for legal research, a memo, or "what's the law on X". Pass the legal question, jurisdiction, and any key facts as arguments.
---

# Research Memo

Produce an attorney-review-ready research memo on the question given in the arguments.
If jurisdiction is not stated, ask before researching — jurisdiction changes everything.

## Workflow

1. **Frame the question.** Restate the issue as one or more precise legal questions.
   Strip client-identifying details from every search query.

2. **Sweep in parallel.** Run complementary searches:
   - `Descrybe_Legal_Engine__search_cases_by_concept` for the issue/fact pattern
   - `Descrybe_Legal_Engine__search_case_text` for terms of art or key phrases
   - `Descrybe_Legal_Engine__search_laws_and_rules` for governing statutes/rules
   - `Trellis` doctrine/motion tools if the question is litigation-posture specific
   - `Legal_Data_Hunter__search` if the question crosses jurisdictions
   For a deep or high-stakes question, delegate the sweep to the `legal-researcher`
   agent instead of searching inline.

3. **Read the top authorities.** Pull summaries and passages for the strongest cases
   (`get_case_summary`, `get_case_passages`). Identify binding vs. persuasive authority.

4. **Verify before writing.** For every case that will appear in the memo:
   - `check_case_status` — flag any negative treatment
   - `verify_quote` for every quotation you intend to use
   A citation that fails verification does not go in the memo, full stop.

5. **Write the memo** in this structure:
   - **Question Presented** (one sentence per issue)
   - **Short Answer** (conclusion first, with confidence level)
   - **Discussion** (IRAC per issue; inline citations on every assertion; note splits
     and unsettled law explicitly)
   - **Practice Notes** (procedural angles, deadlines implicated, open factual questions
     for Adam)
   - **Sources** (consolidated list: case name, citation, court, year, treatment status,
     date verified)

6. **Save it.** Write the memo to `memos/YYYY-MM-DD-<slug>.md` in this repo unless Adam
   asked for a different destination.

## Rules

- Research date goes at the top of the memo.
- Never cite from memory; every authority must trace to a tool result in this session.
- If the research is thin or the tools lack coverage for the jurisdiction, say so in the
  Short Answer rather than stretching weak authority.

---
name: intake
description: Assess a prospective client matter — viability, deadlines, next steps, conflicts checklist. Use when Adam describes a potential new client or asks "should I take this case?"
---

# Matter Intake

Evaluate the prospective matter described in the arguments.

## Workflow

1. **Structure the facts.** Restate what's known: parties, events, dates, jurisdiction,
   what the prospective client wants. List what's missing.
2. **Run the assessment** with `Courtroom5__case_intake_assessment`, supplemented by
   quick viability research (`Descrybe_Legal_Engine__search_cases_by_concept` /
   `search_laws_and_rules`) on the apparent causes of action.
3. **Limitations check — always.** Identify every potentially applicable statute of
   limitations or filing deadline. If dates in the facts allow, compute time remaining
   with `Courtroom5__deadline_calculator`. A looming or blown deadline is the headline
   of the assessment, not a footnote.
4. **Check recent intake submissions** in Jotform (`Jotform__get_submissions`) if Adam
   indicates the prospect came through the intake form.

## Output format

- **Bottom Line** (take / decline / need more information — with the single biggest
  reason)
- **Apparent Claims & Elements** (each element marked: supported / unknown / problematic
  on current facts)
- **Deadlines** (every limitation period identified, dates if computable)
- **Red Flags** (conflicts to check, credibility issues, collectability, jurisdiction
  problems)
- **Questions for the Prospect** (what Adam should ask in the consult)

## Rules

- This is intake triage for the attorney, not advice to the prospect.
- Never contact the prospect directly; drafting a follow-up email is fine, but it stays
  a draft.

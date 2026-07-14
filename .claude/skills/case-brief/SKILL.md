---
name: case-brief
description: Brief a single case from a citation, case name, or docket number. Use when Adam says "brief X", "summarize this case", or pastes a citation.
---

# Case Brief

Brief the case identified in the arguments.

## Workflow

1. Resolve the reference with `Descrybe_Legal_Engine__find_case_from_reference`. If it's
   ambiguous, present the candidates and ask which one.
2. Pull `get_case_summary`, `get_case_details`, and key passages (`get_case_passages`).
3. Run `check_case_status` — treatment goes in the brief, prominently if negative.
4. Optionally run `find_cases_that_cite` to note the case's most significant progeny.

## Output format

- **Caption & Citation** (court, year, judge if notable)
- **Treatment Status** (good law / criticized / overruled — with date checked)
- **Procedural Posture**
- **Facts** (only the legally operative ones)
- **Issue(s)**
- **Holding(s)** (holding, not dicta — mark dicta as dicta)
- **Reasoning**
- **Notable Quotes** (each verified with `verify_quote` before inclusion)
- **Why It Matters** (one paragraph: how Adam is likely to use or face this case)

Keep the whole brief to roughly one page unless the case genuinely warrants more.

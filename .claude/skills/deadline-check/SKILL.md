---
name: deadline-check
description: Compute litigation deadlines from a trigger date and rule set, and optionally add them to Google Calendar. Use when Adam mentions being served, filing something, a hearing date, or asks "when is X due?"
---

# Deadline Check

Compute the deadline(s) implied by the arguments.

## Workflow

1. Identify the trigger event, trigger date, jurisdiction, and court from the arguments.
   If any of these is missing, ask — never guess a jurisdiction for a deadline.
2. Compute with `Courtroom5__deadline_calculator`. Cross-check the governing rule with
   `Descrybe_Legal_Engine__search_laws_and_rules` and cite it.
3. Present each deadline as: **event — due date — governing rule — how computed**
   (calendar vs. court days, service-method extensions, weekend/holiday rollover).
4. Offer to calendar the deadlines. On confirmation, create Google Calendar events that
   include the computation basis in the description, plus a reminder event 7 days ahead
   of each true deadline (3 days ahead for deadlines under two weeks out).

## Rules

- Show your work: the computation chain must be visible so Adam can check it.
- If the calculator and the rule text disagree, flag the conflict — do not silently pick
  one.
- Recommend Adam independently verify any deadline that is jurisdiction-critical or
  claim-dispositive. Computed deadlines are a cross-check, not a docketing system of
  record.

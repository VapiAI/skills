# Coverage planning for Vapi Simulations

How to decide what to simulate, how to write scenarios and success criteria a reviewer will trust, and when a suite is ready for launch. Distilled from the Vapi testing guidance; each section names the page it comes from.

Sources:

- [Testing voice agents](https://docs.vapi.ai/test/voice-testing)
- [Plan test coverage](https://docs.vapi.ai/test/plan-test-coverage)
- [Test outcomes with Simulations](https://docs.vapi.ai/test/simulations-best-practices)
- [Test decisions with Evals](https://docs.vapi.ai/test/evals-best-practices)
- [Run and maintain tests](https://docs.vapi.ai/test/run-and-maintain-tests)

## Contents

1. [Simulations test outcomes, Evals test decisions](#1-simulations-test-outcomes-evals-test-decisions)
2. [Turn requirements into testable statements](#2-turn-requirements-into-testable-statements)
3. [Prioritize by risk](#3-prioritize-by-risk)
4. [Coverage checklist per customer goal](#4-coverage-checklist-per-customer-goal)
5. [Writing the scenario and choosing the personality](#5-writing-the-scenario-and-choosing-the-personality)
6. [Writing evaluations](#6-writing-evaluations)
7. [Chat first, voice to validate](#7-chat-first-voice-to-validate)
8. [Keep real systems safe](#8-keep-real-systems-safe)
9. [Iterations and review](#9-iterations-and-review)
10. [Launch readiness](#10-launch-readiness)
11. [Maintaining an existing suite](#11-maintaining-an-existing-suite)

## 1. Simulations test outcomes, Evals test decisions

A simulation gives an AI tester a goal and lets it adapt through a whole conversation, then scores the final outcome. An Eval freezes the conversation at one point and asks whether the next decision is right. When a requirement is really about one decision at one moment (ask for the timezone before booking, do not refund an ineligible order), note it as an Eval candidate instead of forcing it into a scenario.

Test in layers: critical decisions with Evals, outcomes with chat simulations, audio experience with voice simulations, then human review of transcripts and recordings. Automated tests judge only the requirements you wrote down.

Source: Testing voice agents.

## 2. Turn requirements into testable statements

Rewrite each requirement until two informed reviewers would reach the same pass or fail decision on their own:

| Not testable | Testable |
| --- | --- |
| The agent is helpful | If the requested time is unavailable, the agent offers available alternatives |
| The agent handles verification | The agent shares appointment details only after identity verification succeeds |
| The agent recovers from errors | If the scheduling tool fails, the agent says the change is not confirmed and offers a safe next step |

Record where each requirement came from (a document, a call, a ticket, a person). A requirement with no source is an assumption; return it as an open question before it becomes a scenario.

Source: Plan test coverage, "Start with requirements".

## 3. Prioritize by risk

Cover these first, in this order:

- High impact: a failure exposes data, moves money, changes something without authorization, misses an escalation, or creates legal exposure.
- High frequency: callers rely on the behavior for the agent's main job.
- High uncertainty: the behavior is new, recently changed, inconsistent, or depends on an external tool.

Source: Plan test coverage, "Prioritize".

## 4. Coverage checklist per customer goal

For every primary goal, decide which of these you need:

| Checklist item | Start with | Notes |
| --- | --- | --- |
| Core outcome | Simulation, chat mode | The smoke test; one or two required Boolean outcomes |
| Caller variation | Simulation | Same scenario facts, a different personality or ordering |
| Missing or unclear information | Simulation | The caller omits something the agent must ask for |
| Tool or service failure recovery | Simulation with a tool mock that returns an error | The agent must not claim success |
| Guardrails (data protection, escalation) | Simulation, both directions | See section 6 |
| Safe alternative when the request cannot be met | Simulation | Unavailable slot, ineligible request |
| Handoff quality | Simulation against the squad | A single-assistant target cannot exercise a handoff |
| Voice experience | Voice simulation | Final validation, not the first pass |
| Known production failure | Regression simulation | The smallest scenario that reproduces the incident |
| Critical single decisions | Eval | Hand these to Evals |

Source: Plan test coverage, "Layered coverage checklist".

## 5. Writing the scenario and choosing the personality

The scenario carries what the caller wants, the facts the caller knows, what the caller may volunteer, constraints and acceptable alternatives, and when the caller ends the conversation. Give goals and facts, not exact sentences; six numbered turns is a script, and a script hides the paths a real caller would take.

The personality carries tone, patience, verbosity, interruption habits, what the caller does when an answer is unclear, and the tester's model, transcriber, and voice. Vapi provides default personalities in every org; use a cooperative one for core outcomes so the wrap-up is clean, and reserve rambling or distracted ones for variation cases. A custom personality is a full assistant configuration whose persona prompt is the first system message.

Give every scenario and personality pair its own scenario name. The run view lists results by scenario name, so four simulations sharing one scenario appear as four identical rows and failure triage starts with "which one was this?".

Sources: Test outcomes with Simulations, "Scenario vs personality"; Configure an AI tester.

## 6. Writing evaluations

Each evaluation is one structured output plus a comparator and an expected value. Rules that hold up in review:

- One observable outcome per evaluation. "The tool reported success and the agent read back the time" is two evaluations.
- Judge recorded facts, not the agent's claims. A reschedule passes when the tool result says success, not when the agent says "you're all set".
- State exactly what counts as success in the description, and allow different wording and different valid paths.
- Use an AI-judged Boolean for meaning ("True only if the agent asked for a timezone before calling the tool"), regex for stable identifiers or formats, and never a judge for "the call went well".
- Pair activation with restraint. For every high-impact rule, add the case where the agent must not act: details withheld after failed verification, no booking without a timezone, no refund for an ineligible order.
- Mark nice-to-have checks `required: false` so they report without gating.
- Every scenario that runs in chat mode needs at least one text-based required evaluation. Audio-only evaluations are skipped in chat mode, and a scenario whose required checks are all skipped passes with nothing asserted.

Sources: Test outcomes with Simulations, "Success criteria" and "Pitfalls"; Plan test coverage, "Success and restraint pairing".

## 7. Chat first, voice to validate

Build and debug in chat mode (`vapi.webchat`): faster, cheaper, no audio. Run the primary conversations in voice mode (`vapi.websocket`) before launch to cover transcription, speech, and turn-taking. Voice runs use two concurrent call slots each (tester plus target). Do not rely on voice runs to prove digit accuracy for dates, phone numbers, or codes; synthetic testers can drop trailing digits, and that needs a real caller.

Source: Test outcomes with Simulations, "Chat vs voice".

## 8. Keep real systems safe

Simulations call unmocked tools for real. Before the first run, list every tool that books, charges, messages, or writes, and mock each one in every scenario that could reach it. Use synthetic caller data and safe test accounts. Remove personal information when a scenario is built from a production example.

Sources: Simulations quickstart; Run and maintain tests, "Turn production issues into regression tests".

## 9. Iterations and review

One iteration while building. Before a release, repeat critical scenarios and compare the iterations rather than averaging them: if any iteration breaks a critical requirement, the behavior is unstable until you know why. Read every failed transcript and a sample of passes; ask whether the agent erred, whether the tester followed the scenario, whether the criteria rejected a valid outcome, and whether a tool or configuration issue skewed the run. Listen to recordings for voice runs.

Source: Run and maintain tests, "Repeat critical tests" and "Review beyond pass/fail labels".

## 10. Launch readiness

Before calling a suite launch-ready, confirm:

- end-to-end simulation coverage for each primary goal
- high-impact decisions covered in both activation and restraint
- at least one failure or recovery case per primary goal
- dedicated guardrail and handoff coverage where they apply
- repeated passes on the critical scenarios
- voice-mode runs of the primary conversations
- a human has read representative transcripts and listened to recordings
- every side-effect tool mocked or pointed at a sandbox

Source: Plan test coverage, "Launch readiness".

## 11. Maintaining an existing suite

- Keep improvement tests (behavior the agent cannot do reliably yet) apart from regression tests (behavior production already depends on). Promote an improvement test to regression once it passes reliably.
- Rerun affected tests after any change to prompts, tools, models, voices, transcribers, call settings, or business rules.
- Turn each production incident into the smallest test that would have caught it, plus the opposite case.
- Do not weaken a test to make it pass, and do not rerun until green without an explanation. Record intermittent failures.
- Every critical journey has one owner who maintains expected outcomes and reviews failures.
- A suite update replaces its `simulationIds` list. Fetch the suite first, diff by name, send the retained ids followed by the new ones, and remove an id only when the user named that simulation.

Source: Run and maintain tests, "Separate improvement tests from regression tests", "Triage failures consistently", "Give every critical journey an owner".

# Planning the scenario list

How step 9 turns the flow tree, the prompt branches and the tool catalog into a scenario list tagged Critical or All. When no calls were read there are no traffic numbers, so the steps use the fallbacks marked *Without calls* below.

## Contents

- [Admission test](#admission-test)
- [Rules are checks, not scenarios](#rules-are-checks-not-scenarios)
- [Critical](#critical)
- [All](#all)
- [Merging repeated tests](#merging-repeated-tests)
- [Situations the prompt doesn't cover](#situations-the-prompt-doesnt-cover)
- [Checks before the gate](#checks-before-the-gate)
- [Weights](#weights)

## Admission test

Every scenario earns its place in at least one way. Write the reason in its `admission` field.

- **Common:** it represents real traffic (a route or a variant from the tree).
- **At risk:** a situation the prompt handles specifically that a new model is likely to get wrong: rare cases, error handling, branches no call reached.
- **Severe:** a failure would matter for safety, compliance, money or security.

A scenario that is none of these doesn't go in, however easy it is to write.

## Rules are checks, not scenarios

A general rule that applies on every turn ("never give medical advice", "verify identity before sharing appointment details", "say you're an AI if asked", "never make up an answer") is not a scenario of its own. It becomes a check that is graded on every scenario where it can come up. Dedicated scenarios are only for **compliance situations**: a specific moment the prompt handles in a set way (a caller reports an emergency, a third party asks about a patient, a caller asks to delete their data).

## Critical

The smallest suite that can show whether a model change is safe. Usually 10 to 25 scenarios; a large squad may need up to about 40.

1. **Routes:** one scenario per route (a primary intent with its main steps), highest traffic first, until about 80% of conversations are covered or the next route is under about 3% of traffic. *Without calls:* one route per primary intent the prompt defines, on its main path.
2. **Every ending the model can produce, at least once.** Endings the platform or the caller produce (a transfer that fails to connect, a silence timeout, a caller hanging up) can't be produced in chat; leave them to voice runs. If a route already ends that way, it counts.
3. **The severe compliance situations, once each, and every must-never-break rule from `metrics.md` that needs a caller to trigger it.** Group them by what the assistant must do: one scenario per kind of handling, not one per trigger word (one emergency scenario covers every symptom the prompt lists, for example).
4. **One tool failure** on the main route.
5. **One request for a person,** handled by the prompt's escalation rules.
6. **One upset caller** on a main route, if tone matters to the team.

## All

Everything in Critical, plus:

1. **Routes** up to about 90% of engaging traffic. Past that, routes are one-off combinations of parts already tested.
2. **Variants:** every route with at least 1% of traffic gets one more scenario for each variant that makes up at least 15% of that route. A variant is a different ending, or a caller trait that changes the conversation (another language, a request for a person, a caller acting for someone else).
3. **Tool answers:** every answer kind that makes up at least 0.1% of its tool's calls appears in some scenario. Group answers by what the assistant must do differently, not one scenario per raw shape.
4. **Compliance situations twice,** with a different caller, different wording and a different point in the call, so one run can't decide a gate.
5. **State rules and failure triggers:** every one the tool catalog shows (a lookup that finds nothing, an action refused until the caller is verified). Tool failures are one scenario per kind of failure handling, not one per tool: if several tools fail and the prompt handles them the same way, one scenario covers them.
6. **Prompt-only branches:** a branch no call reached gets its own scenario (weight 0) only if it changes what the assistant does: a different tool call, a transfer or handoff, a different ending, or a failure path. A branch that only changes wording or which question is asked becomes a check on an existing scenario that passes through that point. A rule shared by every member is a check, never a scenario.
7. **Upset callers:** about 4 copies of existing scenarios with an upset caller, spread across the main routes.

*Without calls:* there are no shares, so items 1 to 3 become one scenario per route the prompt defines, one per variant the prompt handles differently, and one per tool answer kind the prompt says how to handle.

## Merging repeated tests

Before writing the list, merge scenarios that test the same handling:

- The same step reached with different wording, or by a different member that shares the rule, is one scenario.
- A family of near-identical branches (one per symptom, one per procedure, one per form type) becomes one scenario per kind of handling, plus at most one or two variants.
- **A situation that needs a tool to answer differently on a later call** (not found, then found after the caller corrects a detail) can't be run as written: each tool gives one answer per scenario. Plan it as two scenarios, or as one where the caller gets it right the first time. If the change itself is the point of the scenario, set it aside and say why.
- **Only merge branches that need the same answer from every tool and the same expected ending.** A simulation gives each tool one fixed answer for the whole conversation and grades one ending, so branches that differ in either can't be tested in one scenario. Keep them separate, or make one a variant.

In a large squad this usually cuts the All list by half or more. Record each merge in the scenario's `covers` field (the branch IDs it stands for).

## Situations the prompt doesn't cover

When the prompt is silent or contradicts itself:

1. **A small moment inside a normal scenario:** skip that moment when grading and check the rest.
2. **The whole point of the scenario is uncovered:** set it aside and add it to `owner_questions.md`. This only applies to scenarios with no traffic weight.
3. **Covered by a general rule** ("don't make things up"): keep it as a check.

## Checks before the gate

- Compare the share of scenarios (weighted) that end with a person with the tree's share. A plan that misses it gives a deflection rate that won't line up with production. *Without calls:* skip.
- Every expected ending is one of the endings in the category list.
- Every scenario that covers more than one branch uses one set of tool answers and one ending that fit all of them.
- Every compliance situation and every must-never-break rule is either a scenario or a check on at least one scenario.
- Show the user the Critical and All counts, the merges, and the scenarios set aside. They lock the list before `migration-simulations` builds anything.

## Weights

- Route and variant scenarios carry their traffic share. Every other kind (compliance, tool answers, failures, prompt-only) has weight 0 and is reported separately, so the weighted rate counts each real call once.
- Without calls, every weight is `null` and rates are reported unweighted.

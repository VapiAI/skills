# Suite levels: Critical and All

Pick the level with the user before writing any scenario. Both levels use the same flow map, the same check rules and the same mocks; they differ in how much of the map becomes simulations.

## Contents

- [Critical](#critical)
- [All](#all)
- [Choosing](#choosing)
- [Moving from Critical to All](#moving-from-critical-to-all)

## Critical

The smallest suite that can tell you whether a model change is safe. Usually 10 to 25 scenarios; a large squad may need up to about 40.

Include, in this order:

1. **Routes.** One scenario per route (a primary intent with its main steps), highest traffic first, until about 80% of conversations are covered or the next route is under about 3% of traffic. Without traffic data, one route per intent the prompt defines.
2. **Every ending at least once.** Resolved, transferred or handed off, callback, refused, caller hangs up. If a route already ends that way, it counts.
3. **The severe compliance situations, once each,** grouped by what the assistant must do: one emergency scenario covers every symptom the prompt lists.
4. **One tool failure on the main route.** The main tool returns an error or no result, so you see what the assistant says when things go wrong.
5. **One request for a person,** following the prompt's escalation rules.
6. **One upset caller** on a main route, if tone matters to the team (it usually does).

General rules that apply on every turn (identity checks before account details, required disclosures, never giving medical or legal advice) are not scenarios of their own: they are checks graded on every scenario where they can come up.

Leave out: rare routes, variants, every tool answer type, and branches only the prompt mentions.

## All

The exhaustive suite. Everything in Critical, plus:

- Routes up to about 90% of engaging traffic.
- Variants: every route with at least 1% of traffic gets one more scenario for each variant that makes up at least 15% of it (a different ending, another language, a request for a person, a caller acting for someone else).
- Every tool answer kind that makes up at least 0.1% of its tool's calls, grouped by what the assistant must do differently, and every state rule (not found, locked, refused until verified).
- Each compliance situation twice, with a different caller, wording and point in the call.
- Branches the prompt describes that no production call reached (`prompt_only` in the flow map), weighted zero, but only those that change what the assistant does (a different tool call, transfer, ending or failure path). The rest are checks on existing scenarios.
- Tool failures as one scenario per kind of failure handling, not one per tool.
- About 4 upset-caller copies of existing scenarios, and regression scenarios for every defect found earlier.
- Silence and timing cases (a caller who never speaks, a slow responder), in voice runs only: chat has no silence timer, so these can't finish in chat.

Merge scenarios that test the same handling before building: the same step reached with different wording, or a family of near-identical branches (one per symptom or form type), becomes one scenario per kind of handling. Only merge branches that need the same answer from every tool and the same ending, since each scenario has one mock answer per tool. Expect 60 to 200 scenarios for a busy assistant after merging, more for a large squad.

## Choosing

| Choose Critical when | Choose All when |
|---|---|
| A first look at whether the new model is viable | The model change is going to production at full traffic |
| The assistant is small or low-traffic | The assistant is high-traffic or handles money, health or legal exposure |
| Budget or concurrency is tight | The team wants a lasting regression suite |
| You need an answer today | Earlier Critical runs showed differences you need to understand |

Tell the user the size and the expected number of conversations before building: scenarios × runs per scenario × models compared. A 20-scenario Critical suite run twice on two models is 80 conversations.

## Moving from Critical to All

Build Critical first when in doubt. All reuses every Critical scenario unchanged, so results stay comparable. Add the extra scenarios as new resources and a new suite; never rewrite a Critical scenario to widen it.

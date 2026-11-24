# Suite levels: Critical and All

Pick the level with the user before writing any scenario. Both levels use the same flow map, the same check rules and the same mocks; they differ in how much of the map becomes simulations.

## Contents

- [Critical](#critical)
- [All](#all)
- [Choosing](#choosing)
- [Moving from Critical to All](#moving-from-critical-to-all)

## Critical

The smallest suite that can tell you whether a model change is safe. Usually 10 to 25 scenarios.

Include, in this order:

1. **Core workflows.** The paths that make up most of the traffic, highest share first, until about 80% of conversations are covered or the next path is under about 3% of traffic. One scenario per path, with a cooperative caller.
2. **Every ending at least once.** Resolved, transferred or handed off, callback, refused, caller hangs up. An ending nobody tests is the one that breaks quietly.
3. **Rules that must never break, in both directions.** Compliance lines, identity checks before account details, payment gates, required disclosures, escalation rules. For each, one scenario where the assistant must act and one where it must hold back.
4. **One tool failure on the main path.** The main tool returns an error or no result, so you see what the assistant says when things go wrong.
5. **One request for a human,** following the prompt's escalation rules.
6. **One upset caller** on the main path, if tone matters to the team (it usually does).

Leave out: rare paths, caller variations, every tool answer type, language variants unless a language is a large share of traffic, and paths only the prompt mentions.

## All

The exhaustive suite. Everything in Critical, plus:

- Every path in the flow map down to a small share of traffic (for example 0.5%), and variants of the big paths (a caller who gives information out of order, changes their mind, asks a side question).
- Every tool answer type that makes up a meaningful share of that tool's calls, and every state the tools can be in (not found, locked, already done).
- Each compliance situation at least twice, with different callers.
- Paths the prompt describes that no production call reached (`prompt_only` in the flow map), weighted zero.
- Language variants, silence and timing cases (voice only), and about 8 upset-caller copies of existing scenarios.
- Regression scenarios for every defect found earlier.

Expect 60 to 200 scenarios for a busy assistant, more for a squad.

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

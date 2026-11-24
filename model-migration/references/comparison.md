# Comparing the two copies and explaining differences

How to read the side-by-side results from `migration-simulations` and decide what each difference means.

## Contents

- [Compare like with like](#compare-like-with-like)
- [What to report](#what-to-report)
- [Behavior signals](#behavior-signals)
- [Explaining a difference](#explaining-a-difference)
- [Noise](#noise)

## Compare like with like

- Compare only scenarios that produced a graded result on both copies. A conversation that errored, timed out or was canceled on one copy is an execution problem, reported separately and rerun; it is not a model result.
- Set aside test artifacts first: the caller ended the chat before the assistant spoke; the conversation hit the turn limit after a transfer (a mocked transfer doesn't end the chat); a tool call reached a tool with no mock; repeated transfer calls after a mocked transfer succeeded.
- With several runs per scenario, judge each scenario by its majority result, and list the scenarios whose runs disagree.

## What to report

In this order:

1. **The team's metrics** from `metrics.md`, computed the same way for both copies. Compute rates from each run item's actual ending (the ending evaluation's `extractedValue`), not from whether it passed. With traffic weights from the flow map: weighted rate = sum of (weight × outcome) divided by the sum of weights, over scenarios with weight above 0 that were graded on both copies; report weight-0 scenarios (rules, failures, prompt-only) separately. Next to each, the production baseline from `metric_baselines.md`, or a note that there is none because the flow map was skipped. Simulated rates won't match production exactly: endings a simulation can't produce (a caller hanging up partway, silence timeouts) only happen in production. Judge the new model by the difference between the two copies, not by the gap to production.
2. **Must-never-break rules:** every failure on either copy, with the scenario and transcript evidence. One failure of a critical rule is a blocker until explained.
3. **Rule and path checks:** pass rates per copy.
4. **Every-check pass rate:** the share of scenarios that passed every evaluation.
5. **Behavior signals** (below), per copy.
6. **The largest differences:** the scenarios where the copies differ most, each with a one-line explanation.

## Behavior signals

Count these from the transcripts of both copies. Checks often miss them, and they are where the new models differ most (see [Model tendencies](model-tendencies.md)).

| Signal | How to count |
|---|---|
| Words per turn, questions per turn, exclamation marks | Over all assistant turns |
| Acknowledgment phrases per conversation | "sorry", "I understand", "frustrat", "apolog", "I hear"; note how many come from lines the prompt scripts |
| Tool calls with nothing said first | Tool calls with no assistant text in the same response or just before |
| Actions announced without a tool call | "transferring you", "I've sent", "I'll text" with no matching tool call in that response |
| Goodbye without the end-call tool | Closing lines with no end-call tool call |
| Empty or symbol-only replies | Assistant turns with no words |
| Tools the prompt never names | Calls to tools absent from the prompt text |
| "Anything else?" asked | Conversations where it appears, and after which kinds of result |
| Markdown in speech | Turns containing `**`, `#`, or list markers |
| Repeated lines | The same assistant line twice in a row, and the most frequent closing lines across conversations |

## Explaining a difference

Read the transcripts behind each large difference on both copies before deciding anything. File it as one of:

| Class | Typical evidence | Next step |
|---|---|---|
| The test: grader | The reply meets the rule, but the evaluation text is narrower than the rule, or grades a tool line as speech | Reword the evaluation once; rerun both copies |
| The test: caller | The simulated caller never said the thing that triggers the step, or ended early | Fix the scenario once; rerun both copies |
| The test: mock | The mock answered something the real tool never would | Fix the mock once; rerun both copies |
| The prompt | Two rules disagree, or no rule covers the situation; the models resolve it differently | Ask the owner; write the answer into the prompt for both copies |
| The model | The prompt states the rule plainly and the new model breaks it, consistently | Pick a fix from [Fixes](fixes.md) |
| The old model | 4.1 broke a stated rule that the new model keeps | Note it. It is a gain, but it may change a metric (for example more transfers where the rules require them) |

On a first suite, expect about half of the differences to be the test or the prompt, not the model. Scenarios are shared by both copies: fix a test once in the scenario, then rerun both copies.

## Noise

- Simulated conversations vary from run to run, even on the same setup.
- One conversation is worth 100 / (scenarios × runs) points. On a 20-scenario suite run once, one conversation is 5 points. Treat a difference of one or two conversations as noise.
- Call a difference real only when the same scenario fails in most runs on one copy and passes in most runs on the other. Repeat the scenarios that matter most before drawing a conclusion from them.

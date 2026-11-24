# gpt-5.6-luna

Notes for moving an assistant from GPT-4.1 to `gpt-5.6-luna`. Read [Model tendencies](model-tendencies.md) first; everything listed there for both models applies.

## Recommended settings

Use low reasoning and fast mode. Fields to set inside the assistant's existing `model` object (keep `messages`, `tools`, `toolIds` and every other field as they are):

```json
{
  "model": "gpt-5.6-luna",
  "reasoningEffort": "low",
  "serviceTier": "fast",
  "promptCacheRetention": "24h"
}
```

- `reasoningEffort: "low"` (recommended). Higher effort did not fix behavior problems that prompt changes did.
- `serviceTier: "fast"` (recommended) is fast mode: lower response time at a higher per-token rate.
- `promptCacheRetention: "24h"` keeps the prompt cached across calls. It only pays off when per-call values (date, caller number, IDs) sit in one block at the end of the prompt.
- Don't rely on `temperature` or `maxTokens` to shape behavior on this model; shape it with the prompt. Check that `maxTokens` isn't set low: reasoning can use output tokens, and a low cap shows up as short or empty replies.
- Check `fallbackModels`: remove GPT-4.1 entries carried over from the old configuration, and set the production fallback you want explicitly before rollout.

## What to expect

- Luna is the faster, lower-cost of the two models. Confirm cost per minute and latency on your own assistant (step 8 of the skill) or in Vapi's model benchmarks.
- Rule adherence matched or beat GPT-4.1 on the real-world assistants we tested, before any prompt change.
- Like Terra, Luna sounds more neutral than GPT-4.1. Plan the tone work in [Fixes](fixes.md#tone-and-warmth) from the start rather than after rollout.

## Where Luna differs from Terra

| Behavior | What to do |
|---|---|
| More likely to say it's doing something ("connecting you now", "I'll text you the link") without calling the tool | Line and tool in the same response; never announce an action without its tool call |
| Follows counted steps ("transfer on the third request") less exactly than Terra | Check counted steps in the suite, and state the count plainly in the step itself |
| More often answers and waits, with no next step | A next-action table (see [Fixes](fixes.md#conversation-flow)) |

## A prompt structure that works for Luna

A structure that worked: one short conversation-state section that the rest of the prompt points to:

- **Open request:** keep the caller's oldest unresolved request through side questions; "okay" or "thanks" doesn't close it.
- **Next action:** after each kind of answer or tool result, the specific next step, before any generic "anything else?".
- **Refusals:** every "no" gives the reason, one alternative and the next step; at most one retry after a decline; never re-ask an answered question.
- **Truthfulness:** claim an action only after a tool confirms it.
- **Introduce yourself once per call.**

Keep each scripted line next to the rule that triggers it, and when merging sections, keep the fallbacks (what to say after a failed lookup, what to do when the caller says nothing useful).

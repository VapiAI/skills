# gpt-5.6-terra

Notes for moving an assistant from GPT-4.1 to `gpt-5.6-terra`. Read [Model tendencies](model-tendencies.md) first; everything listed there for both models applies.

## Recommended settings

Use low reasoning and fast mode. Fields to set inside the assistant's existing `model` object (keep `messages`, `tools`, `toolIds` and every other field as they are):

```json
{
  "model": "gpt-5.6-terra",
  "reasoningEffort": "low",
  "serviceTier": "fast",
  "promptCacheRetention": "24h"
}
```

The notes on these settings, `maxTokens` and `fallbackModels` in [Luna](luna.md#recommended-settings) apply here too.

## What to expect

- Terra is the more accurate and capable of the two models. Confirm cost per minute and latency on your own assistant (step 8 of the skill) or in Vapi's model benchmarks.
- The most literal of the models: the strongest at following stated rules and counted steps.
- Like Luna, Terra sounds more neutral than GPT-4.1. Plan the tone work in [Fixes](fixes.md#tone-and-warmth) from the start, and include upset-caller scenarios so the comparison shows the gap.

## Where Terra differs from Luna

| Behavior | What to do |
|---|---|
| More likely to call a tool with nothing said first, especially the first lookup of a call (silence on a voice call) | Script the line with the tool in the same response; at call start, say what to say before the first lookup |
| Keeps counted steps exactly ("transfer on the third request") | Nothing to fix; make sure the counts in the prompt are the ones you want |
| Plainest style and slightly shorter turns | The tone fixes in [Fixes](fixes.md#tone-and-warmth) |

For a prompt written for GPT-4.1, the conversation-state structure in [Luna](luna.md#a-prompt-structure-that-works-for-luna) helps Terra too.

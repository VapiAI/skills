# Model card: gpt-6.1-terra

- **Target model:** `gpt-6.1-terra`
- **Starting model:** GPT-4.1
- **Last updated:** 2026-11-26
- **Evidence:** GPT-4.1 and Terra on the same simulated scenarios across several real-world assistants (support, collections, applications and scheduling, including a multi-assistant squad), each on its unchanged prompt. Examples are anonymized.

This card is a starting point. It covers the main patterns we saw when we tested 6.1 Terra against GPT-4.1 on several real assistants. Your assistant may behave differently in ways our tests didn't show, so test your own key scenarios before you switch.

## Recommended settings

Use low reasoning and fast mode. Set these fields inside the assistant's existing `model` object, and keep `messages`, `tools`, `toolIds` and every other field as they are:

```json
{
  "model": "gpt-6.1-terra",
  "reasoningEffort": "low",
  "serviceTier": "fast",
  "promptCacheRetention": "24h"
}
```

- `reasoningEffort: "low"` is the setting these patterns were measured with.
- `serviceTier: "fast"` is fast mode: lower response time at a higher per-token rate.
- `promptCacheRetention: "24h"` keeps the prompt cached across calls. It only pays off when per-call values (date, caller number, IDs) sit in one block at the end of the prompt.
- Set `"provider": "openai"` if the current model is from another provider.
- Don't rely on `temperature` or `maxTokens` to shape behavior; shape it with the prompt. Check that `maxTokens` isn't low: reasoning can use output tokens, and a low cap shows up as short or empty replies.
- Check `fallbackModels`: remove GPT-4.1 entries carried over from the old configuration, and set the production fallback explicitly before rollout.

## What to expect

- According to benchmarks the Vapi team ran, gpt-6.1-terra scored competitively on reasoning and latency. Confirm latency and cost per minute on your own assistant (step 8 of the skill).
- Terra followed rules at least as well as GPT-4.1 on the assistants we tested, before any prompt change.
- It reads the prompt more literally than GPT-4.1, down to field names and trigger words, and applies global closing steps even where they don't fit. Include scenarios where a tool result words things differently from the prompt, language switches, and endings after a transfer, so the comparison shows them.
- It sounds plainer than GPT-4.1. Plan the tone work in [Fixes](fixes.md#tone-and-warmth) from the start, and include upset-caller scenarios so the comparison shows the gap.

## Behaviors compared with GPT-4.1

These are tendencies we saw on some assistants, not on every call, ordered by how much they're likely to affect calls. Each pattern held on more than one assistant. Each one pairs what we saw with a prompt habit that helps. Where our tests checked a prompt change, the card says what happened.

### Match names and triggers exactly

- **What we saw:** 6.1 Terra can match field names, labels and trigger words exactly as the prompt writes them, more than GPT-4.1, so a prompt that checked a `verified` field while the tool returned `"state": "VERIFIED"` led it to treat verified callers as unverified. On some assistants a rule triggered by the word "Spanish" didn't fire for callers who simply spoke Spanish, and a list of urgent keywords applied to every mention of those words.
- **For your prompt:** Name each tool-result field once, exactly as the tool returns it, where the decision is made, delete lines about statuses the assistant never sees, and describe triggers by meaning, such as "if the caller's first message is in Spanish or asks for Spanish". This worked in our tests.

### Write down the common situations

- **What we saw:** 6.1 Terra doesn't invent answers the way GPT-4.1 sometimes did. When the prompt doesn't cover a situation, it can say it isn't sure and stop there, or offer a person sooner than GPT-4.1 did.
- **For your prompt:** Write down what to do in the situations that come up often, including the next step to offer.

### Say where each closing step applies

- **What we saw:** 6.1 Terra can apply a global closing step in every branch, even where it doesn't fit, such as offering a survey after a transfer, where GPT-4.1 usually skipped it.
- **For your prompt:** Give each closing step one place and state its scope there once, delete duplicate closing rules and competing "close the call" endings in branches, and tie the order to the end-call tool by name, for example "Call `end_call` only after the caller answers the survey question." This worked in our tests.

### Write complete tool descriptions

- **What we saw:** 6.1 Terra gives tool descriptions, parameter descriptions and the text in tool results more weight than GPT-4.1 did. When a tool returns text meant for the caller, it can read it out right away and then say the prompt's version too.
- **For your prompt:** Write complete tool descriptions that agree with the prompt, keep instructions out of tool results, and keep each script in one place, either the tool result or the prompt.

### Attach only the tools you need

- **What we saw:** 6.1 Terra looks things up before answering, sometimes even when the question doesn't need it, where GPT-4.1 often answered from memory. It can also call attached tools the prompt never mentions.
- **For your prompt:** Attach only the tools the assistant needs, and say which questions it can answer without a lookup.

### Plan for tool failures

- **What we saw:** 6.1 Terra follows written steps strictly and in order, more than GPT-4.1, and keeps counted steps, such as "transfer on the third request", exactly. It doesn't claim an action succeeded when a tool failed.
- **For your prompt:** Check that the counts and conditions in the prompt are the ones you want, and write a fallback line and a next step for each tool failure that matters to you.

### Mark lines that must be said exactly

- **What we saw:** 6.1 Terra says short sample lines word for word more often than GPT-4.1, but it can reword a required script to fit a general rule, such as a rule to say numbers as words.
- **For your prompt:** Label examples clearly and give two or three different ones, and mark lines that must be said exactly with "Say exactly:", making sure no other rule contradicts them.

### Plan for warmth

- **What we saw:** 6.1 Terra sounds plainer than GPT-4.1, with turns about half as long and almost no exclamation marks or filler. It adds a short acknowledgment of bad news more often than GPT-4.1 did, and follows rules that limit acknowledgments exactly.
- **For your prompt:** Loosen or narrow rules that ban acknowledgments, and when the assistant can't do what was asked, have it explain why, offer one alternative and say what happens next.

### Pair each line with its tool call

- **What we saw:** 6.1 Terra usually says its line before a transfer, but on some assistants it called a tool before saying anything, which the caller hears as silence. We didn't see it claim an action that no tool confirmed.
- **For your prompt:** Tie the line and the tool call together in one instruction, for example: "Say 'Let me transfer you to billing.' and call `transfer_call` in the same response."

### Write the next step after each answer

- **What we saw:** 6.1 Terra answers what the caller asked and then waits unless a step in the prompt says what comes next, where GPT-4.1 often offered the next step on its own.
- **For your prompt:** Write in the prompt what the next step should be after each kind of answer or tool result.

## How this changes your prompt

The habits above come down to writing down what the team relied on GPT-4.1 to do on its own: field names and values exactly as your tools return them, triggers described by meaning, where each closing step applies, what to say with each tool call, the next step after each kind of answer, and which tools exist. [Fixes](fixes.md) lists the wording that works for each symptom.

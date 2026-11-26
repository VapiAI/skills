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

Each pattern held on more than one assistant. They're tendencies, not guarantees, ordered by how much they're likely to affect calls.

### Taking the system prompt literally

- **GPT-4.1** read the system prompt for its intent and filled in what it left unsaid.
- **Terra** **matches field names, labels and trigger words in the prompt exactly, even when a tool result says the same thing a different way.** In one case the prompt checked a `verified` field while the tool returned `"state": "VERIFIED"`, and Terra treated verified callers as unverified. A language rule triggered by the word "Spanish" didn't fire for callers who simply spoke Spanish, and a list of urgent keywords was applied to every mention of those words, even where they didn't apply.
- **For your prompt:** Name each tool-result field exactly as the tool returns it, once, where the decision is made, and delete lines about statuses the assistant never sees. Describe a trigger by meaning, such as "if the caller's first message is in Spanish or asks for Spanish", not as a list of words to match. This change fixed it in our tests.

### Situations the prompt doesn't cover

- **GPT-4.1** made up an answer from its own general knowledge when the prompt and tools had none, and those answers were sometimes wrong.
- **Terra** doesn't invent answers. It says it isn't sure, and **sometimes stops there without offering a next step, or offers a person sooner than GPT-4.1 did.**
- **For your prompt:** Write down what the assistant should do in the situations that come up often, including the next step it should offer.

### Global rules in every branch

- **GPT-4.1** applied general rules such as a closing question or a survey most of the time, and skipped them where they clearly didn't fit.
- **Terra** **applies global closing steps in every branch, even where they don't fit, for example offering a survey after a transfer.**
- **For your prompt:** Give each closing step one place in the prompt and state its scope there once, for example "before your closing line" or "not after a transfer". Delete duplicate closing rules and any "close the call" endings inside branches that compete with it, and tie the order to the end-call tool by name, for example: "Call `end_call` only after the caller answers the survey question." This change fixed it in our tests.

### Tool descriptions and tool results

- **GPT-4.1** followed the system prompt when a tool's description or result disagreed with it.
- **Terra** gives tool descriptions, parameter descriptions and the text in tool results more weight than the system prompt. When a tool returns text meant for the caller, it reads it out straight away, and may then say the prompt's version too.
- **For your prompt:** Write complete descriptions that agree with the system prompt. Keep instructions out of tool results, and keep any script in one place, either the tool result or the prompt, not both.

### Using tools

- **GPT-4.1** often answered from memory and skipped lookups the prompt required.
- **Terra** looks things up before answering every time, sometimes even when the question doesn't need it. It also calls tools that are attached to the assistant even when the prompt never mentions them.
- **For your prompt:** Attach only the tools the assistant needs, and say which questions it can answer without a lookup.

### Following procedures

- **GPT-4.1** sometimes bent procedures when a request looked simple, for example by skipping verification or a disclosure.
- **Terra** follows the written steps strictly and in order, and **keeps counted steps (such as "transfer on the third request") exactly.** It doesn't claim an action succeeded when a tool failed.
- **For your prompt:** Make sure the counts and conditions in the prompt are the ones you want, and write a fallback line and a next step for each tool failure that matters to you.

### Scripted lines

- **GPT-4.1** treated sample lines in the prompt as inspiration and varied the wording.
- **Terra** says short sample lines word for word, but it may reword a required script to satisfy a general rule, such as a rule to say numbers as words.
- **For your prompt:** Label examples clearly and give two or three different ones. Mark lines that must be said exactly with "Say exactly:", and make sure no other rule contradicts them.

### Empathy and warmth

- **GPT-4.1** sounded warm without being told to, with enthusiasm, reassurance and long turns.
- **Terra** sounds plainer, with turns about half as long and almost no exclamation marks or filler. It adds a short acknowledgment of bad news more often than GPT-4.1 did, and follows rules that limit acknowledgments exactly.
- **For your prompt:** Loosen or narrow any rules that ban acknowledgments. When the assistant can't do what was asked, have it explain why, offer one alternative and say what happens next.

### Saying and doing

- **GPT-4.1** usually paired what it said with the matching tool call.
- **Terra** usually says its line before a transfer, but on some assistants it calls a tool before saying anything, which the caller hears as silence. It never claims to have done something that no tool confirmed.
- **For your prompt:** Tie the line and the tool call together in one instruction, for example: "Say 'Let me transfer you to billing.' and call `transfer_call` in the same response."

### Offering the next step

- **GPT-4.1** offered the obvious next step on its own, for example asking "Is there anything else I can help with?"
- **Terra** answers what the caller asked and then waits, unless a step in the prompt says what comes next.
- **For your prompt:** Write in the prompt what the next step should be after each kind of answer or tool result.

## How this changes your prompt

Anything the team relied on GPT-4.1 doing implicitly has to be written down: field names and values exactly as your tools return them, triggers described by meaning, where each global closing step applies, what to say with each tool call, the next step after each kind of answer, and which tools exist. [Fixes](fixes.md) lists the wording that works for each symptom.

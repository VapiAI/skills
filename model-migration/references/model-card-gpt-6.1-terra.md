# Model card: gpt-6.1-terra

- **Target model:** `gpt-6.1-terra`
- **Starting model:** GPT-4.1
- **Last updated:** 2026-11-26
- **Evidence:** GPT-4.1 and Terra on the same simulated scenarios across several real-world assistants (support, collections, applications and scheduling, including a multi-assistant squad), each on its unchanged prompt. Examples are anonymized.

This card is a starting point. It covers the main patterns we saw when we tested 6.1 Terra against GPT-4.1 on several real assistants. Your assistant may behave differently in ways our tests didn't show, so test your own key scenarios before you switch.

## Contents

- [Recommended settings](#recommended-settings)
- [What to expect](#what-to-expect)
- [How to use this card](#how-to-use-this-card)
- [Behaviors compared with GPT-4.1](#behaviors-compared-with-gpt-41)
- [How this changes your prompt](#how-this-changes-your-prompt)

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
- Terra has good intelligence; most of what to watch is how the prompt names fields and where closing steps apply.
- It reads the prompt more literally than GPT-4.1, down to field names and trigger words, and applies global closing steps even where they don't fit. Include scenarios where a tool result words things differently from the prompt, language switches, and endings after a transfer, so the comparison shows them.
- It sounds plainer than GPT-4.1. Plan the tone work in [Fixes](fixes.md#tone-and-warmth) from the start, and include upset-caller scenarios so you can hear whether the tone suits your callers.

## How to use this card

Apply these changes while building the gpt-6.1-terra copy, so the first version tested is already adapted:

1. For each pattern below, check the prompt and tools for the shape under **In the prompt**. Only apply the **Change** where that shape is there; leave everything else as it is.
2. Adapt the before/after example to the prompt's own wording. Never paste the example text.
3. Follow each **Don't**: these are variants that made things worse in our tests or common mistakes with this pattern.
4. Show the user the list of changes you made (pattern, where, one line each) in `review.md`, then build the copy. No approval step.
5. Add each applied pattern's **Check with** scenarios to the suite. During the comparison runs, watch for the **In transcripts** signals; if one still shows, treat it as a step 7 fix.

## Behaviors compared with GPT-4.1

### Match names and triggers exactly

- **In the prompt:** a tool-result field or value named differently from what the tool returns, or a trigger written as a single keyword or keyword list.
- **Change:** name each field and value exactly as the tool returns it, where the decision is made, and describe triggers by meaning.
  - *Before:* "If `verified` is true, continue." / "If the caller says Spanish, switch to Spanish."
  - *After:* "If `state` is `VERIFIED`, continue." / "If the caller's first message is in Spanish or asks for Spanish, switch to Spanish."
- **Don't:** add a list of trigger keywords; the model applies a list to every mention of those words.
- **In transcripts:** verified callers treated as unverified, or a rule that should fire not firing.
- **Check with:** a tool result worded differently from the prompt, and a caller who switches language without naming it.

### Aim for good prompt coverage

- **In the prompt:** common requests from the flow map with no line saying what to say or do.
- **Change:** for each common request the prompt doesn't cover, write what to say or do, beside the rule it belongs to.
  - *Before:* (nothing about the request)
  - *After:* "Asking to speed up a pending refund doesn't qualify for a transfer: give the expected date."
- **Don't:** insert the new sentence between a general rule and its fallback, or point it at another rule; in our tests that stopped transfer offers on nearby requests.
- **In transcripts:** "I'm not sure" with no next step, or a person offered for a request the assistant could handle.
- **Check with:** the uncovered request, plus a nearby request that should still reach a person.

### Say where each closing step applies

- **In the prompt:** a closing step written in several places, or branches that end with their own "close the call" line.
- **Change:** give each closing step one place, state its scope there once, delete competing endings, and tie the order to the end-call tool.
  - *Before:* "At the end of every call, ask the survey question." plus "Thank them and end the call." in each branch.
  - *After:* "Before you call `end_call`, ask the survey question, unless the call was transferred." (branch endings removed)
- **Don't:** copy the closing steps into each branch.
- **In transcripts:** a closing step where it doesn't fit, such as a survey offered after a transfer.
- **Check with:** a transferred call, a caller who says goodbye first, and a normal close.

### Write complete tool descriptions

- **In the prompt and tools:** the same script in a tool result and in the prompt, or a tool or parameter description that disagrees with the prompt.
- **Change:** make tool and parameter descriptions agree with the prompt, and keep each script in one place, at a step every call passes.
  - *Before:* the notice in the verify tool's result and in two prompt sections.
  - *After:* "Right after the name check, before anything else including a transfer, say the notice." (removed elsewhere)
- **Don't:** leave a copy of the script in a tool result.
- **In transcripts:** a scripted line said twice, or a tool's returned text read out and then the prompt's version too.
- **Check with:** a caller who asks for a person early, to confirm the notice is still said once.

### Attach only the tools you need

- **In the prompt and tools:** attached tools the prompt never names, or a list of questions that need no lookup.
- **Change:** detach tools the assistant should never call; where the prompt lists questions that need no lookup, also name the ones that still do.
  - *Before:* "Card declines and PIN resets don't need a lookup."
  - *After:* "Card declines and PIN resets don't need a lookup; questions about their own application or when their card will arrive still do."
- **Don't:** write a one-sided "no lookup needed" list; in our tests it suppressed lookups that were needed.
- **In transcripts:** calls to tools the prompt never mentions, or lookups for questions that don't need one.
- **Check with:** a question that needs no lookup and one that does.

### Plan for tool failures

- **In the prompt:** a step that calls a tool with no line for what happens if it fails.
- **Change:** in that step, give each failure that matters a fallback line and a next step the prompt already offers.
  - *Before:* "Set up the callback."
  - *After:* "Set up the callback. If it fails, say you couldn't set it up just now, then send the link."
- **Don't:** invent a next step the prompt doesn't define.
- **In transcripts:** a failure line with no next step, or the call ending after a failed tool.
- **Check with:** failing tool results (errors and blocked results) for each tool that matters.

### Mark lines that must be said exactly

- **In the prompt:** required lines (disclosures, verification asks) next to a general rule that would rewrite them, such as numbers-as-words; or a single sample line for something that should vary.
- **Change:** mark required lines with "Say exactly:" and exempt them from rules that would rewrite them; for lines that should vary, describe what they contain.
  - *Before:* "Ask for their 10-digit phone number." with a global numbers-as-words rule.
  - *After:* "Say exactly: 'What's your 10-digit phone number?' (Lines marked Say exactly are exempt from the numbers rule.)"
- **Don't:** give a single sample line for something that should vary; it gets repeated on every call.
- **In transcripts:** a required script reworded, or the same sample line on every call.
- **Check with:** the scenarios that reach each required line.

### Plan for warmth

- **In the prompt:** broad bans on acknowledgments or apologies, or refusal lines with no reason or next step.
- **Change:** narrow acknowledgment bans to filler; when the assistant can't do what was asked, have it give the reason, one alternative and what happens next.
  - *Before:* "Never apologize or acknowledge more than once."
  - *After:* "Skip filler like 'Got it'. When you can't do something, say why, offer one option this prompt gives, and say what happens next."
- **Don't:** rely on a general "be warm" line; it made no difference in earlier tests.
- **In transcripts:** plain refusals with no reason or next step, or no acknowledgment when the caller shares bad news.
- **Check with:** an upset caller and a request the assistant has to decline.

### Pair each line with its tool call

- **In the prompt:** a spoken line and its tool call written as separate steps or bullets.
- **Change:** put the line and the tool call in one instruction.
  - *Before:* "Say 'Let me transfer you to billing.'" in one step and "Call `transfer_call`." in another.
  - *After:* "Say 'Let me transfer you to billing.' and call `transfer_call` in the same response."
- **Don't:** split the line and the call across steps.
- **In transcripts:** a tool call with no line before it, which the caller hears as silence.
- **Check with:** every transfer path and the first lookup of a call.

### Write the next step after each answer

- **In the prompt:** a step that calls a tool or answers a question with nothing saying what comes next.
- **Change:** after each kind of answer or result, write what comes next.
  - *Before:* "Process the payment."
  - *After:* "Process the payment. After a successful payment, ask whether there's anything else you can help with."
- **Don't:** script a next-step line that isn't true for every result, such as "your payment was approved" when a payment can be pending; the model skips the line when it doesn't fit.
- **In transcripts:** the assistant answering and then waiting, where GPT-4.1 offered the next step.
- **Check with:** each result the tool can return (approved, pending, declined).

## How this changes your prompt

The changes above come down to writing down what the team relied on GPT-4.1 to do on its own: field names and values exactly as your tools return them, triggers described by meaning, where each closing step applies, what to say with each tool call, the next step after each kind of answer, and which tools exist. Apply them while building the copy, as **How to use this card** says. [Fixes](fixes.md) lists wording for any symptom that still shows in the comparison runs.

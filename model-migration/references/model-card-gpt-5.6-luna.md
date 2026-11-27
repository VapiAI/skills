# Model card: gpt-5.6-luna

- **Target model:** `gpt-5.6-luna`
- **Starting model:** GPT-4.1
- **Last updated:** 2026-11-26
- **Evidence:** GPT-4.1 and Luna on the same simulated scenarios across several real-world assistants (support, collections, applications and scheduling, including a multi-assistant squad), each on its unchanged prompt. Examples are anonymized.

This card is a starting point. It covers the main patterns we saw when we tested 5.6 Luna against GPT-4.1 on several real assistants. Your assistant may behave differently in ways our tests didn't show, so test your own key scenarios before you switch.

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
  "model": "gpt-5.6-luna",
  "reasoningEffort": "low",
  "serviceTier": "fast",
  "promptCacheRetention": "24h"
}
```

- `reasoningEffort: "low"`. Higher effort did not fix behavior problems that prompt changes did.
- `serviceTier: "fast"` is fast mode: lower response time at a higher per-token rate.
- `promptCacheRetention: "24h"` keeps the prompt cached across calls. It only pays off when per-call values (date, caller number, IDs) sit in one block at the end of the prompt.
- Set `"provider": "openai"` if the current model is from another provider.
- Don't rely on `temperature` or `maxTokens` to shape behavior; shape it with the prompt. Check that `maxTokens` isn't low: reasoning can use output tokens, and a low cap shows up as short or empty replies.
- Check `fallbackModels`: remove GPT-4.1 entries carried over from the old configuration, and set the production fallback explicitly before rollout.

## What to expect

- According to benchmarks the Vapi team ran, Luna is a smaller model that trades some intelligence for the lowest cost, and it needs more prompt tuning to reach parity. In our tests it cost about a third as much as gpt-5.6-terra and responded faster than Terra but slower than GPT-4.1. Confirm latency and cost per minute on your own assistant (step 8 of the skill).
- It needs fuller, more specific prompts than GPT-4.1, though it kept stated rules about as well as GPT-4.1 on most assistants we tested, before any prompt change.
- It sounds more neutral than GPT-4.1. Plan the tone work in [Fixes](fixes.md#tone-and-warmth) from the start, and include upset-caller scenarios so the comparison shows the gap.

## How to use this card

Apply these changes while building the gpt-5.6-luna copy, so the first version tested is already adapted:

1. For each pattern below, check the prompt and tools for the shape under **In the prompt**. Only apply the **Change** where that shape is there; leave everything else as it is.
2. Adapt the before/after example to the prompt's own wording. Never paste the example text.
3. Follow each **Don't**: these are variants that made things worse in our tests or common mistakes with this pattern.
4. Show the user the list of changes you made (pattern, where, one line each) in `review.md`, then build the copy. No approval step.
5. Add each applied pattern's **Check with** scenarios to the suite. During the comparison runs, watch for the **In transcripts** signals; if one still shows, treat it as a step 7 fix.

## Behaviors compared with GPT-4.1

### Point each branch to your closing steps

- **In the prompt:** branches, declined offers included, that end with their own "close the call" line, and closing steps (a closing question, a link) written somewhere else.
- **Change:** write the closing steps and their exceptions once, and replace each branch's "close the call" with a pointer that names the next step.
  - *Before:* "If they turn down the callback, thank them and close the call."
  - *After:* "If they turn down the callback, that's fine. Then send the link and follow # Closing." (exceptions to sending the link written once, in # Closing)
- **Don't:** copy the exceptions or the full closing steps into every branch; in our tests repeating them added nothing, and it leaves the same rule in several places.
- **In transcripts:** a branch that closes the call without the closing question or link, most often after the caller turns down an offer. If this matters for your calls, Sapien or 6.1 Terra may suit them better.
- **Check with:** a caller who turns down an offer, a caller who says they'll call back later, and a normal close.

### Write exactly what you mean

- **In the prompt:** optional wording ("you can offer", "you may") for a step the team wants on every call, or a status check against a value the tools don't return.
- **Change:** write each required step as a step, and make every status the prompt checks one the tools actually return.
  - *Before:* "You can offer to text them the payment link."
  - *After:* "Offer to text them the payment link."
- **Don't:** turn every optional line into a requirement; change only the ones the team wants on every call.
- **In transcripts:** an offer the team expects that never comes, or a rule answered by its letter where GPT-4.1 worked out what was meant.
- **Check with:** the scenarios that should reach each required offer, and a tool result with each status the prompt checks.

### Aim for good prompt coverage

- **In the prompt:** common requests from the flow map with no line saying what to say or do.
- **Change:** for each common request the prompt doesn't cover, write what to say or do beside the rule it belongs to.
  - *Before:* (nothing about the request)
  - *After:* "Asking when an order will ship doesn't qualify for a transfer: give the shipping estimate."
- **Don't:** insert the new sentence between a general rule and its fallback, or point it at another rule; in our tests that stopped transfers on nearby requests.
- **In transcripts:** a transfer or callback for a request the assistant could handle, or a nearby request that no longer reaches a person. If this matters for your calls, 5.6 Terra may suit them better.
- **Check with:** the uncovered request, plus a nearby request that should still reach a person.

### Write complete tool descriptions

- **In the prompt and tools:** a tool or parameter description that disagrees with the prompt or leaves a value open, or a tool whose description invites a call the prompt forbids.
- **Change:** give every tool and parameter a complete description that matches the prompt.
  - *Before:* parameter `amount_type`: "The amount type."
  - *After:* parameter `amount_type`: "Amount type. Always `CUSTOM`: the amount is whatever the caller chose."
- **Don't:** fix a disagreement in the prompt only; change the description too, since the description can win.
- **In transcripts:** a wrong or invented parameter value, or a tool called where the prompt says not to.
- **Check with:** calls that use each tool's parameters with an unusual value, and the paths where the prompt says not to call a tool.

### Plan for warmth

- **In the prompt:** broad bans on acknowledgments or apologies, or refusal lines with no reason or next step.
- **Change:** narrow acknowledgment bans to filler; when the assistant has to say no, have it give the reason, one alternative and what happens next.
  - *Before:* "Acknowledge the caller at most once. If you can't help, say so."
  - *After:* "Skip filler on routine answers. If you can't help, say why, offer one option this prompt gives, and say what happens next."
- **Don't:** rely on a general "be warm" line; it made no difference in earlier tests.
- **In transcripts:** plain refusals with no reason or next step, or no acknowledgment when the caller shares bad news.
- **Check with:** an upset caller and a request the assistant has to decline.

### Write the next step after each answer

- **In the prompt:** a step that calls a tool or answers a question with nothing saying what comes next.
- **Change:** after each kind of answer and each tool result, write what comes next.
  - *Before:* "Give them their balance."
  - *After:* "Give them their balance, then ask whether they'd like to make a payment today."
- **Don't:** script a next-step line that isn't true for every result, such as "your payment was approved" when a payment can be pending; the model skips the line when it doesn't fit.
- **In transcripts:** the assistant answering and then waiting for the caller to lead, or the close starting in the same turn as a confirmation.
- **Check with:** each result the tool can return (approved, pending, declined).

### Plan for tool failures

- **In the prompt:** a step that calls a tool with no line for what happens if it fails, or a failure line that states the failure and stops.
- **Change:** give each failure that matters a fallback line that ends with the next step as a question, using a next step the prompt already offers.
  - *Before:* "If the payment is blocked, explain why."
  - *After:* "If the payment is blocked, explain why and say no payment was made, then ask: 'Would you like to pay a different amount instead?'"
- **Don't:** invent a next step the prompt doesn't define.
- **In transcripts:** a failure line with no next step, or the caller sent elsewhere after a failed tool.
- **Check with:** failing tool results (errors and blocked results) for each tool that matters.

### Mark lines that must be said exactly

- **In the prompt:** required lines next to a rule that would cut or rewrite them, such as a numbers-as-words or turn-length rule; or a single sample line for something that should vary.
- **Change:** mark required lines with "Say exactly:" and exempt them from rules that would cut or rewrite them; for lines that should vary, describe what they should contain.
  - *Before:* "Explain the policy: 'You can cancel any time before the renewal date at no charge.'" with a rule to keep replies under two sentences.
  - *After:* "Say exactly: 'You can cancel any time before the renewal date at no charge.' (Lines marked Say exactly are exempt from the length rule.)"
- **Don't:** give a single sample line for something that should vary; it gets repeated on every call.
- **In transcripts:** a required script trimmed or reworded, or the same sample line on every call.
- **Check with:** the scenarios that reach each required line, and several normal closes.

### Attach only the tools you need

- **In the prompt and tools:** attached tools the prompt never names, or tools it says never to call.
- **Change:** detach the tools the assistant should never call, and remove the prompt's lines about them.
  - *Before:* a `finish` tool attached, and "Never call `finish`." in the prompt.
  - *After:* `finish` detached; the line about it removed.
- **Don't:** keep a forbidden tool attached and rely on a "never call" line; the tool's own description can win.
- **In transcripts:** calls to tools the prompt never mentions.
- **Check with:** the paths that used to reach the detached tool.

### Pair each line with its tool call

- **In the prompt:** a spoken line and its tool call written as separate steps, especially around transfers, texts and ending the call.
- **Change:** put the line and the tool call in one instruction, and keep the transfer wording in refusal lines that lead to a transfer.
  - *Before:* "Say 'Let me get you to someone who can help.'" in one step and "Call `transfer_call`." in another.
  - *After:* "Say 'Let me get you to someone who can help.' and call `transfer_call` in the same response."
- **Don't:** take the transfer wording out of a refusal line; in our tests the refusal then ended the topic without a transfer.
- **In transcripts:** "connecting you now" with no tool call, or a tool call with no line before it, which the caller hears as silence. If this matters for your calls, Terra may suit them better.
- **Check with:** every transfer path, every text, the end of the call, and a request the assistant declines before transferring.

## How this changes your prompt

The changes above come down to writing down what the team relied on GPT-4.1 to do on its own: the next step after each kind of answer, a pointer to the closing steps from each branch, what to say with each tool call, how to say no (reason, alternative, next step), when to acknowledge feelings, and which tools exist. Apply them while building the copy, as **How to use this card** says. [Fixes](fixes.md) lists wording for any symptom that still shows in the comparison runs.

5.6 Luna gains a lot from this. A structure that worked: one short conversation-state section that the rest of the prompt points to.

- **Open request:** keep the caller's oldest unresolved request through side questions; "okay" or "thanks" doesn't close it.
- **Next action:** after each kind of answer or tool result, the specific next step, before any generic "anything else?".
- **Refusals:** every "no" gives the reason, one alternative and the next step; at most one retry after a decline; never re-ask an answered question.
- **Truthfulness:** claim an action only after a tool confirms it.
- **Introduce yourself once per call.**

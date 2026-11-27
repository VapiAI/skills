# Model card: gpt-5.6-terra

- **Target model:** `gpt-5.6-terra`
- **Starting model:** GPT-4.1
- **Last updated:** 2026-11-26
- **Evidence:** GPT-4.1 and Terra on the same simulated scenarios across several real-world assistants (support, collections, applications and scheduling, including a multi-assistant squad), each on its unchanged prompt. Examples are anonymized.

This card is a starting point. It covers the main patterns we saw when we tested 5.6 Terra against GPT-4.1 on several real assistants. Your assistant may behave differently in ways our tests didn't show, so test your own key scenarios before you switch.

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
  "model": "gpt-5.6-terra",
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

- According to benchmarks the Vapi team ran, Terra has good intelligence and costs much less than GPT-4.1. In our tests it responded more slowly per turn than GPT-4.1, so confirm latency and cost per minute on your own assistant (step 8 of the skill).
- Rule adherence matched or beat GPT-4.1 on every assistant we tested, before any prompt change.
- The more literal of the two 5.6 models: the stronger of them at following stated rules and counted steps.
- It sounds more neutral than GPT-4.1. Plan the tone work in [Fixes](fixes.md#tone-and-warmth) from the start, and include upset-caller scenarios so the comparison shows the gap.

## How to use this card

Apply these changes while building the gpt-5.6-terra copy, so the first version tested is already adapted:

1. For each pattern below, check the prompt and tools for the shape under **In the prompt**. Only apply the **Change** where that shape is there; leave everything else as it is.
2. Adapt the before/after example to the prompt's own wording. Never paste the example text.
3. Follow each **Don't**: these are variants that made things worse in our tests or common mistakes with this pattern.
4. Show the user the list of changes you made (pattern, where, one line each) in `review.md`, then build the copy. No approval step.
5. Add each applied pattern's **Check with** scenarios to the suite. During the comparison runs, watch for the **In transcripts** signals; if one still shows, treat it as a step 7 fix.

## Behaviors compared with GPT-4.1

### Point each branch to your closing steps

- **In the prompt:** branches, failures included, that end with their own "close the call" line, and closing steps (a closing question, a link) written somewhere else.
- **Change:** write the closing steps once, and replace each branch's "close the call" with a pointer that names the next step.
  - *Before:* "If the send fails, say so and close the call."
  - *After:* "If the send fails, say so. Then follow # Closing."
- **Don't:** copy the full closing steps and their exceptions into every branch; in our tests repeating them added nothing, and it leaves the same rule in several places.
- **In transcripts:** a branch that closes the call without the closing question or link, most often after the caller turns down an offer.
- **Check with:** a caller who turns down an offer, a failed send, and a normal close.

### Match names and triggers exactly

- **In the prompt:** a trigger written as a single keyword, such as a language name, or a tool, step or value named differently from the configuration.
- **Change:** describe triggers by meaning, and make every name in the prompt match the configuration.
  - *Before:* "If the caller asks for Spanish, reply in Spanish."
  - *After:* "If the caller's first message is in Spanish or asks for Spanish, reply in Spanish. Otherwise, English."
- **Don't:** answer this with a longer list of trigger words; describe what the caller means instead.
- **In transcripts:** English replies to a caller who speaks Spanish without asking for it, or a step left undone because a name doesn't match.
- **Check with:** a caller who speaks another language without naming it, and one who asks to switch partway through.

### Aim for good prompt coverage

- **In the prompt:** common requests from the flow map with no line saying what to say or do.
- **Change:** for each common request the prompt doesn't cover, write what to say or do beside the rule it belongs to.
  - *Before:* (nothing about the request)
  - *After:* "Asking to waive a late fee doesn't qualify for a transfer: explain the fee and offer the payment options this prompt gives."
- **Don't:** insert the new sentence between a general rule and its fallback, or point it at another rule; in our tests that cost transfers on nearby requests.
- **In transcripts:** a transfer or callback for a request the assistant could handle.
- **Check with:** the uncovered request, plus a nearby request that should still reach a person.

### Write complete tool descriptions

- **In the prompt and tools:** a tool or parameter description that disagrees with the prompt or leaves a format open, or a tool whose description invites a call the prompt forbids.
- **Change:** give every tool and parameter a complete description that matches the prompt.
  - *Before:* parameter `phone`: "The caller's phone number."
  - *After:* parameter `phone`: "The phone number from # Caller details, exactly as written there, including the country code."
- **Don't:** fix a disagreement in the prompt only; change the description too, since the description can win.
- **In transcripts:** a reformatted argument, such as a dropped country code, or a tool called where the prompt says not to.
- **Check with:** calls that pass each formatted parameter, and the paths where the prompt says not to call a tool.

### Plan for warmth

- **In the prompt:** broad bans on acknowledgments or apologies, or refusal lines with no reason or next step.
- **Change:** narrow acknowledgment bans to filler; when the assistant has to say no, have it give the reason, one alternative and what happens next.
  - *Before:* "Keep replies short. Never apologize."
  - *After:* "Keep replies short and skip filler. When you have to say no, say why, offer one option this prompt gives, and say what happens next."
- **Don't:** rely on a general "be warm" line; it made no difference in earlier tests.
- **In transcripts:** plain refusals with no reason or next step, or no acknowledgment when the caller shares bad news.
- **Check with:** an upset caller and a request the assistant has to decline.

### Write the next step after each answer

- **In the prompt:** a step that calls a tool or answers a question with nothing saying what comes next.
- **Change:** after each kind of answer and each tool result, write what comes next.
  - *Before:* "Send the link."
  - *After:* "Send the link. Once it's sent, say what it's for and ask whether there's anything else you can help with."
- **Don't:** script a next-step line that isn't true for every result, such as "your payment was approved" when a payment can be pending; the model skips the line when it doesn't fit.
- **In transcripts:** the assistant answering and then waiting, where GPT-4.1 offered the next step, or the close starting in the same turn as a confirmation.
- **Check with:** each result the tool can return (approved, pending, declined).

### Plan for tool failures

- **In the prompt:** a step that calls a tool with no line for what happens if it fails, or a failure line that states the failure and stops.
- **Change:** give each failure that matters a fallback line that ends with the next step as a question, using a next step the prompt already offers.
  - *Before:* "If the card is declined, tell them."
  - *After:* "If the card is declined, say no payment was made, then ask: 'Would you like me to text you a link to update your card?'"
- **Don't:** invent a next step the prompt doesn't define.
- **In transcripts:** a failure line with no next step, or the caller sent elsewhere after a failed tool.
- **Check with:** failing tool results (errors and blocked results) for each tool that matters.

### Mark lines that must be said exactly

- **In the prompt:** a single sample line for something that should vary, or required lines that another rule contradicts.
- **Change:** label examples clearly and give two or three different ones; mark required lines with "Say exactly:" and make sure no other rule contradicts them.
  - *Before:* "Close with: 'Thanks for calling. Bye.'"
  - *After:* "Close with a short goodbye that ends in 'Bye'. Examples, vary them: 'Alright, take care. Bye.' / 'You're all set. Have a good day. Bye.'"
- **Don't:** give a single sample line for something that should vary; it gets repeated on every call.
- **In transcripts:** the same sample line on every call, or a required script reworded.
- **Check with:** several normal closes, and the scenarios that reach each required line.

### Attach only the tools you need

- **In the prompt and tools:** attached tools the prompt never names, or tools it says never to call.
- **Change:** detach the tools the assistant should never call, and remove the prompt's lines about them.
  - *Before:* a `finish` tool attached, and "Never call `finish`." in the prompt.
  - *After:* `finish` detached; the line about it removed.
- **Don't:** keep a forbidden tool attached and rely on a "never call" line; the tool's own description can win.
- **In transcripts:** calls to tools the prompt never mentions.
- **Check with:** the paths that used to reach the detached tool, and calls that take payments.

### Pair each line with its tool call

- **In the prompt:** a spoken line and its tool call written as separate steps, or a call's first lookup with no line before it.
- **Change:** put the line and the tool call in one instruction, including a line before the call's first lookup.
  - *Before:* "Look up their account."
  - *After:* "Say 'One moment while I pull up your account.' and call `lookup_account` in the same response."
- **Don't:** split the line and the call across steps; "say this, then call X" reads as two steps.
- **In transcripts:** a tool call with no line before it, which the caller hears as silence, most often the first lookup, a transfer or a text.
- **Check with:** every transfer path, every text, and the first lookup of a call.

## How this changes your prompt

The changes above come down to writing down what the team relied on GPT-4.1 to do on its own: the next step after each kind of answer, a pointer to the closing steps from each branch, what to say with each tool call, how to say no (reason, alternative, next step), when to acknowledge feelings, and which tools exist. Apply them while building the copy, as **How to use this card** says. [Fixes](fixes.md) lists wording for any symptom that still shows in the comparison runs.

A structure that helped 5.6 Luna in our tests, and that you can try with Terra: one short conversation-state section that the rest of the prompt points to.

- **Open request:** keep the caller's oldest unresolved request through side questions; "okay" or "thanks" doesn't close it.
- **Next action:** after each kind of answer or tool result, the specific next step, before any generic "anything else?".
- **Refusals:** every "no" gives the reason, one alternative and the next step; at most one retry after a decline; never re-ask an answered question.
- **Truthfulness:** claim an action only after a tool confirms it.
- **Introduce yourself once per call.**

# Model card: gpt-6-luna

- **Target model:** `gpt-6-luna`
- **Starting model:** GPT-4.1
- **Last updated:** 2026-11-26
- **Evidence:** GPT-4.1 and gpt-6-luna on the same simulated scenarios across seven real-world assistants (support, collections, applications and scheduling, including a multi-assistant squad), each on its unchanged prompt, 3 runs per scenario. Each pattern held on at least three assistants unless the line says otherwise. Examples are anonymized.

This card is a starting point. It covers the main patterns we saw when we tested 6 Luna against GPT-4.1 on several real assistants. Your assistant may behave differently in ways our tests didn't show, so test your own key scenarios before you switch.

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
  "model": "gpt-6-luna",
  "reasoningEffort": "low",
  "serviceTier": "fast",
  "promptCacheRetention": "24h"
}
```

- `reasoningEffort: "low"` is the setting these patterns were measured with.
- `serviceTier: "fast"` is fast mode: lower response time at a higher per-token rate.
- `promptCacheRetention: "24h"` keeps the prompt cached across calls. It only pays off when per-call values (date, caller number, IDs) sit in one block at the end of the prompt.
- Set `"provider": "openai"` if the current model is from another provider.
- Check that `maxTokens` isn't low, and set the same explicit value on both copies.
- Check `fallbackModels`: remove GPT-4.1 entries carried over from the old configuration, and set the production fallback explicitly before rollout.

## What to expect

- gpt-6-luna is a smaller model that trades some intelligence for a lower cost, an option for teams moving off GPT-4.1. Confirm latency and cost per minute on the user's own assistant (step 8 of the skill).
- It needs fuller, more specific prompts than GPT-4.1 and does less well when a prompt leaves things to judgment, though it kept stated rules as well as GPT-4.1 on the assistants we tested, before any prompt change.
- It sounds plainer than GPT-4.1, and it pairs lines with tool calls less reliably than GPT-4.1 did. Plan the tone work and the say-and-act fixes in [Fixes](fixes.md) from the start, and include upset-caller scenarios and tool-heavy scenarios so the comparison shows them.

## How to use this card

Apply these changes while building the gpt-6-luna copy, so the first version tested is already adapted:

1. For each pattern below, check the prompt and tools for the shape under **In the prompt**. Only apply the **Change** where that shape is there; leave everything else as it is.
2. Adapt the before/after example to the prompt's own wording. Never paste the example text.
3. Follow each **Don't**: these are variants that made things worse in our tests or common mistakes with this pattern.
4. Show the user the list of changes you made (pattern, where, one line each) in `review.md`, then build the copy. No approval step.
5. Add each applied pattern's **Check with** scenarios to the suite. During the comparison runs, watch for the **In transcripts** signals; if one still shows, treat it as a step 7 fix.

## Behaviors compared with GPT-4.1

### Pair each line with its tool call

- **In the prompt:** a lookup whose spoken line is written as a separate step, or has no line at all; transfers with a line or a safety sentence the caller must hear.
- **Change:** put a lookup's line in that tool's start message and take it out of the prompt; keep transfer lines, safety sentences and refusal lines in the prompt as they are.
  - *Before:* "Say 'One moment while I pull up your account.'" in one step and "Call `lookup_account`." in the next.
  - *After:* `lookup_account` start message: "One moment while I pull up your account." (line removed from the prompt)
- **Don't:** put a transfer line in the transfer tool's start message, or delete the safety or refusal sentences that go with a transfer; in our tests the line was then said twice and a safety sentence was lost.
- **In transcripts:** a lookup or transfer with nothing said first, which the caller hears as silence, or the line said only after the tool result. On one assistant, a goodbye with no end-call tool, or the call ended without a word. If this matters for your calls, Terra may suit them better.
- **Check with:** the first lookup of a call, every transfer path, and a caller who raises a safety topic before a transfer.

### Point each branch to your closing steps

- **In the prompt:** branches that end with their own "close the call" line, and closing steps (a closing question, a link, a survey) written somewhere else.
- **Change:** write the closing steps once, right before the end tool, and replace each branch's "close the call" with a pointer that names the next step.
  - *Before:* "If they don't want a callback, that's fine. Close the call."
  - *After:* "If they don't want a callback, that's fine. Then send the link and follow # Closing."
- **Don't:** add a goodbye or "when the call may end" clause to the closing steps; in our tests that brought a survey after a transfer and a link resent after a failed send.
- **In transcripts:** a call that ends without the closing question or link, a call ended while the caller still had an open request, or a call handed back instead of closed. If this matters for your calls, Sapien or 6.1 Terra may suit them better.
- **Check with:** a caller who declines an offer, a caller who says goodbye first, a failed send, and a normal close.

### Write complete tool descriptions

- **In the prompt and tools:** a tool or parameter description that disagrees with the prompt or leaves a value open, a tool whose description invites a call the prompt forbids, or the same script in a tool result and in the prompt.
- **Change:** give every tool and parameter a complete description that agrees with the prompt, and keep each script in one place.
  - *Before:* parameter `amount_type`: "The amount type."
  - *After:* parameter `amount_type`: "Amount type. Always `CUSTOM`: the amount is whatever the caller chose."
- **Don't:** leave a copy of the script in a tool result; in our tests the script was said twice.
- **In transcripts:** a wrong or invented parameter value, a tool called where the prompt says not to, or a scripted line said twice.
- **Check with:** a call that uses each tool's parameters with an unusual value, and the paths where the prompt says not to call a tool.

### Attach only the tools you need

- **In the prompt and tools:** attached tools the prompt never names, or tools it says never to call.
- **Change:** detach the tools the assistant should never call, and remove the prompt's lines about them.
  - *Before:* an `end_session` tool attached, and "Never call `end_session`." in the prompt.
  - *After:* `end_session` detached; the line about it removed.
- **Don't:** keep a forbidden tool attached and rely on a "never call" line; the tool's own description can win.
- **In transcripts:** calls to tools the prompt never mentions.
- **Check with:** calls that take payments, and every path that used to reach the detached tool.

### Aim for good prompt coverage

- **In the prompt:** common requests from the flow map with no line saying what to say or do, or an escalation route (a transfer or an emergency path) with nothing saying what doesn't qualify for it.
- **Change:** for each common request the prompt doesn't cover, write what to say or do beside the rule it belongs to, including when not to escalate.
  - *Before:* (nothing about the request)
  - *After:* "Asking to change a mailing address isn't a reason to transfer: give the email address for updates."
- **Don't:** insert the new sentence between a general rule and its fallback, or point it at another rule; in our tests that cost transfers on nearby requests.
- **In transcripts:** a transfer or the emergency route for a routine request, such as a long-standing minor symptom, or "I'm not sure" with no next step.
- **Check with:** the uncovered request, a routine request close to an escalation, and a nearby request that should still reach a person.

### Match names and labels exactly

- **In the prompt:** a value or label the prompt checks that differs from what the tools return, or a rule that names one status where several should take the same path.
- **Change:** name every value and label as the tools return them, and list each value a rule covers.
  - *Before:* "If the account status is `ACTIVE`, offer to take a payment."
  - *After:* "If the account status is `ACTIVE` or `PAST_DUE`, offer to take a payment."
- **Don't:** guess the values; take them from real tool results in the transcripts, since a near miss leaves the rule unused.
- **In transcripts:** a request turned down because of a status the prompt didn't name, such as "the account is marked past due rather than active".
- **Check with:** a tool result for each status that should take the same path, and the full payment path.

### Mark lines that must be said exactly

- **In the prompt:** required lines (disclosures, verification asks) next to a rule that would trim or rewrite them, such as a turn-length rule; or a single sample line for something that should vary.
- **Change:** mark required lines with "Say exactly:" and exempt them from rules that would rewrite them; for lines that should vary, give two or three different labeled examples.
  - *Before:* "Tell them the call may be recorded." with a rule to keep every reply to one sentence.
  - *After:* "Say exactly: 'This call may be recorded for quality purposes.' (Lines marked Say exactly are exempt from the length rule.)"
- **Don't:** give a single sample line for something that should vary; it gets repeated on every call.
- **In transcripts:** a required script trimmed or reworded, or the same sample line on every call.
- **Check with:** the scenarios that reach each required line, and several normal closes.

### Write in the warmth you want

- **In the prompt:** moments that matter, such as bad news or a caller in distress, with no acknowledgment written for them; broad bans on acknowledgments; or refusal lines with no reason or next step.
- **Change:** write an acknowledgment into the prompt for those moments, and when the assistant can't do what was asked, have it give the reason, one alternative and what happens next.
  - *Before:* "If the request is denied, tell them it was denied."
  - *After:* "If the request is denied, acknowledge it briefly in your own words, say why, offer one option this prompt gives, and say what happens next."
- **Don't:** rely on a general "be warm" line; it made no difference in earlier tests.
- **In transcripts:** plain refusals with no reason or next step, or no acknowledgment when the caller shares bad news.
- **Check with:** an upset caller, a caller who hears bad news, and a request the assistant has to decline.

### Plan for tool failures

- **In the prompt:** a step that calls a tool with no line for what happens if it fails, or a failure line that states the failure and stops.
- **Change:** give each failure that matters a fallback line that ends with the next step as a question, using a next step the prompt already offers.
  - *Before:* "If the update fails, say it didn't go through."
  - *After:* "If the update fails, say it didn't go through and nothing was changed, then ask: 'Would you like me to text you a link to update it yourself?'"
- **Don't:** stop the line at the failure, or invent a next step the prompt doesn't define.
- **In transcripts:** a failure line with no next step, or the call moving to its close right after a failed tool.
- **Check with:** failing tool results (errors and blocked results) for each tool that matters.

### Write the next step after each answer

- **In the prompt:** a step that calls a tool or answers a question with nothing saying what comes next.
- **Change:** after each kind of answer and each tool result, write what comes next.
  - *Before:* "Book the appointment."
  - *After:* "Book the appointment. Once it's booked, confirm the time and ask whether there's anything else you can help with."
- **Don't:** script a next-step line that isn't true for every result, such as "your payment was approved" when a payment can be pending; the model skips the line when it doesn't fit.
- **In transcripts:** the assistant answering and then waiting, where GPT-4.1 offered the next step, or the close starting in the same turn as a confirmation.
- **Check with:** each result the tool can return (approved, pending, declined).

## How this changes your prompt

The changes above come down to writing down what the team relied on GPT-4.1 to do on its own: what the caller hears with each tool call, a pointer to the closing steps from each branch, what does and doesn't qualify for an escalation, the next step after each kind of answer, and which tools exist. Apply them while building the copy, as **How to use this card** says. [Fixes](fixes.md) lists wording for any symptom that still shows in the comparison runs.

# Model card: gpt-6-luna

- **Target model:** `gpt-6-luna`
- **Starting model:** GPT-4.1
- **Last updated:** 2026-11-26
- **Evidence:** GPT-4.1 and gpt-6-luna on the same simulated scenarios across seven real-world assistants (support, collections, applications and scheduling, including a multi-assistant squad), each on its unchanged prompt, 3 runs per scenario. Every pattern below held on at least three assistants. Examples are anonymized.

This card is a starting point. It covers the main patterns we saw when we tested 6 Luna against GPT-4.1 on several real assistants. Your assistant may behave differently in ways our tests didn't show, so test your own key scenarios before you switch.

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

- gpt-6-luna is a lower-cost option for teams moving off GPT-4.1. Confirm latency and cost per minute on the user's own assistant (step 8 of the skill).
- Rule adherence matched or beat GPT-4.1 on the assistants we tested, before any prompt change.
- It sounds plainer than GPT-4.1, and it pairs lines with tool calls less reliably than GPT-4.1 did. Plan the tone work and the say-and-act fixes in [Fixes](fixes.md) from the start, and include upset-caller scenarios and tool-heavy scenarios so the comparison shows them.

## Behaviors compared with GPT-4.1

These are tendencies we saw on some assistants, not on every call, ordered by how much they're likely to affect calls. Each pattern held on at least three assistants. Each one pairs what we saw with a prompt habit that helps. Where our tests checked a prompt change, the card says what happened.

### Pair each line with its tool call

- **What we saw:** 6 Luna can call a tool, such as a lookup or a transfer, without saying anything first more often than GPT-4.1, which the caller hears as silence. At the end of a call it may also say goodbye without calling the end-call tool, or end the call without a word.
- **For your prompt:** Tie each line to its tool call in one instruction, or put it in the tool's start message, and when you move a line there, keep any other content the caller needs, such as safety instructions or the reason for a refusal, in the prompt.

### Repeat closing steps in each branch

- **What we saw:** When a step in the prompt has its own last line, 6 Luna can follow it and drop closing steps written elsewhere, which GPT-4.1 kept in mind for the whole call. On some assistants it ended the call while the caller still had an open request, or handed the call back instead of closing it.
- **For your prompt:** Repeat each closing step in every branch that needs it, say plainly when the call may end, and say that a caller's goodbye doesn't skip a required closing step, such as a survey question, then test a caller who says goodbye first.

### Write complete tool descriptions

- **What we saw:** 6 Luna gives tool descriptions, parameter options and the text in tool results more weight than GPT-4.1 did. It can call a tool whose description invites it, such as a finish or end tool, even when the prompt says not to.
- **For your prompt:** Write a complete description for every tool and parameter that agrees with the prompt, detach any tool the assistant should never call, and keep instructions out of the text your tools return.

### Attach only the tools you need

- **What we saw:** 6 Luna runs the lookups and verification steps the prompt requires, which GPT-4.1 often skipped. It can also call attached tools the prompt never mentions.
- **For your prompt:** Attach only the tools the assistant actually needs.

### Write down the common situations

- **What we saw:** 6 Luna doesn't invent answers the way GPT-4.1 sometimes did. When the prompt doesn't cover a situation, it can take the broadest, safest option the setup gives it and transfer or escalate more often, sometimes for routine requests.
- **For your prompt:** Write a sentence for each situation that comes up often, and say clearly what does and doesn't qualify for an escalation.

### Match names and labels exactly

- **What we saw:** 6 Luna follows the exact wording of conditions and labels more closely than GPT-4.1. If the prompt says to act on accounts marked "OPEN", an account marked "LATE" falls outside that rule.
- **For your prompt:** Check that every tool, value and label named in the prompt matches what your tools actually return.

### Mark lines that must be said exactly

- **What we saw:** 6 Luna says short sample lines word for word more often than GPT-4.1, but it can trim or reword a longer required script to fit other rules in the prompt.
- **For your prompt:** Label examples clearly and give two or three different ones, and mark lines that must be said exactly with "Say exactly:", making sure no other rule, such as a formatting rule, contradicts them.

### Write in the warmth you want

- **What we saw:** 6 Luna sounds plainer than GPT-4.1, with shorter turns and almost no exclamation marks or filler. Most of its sympathy comes from lines the prompt writes for it, and it adds less of its own than GPT-4.1 did.
- **For your prompt:** Write acknowledgments into the prompt for the moments that matter, such as bad news or a caller in distress, and when the assistant can't do what was asked, have it explain why, offer one alternative and say what happens next.

### Plan for tool failures

- **What we saw:** 6 Luna follows the written steps strictly and keeps the disclosures and checks the prompt requires, where GPT-4.1 sometimes bent them for simple requests. It doesn't claim an action succeeded when a tool failed.
- **For your prompt:** Write a fallback line and a next step for each tool failure that matters to you.

### Write the next step after each answer

- **What we saw:** 6 Luna answers what the caller asked and then waits, and rarely asks "anything else?" unless the current step tells it to, where GPT-4.1 often offered the next step on its own.
- **For your prompt:** Write in the prompt what the next step should be after each kind of answer or tool result.

## How this changes your prompt

The habits above come down to writing down what the team relied on GPT-4.1 to do on its own: what to say with each tool call, the closing steps inside each branch, when the call may end, what qualifies for an escalation, the next step after each kind of answer, and which tools exist. [Fixes](fixes.md) lists the wording that works for each symptom.

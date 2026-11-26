# Model card: gpt-5.6-luna

- **Target model:** `gpt-5.6-luna`
- **Starting model:** GPT-4.1
- **Last updated:** 2026-11-26
- **Evidence:** GPT-4.1 and Luna on the same simulated scenarios across several real-world assistants (support, collections, applications and scheduling, including a multi-assistant squad), each on its unchanged prompt. Examples are anonymized.

This card is a starting point. It covers the main patterns we saw when we tested 5.6 Luna against GPT-4.1 on several real assistants. Your assistant may behave differently in ways our tests didn't show, so test your own key scenarios before you switch.

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

- According to benchmarks the Vapi team ran, Luna is the lowest-cost option, a little cheaper than gpt-5.6-terra, but it responds a little slower and needs more prompt tuning to reach parity. Confirm latency and cost per minute on your own assistant (step 8 of the skill).
- Rule adherence matched or beat GPT-4.1 on every assistant we tested, before any prompt change.
- It sounds more neutral than GPT-4.1. Plan the tone work in [Fixes](fixes.md#tone-and-warmth) from the start, and include upset-caller scenarios so the comparison shows the gap.

## Behaviors compared with GPT-4.1

These are tendencies we saw on some assistants, not on every call, ordered by how much they're likely to affect calls. Each pattern held on more than one assistant. Each one pairs what we saw with a prompt habit that helps. Where our tests checked a prompt change, the card says what happened.

### Repeat closing steps in each branch

- **What we saw:** 5.6 Luna follows the instruction for the step it's on, so a step that ends with "confirm and close the call" can close the call there and skip global steps written elsewhere, such as a closing question or a link to send. GPT-4.1 kept those general rules in mind for the whole call.
- **For your prompt:** Repeat each global step inside every branch that needs it, including branches where something fails, for example: "Then send the link and follow # Closing."

### Match names exactly

- **What we saw:** 5.6 Luna does what the prompt says without inferring what the author meant, more than GPT-4.1. When a prompt named an `end_call` tool but the real tool was `end_call_tool`, it could say goodbye and never end the call, where GPT-4.1 worked out what was meant.
- **For your prompt:** Check that every tool, step and variable the prompt names matches your configuration, and write down anything you relied on GPT-4.1 to work out on its own, such as when to end the call.

### Write down the common situations

- **What we saw:** 5.6 Luna doesn't invent answers the way GPT-4.1 sometimes did. When the prompt doesn't cover a situation, it can hold back and take the broadest option your setup gives it, which on many assistants meant more transfers or callbacks and lower deflection.
- **For your prompt:** Write down what the assistant should do in the situations that come up often, even if it's only one sentence for each.

### Write complete tool descriptions

- **What we saw:** 5.6 Luna gives tool descriptions, parameter descriptions and the text in tool results more weight than GPT-4.1 did, and empty or bare descriptions leave it guessing. On one assistant it called a finish tool whose description said to use it when the conversation was complete, even though the prompt said never to call it.
- **For your prompt:** Give every tool and parameter a complete description of what it does, when to use it and what each value means, in line with the prompt, and keep instructions out of the text your tools return.

### Plan for warmth

- **What we saw:** 5.6 Luna sounds more neutral than GPT-4.1, with turns about a third shorter, and follows rules that limit acknowledgments, which GPT-4.1 often ignored. Most of its warmth comes from what the prompt writes for it, so callers can find it colder than GPT-4.1.
- **For your prompt:** Loosen or narrow rules that ban acknowledgments, and when the assistant has to say no, have it explain why, offer one alternative and say what happens next, since a general line like "be warm" made no difference in our tests.

### Write the next step after each answer

- **What we saw:** 5.6 Luna answers what the caller asked and then waits for the caller to lead, one of the tendencies we saw most often, and rarely asks "anything else?" or offers a link unless the current step tells it to.
- **For your prompt:** Write in the prompt what the next step should be after each kind of answer or tool result, for example as a short table of next actions (see [Fixes](fixes.md#conversation-flow)).

### Plan for tool failures

- **What we saw:** 5.6 Luna follows written steps strictly and in order, and keeps counted steps, such as "transfer on the third request", more closely than GPT-4.1, though not always exactly. When a tool fails and the prompt has no recovery step, it can stop or send the caller elsewhere instead of improvising.
- **For your prompt:** Write a fallback line and a next step for each tool failure that matters to you, and state each count plainly in the step it belongs to.

### Mark lines that must be said exactly

- **What we saw:** 5.6 Luna says sample lines from the prompt word for word more often than GPT-4.1, so calls can start to sound the same.
- **For your prompt:** Label examples clearly and give two or three different ones, or describe what the line should contain, and mark lines that must be said exactly with "Say exactly:", making sure no other rule contradicts them.

### Attach only the tools you need

- **What we saw:** 5.6 Luna runs the lookups and verification steps the prompt requires, which GPT-4.1 often skipped. It may also call attached tools the prompt never mentions.
- **For your prompt:** Attach only the tools the assistant actually needs.

### Pair each line with its tool call

- **What we saw:** Around transfers, texts and ending the call, 5.6 Luna can say it's connecting the caller without calling the tool, and sometimes calls a tool without saying anything first, which the caller hears as silence. It stops talking after a transfer or end-call tool and rarely claims an action no tool confirmed.
- **For your prompt:** Tie the line and the tool call together in one instruction, for example "Say 'Let me transfer you to billing.' and call `transfer_call` in the same response.", and keep any transfer wording in refusal lines so transfers still happen.

## How this changes your prompt

The habits above come down to writing down what the team relied on GPT-4.1 to do on its own: the next step after each kind of answer, the closing steps inside each branch, what to say with each tool call, how to say no (reason, alternative, next step), when to acknowledge feelings, and which tools exist. [Fixes](fixes.md) lists the wording that works for each symptom.

5.6 Luna gains a lot from this. A structure that worked: one short conversation-state section that the rest of the prompt points to.

- **Open request:** keep the caller's oldest unresolved request through side questions; "okay" or "thanks" doesn't close it.
- **Next action:** after each kind of answer or tool result, the specific next step, before any generic "anything else?".
- **Refusals:** every "no" gives the reason, one alternative and the next step; at most one retry after a decline; never re-ask an answered question.
- **Truthfulness:** claim an action only after a tool confirms it.
- **Introduce yourself once per call.**

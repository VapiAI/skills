# Model card: gpt-5.6-terra

- **Target model:** `gpt-5.6-terra`
- **Starting model:** GPT-4.1
- **Last updated:** 2026-11-26
- **Evidence:** GPT-4.1 and Terra on the same simulated scenarios across several real-world assistants (support, collections, applications and scheduling, including a multi-assistant squad), each on its unchanged prompt. Examples are anonymized.

This card is a starting point. It covers the main patterns we saw when we tested 5.6 Terra against GPT-4.1 on several real assistants. Your assistant may behave differently in ways our tests didn't show, so test your own key scenarios before you switch.

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

- `reasoningEffort: "low"`. Higher effort did not fix behavior problems that prompt changes did.
- `serviceTier: "fast"` is fast mode: lower response time at a higher per-token rate.
- `promptCacheRetention: "24h"` keeps the prompt cached across calls. It only pays off when per-call values (date, caller number, IDs) sit in one block at the end of the prompt.
- Set `"provider": "openai"` if the current model is from another provider.
- Don't rely on `temperature` or `maxTokens` to shape behavior; shape it with the prompt. Check that `maxTokens` isn't low: reasoning can use output tokens, and a low cap shows up as short or empty replies.
- Check `fallbackModels`: remove GPT-4.1 entries carried over from the old configuration, and set the production fallback explicitly before rollout.

## What to expect

- According to benchmarks the Vapi team ran, Terra reasons better than GPT-4.1, responds faster and costs much less. Confirm latency and cost per minute on your own assistant (step 8 of the skill).
- Rule adherence matched or beat GPT-4.1 on every assistant we tested, before any prompt change.
- The most literal of the new models: the strongest at following stated rules and counted steps.
- It sounds more neutral than GPT-4.1. Plan the tone work in [Fixes](fixes.md#tone-and-warmth) from the start, and include upset-caller scenarios so the comparison shows the gap.

## Behaviors compared with GPT-4.1

Each pattern held on more than one assistant. They're tendencies, not guarantees, ordered by how much they're likely to affect calls.

1. **Local instructions over global rules.** GPT-4.1 kept the general rules at the top of the prompt in mind for the whole call. Terra follows the instruction for the step it's on, and skips global steps that the current step doesn't repeat.
   *Example:* a prompt said "always ask if there's anything else before closing", but several branches ended with "close the call". GPT-4.1 asked in 60 of 60 conversations on those branches; Terra in 4. A link the prompt said to send after a callback was sent in 12 of 12 on GPT-4.1 and 0 on Terra.
2. **Taking the system prompt literally.** GPT-4.1 read the prompt for its intent and filled in what it left unsaid. Terra does exactly what the prompt says.
   *Example:* a prompt called its end-call tool `end_call`, but the tool's real name was `end_call_tool`. GPT-4.1 ended the call anyway. Terra often said goodbye and never ended the call.
   *For your prompt:* Describe triggers by meaning, such as "if the caller speaks or asks for Spanish", not by a single keyword; this fixed missed language switches in our tests.
3. **Situations the prompt doesn't cover.** GPT-4.1 made up an answer from general knowledge, and was often wrong. Terra doesn't invent answers: it holds back and takes the broadest option the setup gives it, which on many assistants means more transfers or callbacks.
   *Example:* asked whether a document was required, which the prompt didn't say, GPT-4.1 answered anyway in 11 of 12 conversations. Terra never did.
4. **Tool descriptions.** GPT-4.1 followed the system prompt when a tool's description disagreed with it. Terra gives tool descriptions, parameter descriptions and text in tool results more weight than the system prompt. Empty or bare descriptions leave it guessing.
   *Example:* a finish tool whose description said to use it when the conversation was complete got called, even though the prompt said never to call it. GPT-4.1 never called it.
5. **Empathy and warmth.** GPT-4.1 sounded warm without being told to: enthusiasm, reassurance, and a reason or alternative with every "no". Terra sounds more neutral, with turns about a third shorter, and most of its warmth comes from what the prompt writes. Where a prompt limited acknowledgments, GPT-4.1 often ignored the rule and Terra followed it.
6. **Offering the next step.** GPT-4.1 offered the obvious next step on its own, such as "anything else?" or a link. Terra answers and waits, unless the current step says what comes next.
   *Example:* after answering a general question, GPT-4.1 offered to text a link in 11 of 11 conversations; Terra in 4 of 12.
7. **Following procedures.** GPT-4.1 sometimes bent procedures when a request looked simple, skipping verification or a required lookup. Terra follows written steps strictly and in order. When a tool fails and the prompt has no recovery step, it stops or sends the caller elsewhere instead of improvising.
   *Example:* when an action failed and the prompt said "retry once, then read this line", Terra did both in 13 of 13 conversations; GPT-4.1 never retried.
8. **Scripted lines.** GPT-4.1 treated sample lines as inspiration and varied them. Terra says them word for word.
   *Example:* a prompt's sample closing ended 19 conversations on GPT-4.1 and 72 on Terra, so calls started to sound alike.
9. **Using tools.** GPT-4.1 often answered from memory and skipped required lookups. Terra runs the lookups the prompt requires, and may also call attached tools the prompt never mentions.
   *Example:* on a support assistant that required a knowledge lookup before giving steps, GPT-4.1 skipped it in 45 of 108 conversations. Terra almost always ran it.
10. **Saying and doing.** GPT-4.1 usually paired what it said with the matching tool call. Around transfers, texts and ending the call, Terra sometimes separates the two, most often by calling a tool with nothing said first, which a caller hears as silence. It stops talking after a transfer or end-call tool and rarely claims an action no tool confirmed.
    *Example:* on one assistant, 117 of 204 first turns were a lookup with nothing said first.

## Where it differs from gpt-5.6-luna

| Behavior | gpt-5.6-terra | What to do |
|---|---|---|
| Saying and doing | More likely than Luna to call a tool with nothing said first, especially the first lookup of a call | Script the line with the tool in the same response; at call start, say what to say before the first lookup |
| Counted steps | Keeps them exactly ("transfer on the third request": 18 of 18) | Nothing to fix; make sure the counts in the prompt are the ones you want |
| Tone | Plainest style and slightly shorter turns | The tone fixes in [Fixes](fixes.md#tone-and-warmth) |

## How this changes your prompt

Anything the team relied on GPT-4.1 doing implicitly has to be written down: the next step after each kind of answer, the closing sequence inside each branch, what to say with each tool call, how to refuse (reason, alternative, next step), when to acknowledge feelings, and which tools exist. [Fixes](fixes.md) lists the wording that works for each symptom.

A structure that worked: one short conversation-state section that the rest of the prompt points to.

- **Open request:** keep the caller's oldest unresolved request through side questions; "okay" or "thanks" doesn't close it.
- **Next action:** after each kind of answer or tool result, the specific next step, before any generic "anything else?".
- **Refusals:** every "no" gives the reason, one alternative and the next step; at most one retry after a decline; never re-ask an answered question.
- **Truthfulness:** claim an action only after a tool confirms it.
- **Introduce yourself once per call.**

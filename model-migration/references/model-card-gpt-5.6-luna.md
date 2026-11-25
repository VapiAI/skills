# Model card: gpt-5.6-luna

- **Target model:** `gpt-5.6-luna`
- **Starting model:** GPT-4.1
- **Last updated:** 2026-11-24
- **Evidence:** GPT-4.1 and Luna on the same simulated scenarios across several real-world assistants (support, collections, applications and scheduling, including a multi-assistant squad), each on its unchanged prompt. Examples are anonymized.

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

Each pattern held on more than one assistant. They're tendencies, not guarantees, ordered by how much they're likely to affect calls.

1. **Local instructions over global rules.** GPT-4.1 kept the general rules at the top of the prompt in mind for the whole call. Luna follows the instruction for the step it's on, and skips global steps that the current step doesn't repeat.
   *Example:* a prompt said "always ask if there's anything else before closing", but several branches ended with "close the call". GPT-4.1 asked in 60 of 60 conversations on those branches; Luna in 8. A link the prompt said to send after a callback was sent in 12 of 12 on GPT-4.1 and 1 on Luna.
2. **Taking the system prompt literally.** GPT-4.1 read the prompt for its intent and filled in what it left unsaid. Luna does exactly what the prompt says.
   *Example:* a prompt called its end-call tool `end_call`, but the tool's real name was `end_call_tool`. GPT-4.1 ended the call anyway. Luna often said goodbye and never ended the call.
3. **Situations the prompt doesn't cover.** GPT-4.1 made up an answer from general knowledge, and was often wrong. Luna doesn't invent answers: it holds back and takes the broadest option the setup gives it, which on many assistants means more transfers or callbacks.
   *Example:* asked whether a document was required, which the prompt didn't say, GPT-4.1 answered anyway in 11 of 12 conversations. Luna did once.
4. **Tool descriptions.** GPT-4.1 followed the system prompt when a tool's description disagreed with it. Luna gives tool descriptions, parameter descriptions and text in tool results more weight than the system prompt. Empty or bare descriptions leave it guessing.
   *Example:* a finish tool whose description said to use it when the conversation was complete got called, even though the prompt said never to call it. GPT-4.1 never called it.
5. **Empathy and warmth.** GPT-4.1 sounded warm without being told to: enthusiasm, reassurance, and a reason or alternative with every "no". Luna sounds more neutral, with turns about a third shorter, and most of its warmth comes from what the prompt writes. Where a prompt limited acknowledgments, GPT-4.1 often ignored the rule and Luna followed it.
6. **Offering the next step.** GPT-4.1 offered the obvious next step on its own, such as "anything else?" or a link. Luna answers and waits, unless the current step says what comes next.
   *Example:* after answering a general question, GPT-4.1 offered to text a link in 11 of 11 conversations; Luna in 2 of 12.
7. **Following procedures.** GPT-4.1 sometimes bent procedures when a request looked simple, skipping verification or a required lookup. Luna follows written steps strictly and in order, and keeps counted steps more closely than GPT-4.1, though less exactly than Terra. When a tool fails and the prompt has no recovery step, it stops or sends the caller elsewhere instead of improvising.
8. **Scripted lines.** GPT-4.1 treated sample lines as inspiration and varied them. Luna says them word for word.
   *Example:* a prompt's sample closing ended 19 conversations on GPT-4.1 and 111 on Luna, so calls started to sound alike.
9. **Using tools.** GPT-4.1 often answered from memory and skipped required lookups. Luna runs the lookups the prompt requires, and may also call attached tools the prompt never mentions.
   *Example:* on a support assistant that required a knowledge lookup before giving steps, GPT-4.1 skipped it in 45 of 108 conversations. Luna almost always ran it.
10. **Saying and doing.** GPT-4.1 usually paired what it said with the matching tool call. Around transfers, texts and ending the call, Luna sometimes separates the two: it is more likely than Terra to say it's doing something ("connecting you now") without calling the tool, and it also sometimes calls a tool with nothing said first. It stops talking after a transfer or end-call tool and rarely claims an action no tool confirmed.
    *Example:* on one assistant, Luna announced 13 of 36 safety transfers without making them; on a scheduling squad, 113 first transfers happened with nothing said first.

## Where it differs from gpt-5.6-terra

| Behavior | gpt-5.6-luna | What to do |
|---|---|---|
| Saying and doing | More likely than Terra to say it's doing something without calling the tool | Put the line and the tool call in the same response; never announce an action without its tool call |
| Counted steps | Follows them less exactly ("transfer on the third request": 9 of 18) | Check counted steps in the suite, and state the count plainly in the step itself |
| Tone | More often answers and waits for the caller to lead | A next-action table (see [Fixes](fixes.md#conversation-flow)) |

## Prompt work that helps

Anything the team relied on GPT-4.1 doing implicitly has to be written down: the next step after each kind of answer, the closing sequence inside each branch, what to say with each tool call, how to refuse (reason, alternative, next step), when to acknowledge feelings, and which tools exist. [Fixes](fixes.md) lists the wording that works for each symptom.

Luna gains most from this. A structure that worked: one short conversation-state section that the rest of the prompt points to.

- **Open request:** keep the caller's oldest unresolved request through side questions; "okay" or "thanks" doesn't close it.
- **Next action:** after each kind of answer or tool result, the specific next step, before any generic "anything else?".
- **Refusals:** every "no" gives the reason, one alternative and the next step; at most one retry after a decline; never re-ask an answered question.
- **Truthfulness:** claim an action only after a tool confirms it.
- **Introduce yourself once per call.**

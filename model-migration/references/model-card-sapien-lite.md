# Model card: Sapien Lite

- **Target model:** `sapien-lite` (`"provider": "vapi"`)
- **Starting model:** GPT-4.1
- **Last updated:** 2026-11-24
- **Evidence:** GPT-4.1 and Sapien Lite on the same simulated scenarios across seven real-world assistants (support, collections, applications and scheduling, including a multi-assistant squad), each on its unchanged prompt, 3 runs per scenario. Every pattern below held on at least three assistants. Examples are anonymized.

## Recommended settings

Set these fields inside the assistant's existing `model` object, and keep `messages`, `tools`, `toolIds` and every other field as they are:

```json
{
  "provider": "vapi",
  "model": "sapien-lite"
}
```

- Vapi manages the reasoning settings. Remove OpenAI-only fields carried over from the GPT-4.1 configuration, such as `reasoningEffort`, `serviceTier` and `promptCacheRetention`, if the API rejects them.
- Check that `maxTokens` isn't low, and set the same explicit value on both copies.
- Check `fallbackModels`: remove GPT-4.1 entries and set the production fallback explicitly before rollout.

## What to expect

- Sapien Lite is Vapi's option for cost-conscious teams moving off GPT-4.1. Confirm latency and cost per minute on the user's own assistant (step 8 of the skill).
- Rule adherence matched or beat GPT-4.1 on the assistants we tested, before any prompt change.
- It sounds plainer than GPT-4.1, and it pairs lines with tool calls less reliably than GPT-4.1 did. Plan the tone work and the say-and-act fixes in [Fixes](fixes.md) from the start, and include upset-caller scenarios and tool-heavy scenarios so the comparison shows them.

## Behaviors compared with GPT-4.1

They're tendencies, not guarantees, ordered by how much they're likely to affect calls. Lines in bold are the ones most worth testing.

### Acting before speaking

- **GPT-4.1** usually said something first, such as "One moment while I look that up", and then called the tool.
- **Sapien Lite** **often calls a tool, such as a lookup or a transfer, without saying anything first, and sometimes says nothing at all around it.** On a voice call the caller hears silence. At the end of a call it may also say goodbye without calling the end-call tool, or end the call without a word.
- **What to do:** Tie the line and the tool call together in one instruction, for example: "Say 'Let me pull up your account.' and call `lookup_account` in the same response." For tools that always need a line, set the tool's start message so something is always said.

### Local instructions over global rules

- **GPT-4.1** kept the general rules at the top of the prompt in mind for the whole call, such as a closing question or a text it promised to send.
- **Sapien Lite** follows the instruction for the step it's on. **When a step has its own last line, it often drops the closing steps written elsewhere. It can end the call while the caller still has an open request, or hand the call back instead of closing it.**
- **What to do:** Repeat each closing step inside every branch that needs it, for example: "Then send the link and follow # Closing." Say plainly when the call is allowed to end.

### Tool descriptions

- **GPT-4.1** followed the system prompt when a tool's description disagreed with it.
- **Sapien Lite** gives tool descriptions, parameter options and the text in tool results more weight than the system prompt. **It calls tools whose description invites them, such as a finish or end tool, even when the prompt says not to.**
- **What to do:** Write a complete description for every tool and parameter that agrees with the system prompt. Detach any tool the assistant should never call, and keep instructions out of the text your tools return.

### Using tools

- **GPT-4.1** often answered from memory and skipped lookups the prompt required.
- **Sapien Lite** runs the lookups and verification steps the prompt requires. It also calls tools that are attached to the assistant even when the prompt never mentions them.
- **What to do:** Attach only the tools the assistant actually needs.

### Situations the prompt doesn't cover

- **GPT-4.1** made up an answer from its own general knowledge when the prompt and tools had none, and those answers were sometimes wrong.
- **Sapien Lite** doesn't invent answers. **It takes the broadest, safest option the setup gives it, so it transfers or escalates more often, sometimes sending routine requests down an escalation path.**
- **What to do:** Write down what the assistant should do in the situations that come up often, even if it's only one sentence for each. Say clearly what does and doesn't qualify for an escalation.

### Taking the system prompt literally

- **GPT-4.1** read the system prompt for its intent and filled in what it left unsaid.
- **Sapien Lite** follows the exact wording of conditions and labels. If the prompt says to act on accounts marked "OPEN", an account marked "LATE" falls outside that rule.
- **What to do:** Check that every tool, value and label named in the system prompt matches what your tools actually return.

### Scripted lines

- **GPT-4.1** treated sample lines in the prompt as inspiration and varied the wording.
- **Sapien Lite** says short sample lines word for word, but **it may trim or reword longer required scripts to fit other rules in the prompt.**
- **What to do:** Label examples clearly and give two or three different ones. Mark lines that must be said exactly with "Say exactly:", and make sure no other rule, such as a formatting rule, contradicts them.

### Empathy and warmth

- **GPT-4.1** sounded warm without being told to, with enthusiasm, reassurance and long turns.
- **Sapien Lite** sounds plainer, with shorter turns and almost no exclamation marks or filler. **Most of its sympathy comes from lines the prompt writes for it; it adds less of its own than GPT-4.1 did.**
- **What to do:** Write acknowledgments into the prompt for the moments that matter, such as bad news, a refusal or a caller in distress. When the assistant can't do what was asked, have it explain why, offer one alternative and say what happens next.

### Following procedures

- **GPT-4.1** sometimes bent procedures when a request looked simple, for example by skipping verification, a disclosure or a required lookup.
- **Sapien Lite** follows the written steps strictly, keeps the disclosures and checks the prompt requires, and doesn't claim an action succeeded when a tool failed.
- **What to do:** Write a fallback line and a next step for each tool failure that matters to you.

### Offering the next step

- **GPT-4.1** offered the obvious next step on its own, for example asking "Is there anything else I can help with?"
- **Sapien Lite** answers what the caller asked and then waits. It rarely asks "anything else?" unless the current step tells it to.
- **What to do:** Write in the prompt what the next step should be after each kind of answer or tool result.

## Prompt work that helps

Anything the team relied on GPT-4.1 doing implicitly has to be written down: what to say with each tool call, the closing sequence inside each branch, when the call may end, what qualifies for an escalation, the next step after each kind of answer, and which tools exist. [Fixes](fixes.md) lists the wording that works for each symptom.

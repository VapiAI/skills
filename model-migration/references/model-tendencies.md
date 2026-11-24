# How Terra and Luna behave compared with GPT-4.1

What to expect when an assistant moves from GPT-4.1 to gpt-5.6-terra or gpt-5.6-luna on the same prompt. We ran GPT-4.1, Terra and Luna on the same simulated scenarios across several real-world assistants (support, collections, applications and scheduling, including a multi-assistant squad), each on its unchanged prompt, and compared the transcripts. Each pattern below held on more than one assistant and for both new models. They're tendencies, not guarantees, and they're ordered by how much they're likely to affect calls. Examples are anonymized.

Neither model is simply better or worse than GPT-4.1. On rule checks both matched or beat it on the assistants we tested. What changes is how they behave.

## Contents

- [Both Terra and Luna, compared with GPT-4.1](#both-terra-and-luna-compared-with-gpt-41)
- [Where Terra and Luna differ](#where-terra-and-luna-differ)
- [What this means for a prompt](#what-this-means-for-a-prompt)

## Both Terra and Luna, compared with GPT-4.1

1. **Local instructions over global rules.** GPT-4.1 kept the general rules at the top of the prompt in mind for the whole call. Terra and Luna follow the instruction for the step they're on, and skip global steps that the current step doesn't repeat.
   *Example:* a prompt said "always ask if there's anything else before closing", but several branches ended with "close the call". GPT-4.1 asked in 60 of 60 conversations on those branches; Terra in 4 and Luna in 8. A link the prompt said to send after a callback was sent in 12 of 12 on GPT-4.1, 0 on Terra and 1 on Luna.

2. **Taking the system prompt literally.** GPT-4.1 read the prompt for its intent and filled in what it left unsaid. Terra and Luna do exactly what the prompt says.
   *Example:* a prompt called its end-call tool `end_call`, but the tool's real name was `end_call_tool`. GPT-4.1 ended the call anyway. Terra and Luna often said goodbye and never ended the call.

3. **Situations the prompt doesn't cover.** GPT-4.1 made up an answer from general knowledge, and was often wrong. Terra and Luna don't invent answers: they hold back and take the broadest option the setup gives them, which on many assistants means more transfers or callbacks.
   *Example:* asked whether a document was required, which the prompt didn't say, GPT-4.1 answered anyway in 11 of 12 conversations. Terra never did, and Luna did once.

4. **Tool descriptions.** GPT-4.1 followed the system prompt when a tool's description disagreed with it. Terra and Luna give tool descriptions, parameter descriptions and text in tool results more weight than the system prompt. Complete, consistent descriptions matter more than before; empty or bare ones leave the model guessing.
   *Example:* a finish tool whose description said to use it when the conversation was complete got called by Terra and Luna, even though the prompt said never to call it. GPT-4.1 never called it. A note in a mocked tool result telling the assistant to skip an offer made both skip an offer the prompt said was mandatory.

5. **Empathy and warmth.** GPT-4.1 sounded warm without being told to: enthusiasm, reassurance, and a reason or alternative with every "no". Terra and Luna sound more neutral, with turns about a third shorter, and most of their warmth comes from what the prompt writes. Where a prompt limited acknowledgments, GPT-4.1 often ignored the rule and the new models followed it.
   Counting phrases like "I'm sorry" can miss this: the new models may apologize as often, yet the call reads colder because the enthusiasm, the extra offers and the reasons behind each "no" are gone.

6. **Offering the next step.** GPT-4.1 offered the obvious next step on its own, such as "anything else?" or a link. Terra and Luna answer and wait, unless the current step says what comes next.
   *Example:* after answering a general question, GPT-4.1 offered to text a link in 11 of 11 conversations; Terra in 4 of 12, Luna in 2 of 12.

7. **Following procedures.** GPT-4.1 sometimes bent procedures when a request looked simple, skipping verification or a required lookup. Terra and Luna follow written steps strictly and in order, and keep counted steps more closely than GPT-4.1. When a tool fails and the prompt has no recovery step, they stop or send the caller elsewhere instead of improvising.
   *Example:* when an action failed and the prompt said "retry once, then read this line", Terra did both in 13 of 13 conversations; GPT-4.1 never retried.

8. **Scripted lines.** GPT-4.1 treated sample lines as inspiration and varied them. Terra and Luna say them word for word.
   *Example:* a prompt's sample closing "Thanks for your time. Bye" ended 19 conversations on GPT-4.1, 72 on Terra and 111 on Luna, so calls started to sound alike.

9. **Using tools.** GPT-4.1 often answered from memory and skipped required lookups. Terra and Luna run the lookups the prompt requires, and may also call attached tools the prompt never mentions.
   *Example:* on a support assistant that required a knowledge lookup before giving steps, GPT-4.1 skipped it in 45 of 108 conversations and made up troubleshooting steps. Terra and Luna almost always ran it.

10. **Saying and doing.** GPT-4.1 usually paired what it said with the matching tool call. Around transfers, texts and ending the call, Terra and Luna sometimes separate the two: a tool call with nothing said first (silence on a voice call), or "connecting you now" with no tool call. Both stop talking after a transfer or end-call tool, where GPT-4.1 often kept going, and both rarely claim an action that no tool confirmed.
    *Example:* on a scheduling squad, the first transfer happened with no spoken words 58 times on Terra and 113 times on Luna, and never on GPT-4.1.

## Where Terra and Luna differ

In general, Luna is the faster, lower-cost model and Terra is the more accurate and capable one. For cost and latency figures, use Vapi's model benchmarks or measure on the user's own assistant. In behavior, most patterns above held for both; these are the specific differences:

| Behavior | Luna | Terra |
|---|---|---|
| Saying and doing | More likely to say it's doing something without calling the tool (13 of 36 safety transfers on one assistant, against 1 for Terra) | More likely to call a tool with nothing said first, especially the first lookup of a call (117 of 204 first turns on one assistant, against 15 for Luna) |
| Counted steps | Follows them, less exactly (transferred on the third request in 9 of 18) | Keeps them exactly (18 of 18) |
| Tone | More often answers and waits for the caller to lead | Plainest style and slightly shorter turns |

## What this means for a prompt

Anything a team relied on GPT-4.1 doing implicitly has to be written down: the next step after each kind of answer, the closing sequence inside each branch, what to say with each tool call, how to refuse (reason, alternative, next step), when to acknowledge feelings, and which tools exist. [Fixes](fixes.md) lists the wording that works for each symptom.

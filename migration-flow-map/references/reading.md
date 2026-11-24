# Reading calls into a flow tree

How to label sampled calls with intents, paths and endings, decide when enough calls have been read, and turn the labels into a traffic-weighted tree.

## Contents

- [What a label records](#what-a-label-records)
- [Pilot: build the category list](#pilot-build-the-category-list)
- [Label the rest](#label-the-rest)
- [When to stop](#when-to-stop)
- [Build the tree](#build-the-tree)
- [Branches the prompt defines](#branches-the-prompt-defines)
- [Common mistakes](#common-mistakes)

## What a label records

One record per call, written by a reader who sees only that call's transcript, tool calls and tool results (never the caller's personal data in the output):

```json
{
  "call": "<call id>",
  "intent": "reschedule_appointment",
  "secondary_intents": ["ask_parking"],
  "path": ["identify_caller", "find_appointment", "offer_new_times", "confirm_change"],
  "ending": "resolved",
  "caller_traits": ["changes_mind"],
  "tool_answers": {"find_appointment": "found_one"},
  "notes": "Caller asked about parking after confirming."
}
```

- **Intent:** why the caller called, in one category. The first real request counts, not the greeting.
- **Path:** the steps that actually served the intent, in order. Leave out steps that were only offered or mentioned.
- **Ending:** one value from a short fixed list agreed with the user, for example `resolved`, `transferred`, `callback_scheduled`, `refused`, `caller_hung_up`, `no_engagement`. These endings become the ending evaluation in every simulation, and they are what deflection or containment is computed from, so align them with `metrics.md`.
- **Caller traits:** behavior that changes the conversation (upset, confused, speaks another language, gives information out of order).
- **Tool answers:** the kind of answer each tool gave (found, not found, error, locked), not the values.

## Pilot: build the category list

1. Read about 50 calls from across the sample, starting from the category list drafted from the prompt (SKILL.md step 3). Readers use its names where they fit and propose new ones for what the prompt didn't anticipate.
2. Merge the proposals into the category list: each new category gets a short definition and the alternative names readers used.
3. Show the list to the user and agree it. The user knows which distinctions matter to the business (for example whether "change payment date" and "make a payment" are one intent or two).

## Label the rest

- Label the remaining sample in batches of 20 to 25 calls with the fixed list. If the agent supports sub-agents, give each reader one batch, the category list and these instructions, and nothing else.
- A reader that finds a call no category fits proposes a new category with a definition. Collect proposals per batch, agree them with the user, and relabel earlier calls that fit.
- Hand-check about 10 labels against their transcripts after the first batches. Fix the instructions, not just the labels, when a reader misunderstood.

## When to stop

Stop reading when new batches stop adding categories. A practical rule: stop when the share of intents seen in only one call (out of all calls read) is under about 1%, and no ending or step has been seen only once. For a small assistant this can happen after 150 calls; a squad may need 500 or more. Record the number read and the rule used.

## Build the tree

- The tree has three levels: intent > path > ending. Each node carries its share of traffic and 1 to 3 example call IDs (IDs only, never content).
- Weight each read call by how representative it is. If the sample was spread evenly across days, each call counts equally. If some days or groups were over-sampled, weight by their share of all calls in the window.
- Merge paths that differ only in order of trivial steps. Keep paths separate when a step changes the outcome (a failed verification, a tool error).
- Report traffic shares as percentages with the number of calls behind them, and a share for "other" (intents too rare to list).

## Branches the prompt defines

The calls only show what callers did. A rare situation the prompt handles explicitly (an escalation, a legal edge case) may never appear in the sample, yet it is often the first thing a new model gets wrong. So the prompt is read for its own list of branches before any call is read (SKILL.md step 3), and the calls are mapped onto it.

- **What counts as a branch:** a situation the prompt tells the assistant to handle differently. Group the sentences that describe one handling. A general rule ("never make things up") is a check on every scenario, not a branch.
- **Quote, don't infer:** each branch carries the prompt's exact words. A situation you expect an assistant like this to need, but the prompt doesn't state, is not a branch; put it in `owner_questions.md`.
- **Anchor to the category list:** each branch names its intent, steps and ending from the category list. A branch that needs a name the list doesn't have means the list is missing something: add it there first, with a definition.
- **Size:** one branch per distinct handling, at the level of the category list's steps. A list of lookup results, symptoms, form types or provider names that all get the same handling is one branch, not one per item. The same rule in several members is one branch. A seven-member squad with long prompts landed at about 175 branches; several hundred means branches are being split below one handling.
- **Seen or not:** after the calls are read, a branch is `seen` when some read call has its intent, steps and ending, with the share of calls that did. Otherwise it is `prompt_only`. Show the `prompt_only` list to the user. Each one they keep becomes a zero-weight scenario in the All level, after merging.

## Common mistakes

- **The real assistant's behavior is not the answer key.** A call supplies the caller, their situation and what the tools returned. What the assistant should do comes from the prompt and the team's rules. When the prompt is silent, don't invent a rule; add it to the owner question list.
- **The first message is not an intent.** Neither is a request for a human; record why the caller wanted one.
- **Don't count a step that was only offered.** "Would you like me to text you a link?" followed by "no" is not a text-link step.
- **Mask as you go.** Readers write no names, numbers or addresses into records.

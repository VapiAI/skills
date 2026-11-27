# Model card: sapien

- **Target model:** `sapien` (provider `vapi`)
- **Starting model:** GPT-4.1
- **Last updated:** 2026-11-26
- **Evidence:** GPT-4.1 and Sapien on the same simulated scenarios across seven real-world assistants (support, collections, applications and scheduling, including a multi-assistant squad), each on its unchanged prompt, 3 runs per scenario. Each pattern held on more than one assistant. Examples are anonymized.

This card is a starting point. It covers the main patterns we saw when we tested Sapien against GPT-4.1 on several real assistants. Your assistant may behave differently in ways our tests didn't show, so test your own key scenarios before you switch.

## Contents

- [Recommended settings](#recommended-settings)
- [What to expect](#what-to-expect)
- [How to use this card](#how-to-use-this-card)
- [Behaviors compared with GPT-4.1](#behaviors-compared-with-gpt-41)
- [How this changes your prompt](#how-this-changes-your-prompt)

## Recommended settings

Set these fields inside the assistant's existing `model` object, and keep `messages`, `tools`, `toolIds` and every other field as they are:

```json
{
  "provider": "vapi",
  "model": "sapien"
}
```

- Vapi manages reasoning for Sapien, so there's no reasoning setting to choose.
- If the update is rejected because of fields that only apply to OpenAI models, such as `reasoningEffort`, `serviceTier` or `promptCacheRetention`, remove them from the copy.
- Check that `maxTokens` isn't low, and set the same explicit value on both copies.
- Check `fallbackModels`: remove GPT-4.1 entries carried over from the old configuration, and set the production fallback explicitly before rollout.

## What to expect

- Sapien is Vapi's own model, with high intelligence at extremely low latency. Confirm latency and cost per minute on the user's own assistant (step 8 of the skill).
- Of the new models, it's the closest to GPT-4.1's habits (style, warmth, "anything else?" check-ins). That's neither good nor bad by itself; it means less tone work than the other new models need.
- Check that every transfer, text and booking the assistant mentions has a matching tool call in the transcript, and include failing tool results in your scenarios.
- Most prompt work for Sapien is about where instructions live: when to call a tool belongs in the prompt and what the tool does in its description. A start message can carry what the caller hears, but test transfers on your own calls.

## How to use this card

Apply these changes while building the Sapien copy, so the first version tested is already adapted:

1. For each pattern below, check the prompt and tools for the shape under **In the prompt**. Only apply the **Change** where that shape is there; leave everything else as it is.
2. Adapt the before/after example to the prompt's own wording. Never paste the example text.
3. Follow each **Don't**: these are variants that made things worse in our tests or common mistakes with this pattern.
4. Show the user the list of changes you made (pattern, where, one line each) in `review.md`, then build the copy. No approval step.
5. Add each applied pattern's **Check with** scenarios to the suite. During the comparison runs, watch for the **In transcripts** signals; if one still shows, treat it as a step 7 fix.

## Behaviors compared with GPT-4.1

### Keep actions on the tool

- **In the prompt:** an action (a text, a transfer, a booking) that should happen on several paths but is tied to one moment, or a complete-sounding line to say before the action, such as "Let me send that over."
- **Change:** say when to act on every path that should end with the action, and put the line the caller hears in the tool's start message.
  - *Before:* "Everyone gets the link by text as you wrap up." with a callback branch that ends "Set up the callback."
  - *After:* "Once the callback is set up, send the link if you haven't yet, then close the call." (text tool's start message: "I'm texting you the link now.")
- **Don't:** tie the action to a single moment with "only", such as "send the link only as you wrap up"; in our tests that skipped the action on paths where the call went to a person.
- **In transcripts:** a line that announces a transfer, text or booking with no matching tool call in that reply, or a follow-up promised after a send failed.
- **Check with:** every transfer path, the paths where the call goes to a person or a callback, and a failed send.

### Give each instruction one home

- **In the prompt and tools:** a condition for calling a tool written only in the tool's description, troubleshooting steps or sample answers inside example dialogues, or a tool that returns a normal result when the next step can't run.
- **Change:** let the prompt say when to look things up, use placeholders for steps in example dialogues, and have tools return an error when the next step can't run.
  - *Before:* example dialogue "Assistant: First, open the app to your devices screen."
  - *After:* example dialogue "Assistant: (gives the first returned step)"
- **Don't:** delete facts the assistant answers from; in our tests it then answered those questions wrongly.
- **In transcripts:** a step read out before any lookup, or a lookup run right after a failed check.
- **Check with:** a failed verification followed by a status question, troubleshooting questions, and a question answered from a fact in the prompt.

### Keep each rule in one place

- **In the prompt:** one rule that chooses between options, such as a live transfer or a callback, while other lines name only one option; or an absolute clause that contradicts a local rule.
- **Change:** keep the choice in that rule, have other lines name only the generic option, and delete lines that contradict it.
  - *Before:* "If you can't answer, offer a specialist callback." with "In business hours, transfer live instead." elsewhere.
  - *After:* "If you can't answer, offer a specialist." and, in one place, "Specialist help: in business hours, transfer live; otherwise, set up a callback."
- **Don't:** add an exception beside a contradicting line; delete the line, so one rule decides.
- **In transcripts:** a callback offered during business hours, or another option taken where one rule should have decided.
- **Check with:** requests for a person in and out of business hours, and the cases each contradicting line used to cover.

### Aim for good prompt coverage

- **In the prompt:** common questions from the flow map with no line saying what to say, especially questions the team can't answer.
- **Change:** for each one, write either the answer or what to say instead, right after the rule it falls under.
  - *Before:* the question listed under what the assistant doesn't know, with nothing about what to say.
  - *After:* "If they ask whether they need to send in extra documents, say you're not sure and offer a callback."
- **Don't:** only list a question as unknown; say what to do about it.
- **In transcripts:** a confident answer to a question the prompt doesn't answer.
- **Check with:** the uncovered questions, plus covered questions nearby to confirm they still get answered.

### Required steps carry over

- **In the prompt:** required notices and lookups, which Sapien keeps even where GPT-4.1 sometimes skipped them.
- **Change:** keep required steps as written, and for a required lookup, say where it runs.
  - *Before:* "Look up the account."
  - *After:* "Look up the account before your first answer about it."
- **Don't:** remove a step because callers rarely heard it before; ask the user whether it should stay.
- **In transcripts:** steps callers rarely heard before, such as a required notice, or an answer given before a required lookup.
- **Check with:** the scenarios that reach each required notice and lookup.

### Scripted lines

- **In the prompt:** scripted lines that announce or confirm an action.
- **Change:** no extra marking is needed; tie a confirmation line to the tool's result.
  - *Before:* "Say 'I've sent the link to your phone.'"
  - *After:* "When the text tool returns success, say 'I've sent the link to your phone.'"
- **Don't:** add "Say exactly:" markers or extra examples for scripted lines; Sapien already says them as written.
- **In transcripts:** a scripted action line said word for word with no matching tool call.
- **Check with:** each scripted line that announces or confirms an action.

### Test the judgment calls

- **In the prompt:** rules that rest on judgment, such as what counts as an emergency, or a tool-result field named differently from what the tool returns.
- **Change:** name fields as the tools return them, and leave judgment rules as written for the tests to check.
  - *Before:* "If `confirmed` is true, continue."
  - *After:* "If `status` is `CONFIRMED`, continue."
- **Don't:** replace a judgment rule with a keyword list; describe it by meaning.
- **In transcripts:** a routine request sent down an urgent path, or an urgent one treated as routine.
- **Check with:** a clear case and a borderline case for each judgment call that matters.

### Reply style and length

- **In the prompt:** length or formatting rules, or none at all.
- **Change:** keep the rules you have; add a plain-speech rule only if test calls show lists or markdown.
  - *Before:* (no formatting rule, and a test reply reads out a bulleted list)
  - *After:* "Speak in short, plain sentences, with no lists or markdown."
- **Don't:** trim tone or length rules written for GPT-4.1; Sapien's replies stay close to GPT-4.1's.
- **In transcripts:** markdown, numbered lists, or several questions in one turn.
- **Check with:** a few test calls in the user's voice.

### Acknowledgments and apologies

- **In the prompt:** a rule that limits acknowledgments or apologies.
- **Change:** make the limit concrete: how many, and at which moments.
  - *Before:* "Acknowledge only once."
  - *After:* "Acknowledge the caller's feelings at most once per call, in your own words, when they share bad news."
- **Don't:** add a menu of empathy phrases; it turns into a stock line.
- **In transcripts:** repeated "I'm sorry to hear that", stock phrases that aren't in the prompt, or an apology before every failed lookup.
- **Check with:** upset callers and failed lookups.

### Where check-ins land

- **In the prompt:** a step that promises an action, such as a text, followed by a closing check-in.
- **Change:** put the check-in after the action's result.
  - *Before:* "Tell them you'll text the link, then ask if there's anything else."
  - *After:* "Send the link; once it's sent, ask whether there's anything else you can help with."
- **Don't:** write check-ins back into other steps; Sapien keeps GPT-4.1's check-ins on its own.
- **In transcripts:** "anything else?" before an action that hasn't happened yet.
- **Check with:** the paths with a text or booking near the close.

## How this changes your prompt

Most of what the team relied on GPT-4.1 for carries over: tone, warmth, check-ins and judgment calls stay close to GPT-4.1's. The changes above are about where each thing lives: the prompt says when to call each tool and what to do after each result, tool descriptions say what a tool does and what its parameters mean, the tool's start message can carry what the caller hears while it runs, and the knowledge base holds step lists while the prompt keeps the facts the assistant answers from. Each rule gets one place, and lines that contradict it go. Apply them while building the copy, as **How to use this card** says, and cover them with scenarios that check the tool calls, including failing tool results. [Fixes](fixes.md) lists wording for any symptom that still shows in the comparison runs.

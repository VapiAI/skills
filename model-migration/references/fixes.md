# Fixes by symptom

Wording and configuration changes that resolved the behavior differences in the model cards ([index](model-cards.md)). Apply a fix only when the comparison shows the symptom on the new model and the transcripts confirm it is the model, not the test. Every fix is a wording, tool-list or setting change; none adds a workflow the team didn't already have.

## Contents

- [Before you test: prompt and tool hygiene](#before-you-test-prompt-and-tool-hygiene)
- [Tools and actions](#tools-and-actions)
- [Conversation flow](#conversation-flow)
- [Tone and warmth](#tone-and-warmth)
- [Scripts and style](#scripts-and-style)
- [Fixes that did not work](#fixes-that-did-not-work)

## Before you test: prompt and tool hygiene

| Check | Why | Change |
|---|---|---|
| Every tool name in the prompt matches the tool's real function name | The new models take names literally; a near-miss name means the tool isn't called | Rename in the prompt, or create a renamed copy of the tool for the copies. Never edit a tool the live assistant uses |
| Tools the prompt never uses or forbids | The new models call any attached tool, and follow a tool's description over a "don't call X" line | Remove the tool from the copy. If it must stay, give the copy a new tool whose description agrees with the prompt |
| Tool descriptions and parameter descriptions agree with the prompt | A parameter hint ("in the normalized format") beats a prompt rule ("remove the +1") | State the exact format in the parameter description, on a new tool for the copy |
| Per-call values (date, time, caller number, IDs) appear early in the prompt | Everything after the first per-call value can't be cached across calls, which costs money and latency | Move them into one block at the very end of the prompt; set `promptCacheRetention: "24h"` |
| Rules that forbid acknowledgments, apologies or reassurance, or cap replies at one or two sentences | 4.1 ignored them; the new models obey, and sound flat or cut scripted lines short | Propose to the owner deleting them or scoping them to the turn they were meant for |
| Notes in tool results (`"recommendedAction": "skip_offer"`) | The new models follow notes in tool results over the prompt | Remove advisory text from results, or make the prompt say which one wins |
| Contradictions between rules, and situations no rule covers | Each model resolves them differently, which shows up as false model differences | Ask the owner and write the answer down before testing |

## Tools and actions

| Symptom | Fix |
|---|---|
| Calls a tool with nothing said first; silence on a voice call | Script the line in the same instruction as the tool: "Say 'Let me transfer you to our billing team.' and call `transfer_call` in the same response." |
| Says it will act ("connecting you now", "I'll text you the link") but no tool call follows | Same: line and tool in the same response. Add: "Never say you are transferring, texting or booking unless you call the tool in that same response." |
| Splits a line and its tool across two turns | "Say this, then call X" reads as two steps. Write "in the same response". |
| Says goodbye but never ends the call | Name the end-call tool exactly, and write: "Say the goodbye line and call `<end tool>` in the same response." |
| Goes silent after a tool result the prompt doesn't name | Name every result that needs a spoken reply, and add: "After any tool result, the caller always gets a spoken reply." |
| Empty reply after the caller says "okay" or "thanks" | Give a line for when nothing is open: "If the caller only acknowledges and nothing is pending, ask whether there is anything else, or close with the goodbye line." |
| Ends the call or moves on when a tool returns a result the prompt doesn't name | Add a short "If a tool fails or returns something unexpected" rule with the exact line to say and the next step |
| Changes argument formats (keeps or drops a country code, reformats dates) | Put the exact format, with an example value, in the parameter description of a new tool for the copy |

## Conversation flow

| Symptom | Fix |
|---|---|
| Skips "anything else?" or the closing steps after a branch that ends with its own last line | Write the closing steps once, remove other "close the call" endings, and end each branch (failures and declined offers included) with a pointer that names the next step: "Then send the link with `send_sms` and follow # Closing." |
| Answers and waits, without the next step 4.1 offered | A next-action table: for each kind of answer or tool result, the specific next step, placed before any generic "anything else?" |
| Loses the caller's open request after a side question, or treats "okay" as the end | A short conversation-state section: keep the caller's oldest unresolved request open through side questions; "okay" or "thanks" doesn't mean the request is done |
| Gives a bare "no" and repeats it when the caller pushes back | A refusal pattern: every "no" gives the reason, one alternative, and what happens next. On pushback, offer something different instead of repeating |
| Transfers on the first request for a person where the prompt wants an offer first | Script the first-request reply: "The first time the caller asks for a person, say '...' and ask what they need help with. Transfer only if they ask again." |
| Presumes the caller's answer (asks for a time without asking whether they want a callback) | Make the consent step its own line: "First ask whether they'd like a callback. Only if they say yes, ask what time works." |
| Takes a situation the prompt doesn't cover to the broadest rule (usually a transfer) | Write down what should happen in that situation. If it is rare, one sentence is enough |
| Re-asks for information the caller already gave, after a blunt "end every turn with a question" rule | Remove the blanket rule; use the next-action table instead |
| Optional wording ("you may offer...") is skipped | If the team wants it done, write it as a step, not a permission |

## Tone and warmth

What worked:

- **Acknowledge at named moments, in the model's own words.** Acknowledge when the caller voices a feeling or hears bad news (a denial, a failed check). Never for routine answers, questions, or requests for a person. A short reflection specific to what they said; use their own word ("frustrating") only if they said it. Keep a fixed line only for a death ("I'm very sorry for your loss").
- **Cap it.** At most two acknowledgments per call, never in two replies in a row. The acknowledgment comes before the scripted line, never replaces it, and never changes the next step.
- **Pair every "no" with a path** (the refusal pattern above). Much of 4.1's perceived warmth came from this, not from sympathy phrases.
- **A warm goodbye only when the caller thanks the assistant.**
- **Measure it.** Copy about 8 existing scenarios with an upset caller (a denial, money stress, an unexpected fee, grief, repeating themselves) and add two checks: acknowledged the caller's strongest emotional moment (up to the cap of two); sounded natural without repeating itself. Also count acknowledgment phrases per conversation on the regular suite and keep it near the 4.1 baseline; far above reads as robotic.

## Scripts and style

| Symptom | Fix |
|---|---|
| Sample lines repeated word for word, calls sound templated | Mark them clearly ("Example, adapt to the caller:") and give two or three different examples, or describe what the line must contain instead of quoting it |
| A required scripted line is trimmed or reworded | Mark required wording explicitly: "Say exactly:" and quote it. If a general rule conflicts with the line (for example "don't mention transfers"), say the line is the exception |
| A global formatting rule rewrites text it shouldn't (codes or IDs turned into words) | Name the exceptions: "Say codes like AB12 letter by letter." |
| Prompt typos read aloud | Fix the typos in scripted lines |
| A language rule read too literally (English replies to a caller speaking Spanish who didn't ask for Spanish) | Say what triggers the switch: "If the caller speaks Spanish, switch to Spanish, even if they don't ask." Say which scripted lines to translate |

## Fixes that did not work

- **Abstract tone rules** ("be warm", "be empathetic", "short but never curt", "sound natural"). No measurable change, and "sound natural" made one model narrate its internal checks and stack filler phrases.
- **Telling the model when to acknowledge without saying how.** Acknowledgment rates didn't move.
- **A menu of example empathy phrases with broad triggers.** It became a stock line, used even after neutral replies ("I understand, that's frustrating" after "yes, this is me").
- **A single "do not call X" line** against a tool whose own description invites the call. Remove or rewrite the tool instead.
- **Raising reasoning effort** to fix conversation-flow problems. Prompt structure fixed them; higher effort added latency and cost.
- **A blanket "end every turn with a question".** The model re-asked for information the caller had already given.

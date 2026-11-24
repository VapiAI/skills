# Building scenarios from a flow map

How to turn the output of `migration-flow-map` (`flow_tree.json`, `tool_catalog.json`, `scenario_list.json`) into Vapi scenarios, mocks and evaluations. Without a flow map, build the same entries from the prompt and tools with the user (SKILL.md step 3).

## Contents

- [One entry, one scenario](#one-entry-one-scenario)
- [Caller instructions](#caller-instructions)
- [Mocks](#mocks)
- [Evaluations](#evaluations)
- [Caller personality](#caller-personality)
- [Checks before saving](#checks-before-saving)

## One entry, one scenario

Each `scenario_list.json` entry has an ID, the path it covers, its traffic weight, the caller's goal and facts, the tool answers for this situation, the expected ending, and the rules it checks. Keep the entry ID in the scenario name (`MIG-007 reschedule appointment - resolved`) so results map back to the flow map.

## Caller instructions

- Write the caller's goal and the facts they know (synthetic names, dates, numbers). Never script what the assistant should say.
- Say when the caller ends the conversation, in terms of something the assistant does: "Hang up after the assistant confirms the new time", "Hang up once the assistant says it is transferring you." A transfer never ends a simulated chat (the transfer tool is mocked), so a caller told to stay on the line holds until the turn limit. The caller's last line and the hang-up are separate turns: the caller says its last line, waits for the assistant's reply, and hangs up only after the assistant's goodbye. A caller that hangs up in the same turn as its last line cuts off the closing steps you want to grade.
- Never let the caller bring up a step before the assistant does (a survey, a callback offer), or that step can't be graded.
- Give the caller only the information this path needs. A caller who volunteers everything up front skips the steps you want to test.

## Mocks

- Every tool in the target's configuration needs a mock in every scenario, except tools of type `endCall` and static squad handoffs, which act inside Vapi only. A custom function named `end_call` needs a mock. A dynamic handoff (which asks a server for its destination) is not exempt either: point it at a test endpoint or make it static on both copies. Every static handoff tool needs `destination` as a required parameter on both copies, even one with a single destination: a `destination` property (a string whose enum is the destination assistant names, with a description saying to always pass it) and `destination` in `required`. The property is what tells the model to send it; because a simulation refuses a handoff call that leaves it out (see the `model-migration` skill's squad notes). Use the tool's function name exactly as the model sees it (`toolCall.function.name`), not its display name.
- **One fixed answer per tool per scenario.** Vapi returns the same mock result every time that tool is called in that scenario. Design around it:
  - A situation where the same tool should answer differently on a second call (a wrong date of birth, then a right one) becomes two scenarios, or one scenario where the caller gets it right the first time.
  - A value the assistant is supposed to ask for (an amount, a date) should not be baked into the mock in a way that lets the assistant skip asking.
- Copy the shape of real answers from `tool_catalog.json`: same fields, same order, same error format. Use synthetic values with the same format as real ones.
- Include the answers that drive behavior: not found, locked, already done, error. A suite where every tool succeeds tests only the happy path.
- Encode JSON results as a string.
- A mocked transfer answers and the conversation goes on. Grade transfers on the transfer tool call (and its destination), and ignore anything after it.

## Evaluations

Each scenario gets:

1. **Ending** (required): a string output whose allowed values are the endings from the flow map, compared with `=` to this scenario's expected ending. A conversation can reach more than one (a booking fails, then a transfer), so list the endings in priority order in the evaluation and tell the grader to pick the first that applies. Deflection, containment and booking rates are computed from the ending each conversation actually reached (the evaluation's extracted value), not from whether it matched.
2. **Path** (required): one Boolean per step the path must include ("verified identity before reading the balance").
3. **Rules** (required): one Boolean per compliance situation this scenario exists to test, plus one per general rule (from the flow map's rules list) that can come up in this scenario. General rules are checks, not scenarios of their own; attach only the ones the conversation can actually reach.
4. **Metric proxies** (optional): from `metrics.md`, marked `required: false`.

Write each evaluation so a grader who sees only the transcript and the evaluation text reaches the right answer:

- **Quote the words being graded.** The grader never sees the prompt. "Read the disclosure" fails a correct reply; "said that the payment will be charged to the card ending in the last four digits the caller gave" doesn't.
- **Judge recorded facts.** A booking passes when the tool result shows success, not when the assistant says "you're all set".
- **Tell the grader that tool calls and tool results in the transcript are not words the assistant said.** Chat transcripts can print them as assistant lines.
- **A tool name written as text is not a tool call.** Say so in any evaluation about a tool.
- **Use a regex check, not an AI grader, for whether a tool was called** (and with which argument). AI graders can disagree on identical transcripts; a regex structured output that matches the tool's name in the transcript's tool-call lines gives the same answer every time.
- **Check that lookups use collected values.** A mock answers whatever arguments it gets, so a model that calls a lookup with a placeholder (a literal `{{dob}}`) still gets a patient back. Where the assistant must collect a value before a tool call, add a check that the call's arguments hold the caller's values, not `{{...}}` placeholders or empty strings.
- **Allow equivalent wording and order.** Accept digits or words for numbers.
- **Write counting rules as positive musts:** "transferred only after the caller's third request", not "did not transfer before the third request".
- **Conditional checks pass when the condition never happened:** "If the caller asks for a human, the assistant offers one alternative before transferring. Pass if the caller never asks."
- **One fact per evaluation.** Split "confirmed the time and offered a reminder" into two.

## Caller personality

Use one caller personality for the whole suite unless a scenario needs a different temperament (upset, confused, rushed). In its system prompt:

- Follow the scenario's facts; never invent account details.
- Never mention a step before the assistant offers it.
- Let the assistant answer "anything else?" before hanging up, unless the scenario says otherwise.
- Never hang up in the same turn as your last line; wait for the assistant's reply and its goodbye first.
- Hang up once a transfer starts.

Keep the personality and its model the same for every model you compare.

## Checks before saving

- Every target tool except `endCall` tools and static handoffs has a mock in every scenario.
- Every scenario has a required, text-based ending evaluation.
- Every rule from `metrics.md` "Rules that must never break" is checked on at least one scenario, and every compliance situation in the scenario list has its scenario.
- No real customer data anywhere: names, numbers, addresses and IDs are synthetic.
- Names are unique per scenario, so run results can be read by scenario name.

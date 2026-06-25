# Squad Prompting

Use this reference when designing or auditing Vapi Squads, multi-assistant voice workflows, router assistants, specialist assistants, or handoffs between assistants.

## When To Use A Squad

Prefer a Squad when a single assistant prompt would become broad, conflicting, or latency-heavy because it must handle multiple specialized workflows. Squads are useful when the conversation has clear specialist roles, such as triage plus scheduling, orders plus returns, or router plus domain specialists.

Prefer a single assistant when one focused role can complete the whole workflow without many branches, handoffs, or tool sets.

Vapi Squads are specifically meant to split complex workflows into focused assistants with specific tools and clear goals. The first squad member starts the call unless the configuration specifies an entry assistant for a squad destination.

If this choice is unclear, ask before drafting:

```text
Should this be designed as one Vapi assistant, or as a Vapi Squad with multiple assistants and handoffs?
```

## Squad Output Shape

Return a prompt set, not one giant system prompt:

1. Squad overview: purpose, caller experience, and member list.
2. Entry assistant prompt: greeting, intent classification, routing, and guardrails.
3. Specialist assistant prompts: one focused prompt per member.
4. Handoff rules: when each assistant transfers, what it must confirm first, and what it passes forward.
5. Context requirements: caller details, extracted intent, tool results, state, and any summary needed by the next assistant.
6. Shared guardrails: rules that every member must obey.
7. Per-assistant examples: short examples that show normal behavior and handoff behavior.
8. Configuration notes: handoff tools, destination names, and context-passing choices.
9. External tests: routing, fallback, failed handoff, and context preservation scenarios.

## Prompt Boundaries

Keep each assistant narrow:

- Entry/router assistants classify, collect minimal context, and hand off.
- Specialist assistants complete one domain workflow.
- Emergency or escalation assistants handle safety-critical branches only.
- Human-transfer paths should include a warm summary when useful.

Do not copy every instruction into every member prompt. Put shared rules in a shared guardrails section, then include only role-specific instructions in each assistant prompt.

## Handoff Design

Define handoffs as behavioral rules plus configuration needs:

- Source assistant
- Destination assistant
- Trigger condition
- Required context to pass
- Caller-facing transition message, if any
- Rejection/fallback behavior when handoff is unsafe or missing context

Use exact destination/tool identifiers only in machine-facing configuration notes or `Tool Call:` examples. In spoken prose, describe the destination naturally, such as "the scheduling assistant" or "a support specialist."

For assistant prompts that can call Handoff Tools, include a compact multi-agent context rule:

```text
You are part of a multi-agent system. You can hand off the conversation to another assistant when appropriate by calling a handoff function. Handoffs happen in the background; do not mention internal handoff mechanics to the caller.
```

If the caller should hear an announced transfer or warm transition, write the caller-facing transition in natural language and configure handoff tool messages accordingly. For silent handoffs, configure the Handoff Tool `messages` property as `[]` or `null` and tell the destination assistant to proceed directly to its task without a greeting or small talk.

## Handoff Tool Configuration

When giving Vapi configuration notes, account for these Handoff Tool choices:

- Destination type: assistant by `assistantId`, assistant by `assistantName` within a squad, squad by `squadId`, transient squad, or dynamic destination via webhook.
- Destination descriptions: each destination needs a clear description of when the model should choose it.
- Multiple destinations: prefer separate handoff tools per destination for OpenAI models; prefer one handoff tool with multiple destination options for Anthropic models.
- Custom function definitions: use `tool.function.name`, description, parameters, and required fields when the model must pass handoff arguments or choose among destinations.
- Dynamic handoffs: the backend must return a single destination or a custom error; do not imply dynamic routing exists unless the webhook/server behavior is provided.
- Rejection behavior: use rejection plans or prompt fallback rules when handoff should be blocked because required context, consent, or caller intent is missing.
- Tool messages: configure `request-start`, `request-complete`, `request-failed`, and delayed-response messages when the caller should hear transition status.

Do not invent assistant IDs, assistant names, squad IDs, destination enums, webhook URLs, function parameters, or rejection conditions. List missing values under configuration needed.

## Context Preservation

Before handoff, define what the next assistant needs:

- Caller identity or callback number
- Confirmed intent
- Collected fields
- Relevant tool results
- Safety flags or urgency
- Summary of what has already been said

Do not assume every assistant automatically has the right context. If context passing is required, flag it as a Vapi configuration concern.

Choose a context-passing method deliberately:

- Handoff arguments via `function.parameters`: use for values the model derives inline during the handoff, such as intent, sentiment, urgency, or a concise summary. This adds no extra LLM round trip but can hallucinate or paraphrase.
- `variableExtractionPlan.schema`: use when values are spread across multiple turns and need typed extraction. This is more structured but adds a dedicated LLM extraction call.
- Liquid variables in the destination prompt: use when the value already exists in the variable bag, tool result, call data, or prior extraction. Do not use Liquid as if it can extract from conversation history.

Do not use handoff arguments or handoff extraction as proof of identity, permissions, account ownership, payment status, or compliance eligibility. Treat them as LLM-derived routing/context data unless the destination verifies the sensitive fact through backend-owned state or a trusted tool.

Choose a `contextEngineeringPlan` when relevant:

- `all`: full conversation history; safest default but highest token cost.
- `lastNMessages`: recent context only; useful for latency and context-size control.
- `userAndAssistantMessages`: removes system messages, tool calls, and tool results for a cleaner destination prompt.
- `previousAssistantMessages`: excludes the current assistant's session; useful after sensitive workflows.
- `none`: starts the next assistant without previous conversation context.

When using Liquid variables, add defensive behavior for missing variables so the assistant does not speak raw template tokens such as `{{patientId}}`.

When a handoff follows a sensitive workflow, prefer excluding sensitive tool calls and results from the next assistant's context. If the next assistant needs a trusted value, pass a trusted backend key or have the destination perform its own server-trusted lookup.

## Examples

Each specialist should have at least one compact example for its own workflow. Include handoff examples for the entry assistant and any assistant that routes onward.

Example pattern:

```text
User: "I need to reschedule my appointment."
Assistant: "I can help route you. Is this for an existing appointment?"
User: "Yes, tomorrow at two."
Tool Call: handoff_to_scheduling_assistant(reason: "reschedule_existing_appointment", summary: "Caller wants to reschedule an appointment currently set for tomorrow at two.")
```

Keep examples capability-grounded and identifier-clean.

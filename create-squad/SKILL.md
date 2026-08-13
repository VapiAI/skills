---
name: create-squad
description: Design, create, update, and verify Vapi Squads and documented handoff tools through the public API. Use for choosing a single assistant versus a multi-assistant Squad, persistent or transient members, entry-member ordering, specialization boundaries, context engineering, variable extraction, model-specific handoff patterns, assistant-version pins, and safe Squad updates.
license: MIT
compatibility: Internet access and VAPI_API_KEY are required only for live Vapi API operations.
metadata:
  author: vapi
  version: "2.0"
---

# Vapi Squad Creation

Use a Squad only when multiple focused assistants improve the design. Default to a payload or implementation plan unless the user explicitly requests live Vapi mutations.

## Decide Whether to Use a Squad

Prefer one assistant when one focused prompt and one compatible tool set can handle the use case reliably. Use a Squad for genuine boundaries such as:

- distinct domains or personas;
- different tool or credential access;
- deliberate context isolation;
- separately maintained specialists.

Do not create one assistant per conversational step. Keep related steps in one member and make each handoff boundary earn its latency and operational cost.

## Safety and Source Rules

- Verify squad, member, handoff, context, and version fields against the current public [Squads documentation](https://docs.vapi.ai/squads), [Handoff tool guide](https://docs.vapi.ai/squads/handoff), and OpenAPI schema.
- Never invent assistant IDs, names, tool IDs, destinations, versions, credentials, server URLs, or extracted variables.
- Prompt text does not create a handoff. Configure and attach a documented `handoff` tool.
- Keep member order explicit: the first member starts the call.
- Prefer saved assistants, reusable tools, and a saved Squad for production. Use transient members or Squads only when the request is intentionally ephemeral or a prototype.

## Persistent Squad Procedure

1. Determine the execution mode.
   - Return JSON or a plan when the user asks for a draft or does not clearly authorize live writes.
   - Perform live creates or updates only with explicit intent and an available `VAPI_API_KEY`.

2. Define focused members.
   - State each member's responsibility, tools, and handoff boundaries.
   - Choose the entry member and place it first.
   - Reuse existing assistants by resolving names through `GET /assistant`; create missing assistants first with the `create-assistant` skill.

3. Create handoff relationships after destinations exist.
   - Resolve every destination assistant before building a persistent handoff tool.
   - Use `type: "assistant"` plus a verified `assistantId` for saved cross-assistant destinations.
   - Use clear descriptions that state when the model should hand off and what should be collected first.
   - Create reusable handoff tools through `POST /tool`, then attach them to the source assistants with the configuration-preserving procedure in the `create-tool` skill.
   - For OpenAI models, current public guidance recommends one handoff tool per destination. For Anthropic models, one tool with multiple destinations is supported and recommended.

4. Configure public context controls only when needed.
   - Use `contextEngineeringPlan` on a handoff destination: `all`, `lastNMessages`, `userAndAssistantMessages`, `previousAssistantMessages`, or `none` when supported by the current schema.
   - Use `variableExtractionPlan.schema` only for specific structured values needed downstream. Do not invent values or claim extraction occurred before a real handoff.
   - Keep sensitive tool results out of downstream context when the use case requires isolation.

5. Create and verify the Squad.
   - Build `members` from verified assistant IDs in explicit order.
   - Optionally set `assistantVersion` only to a version returned by the public assistant API when the user wants an immutable pin. Omit it to follow latest.
   - Before a production-affecting create or update, recap member order, handoffs, and target and obtain explicit confirmation unless the user's current instruction already unambiguously authorizes that exact mutation now.
   - Send `POST /squad` only after explicit live-create intent.
   - Validate the returned Squad ID, complete member order, entry member, pins, and handoff attachments before reporting success.

6. Handle failures honestly.
   - On a `400`, correct a documented field placement or limit before at most one justified retry.
   - On `401` or `403`, stop for authentication or permission issues. On `404`, report the missing assistant, tool, or Squad. On `5xx`, report the service failure.
   - If a sequence partially succeeds, list the IDs created so the user can review or clean them up. Do not continue creating dependent resources after a fatal error.

## Persistent Squad Payload

Use verified IDs only:

```json
{
  "name": "Support Squad",
  "members": [
    { "assistantId": "<verified-triage-assistant-id>" },
    { "assistantId": "<verified-billing-assistant-id>" },
    { "assistantId": "<verified-technical-assistant-id>" }
  ]
}
```

The first member is the entry assistant. Handoff tools belong on the relevant source assistants; Squad membership alone does not define every transition.

## Handoff Payload

```json
{
  "type": "handoff",
  "function": { "name": "handoff_to_billing" },
  "destinations": [
    {
      "type": "assistant",
      "assistantId": "<verified-billing-assistant-id>",
      "description": "The caller needs billing, invoice, or payment help.",
      "contextEngineeringPlan": {
        "type": "userAndAssistantMessages"
      },
      "variableExtractionPlan": {
        "schema": {
          "type": "object",
          "properties": {
            "accountNumber": { "type": "string" }
          }
        }
      }
    }
  ]
}
```

Placeholders are acceptable in templates, never in live requests. Read [Squad Configuration](references/squad-configuration.md) for transient Squads, context transfer, version pins, and safe Squad updates.

## Update Safely

`PATCH /squad/{id}` expects a complete `members` array. Always:

1. `GET /squad/{id}`.
2. Copy the complete ordered member objects and `membersOverrides`.
3. Apply only the requested change, preserving each member's `assistantId` or inline assistant, `assistantVersion`, `assistantOverrides`, and any documented destination fields already present.
4. Patch the complete merged configuration.
5. Re-fetch and verify order, entry member, pins, overrides, and handoffs.

## Public Sources

- [Introduction to Squads](https://docs.vapi.ai/squads)
- [Handoff tool](https://docs.vapi.ai/squads/handoff)
- [Passing data between assistants](https://docs.vapi.ai/squads/passing-data-between-assistants)
- [Squad API reference](https://docs.vapi.ai/api-reference/squads/get)

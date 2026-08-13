# Squad Configuration

Read the relevant section for transient designs, context transfer, version pins, or Squad updates.

## Contents

- [Transient Squads](#transient-squads)
- [Context and variable transfer](#context-and-variable-transfer)
- [Assistant-version pins](#assistant-version-pins)
- [Updating a Squad](#updating-a-squad)

## Transient Squads

Transient members and Squads are valid in a call or documented handoff destination. Use them for prototypes or call-specific behavior, not as the default production architecture.

```json
{
  "squad": {
    "members": [
      { "assistant": { "name": "Temporary Greeter" } },
      { "assistantId": "<verified-saved-assistant-id>" }
    ]
  }
}
```

Complete any required model, voice, and transcriber configuration before treating an inline assistant as call-ready.

## Context and Variable Transfer

Place `contextEngineeringPlan` and `variableExtractionPlan` on the handoff destination, not on the Squad member. Current public context types include:

- `all` — full history;
- `lastNMessages` with `maxMessages`;
- `userAndAssistantMessages` — omit system and tool messages;
- `previousAssistantMessages` — exclude the current assistant's session;
- `none` — blank downstream context.

Extraction performs a dedicated model step and stores the documented variables for later assistants. Define only variables the destination needs and use a small JSON Schema.

## Assistant-Version Pins

The current public Squad member schema supports `assistantVersion` with a saved `assistantId`:

```json
{
  "assistantId": "<verified-assistant-id>",
  "assistantVersion": "<version-returned-by-the-api>"
}
```

Never invent `vN`. Read the assistant and use a returned public version label. Omit `assistantVersion` to follow latest. Do not use a pin with an inline `assistant`.

## Updating a Squad

For a name-only or other non-member update, send a minimal partial PATCH and omit `members`. To reorder, add, remove, pin, unpin, override, or change a member destination:

1. Fetch the current Squad.
2. Deep-copy the complete ordered `members` array and current `membersOverrides` when it must also change.
3. Change only the intended member object.
4. Send the complete merged `members` array plus only the other changed top-level fields.
5. Fetch again and compare order and every untouched member.

Do not rebuild member objects from IDs alone; that can drop overrides, pins, inline configuration, or existing destination data.

## Public Sources

- [Handoff tool](https://docs.vapi.ai/squads/handoff)
- [Passing data between assistants](https://docs.vapi.ai/squads/passing-data-between-assistants)

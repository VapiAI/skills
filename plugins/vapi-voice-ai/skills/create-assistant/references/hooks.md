# Assistant Hooks

Read this file only when the user wants Vapi to run an action automatically in response to a supported call event.

## Choose the Right Mechanism

Use a hook when the event itself should deterministically trigger an action, such as speaking after customer silence or beginning call wrap-up after a time limit.

Do not use a hook when:

- The model should decide whether to act from the conversation. Attach an assistant tool instead.
- The user's backend only needs to receive call updates. Configure documented server events instead.
- Prompt instructions alone already express the behavior and no deterministic event trigger is required.

## Build and Verify

- Use the current Assistant Hooks guide to select the event and understand its behavior.
- Validate the final event, options, filters, and actions against the current `CreateAssistantDTO` schema before returning or creating a payload.
- If the guide and create schema disagree, do not guess or silently substitute another event. Use a guide-documented event missing from the schema only after disclosing the SDK/schema compatibility risk and validating both creation and behavior outside production; omit a schema-only event unless public behavioral documentation supports it.
- Do not reuse event names or shapes from memory. Do not invent destinations, server URLs, tool IDs, filters, or events.
- Keep secrets in Vapi credentials or the user's backend.

Choose actions deliberately:

- `say.exact`: speak fixed text. Prefer this when wording must be predictable.
- `say.prompt`: generate a spoken response from conversation context.
- `message.add`: add context or an instruction to the conversation; set its documented response behavior intentionally.
- `tool`: execute a verified saved tool by ID or a fully documented inline native tool.

Reuse a saved tool when it already exists and its real ID is available. Use an inline tool only when its complete current configuration and every required value are known.

## Customer Speech Timeout

This is a safe pattern for prompting a silent caller. Include an explicit timeout in creation-ready payloads rather than relying on a documented default that may differ from schema validation.

```json
{
  "hooks": [
    {
      "on": "customer.speech.timeout",
      "options": {
        "timeoutSeconds": 10,
        "triggerMaxCount": 3,
        "triggerResetMode": "onUserSpeech"
      },
      "do": [
        {
          "type": "say",
          "exact": "Are you still there?"
        }
      ]
    }
  ]
}
```

Verify the supported timeout range, trigger count, and reset modes against the current schema before changing these values.

## Tool Action

Call an already saved tool only with its real ID:

```json
{
  "type": "tool",
  "toolId": "<verified-tool-id>"
}
```

Use a native inline action only when its complete public shape is known:

```json
{
  "type": "tool",
  "tool": { "type": "endCall" }
}
```

The saved-tool example is a template, not creation-ready JSON. Do not put placeholders into a creation-ready payload.

## Public Sources

- [Assistant Hooks](https://docs.vapi.ai/assistants/assistant-hooks) — event behavior, actions, options, and examples
- [Create Assistant API](https://docs.vapi.ai/api-reference/assistants/create) — final payload schema
- [Server Events](https://docs.vapi.ai/server-url/events) — backend notifications that should not be modeled as hooks

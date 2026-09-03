# Assistant Tool Attachments

Use this procedure only when attaching or detaching a reusable tool through the public assistant API.

## Choose Inline or Reusable

- Put a one-off tool definition in `model.tools` when it belongs only to that assistant or transient configuration.
- Create a reusable tool with `POST /tool`, then attach its returned ID in `model.toolIds` when it should be managed independently or shared.
- Both arrays may coexist. Do not convert or discard existing inline tools during a reusable-tool attachment change.

Creating a tool does not attach it. Attaching a tool does not create its provider connection, destination, credential, or external backend.

## Attach Safely

1. Resolve exactly one assistant and exactly one reusable tool.
2. `GET /assistant/{assistantId}`.
3. Deep-copy the complete returned `model` configuration, excluding response-only fields if any are present.
4. Copy the existing `toolIds` array or start with an empty array.
5. Add the verified tool ID once; do not duplicate it.
6. Preserve `tools`, messages, provider, model name, temperature, token limits, reasoning settings, and every other unrelated model field.
7. `PATCH /assistant/{assistantId}` with the complete merged model.
8. Re-fetch the assistant. Verify the ID is present and all preserved fields remain unchanged.

Conceptual merged patch:

```json
{
  "model": {
    "provider": "<preserved-provider>",
    "model": "<preserved-model>",
    "messages": "<preserved-complete-message-array>",
    "tools": "<preserved-complete-inline-tool-array>",
    "toolIds": [
      "<preserved-existing-tool-id>",
      "<verified-new-tool-id>"
    ],
    "<other-model-fields>": "<preserved-values>"
  }
}
```

This is an explanatory template, not a live payload. Replace every placeholder from the fetched assistant before use.

## Detach Safely

Follow the same read–copy–merge–patch–verify sequence, but remove only the requested ID from `model.toolIds`. Do not delete the reusable tool resource unless the user separately asks for deletion and the impact on every assistant using it has been reviewed.

If the same capability is also defined inline in `model.tools`, report that separately. Removing a reusable ID does not remove an inline definition.

## Update the Prompt When Necessary

If the assistant's system prompt names tools or describes when to invoke them, update that complete system message alongside the attachment change. Do not append a fragment or claim the assistant has a capability that is not attached and operational.

## Failure Rules

- If the assistant cannot be fetched, do not construct a replacement model from memory.
- If the tool ID is missing, stop rather than attaching a guessed resource.
- If the patch fails, do not claim the tool is attached or detached.
- If re-fetch shows unrelated model changes, report the mismatch and do not conceal it with another blind patch.

## Public Sources

- [Create Assistant API](https://docs.vapi.ai/api-reference/assistants/create)
- [Update Assistant API](https://docs.vapi.ai/api-reference/assistants/update)

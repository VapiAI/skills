---
name: create-assistant
description: Create or validate Vapi voice-assistant payloads and, when explicitly requested, create assistants through the public Vapi API. Use for phone or web agents, short assistant intake, model/voice/transcriber selection, multilingual compatibility, native end-call or voicemail behavior, existing tool attachment, hooks, compliance settings, and assistant API validation errors.
license: MIT
compatibility: Internet access and VAPI_API_KEY are required only for live Vapi API operations.
metadata:
  author: vapi
  version: "3.0"
---

# Vapi Assistant Creation

Produce the smallest useful assistant. Default to a payload or implementation when live creation is not explicit. Mutate Vapi only when the user clearly asks for a live create and `VAPI_API_KEY` is available.

## Safety and Source Rules

- Use the current [Create Assistant API reference](https://docs.vapi.ai/api-reference/assistants/create), public OpenAPI schema, or public server SDK for payload shape and unstable selectable values.
- Never print, request in chat, or embed API keys, provider secrets, credentials, private URLs, or real customer data.
- Never invent IDs, destinations, integrations, server URLs, model names, voices, transcribers, or presets.
- Keep the assistant name at 40 characters or fewer.
- Do not enable paid, HIPAA, PCI, recording, retention, or other compliance behavior unless the user requests it and the current public docs support the exact configuration.
- Treat prompt text as behavior guidance, not a capability. Scheduling, transfer, messaging, and other actions require configured tools and dependencies.

## Procedure

1. Determine the execution mode.
   - Return JSON or code only when the user asks for a payload, draft, implementation, or does not clearly authorize a live mutation.
   - Use `POST https://api.vapi.ai/assistant` only when the user explicitly asks to create the assistant in Vapi and `VAPI_API_KEY` is set.
   - If live creation is requested but the key is unavailable, return a ready payload and the command the user can run locally. Do not ask them to paste the key into chat.

2. Run a short, high-signal intake.
   - Infer a concise name, use case, first message, and spoken style from the request.
   - Preserve every language requirement exactly.
   - Ask only for a missing choice that blocks a valid result, such as an unknown language or an exact transfer destination. Do not turn intake into a questionnaire.
   - Defer integrations, knowledge sources, escalation destinations, and provider preferences unless the user made them part of the goal.

3. Build the smallest useful payload.
   - Include `name`, `firstMessage`, `model`, `voice`, and `transcriber` for a ready voice assistant.
   - Put behavioral instructions in a system entry under `model.messages`.
   - Keep spoken responses concise and give the assistant an honest fallback when a capability is not configured.
   - Add the native inline end-call tool, `{ "type": "endCall" }`, under `model.tools` as the default baseline. Do not substitute `endCallPhrases` or prompt-only instructions for the tool.

4. Select compatible providers.
   - Read [Provider Policy](references/providers.md) before choosing defaults, honoring a user-requested provider, or configuring more than one language.
   - Verify user-requested model, voice, transcriber, language, or preset values against current public sources before using them.
   - Ensure the voice can speak every requested language and the transcriber can recognize them. Do not use a voice-language value such as `multi` unless the current voice schema explicitly permits it.

5. Add only real capabilities.
   - Reuse exact saved tool IDs in `model.toolIds`, or define documented inline native tools in `model.tools`.
   - Use the `create-tool` skill for reusable tools or external-server behavior. Creating a function definition does not implement the server it calls.
   - If the user requests voicemail handling, add the native `voicemail` tool and tell the system prompt when to invoke it. Configure documented voicemail-tool messages when needed; do not replace the tool with prompt text or an unrelated voicemail-detection field.
   - Read [Assistant Hooks](references/hooks.md) only when the user wants Vapi to run an action automatically in response to a supported call event. Use an assistant tool when the model should decide whether to act from the conversation, and use server events when the user's backend only needs call updates.
   - Never claim scheduling, transfer, messaging, or another action is configured unless every required resource was created or resolved, attached, and verified successfully.

6. Validate, optionally create, and verify.
   - Check the payload for placeholders, unsupported values, leaked secrets, incompatible language settings, and missing dependencies.
   - Before a production-affecting create, recap the resource and obtain explicit confirmation unless the user's current instruction already unambiguously says to create it now.
   - For a live create, send one `POST /assistant`, require a success response, and verify the returned `id` plus the requested configuration.
   - On a `400`, correct a documented validation error and retry at most once when the fix is clear. Never repeat an unchanged request.
   - On `401` or `403`, stop and report an authentication or permission problem. On `404`, report the missing referenced resource. On `5xx`, report the service failure and do not claim creation succeeded.
   - Report only capabilities confirmed by successful API responses. Name any requested but unconfigured dependencies separately.

## Baseline Payload

Use this when the user does not request different providers. Revalidate defaults against public sources when the request depends on “latest” behavior.

```json
{
  "name": "Support Assistant",
  "firstMessage": "Hello! How can I help you today?",
  "model": {
    "provider": "openai",
    "model": "gpt-4.1",
    "messages": [
      {
        "role": "system",
        "content": "You are a friendly phone support assistant. Give concise spoken answers. When the conversation is complete, say goodbye and use the end-call tool."
      }
    ],
    "tools": [
      { "type": "endCall" }
    ]
  },
  "voice": {
    "provider": "vapi",
    "voiceId": "Elliot",
    "version": 2
  },
  "transcriber": {
    "provider": "deepgram",
    "model": "flux-general-en",
    "language": "en"
  }
}
```

## Live Create

Use this only after explicit live-create intent:

```bash
curl --fail-with-body -X POST https://api.vapi.ai/assistant \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @assistant-payload.json
```

After success, return the assistant ID and a concise summary of verified configuration. A locally generated payload is not a created assistant.

## Public Sources

- [Create Assistant API](https://docs.vapi.ai/api-reference/assistants/create) — current schema and limits
- [Vapi Voices](https://docs.vapi.ai/providers/voice/vapi-voices) — active voices and multilingual behavior
- [Transcriber fallback configuration](https://docs.vapi.ai/customization/transcriber-fallback-plan) — current Deepgram model guidance
- [Default tools](https://docs.vapi.ai/tools/default-tools) and [Voicemail tool](https://docs.vapi.ai/tools/voicemail-tool) — native tool behavior

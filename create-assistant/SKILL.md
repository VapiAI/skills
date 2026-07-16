---
name: create-assistant
description: Create Vapi voice AI assistant payloads or assistants through the Vapi API. Use when building phone or web call agents, generating assistant JSON, choosing safe default model/voice/transcriber settings, attaching existing Vapi tool IDs, adding assistant hooks, configuring HIPAA/compliance only when explicitly requested, or fixing Vapi assistant API validation errors.
license: MIT
compatibility: Requires internet access and a Vapi API key (VAPI_API_KEY).
metadata:
  author: vapi
  version: "2.0"
---

# Vapi Assistant Creation

Create a valid Vapi assistant payload first. Call the Vapi API only when the user clearly asks to create the assistant in Vapi and `VAPI_API_KEY` is available.

## Reliability Rules

- Do not invent model names, voice IDs, tool IDs, credential IDs, assistant IDs, phone numbers, or server URLs.
- Use the known-good defaults below when the user does not specify provider choices.
- Verify any user-requested specific or latest model, voice, transcriber, hook, or provider shape in official Vapi docs, Vapi API responses, or the user's Vapi dashboard/API value before using it.
- Treat Vapi API validation errors as the source of truth. Correct the payload and retry rather than guessing.
- Do not enable HIPAA or other paid/compliance behavior unless the user explicitly asks for HIPAA, compliance mode, no recording, or no transcript storage.

## Creation Workflow

1. Determine the output mode.
   - If the user asks for a payload, JSON, config, draft, or says not to call the API, return assistant JSON only.
   - If the user asks to create in Vapi, add it to their Vapi account, make it live, or call the API, use `POST https://api.vapi.ai/assistant` with `VAPI_API_KEY`.
   - If the user only says to create, build, or make an assistant and does not specify payload-only or live creation, ask: "Do you want the assistant JSON only, or should I create it in your Vapi account if `VAPI_API_KEY` is available?"
   - Completion: the mode is clear before any live API request is sent.

2. Build the smallest valid assistant.
   - Include `name`, `firstMessage`, `model`, `voice`, and `transcriber`.
   - Keep `name` at 40 characters or fewer, as enforced by the Vapi API.
   - Put behavior in `model.messages[0].content`.
   - Keep voice-agent prompts concise and spoken-response oriented.
   - Completion: the payload can stand alone with a name of 40 characters or fewer and without placeholder IDs, URLs, phone numbers, or provider names.

3. Apply safe defaults.
   - Model: `{ "provider": "openai", "model": "gpt-4.1" }`
   - Voice: `{ "provider": "vapi", "voiceId": "Elliot", "version": 2 }`
   - English transcriber: `{ "provider": "deepgram", "model": "flux-general-en", "language": "en" }`
   - Multilingual transcriber: `{ "provider": "deepgram", "model": "nova-3", "language": "multi" }`
   - Completion: defaults are used only where the user did not request a different provider.

4. Add optional features only with enough exact information.
   - Tools: include saved `model.toolIds` only when the user provides real Vapi tool IDs. Inline tools require a real server URL or an explicit draft-only request.
   - Hooks: read [hooks reference](references/hooks.md) before adding hooks. Transfer, function, and notification hooks require exact destination numbers, server URLs, or tool definitions from the user.
   - Non-default providers: read [provider policy](references/providers.md) before using non-default model, voice, or transcriber shapes.
   - Compliance: add `compliancePlan.hipaaEnabled` only when explicitly requested, and verify provider constraints.
   - Completion: every optional field is backed by a user request or verified source.

5. Validate before finalizing.
   - Prefer Vapi's current OpenAPI schema and the API response as the final authority.
   - Review the payload for placeholders, invented IDs, accidental paid compliance defaults, and Vapi voice configs missing `version: 2`.
   - If creating the assistant, use the Vapi API response to resolve validation errors. Correct clear errors and retry only when the fix is supported by docs, API output, or exact user-provided values.
   - Completion: the final payload has no placeholders, no accidental paid compliance defaults, Vapi voices use `version: 2`, and any API validation errors have been resolved.

## Minimal Default Payload

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
        "content": "You are a friendly phone support assistant. Keep responses concise and under 30 words."
      }
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

## Create Through API

Use this only when the user clearly asked to create the assistant in Vapi and `VAPI_API_KEY` is set:

```bash
curl -X POST https://api.vapi.ai/assistant \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d @assistant-payload.json
```

After creation, return the assistant ID and any Vapi warnings or validation notes. If creation fails, summarize the API error, fix the payload when possible, and retry only when the fix is clear.

## Source Hierarchy

- Payload shape: Vapi OpenAPI `CreateAssistantDTO` and Create Assistant API docs.
- Current selectable values: Vapi dashboard/API responses and official Vapi provider docs.
- Provider-specific IDs: exact values selected or supplied by the user.
- Runtime correctness: Vapi API validation response.

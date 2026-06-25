# Provider Policy

Use this reference when the user asks for a non-default model, voice, or transcriber.

## Source of Truth

1. Use the Vapi OpenAPI schema for payload structure.
2. Use the Vapi dashboard, API responses, and official Vapi provider docs for current selectable provider values.
3. Use exact user-provided provider IDs for private, synced, custom, or third-party resources.
4. Use Vapi API validation errors as the final check.

Do not maintain exhaustive provider/model/voice tables in this skill. Provider availability changes too often, and stale tables cause failed assistant creation.

## Defaults

Use these defaults when the user does not specify alternatives:

```json
{
  "model": { "provider": "openai", "model": "gpt-4.1" },
  "voice": { "provider": "vapi", "voiceId": "Elliot", "version": 2 },
  "transcriber": { "provider": "deepgram", "model": "flux-general-en", "language": "en" }
}
```

For multilingual assistants, use:

```json
{
  "transcriber": { "provider": "deepgram", "model": "nova-3", "language": "multi" }
}
```

## Model Selection

- Use the default OpenAI model unless the user asks for a different provider or model.
- For specific or latest model requests, verify the exact model ID in official Vapi docs, Vapi dashboard/API output, or the user's selected Vapi value.
- For OpenRouter, custom LLMs, Azure deployments, or providers that accept account-specific model names, require the exact model ID or deployment value from the user.
- Exclude models marked deprecated by Vapi or by the upstream provider, even if they still appear in older examples.
- If the user asks what is available and current values are not exposed in public docs, say that the selectable list must be checked in the Vapi dashboard instead of guessing.

## Voice Selection

- Use Vapi `Elliot` with `version: 2` by default.
- For other Vapi voices, use only active Vapi voice names documented by Vapi or selected by the user.
- For ElevenLabs and other third-party voices, use the exact Vapi dropdown/API value selected by the user. Do not infer provider-native IDs from display names.
- For Deepgram voices, use the named Vapi/Deepgram voice ID from the dropdown, such as `asteria`, and put `aura` or `aura-2` in `voice.model` when that model is selected.
- For custom voices, require the exact server URL or saved configuration value. Do not draft creation-ready custom voice payloads from placeholders.

## Transcriber Selection

- Use Deepgram `flux-general-en` with `language: "en"` for English-only assistants.
- Use Deepgram `nova-3` with `language: "multi"` for multilingual assistants.
- For non-default transcribers, require a documented Vapi shape or exact user-selected dashboard/API value.
- Do not assume every transcriber supports every language, keyword, formatting, or endpointing option.

## Credentials

When a provider requires customer credentials, tell the user to configure provider credentials in the Vapi Dashboard under Integrations. Do not invent credential IDs or provider account values.

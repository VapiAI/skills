# Provider Policy

Read this file when selecting defaults, honoring a specific provider request, or configuring multiple languages.

## Source Order

1. Use the current public Vapi OpenAPI schema or API reference for payload structure and accepted values.
2. Use current Vapi provider documentation for compatibility and recommended settings.
3. Use exact user-supplied IDs only for private, synced, cloned, or account-specific resources.
4. Treat the Vapi API validation response as the final runtime check.

Do not maintain exhaustive provider tables. Verify unstable model, voice, transcriber, and language values at execution time.

## Default Selection Strategy

When the user has no provider preference and the use case has no special language, latency, compliance, region, or credential constraint:

1. When an API payload needs an explicit model to carry `model.messages`, verify and use a currently supported model from the Create Assistant schema and provider documentation.
2. Omit voice or transcriber only when the Create Assistant API documents the field as optional and defines the resulting behavior; otherwise provide verified explicit configuration.

Pinning every component is not inherently more production-ready. It trades automatic platform improvements for reproducibility and must be an intentional choice.

For a multilingual assistant, first verify that every requested language is supported by the model, voice, and transcriber. The current public Vapi guidance supports Vapi Version 2 voices with automatic language detection and Deepgram Flux Multilingual:

```json
{
  "voice": {
    "provider": "vapi",
    "voiceId": "Elliot",
    "version": 2,
    "language": "auto"
  },
  "transcriber": {
    "provider": "deepgram",
    "model": "flux-general-multi"
  }
}
```

Omit the transcriber `language` field to enable automatic language detection. If the assistant must recognize one known language, set `language` to one of the documented codes supported by `flux-general-multi`; do not use `multi`. List the supported conversation languages in the system prompt, and do not claim universal language support.

## Selection Rules

- Verify a user-requested exact or “latest” model before using it. If unsupported, ask for one alternative decision instead of silently substituting.
- Use only active Vapi voice names. `Elliot` Version 2 is a documented baseline; several older example voices were retired in 2026.
- For cloned, custom, or third-party voices, require the exact saved ID or publicly documented value. Do not derive IDs from display names.
- Never assume a transcriber supports every language or every provider-specific option.
- Keep provider credentials in Vapi credentials or the user's secure environment. Never place real secrets in examples or chat.

## Public Sources

- [Vapi Voices](https://docs.vapi.ai/providers/voice/vapi-voices)
- [Legacy voice migration](https://docs.vapi.ai/providers/voice/vapi-voices/legacy-migration)
- [Transcriber fallback configuration](https://docs.vapi.ai/customization/transcriber-fallback-plan)
- [Create Assistant API](https://docs.vapi.ai/api-reference/assistants/create)

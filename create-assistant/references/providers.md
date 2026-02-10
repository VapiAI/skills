# Voice, Model, and Transcriber Providers

Complete reference for all providers supported in Vapi assistant configuration.

## Model Providers

### OpenAI
```json
{ "provider": "openai", "model": "gpt-4.1" }
```
Models: `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`, `gpt-3.5-turbo`

### Anthropic
```json
{ "provider": "anthropic", "model": "claude-3-5-sonnet-20241022" }
```
Models: `claude-3-5-sonnet-20241022`, `claude-3-5-haiku-20241022`, `claude-3-opus-20240229`

### Google Gemini
```json
{ "provider": "google", "model": "gemini-1.5-pro" }
```
Models: `gemini-1.5-pro`, `gemini-1.5-flash`

### Groq
```json
{ "provider": "groq", "model": "llama-3.1-70b-versatile" }
```
Models: `llama-3.1-70b-versatile`, `llama-3.1-8b-instant`, `mixtral-8x7b-32768`

### DeepInfra
```json
{ "provider": "deepinfra", "model": "meta-llama/Meta-Llama-3.1-70B-Instruct" }
```

### OpenRouter
```json
{ "provider": "openrouter", "model": "anthropic/claude-3.5-sonnet" }
```
Access 100+ models via OpenRouter.

### Perplexity
```json
{ "provider": "perplexity", "model": "llama-3.1-sonar-large-128k-online" }
```
Web-connected models for real-time information.

### Together AI
```json
{ "provider": "together-ai", "model": "meta-llama/Llama-3-70b-chat-hf" }
```

### Azure OpenAI
```json
{ "provider": "azure-openai", "model": "your-deployment-name" }
```
Requires Azure credential setup.

### Custom LLM
```json
{
  "provider": "custom-llm",
  "model": "your-model-name",
  "url": "https://your-llm-server.com/v1/chat/completions"
}
```
Any OpenAI-compatible endpoint.

## Voice Providers

### Vapi Voices (Recommended — lowest latency)
```json
{ "provider": "vapi", "voiceId": "Elliot" }
```
Voices: `Elliot`, `Lily`, `Rohan`, `Paola`, `Kian`, and more.

### ElevenLabs
```json
{ "provider": "11labs", "voiceId": "JBFqnCBsd6RMkjVDRZzb" }
```
Requires ElevenLabs API key as credential.

### PlayHT
```json
{ "provider": "playht", "voiceId": "voice-id-from-playht" }
```

### Cartesia
```json
{ "provider": "cartesia", "voiceId": "voice-id-from-cartesia" }
```

### OpenAI
```json
{ "provider": "openai", "voiceId": "alloy" }
```
Voices: `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`

### Azure
```json
{ "provider": "azure", "voiceId": "en-US-JennyNeural" }
```

### Deepgram
```json
{ "provider": "deepgram", "voiceId": "aura-asteria-en" }
```

### Rime AI
```json
{ "provider": "rime-ai", "voiceId": "voice-id-from-rime" }
```

## Transcriber Providers

### Deepgram (Recommended)
```json
{ "provider": "deepgram", "model": "nova-3", "language": "en" }
```
Models: `nova-3` (best), `nova-2`, `base`, `enhanced`

### Google
```json
{ "provider": "google", "model": "latest_long", "language": "en" }
```

### Gladia
```json
{ "provider": "gladia", "model": "fast", "language": "en" }
```
Models: `fast`, `accurate`

### Assembly AI
```json
{ "provider": "assembly-ai", "model": "best", "language": "en" }
```
Models: `best`, `nano`

### Speechmatics
```json
{ "provider": "speechmatics", "language": "en" }
```

### Talkscriber
```json
{ "provider": "talkscriber", "language": "en" }
```

## Multilingual Support

For multilingual assistants, set the transcriber language to `"multi"`:

```json
{
  "transcriber": { "provider": "deepgram", "model": "nova-3", "language": "multi" }
}
```

## Adding Provider Credentials

If using your own API keys (e.g., your own OpenAI or ElevenLabs key), add them in the Vapi Dashboard under **Integrations**: https://dashboard.vapi.ai

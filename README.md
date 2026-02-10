# Vapi Skills

Agent skills for [Vapi](https://vapi.ai) — the developer platform for building voice AI agents. These skills follow the [Agent Skills specification](https://agentskills.io/specification) and can be used with any compatible AI coding assistant including Claude Code, Cursor, VS Code Copilot, Gemini CLI, and more.

## Installation

### Option 1: npx skills (works with all agents)

```bash
npx skills add VapiAI/skills
```

Install specific skills:

```bash
npx skills add VapiAI/skills --skill create-assistant
npx skills add VapiAI/skills --skill create-tool
```

Install for a specific agent:

```bash
npx skills add VapiAI/skills -a claude-code
npx skills add VapiAI/skills -a cursor
```

### Option 2: Claude Code Plugin (native integration)

```
/plugin marketplace add VapiAI/skills
/plugin install vapi-voice-ai@vapi-skills
```

### Option 3: Manual installation

Copy any skill directory into your project's `.claude/skills/` (for Claude Code), `.cursor/skills/` (for Cursor), or the equivalent skills directory for your agent.

## Available Skills

| Skill | Description |
|-------|-------------|
| [setup-api-key](./setup-api-key) | Guide through obtaining and configuring a Vapi API key |
| [create-assistant](./create-assistant) | Create voice AI assistants with models, voices, transcribers, tools, and hooks |
| [create-tool](./create-tool) | Build custom tools for assistants — function calls, transfers, integrations |
| [create-call](./create-call) | Initiate outbound phone calls, web calls, and batch calls |
| [create-squad](./create-squad) | Build multi-assistant squads with handoff workflows |
| [create-phone-number](./create-phone-number) | Set up phone numbers from Twilio, Vonage, Telnyx, or Vapi |
| [setup-webhook](./setup-webhook) | Configure server URLs to receive real-time call events |
| [create-workflow](./create-workflow) | Build visual conversation workflows with branching logic |

## Configuration

All skills require a Vapi API key. Set it as an environment variable:

```bash
export VAPI_API_KEY="your-api-key"
```

Get your API key from the [Vapi Dashboard](https://dashboard.vapi.ai/org/api-keys) or use the `setup-api-key` skill.

## SDK Support

Skills include examples for:

- **cURL** — Direct REST API calls
- **TypeScript** — `npm install @vapi-ai/server-sdk`
- **Python** — `pip install requests` (direct API) or Vapi's Python SDK
- **Web SDK** — `npm install @vapi-ai/web` (client-side, uses public API key)

## Quick Start

1. **Get an API key**: Use the `setup-api-key` skill or visit https://dashboard.vapi.ai/org/api-keys
2. **Create an assistant**: Use the `create-assistant` skill to build a voice AI agent
3. **Add a phone number**: Use `create-phone-number` to get a phone number
4. **Make a call**: Use `create-call` to test your assistant

## API Reference

- **Base URL**: `https://api.vapi.ai`
- **Authentication**: Bearer token via `Authorization: Bearer $VAPI_API_KEY`
- **Full API Docs**: https://docs.vapi.ai
- **API Swagger**: https://api.vapi.ai/api

## License

MIT

---
name: setup-webhook
description: Configure Vapi server URLs and webhooks to receive real-time call events, transcripts, tool calls, and end-of-call reports. Use when setting up webhook endpoints, building tool servers, or integrating Vapi events into your application.
license: MIT
compatibility: Requires internet access and a Vapi API key (VAPI_API_KEY).
metadata:
  author: vapi
  version: "1.0"
---

# Vapi Webhook / Server URL Setup

Configure server URLs to receive real-time events from Vapi during calls — transcripts, tool calls, status changes, and end-of-call reports.

> **Setup:** Ensure `VAPI_API_KEY` is set. See the `setup-api-key` skill if needed.

## Overview

Vapi uses "Server URLs" (webhooks) to communicate with your application. Unlike traditional one-way webhooks, Vapi server URLs support bidirectional communication — your server can respond with data that affects the call.

## Where to Set Server URLs

### On an Assistant

```bash
curl -X PATCH https://api.vapi.ai/assistant/{id} \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "server": {
      "url": "https://your-server.com/vapi/webhook",
      "credentialId": "cred_abc123"
    }
  }'
```

Create the optional `credentialId` in **Dashboard > Custom Credentials**. Omit it only for a deliberately public endpoint.

### On a Phone Number

Phone-number updates also use a `server` object with `url` and optional `credentialId`. When updating through the API, first retrieve the number and preserve its existing `provider` discriminator in the PATCH body. The dashboard is the safest choice when the provider is unknown.

### At the Organization Level

Set a default server URL in the Vapi Dashboard under **Settings > Server URL**.

Priority order: Tool server URL > Assistant server URL > Phone Number server URL > Organization server URL.

## Event Types

| Event | Description | Expects Response? |
|-------|-------------|-------------------|
| `assistant-request` | Request for dynamic assistant config | Yes — return assistant config |
| `tool-calls` | Assistant is calling a tool | Yes — return tool results |
| `status-update` | Call status changed | No |
| `transcript` | Real-time transcript update | No |
| `end-of-call-report` | Call completed with summary | No |
| `hang` | Assistant failed to respond | No |
| `speech-update` | Speech activity detected | No |

## Webhook Server Example (Express.js)

```typescript
import express from "express";
const app = express();
app.use(express.json());

app.post("/vapi/webhook", (req, res) => {
  const { message } = req.body;

  switch (message.type) {
    case "assistant-request":
      // Dynamically configure the assistant based on the caller
      res.json({
        assistant: {
          name: "Dynamic Assistant",
          firstMessage: `Hello ${message.call.customer?.name || "there"}!`,
          model: {
            provider: "openai",
            model: "gpt-4.1",
            messages: [
              { role: "system", content: "You are a helpful assistant." },
            ],
          },
          voice: { provider: "vapi", voiceId: "Elliot", version: 2 },
          transcriber: { provider: "deepgram", model: "nova-3", language: "en" },
        },
      });
      break;

    case "tool-calls":
      // Handle tool calls from the assistant
      const results = (message.toolCallList || []).map((toolCall: any) => ({
        toolCallId: toolCall.id,
        result: handleToolCall(
          toolCall.name,
          toolCall.parameters || toolCall.arguments
        ),
      }));
      res.json({ results });
      break;

    case "end-of-call-report":
      // Process the call report
      console.log("Call ended:", {
        callId: message.call.id,
        endedReason: message.endedReason,
        cost: message.cost,
        analysis: message.analysis,
        artifact: message.artifact,
      });
      res.json({});
      break;

    case "status-update":
      console.log("Call status:", message.status);
      res.json({});
      break;

    case "transcript":
      console.log(`[${message.role}]: ${message.transcript}`);
      res.json({});
      break;

    default:
      res.json({});
  }
});

function handleToolCall(name: string, args: any): string {
  // Implement your tool logic here
  return `Result for ${name}`;
}

app.listen(3000, () => console.log("Webhook server running on port 3000"));
```

## Webhook Server Example (Python / Flask)

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/vapi/webhook", methods=["POST"])
def vapi_webhook():
    data = request.json
    message = data.get("message", {})
    msg_type = message.get("type")

    if msg_type == "assistant-request":
        return jsonify({
            "assistant": {
                "name": "Dynamic Assistant",
                "firstMessage": "Hello! How can I help?",
                "model": {
                    "provider": "openai",
                    "model": "gpt-4.1",
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant."}
                    ],
                },
                "voice": {"provider": "vapi", "voiceId": "Elliot", "version": 2},
                "transcriber": {"provider": "deepgram", "model": "nova-3", "language": "en"},
            }
        })

    elif msg_type == "tool-calls":
        results = []
        for tool_call in message.get("toolCallList", []):
            results.append({
                "toolCallId": tool_call["id"],
                "result": f"Handled {tool_call['name']}",
            })
        return jsonify({"results": results})

    elif msg_type == "end-of-call-report":
        print(f"Call ended: {message['call']['id']}")
        print(f"Summary: {message.get('analysis', {}).get('summary')}")

    return jsonify({})

if __name__ == "__main__":
    app.run(port=3000)
```

## Webhook Authentication

Use a Vapi Custom Credential and place its ID in `server.credentialId`. Vapi supports Bearer Token, OAuth 2.0 client credentials, and HMAC credentials. Verify requests according to the credential you configured; HMAC header names, algorithms, timestamps, and payload formats are configurable, so do not assume a fixed `x-vapi-signature` format.

For a bearer credential, compare the incoming `Authorization: Bearer <token>` value with the token stored securely by your server. Never put the secret itself in an assistant or phone-number payload.

## Local Development

Use the Vapi CLI with a public tunnel. The CLI forwards from port 4242 to your app, but it does not create the public URL itself:

```bash
# Install the CLI
curl -sSL https://vapi.ai/install.sh | bash

# Terminal 1: expose the CLI listener
ngrok http 4242

# Terminal 2: forward events from the CLI to your app
vapi listen --forward-to localhost:3000/vapi/webhook
```

Set the Vapi server URL to the public ngrok URL. To skip the CLI and tunnel directly to the Express or Flask server instead:

```bash
ngrok http 3000
# Copy the ngrok URL and set it as your server URL
```

## End-of-Call Report Fields

The `end-of-call-report` event includes:

| Field | Description |
|-------|-------------|
| `call` | Full call object with metadata |
| `endedReason` | Why the call ended |
| `artifact` | Recording, transcript, messages, and other enabled artifacts |
| `analysis` | Configured summaries, structured data, and success evaluation |
| `cost` | Total call cost |
| `startedAt` / `endedAt` | Call timing, when included |

## References

- [Common Server URL Events](references/webhook-events.md) — Common event payloads and responses
- [Setting Server URLs](https://docs.vapi.ai/server-url/setting-server-urls) — Placement and priority
- [Server Authentication](https://docs.vapi.ai/server-url/server-authentication) — Custom Credentials
- [Local Development](https://docs.vapi.ai/server-url/developing-locally) — Testing webhooks locally

## Additional Resources

Vapi provides a **documentation MCP server** that gives compatible AI agents access to the Vapi knowledge base. Use its documentation search for advanced configuration, troubleshooting, SDK details, and anything beyond this skill.

To add the Vapi documentation MCP server manually in Claude Code, run:
```bash
claude mcp add vapi-docs -- npx -y mcp-remote https://docs.vapi.ai/_mcp/server
```

See the [Vapi MCP integration guide](https://docs.vapi.ai/cli/mcp) for setup instructions across supported agents.

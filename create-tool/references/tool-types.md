# Tool Type Selection

Read only the section for the capability being built. Revalidate every example against the current public Create Tool schema before a live request.

## Contents

- [Native Vapi tools](#native-vapi-tools)
- [Provider integration tools](#provider-integration-tools)
- [API Request tools](#api-request-tools)
- [Custom function tools](#custom-function-tools)
- [MCP tools](#mcp-tools)

## Native Vapi Tools

Choose the exact native type for behavior Vapi already implements:

- `endCall` to let the assistant end the call;
- `transferCall` to transfer to documented phone-number or SIP destinations;
- `handoff` to move between assistants in a Squad;
- `dtmf` to send keypad tones;
- `sms` to send a text message through supported call infrastructure;
- `sipRequest` to send a documented SIP request;
- `voicemail` for assistant-controlled voicemail handling.

Resolve required destinations before creating the tool. Do not replace native behavior with a function endpoint or prompt-only instructions.

Minimal shape:

```json
{
  "type": "endCall",
  "function": { "name": "end_completed_call" }
}
```

Some native types have destinations, messages, or other required fields. Use the type-specific public guide and schema rather than extrapolating from this minimal example.

## Provider Integration Tools

Use the exact documented integration type when the user's requested provider and action are publicly supported. Current public Create Tool schemas include integrations such as Google Calendar availability and event creation, Google Sheets row append, Slack message send, and GoHighLevel actions.

Before building the tool:

1. Confirm the provider connection exists through a secure supported flow.
2. Resolve the exact calendar, spreadsheet and range, Slack channel, or other target.
3. Verify the current type-specific fields.
4. Keep OAuth tokens and provider secrets out of the payload and chat.

Do not substitute a generic function tool for a supported integration. Do not claim the integration is usable until the provider connection, tool creation, and assistant attachment are each verified.

## API Request Tools

Use `apiRequest` when Vapi can call a known HTTP API declaratively. Require the real endpoint and enough API contract information to define its method, input schema, authentication, and expected response.

```json
{
  "type": "apiRequest",
  "name": "check_order_status",
  "description": "Fetch an order's current status after the caller provides its number.",
  "method": "GET",
  "url": "https://api.example.com/orders/{{orderNumber}}",
  "body": {
    "type": "object",
    "properties": {
      "orderNumber": {
        "type": "string",
        "description": "The order number stated by the caller."
      }
    },
    "required": ["orderNumber"]
  },
  "credentialId": "<verified-credential-id>"
}
```

Use a verified Vapi credential where supported. Never put a literal authorization token in an example or model-visible field. Configure retries only for operations that are safe to retry; do not automatically retry a non-idempotent mutation.

## Custom Function Tools

Use `function` only for custom behavior implemented by the user's backend using Vapi's tool-call callback contract. A function tool is appropriate when the backend needs custom orchestration, authorization, business logic, or a response shape that is not well represented by a declarative API Request tool.

```json
{
  "type": "function",
  "function": {
    "name": "calculate_shipping_quote",
    "description": "Calculate a shipping quote after collecting package weight and destination postal code.",
    "parameters": {
      "type": "object",
      "properties": {
        "weightKg": { "type": "number" },
        "postalCode": { "type": "string" }
      },
      "required": ["weightKg", "postalCode"]
    }
  },
  "server": {
    "url": "<user-supplied-https-url>",
    "credentialId": "<verified-credential-id>"
  }
}
```

The Vapi tool and the server implementation are separate deliverables. If the endpoint does not exist, return the tool contract and identify the backend as incomplete; do not invent a URL or claim the tool is operational.

Read [Function Tool Server](function-tool-server.md) only when the user asks to implement this backend.

## MCP Tools

Use `mcp` when the user already has an MCP-compatible server whose dynamically discovered tools should be available to the assistant.

```json
{
  "type": "mcp",
  "function": { "name": "connected_mcp_tools" },
  "server": {
    "url": "<secret-mcp-server-url>"
  }
}
```

Use the default Streamable HTTP transport. Treat token-bearing MCP URLs and headers as credentials: source them from secure local configuration and never print or persist them in example payloads. Verify that the server returns a focused tool set and bounded results so it does not overwhelm the model context.

## Public Sources

- [Create Tool API](https://docs.vapi.ai/api-reference/tools/create)
- [Default tools](https://docs.vapi.ai/tools/default-tools)
- [Custom tools](https://docs.vapi.ai/tools/custom-tools)
- [Google Calendar](https://docs.vapi.ai/tools/google-calendar), [Google Sheets](https://docs.vapi.ai/tools/google-sheets), and [Slack](https://docs.vapi.ai/tools/slack)
- [MCP integration](https://docs.vapi.ai/tools/mcp)

# Assistant API Examples

Use these patterns only after assembling and validating the complete assistant configuration. Recheck the current Create Assistant schema and SDK docs before generating final code. Templates may contain placeholders; live requests may not.

## Conceptual JSON

```json
{
  "name": "Customer Support",
  "firstMessage": "Thanks for calling. How can I help today?",
  "model": {
    "provider": "<verified-provider>",
    "model": "<verified-model>",
    "messages": [
      {
        "role": "system",
        "content": "<complete-validated-system-prompt>"
      }
    ],
    "tools": [{ "type": "endCall" }]
  }
}
```

## TypeScript Server SDK

Install `@vapi-ai/server-sdk`, preserve camelCase API fields, and pass the complete payload to `assistants.create`:

```typescript
import { VapiClient } from "@vapi-ai/server-sdk";

const vapi = new VapiClient({ token: process.env.VAPI_API_KEY! });
const assistant = await vapi.assistants.create({
  name: "Customer Support",
  firstMessage: "Thanks for calling. How can I help today?",
  model: {
    provider: "openai",
    model: "gpt-4o",
    messages: [
      { role: "system", content: "You are a concise customer support assistant." },
    ],
    tools: [{ type: "endCall" }],
  },
});
```

## Python Server SDK

Install `vapi_server_sdk`. Use snake_case keyword arguments at the Python SDK boundary:

```python
import os
from vapi import Vapi

client = Vapi(token=os.environ["VAPI_API_KEY"])
assistant = client.assistants.create(
    name="Customer Support",
    first_message="Thanks for calling. How can I help today?",
    model={
        "provider": "openai",
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are a concise customer support assistant."}
        ],
        "tools": [{"type": "endCall"}],
    },
)
```

## cURL

Write the validated conceptual payload to `assistant-payload.json`, then send it through the public REST API:

```bash
curl --fail-with-body -X POST https://api.vapi.ai/assistant \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @assistant-payload.json
```

## Public Sources

- [Create Assistant API](https://docs.vapi.ai/api-reference/assistants/create)
- [Documentation agent example](https://docs.vapi.ai/assistants/examples/docs-agent)
- [Server SDK quickstart](https://docs.vapi.ai/quickstart/web)

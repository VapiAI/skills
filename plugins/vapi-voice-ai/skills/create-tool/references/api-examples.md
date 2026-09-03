# Tool API Examples

Use these patterns only after selecting and validating the exact tool type. Recheck the current Create Tool schema and SDK docs before generating final code.

The current docs demonstrate tool creation through the TypeScript Server SDK but do not demonstrate `client.tools.create` in the Python Server SDK. Use direct REST in Python instead of guessing an SDK method.

## Conceptual JSON

```json
{
  "type": "endCall",
  "function": {
    "name": "end_completed_call"
  }
}
```

## TypeScript Server SDK

Install `@vapi-ai/server-sdk` and pass the complete validated payload to `tools.create`:

```typescript
import { VapiClient } from "@vapi-ai/server-sdk";

const vapi = new VapiClient({ token: process.env.VAPI_API_KEY! });
const tool = await vapi.tools.create({
  type: "endCall",
  function: { name: "end_completed_call" },
});
```

## Python REST

```python
import os
import requests

tool_payload = {
    "type": "endCall",
    "function": {"name": "end_completed_call"},
}

response = requests.post(
    "https://api.vapi.ai/tool",
    headers={"Authorization": f"Bearer {os.environ['VAPI_API_KEY']}"},
    json=tool_payload,
    timeout=30,
)
response.raise_for_status()
tool = response.json()
```

## cURL

Write the validated conceptual payload to `tool-payload.json`, then send it through the public REST API:

```bash
curl --fail-with-body -X POST https://api.vapi.ai/tool \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @tool-payload.json
```

Read current state before an update or attachment change:

```bash
curl --fail-with-body https://api.vapi.ai/tool/<tool-id> \
  -H "Authorization: Bearer $VAPI_API_KEY"

curl --fail-with-body https://api.vapi.ai/assistant/<assistant-id> \
  -H "Authorization: Bearer $VAPI_API_KEY"
```

## Public Sources

- [Create Tool API](https://docs.vapi.ai/api-reference/tools/create)
- [Default tools](https://docs.vapi.ai/tools/default-tools)
- [Server SDK quickstart](https://docs.vapi.ai/quickstart/web)

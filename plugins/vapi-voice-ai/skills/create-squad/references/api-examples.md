# Squad API Examples

Use these patterns only after resolving and verifying every assistant ID and the intended member order. Recheck the current Create Squad schema and SDK docs before generating final code.

## Conceptual JSON

```json
{
  "name": "Support Squad",
  "members": [
    { "assistantId": "<verified-triage-assistant-id>" },
    { "assistantId": "<verified-billing-assistant-id>" }
  ]
}
```

## TypeScript Server SDK

Install `@vapi-ai/server-sdk`, preserve camelCase API fields, and pass the complete payload to `squads.create`:

```typescript
import { VapiClient } from "@vapi-ai/server-sdk";

const vapi = new VapiClient({ token: process.env.VAPI_API_KEY! });
const triageAssistantId = process.env.VAPI_TRIAGE_ASSISTANT_ID!;
const billingAssistantId = process.env.VAPI_BILLING_ASSISTANT_ID!;
const squad = await vapi.squads.create({
  name: "Support Squad",
  members: [
    { assistantId: triageAssistantId },
    { assistantId: billingAssistantId },
  ],
});
```

## Python Server SDK

Install `vapi_server_sdk`. Use snake_case keyword and nested field names at the Python SDK boundary:

```python
import os
from vapi import Vapi

client = Vapi(token=os.environ["VAPI_API_KEY"])
triage_assistant_id = os.environ["VAPI_TRIAGE_ASSISTANT_ID"]
billing_assistant_id = os.environ["VAPI_BILLING_ASSISTANT_ID"]
squad = client.squads.create(
    name="Support Squad",
    members=[
        {"assistant_id": triage_assistant_id},
        {"assistant_id": billing_assistant_id},
    ],
)
```

## cURL

Write the validated conceptual payload to `squad-payload.json`, then send it through the public REST API:

```bash
curl --fail-with-body -X POST https://api.vapi.ai/squad \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @squad-payload.json
```

## Public Sources

- [Squads documentation](https://docs.vapi.ai/squads)
- [Clinic triage Squad example](https://docs.vapi.ai/squads/examples/clinic-triage-scheduling)
- [Squad API reference](https://docs.vapi.ai/api-reference/squads/create)

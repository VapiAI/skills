# Structured Output API Examples

Use these examples only after validating the current resource shape against Vapi's public API documentation. Placeholder IDs are illustrative; resolve real IDs before a live request.

## Contents

- [Environment and sample definition](#environment-and-sample-definition)
- [Direct REST](#direct-rest)
- [TypeScript Server SDK](#typescript-server-sdk)
- [Python Server SDK](#python-server-sdk)
- [Safe relationship changes](#safe-relationship-changes)
- [Preview, execute, and retrieve](#preview-execute-and-retrieve)
- [Verification checklist](#verification-checklist)

## Environment and sample definition

Keep the private key server-side:

```bash
export VAPI_API_KEY="replace-with-a-private-server-key"
```

Use a narrow definition for a single business question:

```json
{
  "name": "Appointment outcome",
  "description": "Whether the caller and assistant confirmed an appointment during the call.",
  "type": "ai",
  "schema": {
    "type": "object",
    "properties": {
      "booked": {
        "type": "boolean",
        "description": "True only when a specific appointment was confirmed by both parties."
      },
      "startAt": {
        "type": "string",
        "format": "date-time",
        "description": "The confirmed appointment start time, when stated."
      }
    },
    "required": ["booked"]
  }
}
```

If the user asks only for a payload, stop here and state that nothing was saved or attached.

## Direct REST

### Create and capture the returned ID

```bash
curl --fail-with-body -X POST https://api.vapi.ai/structured-output \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  --data @structured-output.json
```

Require a successful response and capture its real `id`. Do not copy an example ID into later requests.

### List and inspect

```bash
curl --fail-with-body "https://api.vapi.ai/structured-output?name=Appointment%20outcome&limit=10" \
  -H "Authorization: Bearer $VAPI_API_KEY"

curl --fail-with-body "https://api.vapi.ai/structured-output/$STRUCTURED_OUTPUT_ID" \
  -H "Authorization: Bearer $VAPI_API_KEY"
```

Use exact IDs after resolving ambiguity. Treat names as user-facing selectors, not durable identifiers.

### Update without changing the schema's top-level type

```bash
curl --fail-with-body -X PATCH \
  "https://api.vapi.ai/structured-output/$STRUCTURED_OUTPUT_ID?schemaOverride=false" \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Whether a specific appointment was confirmed, with its start time when available."
  }'
```

Send only fields that should change. Set `schemaOverride=true` only when the user deliberately changes the schema's top-level type and understands the downstream compatibility impact.

## TypeScript Server SDK

The current official TypeScript Server SDK exposes generated Structured Output methods under `client.structuredOutputs`:

```typescript
import { VapiClient } from "@vapi-ai/server-sdk";

const client = new VapiClient({ token: process.env.VAPI_API_KEY! });

const output = await client.structuredOutputs.structuredOutputControllerCreate({
  name: "Appointment booked",
  description: "Whether a specific appointment was confirmed during the call.",
  type: "ai",
  schema: {
    type: "boolean",
    description: "True only when both parties confirmed a specific appointment.",
  },
});

const verified =
  await client.structuredOutputs.structuredOutputControllerFindOne({
    id: output.id,
  });

console.log({ id: verified.id, name: verified.name, type: verified.type });
```

Preview one existing call without changing its artifact:

```typescript
const preview =
  await client.structuredOutputs.structuredOutputControllerRun({
    structuredOutputId: output.id,
    callIds: [process.env.VAPI_CALL_ID!],
    previewEnabled: true,
  });

console.log(preview);
```

Generated method names can change between SDK releases. Recheck the official SDK reference when producing final code.

## Python Server SDK

The current official Python Server SDK exposes generated methods under `client.structured_outputs`:

```python
import os

from vapi import JsonSchema, Vapi

client = Vapi(token=os.environ["VAPI_API_KEY"])

output = client.structured_outputs.structured_output_controller_create(
    name="Appointment booked",
    description="Whether a specific appointment was confirmed during the call.",
    schema=JsonSchema(
        type="boolean",
        description="True only when both parties confirmed a specific appointment.",
    ),
)

verified = client.structured_outputs.structured_output_controller_find_one(
    id=output.id,
)

print({"id": verified.id, "name": verified.name, "type": verified.type})
```

Preview one call:

```python
import os

preview = client.structured_outputs.structured_output_controller_run(
    structured_output_id=output.id,
    call_ids=[os.environ["VAPI_CALL_ID"]],
    preview_enabled=True,
)

print(preview)
```

Use direct REST if the installed SDK version does not expose the documented resource or generated method signature.

## Safe relationship changes

The Structured Output resource exposes `assistantIds`. Read the definition, construct the full intended relationship array, and patch that array without changing unrelated fields.

Attach using an already resolved ID:

```bash
curl --fail-with-body -X PATCH \
  "https://api.vapi.ai/structured-output/$STRUCTURED_OUTPUT_ID?schemaOverride=false" \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"assistantIds\":[\"$ASSISTANT_ID\"]}"
```

That literal example is safe only when the current relationship list is empty. If other assistants are already linked, include their IDs too. To detach, remove exactly the target assistant ID and send the complete remaining array.

If an integration patches the assistant instead, fetch the assistant first:

```bash
curl --fail-with-body "https://api.vapi.ai/assistant/$ASSISTANT_ID" \
  -H "Authorization: Bearer $VAPI_API_KEY"
```

Construct this request from the returned `artifactPlan`, retaining every existing property:

```json
{
  "artifactPlan": {
    "recordingEnabled": true,
    "loggingEnabled": true,
    "structuredOutputIds": [
      "existing-output-id",
      "new-output-id"
    ]
  }
}
```

The shown fields are illustrative, not a complete artifact plan. Never replace a real assistant's artifact plan with this abbreviated example.

After either attachment method, retrieve both resources and verify the output relationship. Do not report success from the PATCH response alone.

## Preview, execute, and retrieve

### Preview a saved definition

```bash
curl --fail-with-body -X POST https://api.vapi.ai/structured-output/run \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"structuredOutputId\": \"$STRUCTURED_OUTPUT_ID\",
    \"callIds\": [\"$VAPI_CALL_ID\"],
    \"previewEnabled\": true
  }"
```

Preview requires exactly one call ID and does not update the call artifact.

### Preview a transient definition

```json
{
  "callIds": ["resolved-call-id"],
  "previewEnabled": true,
  "structuredOutput": {
    "name": "Needs follow-up",
    "type": "ai",
    "description": "Whether the customer needs a follow-up after this call.",
    "schema": {
      "type": "boolean"
    }
  }
}
```

Send that body to `POST /structured-output/run`. It tests the definition without saving it.

### Execute against existing calls

```bash
curl --fail-with-body -X POST https://api.vapi.ai/structured-output/run \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"structuredOutputId\": \"$STRUCTURED_OUTPUT_ID\",
    \"callIds\": [\"$VAPI_CALL_ID\"],
    \"previewEnabled\": false
  }"
```

This operation writes the value into each call artifact and can replace the existing value for the same Structured Output. Batch at no more than 100 call IDs per request unless current public documentation states a different limit.

### Retrieve the stored result

```bash
curl --fail-with-body "https://api.vapi.ai/call/$VAPI_CALL_ID" \
  -H "Authorization: Bearer $VAPI_API_KEY"
```

Read:

```text
call.artifact.structuredOutputs[structuredOutputId].result
```

Do not confuse a valid JSON shape with a factually correct extraction. Compare representative results with the transcript or messages before calling the output reliable.

## Verification checklist

- The saved definition has the expected real ID, name, type, schema, and description.
- Every intended assistant relationship exists, and no unrelated relationship disappeared.
- Preview used one representative call and did not update its artifact.
- Broad execution used only resolved call IDs and reported per-call failures.
- Each executed call contains the output under its real Structured Output ID.
- The result validates against the schema.
- Representative extracted values agree with call evidence.
- Logs and final output do not expose API keys or unnecessary customer data.

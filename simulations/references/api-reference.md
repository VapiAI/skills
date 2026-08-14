# Simulation API Reference

Use this reference for REST implementation details after reading the workflow in `SKILL.md`. Revalidate fields against Vapi's current [API reference index](https://docs.vapi.ai/llms.txt) or [OpenAPI specification](https://docs.vapi.ai/openapi/api-reference.json) before a live mutation because the public schema can evolve.

## Contents

- [Authentication and conventions](#authentication-and-conventions)
- [Endpoint inventory](#endpoint-inventory)
- [Create reusable resources](#create-reusable-resources)
- [Run simulations](#run-simulations)
- [Inspect and judge results](#inspect-and-judge-results)
- [Advanced scenario fields](#advanced-scenario-fields)
- [Update, cancel, and delete](#update-cancel-and-delete)
- [Implementation patterns](#implementation-patterns)

## Authentication and Conventions

Use the private key only from a server-side environment:

```bash
-H "Authorization: Bearer $VAPI_API_KEY" \
-H "Content-Type: application/json"
```

Base URL: `https://api.vapi.ai`

Create operations return `201`. Reads, updates, cancellations, and deletes return `200` according to the current OpenAPI.

The resource graph is:

```text
personality + scenario -> simulation -> suite -> run -> run items -> evaluations
```

## Endpoint Inventory

| Resource | List/Create | Get/Update/Delete |
|---|---|---|
| Personalities | `GET`, `POST /eval/simulation/personality` | `GET`, `PATCH`, `DELETE /eval/simulation/personality/{id}` |
| Scenarios | `GET`, `POST /eval/simulation/scenario` | `GET`, `PATCH`, `DELETE /eval/simulation/scenario/{id}` |
| Simulations | `GET`, `POST /eval/simulation` | `GET`, `PATCH`, `DELETE /eval/simulation/{id}` |
| Suites | `GET`, `POST /eval/simulation/suite` | `GET`, `PATCH`, `DELETE /eval/simulation/suite/{id}` |
| Runs | `GET`, `POST /eval/simulation/run` | `GET /eval/simulation/run/{id}`; `PATCH` cancels |
| Run items | `GET /eval/simulation/run/{id}/item` | `GET /eval/simulation/run/{id}/item/{itemId}`; `PATCH` cancels |

Additional operations:

- `GET /eval/simulation/concurrency`
- `POST /eval/simulation/scenario/generate`
- `POST /eval/simulation/run/{id}/item/{itemId}/generate` for improvement suggestions

## Create Reusable Resources

### 1. Personality

Prefer listing and reusing a suitable personality. A new personality requires a complete valid Create Assistant configuration under `assistant`:

```json
{
  "name": "Impatient customer",
  "assistant": {
    "name": "Impatient customer tester",
    "model": {
      "provider": "<current-supported-provider>",
      "model": "<current-supported-model>",
      "messages": [
        {
          "role": "system",
          "content": "You are an impatient customer. Be direct and interrupt overly long answers, but follow the scenario intent and use only the facts it provides."
        }
      ]
    }
  }
}
```

Do not send the angle-bracket placeholders. Resolve current provider/model configuration first. Add voice and transcriber only for a deliberate voice-test configuration.

```bash
curl -X POST "https://api.vapi.ai/eval/simulation/personality" \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @personality.json
```

### 2. Scenario

Inline evaluation definitions require `name` and `schema`. Keep the schema primitive unless using `path` to select a primitive leaf from an object structured output.

```json
{
  "name": "Book requested appointment",
  "instructions": "Book an appointment for next Monday at 2:00 PM. Provide the synthetic customer details when asked. End after the assistant confirms the booking reference.",
  "evaluations": [
    {
      "structuredOutput": {
        "name": "appointment_booked",
        "description": "Return true only if the assistant confirms the appointment is booked for next Monday at 2:00 PM.",
        "schema": {
          "type": "boolean",
          "description": "Whether the requested appointment was booked and confirmed."
        }
      },
      "comparator": "=",
      "value": true,
      "required": true
    }
  ],
  "toolMocks": [
    {
      "toolName": "book_appointment",
      "result": "{\"status\":\"confirmed\",\"confirmationId\":\"SIM-12345\"}",
      "enabled": true
    }
  ],
  "targetOverrides": {
    "variableValues": {
      "customerName": "Simulation Customer",
      "accountTier": "test"
    }
  }
}
```

Create it:

```bash
curl -X POST "https://api.vapi.ai/eval/simulation/scenario" \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @scenario.json
```

To reuse a saved structured output, replace `structuredOutput` with:

```json
{
  "structuredOutputId": "<structured-output-id>",
  "comparator": "=",
  "value": true,
  "required": true
}
```

Valid comparators are `=`, `!=`, `>`, `<`, `>=`, and `<=`. Boolean and string values support only `=` and `!=`. The expected value must be a string, number, or Boolean matching the evaluated output.

### 3. Simulation

```json
{
  "name": "Appointment booking - impatient customer",
  "scenarioId": "<scenario-id>",
  "personalityId": "<personality-id>"
}
```

```bash
curl -X POST "https://api.vapi.ai/eval/simulation" \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @simulation.json
```

`scenarioId` and `personalityId` are required. `name` is optional.

### 4. Suite

```json
{
  "name": "Appointment booking regression",
  "simulationIds": ["<simulation-id>"],
  "targetAssignments": [
    {
      "targetType": "assistant",
      "targetId": "<assistant-id>"
    }
  ]
}
```

```bash
curl -X POST "https://api.vapi.ai/eval/simulation/suite" \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @suite.json
```

`name` and `simulationIds` are required. `targetAssignments` accepts `assistant` or `squad` targets and is optional in the create schema.

## Run Simulations

### Run a saved suite against an assistant in chat mode

```json
{
  "simulations": [
    {
      "type": "simulationSuite",
      "simulationSuiteId": "<suite-id>"
    }
  ],
  "target": {
    "type": "assistant",
    "assistantId": "<assistant-id>"
  },
  "iterations": 1,
  "transport": {
    "provider": "vapi.webchat"
  }
}
```

### Run a saved simulation against a squad in voice mode

```json
{
  "simulations": [
    {
      "type": "simulation",
      "simulationId": "<simulation-id>"
    }
  ],
  "target": {
    "type": "squad",
    "squadId": "<squad-id>"
  },
  "iterations": 1,
  "transport": {
    "provider": "vapi.websocket"
  }
}
```

Run the payload:

```bash
curl -X POST "https://api.vapi.ai/eval/simulation/run" \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @run.json
```

The response includes the run `id`, `status`, queued item IDs, and a dashboard `url`. A run can also use inline scenario, personality, assistant, or squad configurations, but saved resources are easier to audit and rerun.

Transport values:

- `vapi.webchat`: text-only conversation
- `vapi.websocket`: full voice conversation

## Inspect and Judge Results

Poll the group:

```bash
curl "https://api.vapi.ai/eval/simulation/run/<run-id>" \
  -H "Authorization: Bearer $VAPI_API_KEY"
```

Then fetch every run item:

```bash
curl "https://api.vapi.ai/eval/simulation/run/<run-id>/item" \
  -H "Authorization: Bearer $VAPI_API_KEY"
```

The group status progresses through `queued`, `running`, and `ended`. Do not judge the run until it is `ended`.

Check all of the following:

1. `itemCounts.total` is greater than zero.
2. `itemCounts.failed` and `itemCounts.canceled` are zero.
3. Every item's `results.passed` is `true`.
4. Every required evaluation has `passed: true`.
5. No required evaluation has an extraction `error` or unexpected `isSkipped` value.

For each evaluation, report its `name`, `extractedValue`, `expectedValue`, `comparator`, `required`, `passed`, and any `error` or `skipReason`. For execution failures, report item `failureReason`, transport, and iteration number separately from evaluation failures.

## Advanced Scenario Fields

### Tool mocks

```json
{
  "toolMocks": [
    {
      "toolName": "lookup_order",
      "result": "{\"status\":\"not_found\"}",
      "enabled": true
    }
  ]
}
```

The result is a string. Only the exact named tool is intercepted; all other tools remain live.

### Lifecycle hooks

```json
{
  "hooks": [
    {
      "on": "simulation.run.ended",
      "do": [
        {
          "type": "webhook",
          "server": {
            "url": "https://example.com/vapi/simulation-events",
            "credentialId": "<credential-id>"
          },
          "include": {
            "transcript": true,
            "messages": false,
            "recordingUrl": false
          }
        }
      ]
    }
  ]
}
```

Hook events are `simulation.run.started` and `simulation.run.ended`. Both chat and voice can send them. Chat payloads omit call-specific fields; voice payloads can include call metadata and recordings when configured.

### Target variables

```json
{
  "targetOverrides": {
    "variableValues": {
      "customerName": "Simulation Customer",
      "caseId": "SIM-CASE-001"
    }
  }
}
```

Variable names must match Liquid placeholders in the target assistant or squad configuration.

## Update, Cancel, and Delete

Fetch before patching. Send only the scalar fields being changed. When changing arrays, send the complete desired array.

```bash
curl -X PATCH "https://api.vapi.ai/eval/simulation/personality/<personality-id>" \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name":"Renamed tester"}'
```

Suite `simulationIds` and `targetAssignments` explicitly replace existing arrays. Treat scenario `evaluations`, `hooks`, and `toolMocks` as complete replacement values when sent.

Cancel a queued or running group:

```bash
curl -X PATCH "https://api.vapi.ai/eval/simulation/run/<run-id>" \
  -H "Authorization: Bearer $VAPI_API_KEY"
```

Cancel one queued or running item:

```bash
curl -X PATCH "https://api.vapi.ai/eval/simulation/run/<run-id>/item/<item-id>" \
  -H "Authorization: Bearer $VAPI_API_KEY"
```

Delete only after resolving and confirming the exact dependency ID:

```bash
curl -X DELETE "https://api.vapi.ai/eval/simulation/suite/<suite-id>" \
  -H "Authorization: Bearer $VAPI_API_KEY"
```

## Implementation Patterns

### TypeScript REST

```typescript
const response = await fetch("https://api.vapi.ai/eval/simulation/run", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${process.env.VAPI_API_KEY}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify(runPayload),
});

if (response.status !== 201) {
  throw new Error(`Vapi simulation run failed: ${response.status} ${await response.text()}`);
}

const run = await response.json();
console.log(run.id, run.url);
```

### Python REST

```python
import os
import requests

response = requests.post(
    "https://api.vapi.ai/eval/simulation/run",
    headers={
        "Authorization": f"Bearer {os.environ['VAPI_API_KEY']}",
        "Content-Type": "application/json",
    },
    json=run_payload,
    timeout=30,
)
response.raise_for_status()
if response.status_code != 201:
    raise RuntimeError(f"Unexpected status: {response.status_code}")

run = response.json()
print(run["id"], run.get("url"))
```

Use an SDK method only if the installed SDK and current official documentation expose that exact simulations method. Direct REST is the safe fallback for this API family.

# Function Tool Server

Read this file only after selecting a custom `function` tool and only when the user asks to implement its external backend. It does not apply to native, integration, API Request, or MCP tools.

## Contract

Vapi sends a `tool-calls` server message to the function tool's resolved server URL. Verify the complete request and response schemas against the current public `ServerMessageToolCalls` documentation before deployment.

A handler must:

1. accept only the expected Vapi tool-call message;
2. authenticate the request using the configured Vapi server credential mechanism;
3. allowlist supported function names;
4. parse and validate arguments against the selected function's schema;
5. authorize the call or tenant before accessing business data;
6. execute the function idempotently where practical;
7. return one result for each tool-call ID.

Representative response shape:

```json
{
  "results": [
    {
      "toolCallId": "<id-from-request>",
      "result": "<safe-result-for-the-assistant>"
    }
  ]
}
```

Do not hard-code an example request shape into production parsing. Generate or validate types from the current public server-message schema because message representations can change.

## Implementation Requirements

- Use a real HTTPS endpoint supplied or created within the user's project scope.
- Keep credentials in secret storage and reference a verified Vapi credential from the function tool's `server` configuration.
- Reject unknown message types and function names.
- Enforce body-size limits, argument schemas, authorization, downstream timeouts, and safe error responses.
- Use the tool-call ID as an idempotency key for state-changing operations where practical.
- Log correlation IDs and outcomes, not secrets or unnecessary personal data.
- Return bounded, model-useful results; do not expose stack traces, tokens, or private records.
- Test success, invalid arguments, unknown functions, unauthorized access, downstream timeouts, duplicate delivery, and partial multi-call failure.

## Completion Boundary

The function tool is operational only after all of these are true:

1. the backend exists and is reachable;
2. authentication is configured;
3. the request and response contract passes tests;
4. the Vapi function tool references the verified endpoint;
5. the tool is attached to the intended assistant;
6. a safe test confirms the complete path.

If only the tool payload or server code exists, state exactly which remaining steps are incomplete.

## Public Sources

- [Custom tools](https://docs.vapi.ai/tools/custom-tools)
- [Server authentication](https://docs.vapi.ai/server-url/server-authentication)
- [ServerMessageToolCalls type](https://github.com/VapiAI/server-sdk-typescript/blob/main/src/api/types/ServerMessageToolCalls.ts)

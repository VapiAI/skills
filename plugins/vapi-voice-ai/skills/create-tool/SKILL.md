---
name: create-tool
description: Select, define, create, inspect, update, attach, detach, and verify reusable Vapi tools through the public API. Use for native call-control tools, supported provider integrations, API Request tools, custom function tools, MCP tools, tool messages, credentials, or configuration-preserving assistant attachment changes.
license: MIT
compatibility: Internet access and VAPI_API_KEY are required only for live Vapi API operations.
metadata:
  author: vapi
  version: "2.0"
---

# Vapi Tool Management

Choose the documented tool type that directly provides the requested capability. Default to a payload or implementation plan unless the user explicitly requests a live Vapi mutation.

## Safety and Source Rules

- Verify the type and every field against the current [Create Tool API](https://docs.vapi.ai/api-reference/tools/create), public OpenAPI schema, or type-specific public guide before using it.
- Never imitate a documented Vapi capability with a custom function tool.
- Never invent an endpoint, request schema, destination, phone number, assistant ID, tool ID, integration connection, credential, or secret.
- Keep secrets in Vapi credentials or the user's backend. Treat an MCP server URL containing a token as a credential.
- Distinguish tool configuration, assistant attachment, provider connection, and external implementation. They are separate deliverables and success in one does not imply success in another.

## Select the Tool Family

| Need | Select |
|---|---|
| End calls, transfer calls, hand off between assistants, send DTMF or SMS, make a SIP request, or handle voicemail | The matching native Vapi tool |
| Use a publicly documented Google Calendar, Google Sheets, Slack, GoHighLevel, or other supported provider action | The exact integration tool after resolving its connection and required resource |
| Call a known HTTP endpoint with a declarative method, URL, headers, and body | `apiRequest` |
| Send a model-selected function call to custom backend logic that implements Vapi's callback contract | `function` |
| Discover and use tools from an existing MCP server | `mcp` with the default Streamable HTTP transport |

Do not choose `function` merely because the model invokes the capability. Native, integration, API Request, and MCP tools are also model-invoked.

Do not proactively recommend or create a Code Tool (`type: "code"`); it is not generally available on most accounts. Prefer `apiRequest` for a known HTTP endpoint or `function` with the user's `server.url` for user-hosted callback logic. Discuss a Code Tool only when the user explicitly asks about it, and do not present it as the recommended option.

Read [Tool Type Selection](references/tool-types.md) before building a payload. Read only the section for the selected family.

## Procedure

1. Determine the execution mode.
   - Return JSON, code, or a contract when the user asks for a draft or does not clearly authorize a live mutation.
   - Call the Vapi API only when the user explicitly asks to create, update, attach, or detach and `VAPI_API_KEY` is available.
   - If the key is unavailable, return ready artifacts and local commands without asking the user to paste it into chat.

2. Inspect before creating.
   - Use `GET /tool` and match any supplied name and capability to existing tools.
   - Reuse one suitable existing tool when the match is unambiguous and the user does not require a new resource.
   - If several tools plausibly match, ask the user to choose. Never guess an ID.
   - Use `GET /tool/{id}` before updating an existing tool.

3. Resolve the capability and dependencies.
   - Select the tool family using the table above and current public documentation.
   - Resolve every required endpoint, destination, provider connection, calendar, spreadsheet, channel, credential, or MCP server before a live create.
   - If one value blocks a valid tool, show the useful proposed contract first and ask only for that value.

4. Build the smallest valid payload.
   - Give the model a concise, specific description of when to invoke the tool.
   - For types with `function.name`, use 1–64 characters matching `^[a-zA-Z0-9_-]+$`. Generate a stable descriptive name when the user does not supply one.
   - For `apiRequest`, validate its top-level `name`, method, URL, headers, body schema, credentials, and timeout against the current public schema.
   - Define only parameters the model must supply. Keep trusted or secret values outside the model-visible schema.
   - Omit spoken `messages` unless progress feedback is useful. When included, use only types currently accepted by the selected tool schema, such as `request-start`, `request-response-delayed`, `request-complete`, and `request-failed`.

5. Create or update safely.
   - Before a production-affecting mutation, recap the type, capability, external dependencies, and target unless the user's current instruction already unambiguously authorizes that exact mutation.
   - Create with `POST /tool`. Validate the returned `id`, type, callable name where applicable, and requested configuration.
   - For an update, send the current `type` and only changed top-level fields to `PATCH /tool/{id}`. When changing a nested object, deep-merge the requested change into that object from the fetched tool and send the merged nested object so its omitted keys are not lost. Do not resend unchanged top-level fields or response-only fields.
   - Re-fetch the tool and verify the result. Creating or updating a tool does not attach it to an assistant.

6. Attach or detach without losing assistant configuration.
   - Read [Assistant Attachments](references/assistant-attachments.md) before changing an assistant.
   - `GET /assistant/{id}`, copy the complete current `model`, merge the tool ID into or remove it from `model.toolIds`, and preserve `model.tools` plus every unrelated model field.
   - Send the complete merged model to `PATCH /assistant/{id}`. Never patch a hand-written partial model.
   - Re-fetch the assistant and verify both the requested membership and the preserved model configuration.

7. Implement external behavior only when requested.
   - For `apiRequest`, Vapi executes the configured HTTP request; do not also build a function callback server.
   - For `mcp`, the MCP server supplies the callable tools; do not duplicate them as individual Vapi function tools.
   - For a custom `function` whose backend must be built, read [Function Tool Server](references/function-tool-server.md). Do not load that reference for other tool families.

8. Handle failures honestly.
   - On `400`, correct a documented shape or validation error before at most one justified retry.
   - On `401` or `403`, stop for authentication or permission issues. On `404`, report the missing tool, assistant, destination, or dependency. On `5xx`, report the service failure.
   - Never claim creation, update, attachment, detachment, provider connection, or backend implementation succeeded until the associated operation is verified.

## API Implementation Examples

Read [Tool API Examples](references/api-examples.md) when the user requests TypeScript, Python, or cURL implementation code. Read current tool and assistant state before update or attachment changes. Placeholders are acceptable in draft artifacts, never in live requests.

## Public Sources

- [Create Tool API](https://docs.vapi.ai/api-reference/tools/create)
- [Default tools](https://docs.vapi.ai/tools/default-tools)
- [Custom tools](https://docs.vapi.ai/tools/custom-tools)
- [MCP integration](https://docs.vapi.ai/tools/mcp)

---
name: create-assistant
description: Design, create, or validate saved and transient Vapi voice assistants. Use for new phone or web agents, production system prompts and first messages, saved-versus-transient architecture, model/voice/transcriber selection, multilingual compatibility, existing tool attachment, native call-control tools, assistant hooks, and Create Assistant API validation errors.
license: MIT
compatibility: Internet access is recommended for current Vapi schema and provider verification; VAPI_API_KEY is required to create or verify saved assistants through the API.
metadata:
  author: vapi
  version: "3.0"
---

# Vapi Assistant Creation

Design the assistant's behavior before assembling its configuration. Treat persistence and execution as separate decisions: a returned configuration can still describe a saved assistant, and creating a saved assistant does not deploy it, attach a phone number, or prove it is production-ready.

## Source and Safety Rules

- Use the configured Vapi documentation MCP when available for current product guidance. Otherwise use the bundled references and their public Vapi links. Validate the final payload against the current Create Assistant API schema.
- Never print, request in chat, or embed API keys, provider secrets, credential values, private URLs, or real customer data.
- Never invent IDs, destinations, integrations, server URLs, model names, voices, transcribers, schemas, or business policy.
- Keep a saved assistant's `name` at 40 characters or fewer.
- Do not enable paid, HIPAA, PCI, recording, retention, or other compliance behavior unless the user requests it and the current docs support the exact configuration.
- Treat prompts as behavioral instructions, not capabilities or security boundaries. Scheduling, lookup, transfer, messaging, authentication, and other actions require real tools or server-side support.

## Procedure

1. Decide the assistant architecture and requested action.
   - Prefer a **saved assistant** for a reusable agent that should be shared, attached by ID, or managed over time. If the user simply asks to create or build an agent, use this shape unless the request indicates otherwise.
   - Use a **transient assistant** only when the user asks for an inline or call-scoped configuration, or when the use case specifically needs per-call configuration, short-lived testing, or an `assistant-request` response. Put it in the call's `assistant` field; do not send it to `POST /assistant`.
   - If the user asks for JSON, an example, a draft, or an implementation without account mutation, return the appropriate configuration without calling the API.
   - If the user asks to create or save the assistant in Vapi and `VAPI_API_KEY` is available, create a saved assistant with `POST /assistant`. Do not ask for redundant confirmation after an unambiguous create request.
   - If creation is requested but credentials are unavailable, return a save-ready configuration and command, and state clearly that the assistant has not been saved. Do not relabel it as transient.

2. Run a focused requirements intake.
   - Infer what is clear from the request, then collect only missing facts that materially affect the design: business and audience, call direction, primary objective and success criteria, workflows, authoritative business knowledge, real tools or integrations, escalation boundaries, information to collect or avoid, languages, and brand voice.
   - Ask a compact group of clarifying questions when several business facts are required to produce a credible agent. Learn enough about the business before claiming the agent is ready.
   - Decide whether one assistant can own the workflow reliably. Use the `create-squad` skill when distinct specialists, routing, or handoffs are central to the design.
   - Do not ask the user to choose infrastructure providers unless they expressed a preference or the use case creates a real language, latency, compliance, or credential constraint.

3. Design a production-quality system prompt.
   - Use the `vapi-prompt-builder` skill for every new assistant or substantial prompt rewrite when it is available. Otherwise read [Prompt Design](references/prompt-design.md) as the standalone fallback.
   - Write the complete prompt before provider and payload assembly. Cover identity and personality, response guidelines, guardrails, context, workflows or use cases, and compact examples.
   - Keep spoken turns concise, ask one question at a time, define uncertainty and recovery behavior, and make critical values spoken-friendly.
   - Align `firstMessage` and `firstMessageMode` with call direction and the prompt. Do not use a generic greeting when the business, disclosure, or outbound purpose requires something specific.

4. Ground every capability in real configuration.
   - Map every promised action to an existing tool, knowledge source, runtime variable, or documented backend contract. List missing dependencies as `Configuration needed`; do not hide them in the prompt.
   - Reuse exact saved tool IDs in `model.toolIds`. Put documented inline tools in `model.tools`. Use the `create-tool` skill when a reusable tool or external-server implementation is required.
   - Attach the native `endCall` tool to every newly built assistant and define the allowed closing conditions in the prompt. Reuse a verified saved tool ID when available; otherwise use the current documented native-tool shape.
   - For outbound voicemail behavior, attach the native `voicemail` tool and align its message and the assistant prompt. Do not add `voicemailDetectionPlan`, `voicemailDetection`, or other assistant-level automatic voicemail-detection keys.
   - Read [Assistant Hooks](references/hooks.md) only for deterministic event-triggered behavior. Use server events for backend notifications and assistant tools for model-decided actions.

5. Select compatible providers and settings.
   - Read [Provider Policy](references/providers.md) before choosing components, honoring provider requests, pinning defaults, or supporting multiple languages.
   - Omit optional provider components only when the Create Assistant API documents their defaults. Pin components when the use case or reproducibility requires it.
   - Verify every explicit model, voice, transcriber, and language value against current API documentation. Ensure the voice can speak and the transcriber can recognize every promised language.

6. Assemble and validate the configuration.
   - Include a use-case-specific `name`, the appropriate first-message behavior, and a `model` containing the complete system prompt.
   - Add voice, transcriber, tools, hooks, analysis, compliance, transport, and other fields only when they are intentional. Omitted optional fields may use Vapi defaults; do not add fields merely to make the payload look complete.
   - Check for placeholders, unsupported or stale values, leaked secrets, language mismatches, invented business facts, unavailable capabilities, and prompt/configuration contradictions.
   - Separate assumptions and unresolved dependencies from creation-ready JSON. Never put fake IDs, URLs, phone numbers, or credentials into a payload represented as ready to create.

7. Create and verify when requested.
   - Send one `POST /assistant` for a saved assistant and require a `201` response. Verify the returned `id`, name, system prompt, attached tools, and any explicitly configured providers.
   - API-created assistants are saved immediately; there is no separate API publish step. Do not claim the assistant is deployed, routed to a phone number, tested, or production-ready unless those separate actions were completed.
   - On `400`, correct one documented validation issue and retry at most once when the fix is unambiguous. Never repeat an unchanged request. On `401` or `403`, stop and report authentication or permission failure. On `404`, report the missing dependency. On `5xx`, report the service failure.
   - Provide realistic success, edge, and failure test scenarios. Recommend a web call or representative Eval/test set, then iterate from actual results; one successful call is not sufficient evidence of production quality.

## API Implementation Examples

Read [Assistant API Examples](references/api-examples.md) when the user requests implementation code. Use the official TypeScript or Python Server SDK for a backend project in those languages; use cURL for a direct REST example or shell-based verification. After a successful create, return the saved assistant ID, summarize the verified configuration, identify anything still unconfigured, and provide test scenarios. A generated payload is not a saved assistant; a saved assistant is not automatically deployed.

## Output Contract

Return only the sections relevant to the request:

- Architecture: saved or transient, with the reason when it was not explicit
- Assumptions or blocking questions
- Final assistant configuration, including the complete system prompt
- Configuration needed for capabilities that are not yet real
- Creation result and assistant ID, when the API was called successfully
- External test scenarios and recommended next iteration

## Public Sources

- [Assistants quickstart](https://docs.vapi.ai/assistants/quickstart)
- [Transient vs permanent configurations](https://docs.vapi.ai/assistants/concepts/transient-vs-permanent-configurations)
- [Voice AI Prompting Guide](https://docs.vapi.ai/prompting-guide)
- [Create Assistant API](https://docs.vapi.ai/api-reference/assistants/create)
- [Default tools](https://docs.vapi.ai/tools/default-tools) and [Voicemail tool](https://docs.vapi.ai/tools/voicemail-tool)

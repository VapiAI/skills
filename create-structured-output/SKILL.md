---
name: create-structured-output
description: Design, create, inspect, update, attach, detach, preview, execute, and verify reusable Vapi Structured Outputs through public API or Server SDK workflows. Use for post-call extraction, typed call artifacts, AI-versus-regex extraction, JSON Schema design, backfilling existing calls, or retrieving structured results programmatically.
license: MIT
compatibility: Internet access is recommended for current Vapi schema verification; VAPI_API_KEY is required for saved resources, assistant attachments, call execution, and result retrieval.
metadata:
  author: vapi
  version: "1.0"
---

# Vapi Structured Output Creation

Build the smallest reusable post-call extraction that represents the user's actual downstream contract. Keep definition creation, assistant attachment, execution, and result retrieval separate: success at one stage does not prove the next stage occurred.

## Source and Safety Rules

- Use the configured Vapi documentation MCP when available. Otherwise use current public Vapi API documentation and [API Examples](references/api-examples.md). Revalidate request fields and SDK methods before final implementation.
- Use a private Vapi API key only on a trusted server. Read it from `VAPI_API_KEY`; never print, request in chat, or embed it in source, client-side code, or examples.
- Never invent resource IDs, call IDs, extraction fields, enum values, data-retention requirements, or customer data.
- Do not enable `compliancePlan.forceStoreOnHipaaEnabled` unless the user explicitly requests it and confirms that the output cannot contain PHI or other sensitive data.
- Treat call transcripts, messages, tool results, and extracted values as sensitive customer data. Minimize what is logged or reproduced.

## Procedure

1. Choose the output mode.
   - For a schema, payload, review, or implementation example, return an artifact without calling Vapi. State that nothing was saved, attached, or executed.
   - For a reusable saved definition, use `POST /structured-output` only when the user asks to create or save it and credentials are available.
   - For a one-call experiment that does not need a saved definition, pass a transient `structuredOutput` to `POST /structured-output/run` with `previewEnabled: true`.
   - Treat attachment, detachment, and execution against existing calls as separate requested actions. Do not infer them from creation alone.

2. Define the extraction contract.
   - Identify the downstream consumer, required fields, optional fields, allowed categories, formats, and behavior when evidence is absent or ambiguous.
   - Ask only for missing facts that materially change the schema. State safe assumptions for the rest.
   - Split unrelated outputs when they have different consumers, retention policies, or iteration cycles. Keep one output when the fields form one stable business record.

3. Choose AI or regex.
   - Use `type: "ai"` for meaning, classification, summarization, sentiment, outcome detection, normalization, or facts expressed in varied language.
   - Use `type: "regex"` only for deterministic transcript matching with a stable pattern. Use RE2-compatible syntax and choose a top-level schema type that matches the documented regex result: boolean, string, number/integer, or array.
   - Do not use regex to infer meaning. Do not use AI when a literal, stable pattern is the entire requirement.

4. Design the smallest useful JSON Schema.
   - Include only fields the caller can provide or the call evidence can support.
   - Add concise descriptions that distinguish semantically similar fields.
   - Use `enum` for a closed category set, `format` or `pattern` for externally validated strings, and numeric bounds when the business contract defines them.
   - Mark a field required only when every valid call should produce it. Make conditionally available values optional instead of forcing guesses.
   - Prefer a primitive schema for a single value and an object only for a cohesive record. Avoid deep nesting unless the downstream contract needs it.
   - Validate the schema with a standard JSON Schema validator before sending it.

5. Create, inspect, or update the definition.
   - Keep saved names between 1 and 40 characters.
   - On create, send `name` and `schema`; add `type`, `description`, `regex`, `model`, or `compliancePlan` only when intentional.
   - On inspect, resolve the exact resource with list filters or a verified ID, then use `GET /structured-output/{id}`. Do not guess from a partial name.
   - On update, read the current definition first and send only fields that should change. Use `schemaOverride=true` only when intentionally changing the schema's top-level type; otherwise do not use it to bypass schema safety.
   - Re-fetch after mutation and compare the requested fields. A successful HTTP status without the expected returned state is not verified success.

6. Attach or detach safely.
   - Prefer the saved Structured Output's documented `assistantIds` relationship for attachment. Read its current `assistantIds`, add or remove exactly the resolved assistant ID, and preserve every unrelated ID.
   - Patch only `assistantIds` on the Structured Output for this operation. Re-fetch the Structured Output and assistant; verify the relationship and the assistant's `artifactPlan.structuredOutputIds` when returned.
   - If the implementation instead patches the assistant, first read the assistant and send the complete existing `artifactPlan` with only `structuredOutputIds` changed. Preserve recording, logging, transcript, scorecard, storage, and other artifact settings.
   - Do not claim that creating a definition attached it. Do not claim that detaching deleted it or removed results already stored on past calls.

7. Preview before broad execution.
   - Use `POST /structured-output/run` with one real call ID and `previewEnabled: true`. Supply either `structuredOutputId` or a transient `structuredOutput`, not both.
   - Confirm the selected call contains representative evidence and that the returned value satisfies the schema and business meaning.
   - State that preview does not update the call artifact.
   - If extraction is wrong, simplify the schema or improve descriptions before changing models or custom extraction prompts.

8. Execute or backfill only when requested.
   - Use `previewEnabled: false` or omit it to update call artifacts. Pass no more than the currently documented maximum of 100 call IDs per request.
   - Before a multi-call run, state the exact output, call count, and that existing values for this output may be replaced while other structured-output values remain.
   - Use only call IDs supplied by the user or returned by a verified public API query. Report partial failures by call ID; do not imply an all-or-nothing transaction.

9. Retrieve and verify results.
   - After a normal attached call finishes, allow for post-call processing before checking the call.
   - Retrieve each call with `GET /call/{id}` and read `call.artifact.structuredOutputs[structuredOutputId].result`.
   - Validate the result against the intended schema and inspect representative source evidence before calling it accurate. Schema validity proves shape, not factual correctness.
   - Report separately: definition saved, assistant linked, preview returned, call artifact updated, and result validated. Mention only stages actually verified.

## Error Handling

- On `400`, inspect the response for schema, regex, model, relationship, or run constraints. Correct one unambiguous documented issue and retry once; never repeat an unchanged request.
- On `401` or `403`, stop and report authentication or permission failure.
- On `404`, report the missing Structured Output, assistant, or call and identify the exact unresolved ID.
- On `409`, re-read current state before deciding whether the intended relationship or update already exists.
- On `429` or `5xx`, preserve the request context, report the service condition, and do not claim success.
- If a result is absent, distinguish processing delay, missing attachment, disabled artifact storage, insufficient call evidence, and extraction failure before recommending a change.

## API Implementation Examples

Read [API Examples](references/api-examples.md) when implementation code is needed. Use the official TypeScript or Python Server SDK only after confirming the generated method in its current official reference; use direct REST when SDK syntax is unavailable or unstable.

## Output Contract

Return only the sections relevant to the request:

- Mode: artifact-only, saved definition, relationship change, preview, or artifact-writing run
- Assumptions or blocking questions
- Final schema and Structured Output configuration
- Created or updated resource ID and verified fields, when mutated
- Attachment state and preserved relationships, when changed
- Preview or execution result, affected call IDs, and whether artifacts changed
- Retrieved result plus schema and evidence limitations
- Remaining configuration or validation work

## Public Sources

- [Structured Outputs quickstart](https://docs.vapi.ai/assistants/structured-outputs-quickstart/)
- [Create Structured Output API](https://docs.vapi.ai/api-reference/structured-outputs/structured-output-controller-create)
- [List Structured Outputs API](https://docs.vapi.ai/api-reference/structured-outputs/structured-output-controller-find-all)
- [Get Structured Output API](https://docs.vapi.ai/api-reference/structured-outputs/structured-output-controller-find-one)
- [Update Structured Output API](https://docs.vapi.ai/api-reference/structured-outputs/structured-output-controller-update)
- [Run Structured Output API](https://docs.vapi.ai/api-reference/structured-outputs/structured-output-controller-run)
- [Get Call API](https://docs.vapi.ai/api-reference/calls/get/)
- [Official TypeScript Server SDK reference](https://github.com/VapiAI/server-sdk-typescript/blob/main/reference.md)
- [Official Python Server SDK reference](https://github.com/VapiAI/server-sdk-python/blob/main/reference.md)

---
name: simulations
description: Design, create, run, monitor, and maintain Vapi Simulations for assistants and squads. Use for simulation personalities, scenarios, structured-output success criteria, simulations, suites, chat or voice runs, tool mocks, target variables, lifecycle webhooks, regression coverage, CI quality gates, run-result analysis, and simulation API validation errors. Do not use for fixed-turn mock-conversation Evals unless the user is deciding between Evals and Simulations.
license: MIT
compatibility: Internet access is recommended for current Vapi schema verification; VAPI_API_KEY is required for live simulation resource operations and runs.
metadata:
  author: vapi
  version: "1.0"
---

# Vapi Simulations

Build realistic conversation tests in five layers: a personality controls the AI tester, a scenario defines its intent and measurable outcomes, a simulation pairs them, a suite groups simulations, and a run executes them against an assistant or squad.

## Source and Safety Rules

- Verify live payloads against the current Vapi documentation MCP, API reference, or public OpenAPI before sending them. Simulations use the `/eval/simulation` API family.
- Never print, request in chat, or embed API keys, provider secrets, credential values, private webhook URLs, or real customer data.
- Treat running a simulation as an external action. It can consume credits, use concurrency, send webhooks, and call the target's real tools unless they are mocked.
- Do not run, cancel, update, or delete resources unless the user clearly requests that operation. Draft configurations when mutation is not requested.
- Resolve every assistant, squad, personality, scenario, simulation, suite, tool, structured-output, and credential ID from user input or the API. Never invent an ID.
- Do not create legacy Test Suites. Use Evals for deterministic turn-by-turn checks and Simulations for dynamic conversations over chat or voice.

## Procedure

1. Choose the test type and execution mode.
   - Use Simulations for multi-turn behavior, personality variation, squad handoffs, realistic tool paths, or audio behavior.
   - Use Evals instead when the requirement is an exact response, regex, fixed mock conversation, or precise tool-call argument check.
   - Return a test plan or payload when the user asks to design, draft, review, or explain. Perform live mutations only when explicitly requested and `VAPI_API_KEY` is available.

2. Inspect the target and existing test resources.
   - Fetch the assistant or squad and identify its core paths, guardrails, tools, variables, languages, and failure behavior.
   - List existing personalities, scenarios, simulations, suites, and reusable structured outputs before creating duplicates.
   - Reuse an existing resource only when its intent and configuration match unambiguously. Otherwise create a clearly named new resource or ask the user to choose among plausible matches.

3. Design coverage before payloads.
   - Start with one smoke simulation for the core path, one or two required Boolean outcomes, chat transport, and one iteration.
   - Add regression simulations for repaired defects. Add separate edge cases for ambiguity, interruption, refusal, unavailable dependencies, failed tools, escalation, and handoffs.
   - Keep scenario intent, personality behavior, and evaluation criteria independent so each can be reused.
   - Name resources by behavior and expected outcome, not implementation details.

4. Define the personality.
   - Prefer a suitable existing personality when available.
   - When creating one, provide a complete valid assistant configuration for the AI tester. Put stable temperament, speaking style, and caller behavior in its system prompt; put the situation-specific goal in the scenario.
   - Use the `create-assistant` skill to assemble or validate the personality's assistant configuration when available.
   - Configure voice and transcriber only when voice runs need them. Chat runs use the personality's model but skip its audio path.

5. Define the scenario and evaluations.
   - Write `instructions` as the AI tester's intent and facts. Describe the goal and constraints without scripting the target assistant's answer.
   - Make each evaluation measure one observable outcome. Prefer descriptive Boolean outputs for pass/fail facts and numeric outputs for thresholds.
   - Provide either `structuredOutputId` or inline `structuredOutput`, never both. Inline outputs require `name` and a JSON `schema`.
   - Match the expected `value` type to the evaluated primitive. Use `=` or `!=` for Boolean and string; numeric types also support `>`, `<`, `>=`, and `<=`.
   - Keep important criteria `required: true`. Use optional criteria only for diagnostics that must not fail the simulation.
   - Object structured outputs may be evaluated through a primitive leaf using `path`. Do not compare an object or array directly.

6. Isolate side effects and runtime context.
   - Inspect the target's configured tools before every run. Mock any tool whose real execution could write data, contact people, spend money, or make the test non-deterministic.
   - Match each `toolMocks[].toolName` exactly. The mock `result` is always a string; encode JSON as a string when the target expects JSON-shaped output.
   - Assume every unmocked tool remains live in both chat and voice simulations.
   - Put test values for `{{variables}}` in `targetOverrides.variableValues`. Use synthetic data and keep secrets in Vapi credentials.
   - Configure `simulation.run.started` or `simulation.run.ended` hooks only when requested. Prefer `server.credentialId` to inline authorization headers.

7. Create and verify reusable resources.
   - Create in dependency order: personality and scenario, then simulation, then optional suite.
   - Require `201` for create operations. Verify returned IDs and the fields that define the test.
   - For updates, fetch the current resource first. Omit unrelated scalar fields and send the complete intended value for any array being changed; suite `simulationIds` and `targetAssignments` replace their existing arrays.
   - Re-fetch after update. Deleting a suite or other simulation resource is permanent; verify the exact ID and dependency impact first.

8. Run deliberately.
   - Prefer `vapi.webchat` for fast prompt, tool, and conversation-logic iteration.
   - Use `vapi.websocket` for speech recognition, voice output, interruptions, recordings, or final end-to-end validation.
   - Start with one iteration. Increase iterations only to measure behavioral consistency after a single run is valid.
   - Before sending the run, recap the target, simulations or suite, transport, iterations, tool mocks, and any remaining live side effects.
   - Create the run with `POST /eval/simulation/run` and require `201`. Return the run ID and dashboard `url` when present.

9. Monitor and diagnose results.
   - Poll `GET /eval/simulation/run/{id}` until `status` is `ended`; do not treat `queued` or `running` as success.
   - Fetch `GET /eval/simulation/run/{id}/item` and inspect every item. A passing group has items to evaluate, zero failed or canceled items, and every required evaluation passes.
   - Report actual versus expected values, extraction errors, skipped evaluations, failure reasons, transcript evidence, transport, and iteration number.
   - Diagnose the failing layer before changing the assistant: target runtime failure, scenario ambiguity, personality behavior, tool mock mismatch, structured-output extraction, or genuine assistant behavior.
   - Keep the evaluation stable when fixing the assistant. Change expected criteria only when the business requirement changed.

10. Handle failures honestly.
   - On `400`, compare the request with the current schema and correct one unambiguous validation issue before at most one retry.
   - On `401` or `403`, stop for authentication or permission. On `404`, report the missing dependency. On `409` or concurrency errors, inspect `GET /eval/simulation/concurrency` and active runs. On `5xx`, report the service failure.
   - Cancel only queued or running groups or items. Never claim a run, cancellation, mutation, or pass succeeded until the corresponding API response is verified.

## API Implementation

Read [Simulation API Reference](references/api-reference.md) before producing REST code, making a live request, configuring hooks or mocks, or interpreting run results. Use direct REST unless the current official Vapi SDK documentation explicitly exposes the required simulation resource and method; never invent SDK method names.

## Output Contract

Return only the sections relevant to the request:

- Test strategy: target behavior, coverage, and why Simulation rather than Eval
- Resource plan: personality, scenario, evaluations, simulation, and suite
- Side-effect review: mocked tools, live tools, hooks, variables, transport, iterations, and expected cost/concurrency impact
- Save-ready JSON or implementation code
- Created resource IDs and verified fields, when mutations succeeded
- Run ID, dashboard URL, status, item counts, and per-evaluation evidence, when a run was requested
- Failure diagnosis and the smallest recommended next change

## Public Sources

- [Simulations overview](https://docs.vapi.ai/observability/simulations-overview)
- [Simulations quickstart](https://docs.vapi.ai/observability/simulations-quickstart)
- [Simulations advanced](https://docs.vapi.ai/observability/simulations-advanced)
- [Manage simulations](https://docs.vapi.ai/observability/simulations-manage)
- [Vapi API reference index and OpenAPI](https://docs.vapi.ai/llms.txt)

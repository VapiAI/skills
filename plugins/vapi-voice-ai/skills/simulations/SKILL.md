---
name: simulations
description: Design, create, run, monitor, and maintain Vapi Simulations for assistants and squads. Use for turning plain-language requirements into a coverage plan, simulation personalities, scenarios, structured-output success criteria, simulations, suites, extending an existing suite, chat or voice runs, tool mocks, target variables, lifecycle webhooks, regression coverage, launch readiness, CI quality gates, run-result analysis, and simulation API validation errors. Do not use for fixed-turn mock-conversation Evals unless the user is deciding between Evals and Simulations.
license: MIT
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

3. Turn requirements into testable statements.
   - Collect the requirements from the user, a document, a transcript, or the target's prompt and tools. Rewrite each one until two reviewers would reach the same pass or fail decision: "the agent handles errors gracefully" becomes "if the scheduling tool fails, the agent says the change is not confirmed and offers a safe next step".
   - Record where each requirement came from. Return vague or unsourced requirements as open questions instead of guessing.
   - Tag each requirement as high-impact (data, money, unauthorized changes, missed escalation, legal exposure), high-frequency (the agent's main job), or high-uncertainty (new, recently changed, inconsistent, tool-dependent), and cover those before anything else.
   - Read [Coverage planning](references/coverage-planning.md) for the intake table, the per-goal checklist, the writing rules, and the launch readiness list. It is distilled from the Vapi testing guidance linked under Public Sources.

4. Design coverage before payloads.
   - Start with one smoke simulation for the core path, one or two required Boolean outcomes, chat transport, and one iteration.
   - For each primary goal, cover in this order: the core outcome, caller variation, missing or unclear information, tool or service failure recovery, guardrails, the safe alternative when the request cannot be met, handoff quality against the squad, a voice pass, and known production failures as regressions.
   - Test every high-impact rule in both directions: the case where the agent acts and the case where it must refuse or hold back. Verification that shares details after success needs a partner scenario that withholds them after failure.
   - Add regression simulations for repaired defects. Add separate edge cases for ambiguity, interruption, refusal, unavailable dependencies, failed tools, escalation, and handoffs.
   - Keep scenario intent, personality behavior, and evaluation criteria independent so each can be reused.
   - Name resources by behavior and expected outcome, not implementation details. Give each scenario and personality pair its own scenario name; the run view lists results by scenario name, so one scenario shared by several personalities reads as identical rows.
   - Report the plan as a coverage matrix, one row per requirement, with the scenarios, directions, and transports that cover it, before writing payloads.

5. Define the personality.
   - Prefer a suitable existing personality when available.
   - When creating one, provide a complete valid assistant configuration for the AI tester. Put stable temperament, speaking style, and caller behavior in its system prompt; put the situation-specific goal in the scenario.
   - Use the `create-assistant` skill to assemble or validate the personality's assistant configuration when available.
   - Configure voice and transcriber only when voice runs need them. Chat runs use the personality's model but skip its audio path.

6. Define the scenario and evaluations.
   - Write `instructions` as the AI tester's intent and facts. Describe the goal and constraints without scripting the target assistant's answer, and say when the caller should end the conversation.
   - Make each evaluation measure one observable outcome. Prefer descriptive Boolean outputs for pass/fail facts and numeric outputs for thresholds. Split "confirmed the time and offered alternatives" into two evaluations so a failure names one thing.
   - Judge recorded facts, not the target's claims: a booking passes when the tool result reports success, not when the assistant says the caller is all set. State in each description exactly what counts as success and allow different wording and paths.
   - Include at least one text-based required evaluation in every scenario that will run in chat mode. Audio-only evaluations are skipped in chat runs, and a scenario whose required evaluations are all skipped passes without asserting anything.
   - Provide either `structuredOutputId` or inline `structuredOutput`, never both. Inline outputs require `name` and a JSON `schema`.
   - Match the expected `value` type to the evaluated primitive. Use `=` or `!=` for Boolean and string; numeric types also support `>`, `<`, `>=`, and `<=`.
   - Keep important criteria `required: true`. Use optional criteria only for diagnostics that must not fail the simulation.
   - Object structured outputs may be evaluated through a primitive leaf using `path`. Do not compare an object or array directly.

7. Isolate side effects and runtime context.
   - Inspect the target's configured tools before every run. Mock any tool whose real execution could write data, contact people, spend money, or make the test non-deterministic.
   - Match each `toolMocks[].toolName` exactly. The mock `result` is always a string; encode JSON as a string when the target expects JSON-shaped output.
   - Assume every unmocked tool remains live in both chat and voice simulations.
   - Put test values for `{{variables}}` in `targetOverrides.variableValues`. Use synthetic data and keep secrets in Vapi credentials.
   - Configure `simulation.run.started` or `simulation.run.ended` hooks only when requested. Prefer `server.credentialId` to inline authorization headers.

8. Create and verify reusable resources.
   - Create in dependency order: personality and scenario, then simulation, then optional suite.
   - Require `201` for create operations. Verify returned IDs and the fields that define the test.
   - For updates, fetch the current resource first. Omit unrelated scalar fields and send the complete intended value for any array being changed; suite `simulationIds` and `targetAssignments` replace their existing arrays.
   - To extend an existing suite, fetch the suite and its scenarios and simulations, then diff by name: keep scenarios whose instructions and evaluations already match, update only the ones the user changed, create the rest, and send the suite's full `simulationIds` list with the retained IDs followed by the new ones. Remove an ID only when the user named that simulation.
   - Read every planned update back to the user before sending it. Changing an existing scenario's evaluations changes what production has been measured against; when the existing version is the one production relies on, add the new expectation under a new scenario name instead.
   - Re-fetch after update. Deleting a suite or other simulation resource is permanent; verify the exact ID and dependency impact first.

9. Run deliberately.
   - Prefer `vapi.webchat` for fast prompt, tool, and conversation-logic iteration.
   - Use `vapi.websocket` for speech recognition, voice output, interruptions, recordings, or final end-to-end validation. Run the primary conversations in voice mode before any launch claim, and do not rely on voice runs to prove digit accuracy for dates, phone numbers, or codes.
   - Start with one iteration. Increase iterations only to measure behavioral consistency after a single run is valid. Before a release, repeat the critical scenarios and compare the iterations instead of averaging them; one violation of a critical requirement means the behavior is unstable until it is explained.
   - Before sending the run, recap the target, simulations or suite, transport, iterations, tool mocks, and any remaining live side effects.
   - Create the run with `POST /eval/simulation/run` and require `201`. Return the run ID and dashboard `url` when present.

10. Monitor and diagnose results.
   - Poll `GET /eval/simulation/run/{id}` until `status` is `ended`; do not treat `queued` or `running` as success.
   - Fetch `GET /eval/simulation/run/{id}/item` and inspect every item. A passing group has items to evaluate, zero failed or canceled items, and every required evaluation passes.
   - Report actual versus expected values, extraction errors, skipped evaluations, failure reasons, transcript evidence, transport, and iteration number.
   - Diagnose the failing layer before changing the assistant: target runtime failure, scenario ambiguity, personality behavior, tool mock mismatch, structured-output extraction, or genuine assistant behavior.
   - Keep the evaluation stable when fixing the assistant. Change expected criteria only when the business requirement changed. Never loosen a criterion or rerun until green without explaining the failure.
   - Before calling a suite launch-ready, check the launch readiness list in [Coverage planning](references/coverage-planning.md): every primary goal covered end to end, high-impact rules covered in both directions, a failure path per goal, repeated passes on the critical scenarios, voice runs of the primary conversations, and a human who has read transcripts and listened to recordings.

11. Handle failures honestly.
   - On `400`, compare the request with the current schema and correct one unambiguous validation issue before at most one retry.
   - On `401` or `403`, stop for authentication or permission. On `404`, report the missing dependency. On `409` or concurrency errors, inspect `GET /eval/simulation/concurrency` and active runs. On `5xx`, report the service failure.
   - Cancel only queued or running groups or items. Never claim a run, cancellation, mutation, or pass succeeded until the corresponding API response is verified.

## API Implementation

Read [Simulation API Reference](references/api-reference.md) before producing REST code, making a live request, configuring hooks or mocks, or interpreting run results. Use direct REST unless the current official Vapi SDK documentation explicitly exposes the required simulation resource and method; never invent SDK method names.

## Output Contract

Return only the sections relevant to the request:

- Test strategy: target behavior, coverage, and why Simulation rather than Eval
- Coverage matrix: one row per requirement with its source, priority, and the scenarios, directions, and transports that cover it
- Resource plan: personality, scenario, evaluations, simulation, and suite
- Suite diff, when extending an existing suite: scenarios and simulations kept, updated, and created; suite IDs retained, added, and removed
- Side-effect review: mocked tools, live tools, hooks, variables, transport, iterations, and expected cost/concurrency impact
- Save-ready JSON or implementation code
- Created resource IDs and verified fields, when mutations succeeded
- Run ID, dashboard URL, status, item counts, and per-evaluation evidence, when a run was requested
- Failure diagnosis and the smallest recommended next change

## Public Sources

- [Testing voice agents](https://docs.vapi.ai/test/voice-testing)
- [Plan test coverage](https://docs.vapi.ai/test/plan-test-coverage)
- [Test outcomes with Simulations](https://docs.vapi.ai/test/simulations-best-practices)
- [Test decisions with Evals](https://docs.vapi.ai/test/evals-best-practices)
- [Run and maintain tests](https://docs.vapi.ai/test/run-and-maintain-tests)
- [Simulations overview](https://docs.vapi.ai/observability/simulations-overview)
- [Simulations quickstart](https://docs.vapi.ai/observability/simulations-quickstart)
- [Simulations advanced](https://docs.vapi.ai/observability/simulations-advanced)
- [Manage simulations](https://docs.vapi.ai/observability/simulations-manage)
- [Vapi API reference index and OpenAPI](https://docs.vapi.ai/llms.txt)

---
name: migration-simulations
description: Build and run Vapi Simulations that compare an assistant or squad on its current model with a copy on a new model, for a model migration (for example GPT-4.1 to gpt-5.6-terra or gpt-5.6-luna). Builds a Critical suite (core workflows, every ending, must-never-break rules) or an All suite (exhaustive) from a migration-flow-map output or from the prompt, mocks every tool, scores the team's own metrics (deflection, containment, booking rate and similar), runs both copies on the same scenarios and reports results side by side. Use with the model-migration skill. For general simulation work outside a migration, use the simulations skill.
license: MIT
compatibility: VAPI_API_KEY is required for live resource operations and runs. Internet access is recommended for current Vapi schema verification. Works best with the output of the migration-flow-map skill.
metadata:
  author: vapi
  version: "0.1"
---

# Migration simulations

Test a model change before it reaches callers. The same scenarios run against two copies of the assistant or squad, one on the current model and one on the new model, and the results are compared on the team's own metrics.

Simulations have five layers: a personality controls the AI caller, a scenario defines its goal, its tool mocks and its evaluations, a simulation pairs the two, a suite groups simulations, and a run executes them against an assistant or squad.

## Source and safety rules

- Use the Vapi documentation MCP when available. Otherwise use the bundled references and their public Vapi links. Verify payloads against the current public OpenAPI before sending them. Simulations use the `/eval/simulation` API family.
- Never print, request in chat, or embed API keys, provider secrets, credential values, private webhook URLs, or real customer data.
- **Never run simulations against the live assistant or squad.** Run against copies made by the `model-migration` skill (or by the user). A run on the live resource can trigger its real tools and webhooks.
- **Mock every tool.** Every tool the target can call gets a mock in every scenario, except tools of type `endCall` and static squad handoffs (`handoff` tools with fixed destinations), which act only inside Vapi. A custom function that happens to be named `end_call` is not exempt. A dynamic handoff asks your server for its destination, so it is not exempt either: point it at a test endpoint or make it static on both copies (the `model-migration` skill's squad reference covers this). An unmocked tool is live in both chat and voice: it can write data, text or call people, or spend money.
- **If the environment refuses a run request, stop and report it.** Never retry it through another tool or route.
- **Never start simulations on your own.** Building the suite never launches it. Running simulations is an external action that uses credits and concurrency, so every run (the smoke test, the full runs, reruns and voice runs) waits for the user's yes. Before each one, state how many conversations it will start (scenarios × runs per scenario × copies).
- Do not run, cancel, update, or delete resources unless the user asks. Draft configurations when changes were not requested.
- Resolve every ID from user input or the API. Never invent an ID.
- Use Simulations, not legacy Test Suites. Use Evals only for exact, turn-by-turn checks.

## Inputs

- The two targets: a baseline copy (current model) and a candidate copy (new model), identical apart from the model settings. The `model-migration` skill makes them and records their IDs in `copies.json`.
- `metrics.md`: the team's metrics and how each is measured. If it doesn't exist, build it with the user from [Metrics template](references/metrics-template.md) before writing any scenario.
- The org's API key, read from the `VAPI_API_KEY` environment variable. If it isn't set, ask the user to copy the private key for the org that owns the targets from https://dashboard.vapi.ai/org/api-keys, run `export VAPI_API_KEY=<key>` in their terminal, and restart the agent from that terminal.
- The flow map from `migration-flow-map`: `flow_tree.json`, `tool_catalog.json`, `scenario_list.json`. If there is none, step 3 builds the scenario list from the prompt and tools with the user.
- The suite level: Critical or All. See [Suite levels](references/levels.md).

## Procedure

1. **Agree the level and the size.**
   - Explain Critical and All in one or two lines each and recommend one (see [Suite levels](references/levels.md)). Default to Critical for a first comparison.
   - State the expected size: scenarios, runs per scenario, and the two copies.
   - Ask how many runs per scenario. One run per scenario is enough to find big differences. Two or three show which differences are consistent; the user decides the trade-off between cost and confidence.

2. **Inspect the targets and existing resources.**
   - Fetch both copies. Confirm they are identical except `model.model`, `model.reasoningEffort`, `model.serviceTier` and `model.promptCacheRetention` (plus `model.provider`, `model.fallbackModels` or `model.maxTokens` if the `model-migration` skill changed them). Compare explicitly: `model.messages` (the prompt), `model.tools` and `model.toolIds`, first message, voice, transcriber, hooks, variables, and for a squad every member, its `assistantOverrides` (where handoff tools often live) and the squad's `membersOverrides`. Stop if either copy has no prompt or no tools where the live assistant has them.
   - List the tools each copy can call, with their function names. These are the names every scenario must mock.
   - List existing personalities, scenarios, simulations and suites. Reuse a resource only when it clearly belongs to this migration (its name or the user says so). A resource with a similar name may belong to another test.

3. **Get the scenario list.**
   - With a flow map: take the entries for the chosen level from `scenario_list.json` (each entry is tagged `critical` or `all`).
   - Without a flow map: build the list with the user from the prompt and tools, following [Suite levels](references/levels.md). Read the prompt for its workflows, endings, rules and failure handling. Ask the user which paths are most common. Record where each entry came from.
   - Each entry needs: the path it covers, its traffic weight (or "unknown"), the caller's goal and facts, the tool answers for the situation, the expected ending, and the rules it checks.
   - For requirements gathered in plain language, [Coverage planning](references/coverage-planning.md) has the intake table and writing rules. [Requirements-driven generation](references/requirements-generation.md) describes Vapi's suite generator. It is not generally available: use it only if the user asks for it, generate against the baseline copy, review its output against the chosen level, and check that every generated scenario mocks every tool before any run.
   - Show the list to the user as a table (ID, path, weight, ending, rules) and agree it before writing payloads.

4. **Write scenarios, mocks and evaluations.**
   - Follow [Building scenarios from a flow map](references/from-flow-map.md). The essentials:
     - The caller's goal and facts, and when they hang up, in terms of something the assistant does. A caller hangs up once a transfer starts.
     - A mock for every tool except `endCall` tools and static handoffs, using the exact function name. One fixed result per tool per scenario: a situation that needs a different answer on a second call becomes its own scenario.
     - A required ending evaluation (a string with the flow map's endings as allowed values), required path and rule evaluations, and optional metric proxies from `metrics.md`.
     - Evaluations quote the words they grade, judge tool results rather than the assistant's claims, and tell the grader that tool calls and tool names written as text are not things the assistant said.
   - Every scenario that runs in chat needs at least one text-based required evaluation. Audio-only evaluations are skipped in chat, and a scenario whose required evaluations are all skipped passes without testing anything.
   - Provide either `structuredOutputId` or inline `structuredOutput`, never both. Inline outputs need `name` and a JSON `schema`. Match the expected `value` type to the output: `=` or `!=` for Boolean and string, any comparator for numbers.
   - Put test values for `{{variables}}` in `targetOverrides.variableValues`. Built-in caller values such as `{{customer.number}}` are not filled in a chat simulation: the placeholder stays as literal text, and the model can pass it to a tool as a value. Where the prompt or a tool uses one, set it in `targetOverrides.variableValues` (for example `"customer": {"number": "+15555550123"}`), and note the path difference. If the prompt reads the current date or time, pin it to a fixed test value so business-hours paths don't change with the hour the suite runs. If the team's server writes the date into the prompt text itself (not a `{{variable}}`), replace that line with the same fixed date on both copies, and say so in the report.

5. **Define the caller personality.**
   - One personality for the suite, plus extra ones only where a scenario needs a different temperament (upset, rushed, confused). See the personality rules in [Building scenarios from a flow map](references/from-flow-map.md#caller-personality).
   - A new personality needs a complete, valid assistant configuration, including an end-call tool so the caller can hang up. Use the `create-assistant` skill to assemble it when available. Add a voice and transcriber only to a personality used for voice runs (step 11).
   - Use the same personalities and the same caller model for both copies.
   - Read [Opening order](references/coverage-planning.md#12-opening-order-and-greeting-coverage): the personality's `firstMessageMode` decides who speaks first.

6. **Create and verify resources.**
   - Create in order: personalities and scenarios, then simulations, then one suite per level.
   - Require `201` for creates. Verify the returned IDs and the fields that define the test.
   - Name every resource with the migration and the scenario ID (`<assistant> migration MIG-007 ...`) so it can't be mistaken for another test. Names are limited: 80 characters for personalities, scenarios, simulations and suites, 40 for evaluation (structured output) names.
   - Keep a local record of every created ID (`sims_created.json` in the working folder, by default `~/vapi-migration/<slug>/`). Update or delete only what is recorded there.
   - Before any update, fetch the resource and read the planned change back to the user. Arrays you send replace the existing ones (`simulationIds`, `evaluations`, `toolMocks`, `hooks`).
   - Configure `simulation.run.started` or `simulation.run.ended` hooks only when the user asks for them, and prefer `server.credentialId` over inline authorization headers.
   - **Stop here.** Show what was built (the level, the number of scenarios, the mocks and the targets) and ask: "The suite is ready. Do you want me to start the smoke test (N conversations, baseline only, chat)? For the full runs afterwards, how many runs per scenario: 1, 2 or 3 (X, Y or Z conversations)?" Start nothing until the user says yes. If they want to review or change the suite first, do that and ask again.

7. **Run a smoke test.**
   - With the user's yes, run 2 or 3 scenarios once, in chat (`vapi.webchat`), against the baseline copy only.
   - Read every transcript. Check that the caller behaves as written, every tool call hit a mock (no live calls), the evaluations grade what they should, and nothing hit the turn limit.
   - Fix test problems now. A test problem found after the full run costs both runs.

8. **Run both copies.**
   - Recap before sending: the suite, both targets, transport, runs per scenario, the mocks, any tool left unmocked, and the number of conversations. Ask whether to start the full runs, and wait for the user's yes even if they approved the smoke test.
   - Run the same suite, with the same settings, against the baseline and the candidate. Use chat for behavior; it is faster and cheaper, and it is where the comparison happens.
   - Create each run with `POST /eval/simulation/run` and require `201`. Return the run IDs and dashboard URLs. A run runs each listed simulation once even if you list it twice; for more conversations per scenario, raise `iterations` or start another run.
   - For large suites, keep the number of conversations in flight moderate (check `GET /eval/simulation/concurrency`), so one run doesn't block others in the org.

9. **Collect and check results.**
   - Poll `GET /eval/simulation/run/{id}` until `status` is `ended`. Do not judge `queued` or `running`.
   - Fetch every item (`GET /eval/simulation/run/{id}/item`) 100 at a time and deduplicate by item ID: page order isn't stable, and one request for a whole run can stall for a long time. Save them in the working folder as `sim_results/<baseline|candidate>/<run-id>.json`. The `model-migration` skill reads them from there.
   - Separate execution failures (an item that errored, timed out or was canceled) from evaluation failures. An execution failure is not a model result; rerun those items before comparing. A conversation that hangs can come back as `failed` with no `failureReason` and empty evaluation results, about 20 minutes later, and `itemCounts.failed` counts it with evaluation failures: treat an item with no evaluation results as an execution failure.
   - Set aside test artifacts before comparing: the caller ended the chat before the assistant spoke or before the assistant's last turn, the conversation hit the turn limit after a transfer, or a tool call reached a tool with no mock.

10. **Report side by side.**
    - Compare the two copies on the same scenarios: only scenarios that produced a graded result on both copies.
    - Lead with the team's metrics from `metrics.md`, computed the same way for both copies. Compute rates from each item's actual ending (the ending evaluation's extracted value), not from whether the evaluation passed. With flow-map weights: weighted rate = sum of (weight × outcome) divided by the sum of weights, over scenarios with weight above 0 graded on both copies; report weight-0 scenarios separately. Then rule checks, then every-check pass rate.
    - With a flow map, also report each copy's rates per intent and per ending (the tree's nodes) and name the weakest, and list the checks that fail on every run. Read those transcripts before blaming the model: they are often test problems.
    - List the scenarios where the two copies differ most, with the transcript evidence for each.
    - Say which differences could be run-to-run noise. One conversation is worth 100 / (scenarios × runs) points, so on a 20-scenario suite run once, one conversation is 5 points. A difference is real only when the same scenario fails in most runs on one copy and passes in most runs on the other.
    - Hand the results to the `model-migration` skill, which explains the differences and suggests fixes.

11. **Voice check (optional, after chat).**
    - With the user's yes, run a small set (5 to 20 core scenarios) in voice (`vapi.websocket`) on each copy, with a personality that has a voice and a transcriber. For each item, fetch its `callId` with `GET /call/{id}` and read turn latency (`artifact.performanceMetrics`), `cost`, and duration (`endedAt` minus `startedAt`). Listen to a few recordings to hear how the new model sounds.
    - Do not judge behavior on a few voice runs; differences there are mostly noise. Do not rely on voice runs to prove digit accuracy.

12. **Handle failures honestly.**
    - On `400`, compare the request with the current schema and fix one clear validation issue before at most one retry.
    - On `401` or `403`, stop for authentication or permission. On `404`, report the missing dependency. On `409` or concurrency errors, check `GET /eval/simulation/concurrency` and active runs. On `5xx`, report the service failure.
    - Cancel only queued or running runs or items. Never claim a run, cancellation, change or pass succeeded until the API response confirms it.
    - Keep evaluations stable while comparing. Change one only when it is wrong for both copies, then rerun both. Never loosen a check or rerun until green without explaining the failure.

## API implementation

Read [Simulation API reference](references/api-reference.md) before writing REST code, making a live request, configuring mocks, or reading run results. Use direct REST unless the current official Vapi SDK documentation exposes the exact simulation method; never invent SDK method names.

## Output contract

Return only the sections the request needs:

- Level and size: Critical or All, scenarios, runs per scenario, conversations per copy
- Scenario table: ID, path, traffic weight, expected ending, rules checked, source
- Mock review: every target tool and its mock, and any tool left unmocked with the reason
- Created resource IDs, from `sims_created.json`
- Run IDs, dashboard URLs, status and item counts for each copy
- Side-by-side results: the team's metrics first, then rule checks and every-check pass rate, on the same scenarios
- The scenarios with the largest differences, with transcript evidence
- Execution failures and test artifacts set aside, with counts

## Public sources

- [Simulations overview](https://docs.vapi.ai/observability/simulations-overview)
- [Simulations quickstart](https://docs.vapi.ai/observability/simulations-quickstart)
- [Simulations advanced](https://docs.vapi.ai/observability/simulations-advanced)
- [Manage simulations](https://docs.vapi.ai/observability/simulations-manage)
- [Test outcomes with Simulations](https://docs.vapi.ai/test/simulations-best-practices)
- [Plan test coverage](https://docs.vapi.ai/test/plan-test-coverage)
- [Run and maintain tests](https://docs.vapi.ai/test/run-and-maintain-tests)
- [Vapi API reference index and OpenAPI](https://docs.vapi.ai/llms.txt)

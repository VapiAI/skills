---
name: migration-flow-map
description: Map how a Vapi assistant or squad is used in production before changing its model. Reads a sample of its real calls through the Vapi API, builds a traffic-weighted flow tree (intent, path, ending), a tool catalog of every tool and the answers it returns, production baselines for the team's own metrics (deflection, containment, transfer or booking rate), and a scenario list tagged Critical or All for the migration-simulations skill. When call content can't be read (zero data retention, compliance limits, no access) or traffic is too thin, it builds the same files from the system prompt and tool definitions instead. Use before a model migration (for example GPT-4.1 to gpt-5.6-terra or gpt-5.6-luna), or when the user wants to know what callers actually do with an assistant. Read-only; never changes the assistant.
license: MIT
compatibility: Requires VAPI_API_KEY with read access to the org's assistants, squads and tools; call reading also needs access to calls with transcripts, otherwise the skill runs from the prompt alone. Reading many calls works best in an agent that supports sub-agents.
metadata:
  author: vapi
  version: "0.1"
---

# Migration flow map

Before testing a new model, find out what the assistant really does: which reasons people call for, which paths those calls take, how they end, which tools answer what, and how the team's metrics look today. The result is the input to `migration-simulations`, so the tests reflect real traffic instead of guesses.

When production calls can't be used, the skill falls back to the system prompt: see [Prompt-only mode](#prompt-only-mode).

This skill is read-only. It never creates, updates or deletes anything in Vapi.

## Safety and privacy rules

- **Call data is personal data.** Create the working folder outside any git repository (`~/vapi-migration/<slug>/` by default). If the user wants it inside a repository, add it to `.gitignore` first and confirm with `git check-ignore`. Raw API responses and configuration snapshots go in its `raw/` folder, which is deleted when the migration is done. Every other output holds no names, phone numbers, emails, addresses, account numbers or dates of birth: in text taken from transcripts or tool results, mask digit runs of 3 or more and use synthetic values of the same format.
- Never paste transcripts into chat, tickets or shared documents. Quote at most a short, masked phrase when a finding needs evidence.
- If the account has compliance constraints (HIPAA, PCI or similar), ask the user whether call content may be read, and by which tools, before pulling transcripts.
- Never print or store API keys, credential values, server URLs or webhook secrets in any output.
- The live prompt and the team's rules are the answer key. What the real assistant did on a call is evidence of the caller's situation, not of what it should have done.

## Inputs

- The assistant ID or squad ID. For a transient assistant or squad (sent per call by the team's server through `assistant-request`, or inline when the call is created), there is no ID to fetch: ask the user to paste the full configuration JSON or give a file path, and to say which phone number or traffic it serves.
- The team's metrics, or time with the user to define them (step 1).
- The sample size: how many calls to read. This is the one cost setting. See [Reading call data](references/call-data.md#sampling).

## Procedure

1. **Agree the metrics.**
   - Ask the user which metrics they track for this assistant and exactly how production measures each one: deflection or containment, satisfaction scores, transfer, booking or payment rate, handle time, and any rule that must never break.
   - If `metrics.md` already exists in the working folder (the `model-migration` skill writes it in its step 1), confirm it with the user instead of asking again. Otherwise fill it from [Metrics template](references/metrics-template.md). Ask; don't guess. A metric the team doesn't track doesn't belong in the file.
   - Ask whether post-call analysis or structured outputs already capture any of them (`analysis`, `artifact.structuredOutputs` on each call).

2. **Snapshot the configuration.**
   - Fetch the assistant (`GET /assistant/{id}`), or the squad (`GET /squad/{id}`) and every member assistant. For a transient configuration, use the one the user provided, and compare it with the `assistant` or `squad` object on one recent call to confirm it's the version in production. Resolve every tool (`GET /tool/{id}`).
   - Save the responses in `raw/config_snapshot/`, with server URLs, headers and credential values replaced by `<redacted>`. Record the prompt, the first message, every tool's function name and description, handoff destinations, and every `{{variable}}` the prompt uses.
   - **Decide the source.** Use [Prompt-only mode](#prompt-only-mode) instead of steps 3 to 5 when any of these holds, and tell the user which one:
     - The org has zero data retention, or the calls are stored without transcripts or messages (check one recent call).
     - The user says call content may not be read (step 1 and the compliance rule above).
     - The key can't list the org's calls.
     - Fewer than about 50 calls ended in a conversation in the window.

3. **Pull and sample calls.**
   - Agree the window (default: the last 4 weeks, or since the current prompt version went live) and the sample size (default about 300 calls; more for busy assistants and squads).
   - List calls with `GET /call` and sample them evenly across days, following [Reading call data](references/call-data.md). For squads, list by each of the squad's phone numbers and keep calls with the squad's ID.
   - Keep only calls that ended and reached a conversation. Count what you dropped and why.
   - For each sampled call, write one structured row to `call_records.jsonl`: ended reason, duration, the ordered tool path, failed tool calls, transfers, handoffs and the members reached, cost. No transcript text.
   - Tell the user the window, the calls available, the sample size and the drops before reading.

4. **Compute metric baselines.**
   - For each metric in `metrics.md`, compute its value over the sample the same way production does, as far as call data allows (for example: share of calls with no transfer; share of calls whose structured output marks the issue resolved).
   - Write `metric_baselines.md`: each value, the number of calls behind it, the exact rule used, and anything that couldn't be computed from calls (callbacks, survey scores collected elsewhere). Compare with the team's own number if they gave one; a big gap means the definitions differ, so resolve it with the user before going on.

5. **Read calls into labels.**
   - Follow [Reading calls into a flow tree](references/reading.md): a pilot of about 50 calls to build the category list (intents, path steps, endings, caller traits), agreed with the user, then the rest of the sample in batches with the fixed list.
   - Align the endings with the metrics. If the team counts deflection as "no transfer and no callback", the endings must separate those cases.
   - Stop when new batches stop adding categories (the stopping rule is in the reading reference).

6. **Build the flow tree.**
   - Intent > path > ending, each node with its share of traffic and example call IDs. For squads, also the share of calls that reached each member.
   - List the situations the prompt handles that no sampled call reached (`prompt_only`), with exact quotes.
   - Write `flow_tree.json` (format in [Output files](references/outputs.md#flow_treejson)) and walk the user through the top of the tree.

7. **Build the tool catalog.**
   - For every tool: its function name (what a mock must match), how often it is called, the arguments the assistant sends, every kind of answer it returns with its share and one synthetic example in the real format, and rules about when its answer changes (for example "returns not found until the caller is verified").
   - Include tools that were never called in the sample. They are candidates for removal before migration.
   - Write `tool_catalog.json` (format in [Output files](references/outputs.md#tool_catalogjson)). Check that no real value leaked into an example.

8. **Write the scenario list.**
   - Turn the tree, the prompt-only situations, the tool catalog and the must-never-break rules into scenarios, each tagged `critical` or `all`:
     - **Critical:** the core paths, highest traffic first, until about 80% of conversations are covered or the next path is under about 3% of traffic; every ending at least once; each must-never-break rule in both directions (one scenario where the assistant must act, one where it must hold back); one tool failure on the main path; one request for a human; one upset caller. Usually 10 to 25 scenarios.
     - **All:** everything else worth testing: smaller paths down to about 0.5% of traffic, variants of big paths, every meaningful tool answer and state, each compliance situation at least twice, prompt-only situations (weight 0), language variants, and more upset callers.
   - Each scenario has: the path, its traffic weight, the caller's goal and synthetic facts, when the caller hangs up, the tool answer kind for every tool it can reach, the expected ending, the rules it checks with their quoted source, and the metrics it informs.
   - Expected endings and rules come from the prompt and the team's rules, never from what the assistant did on the source call.
   - Write `scenario_list.json` (format in [Output files](references/outputs.md#scenario_listjson)).

9. **Collect questions for the owner.**
   - While reading the prompt and calls, note contradictions (two rules that disagree), situations the prompt doesn't cover, and tools the prompt never mentions. These show up later as false model differences if nobody resolves them.
   - Write `owner_questions.md`, one question per item, each with the prompt quote and how often the situation occurred in the sample.

10. **Report and hand over.**
    - Write `flow_map_report.md`: window and sample, the top of the tree, metric baselines, tool catalog highlights (never-called tools, common failures), prompt-only situations, the Critical and All scenario counts, and the owner questions.
    - Hand the folder to `migration-simulations`. Remind the user to delete `raw/` when the migration is done.

## Prompt-only mode

The fallback when production calls can't be read or are too few. It produces the same files from the system prompt (every member's, for a squad) and the tool definitions, so `migration-simulations` works the same way. What changes:

- **Skip steps 3 to 5.** No calls are listed, sampled or read, and nothing is saved under `raw/` except the redacted configuration.
- **Metric baselines.** Write `metric_baselines.md` saying there is no production baseline and why. If the team gives its own current numbers, record them with their source.
- **Flow tree.** Build it from the workflows the prompt defines: each reason to call the prompt handles, the steps it lays out, and the endings it allows. `share` is `null` everywhere, `example_calls` is empty, and the tree carries `"source": "prompt"`.
- **Tool catalog.** Take each tool's arguments and answer kinds from its definition, its description and what the prompt says about its results. Ask the user for one example response per tool in the real format, with synthetic values. Where none is available, mark the example `"example_source": "inferred"` and list the tool in `owner_questions.md`, because a mock that doesn't match the real format tests the wrong thing.
- **Scenario list.** Critical covers every workflow the prompt defines, every ending once, each must-never-break rule in both directions, one tool failure, one request for a human and one upset caller. All adds the variants and the rarer branches. `weight` is `null` on every scenario, so rates are reported unweighted.
- **Report.** `flow_map_report.md` says prompt-only mode was used and why, so nobody reads the tree as traffic.

## Output contract

- `metrics.md` and `metric_baselines.md`
- `flow_tree.json`, `tool_catalog.json`, `scenario_list.json` (formats in [Output files](references/outputs.md)), built from calls or, in prompt-only mode, from the prompt
- `owner_questions.md` and `flow_map_report.md`
- Supporting files: `call_records.jsonl`, `labels.jsonl`, `categories.md` (and, in `raw/`, the redacted `config_snapshot/` and the raw calls)
- A short summary for the user: sample size, top intents with shares, metric baselines, Critical and All counts, open owner questions

## Public sources

- [Vapi API reference index and OpenAPI](https://docs.vapi.ai/llms.txt)
- [Call object and endedReason values](https://docs.vapi.ai/api-reference/calls/get)
- [Squads](https://docs.vapi.ai/squads)
- [Plan test coverage](https://docs.vapi.ai/test/plan-test-coverage)

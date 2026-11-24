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

It always uses both the system prompt and production calls. When calls can't be read, it uses the prompt alone and produces the same files; each step says what changes.

This skill is read-only. It never creates, updates or deletes anything in Vapi.

## Safety and privacy rules

- **Call data is personal data.** Create the working folder outside any git repository (`~/vapi-migration/<slug>/` by default). If the user wants it inside a repository, add it to `.gitignore` first and confirm with `git check-ignore`. Raw API responses and configuration snapshots go in its `raw/` folder, which is deleted when the migration is done. Every other output holds no names, phone numbers, emails, addresses, account numbers or dates of birth: in text taken from transcripts or tool results, mask digit runs of 3 or more and use synthetic values of the same format.
- Never paste transcripts into chat, tickets or shared documents. Quote at most a short, masked phrase when a finding needs evidence.
- If the account has compliance constraints (HIPAA, PCI or similar), ask the user whether call content may be read, and by which tools, before pulling transcripts.
- Never print or store API keys, credential values, server URLs or webhook secrets in any output.
- The live prompt and the team's rules are the answer key. What the real assistant did on a call is evidence of the caller's situation, not of what it should have done.

## Inputs

- The assistant ID or squad ID. For a transient assistant or squad (sent per call by the team's server through `assistant-request`, or inline when the call is created), there is no ID to fetch: ask the user to paste the full configuration JSON or give a file path. A transient configuration is mapped from the configuration alone (step 2).
- The team's metrics, or time with the user to define them (step 1).
- The sample size: how many calls to read. This is the one cost setting. See [Reading call data](references/call-data.md#sampling).

## Procedure

1. **Agree the metrics.**
   - Ask the user which metrics they track for this assistant and exactly how production measures each one: deflection or containment, satisfaction scores, transfer, booking or payment rate, handle time, and any rule that must never break.
   - If `metrics.md` already exists in the working folder (the `model-migration` skill writes it in its step 1), confirm it with the user instead of asking again. Otherwise fill it from [Metrics template](references/metrics-template.md). Ask; don't guess. A metric the team doesn't track doesn't belong in the file.
   - Ask whether post-call analysis or structured outputs already capture any of them (`analysis`, `artifact.structuredOutputs` on each call).

2. **Snapshot the configuration.**
   - Fetch the assistant (`GET /assistant/{id}`), or the squad (`GET /squad/{id}`) and every member assistant, including the squad's `membersOverrides` (hooks, voice and transcriber settings) and each member's handoff tools (`assistantOverrides`). For a transient configuration, use the one the user provided. Resolve every tool (`GET /tool/{id}`).
   - Save the responses in `raw/config_snapshot/`, with server URLs, headers and credential values replaced by `<redacted>`. Record the prompt, the first message, every tool's function name and description, handoff destinations, and every `{{variable}}` the prompt uses.
   - **Check whether calls can be read.** Skip steps 4 and 6 (pulling and reading calls) when any of these holds, and tell the user which one:
     - The assistant or squad is transient. Its calls carry no assistant or squad ID, so they can't be reliably matched to the configuration the user gave.
     - The org has zero data retention, or the calls are stored without transcripts or messages (check one recent call).
     - The user says call content may not be read (step 1 and the compliance rule above).
     - The key can't list the org's calls.
     - Fewer than about 50 calls ended in a conversation in the window.

3. **Draft the category list and the prompt's branches.**
   - Read the whole system prompt (every member's, for a squad, and the squad's own hooks) and the tool definitions. Draft the category list from it: the reasons to call (intents), the named steps, and the endings the prompt allows. Endings must separate what the team's metrics count (for deflection, an ending with a person apart from one without). Write `categories.md`.
   - List the branches: each situation the prompt tells the assistant to handle differently, with the exact quote, what the caller would say or do to reach it, what the prompt says to do, and the intent, steps and ending it maps to (names from the category list). Group the sentences that describe one handling into one branch. A rule repeated by several members is one branch for all of them.
   - General rules that apply on every turn (disclosures, tone, never-do lists) are rules, not branches: list them separately; they become checks.
   - Check the list: every quote appears word for word in the prompt, and every intent, step and ending exists in the category list. Follow [Branches the prompt defines](references/reading.md#branches-the-prompt-defines).
   - Write `prompt_branches.json` (format in [Output files](references/outputs.md#prompt_branchesjson)) and show the user the category list and the branch counts per member.

4. **Pull and sample calls.**
   - Agree the window (default: the last 4 weeks, or since the current prompt version went live) and the sample size (default about 300 calls; more for busy assistants and squads).
   - List calls with `GET /call` and sample them evenly across days, following [Reading call data](references/call-data.md). For squads, list by each of the squad's phone numbers and keep calls with the squad's ID.
   - Keep only calls that ended and reached a conversation. Count what you dropped and why.
   - For each sampled call, write one structured row to `call_records.jsonl`: ended reason, duration, the ordered tool path, failed tool calls, transfers, handoffs and the members reached, cost. No transcript text.
   - Tell the user the window, the calls available, the sample size and the drops before reading.

5. **Compute metric baselines.**
   - For each metric in `metrics.md`, compute its value over the sample the same way production does, as far as call data allows (for example: share of calls with no transfer; share of calls whose structured output marks the issue resolved).
   - Without calls, write in `metric_baselines.md` that there is no production baseline and why, and record the team's own current numbers if they give them.
   - Write `metric_baselines.md`: each value, the number of calls behind it, the exact rule used, and anything that couldn't be computed from calls (callbacks, survey scores collected elsewhere). Also record the share of calls whose ending a simulation can't produce (the caller hung up partway, a silence timeout). Simulated rates will differ from production by about that much, so the two copies are compared with each other, not with this baseline. Compare with the team's own number if they gave one; a big gap means the definitions differ, so resolve it with the user before going on.

6. **Read calls into labels.**
   - Follow [Reading calls into a flow tree](references/reading.md): a pilot of about 50 calls that refines the category list drafted from the prompt (adding what callers actually do, and caller traits), agreed with the user, then the rest of the sample in batches with the fixed list.
   - Align the endings with the metrics. If the team counts deflection as "no transfer and no callback", the endings must separate those cases.
   - Name path steps after the branch IDs from `prompt_branches.json` where they match, so the tree maps onto the branch list.
   - Stop when new batches stop adding categories (the stopping rule is in the reading reference).

7. **Build the flow tree.**
   - Intent > path > ending, each node with its share of traffic and example call IDs. For squads, also the share of calls that reached each member.
   - Map the tree onto `prompt_branches.json`: mark each branch with the share of calls that reached it, or `prompt_only` if no sampled call did. A path that matches no branch is a situation the prompt doesn't cover; add it to the owner questions.
   - Without calls, build the tree from the category list and the branches: each intent the prompt handles, its steps and its endings. Every share is `null`, every branch is `prompt_only`, and the tree carries `"source": "prompt"` so nobody reads it as traffic.
   - Write `flow_tree.json` (format in [Output files](references/outputs.md#flow_treejson)) and walk the user through the top of the tree.

8. **Build the tool catalog.**
   - For every tool: its function name (what a mock must match), how often it is called, the arguments the assistant sends, every kind of answer it returns with its share and one synthetic example in the real format, and rules about when its answer changes (for example "returns not found until the caller is verified").
   - Include tools that were never called in the sample. They are candidates for removal before migration.
   - Without calls, take each tool's arguments and answer kinds from its definition, its description and what the prompt says about its results. Ask the user for one example response per tool in the real format, with synthetic values. Where none is available, mark the example `"example_source": "inferred"` and list the tool in `owner_questions.md`, because a mock that doesn't match the real format tests the wrong thing.
   - Write `tool_catalog.json` (format in [Output files](references/outputs.md#tool_catalogjson)). Check that no real value leaked into an example.

9. **Write the scenario list.**
   - Follow [Planning the scenario list](references/scenario-plan.md): the admission test, rules as checks rather than scenarios, the Critical and All coverage rules, merging repeated tests, setting aside what the prompt doesn't cover, and the checks before the gate.
   - Each scenario has: its level and kind, the reason it was admitted, the path, its traffic weight, the caller's goal and synthetic facts, when the caller hangs up, the tool answer kind for every tool it can reach, the expected ending, the rules it checks with their quoted source, the metrics it informs, and the branches it covers.
   - Expected endings and rules come from the prompt and the team's rules, never from what the assistant did on the source call.
   - Without calls, every `weight` is `null` (rates are reported unweighted) and the routes are the intents the prompt defines.
   - Write `scenario_list.json` (format in [Output files](references/outputs.md#scenario_listjson)). **Gate:** the user locks the list (its size, merges and set-aside scenarios) before `migration-simulations` builds anything.

10. **Collect questions for the owner.**
   - While reading the prompt and calls, note contradictions (two rules that disagree), situations the prompt doesn't cover, and tools the prompt never mentions. These show up later as false model differences if nobody resolves them.
   - Write `owner_questions.md`, one question per item, each with the prompt quote and how often the situation occurred in the sample.

11. **Report and hand over.**
    - Write `flow_map_report.md`: whether calls were read (and if not, why), window and sample, the top of the tree, metric baselines, tool catalog highlights (never-called tools, common failures), prompt-only situations, the Critical and All scenario counts, and the owner questions.
    - Hand the folder to `migration-simulations`. Remind the user to delete `raw/` when the migration is done.

## Output contract

- `metrics.md` and `metric_baselines.md`
- `prompt_branches.json`, `flow_tree.json`, `tool_catalog.json`, `scenario_list.json` (formats in [Output files](references/outputs.md)), built from the prompt and calls, or from the prompt alone when calls can't be read
- `owner_questions.md` and `flow_map_report.md`
- Supporting files: `categories.md`, plus `call_records.jsonl` and `labels.jsonl` when calls were read (and, in `raw/`, the redacted `config_snapshot/` and the raw calls)
- A short summary for the user: sample size, top intents with shares, metric baselines, Critical and All counts, open owner questions

## Public sources

- [Vapi API reference index and OpenAPI](https://docs.vapi.ai/llms.txt)
- [Call object and endedReason values](https://docs.vapi.ai/api-reference/calls/get)
- [Squads](https://docs.vapi.ai/squads)
- [Plan test coverage](https://docs.vapi.ai/test/plan-test-coverage)

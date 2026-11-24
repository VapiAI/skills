---
name: model-migration
description: Move a Vapi assistant or squad from one model to another, for example GPT-4.1 to gpt-5.6-terra or gpt-5.6-luna, without losing the behavior and metrics the team relies on. Reviews the prompt and tools for known migration risks, makes a baseline copy and a candidate copy (never edits the live one), tests both with the migration-simulations skill on the same scenarios, explains each difference using documented model tendencies, applies wording-only fixes, checks voice latency and cost, and plans a gradual rollout tracked on the team's own metrics. Use when the user wants to migrate, switch or upgrade an assistant's model, compare a new model with the current one, or prepare for a model retirement.
license: MIT
compatibility: Requires VAPI_API_KEY for an org where copies of the assistant may be created. Uses the migration-flow-map and migration-simulations skills for mapping and testing.
metadata:
  author: vapi
  version: "0.1"
---

# Model migration

A model change is measured, not guessed: build a test set, measure the current setup on it, measure the new model on the same set, and change only what the differences show. Expect a few rounds of fixes before the new model holds the team's metrics. That iteration happens on copies, before any caller hears the new model.

Before starting, read [Model tendencies](references/model-tendencies.md). It describes how Terra and Luna behave differently from GPT-4.1, and most of this procedure exists to catch those differences.

## Safety rules

- **Never edit the live assistant or squad.** Every change goes to a copy. Moving the change to production is the user's decision, after the report.
- **Copies must not reach production systems.** Copies take no calls (no phone number attached). On both copies, remove `server` and any hooks whose actions call a server or a tool, and turn off custom-storage uploads (`artifactPlan` options that use custom storage) and `observabilityPlan`, or point each at a test destination. Simulations mock every tool (see `migration-simulations`).
- **Copies share saved tools with the live assistant.** A copy keeps the same `model.toolIds`, so editing one of those tools (`PATCH /tool/{id}`) changes production. Never edit a tool a live assistant uses. To change a tool's name, description or parameters, create a new tool from the fetched one (`POST /tool`), point only the copy at it, and record it in `copies.json`.
- **Keep working files out of the customer's repository.** Create the working folder outside any git repository (for example `~/vapi-migration/<slug>/`). If the user wants it inside a repo, add the folder to `.gitignore` first and confirm with `git check-ignore`.
- Running simulations uses credits and concurrency. State how many conversations a run will start and get the user's yes before each run.
- Prompt changes are wording only. Never add a workflow, step or rule the team's prompt doesn't already define. Where two rules disagree or a situation is uncovered, ask the owner; don't pick a side.
- Never print or store API keys, credential values or caller data.

## Inputs

- The assistant ID or squad ID, and the org's API key.
- The new model. If the user hasn't chosen, see [Choosing between Terra and Luna](#choosing-between-terra-and-luna).
- The team's metrics and how they measure them, or time to define them (step 1).

## Procedure

### 1. Define what success means

Ask which metrics the team tracks for this assistant and how production measures each one: deflection or containment, satisfaction scores, transfer, booking or payment rate, handle time, and any rule that must never break. Fill `metrics.md` in the working folder from [Metrics template](references/metrics-template.md). Every comparison and the rollout report these first.

### 2. Map how the assistant is used

Run the `migration-flow-map` skill. It reads a sample of production calls and produces the flow tree, the tool catalog, production baselines for the metrics, the Critical and All scenario list, and questions for the owner.

For a small or brand-new assistant with little traffic, skip it and build the scenario list from the prompt in `migration-simulations` step 3.

### 3. Review the prompt and tools before testing

Without running anything, check the prompt and tools against [Fixes: before you test](references/fixes.md#before-you-test-prompt-and-tool-hygiene) and write `review.md`. Each finding names the line or tool and the risk:

- tool names in the prompt that don't exactly match the real tool names;
- tools the prompt never uses or forbids, and tool or parameter descriptions that disagree with the prompt;
- per-call values early in the prompt (they defeat prompt caching);
- rules that forbid acknowledgments or cap replies very short;
- example lines that will become scripts, and closing steps that live in a separate section from the branches that need them;
- contradictions and uncovered situations (add them to `owner_questions.md`).

Show the review to the user and resolve the owner questions before testing where possible: an unresolved contradiction shows up later as a false model difference.

Some findings are defects on any model (a tool name that doesn't match). Fix those on both copies so the comparison stays fair (through new tools where a tool changes, never by editing a shared one), and tell the user they also apply to the live assistant.

### 4. Make two copies

- **Baseline:** a copy of the live assistant (or squad) on the current model, unchanged apart from the safety changes above.
- **Candidate:** a second copy of the baseline with only these fields changed inside its existing `model` object. Keep every other `model` field as it is (`messages`, `tools`, `toolIds`, `knowledgeBase` and the rest): the prompt and tools live inside `model`, so replacing the whole object deletes them. The recommended settings for Terra and Luna are low reasoning and fast mode:

  ```json
  { "model": "gpt-5.6-luna", "reasoningEffort": "low", "serviceTier": "fast", "promptCacheRetention": "24h" }
  ```

  Use `gpt-5.6-terra` for Terra, and also set `"provider": "openai"` if the current model is from another provider. See [Luna](references/luna.md) and [Terra](references/terra.md) for what each setting does.
- Check `model.fallbackModels` on the candidate. Remove GPT-4.1 entries: they hide candidate failures during tests and stop working when GPT-4.1 is retired. Decide the production fallback explicitly before rollout.
- Check `model.maxTokens` on the candidate. A low value carried over from GPT-4.1 can cut replies short or leave them empty on reasoning models.
- To copy an assistant: `GET /assistant/{id}`, remove the read-only fields (`id`, `orgId`, `createdAt`, `updatedAt`, `latestVersion`, `modelDeprecations`, and any other field the create endpoint rejects), name it clearly (`<name> - migration baseline`, `<name> - migration candidate`), and `POST /assistant`. Require `201`.
- For a squad, copy every member and build two squads from the copies. Squad members keep their `name` unchanged, because handoffs refer to members by name; tell the copies apart by the squad name and `copies.json`. See [Migrating a squad](references/squads.md).
- Fetch both copies and compare them field by field. They must be identical except `model.model`, `model.reasoningEffort`, `model.serviceTier` and `model.promptCacheRetention`, plus `model.provider`, `model.fallbackModels` and `model.maxTokens` where you changed them above. Compare `model.messages`, `model.tools` and `model.toolIds`, the first message, voice, transcriber, hooks and variables explicitly. Record every created ID (assistants, squads, new tools) in `copies.json`.
- Test the candidate on the **unchanged prompt first**. The first comparison shows what the model does on its own; prompt changes come after.
- If the current model can no longer run (already retired), skip the baseline copy and compare the candidate with the production baselines from `migration-flow-map`.

### 5. Test both copies

Run the `migration-simulations` skill with both copies as targets:

- Agree the level with the user: **Critical** for a first comparison, **All** before moving full traffic.
- Agree the runs per scenario: one finds big differences; two or three show which ones are consistent.
- Chat transport for behavior. Voice comes in step 8.

`migration-simulations` builds the suite and then stops to ask whether to start the simulations. Don't start any run, here or in later steps, without the user's yes.

### 6. Compare and explain the differences

Use the results `migration-simulations` saved in `sim_results/` and [Comparing the two copies](references/comparison.md):

- Compare only scenarios graded on both copies. Lead with the team's metrics, then must-never-break rules, then rule checks and behavior signals.
- Read the transcripts behind the largest differences and file each as the test, the prompt, the model, or the old model breaking a rule the new one keeps.
- Explain model differences with [Model tendencies](references/model-tendencies.md), so the user knows whether a difference is a known trait or something specific to this assistant.

Scenarios are shared by both copies: fix a test problem once in the scenario, then rerun both copies before changing the candidate's prompt.

### 7. Fix and rerun

- Pick fixes by symptom from [Fixes](references/fixes.md), plus [Luna](references/luna.md) or [Terra](references/terra.md). Each is a wording, tool-list or setting change.
- Plan the tone work from the start: the new models sound more neutral than GPT-4.1, and callers notice. Add upset-caller scenarios and tone proxy checks to the suite before the first run, and apply tone fixes after the first comparison shows the gap.
- Apply all chosen fixes to a new candidate version (keep the previous one for comparison), ask the user before rerunning it on the same suite, and compare again.
- Stop when the candidate holds the team's metrics and the must-never-break rules within noise, or after about three rounds with every remaining difference explained.

### 8. Check voice

With the user's yes, run 5 to 20 core scenarios in voice on the baseline and the final candidate (the caller personality needs a voice and a transcriber for voice runs). For each run item, take its `callId`, fetch `GET /call/{id}`, and read turn latency (`artifact.performanceMetrics`), `cost`, and duration (`endedAt` minus `startedAt`). Listen to a few recordings for pace, markdown read aloud and silences around tool calls. Check what chat can't show: [What simulations don't show](references/what-sims-cant-test.md).

### 9. Report and plan the rollout

Write `report.md` in the working folder:

- The team's metrics on both copies, with the production baselines.
- Every remaining difference, its class and evidence, and whether it matches a known model tendency.
- The exact changes in the candidate: model block, prompt diff, tool changes.
- Voice latency and cost per minute.
- What the tests couldn't cover and the manual checks to run.
- A rollout plan: keep the current configuration saved for rollback, keep a fallback model configured, move a small share of traffic first, compare the team's metrics and complaints against the previous weeks, and widen only when they hold.

Clean up with the user's yes, one list at a time, since deletes are permanent: the copies and new tools in `copies.json`, the extra candidate versions, and the simulation resources in `sims_created.json`. Remind them to delete the `raw/` folder from `migration-flow-map` (call data and configuration snapshots).

## Choosing between Terra and Luna

In general, Luna is the faster, lower-cost model and Terra is the more accurate and capable one; for cost and latency figures use Vapi's model benchmarks or step 8. Most behavior patterns are shared ([Model tendencies](references/model-tendencies.md)); the differences:

| | gpt-5.6-luna | gpt-5.6-terra |
|---|---|---|
| Saying and doing | More likely to say it's acting without calling the tool | More likely to call a tool with nothing said first |
| Counted steps | Follows them, less exactly | Keeps them exactly |
| Tone | More often answers and waits | Plainest style, slightly shorter turns |

Both need the same kind of prompt work. If unsure, test both as candidates against the same baseline: the suite, the copies and the comparison are the same.

## Output layout

```text
<working folder>/   (outside any git repository)
  metrics.md            the team's metrics and how they are measured
  review.md             step 3 findings
  owner_questions.md    contradictions and uncovered situations
  copies.json           IDs of every copy and new tool created
  (migration-flow-map and migration-simulations outputs)
  report.md             results, changes and rollout plan
```

## Public sources

- [Vapi API reference index and OpenAPI](https://docs.vapi.ai/llms.txt)
- [Simulations overview](https://docs.vapi.ai/observability/simulations-overview)
- [Test outcomes with Simulations](https://docs.vapi.ai/test/simulations-best-practices)
- The `migration-flow-map` and `migration-simulations` skills in this folder.

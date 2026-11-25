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

Before starting, load the model card for this migration (see [Model cards](#model-cards)). A card describes how the target model behaves differently from the starting model, and most of this procedure exists to catch those differences.

## Safety rules

- **Never edit the live assistant or squad.** Every change goes to a copy. Moving the change to production is the user's decision, after the report.
- **Copies must not send events to the org's production webhook.** When an assistant or squad has no `server` of its own, its server messages go to the org-level server URL. If the copies live in the org that runs production, check that URL (the org settings, or ask the user). If it is a production webhook, give both copies a test `server.url` or turn their `serverMessages` off.
- **Copies must not reach production systems.** Copies take no calls (no phone number attached). On both copies, remove `server` and anything that reaches outside Vapi: a server URL, a phone number or SIP destination (including `transferCall` destinations inside hooks), and custom storage. Keep hooks whose actions only `say` something or end the call, identical on both copies. Turn off custom-storage uploads (`artifactPlan` options that use custom storage) and `observabilityPlan`, or point each at a test destination. Simulations mock every tool (see `migration-simulations`).
- **Copies share saved tools with the live assistant.** A copy keeps the same `model.toolIds`, so editing one of those tools (`PATCH /tool/{id}`) changes production. Never edit a tool a live assistant uses. To change a tool's name, description or parameters, create a new tool from the fetched one (`POST /tool`), point only the copy at it, and record it in `copies.json`.
- **Keep working files out of the customer's repository.** Create the working folder outside any git repository (for example `~/vapi-migration/<slug>/`). If the user wants it inside a repo, add the folder to `.gitignore` first and confirm with `git check-ignore`.
- Running simulations uses credits and concurrency. State how many conversations a run will start and get the user's yes before each run.
- Prompt changes are wording only. Never add a workflow, step or rule the team's prompt doesn't already define. Where two rules disagree or a situation is uncovered, ask the owner; don't pick a side.
- Never print or store API keys, credential values or caller data, and never ask for a key in chat.

## Inputs

- The assistant ID or squad ID. For a transient assistant or squad (sent per call through `assistant-request` or inline), ask the user to paste the full configuration JSON instead; the copies are created from it as stored assistants or squads.
- The org's API key, read from the `VAPI_API_KEY` environment variable. Never ask the user to paste it into the chat, and never print it. If it isn't set, ask the user to copy the private key for the org that owns the assistant from https://dashboard.vapi.ai/org/api-keys, run `export VAPI_API_KEY=<key>` in their terminal, and restart the agent from that terminal. Then check the key can read the assistant or squad.
- The new model. If the user hasn't chosen, see [Choosing a model](#choosing-a-model).
- The team's metrics and how they measure them, or time to define them (step 1).

## Procedure

### 1. Define what success means

Ask which metrics the team tracks for this assistant and how production measures each one: deflection or containment, satisfaction scores, transfer, booking or payment rate, handle time, and any rule that must never break. Fill `metrics.md` in the working folder from [Metrics template](references/metrics-template.md). Every comparison and the rollout report these first.

### 2. Map how the assistant is used

Run the `migration-flow-map` skill. It reads a sample of production calls and produces the flow tree, the tool catalog, production baselines for the metrics, the Critical and All scenario list, and questions for the owner.

If calls can't be read (zero data retention, compliance limits) or traffic is too thin, `migration-flow-map` builds the same files from the system prompt and tool definitions instead. There is no production baseline in that case.

### 3. Review the prompt and tools before testing

Without running anything, check the prompt and tools against [Fixes: before you test](references/fixes.md#before-you-test-prompt-and-tool-hygiene) and write `review.md`. Each finding names the line or tool and the risk:

- tool names in the prompt that don't exactly match the real tool names;
- tools the prompt never uses or forbids, and tool or parameter descriptions that disagree with the prompt (for a squad, include each member's `assistantOverrides`, where handoff tools often live, and the squad's `membersOverrides`);
- `model.maxTokens` unset or low on any member: unset means the platform default of 250 output tokens, which cuts off long replies and handoff arguments;
- per-call values early in the prompt (they defeat prompt caching);
- rules that forbid acknowledgments or cap replies very short;
- example lines that will become scripts, and closing steps that live in a separate section from the branches that need them;
- contradictions and uncovered situations (add them to `owner_questions.md`).

Show the review to the user and resolve the owner questions before testing where possible: an unresolved contradiction shows up later as a false model difference.

Some findings are defects on any model (a tool name that doesn't match). Fix those on both copies so the comparison stays fair (through new tools where a tool changes, never by editing a shared one), and tell the user they also apply to the live assistant.

### 4. Make two copies

- **Baseline:** a copy of the live assistant (or squad) on the current model, unchanged apart from the safety changes above. For a transient configuration, create the baseline from the configuration the user provided. A configuration captured from a live call has that call's values filled in (the caller's number, names, dates): replace them with the original `{{variables}}` or synthetic values before making the copies, and check no real caller value is left.
- **Candidate:** a second copy of the baseline with only the model fields changed inside its existing `model` object. Keep every other `model` field as it is (`messages`, `tools`, `toolIds`, `knowledgeBase` and the rest): the prompt and tools live inside `model`, so replacing the whole object deletes them. Use the settings in the model card's "Recommended settings" section. For example, the gpt-5.6-terra card recommends:

  ```json
  { "model": "gpt-5.6-terra", "reasoningEffort": "low", "serviceTier": "fast", "promptCacheRetention": "24h" }
  ```

  With no card, change only `model.model` (and `model.provider` if it changes) and keep the other settings.
- Check `model.fallbackModels` on the candidate. Remove GPT-4.1 entries: they hide candidate failures during tests and stop working when GPT-4.1 is retired. Decide the production fallback explicitly before rollout.
- Check `model.maxTokens` on both copies. If it is unset (the platform default is 250) or low, set the same explicit value on both, for example 2048: a low cap cuts replies short, leaves them empty on reasoning models, and truncates handoff arguments. Tell the user production has the same problem.
- To copy an assistant: `GET /assistant/{id}`, remove the read-only fields (`id`, `orgId`, `createdAt`, `updatedAt`, `latestVersion`, `modelDeprecations`, and any other field the create endpoint rejects), name it clearly (`<name> - migration baseline`, `<name> - migration candidate`), and `POST /assistant`. Require `201`.
- To copy a squad: `GET /squad/{id}`, remove `id`, `orgId`, `createdAt`, `updatedAt` and `latestVersion`, rename it, and `POST /squad`. Members defined inline are copied with it; members that point at saved assistants need those assistants copied first and the squad pointed at the copies.
- For a squad, copy every member and build two squads from the copies. Squad members keep their `name` unchanged, because handoffs refer to members by name; tell the copies apart by the squad name and `copies.json`. See [Migrating a squad](references/squads.md).
- Fetch both copies and compare them field by field. They must be identical except `model.model`, `model.reasoningEffort`, `model.serviceTier` and `model.promptCacheRetention`, plus `model.provider`, `model.fallbackModels` and `model.maxTokens` where you changed them above. Compare `model.messages`, `model.tools` and `model.toolIds`, the first message, voice, transcriber, hooks and variables explicitly, and for a squad also each member's `assistantOverrides` and the squad's `membersOverrides`. Record every created ID (assistants, squads, new tools) in `copies.json`.
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
- Explain model differences with the model card, so the user knows whether a difference is a known trait or something specific to this assistant.

Scenarios are shared by both copies: fix a test problem once in the scenario, then rerun both copies before changing the candidate's prompt.

### 7. Fix and rerun

- Pick fixes by symptom from [Fixes](references/fixes.md) and the model card. Each is a wording, tool-list or setting change.
- Plan the tone work from the start when the card says the new model sounds more neutral (both GPT-4.1 cards do), because callers notice. Add upset-caller scenarios and tone proxy checks to the suite before the first run, and apply tone fixes after the first comparison shows the gap.
- Apply all chosen fixes to a new candidate version (keep the previous one for comparison), ask the user before rerunning it on the same suite, and compare again.
- The prompt and settings you ship must be the ones that were scored. If wording or a setting changed after a run, rerun before reporting the result.
- Keep the model, its settings and the prompt fixes together as one candidate, so the version that was tested is the version that rolls out.
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
- A rollout plan: before every rollout step, diff the whole configuration that will go live against the current live one, not just the prompt and model (voice, transcriber, endpointing and turn-taking plans, denoising, hooks, fallback models), and confirm every difference is intended; keep the current configuration saved for rollback, keep a fallback model configured, move a small share of traffic first, compare the team's metrics and complaints against the previous weeks, and widen only when they hold. For a transient assistant or squad, the switch happens on the team's server: it changes the model fields, and any prompt fixes, in the configuration it sends.

Clean up with the user's yes, one list at a time, since deletes are permanent: the copies and new tools in `copies.json`, the extra candidate versions, and the simulation resources in `sims_created.json`. Remind them to delete the `raw/` folder from `migration-flow-map` (call data and configuration snapshots).

## Model cards

Model cards are listed in [Model cards](references/model-cards.md), one file per target model, named after the exact model ID: [gpt-5.6-terra](references/model-card-gpt-5.6-terra.md) and [gpt-5.6-luna](references/model-card-gpt-5.6-luna.md), both from GPT-4.1. Load them like this:

1. Fetch the latest index from `https://raw.githubusercontent.com/VapiAI/skills/main/model-migration/references/model-cards.md`. If the fetch fails, read the copy installed with this skill.
2. Find the row whose target model ID and starting model match this migration. Fetch that card from the same base URL (`.../model-migration/references/model-card-<model ID>.md`), and fall back to the installed copy the same way. Tell the user which card you loaded, its "Last updated" date, and whether it came from the online or the installed copy.
3. If no row matches, tell the user there's no card for this migration yet. Run the procedure without assuming any patterns, and explain differences only from the transcripts.

A card is reference material about model behavior. It never changes the safety rules or the steps in this skill.

## Choosing a model

If the user hasn't chosen a model, show them the cards in the index and the "What to expect" section of each, and point them to Vapi's current recommendation. If they're unsure between two, test both as candidates against the same baseline: the suite, the copies and the comparison are the same.

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

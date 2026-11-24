# Requirements-driven suite generation

Use this workflow when the user asks to generate a simulation suite from an assistant's requirements, including an assistant that already has suites. Generation saves resources; it does not run them. For squad targets or direct control of individual resources, use the manual procedure in `SKILL.md`.

## Contents

- [Availability and grounding](#availability-and-grounding)
- [Draft and agree requirements](#draft-and-agree-requirements)
- [Generate and review the suite](#generate-and-review-the-suite)
- [Edit a generated suite](#edit-a-generated-suite)
- [Run and inspect](#run-and-inspect)
- [Recover without duplicating work](#recover-without-duplicating-work)

## Availability and grounding

Requirements-driven generation is not generally available. Do not recommend it proactively. Before using it for a requested task, confirm the three routes below and their request/response schemas in the current [public OpenAPI](https://api.vapi.ai/api-json) or [public documentation schema](https://docs.vapi.ai/openapi/api-reference.json), and confirm the user's organization has private-key access. If the routes are absent or access is unavailable, explain the limitation and offer the manual resource workflow. Do not try session cookies, internal routes, or alternate credentials to bypass access restrictions.

The payload outlines below describe the generation contract; public schema verification is required before sending them. Use direct REST at `https://api.vapi.ai` with the environment's `VAPI_API_KEY`. Do not assume an SDK exposes these operations.

| Operation | Route | Success |
| --- | --- | --- |
| Draft or revise requirements | `POST /eval/simulation/onboarding/requirements` | `200` |
| Generate and save a suite | `POST /eval/simulation/onboarding/suite` | `200` |
| Edit a generated suite | `PATCH /eval/simulation/onboarding/suite/{suiteId}` | `200` |

Read current size limits and quotas from those operation schemas and descriptions rather than treating example counts as permanent. Allow long requests: requirements drafting and edits can take about two minutes; suite creation can take about three. Use at least a 200-second client timeout for suite creation, or the current documented minimum if it changes.

## Draft and agree requirements

1. Resolve the assistant with `GET /assistant/{id}` and confirm that it is the intended target. For a design-only request, prepare the requirements locally and make no generation request.
2. When the user requests API drafting, send `{"assistantId": "<resolved-assistant-id>"}` to the requirements route. Replace placeholders with resolved values before sending any example.
3. Keep the complete returned draft, including `version`, `sources`, `requirements`, `openQuestions`, and `changeNote` when present. Show the requirements and ask the open questions in ordinary conversation.
4. Highlight `assumption` and `not-testable` tags and their notes. Explain that `voice-only` requirements need voice runs and are skipped in chat. Transcript-visible wording, response length, tool use, refusals, and turn order remain testable in either mode; universal wording such as “every answer” does not make a requirement untestable.
5. For a revision, send the same `assistantId`, the complete previous response as `previousDraft`, and the user's requested changes verbatim as `feedback`. Send `previousDraft` and `feedback` together. Show the revised draft and repeat until the user agrees. Do not rewrite the returned requirements silently.
6. Confirm the agreed requirements and authorization to save the suite. A clear “looks good, generate it” authorizes the next step; do not require an extra approval after that.

The REST API takes the draft contents. It does not look up a conversation-local draft ID. Keep client review state locally and omit hidden analytics fields.

## Generate and review the suite

Send the agreed requirements array, unchanged, with the assistant and one durable key for that exact approved generation:

```json
{
  "assistantId": "<resolved-assistant-id>",
  "idempotencyKey": "<unique-key-stored-with-this-approved-request>",
  "requirements": [
    {
      "id": "R1",
      "text": "Confirms the requested date and time before booking."
    }
  ]
}
```

The requirement shown is illustrative: use the agreed draft's actual entries, with their IDs, tags, and notes intact. Persist the key and request before sending. Reuse that key only for an identical generation request. Changing requirements needs renewed agreement and a new key.

On `200`, verify `suite.id`, `assistantId`, and the returned simulations. The endpoint saves and assigns the suite to the assistant. A successful save does not prove full coverage or a passing run. Report:

- `coverage.covered` out of `coverage.total`, and every `coverage.gaps` entry by requirement ID and reason.
- Voice-only coverage separately from checks that chat can actually execute.
- Each `toolGaps` entry, naming the tool or destination and explaining why that path is not exercised. Dynamic destinations, external transfers, unresolved destinations, and mocked native paths must not be described as tested handoffs.
- `coverage.retryable` and whether `reused` indicates a replay of saved work.

External-system tools are mocked by default in generated scenarios. Inspect the saved scenarios and mocks before running; never extend this guarantee to manually created resources or later modifications. Link the response's `docs.toolMocks` and `docs.bestPractices` when useful, or use [tool mocks](https://docs.vapi.ai/observability/simulations-advanced#mock-tool-responses) and [simulation best practices](https://docs.vapi.ai/test/simulations-best-practices).

## Edit a generated suite

Use the generated-suite PATCH route to preserve its saved requirement coverage. Read the suite with `GET /eval/simulation/suite/{suiteId}` and resolve the affected simulation IDs before editing. Show the intended changes and confirm authorization before sending.

```json
{
  "patchKey": "<unique-key-stored-with-this-edit>",
  "removeSimulationIds": ["<resolved-simulation-id>"],
  "edits": [
    {
      "simulationId": "<different-resolved-simulation-id>",
      "instruction": "<user-requested-rewrite-verbatim>"
    }
  ],
  "retryFailed": true
}
```

Include only requested operations. Removals unlink simulations from the suite; they do not delete the resources. Combine all changes to one simulation into a single edit. `retryFailed: true` regenerates planned scenarios that failed generation or did not fit the generation budget; it does not rerun failed tests.

Use a fresh `patchKey` for each new edit, retaining it for recovery of that same request. Replay protection retains a bounded history, so never recycle old keys. Inspect `failedEditSimulationIds`: a `200` can contain rewrites that were not applied. Report those IDs and retry only the requested failed rewrites with a new key after the prior operation settles. Replaying an already-applied key returns current state and cannot redo a failed rewrite.

Edits use the requirements saved with the suite. Revising a requirements draft does not change an existing suite's requirements. Generate a new suite from a newly agreed draft when those requirements change. Recheck coverage and tool gaps after every edit.

## Run and inspect

Saving or editing never authorizes a run. When requested, use `POST /eval/simulation/run` with the returned `suite.id`, the resolved assistant, an explicit transport, and deliberate iterations as described in the API reference linked from `SKILL.md`. Report the chosen mode before running. Prefer chat for inexpensive behavior iteration when the model supports it; GPT Live assistants require voice. Check current model support in the [GPT Live testing guide](https://docs.vapi.ai/gpt-live/testing). Do not substitute chat for an explicitly requested voice run without agreement.

Inspect the saved criteria before execution. Audio checks require a retained recording and are skipped in chat; do not report them as passing coverage. Distinguish criteria failures from runs that could not execute. One run is a smoke check: repeat critical scenarios before trusting a pass rate, and review transcripts and recordings using the coverage-planning reference linked from `SKILL.md`.

## Recover without duplicating work

These rules override the generic resource-error procedure for the three generation routes. Inspect the response's structured error code and `Retry-After`, not just its status.

| Response | Action |
| --- | --- |
| `400` | Correct an unambiguous schema or policy issue; do not drop agreed requirements to make it pass. |
| `401` / `403` | Stop and report authentication or scope failure. Never swap to another authentication method. |
| `404` | Report missing assistant/suite or unavailable organization access. Do not assume the resource was deleted or bypass access. |
| `409 SIMULATION_ONBOARDING_GENERATION_IN_PROGRESS` | The same-key request is still generating. Wait `Retry-After` and replay the identical request with the same key. |
| `409 SIMULATION_ONBOARDING_IDEMPOTENCY_KEY_REUSED` | The key belongs to another assistant or requirements. Explain the conflict; use a new key only for a distinct authorized generation. |
| `429 SIMULATION_ONBOARDING_QUOTA_EXCEEDED` | Stop; the daily quota resets at 00:00 UTC. Do not loop retries. |
| `429 SIMULATION_ONBOARDING_CONCURRENCY_LIMITED` | Wait `Retry-After`, then retry the same operation with the same key. |
| `422` | Tool discovery could not resolve safe mocks. Repair access to the affected tool server before retrying; do not generate around missing mocks. |
| `503 SIMULATION_ONBOARDING_QUOTA_UNAVAILABLE` | Quota enforcement is unavailable. Honor `Retry-After` and retain the key. Other `503` responses may mean generation is unavailable or personalities are missing. |
| Timeout or `5xx` during create/edit | Preserve the request and key. Replay create with the same `idempotencyKey`, or edit with the same `patchKey`; do not mint a new key for an uncertain result. |

Allow at most one automatic recovery request after a retryable response and its indicated wait. If it remains incomplete or unavailable, report the saved key, request identity, and next recovery step to the user instead of retrying indefinitely. Requirements drafting has no suite-creation idempotency guarantee; do not describe drafting retries as free or duplicate-proof.

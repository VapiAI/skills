# Identifier Hygiene

Use this reference when a prompt includes tool names, resource IDs, slugs, snake_case identifiers, placeholder names, field names, enum values, or generic values such as `the_tool_name`.

## Principle

Separate machine-facing identifiers from spoken prose. The voice agent needs exact identifiers to call tools correctly, but caller-facing prose should use natural capability descriptions. Identifiers that appear repeatedly in prose can leak into spoken output or make the agent sound like it is reading implementation details.

## Where Exact Identifiers Belong

Use exact names only in machine-facing or developer-facing contexts:

- `Tool Call:` lines inside few-shot examples
- Tool schema/configuration notes
- Parameter names and enum values when the model must pass them exactly
- Internal implementation notes outside the final prompt
- Query Tool instructions when Vapi needs the system prompt to name the exact search tool function

Do not use exact tool IDs, resource slugs, generic placeholders, or snake_case names as ordinary prose.

Exception: for Vapi Query Tools, the final system prompt may name the exact query tool function in a tool-use rule, such as "When callers ask about pricing, use `billing-query` before answering." Do not put that identifier in caller-facing assistant lines.

## Prose Normalization

Rewrite prose like this:

- `start_lead_onboarding_workflow` -> "start the lead follow-up workflow"
- `transfer_to_support` -> "transfer the caller to support"
- `end_call` -> "end the call"
- `lookup_customer_by_phone` -> "look up the customer by phone number"
- `draft_only` -> "draft follow-ups only" when speaking to the caller
- `schedule_after_approval` -> "prepare follow-ups to schedule after approval" when speaking to the caller

Keep the exact enum or parameter value only where the tool requires it:

```text
If the caller chooses draft follow-ups only, pass outreachMode: "draft_only".
```

## Placeholder Rules

Never leave placeholder-looking names in a final production prompt:

- `the_tool_name`
- `tool_name`
- `my_tool`
- `api_call`
- `workflow_tool`
- `[tool_name]`
- `[param: value]`

If the actual tool name is unknown, either ask for it or write a configuration note outside the final prompt:

```text
Configuration needed: provide the exact Vapi tool name for starting the lead follow-up workflow.
```

## Example Pattern

Good in prose:

```text
After the caller confirms, start the lead follow-up workflow.
```

Good in a few-shot tool call:

```text
Tool Call: start_lead_onboarding_workflow(campaignName: "Q3 AI Infra Sponsors", outreachMode: "draft_only", confirmedByUser: true)
```

Avoid:

```text
Tell the caller you are calling start_lead_onboarding_workflow.
Use the_tool_name to process the request.
```

## Final Pass

Before finalizing, scan for:

- Snake_case identifiers in prose outside tool calls or parameter examples
- Placeholder values that survived template filling
- Tool IDs mentioned in caller-facing assistant lines
- Enum values exposed to callers when a natural phrase would work
- Repeated implementation names that could be replaced with capability wording

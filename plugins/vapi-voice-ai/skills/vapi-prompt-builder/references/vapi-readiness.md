# Vapi Readiness

Use this reference before presenting a prompt or Squad prompt set as ready for Vapi implementation. This is a skill-defined readiness check based on Vapi platform surfaces; do not present "readiness pass", "hard fail", or "blocking condition" as official Vapi terminology.

## Output Labels

Use plain labels that are safe in a Vapi-facing artifact:

- Final prompt or prompt set
- Vapi configuration notes
- Configuration needed
- Blocking questions
- Assumptions
- External test scenarios

Avoid official-sounding labels unless they are actual Vapi product names, such as Assistants, Squads, Handoff Tools, Custom Tools, Structured Outputs, Dynamic Variables, Pronunciation Dictionaries, Evals, or Simulations.

## Blocking Questions

Ask a blocking question instead of drafting when a missing answer would change the artifact shape or create a false deployment claim:

- Single assistant vs Squad is ambiguous and the workflow may need specialized handoffs.
- A tool is required, but its existence, name, purpose, required parameters, or side effect is unknown.
- A handoff destination is required, but the target assistant or handoff condition is unknown.
- A structured output is required, but the schema or extracted fields are unknown.
- A dynamic variable is referenced, but its source or variable name is unknown.
- A verified, trusted, or security-sensitive value is required, but its source and trust tier are unknown.
- A safety-sensitive workflow depends on undefined business policy, severity routing, escalation rules, or prohibited advice.
- A file, document, account record, or backend artifact is required, but there is no confirmed acquisition path.

Do not block for details that can be safely handled as assumptions or configuration notes.

## Do Not Invent Deployment Contracts

Never present invented schemas or contracts as deployable Vapi configuration:

- Tool names
- Tool parameter schemas
- Required parameter arrays
- Enum values
- Handoff destinations
- Handoff argument schemas
- Structured output schemas
- Dynamic variable names
- Server URLs
- Authentication or secret-handling details
- Verified identity, account ownership, permission, or compliance-gating values

If these are not provided, either ask or mark them under `Configuration needed`.

Use examples only when clearly illustrative:

```text
Configuration needed: provide the exact Vapi tool name, required parameters, and enum values for starting the lead follow-up workflow.
```

## Vapi Configuration Surfaces To Check

Check the relevant surface before finalizing:

- Custom Tools: tool name, description, LLM-facing JSON schema, required parameters, server URL or Code Tool implementation.
- Tool reliability: strict schema validation, logs for schema validation errors, short tool responses, request-start messages for slow operations.
- Static parameters and trust boundaries: server-trusted values belong in top-level static `parameters` or backend state, not in prompt text, `function.parameters`, handoff arguments, or conversation-derived variables.
- Structured Outputs: JSON schema and attachment to the assistant or workflow.
- Dynamic Variables: variables are provided through runtime configuration and referenced with supported template syntax.
- Squads: first member starts the call; handoff tools define destinations and conditions.
- Handoff Tools: destination type, destination names or IDs, destination descriptions, function names, required parameters, model-specific multi-destination pattern, tool messages, rejection behavior, and context arguments.
- Passing data between assistants: choose handoff arguments, `variableExtractionPlan.schema`, or Liquid variables based on where the value comes from and whether latency or hallucination risk matters most.
- Handoff context engineering: choose `all`, `lastNMessages`, `userAndAssistantMessages`, `previousAssistantMessages`, or `none` based on what the next assistant needs and whether sensitive tool/context data should be excluded.
- Silent handoffs: verify Handoff Tool messages are empty or null and destination prompts skip greetings when the experience should feel continuous.
- Tool responses and aliases: return only fields the model needs; aliases and extraction help deterministic chaining but do not redact the underlying tool response from model context.
- Pronunciation Dictionaries: use for brand names, proper nouns, acronyms, and technical terms when prompt-level spelling is not enough.
- Evals or Simulations: include external test scenarios that validate success, edge cases, routing, and failure handling.

## Policy Clarity

For safety-sensitive or operationally sensitive domains, do not invent business policy. Ask for or flag:

- Emergency or urgent escalation thresholds
- After-hours behavior
- When to transfer to a human
- What advice the agent must not give
- What actions require explicit confirmation
- What data the agent must not collect
- Required disclosures or consent language
- Which values must be server-trusted rather than caller-spoken or LLM-derived

Keep this general. Do not add narrow domain policy unless the user provides it.

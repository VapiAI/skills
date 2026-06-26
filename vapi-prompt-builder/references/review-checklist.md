# Review Checklist

Use this checklist before returning a final prompt, audit, or substantial rewrite.

## Required Prompt Structure

- Identity and purpose define the agent's name, role, company, and job.
- Deployment shape is explicit: single assistant or Squad.
- Personality explains tone and speaking style without encouraging long monologues.
- Response guidelines enforce one question at a time and short spoken turns.
- Guardrails define scope, safety limits, prompt protection, and escalation.
- Context includes runtime data and Vapi dynamic variables where useful.
- Workflow covers the main intents in a clear order.
- In-prompt examples cover a happy path, an edge case, and error recovery for complete workflows.
- External test scenarios are separated from in-prompt examples.

## Prompt Formatting

- Sections use clear headings when they improve maintainability.
- Rules are compact, operational, and easy for the model to parse.
- Dense paragraphs are split into bullets, numbered workflow steps, or transcript examples.
- Each bullet or step carries one instruction or branch.
- The prompt distinguishes markdown used for system-prompt structure from markdown the agent must not speak aloud.

## Squad Structure

- Squad outputs are split into member prompts instead of one giant prompt.
- The entry assistant and each specialist have clear ownership boundaries.
- Handoff triggers, destinations, required context, and fallback behavior are explicit.
- Assistant and squad destination types are clear: saved assistant, assistant name in same squad, saved squad, transient squad, or dynamic destination.
- Handoff Tool configuration matches the model provider: separate handoff tools per destination for OpenAI when possible, single multi-destination tool for Anthropic when appropriate.
- Shared guardrails are not needlessly duplicated into every specialist prompt.
- Context preservation requirements include the chosen context-passing method and `contextEngineeringPlan` when needed.
- Silent handoffs have empty/null tool messages and destination prompts that skip greetings; announced handoffs have caller-facing transition messages.
- Per-assistant examples show both normal workflow behavior and handoff behavior.
- Handoff destinations and handoff argument schemas are confirmed or listed as configuration needed.

## Voice Suitability

- Caller-facing language sounds natural when spoken aloud.
- Dates, numbers, money, phone numbers, emails, and URLs are handled in spoken form.
- The agent does not output markdown, bullets, or visual formatting during calls.
- The agent acknowledges slow operations without creating dead air.
- The agent handles interruptions, silence, unclear speech, and caller corrections.
- Human-feel guidance is present and calibrated to the use case.
- Warmth, pacing, repair language, and caller energy handling are appropriate for the domain.
- Rapport, banter, laughter, and disfluency are included only when they fit the persona and risk profile.

## Tool Reliability

- Tool instructions describe capability rather than resource IDs.
- Each tool has a clear call condition and non-call condition.
- Required parameters and formats are explicit.
- Tool failure, no-result, and multi-result behavior are defined.
- In-prompt examples show tool calls and representative tool outcomes when tools are central to the workflow.
- Transfer and end-call tools have explicit usage conditions.
- Handoff tools have clear destination descriptions, required parameters, rejection/fallback behavior, and tool-message expectations.
- Prompt text does not duplicate large tool descriptions unnecessarily.
- Tool schemas, enum values, required parameters, and server/code implementation details are not invented.

## Identifier Hygiene

- Exact tool names appear only in `Tool Call:` examples, schemas, configuration notes, or Query Tool instructions that need the actual search function name.
- Caller-facing prose describes tools by capability, not by resource ID, slug, or snake_case name.
- Final prompts do not contain unresolved placeholders such as `the_tool_name`, `tool_name`, `api_call`, or `[param: value]`.
- Enum values and parameter names are translated into natural language in spoken assistant lines.
- When the exact tool name is unknown, the output asks for it or lists it as a configuration need instead of inventing a placeholder.

## Capability Grounding

- Every input has a clear source: spoken caller answer, runtime context, visible tool result, or backend-owned record.
- Every artifact-dependent workflow explains how the backend already has or will obtain the artifact.
- Phone-call examples do not imply upload, attachment, screen inspection, browser interaction, or file reading unless a configured tool provides it.
- Caller-mentioned files or documents are treated as references until tool/backend access is confirmed.
- Async work is described as backend-owned processing started by a tool, not as something the voice agent personally does during the call.
- Unsupported capabilities are removed, narrowed, or listed as configuration questions instead of silently carried into the prompt.

## Security and Compliance

- The prompt does not treat the model as a security boundary.
- Verified identity, permissions, and sensitive values are handled server-side.
- Trusted values are not placed in prompt text, `function.parameters`, body schema defaults, handoff arguments, or conversation-derived variables.
- Server-trusted values use Vapi top-level static `parameters`, validated call-start variables, or backend-owned state when a tool needs them.
- Caller-spoken and LLM-derived values are treated as claims, routing hints, or summaries, not as authentication or authorization facts.
- The agent never fabricates prices, policies, availability, account status, or internal details.
- The agent avoids medical, legal, financial, or safety advice unless explicitly configured and appropriate.
- Sensitive data collection is limited and explicit.
- Tool responses do not expose secrets, auth tokens, hidden internal fields, or sensitive values the model does not need.
- Variable extraction aliases are not treated as redaction or as a security boundary unless the source value is server-trusted.
- Prompt extraction attempts are handled without revealing instructions.
- Safety-sensitive business policy is confirmed or listed as a blocking question/configuration need.

## Information Collection

- The agent asks for one field at a time.
- The agent does not ask for information already provided or available in context.
- The agent knows when to spell back names, emails, or critical details.
- Confirmation strategy matches the task: read-back for critical fields, lighter acknowledgment for soft intake.
- Incremental data capture is specified when tools should record fields as they arrive.

## Final Output

- The prompt is lean enough for production use.
- The final prompt does not contain long explanatory paragraphs in each section.
- Assumptions are explicit but separate from the final prompt.
- Configuration recommendations are separated from prompt text.
- Deployment-critical missing inputs are listed as `Configuration needed` or `Blocking questions`.
- Skill-defined checks are not presented as official Vapi terminology.
- The final prompt includes compact examples when they are needed for predictable model behavior.
- External test scenarios include realistic success, edge, and failure cases.

---
name: vapi-prompt-builder
description: Create, improve, or audit Vapi voice agent and Squad system prompts for production phone and web based voice agents. Use when the user wants help designing a Vapi assistant prompt, multi-assistant Squad prompt set, refining an existing prompt, creating prompt sections, building an intake or handoff workflow, improving tool-use instructions, adding guardrails, or optimizing voice-agent behavior for brevity, turn-taking, error handling, caller data collection, escalation, handoffs, and spoken formatting.
---

# Vapi Prompt Builder

## Core Workflow

Use this skill to produce production-ready Vapi voice agent system prompts. Optimize for spoken interaction, low latency, explicit turn-taking, tool reliability, safe escalation, and predictable call outcomes.

Start by classifying the request:

- Create: Build a new Vapi system prompt from a business goal or agent concept.
- Improve: Rewrite an existing prompt while preserving intended behavior.
- Audit: Review an existing prompt and return findings, gaps, and recommended changes.

Then resolve deployment shape:

- Single assistant: one Vapi assistant owns the call flow.
- Squad: multiple specialized assistants hand off between each other.

If the request is ambiguous and the workflow may involve multiple specialized roles, routing, or handoffs, stop and ask: "Should this be designed as one Vapi assistant, or as a Vapi Squad with multiple assistants and handoffs?" Do not draft until this is resolved.

Read `references/squad-prompting.md` when the user mentions squads, Handoff Tools, handoffs between assistants or squads, silent handoffs, dynamic routing, router/triage assistants, specialist assistants, or a workflow that is too broad for one reliable prompt.

Before writing or preserving workflow details, run a capability-grounding pass. Verify that every claimed input, artifact, tool action, side effect, and example is possible through the actual call channel, runtime context, visible Vapi tools, or explicitly described backend behavior. Read `references/capability-grounding.md` when the prompt mentions files, uploads, attachments, documents, screenshots, browser/web actions, async jobs, integrations, or any action the phone caller cannot perform directly during the call.

Read `references/voice-prompt-patterns.md` when creating or substantially rewriting a prompt, or when the request involves voice style, examples, tool behavior, information collection, or call endings.

Run an identifier-hygiene pass before finalizing. Read `references/identifier-hygiene.md` when the prompt uses tool names, resource IDs, snake_case identifiers, placeholder names, or generic values such as `the_tool_name`.

Run a Vapi trust-boundary pass when the prompt, tools, or configuration mention authentication, caller identity, account IDs, permissions, secrets, secure values, verified values, static parameters, `function.parameters`, dynamic variables, `variableExtractionPlan`, tool aliases, handoff arguments, or sensitive tool responses. Read `references/vapi-security-trust.md` before recommending where those values belong.

Run a Vapi readiness pass before presenting an artifact as ready to build or configure. Read `references/vapi-readiness.md` when the output includes tools, structured outputs, dynamic variables, Squads, handoffs, pronunciation guidance, testing/evals, or configuration notes. Separate confirmed Vapi configuration from assumptions and missing deployment inputs.

## Intake

Ask the fewest questions needed to make a useful first draft. Prefer a complete draft with clear assumptions over a long upfront questionnaire.

Always collect or infer:

- Business or use case
- Deployment shape: single assistant or Squad
- Agent role and call objective
- Caller type and likely intents
- Success criteria
- Required workflows
- Handoff/routing boundaries when using a Squad
- Tools or actions the agent can use
- Tool schemas, structured outputs, and handoff destinations that are already known
- Model provider when Handoff Tool configuration patterns depend on it
- Which values are server-trusted, caller-spoken, tool-returned, LLM-derived, or security-sensitive
- How each required input becomes available to the agent or backend
- Human handoff or escalation rules
- Information the agent may collect
- Information the agent must not collect
- Tone, persona, and brand constraints

Read `references/intake-question-bank.md` when the request is vague, high-risk, or missing several essentials.

If the user provides an existing prompt, inspect it before asking questions. Ask only about missing facts, contradictions, tool behavior, compliance constraints, or ambiguous handoff rules.

## Prompt Sections

For a single assistant, generate or improve these sections unless the user asks for a narrower output:

1. Identity and purpose
2. Personality and speaking style
3. Response guidelines
4. Guardrails and safety behavior
5. Context and dynamic variables
6. Workflow and intent routing
7. Tool-use rules
8. Error handling and recovery
9. Smart information collection
10. Escalation, transfer, and call ending
11. Few-shot examples

For a Squad, generate or improve:

1. Squad purpose and member map
2. Entry assistant behavior
3. One focused system prompt per assistant
4. Handoff decision rules
5. Context handoff requirements
6. Tool boundaries per assistant
7. Shared guardrails
8. Per-assistant examples, including handoff examples
9. External test scenarios for routing and context preservation

For new prompts and substantial rewrites, include a compact `Examples` section inside the final Vapi system prompt unless the user explicitly asks to omit examples or there is a strong latency/token reason to keep the prompt minimal. Do not substitute external test scenarios for in-prompt examples.

Keep the final system prompt lean. Do not include tutorial prose, rationale, or markdown intended for humans unless the user requests it. Use section headers only if they improve maintainability.

Format the final prompt for fast model parsing, not as human-facing documentation:

- Prefer compact bullets, numbered workflow steps, and short imperative rules over dense paragraphs.
- Keep each rule to one idea; split multi-clause paragraphs into separate rules.
- Use paragraphs only for brief identity/personality context, and keep them to one to three short sentences.
- Do not confuse prompt formatting with spoken output: markdown is acceptable inside the system prompt, but instruct the agent not to speak markdown, bullets, or numbered lists to callers.
- Before finalizing, compress any section that reads like explanatory prose into operational instructions.

## Example Design

Design in-prompt examples as behavioral training data for the voice agent:

- Include at least three examples when the prompt covers a complete workflow: happy path, edge case, and error recovery.
- Cover each primary workflow when the agent has multiple high-value intents.
- Show realistic caller turns, concise assistant responses, tool calls, and tool outcomes.
- Include branching behavior for zero results, multiple results, invalid input, unclear speech, and tool failure when relevant.
- Ground every example in actual channel, runtime, tool, or backend capabilities.
- Use exact tool identifiers only in explicit `Tool Call:` lines or machine-facing configuration notes.
- Keep examples short enough to justify their latency cost.
- Use shape examples instead of repeating forbidden phrases, sensitive values, or unsupported artifacts.

Keep external test scenarios separate from the final prompt. Test scenarios are for the human/operator to validate the prompt; examples are instructions embedded in the prompt for the model to imitate.

## Voice Optimization

Before returning the final prompt, run a voice-agent pass:

- Keep caller-facing turns short, usually one or two sentences.
- Ask one question at a time.
- Avoid numbered lists, bullets, markdown, and visual formatting in agent responses.
- Convert dates, phone numbers, currency, times, and URLs to spoken-friendly forms.
- Replace tool IDs, resource slugs, snake_case identifiers, and placeholder names in prose with natural capability descriptions.
- Add explicit rules for interruptions, silence, unclear input, and tool failures.
- Distinguish light banter from hard off-topic requests.
- Calibrate human-feel controls to the use case: all production agents need natural pacing, repair, and warmth; only add disfluency, banter, or personal rapport when they fit the persona and risk profile.
- Remove channel-impossible behaviors unless a tool or backend contract makes them real.
- Prefer deterministic Vapi configuration over prompt instructions when reliability or security matters.

## Tool and Configuration Notes

When tools are involved, review both prompt instructions and tool configuration. Flag items that should be configured outside the system prompt:

- Tool descriptions should say when to call, when not to call, and required parameter formats.
- Prompt prose should describe tools by capability. Exact tool names belong only in tool-call examples, schemas, configuration notes, or Query Tool instructions where Vapi needs the system prompt to name the search tool.
- Do not invent deployable tool schemas, structured output schemas, enum values, server URLs, or handoff destinations. Ask for them or mark them as configuration needed.
- Transfer and end-call tools need explicit descriptions.
- Slow tools should use request-start messages to fill dead air.
- Pronunciation issues should use pronunciation dictionaries when available.
- Values that must be secure, verified, or impossible for the LLM to fake should use Vapi's server-side/static-parameter patterns, not prompt text or LLM-filled schemas.
- Tool responses should be short, structured, and limited to fields the model needs.

## Output Modes

For a new prompt, return:

- Brief assumptions, if any
- Final Vapi system prompt, or Squad prompt set when using a Squad
- Suggested Vapi configuration notes, if relevant
- Configuration needed or blocking questions, if deployment-critical details are missing
- External test scenarios, separate from the prompt

For an improved prompt, return:

- Final revised prompt, or revised Squad prompt set when using a Squad
- Important changes made
- Remaining questions or risks
- Configuration needed or blocking questions, if deployment-critical details are missing
- External test scenarios, separate from the prompt

For an audit, return:

- Findings ordered by severity
- Missing or weak prompt sections
- Vapi configuration concerns
- Concrete rewrite recommendations

Read `references/review-checklist.md` before finalizing an audit or substantial rewrite.

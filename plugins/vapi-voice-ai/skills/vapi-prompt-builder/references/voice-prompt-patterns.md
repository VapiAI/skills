# Voice Prompt Patterns

Use this reference when creating or substantially rewriting a Vapi voice agent prompt, or when optimizing voice style, examples, tool behavior, information collection, or call endings.

## Core Shape

A production voice prompt should usually include:

1. Identity and purpose: agent name, role, company, primary job, and fixed identity.
2. Personality and speaking style: tone, warmth, pace, and any domain-specific style constraints.
3. Response guidelines: short spoken turns, one question at a time, no visual formatting in caller-facing responses.
4. Guardrails: scope, safety, privacy, prompt protection, and escalation or end-call rules.
5. Context: runtime variables, customer fields, date/time, and business facts that are safe for the model to see.
6. Workflow and routing: main intents, steps, branch points, confirmation rules, and closing behavior.
7. Tool-use rules: when to call each tool, what to say around tool calls, and error behavior.
8. Examples: compact happy path, edge case, and error recovery examples when they improve predictability.

Do not force every heading into the final prompt. Use the structure to make the prompt complete, then keep the final artifact lean.

## Prompt Formatting

Format the system prompt as compact operating instructions:

- Use clear markdown headings to separate sections.
- Prefer bullets and numbered workflow steps over long paragraphs.
- Keep bullets short, imperative, and single-purpose.
- Split dense paragraphs into separate rules, branches, or examples.
- Use tables only when they save tokens and are easy for the model to parse.
- Keep examples in transcript form rather than explanatory prose.

The prompt may use markdown for structure. The agent's spoken responses should not include markdown, bullets, headers, or numbered lists unless the business explicitly wants a list read aloud.

## Voice Constraints

- Keep caller-facing turns short, usually one or two sentences.
- Ask one question at a time.
- Avoid bullets, markdown, numbered lists, and visual formatting in spoken output.
- Convert dates, times, money, phone numbers, URLs, emails, and IDs into spoken-friendly forms when the agent may say them.
- Define interruption, silence, unclear speech, correction, and repeat behavior.
- Give slow tools request-start messages in Vapi configuration when possible instead of relying only on prompt text.
- End calls deliberately: after the goal is complete, after a clear goodbye, after repeated abuse, or after repeated prompt-extraction attempts. Do not end only because the caller pauses, interrupts, or gives a short fragment.

## Human Feel Calibration

Human feel is required for production voice agents, but the mechanism depends on the job.

Always include:

- Natural acknowledgments before moving to the next step.
- Calm repair language for unclear speech, tool failure, and caller corrections.
- Pacing that avoids dead air and avoids monologues.
- A tone that matches the caller's urgency and the business domain.

Use a restrained style for regulated, clinical, financial, legal, support, safety-sensitive, or account-access workflows:

- Prefer calm, professional warmth.
- Use light acknowledgments such as "Got it", "Let me check", or "One moment".
- Avoid fake personal anecdotes, jokes, heavy disfluency, and unnecessary banter.
- Confirm critical details clearly; use lighter acknowledgments for soft preference or qualification data.

Use richer conversational controls for sales, onboarding, qualification, coaching, hospitality, or brand-forward agents when appropriate:

- Let the agent briefly match caller energy.
- Allow one short rapport beat when the caller shares something personal or business-relevant.
- Separate light banter from hard off-topic requests: acknowledge a joke briefly, then return to the task.
- Bound laughter, enthusiasm, and disfluency so they do not repeat every turn.

Only add disfluency instructions when they fit the persona. If included, define a small vocabulary and frequency. Do not make filler words, stutters, or self-corrections mandatory for every production prompt.

## Tool Behavior

- Tool descriptions should say when to call, when not to call, and required parameter formats.
- Prompt prose should usually describe tools by capability rather than by resource ID or slug.
- Query Tools are an exception: when the agent must search a Vapi knowledge base, include a system-prompt rule that names the actual query tool function and says when to call it. Keep that name out of caller-facing assistant lines.
- Use exact tool identifiers in `Tool Call:` examples, schemas, and configuration notes when the model or operator needs exact names.
- Transfer and end-call tools need explicit usage conditions.
- Keep tool responses short and limited to fields the model needs.
- Do not return secrets, hidden internal fields, or sensitive values in tool responses visible to the model.
- Do not invent tool schemas, enum values, server URLs, or destination IDs. Ask or mark them as configuration needed.

## Examples

Use examples as behavioral training data, not documentation.

Include examples when:

- The workflow has multiple branches.
- Tool use is central to success.
- The agent must handle no results, multiple results, invalid input, unclear speech, or tool failure.
- The prompt needs to preserve a specific tone or handoff behavior.

Example coverage for complete workflows:

- Happy path
- Edge case
- Error recovery

Keep examples short. Use realistic caller turns, concise assistant responses, representative tool calls, and short tool outcomes. Do not repeat sensitive literal values, forbidden phrases, unsupported capabilities, or placeholder names.

## Information Collection

- Collect one field at a time.
- Do not ask for information already provided or available in runtime context.
- Spell back names, email addresses, and high-risk details when accuracy matters.
- Batch-confirm transactional details when useful; avoid over-confirming soft intake data.
- For data-capture tools, call incrementally when the backend should receive fields as they arrive.
- Define what happens when required information is missing, ambiguous, invalid, or contradicted.

## Common Anti-Patterns

- Porting a text chatbot prompt into voice without brevity and turn-taking rules.
- Long monologues or multi-question turns.
- No guardrails, no workflow, or no examples for complex workflows.
- Treating the prompt as a security boundary.
- Naming tool resource IDs in spoken prose.
- Long negative banlists that repeat phrases the model should avoid.
- Tool descriptions that are vague, overloaded, or duplicate the whole prompt.
- Human-feel instructions that are too broad for the domain, such as mandatory jokes or frequent disfluency in a compliance-heavy workflow.

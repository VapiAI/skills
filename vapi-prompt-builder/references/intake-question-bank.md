# Intake Question Bank

Use these questions selectively. Ask only questions whose answers materially change the prompt or expose risk.

## Minimum New-Agent Intake

Start with these when the user gives only a vague concept:

1. What business or product is this agent representing?
2. Should this be one Vapi assistant, or a Vapi Squad with multiple assistants and handoffs?
3. What is the agent's primary job on the call?
4. Who will usually be calling?
5. What outcome counts as a successful call?
6. What tools or actions can the agent take?
7. When should the agent transfer or escalate to a human?

## Squad Questions

Ask these when the user wants a Squad, mentions handoffs, or describes multiple specialized roles:

- What assistants should be in the Squad?
- Which assistant starts the call?
- What does each assistant own, and what should it never handle?
- What are the handoff triggers between assistants?
- What context must pass to the next assistant at each handoff?
- Should handoffs be silent, announced, or summarized to the caller?
- What shared guardrails apply to every assistant?
- Which tools belong to which assistant?
- Which model provider will the assistants use, if the Handoff Tool pattern depends on it?
- Should any handoff route to a whole squad or be determined dynamically by a backend webhook?

## Workflow Questions

Ask when the call flow is underspecified:

- What are the top three caller intents?
- What steps should happen for each intent?
- Which fields must be collected before the agent can act?
- Which fields are optional or only needed in certain branches?
- Should the agent confirm every field, batch-confirm at the end, or skip read-backs for soft qualification data?
- How should the agent handle no availability, no matching account, invalid input, or duplicate records?

## Tool Questions

Ask when tools are mentioned but unclear:

- What tools exist, and what does each one do?
- Are the exact Vapi tool names, required parameters, enum values, and descriptions already defined?
- What parameters does each tool require?
- What parameter formats should the model use?
- Which tool inputs must be trusted or impossible for the caller/model to fake?
- For trusted inputs, will they come from top-level static `parameters`, call-start variables, or backend state rather than `function.parameters`?
- For Handoff Tools, are destinations assistant IDs, assistant names in the same squad, squad IDs, transient squads, or dynamic destinations?
- If data must pass during handoff, should it be a tool-call argument, a `variableExtractionPlan` extraction, or a Liquid variable already available in the variable bag?
- What conversation history should the destination receive: all, recent messages only, user/assistant messages only, previous assistant messages only, or none?
- Which required inputs come from the caller's spoken answers, runtime context, visible tools, or backend-owned records?
- If the workflow depends on a file, document, screenshot, uploaded data, or external artifact, where does the backend get it from?
- Does the phone agent need to verify that an artifact is already available before starting the workflow?
- What should the agent say before or after calling each tool?
- What should happen if the tool returns zero results, multiple results, or an error?
- Are there transfer or end-call tools, and when should they be used?

## Safety and Compliance Questions

Ask when the domain touches health, finance, legal, minors, insurance, payments, account access, regulated services, or private data:

- What sensitive information must the agent never collect?
- What advice is the agent not allowed to give?
- What caller identity checks happen outside the prompt?
- Which values are server-trusted, caller-spoken, or LLM-derived?
- Are any account IDs, auth flags, caller IDs, tenant IDs, or permission checks currently being passed through the prompt or LLM-facing schemas?
- What information can only come from tools or approved configuration?
- Are there required disclosures, consent language, or recording notices?
- What should trigger immediate escalation?
- Are emergency, urgent, after-hours, or safety-sensitive routing policies defined by the business?

## Voice and Brand Questions

Ask when tone matters or the brand is distinctive:

- Should the agent sound formal, warm, clinical, energetic, casual, or sales-oriented?
- Should the agent use light rapport or stay task-focused?
- Should disfluencies be avoided, subtle, or intentionally conversational?
- Are there brand names, acronyms, or domain terms that need pronunciation guidance?
- How long should the call ideally last?

## Improvement Questions

Ask after reading an existing prompt:

- Which current behavior must stay exactly the same?
- What failures have you seen in real calls?
- Are there transcripts, logs, or call summaries that show the problem?
- Are tool calls failing because of the prompt, the tool descriptions, or the returned data shape?
- Are any current examples copied from a web or backend workflow that the phone agent cannot actually perform?
- Which prompt claims should be downgraded to backend prerequisites or configuration notes?
- Should the rewrite prioritize reliability, naturalness, compliance, conversion, or shorter calls?

# Prompt Design Fallback

Use this only when the `vapi-prompt-builder` skill is unavailable.

- Collect or safely infer the business, audience, call direction, objective, success criteria, workflows, authoritative context, tools, escalation rules, collection limits, languages, and brand voice.
- Ask only questions that materially change the design. Stop when a required capability, trusted value, destination, or safety-sensitive rule cannot be inferred.
- Cover identity and personality, spoken-response guidelines, guardrails, context, workflows, tool behavior, recovery, escalation, closing behavior, and compact examples.
- Keep turns concise, ask one question at a time, and define behavior for interruptions, silence, unclear speech, corrections, and tool failures.
- Ground every promised capability and example in real tools, knowledge, runtime context, or documented backend behavior. Keep secrets and server-trusted values outside the prompt.
- Align `firstMessage` with call direction, required disclosure, and the first workflow step.
- Separate assumptions and configuration needs from the prompt. Test representative happy, edge, and failure cases before calling the assistant production-ready.

## Public Sources

- [Voice AI Prompting Guide](https://docs.vapi.ai/prompting-guide)

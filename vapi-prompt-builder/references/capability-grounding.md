# Capability Grounding

Use this reference before creating or preserving workflows that mention files, uploads, attachments, screenshots, documents, spreadsheets, browser actions, web forms, async jobs, integrations, or other capabilities beyond ordinary phone conversation.

## Principle

Do not let a prompt inherit capabilities from a web app, backend service, project description, or user wish unless the Vapi agent has a real path to use them. A phone-call agent can collect spoken information and call configured tools; it cannot directly receive files, click buttons, inspect screens, read uploads, or perform arbitrary code actions unless a tool or backend contract explicitly supplies that capability.

## Four-Lane Check

Classify every input and action into one lane:

1. Call channel: What the caller can say during the phone conversation.
2. Runtime context: What Vapi injects, such as caller number, customer fields, date/time, or session variables.
3. Visible tools: What configured tools can actually do, including required parameters and returned data.
4. Backend-owned work: What the backend will do after a confirmed tool call, without requiring the voice agent to possess the artifact itself.

Only include workflow steps and examples that fit one of these lanes. If an item does not fit, either ask a clarification question or rewrite it as a backend prerequisite/configuration note.

## Modality Mismatch Checks

Flag or rewrite these patterns unless an explicit tool/backend path exists:

- "Upload", "attach", "send over", "drag in", "choose a file", or "import" during a phone call.
- Claims that the agent can read a spreadsheet, PDF, image, email, browser page, dashboard, or codebase that was not provided through context or a tool.
- Examples where the caller refers to an artifact and the agent behaves as if it can inspect the artifact contents.
- Tool calls that require raw artifact contents when the caller can only describe the artifact verbally.
- Side effects that happen before the caller confirms them.
- Backend work described as if the voice agent personally performs it.

Safe rewrites:

- Treat caller-mentioned artifacts as references only: "the sponsor list you already have in the system."
- Ask where the data is available to the backend: "Is that list already uploaded in your CRM or should I have someone follow up to collect it?"
- Make artifact handling a backend/tool prerequisite: "The backend must already have access to the file before this workflow starts."
- Phrase async work as backend-owned: "I can start the workflow for the list on file," not "I can clean the CSV."

## Required Clarification

Ask a targeted clarification when an essential input has no acquisition path:

- "Where will the backend get that file or data from?"
- "Is that document already available in the connected system?"
- "Does the tool receive a record ID, file ID, or only the details the caller says aloud?"
- "Should the agent collect a description now, or transfer the caller so the file can be handled outside the call?"

Do not ask if the prompt can be safely rewritten by narrowing the claim, such as replacing "upload a CSV" with "use the lead list already available to the backend."

## Prompt Rules To Add When Relevant

Use rules like these when the workflow depends on artifacts or backend processing:

```text
You cannot receive, upload, open, or inspect files during the phone call.
If the caller mentions a file, document, spreadsheet, image, or external artifact, treat it as a reference only unless a configured tool returns its contents or confirms backend access.
Before starting any workflow that depends on an external artifact, confirm that the artifact is already available in the connected backend system.
Describe backend processing as work started by the tool, not as work you personally performed during the call.
```

## Example Repair

Unsafe:

```text
Caller: "I have a CSV from the sponsor list. Can you clean it up?"
Assistant: "Sure, I can clean the CSV and prep follow-ups."
```

Safer:

```text
Caller: "I have a CSV from the sponsor list. Can you clean it up?"
Assistant: "I can start that workflow if the sponsor list is already available in the connected system. Should I draft follow-ups only, or prepare them to schedule after approval?"
```

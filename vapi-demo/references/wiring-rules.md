# Phase 5 — Wiring rules (where demos break agents)

- **Observe tools via `conversation-update`, never by taking tool webhooks.**
  The messages array carries every tool call and result no matter whose server
  executes them. Verified live shape (2026-08-18): every update resends the
  FULL history; tool calls carry stable ids; tool RESULTS carry `name` and
  `result` but NO id, so results can only be paired to calls positionally per
  name — the skeleton does this. Models really do emit parallel same-name
  calls (observed: two `order_food` calls in one turn), so never assume one
  running card.
- 🔴 **Taking over `assistant.server.url` hijacks tools that lack their own
  `server.url`** — tool webhooks fall back to the assistant's server, the demo
  won't answer them, and those tools silently break. Check every attached tool
  has its own server.url before pointing the assistant at the demo. If the
  assistant's server.url is load-bearing (production `assistant-request`, tool
  fallback), DON'T retarget it — ask the user how they want events forwarded.
- `serverMessages` for a demo: `status-update`, `transcript`,
  `conversation-update`, `end-of-call-report`, plus `assistant.started` for a
  squad. Note `transcript` is NOT in Vapi's default set, so it must be listed
  explicitly. Never add `phone-call-control` (it delegates hang-up to your
  server — a behavior switch, not telemetry).
- **Which squad member is talking** is not something to infer. Every server
  message carries `message.assistant`, and that IS the currently active member,
  re-pointed on every hop; `assistant.started` announces each swap in
  `newAssistant`. Do not try to read it off handoff tool calls: `handoff` and
  `transferCall` are local tools and never produce a `tool-calls` webhook.
- Assistant-request answers have a **hard 7.5s end-to-end budget** (telephony
  ceiling, NOT `server.timeoutSeconds`); a late answer kills the call. Any
  `assistantOverrides.model` must include `provider` + `model`.

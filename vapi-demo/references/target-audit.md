# Phase 3 — Read the target and AUDIT it against the dashboard (read-only)

`GET /assistant/:id` (or squad + members) and every tool by id, into `configs/`
(Phase 0). Then read those configs AGAINST the dashboard code you are about to
ship, checking each row below. Ten minutes here prevents the worst demo
failure, which is discovering an incompatibility with the room watching.

| Config | Check against the dashboard |
|---|---|
| `transcriber.provider` | The webhook SHAPE is uniform (`role`, `transcript`, `transcriptType`) but `transcriptType` is a VERBATIM passthrough of whatever the provider's stream decided, with no normalization anywhere downstream. There are two incompatible FINAL semantics, and which one you get is the thing that matters: **multi-final and disjoint** (Deepgram nova family, Speechmatics) sends several finals per sentence, each carrying only its own fragment, so finals must be APPENDED; **single-final and whole-utterance** (Soniox, Deepgram Flux, AssemblyAI, Gladia, OpenAI) sends one final restating everything the partials showed, so appending it double-writes. Do not branch on the provider. Use the watermark algorithm in [demo-craft.md](demo-craft.md), which satisfies both, and correct from `conversation-update` on top of it. |
| `model.tools` / `toolIds` | 🔴 Every SERVER-BACKED tool needs its OWN `server.url` before the assistant's server can be retargeted (see [wiring-rules.md](wiring-rules.md)). Built-in types execute inside Vapi and never call out, so `voicemail`, `dtmf`, `endCall`, `transferCall`, and `handoff` showing no server.url is normal and not a blocker. The rule bites `function`, `apiRequest`, and MCP tools. Also eyeball arg schemas: the tool card prints args as `key: value` lines, so a tool that takes a 2KB blob argument needs the card's arg rendering trimmed. |
| `server.url` (current) | Non-empty means it is load-bearing (production assistant-request, tool fallback). Do NOT overwrite without the conflict conversation in [wiring-rules.md](wiring-rules.md). |
| `serverMessages` (current) | If `phone-call-control` is present, the agent's hang-up is delegated to that server — never carry it into the demo wiring, and flag it to the user. |
| voice / languages | Multilingual agents render fine (text is text), but the speaker label in the example is a fixed name — rename it to this agent's persona. |
| `maxDurationSeconds` | Longer than the presenter's demo script? A call that dies mid-demo at a 60s cap looks like a crash. |
| `analysisPlan` / structured outputs | Whatever exists lands on `call.report`, keyed by structured-output id with its own `name` and `result`. This is exactly what the report panel (`report-panel.html` in the skill's assets folder) renders, so it decides how much the default right panel pays off. None configured is fine — the panel still shows the ended reason. |
| squad members | Run every row above per member; members share the one board. |
| squad handoff wiring | Before concluding a squad cannot hand off, look in `.members[].assistantOverrides["tools:append"]` — that is where a squad's `handoff` tool and its `destinations` usually live, NOT on the member assistant's own `model.tools`/`toolIds`. Checking only the assistant produces a confident, wrong "this squad has no handoff." A squad with genuinely no destinations anywhere will never leave member 1, so say so before building a panel that depends on the hop. |

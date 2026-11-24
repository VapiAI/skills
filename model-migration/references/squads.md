# Migrating a squad

A squad migration is an assistant migration for every member at once, plus the handoffs between them.

## Making the copies

- Copy every member assistant. Keep each member's `name` exactly: handoff destinations and prompts refer to members by name. Members defined inline in the squad (with no assistant ID) are copied with the squad.
- Build the baseline squad from the baseline copies and the candidate squad from the candidate copies.
- Point every handoff at the copy in the same squad, never at a live member. A handoff destination that uses `assistantId` must be rewritten to the copy's ID; if the handoff tool is a saved tool shared with the live squad, create a new tool for the copies instead of editing it.
- Dynamic handoffs (destinations requested from your server at call time) call your server. Point them at a test endpoint, or replace them with static destinations on both squads.
- Keep `membersOverrides` and squad-level settings (voice, transcriber, speaking plans) identical on both squads, but remove `server` and server-calling hooks from `membersOverrides` and from each member's `assistantOverrides`.
- Change the model on the members you are migrating. If only some members move, say so in every report.

## Testing

- Mock every member's tools in every scenario. Leave static handoff tools unmocked so handoffs really happen inside the squad.
- Include scenarios that cross members: a handoff in each direction the flow map shows, and a handoff back to the first member if the squad allows it.
- Report per member as well as per conversation: replies, tool calls, handoffs in and out, and empty or missing first replies after a handoff.

## What to expect

- Both new models follow handoff rules more strictly than GPT-4.1: no filler line before a handoff when the prompt says none, and the handoff carries every argument the tool needs.
- What is said around a handoff can change. One model may speak a short line before handing back; the other may hand off silently, which leaves the caller repeating themselves. Script the line if it matters.
- Long member prompts make the first reply after a handoff slower, because the next member's prompt starts uncached. Measure latency after handoffs separately in voice.
- Keyword-triggered handoffs (for example a safety escalation on listed symptoms) fire on any listed word with the new models, even when the caller says it is past or mild. If that is not intended, say when the trigger applies.

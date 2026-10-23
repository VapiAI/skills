# Phase 1 — Discovery (before any code)

Ask one question at a time. The goal is to find the demo's MOMENTS — the 3–5
seconds where a Vapi feature becomes visible — then design panels around them.

**Skip this phase entirely on the Cold start path.** Take the defaults and get
them a deployed board first. These questions land once there is something on a
screen to react to.

1. **Which Vapi features is this demo selling?** (tool calling, caller
   recognition via assistant-request, live call control pushes, multilingual,
   structured outputs, transfers…) The answer decides which optional pieces get
   built. Push back on "all of them" — a demo that dramatizes two features beats
   one that gestures at six.
2. **What does the agent DO that changes over a call?** That's the right panel.
   Ride status, an order building up, a form filling in, an appointment slot
   locking, a verification checklist. If nothing accumulates, the right panel can
   show the end-of-call structured outputs landing instead.
3. **Who is watching, and on what screen?** Projector = bigger type, fewer
   panels, higher contrast. Screen share = denser is fine.
4. **How do calls reach the agent during the demo?** Phone number on the wall,
   presenter dials, or a web-call button on the page (see the optional pieces in
   Phase 4 of SKILL.md).

**The standard layout is not a per-demo decision — start from it every time.**
A bounded shell (max 1380px, full viewport height) holding a card header and
three card panels that scroll internally, so the page itself never scrolls. The
header carries logo, a divider, the agent name, the number as a pill, then the
call id and a status pill pushed right, and Reset. Panels are numbered in
Gridnik (`01 · LIVE TRANSCRIPT`): **transcript left, tool calls middle, use-case
panel right**. The assistant-request strip sits between header and panels and
hides itself unless a call resolves through it. Only the RIGHT PANEL is a design
decision, so confirm its content with a quick sketch and leave the rest alone.

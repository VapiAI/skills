---
name: vapi-demo
description: Use when building a LIVE DEMO DASHBOARD for an EXISTING Vapi assistant or squad — a Vapi-branded web page that visualizes a call as it happens (streaming transcript, tool calls, optional assistant-request strip, optional web-call button, a custom panel per use case) and deploys to Railway. Triggers on "make a demo for this assistant", "demo dashboard", "showcase this agent", "live call visualization", "demo this to a customer/exec". NOT for creating, prompting, or testing voice agents — it points at an agent that already exists and already works, and it never edits the agent itself.
license: MIT
compatibility: Requires a local shell with Node 20+, curl, jq, the Railway CLI and a Railway account, internet access, and the private Vapi API key (VAPI_API_KEY) of the org that owns the agent. Playwright is optional, for screenshots.
metadata:
  author: vapi
  version: "1.0"
---

# Vapi Demo Builder

Point at an existing assistant or squad and produce a deployed, Vapi-branded demo
dashboard for live calls. The demo is theater built on real signals: every panel
is driven by actual webhooks from the actual agent, paced so a room can read it.

This is an experimental reference workflow. It is not part of the standard
`vapi-voice-ai` plugin, so install it explicitly.

**Hard scope limits.** This skill never creates, edits, or tests the AGENT — no
prompt work, no tool changes, no test calls against it. The only mutations ever
made to Vapi resources are demo wiring (the assistant's `server.url` +
`serverMessages`, and optionally detaching the assistant from a phone number for
assistant-request), each done only after the user explicitly approves it and with
the prior value recorded for rollback.

## Before you start

Four things about the agent, and none of them are optional:

1. **An assistant or squad that already works.** This skill visualizes an agent,
   it does not build one. If the agent cannot hold a call yet, fix that first:
   `create-assistant` or `create-squad` to build it, `create-call` or
   `simulations` to test it.
2. **Its id**, copied out of the dashboard URL. Assistant ids and squad ids are
   indistinguishable UUIDs, and Phase 0 step 2 resolves which one you have.
3. **The PRIVATE API key of the org that owns it** (dashboard → Organization
   Settings → API Keys). The public key cannot read configs and cannot wire
   webhooks, so it is not a substitute.
4. **Edit rights on that agent.** Wiring the demo PATCHes `server.url` and
   `serverMessages` on the assistant, or on every member of the squad.

And four things about the machine: Node 20+, `curl`, `jq`, and a Railway
account with the CLI installed (`npm i -g @railway/cli`). `railway login` opens
a browser and finishes there, so a person has to run that one themselves.
Optional but strongly recommended: `npx playwright install chromium`, which is
what lets the builder screenshot its own work instead of asking you to look.

If the agent has no phone number attached, settle before building whether to
attach one (`create-phone-number`) or ship the web-call button instead.

## Quickstart

See the whole thing move first, with no Vapi account, no key, and no phone
call. From the root of this skill:

    mkdir -p demo/public
    cp assets/server-skeleton.mjs  demo/server.mjs
    cp assets/demo-dashboard.html  demo/public/index.html
    (cd demo && PORT=7788 node server.mjs > server.log 2>&1 &)
    cat demo/server.log                       # MUST say: demo server on :7788
    open http://localhost:7788
    bash scripts/try-it.sh http://localhost:7788

That replays a scripted call through every panel. If the board does not move,
stop and fix that before going near a real agent.

Then build the real one. **Phase 0 Cold start** is the path when all you were
given is an id, **Phase 0 Intake** is the path when the user arrives with their
setup already in hand, and both feed the **Default path**, which is the exact
sequence from an empty folder to a deployed URL.

## Phase 0 — Cold start (you were given only an id)

**Enter here when the request is just an id** — "make me a demo for this
assistant id `<uuid>`" — with no env file, no key, no phone number, and no
Railway. That is the common case, and it is not a reason to open the full
intake interview. Run the steps below in order, starting with step 0. They
REPLACE Phase 0 Intake and Phase 1 Discovery; every other phase still applies
unchanged.

**0. Before anything else, confirm you can actually run here.** Try
`node --version`.

- **No shell tool at all, or code runs only in a hosted sandbox** — you are in
  a hosted chat app rather than a coding agent on the user's own machine.
  **Stop and say so.** This skill needs a local machine. It writes a project
  folder, runs a server on a port, installs and logs into the Railway CLI, and
  deploys to a URL that Vapi can reach. A hosted sandbox is not the user's
  machine and has none of that, so there is nothing partial worth building.
  Tell the user this needs a coding agent running on their own computer, and
  stop there. Do NOT start the intake, do not ask for an API key, and do not
  produce a dashboard file as a consolation prize — a page nobody can deploy
  or wire is worse than a clear no.
- **A shell that works** — continue to step 1.

Getting this wrong is expensive in one direction only. Stopping early costs a
sentence. Discovering it at deploy time costs the user their whole session and
their API key was pasted for nothing.

**1. Ask for one thing and nothing else: the org's PRIVATE API key.** Say where
it is (dashboard → Organization Settings → API Keys) and that the private key is
the one that works. Do not ask about squads, phone numbers, panels, or Railway
yet. You cannot resolve the id without the key, so this question comes first and
alone.

**2. Resolve the id yourself. Never ask "is that an assistant or a squad".**
The two id types are indistinguishable UUIDs, and users call both "the assistant
id". Probe, in this order:

    curl -s -o /dev/null -w '%{http_code}' https://api.vapi.ai/assistant/$ID \
      -H "Authorization: Bearer $KEY"     # 200 → assistant
    curl -s -o /dev/null -w '%{http_code}' https://api.vapi.ai/squad/$ID \
      -H "Authorization: Bearer $KEY"     # 200 → squad

Verified status codes (2026-08-19, live): the wrong type returns a clean **404**,
a bad key returns **401**, and a non-UUID returns **400** `id must be a valid
UUID`. Nothing returns 400 or 500 in a way that breaks the fallthrough, so treat
the codes literally:

| Outcome | What it means | What to do |
|---|---|---|
| assistant 200 | It is an assistant | Continue. Right panel = `assets/report-panel.html` |
| assistant 404, squad 200 | It is a squad | Continue. Right panel = `assets/squad-panel.html`, and EVERY member gets wired in Default path step 9 |
| both 404 | Wrong id, or the key belongs to a different org | Say both possibilities and stop. Do not guess |
| 401 | Wrong or public key | Ask again for the private key |
| 400 | Not a UUID | They pasted a name or a URL fragment. Ask for the id from the dashboard URL |

The 200 body carries `orgId` and `name`, so **this probe is also the credential
test** — print the agent name back to the user as confirmation before going on.
That one line catches a wrong-org key before it wastes a build.

**3. Write `demo.env` FOR them.** Do not hand over `assets/demo.env.example`
and ask them to fill it in. Create the project folder, write `demo.env` with the
key and the resolved `ASSISTANT_ID` or `SQUAD_ID`, write `.gitignore` containing
`demo.env` in the same step, and pull the configs into `configs/` as Phase 0
Intake describes. They gave you a key and an id, which is everything the file
needs so far.

**3a. If writing or reading `demo.env` is denied, do not fight it.** Many
setups deny `.env` access on purpose (`Read(./.env)`, `Read(./.env.*)`,
`Read(**/*.env)`, or a managed policy), and the deny can cover writes as well as
reads. **Never route around the guard** — no `cat` to dodge a blocked `Read`, no
renaming the file to slip past a glob. That is the user's security config doing
its job, and defeating it silently is worse than the inconvenience.

You do not need the file. You already have the key in context because the user
pasted it in step 1, and the deploy-time home for secrets is Railway variables,
not a file on disk. So when the file is blocked:

- Run the local server with the values inline for that one command rather than
  sourcing a file (`VAPI_API_KEY=... ASSISTANT_ID=... node server.mjs`).
- Put the real values in Railway with `railway variables --set` after the first
  `railway up`, exactly as the Default path already does. The deployed demo
  reads them from the environment and never wants the file.
- Skip `configs/` to disk if file writes are blocked too. Pull the assistant or
  squad config, read it in context for the Phase 3 audit, and tell the user you
  have no on-disk rollback record so they should keep the `assistant-before`
  JSON you print for them.

Say plainly which step was blocked and which of these you are doing instead.
Offer the two alternatives once, then proceed without waiting: the user can
create `demo.env` themselves from content you print, or they can relax the
matching permission rule. Neither is required to finish.

**4. Preflight, and heal what you can without them.** Run the Phase 0 preflight
checks. Install the missing pieces yourself rather than reporting them
(`npm i -g @railway/cli`, `brew install jq`, `npx playwright install chromium`).
Exactly one item ever goes back to the user, so make it a single clear ask:
`railway login` opens a browser and finishes there, so an agent cannot complete
it. Give them the command, wait, then confirm with `railway whoami`.

**5. Now ask the one question that has no default: how do calls reach the agent
during the demo?** An existing phone number (get the number and its id), or the
web-call button. If neither exists, say so and resolve it before building.

**6. Take the defaults for everything else and run the Default path.** On this
path do NOT run the Phase 1 discovery interview — a user who pasted an id and
nothing else has no basis to answer it, and it is what makes a first build stall.
Use the standard layout, the right panel chosen in step 2, no assistant-request
strip, and no web-call button unless step 5 selected it. Go straight through the
Default path to a deployed URL. Offer the optional pieces AFTER they have a live
board to look at, when the questions are concrete.

## Phase 0 — Intake (collect ALL of this before anything else)

**Given only an id and nothing else? Do Phase 0 Cold start above instead** — it
gathers the same things in an order a user with an empty machine can actually
answer. This section is the checklist of what must end up collected, and the
path to run when the user arrives with their setup already in hand.

One conversation, up front. A demo that stalls halfway because a key or a
phone number is missing wastes the exact person it was meant to impress.

**1. The env file.** Have the user fill `assets/demo.env.example` → save as
`demo.env` in the project folder, and add `demo.env` to `.gitignore` in the
same step. Load it with `set -a; source demo.env; set +a`. If that read or
write is denied by the user's permission rules, see Cold start step 3a — the
build finishes without the file, and you never route around the guard. The API key must be
the org's PRIVATE key — it is what makes you debuggable, not just buildable:

    # pull the full agent config (and each tool by id from model.toolIds)
    curl -s https://api.vapi.ai/assistant/$ASSISTANT_ID -H "Authorization: Bearer $VAPI_API_KEY"
    curl -s https://api.vapi.ai/tool/$TOOL_ID          -H "Authorization: Bearer $VAPI_API_KEY"
    # when a panel stays empty: read what the platform recorded for the call
    curl -s "https://api.vapi.ai/call?assistantId=$ASSISTANT_ID&limit=3" \
      -H "Authorization: Bearer $VAPI_API_KEY"

Pull the assistant (or squad + every member) and its tools FIRST and save them
to a `configs/` folder in the project. That snapshot is your rollback record, the
input to the compatibility audit (Phase 3), and your context when something
misbehaves mid-demo.

**2. Preflight the machine.** Run these; fix anything missing before building:

    node --version          # need 20+
    railway whoami          # see the note below — this one can block you
    jq --version            # used throughout
    curl --version
    npx playwright --version              # fetches the package on first run
    npx playwright install chromium       # idempotent; downloads the browser once
                            # Optional but STRONGLY recommended: lets the builder
                            # verify its own work by screenshot instead of asking
                            # the user to look. Works from any folder, no
                            # node_modules needed:
                            #   npx playwright screenshot --browser chromium \
                            #     --viewport-size 1440,760 http://localhost:7788 check.png
                            # Screenshot every state that matters (idle, mid-call
                            # via try-it.sh, ended, after reset) and LOOK at them.

**Railway is the one preflight item that can stall a build, so clear it first.**
`command not found` means the CLI is missing (`brew install railway`, or
`npm i -g @railway/cli`). `Unauthorized` means the user must run `railway login`
themselves — it opens a browser and finishes in a browser, so an agent cannot
complete it. Ask for it in the same message as the rest of the intake, never
after the demo is built. On a machine with no browser, `railway login
--browserless` prints a code to paste. Also settle now whether the deploy goes
to a NEW project (`railway init`) or an existing one (`railway link`), and that
the user accepts a real deployment being created on their account.

**3. How will calls reach the agent during the demo?** Decide now, not at the
end: an attached phone number (fill PHONE_NUMBER in the env), or the web-call
button (fill VAPI_ORG_ID; PUBLIC_ORIGIN after first deploy). If the answer is
"no number exists and no web calls", stop and resolve that with the user.

**4. What the room should see.** Two questions that make the demo land:
which 2–3 moments of the call should the audience be able to SEE happening,
and what will the presenter actually say on the call? Panels built against
the presenter's real script always beat generic ones. Ask whether the demo
should carry their own brand instead of Vapi's (optional; see "Making it look
like yours" in Phase 4).

## Default path (when in doubt, do exactly this)

Everything beyond this section is judgment. This section is not. Given nothing
but an assistant id and an API key, this produces a working deployed demo. The
local half (steps 2 to 7) has been run from an empty folder and screenshotted at
every state; the wiring half (steps 9 and 10) has carried a real production
call. Do them in order and do not skip the proofs — several steps exist because
skipping the proof produced a demo that looked finished and was not.

1. Complete Phase 0 (env file saved, preflight green, configs pulled) — via
   Cold start if the user gave you only an id, via Intake if they arrived
   prepared. Either way you reach this step knowing whether the target is an
   assistant or a squad, which decides the right panel in step 6.
2. `mkdir demo && cd demo && mkdir public`
3. Copy this skill's `assets/server-skeleton.mjs` → `server.mjs`, and
   `assets/demo-dashboard.html` → `public/index.html`.
4. Prove it runs before touching Vapi — and prove the thing answering is YOURS.
   Pick a port nothing is on, start the server so its output goes to a file you
   read, then confirm the boot line and the owner before believing anything:

       lsof -nP -i :7788 -sTCP:LISTEN        # busy? pick another and export PORT
       PORT=7788 node server.mjs > server.log 2>&1 &
       cat server.log                        # MUST say: demo server on :7788
       lsof -a -p $(lsof -nP -ti :7788 -sTCP:LISTEN) -d cwd -Fn | tail -1

   Then run this skill's `scripts/try-it.sh` with the URL as its argument
   (`http://localhost:7788`) — always pass the URL, because the script's
   default is 7788 and it reports nothing when it lands on a stranger. Every panel must move. If it does not, stop and fix that
   first.

   🔴 **A leftover server on the port fakes a perfect result.** The port is in
   use, your `node server.mjs` dies with EADDRINUSE into a log nobody reads,
   `/health` answers `{"ok":true}`, the page loads, the replay POSTs return
   200, and the screenshot shows a plausible call — all served by someone
   else's process. Caught exactly this way while rehearsing this skill. The
   boot line and the cwd check above are what make the proof real.
5. Make it yours. The example is a ride-booking demo; six strings carry that
   scenario, and a demo shown with any of them left over looks unfinished:
   `<title>`, the `.brand` agent name, the `.phone` link (its `href` and its
   text), the `Sarah`
   speaker label (two places, plus the assembly strip's persona fallback), the
   third panel's `<h2>`, and the `PLACEHOLDERS` icon for that panel. Search the
   file for `Sarah` and `ride` and leave neither behind.
6. Right panel default: replace the ride panel with `assets/squad-panel.html`
   if the target is a squad, otherwise `assets/report-panel.html` (a titled
   card that fills at hangup from `call.report`). Both are copy-paste edits that
   work for any agent. Do not invent a custom panel unless the user asked for
   one in discovery.
7. The assistant-request strip needs nothing from you unless the demo is
   showcasing caller recognition: it hides itself while idle and only appears
   once a call resolves through it. To remove the code entirely, deleting the
   `<div class="assembly idle" id="assembly">` block is enough — the strip's
   JavaScript is null-guarded and goes inert. If you do delete it, load the
   page and check the browser console is clean, because a dead listener here
   stops the whole script and the page then quietly never updates. Skip the
   web-call button unless asked. Both are additive later.
8. Deploy. Order matters here, and three of these steps are easy to get wrong:

       # Railway detects Node from package.json. The skeleton has no deps, but
       # without this file there is no start command and the deploy is useless.
       cat > package.json <<'JSON'
       { "name": "vapi-demo", "private": true, "type": "module",
         "scripts": { "start": "node server.mjs" }, "engines": { "node": ">=20" } }
       JSON

       railway init --name <demo-name>        # or railway link for an existing project
       railway up --detach --service <demo-name>
       railway variables --set "KEY=value"    # ONLY works after a service exists
       railway domain                         # prints the public URL, or makes one
       curl <url>/health                      # until {"ok":true}; ~30s on a cold project

   `railway variables` before the first `railway up` fails with "Project has no
   services". Later deploys need `--service <name>` once the CLI reports the
   linked service as None. `railway domain` is what turns a running service into
   a URL you can hand to Vapi.
9. Wire the assistant — record the old value FIRST, then patch:

       curl -s https://api.vapi.ai/assistant/$ID -H "Authorization: Bearer $KEY" \
         | tee assistant-before.json | jq '{server, serverMessages}'

       curl -s -X PATCH https://api.vapi.ai/assistant/$ID \
         -H "Authorization: Bearer $KEY" -H 'Content-Type: application/json' \
         -d '{"server": {"url": "https://<your-app>.up.railway.app/vapi"},
              "serverMessages": ["status-update","transcript","conversation-update","end-of-call-report"]}'

   Rollback is PATCHing back the `server` and `serverMessages` from
   `assistant-before.json`. 🔴 Before this step, confirm every tool on the
   assistant has its OWN `server.url` ([wiring-rules.md](references/wiring-rules.md)
   explains why).

   **Squad id instead of an assistant id?** `server` and `serverMessages`
   live on ASSISTANTS, never on the squad object. Resolve the members first:

       curl -s https://api.vapi.ai/squad/$SQUAD_ID -H "Authorization: Bearer $KEY" \
         | jq '[.members[] | {assistantId, hasInline: (.assistant != null)}]'

   Then run step 9 once per member `assistantId` (record each before-file).
   🔴 **Every member, without exception.** `server.url` and `serverMessages`
   are read off the ACTIVE assistant, not the call, so an unwired member takes
   over mid-call and the board goes dark exactly when the handoff happens.
   All members share one call id, so the one dashboard shows the whole call
   across handoffs with no extra work. Add `assistant.started` to
   `serverMessages` for squads, and use `assets/squad-panel.html` as the
   right panel: it lights up whichever member is talking. Members defined INLINE in the squad
   (no assistantId) must be wired by PATCHing the squad's own `members`
   array to add `server` + `serverMessages` inside each inline assistant —
   record the full squad JSON first.
10. Replay `scripts/try-it.sh` against the deployed `/vapi`, then dial the
    agent's real number and watch the board. If a panel stays empty, redeploy
    with `DEBUG_BODIES=1` set as a Railway variable and read the raw webhook
    bodies in the Railway logs.

**Testing locally before deploying?** A cloudflared quick tunnel works for
WEBHOOK ingress (point the assistant's server.url at it) but does NOT stream
SSE — the page loads and then nothing moves, with no error anywhere (verified
live: 200 + correct headers, zero body bytes, padding did not help). Watch the
dashboard on localhost while the tunnel carries webhooks. Railway streams SSE
correctly once deployed.

## Phase 1 — Discovery (before any code)

Find the demo's MOMENTS, the 3–5 seconds where a Vapi feature becomes visible,
then design panels around them. **Skip this phase entirely on the Cold start
path.** The questions to ask, one at a time, and the standard layout every demo
starts from are in [discovery.md](references/discovery.md). Only the RIGHT PANEL
is a design decision.

## Phase 2 — Prerequisites gate (all of it BEFORE building)

Batch every environment question here so nothing interrupts the build later.

- `railway whoami` — logged in? If not: `railway login`. Which workspace/project
  (new `railway init` vs existing `railway link`)?
- Node 20+ locally (`node --version`) — the skeleton is dependency-free ESM.
- A Vapi API key for the org that owns the agent, provided by the user. Store it
  ONLY in env vars / Railway variables, never in the repo.
- Which assistant/squad id, and does the user have edit rights on it?
- Brand assets, only if the demo should carry the user's brand instead of
  Vapi's: logo, colors, font files. Never fetch fonts from a CDN at demo time.

## Phase 3 — Read the target and AUDIT it against the dashboard (read-only)

Pull the assistant (or squad + members) and every tool by id into `configs/`,
then check each config against the dashboard you are about to ship, using the
table in [target-audit.md](references/target-audit.md). It covers transcriber
final semantics, tools without their own `server.url`, a load-bearing
`server.url`, `phone-call-control`, `maxDurationSeconds`, structured outputs,
and where a squad's handoff tools actually live. Ten minutes here prevents the
worst demo failure, which is discovering an incompatibility with the room
watching.

## Phase 4 — Scaffold

Copy `assets/server-skeleton.mjs` (rename to `server.mjs`, add `public/`),
start the dashboard from `assets/demo-dashboard.html` — a complete, sanitized,
production-tested page carrying the default look above plus every behaviour the
demo-craft reference argues for: idle placeholders, a reset that clears state,
the stale-event guard, the live-state fallback, the authoritative transcript
correction, tool cards, and the self-hiding assistant-request strip with manual
flatten/expand. Replace the ride-specific right panel with `squad-panel.html`,
`report-panel.html`, or your own. Keep the shell and header as they are.

The example is self-contained (logo and favicon are inlined) except for the
Avantt / Foundry Gridnik font files, which its `@font-face` blocks reference at
`/fonts/`. Those are Vapi's licensed fonts and are NOT shipped in this skill.
Without them the font stacks fall back cleanly and the page still reads as Vapi.
The page is branded already: when you write new markup, use only the color
tokens and type rules in [branding.md](references/branding.md). If the user
wants their own brand instead of Vapi's, the same file covers swapping the
logo, colors, and fonts. Do that only when they ask for it.

Optional pieces:

- **Assistant-request strip** — only if the number can be detached from the
  assistant (that phone number then answers NOTHING without the demo server up;
  get explicit approval, record the prior `assistantId`).
- **Web-call button** — `assets/webcall-button.html` (client) + the
  `/webcall-token` block already in the skeleton (server). Needs VAPI_ORG_ID,
  VAPI_PRIVATE_KEY, ASSISTANT_ID, PUBLIC_ORIGIN in Railway variables.

## Phase 5 — Wiring rules (where demos break agents)

Read [wiring-rules.md](references/wiring-rules.md) before step 9 of the Default
path. The short version: observe tools through `conversation-update`, never by
taking tool webhooks; 🔴 retargeting `assistant.server.url` silently breaks any
tool without its own `server.url`; list `transcript` in `serverMessages`
explicitly and never add `phone-call-control`; read the active squad member off
`message.assistant`; and answer an assistant-request inside 7.5 seconds.

## Phase 6 — Deploy and verify THE DEMO (not the agent)

1. `railway up --detach`, set variables, `curl /health` until live.
2. **Byte-diff the deployed page against the local file** — Railway serves the
   last image, and "deployed = HEAD" is an assumption until checked.
3. **Synthetic webhook probes**: replay `scripts/try-it.sh` against the
   deployed `/vapi` (or hand-craft bodies for the use-case panel) and watch the
   panels move. This exercises the whole demo with zero calls placed.
4. Screenshot the states that matter (idle, mid-call, ended, reset) and LOOK at
   them — DOM assertions pass while the screen shows empty cards.
5. A live-call rehearsal is out of scope here — dial the demo line yourself and
   watch the board. Automated call testing and agent-side changes are outside
   this skill entirely; use `create-call` or `simulations` for testing, and
   `create-assistant` or `create-squad` for agent changes.

## Demo craft — what makes it land

Read [demo-craft.md](references/demo-craft.md) before changing any panel's
behaviour. It explains why the example does what it does: slowing real steps to
a readable pace, idle states, a reset that clears state, stale-event guards,
deriving "live" from any content event, the watermark transcript model, and
correcting the live transcript from `conversation-update`.

## Files in this skill

- `assets/demo-dashboard.html` — the full worked example (ride-booking
  scenario), every pattern above implemented and demo-proven. It pairs with the
  server skeleton out of the box: copy both into a folder, `node server.mjs`,
  then `bash scripts/try-it.sh` replays a scripted call through every panel —
  no Vapi account, no phone call.
- `scripts/try-it.sh` — that scripted call, paced like a real conversation;
  also the template for probing any generated demo before dialing.
- `assets/server-skeleton.mjs` — dependency-free observer server: SSE with
  boot-token resume, webhook ingest, tool observation, optional
  assistant-request + web-call token blocks.
- `assets/squad-panel.html` — the right panel for a squad demo: every member
  listed, the one speaking lit up, handoffs marked. Includes the server half
  (roster fetch plus active-member detection). Use this whenever the target is
  a squad; use the report panel otherwise.
- `assets/report-panel.html` — the default right panel: a "Call outcome"
  card filled from the end-of-call report. Four copy-paste edits, no use-case
  knowledge needed. The example's own right panel is ride-specific; this is
  what replaces it.
- `assets/webcall-button.html` — the client half of the web-call button.
- `assets/demo.env.example` — the Phase 0 intake file; everything the
  builder needs from the user, with the why for each value.
- `references/discovery.md`, `references/target-audit.md`,
  `references/wiring-rules.md`, `references/demo-craft.md`,
  `references/branding.md` — the detail behind Phases 1, 3, 4 and 5 and the
  demo-craft rules.

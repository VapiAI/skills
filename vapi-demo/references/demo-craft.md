# Demo craft — what makes it land (hard-won)

- **Slow real steps down to legible speed; never invent steps.** The
  assistant-request resolution takes ~1.1s naturally — invisible. Holding the
  webhook to a ~3.5s DEADLINE (target total elapsed, never an unconditional
  sleep — a cold container's startup must eat the wait, not stack on it) makes
  four stages readable while spending half the budget. Every animated stage must
  map to work that actually happens, because someone in the room will ask.
- **Idle states everywhere.** Panels show titled placeholder cards before the
  first call — a blank dashboard on a projector reads as broken.
- **A reset button, and test it AFTER a call, not before.** Reset has to clear
  the STATE behind each panel, not just its markup. A panel blanked without its
  variables cleared looks reset until the next render restores the old view, so
  a presenter clears the board and one stale card stares back. Run a call, hit
  reset, and look at every panel.
- **Auto-collapse is a presenting decision — give a manual toggle.** The strip
  that folded itself away on call-connect got rebuilt as flatten/expand by hand.
- **Animations settle, never vanish.** Chips that fly out of a panel leave it
  empty for the rest of the call; push toward the target and return.
- **Verify each edit landed, not that "something changed".** A scripted
  multi-part edit whose only check is "the file differs" will happily apply
  four of five replacements and report success, and the missing one is found
  later by a person watching a demo. Grep for a string unique to EVERY part.
  This exact failure shipped a squad panel whose state flag was set by code
  that nothing rendered.
- **Instrument the timeline instead of screenshotting a moment.** Sampling the
  DOM every 250ms through a whole call and printing only the transitions
  answers "was the right thing lit at the right time" in one run. Screenshots
  keep landing on the wrong instant, and a page that connects mid-call replays
  the buffer instantly, collapsing every intermediate state into the final one.
- **Never let one event own a visual state.** A single lost `status-update`
  left a deployed board reading "Ringing" for an entire call while the
  transcript scrolled underneath it. Any content event proves the call is live,
  so derive the live state from transcripts and tool calls too, and treat the
  status event as a hint rather than the source of truth. The same applies to
  anything else a demo asserts once and then never re-checks.
- **Guard against stale events.** A finished call's end-of-call report arrives
  seconds after hangup — on a quick redial it lands INSIDE the next call and, if
  the page resets on any unfamiliar callId, wipes the live board. Only a
  call-opening event may claim the view (`callScopeAccept` in the example).
- **Use the watermark model for the live transcript, not prefix matching.**
  Track a `finalTextLength` per bubble: a PARTIAL replaces everything after the
  watermark, a FINAL appends and advances it. That one algorithm handles
  cumulative partials, disjoint finals, whole-utterance finals, and mid-turn
  revisions without knowing which transcriber is attached. Prefix and growth
  heuristics look equivalent and are not: they encode one vendor's habits, and
  a provider that revises a word mid-utterance produces two bubbles for one
  sentence. Two edges the watermark still does not cover, worth deciding
  explicitly: the `transcript` message carries no turn id, so consecutive turns
  from one speaker collapse into a single bubble; and Deepgram Flux can emit a
  second final for a turn (a timeout-driven synthetic end-of-turn followed by
  the real one), which appends the turn twice unless a final whose text is a
  superset of the just-finalized text replaces instead of appends.
- **Stream the transcript, but correct it from `conversation-update`.** Speech
  to text does not only append, it REVISES: "this is Sam calling for" becomes
  "this is Sam calling from the clinic", and one changed word defeats every
  prefix-based match, so the panel keeps both and the room sees the same
  sentence twice. Continuation fragments ("date.") and re-cut caller lines
  ("No. I do" then "Uh, no. I did not.") do the same. No matching heuristic
  fixes this reliably. The same `conversation-update` you already subscribe to
  carries the platform's OWN merged history, one message per turn with the
  speaking member named, so rewrite the settled turns from it at every turn
  boundary and re-append whatever is still being spoken. Live for immediacy,
  authoritative for truth: fragments appear for about a second and then heal.
  One honest limit: the LIVE `conversation-update` does not merge consecutive
  same-speaker user finals (only consecutive bot messages are merged; full
  merging happens in the end-of-call artifact). So on a multi-final provider a
  single spoken sentence can settle as several caller bubbles. The correction
  fixes revision duplicates, not fragment counts, which is the other reason to
  get the live watermark model right rather than lean on the correction alone.
- **Transcript partials/finals also reorder in transit** — reconcile by content,
  not arrival order (renderer in the example handles duplicates, late partials,
  and growth-merge).
- **Read the call record before blaming the dashboard.** `GET /call/:id` returns
  the merged `messages`. If a wrong word is in there too it is a speech-to-text
  problem to fix on the agent (add the term to the transcriber's keyterms), and
  if the record is clean but the screen is not, the bug is yours.
- **Testing trap:** a mocked clock advances JS timers but NOT CSS animations —
  content assertions pass while everything sits at opacity 0. Keep one test on a
  real clock reading `getComputedStyle(...).opacity`, and review screenshots.
- `prefers-reduced-motion`: state changes carry the meaning; motion is garnish.

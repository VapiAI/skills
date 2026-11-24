# Reading call data from the Vapi API

How to pull an assistant's or squad's production calls with the public API, and which fields carry what the flow map needs. Revalidate fields against the [API reference index](https://docs.vapi.ai/llms.txt) before relying on them; the schema evolves.

## Contents

- [Privacy first](#privacy-first)
- [Configuration](#configuration)
- [Listing calls](#listing-calls)
- [Sampling](#sampling)
- [Fields per call](#fields-per-call)
- [Messages](#messages)
- [Squads](#squads)
- [Example: list and sample in Python](#example-list-and-sample-in-python)

## Privacy first

Production calls hold callers' personal data. Before pulling anything, agree with the user where raw data lives:

- Save raw API responses only in `raw/` inside a working folder outside any git repository (for example `~/vapi-migration/<slug>/raw/`). If the folder must live inside a repository, add it to `.gitignore` first and confirm with `git check-ignore`. Delete `raw/` when the migration is done.
- Everything written outside `raw/` (records, the flow tree, the tool catalog, scenarios) holds no names, phone numbers, emails, addresses, account numbers or dates of birth. In any text taken from a transcript or tool result (notes, quotes, examples), mask digit runs of 3 or more and replace identifying values with synthetic values of the same format. Counts, call IDs and dates in the outputs stay as they are.
- Never paste transcripts into chat, tickets or shared documents.
- If the account has compliance constraints (HIPAA, PCI or similar), ask the user whether call content may be read at all, and by which tools.

## Configuration

Read the current configuration first, so every call can be measured against it:

- Assistant: `GET /assistant/{id}`. The prompt is in `model.messages` (system role), the tools in `model.tools` (inline) and `model.toolIds` (resolve each with `GET /tool/{id}`).
- Squad: `GET /squad/{id}`, then every member's assistant. Record each member's name, prompt, tools and handoff destinations.
- Transient assistant or squad: there is no stored ID. Use the configuration the user pasted, and don't read calls (SKILL.md step 2): its calls can't be reliably matched to that configuration.
- Save the responses in `raw/config_snapshot/`, with `server.url`, `server.headers` and any credential values replaced by `<redacted>`. Never copy server URLs, headers or credential values into any other output.

## Listing calls

`GET /call` returns a page of calls for the filters you give. Useful query parameters:

| Parameter | Use |
|---|---|
| `assistantId` | Calls that used this assistant |
| `phoneNumberId` | Calls on one phone number (useful for squads) |
| `createdAtGe`, `createdAtLt` | The time window |
| `limit` | Page size (default 100) |

The list endpoint has no sort or cursor parameter, so don't rely on the order calls come back in. The example below fetches a day at a time and, when a page comes back full, splits the window in half until every page is complete. Keep requests gentle: one request at a time, and windows of a day or less.

Keep only calls that ended (`status: "ended"`) and that reached a conversation: drop calls whose `endedReason` shows the call never connected (for example `customer-did-not-answer`, `voicemail` on outbound, or start errors). Count what you dropped and why.

## Sampling

Reading every call is rarely needed. Agree a sample size with the user; it is the one cost setting of this skill.

| Assistant | Suggested sample |
|---|---|
| Low traffic (under about 50 calls a day) | All calls from the last 2 to 4 weeks, up to about 300 |
| Typical | About 300 calls |
| High traffic, many intents, or a squad | 500 to 1,000 calls |

- Spread the sample across days and times of day (for example the same number of calls from each day in the window), so one busy day or one campaign doesn't dominate.
- Use a window that matches the current prompt version where possible. Calls from an old version show old behavior.
- Report the window, the calls available in it, and the sample size.

## Fields per call

| Need | Field |
|---|---|
| When | `createdAt`, `startedAt`, `endedAt` |
| How it ended | `endedReason` (for example `customer-ended-call`, `assistant-ended-call`, `assistant-forwarded-call`, `silence-timed-out`, `exceeded-max-duration`) |
| Transfers | `artifact.transfers` (destination, mode, status) and `endedReason` |
| Which assistants spoke (squads) | `artifact.assistantActivations` (ordered list of assistants that were active) |
| What was said and done | `messages` or `artifact.messages` (see below) |
| Plain transcript | `artifact.transcript` |
| Cost | `cost`, `costBreakdown` |
| Post-call data the team defined | `analysis`, `artifact.structuredOutputs` |
| Variables passed into the call | `assistantOverrides.variableValues` |

Post-call analysis and structured outputs often hold exactly the metrics the team tracks (a resolution flag, a satisfaction score, a booking outcome). Ask the user which ones matter before computing anything.

## Messages

Each entry has a `role`:

| Role | Meaning |
|---|---|
| `system` | The prompt and system notes. Skip it when reading; it repeats the configuration. |
| `bot` | Something the assistant said (`message`), with `assistantName` in squads |
| `user` | Something the caller said (`message`) |
| `tool_calls` | The assistant called one or more tools: `toolCalls[].function.name` and `.arguments` |
| `tool_call_result` | A tool answered: `name`, `result`, `toolCallId` |

From these, build per call: the ordered tool path (names), each tool's arguments and results, failed tool calls (errors or empty results), and the turn where each happened.

## Squads

- `GET /call` filters by `assistantId` but not by squad. List calls by each of the squad's phone numbers (`phoneNumberId`) and keep calls whose `squadId` matches. Listing by time window alone pulls every call in the org; use it only when the squad has no number of its own, with short windows. For outbound squads, expect high volume and sample per day.
- A call belongs to the member it started on. Record the full member path from `artifact.assistantActivations`.
- Report traffic per member as well as per conversation: how many calls reached each member and where each handed off.

## Example: list and sample in Python

```python
import os, random, requests
from datetime import datetime, timedelta, timezone

API = "https://api.vapi.ai"
HEADERS = {"Authorization": f"Bearer {os.environ['VAPI_API_KEY']}"}
ISO = "%Y-%m-%dT%H:%M:%S.%fZ"

def calls_in_window(filters, start, end, page_size=100):
    """Every call matching filters created in [start, end).
    If a page comes back full, split the window in half and fetch each half,
    so the result doesn't depend on the order the API returns calls in."""
    params = {**filters, "createdAtGe": start.strftime(ISO),
              "createdAtLt": end.strftime(ISO), "limit": page_size}
    resp = requests.get(f"{API}/call", headers=HEADERS, params=params, timeout=60)
    resp.raise_for_status()
    page = resp.json()
    if len(page) >= page_size and end - start > timedelta(seconds=1):
        mid = start + (end - start) / 2
        return (calls_in_window(filters, start, mid, page_size)
                + calls_in_window(filters, mid, end, page_size))
    return page

def sample_window(filters, first_day, last_day, per_day, seed=7):
    """Up to per_day random ended calls from each UTC day in the window.
    Returns (picked, calls_available)."""
    rng, picked, available, day = random.Random(seed), [], 0, first_day
    while day <= last_day:
        start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
        pool = [c for c in calls_in_window(filters, start, start + timedelta(days=1))
                if c.get("status") == "ended"]
        available += len(pool)
        picked += rng.sample(pool, min(per_day, len(pool)))
        day += timedelta(days=1)
    return picked, available

# Assistant: filters = {"assistantId": "<assistant-id>"}
# Squad: filters = {"phoneNumberId": "<phone-number-id>"}, then keep calls whose
#        squadId is the squad's ID. Repeat for each of the squad's numbers.
# Example, about 300 calls over the last 4 weeks:
# from datetime import date
# picked, available = sample_window({"assistantId": "<assistant-id>"},
#     date.today() - timedelta(days=28), date.today() - timedelta(days=1), per_day=11)
```

List responses are full call objects, transcripts included. Save each picked call's JSON under `raw/` as you go, and keep nothing else from the pool. Then derive the records in the skill's step 3 from those files, never from memory.

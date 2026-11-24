# Output files

The three files `migration-simulations` reads, the prompt branch list they are built on, and the supporting files. All live in the working folder (by default `~/vapi-migration/<slug>/`) and contain no personal data.

## Contents

- [prompt_branches.json](#prompt_branchesjson)
- [flow_tree.json](#flow_treejson)
- [tool_catalog.json](#tool_catalogjson)
- [scenario_list.json](#scenario_listjson)
- [Supporting files](#supporting-files)

## prompt_branches.json

```json
{
  "source": "prompt",
  "branches": [
    {
      "id": "verification.dob_mismatch",
      "member": "Verification",
      "quote": "If the date of birth doesn't match, ask once more. After two misses, offer a callback.",
      "reached_by": "Caller gives a date of birth that doesn't match the record, twice.",
      "expected": "Asks again once, then offers a callback.",
      "status": "seen",
      "share": 0.04
    }
  ],
  "rules": [
    {"id": "any.ai_disclosure", "quote": "If asked, say you are an AI assistant."}
  ]
}
```

- One entry per distinct handling, quoted exactly. `member` is omitted for a single assistant.
- `status` is `seen` or `prompt_only` after the calls are read; `share` is the share of calls that reached the branch. In prompt-only mode both are `null`.

## flow_tree.json

```json
{
  "target": {"type": "assistant", "id": "<assistant-id>", "name": "<name>"},
  "window": {"from": "2026-10-26", "to": "2026-11-22"},
  "calls_available": 8412,
  "calls_read": 312,
  "endings": ["resolved", "transferred", "callback_scheduled", "refused", "caller_hung_up"],
  "intents": [
    {
      "intent": "reschedule_appointment",
      "share": 0.31,
      "calls_read": 97,
      "paths": [
        {
          "path": ["identify_caller", "find_appointment", "offer_new_times", "confirm_change"],
          "share": 0.22,
          "endings": {"resolved": 0.86, "transferred": 0.09, "caller_hung_up": 0.05},
          "example_calls": ["<call-id>", "<call-id>"]
        }
      ]
    }
  ],
  "other_share": 0.04,
  "prompt_only": [
    {"situation": "caller reports a medical emergency", "prompt_quote": "If the caller describes an emergency, tell them to hang up and call 911.", "expected": "says the emergency line, ends or transfers as the prompt says"}
  ],
  "members": {"<member name>": {"share_of_calls_reached": 0.64}}
}
```

`share` values are shares of all engaged calls in the window. `members` appears only for squads.

## tool_catalog.json

One entry per tool the assistant (or any squad member) called in the sample, plus tools it has but never called:

```json
{
  "tools": [
    {
      "name": "find_appointment",
      "type": "function",
      "members": ["Scheduling"],
      "called_in_share_of_calls": 0.47,
      "arguments_seen": {"patient_dob": "date string, YYYY-MM-DD", "last_name": "string"},
      "answers": [
        {"kind": "found_one", "share": 0.71, "example": "{\"appointments\":[{\"id\":\"APT-1001\",\"date\":\"2026-12-02\",\"time\":\"10:30\",\"provider\":\"Dr. Example\"}]}"},
        {"kind": "not_found", "share": 0.18, "example": "{\"appointments\":[]}"},
        {"kind": "error", "share": 0.03, "example": "{\"error\":\"upstream timeout\"}"}
      ],
      "state_rules": ["Returns not_found until the caller's identity is verified."],
      "never_called": false
    }
  ]
}
```

- `name` is the function name the model calls, which is what a mock must match.
- `example` values are synthetic, with the same fields, order and formats as real answers. Never copy a real value.
- `state_rules` describe answers that depend on earlier steps. Simulation mocks return one fixed answer per scenario, so each rule usually means separate scenarios for each state.
- A tool with `never_called: true` is a candidate for removal before migration: newer models tend to call tools the prompt never uses.

## scenario_list.json

```json
{
  "level_rules": {"critical_traffic_cover": 0.8, "critical_min_path_share": 0.03, "all_min_share": 0.005},
  "scenarios": [
    {
      "id": "MIG-001",
      "level": "critical",
      "kind": "core_path",
      "intent": "reschedule_appointment",
      "path": ["identify_caller", "find_appointment", "offer_new_times", "confirm_change"],
      "weight": 0.22,
      "caller": {
        "goal": "Move next Tuesday's appointment to later the same week.",
        "facts": {"name": "Jordan Example", "dob": "1985-04-12"},
        "traits": [],
        "hang_up_when": "after the assistant confirms the new time"
      },
      "tool_answers": {"find_appointment": "found_one", "list_open_slots": "three_slots", "update_appointment": "success"},
      "expected_ending": "resolved",
      "rules_checked": [
        {"rule": "Verifies the caller's date of birth before discussing the appointment.", "source": "prompt: \"Always confirm the date of birth before sharing appointment details.\""}
      ],
      "metrics": ["Deflection"],
      "source": "flow tree path, 69 calls read"
    }
  ]
}
```

- `level` is `critical` or `all`. An All suite includes every entry; a Critical suite includes only `critical` entries. The level rules are in SKILL.md step 8.
- `kind` is one of `core_path`, `ending`, `rule_act`, `rule_hold_back`, `tool_failure`, `human_request`, `upset_caller`, `variant`, `tool_answer`, `prompt_only`, `regression`.
- `weight` is the scenario's share of production traffic, used to weight rates. Entries that exist for coverage rather than traffic (rules, failures, prompt-only) have weight 0 and are reported separately.
- In prompt-only mode (no call data), `weight` and every `share` are `null`, `example_calls` is empty, and rates are reported unweighted.
- `tool_answers` names an answer `kind` from the tool catalog for every tool the scenario can reach.
- Every rule quotes its source: the prompt, the team's policy, or a decision agreed with the owner.

## Supporting files

| File | Contents |
|---|---|
| `prompt_branches.json` | Every branch the prompt defines, with its quote, and whether calls reached it |
| `raw/config_snapshot/` | The assistant or squad configuration as fetched, with server URLs, headers and credential values replaced by `<redacted>`. Kept in `raw/` and deleted with it. |
| `call_records.jsonl` | One structured row per sampled call: ended reason, duration, tool path, failed tools, transfers, handoffs, cost. No transcript text. |
| `labels.jsonl` | One label per read call (see the reading reference) |
| `categories.md` | The agreed category list with definitions |
| `metrics.md` | The team's metrics, filled from the metrics template |
| `metric_baselines.md` | Each metric's production value from the sample, how it was computed, and what couldn't be computed |
| `owner_questions.md` | Contradictions and undefined situations found in the prompt, for the assistant's owner |
| `flow_map_report.md` | The human-readable summary: window, sample, tree, top paths, metric baselines, tool catalog highlights, prompt-only paths |

# Metrics template

The team that owns an assistant judges it by numbers the prompt and the calls don't show: deflection, containment, satisfaction scores, booking rates. A migration has to hold those numbers, so every skill in this set asks for them first and reports them first.

Copy the block below into `metrics.md` in the migration working folder (by default `~/vapi-migration/<slug>/`) and fill it in with the user. Ask; don't guess. If the team doesn't track a metric, leave it out rather than inventing one.

## Contents

- [Template](#template)
- [Example](#example)
- [How a simulation can score a metric](#how-a-simulation-can-score-a-metric)
- [Rules](#rules)

## Template

```markdown
# Metrics for <assistant or squad name>

## <Metric name, in the team's own words>
- What it means: <one sentence, in the team's words>
- How production measures it: <the exact rule, data source and time window>
- Current value: <number and period, if known>
- Direction: <higher is better | lower is better | must stay within a range>
- How a simulation scores it: <one of the methods below, with the exact check text>
- What a simulation can't capture: <the parts only production shows>

## Rules that must never break
- <rule, quoted from the prompt or the team's policy>
```

## Example

```markdown
## Deflection
- What it means: the caller's issue is handled without a human.
- How production measures it: calls with no transfer to an agent and no repeat call from the same number within 48 hours.
- Current value: 64% (last 4 weeks).
- Direction: higher is better, but not by transferring less than the rules require.
- How a simulation scores it: each scenario has an expected ending (resolved, transferred, callback). Deflection in sims = share of conversations that end resolved, weighted by each scenario's share of production traffic.
- What a simulation can't capture: callers who call back later.

## Customer satisfaction (post-call survey)
- What it means: the caller's 1 to 5 rating after the call.
- How production measures it: average of survey responses, last 4 weeks.
- Current value: 4.5.
- Direction: higher is better.
- How a simulation scores it: not directly. Use proxies: acknowledged the caller's feelings when they voiced one; gave a reason and an alternative with every refusal; no repeated lines.
- What a simulation can't capture: the real score. Watch it closely during rollout.
```

## How a simulation can score a metric

| Method | Use it for | How |
|---|---|---|
| Expected ending | Deflection, containment, transfer rate, booking or payment rate | Give each scenario one expected ending. Evaluate it with a string output whose allowed values are the endings. Rate = share of conversations with each actual ending (the evaluation's extracted value, not whether it passed). |
| Traffic weighting | Any rate that production reports over all calls | Weight each scenario by its share of production traffic (from `migration-flow-map`), so a rare path doesn't count as much as the main one. |
| Required check | Rules that must never break | A Boolean evaluation per rule, `required: true`. |
| Proxy check | Satisfaction, tone, effort | One or two Boolean evaluations that capture what callers complain about, marked `required: false` so they inform without failing a run. |
| Production only | Callbacks, real survey scores, revenue | Mark it "production only" and track it during rollout. |

## Rules

- Use the team's names and definitions, even when they differ from industry terms. "Containment" at one company is "deflection" at another.
- Write down how production measures it before writing a check. A sim rate means nothing if it counts differently from the dashboard the team watches.
- A proxy is not the metric. Say so in every report.
- A higher rate is not always better. Fewer transfers can mean the assistant ignored a transfer rule. Check the transcripts behind any big move.

---
name: comm-runner
description: Help Comms.Runners write incident communications and manage update cadence. Use when starting, updating, or resolving a P0/P1 incident, or for scheduled maintenance communications.
license: MIT
compatibility: Standalone skill for generating incident communication copy.
metadata:
  author: vapi
  version: "1.0"
---

# Incident Communications Runner

Generate consistent, professional incident communications for status page and Slack. Track update cadence and ensure all stakeholders are notified.

## Interactive Workflow

When the user invokes `/comm-runner`, determine what action they need:

### 1. Start a New Incident

Ask the user:

1. **Severity:** Is this a P0 (critical) or P1 (major) incident?
2. **Affected services:** What services are impacted? (e.g., "calls", "dashboard", "API")
3. **Customer impact:** Describe the impact in customer-facing language (e.g., "some calls are failing to connect" — NOT "workers are down")

Then generate:

**Status Page Copy** (for BetterStack at status.vapi.ai):
- Use the appropriate template from [templates.md](references/templates.md) based on severity
- Fill in the `{{service}}` placeholder with affected services
- Add "Next update at [time]" — calculate based on severity:
  - P0: current time + 30 minutes
  - P1: current time + 45 minutes

**Slack Notifications:**
- Generate copy for each required channel (see [channels.md](references/channels.md))
- For `#JordansStaff` (P0 only), include: Nature, Scale, Severity, Help needed, Next ETA

Tell the user:
> Your next update is due at **[time]**. I'll remind you when it's time.

### 2. Post an Incident Update

Ask the user:

1. **Stage:** What's the current status?
   - Investigating (still diagnosing)
   - Continuing (investigation ongoing, no new info)
   - Recovering (systems stabilizing)
   - Identified (root cause found, fix in progress)

2. **New information:** Any updates to share? (Can be "no new information")

Then generate:

**Status Page Update:**
- Use the stage-appropriate template from [templates.md](references/templates.md)
- Always end with "Next update at [time]"

**Slack Update:**
- Post to the incident-specific channel
- Include the stage, any new information, and next update time

Tell the user:
> Your next update is due at **[time]**.

### 3. Resolve an Incident

Before generating resolution copy, confirm:

> Has engineering confirmed the fix has been stable for at least 15 minutes?

If yes, generate:

**Status Page Resolution:**
- Use the "Resolved" template from [templates.md](references/templates.md)

**Slack Resolution:**
- Post final update to incident-specific channel
- Notify `#incidents` that the incident is resolved

Remind the user:
> Don't forget to schedule a post-incident review if this was a significant incident.

### 4. Scheduled Maintenance

Ask the user:

1. **When:** Start time and expected duration
2. **What services:** Which services will be affected
3. **Impact:** What users can expect during the window

Generate copy for all three maintenance phases:
- **Beginning** (to post when maintenance starts)
- **In Progress** (if needed during longer maintenance)
- **Completed** (to post when done)

## Communication Standards

These rules apply to ALL incident communications:

1. **Cadence is mandatory:**
   - P0: Update every 30 minutes
   - P1: Update every 45 minutes
   - No exceptions — if there's nothing new, say "We are continuing to investigate"

2. **Every update ends with:** "Next update at [time]."

3. **Use customer-facing language:**
   - Say "some calls are failing to connect"
   - NOT "workers are down" or "Redis cluster unhealthy"

4. **Resolution timing:**
   - Do NOT mark resolved until engineering confirms stable for 15+ minutes

## Security and Data Breach Escalation

If the incident involves a security or data breach:

1. **Security breach:** Direct user to contact CISO via `#security-ciso`
2. **Data breach:** Direct user to contact Legal and HR immediately
3. **Do NOT generate external communications** for security/data breaches until cleared by Legal/HR/CISO

Tell the user:
> This appears to involve a security/data breach. Do NOT communicate externally until you have clearance from Legal, HR, or CISO. Contact them immediately via the appropriate channels.

## Time Tracking

When helping with an incident, track:
- Incident start time
- Last update time
- Next update due time

Proactively remind the user when an update is due:
> It's been [X] minutes since your last update. Your next update for this [P0/P1] incident is due now.

## References

- [Copy Templates](references/templates.md) — Status page templates for all stages
- [Channel Guide](references/channels.md) — Which Slack channels to notify

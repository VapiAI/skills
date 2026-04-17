# Slack Channel Guide

## Channel Checklist by Severity

| Channel | Purpose | P0 | P1 |
|---------|---------|:--:|:--:|
| Incident-specific channel | All detailed updates (created by Incident Commander) | Required | Required |
| `#incidents` | Notify that incident channel exists, link to it | Required | Required |
| `#general` | Link to Status Page for visibility | Required | — |
| `#JordansStaff` | Executive summary with nature, scale, severity, help needed | Required | — |

## Channel Details

### Incident-Specific Channel
- **Created by:** Incident Commander (Core or Product Runner)
- **Naming:** Typically `#incident-YYYY-MM-DD-description` or similar
- **Content:** All technical updates, investigation progress, timeline
- **Audience:** Engineering, on-call responders, Comms.Runner

### #incidents
- **Purpose:** Central hub so anyone can find active incidents
- **What to post:** Brief notification that an incident is in progress with link to the specific channel
- **When:** At incident start and resolution

### #general (P0 only)
- **Purpose:** Company-wide visibility for critical incidents
- **What to post:** Link to status page, brief impact description
- **When:** P0 incidents only — do not use for P1

### #JordansStaff (P0 only)
- **Purpose:** Executive leadership updates
- **What to post:** Structured update with:
  - **Nature:** What is happening
  - **Scale:** How many customers/calls affected
  - **Severity:** Business impact
  - **Help needed:** Any asks from leadership
  - **Next ETA:** When to expect next update
- **When:** P0 incidents only, at key milestones

## Update Cadence Reminder

| Severity | Update Frequency | Channels to Update |
|----------|-----------------|-------------------|
| P0 | Every 30 minutes | Incident channel, status page, #JordansStaff if significant change |
| P1 | Every 45 minutes | Incident channel, status page |

Even if there's no new information, post an update: "We are continuing to investigate. Next update at [time]."

## Do NOT Post To

- Customer-facing Slack channels (use email or direct outreach)
- Public social media (requires separate approval)
- Any external channel for security/data breaches (requires Legal/CISO clearance)

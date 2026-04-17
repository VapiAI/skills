# Status Page Copy Templates

Use these templates for BetterStack status page updates at status.vapi.ai. Replace `{{service}}` with the affected services and `{{time}}` with the next update time.

## Minor Incident (P1)

### Investigating
> We are investigating reports of degraded performance affecting {{service}}. Our team is actively working to determine the root cause and will provide the next update within {{time}}.

### Continuing
> We are continuing to investigate degraded performance affecting {{service}}. We will provide our next update at {{time}}.

### Recovering
> We are observing systems recover and performance is returning to normal. Some users may still see brief residual impact as systems stabilize. Next update at {{time}}.

### Identified / Mitigating
> We have identified the cause of the issue and are actively deploying mitigations to restore normal performance. Some users may still experience intermittent degradation while fixes roll out. Next update at {{time}}.

### Resolved
> The issue has been resolved, and all systems are operating normally. We will continue monitoring to ensure stability.

---

## Major Incident (P0)

### Investigating
> We are investigating a service disruption that is impacting {{service}}. Our engineering team is actively diagnosing the issue and will provide updates as we learn more. Next update at {{time}}.

### Continuing
> We are continuing to investigate the service disruption affecting {{service}}. Our engineering team remains engaged. Next update at {{time}}.

### Recovering
> We are observing systems recover and performance is returning to normal. Some users may still see brief residual impact as systems stabilize. Next update at {{time}}.

### Identified / Mitigating
> The root cause has been identified and we are actively deploying fixes to restore normal service. Some users may still experience failures or degraded performance while mitigation is in progress and fixes roll out. Next update at {{time}}.

### Resolved
> The incident has been resolved and platform functionality has been fully restored. We will continue monitoring and will publish additional details if necessary.

---

## Scheduled Maintenance

### Beginning
> Scheduled maintenance is about to begin and is expected to complete by {{time}}. During this window, {{service}} may experience temporary disruption or reduced performance.

### In Progress
> Maintenance is currently in progress. {{service}} may be temporarily unavailable while updates are being deployed. Expected completion at {{time}}.

### Completed
> Scheduled maintenance has been completed, and all services are operating normally.

---

## Slack Message Templates

### Incident Channel Notification (#incidents)

**New Incident:**
> :rotating_light: **[P0/P1] Incident in Progress**
> Impact: {{brief description of customer impact}}
> Channel: #{{incident-channel-name}}
> Status Page: https://status.vapi.ai

**Resolution:**
> :white_check_mark: **Incident Resolved**
> The incident in #{{incident-channel-name}} has been resolved. All systems operating normally.

### Executive Update (#JordansStaff) — P0 Only

> **Incident Update**
> - **Nature:** {{what is happening}}
> - **Scale:** {{how many customers/calls affected}}
> - **Severity:** {{impact on customer operations}}
> - **Help needed:** {{any asks from leadership}}
> - **Next internal update:** {{time}}

### General Channel (#general) — P0 Only

> :warning: We are currently experiencing an incident affecting {{service}}. 
> Status: https://status.vapi.ai
> Updates: #{{incident-channel-name}}

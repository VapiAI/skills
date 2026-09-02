# Campaign REST API Reference

Use these REST examples only after resolving real resources and revalidating the current public schema. All requests use `https://api.vapi.ai` and a private `VAPI_API_KEY` on a trusted server.

## Contents

- Create a campaign
- Add campaign webhooks
- Duplicate or rerun
- List and inspect
- Paginate contact outcomes
- Inspect a dialed contact's call
- Cancel
- Archive
- Public API pages

## Create a campaign

```bash
curl --request POST \
  --url https://api.vapi.ai/v2/campaign \
  --header "Authorization: Bearer $VAPI_API_KEY" \
  --header "Content-Type: application/json" \
  --data '{
    "name": "Appointment reminders",
    "assistantId": "<assistant-id>",
    "phoneNumberId": "<phone-number-id>",
    "customers": [
      {
        "number": "+14155550100",
        "name": "Ada",
        "assistantOverrides": {
          "variableValues": {
            "name": "Ada",
            "appointment_date": "September 8 at 10:00 AM"
          }
        }
      }
    ],
    "maxConcurrency": 5,
    "schedulePlan": {
      "earliestAt": "<future-iso-8601-start>",
      "latestAt": "<future-iso-8601-end>"
    }
  }'
```

Use exactly one of `assistantId` and `squadId`. For a squad, put per-contact variables in `squadOverrides.variableValues` and campaign-wide values in `squadOverrides`.

For a fresh send-now campaign, omit `schedulePlan`. The current `/v2/campaign` API requires one `phoneNumberId`; do not send the legacy `dialPlan` field.

For an intentional non-E.164 number on a SIP trunk, disable E.164 validation explicitly in the API customer object:

```json
{
  "number": "1234",
  "numberE164CheckEnabled": false
}
```

With E.164 validation disabled, `number` must still contain only an optional leading `+` followed by letters or digits. Do not disable validation for ordinary PSTN destinations. The Dashboard CSV importer cannot express this customer-level flag; a `numberE164CheckEnabled` CSV column becomes a dynamic variable instead.

## Add campaign webhooks

Add these fields to the create request only when the endpoint is ready:

```json
{
  "server": {
    "url": "https://example.com/vapi/campaigns",
    "timeoutSeconds": 10,
    "credentialId": "<credential-id>"
  },
  "predialPlan": {
    "enabled": true
  },
  "serverMessages": [
    "campaign.started",
    "contact.dispatched",
    "contact.completed",
    "contact.failed",
    "contact.skipped",
    "contact.predial-failed",
    "campaign.ended",
    "campaign.cancelled",
    "campaign.archived"
  ]
}
```

The pre-dial endpoint receives a `campaign.predial` message and must answer with one of:

```json
{ "eligible": true }
```

```json
{ "eligible": false }
```

The first permits dialing. The second records `contact.skipped`. An unreachable endpoint, timeout, non-2xx response, or invalid response records `contact.predial-failed` without placing the call.

Selected lifecycle notifications use a `campaign.event` envelope with `eventType` and event-specific `data`. Acknowledge them with a 2xx response, handle duplicate delivery idempotently, and do not require arrival order.

## Duplicate or rerun

Creating a duplicate is the only rerun path:

```bash
curl --request POST \
  --url https://api.vapi.ai/v2/campaign \
  --header "Authorization: Bearer $VAPI_API_KEY" \
  --header "Content-Type: application/json" \
  --data '{
    "duplicateFromCampaignId": "<source-campaign-id>",
    "name": "Appointment reminders - rerun",
    "schedulePlan": {
      "earliestAt": "<future-iso-8601-with-safety-margin>"
    }
  }'
```

Omitted configuration and contacts inherit from the source. Supplied fields override it. A supplied `customers` array replaces the copied audience rather than appending to it. The source must be a campaign created through the current `/v2/campaign` API.

Duplication cannot unset every inherited field. Do not use it to switch between `assistantId` and `squadId`, because the old caller is inherited and the resulting request contains both. Create a fresh campaign when changing caller type or removing another inherited option.

When the duplicate should run near-immediately, generate `schedulePlan.earliestAt` immediately before the request with enough future margin to survive transport and validation, such as current UTC time plus 60 seconds. An exact current timestamp can become invalid before the server validates it. Tell the user about the short delay.

## List and inspect

```bash
# List campaign summaries. Add only documented filters needed by the request.
curl --get https://api.vapi.ai/v2/campaign \
  --header "Authorization: Bearer $VAPI_API_KEY" \
  --data-urlencode "limit=20" \
  --data-urlencode "includeCounters=true"

# Read one campaign with aggregate contact counters and call metrics.
curl --get "https://api.vapi.ai/v2/campaign/<campaign-id>" \
  --header "Authorization: Bearer $VAPI_API_KEY" \
  --data-urlencode "includeCounters=true"
```

With counters included, use:

- `contactCounters.pending` and `contactCounters.dispatched` for work not yet terminal;
- `contactCounters.completed`, `failed`, `skipped`, and `predialFailed` for final contact outcomes;
- `callMetrics.dialed` for contacts where a call was actually placed;
- `callMetrics.connected` for calls answered by a person.

Pickup rate is `connected / dialed`; voicemail does not count as connected. Guard against `dialed` being zero.

## Paginate contact outcomes

```bash
curl --get "https://api.vapi.ai/v2/campaign/<campaign-id>/contacts" \
  --header "Authorization: Bearer $VAPI_API_KEY" \
  --data-urlencode "limit=100" \
  --data-urlencode "page=1" \
  --data-urlencode "sortBy=position" \
  --data-urlencode "sortOrder=ASC"
```

The maximum documented page size is 1,000. Use repeated `status` parameters to select more than one of:

- `contact.pending`
- `contact.dispatched`
- `contact.completed`
- `contact.failed`
- `contact.skipped`
- `contact.predial-failed`

Each result can contain `id`, `number`, `name`, `status`, `callId`, `dispatchedAt`, and `endedReason`. A missing `callId` means there may be no call record to inspect. Never invent one from the contact ID.

## Inspect a dialed contact's call

```bash
curl "https://api.vapi.ai/call/<call-id>" \
  --header "Authorization: Bearer $VAPI_API_KEY"
```

Use the call's actual status, ended reason, timestamps, artifact, analysis, and logs. Redact customer data and URLs that grant access to recordings.

## Cancel

```bash
curl --request PATCH \
  --url "https://api.vapi.ai/v2/campaign/<campaign-id>" \
  --header "Authorization: Bearer $VAPI_API_KEY" \
  --header "Content-Type: application/json" \
  --data '{"status":"cancelled"}'
```

The update body must be status-only. Queued or pending dispatch stops; in-progress calls may complete. Fetch the campaign again and verify its returned status and ended reason.

## Archive

```bash
curl --request DELETE \
  --url "https://api.vapi.ai/v2/campaign/<campaign-id>" \
  --header "Authorization: Bearer $VAPI_API_KEY"
```

Delete archives the campaign. An active campaign is cancelled first. This does not undo calls, erase downstream webhook data, or guarantee deletion of call artifacts.

## Public API pages

- [Create Campaign V2](https://docs.vapi.ai/api-reference/campaigns/campaign-controller-create-v-2)
- [List Campaigns V2](https://docs.vapi.ai/api-reference/campaigns/campaign-controller-find-all-v-2)
- [Get Campaign V2](https://docs.vapi.ai/api-reference/campaigns/campaign-controller-find-one-v-2)
- [Update Campaign V2](https://docs.vapi.ai/api-reference/campaigns/campaign-controller-update-v-2)
- [Delete Campaign V2](https://docs.vapi.ai/api-reference/campaigns/campaign-controller-remove-v-2)
- [Get Campaign V2 Contacts](https://docs.vapi.ai/api-reference/campaigns/campaign-controller-get-campaign-v-2-contacts)

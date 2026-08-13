# Provider API Procedures

Read the relevant section only after choosing a provider. Revalidate every field against the current public OpenAPI before a live request.

## Contents

- [Common live procedure](#common-live-procedure)
- [Vapi-hosted US PSTN](#vapi-hosted-us-pstn)
- [SIP](#sip)
- [Twilio](#twilio)
- [Vonage and Telnyx](#vonage-and-telnyx)
- [BYO carrier or SIP trunk](#byo-carrier-or-sip-trunk)
- [Routing update](#routing-update)

## Common Live Procedure

1. Resolve the assistant or squad and read existing phone numbers.
2. Assemble the provider-specific request without secrets in files or terminal output.
3. Show the exact mutation and obtain explicit confirmation.
4. Send one request and capture its status and body without verbose credential output.
5. Re-fetch the returned ID and verify provider, route, and number or SIP URI.

```bash
curl --fail-with-body -X POST https://api.vapi.ai/phone-number \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @phone-number-payload.json
```

Do not put a secret-bearing carrier import body in a persistent payload file.

## Vapi-Hosted US PSTN

The public create schema accepts a desired area code but does not expose a public inventory-list endpoint:

```json
{
  "provider": "vapi",
  "numberDesiredAreaCode": "415",
  "assistantId": "<verified-assistant-id>",
  "name": "Main Support Line"
}
```

Use only after the area code and routing target are resolved and provisioning is confirmed.

## SIP

Use only for an explicit SIP request. The public Vapi phone-number schema accepts `sipUri`, but an external agent must not invent the Vapi realm or claim that an arbitrary URI can be provisioned. Use an exact supported URI from the user/current docs or complete setup in the secure dashboard.

## Twilio

The current public phone-number create DTO requires an owned number, `twilioAccountSid`, and either an auth-token path or API-key/API-secret path; it does not offer `credentialId` in that DTO. Prefer the secure dashboard import. If the user explicitly requires the API:

- read values from local secret environment variables;
- build and send the JSON in memory;
- disable shell tracing and verbose HTTP output;
- never echo or persist the body;
- rotate credentials if exposure is suspected.

Do not show a live-ready example containing raw credential fields.

## Vonage and Telnyx

The current public schemas use an existing Vapi credential object:

```json
{
  "provider": "telnyx",
  "number": "+14155550123",
  "credentialId": "<verified-vapi-credential-id>",
  "squadId": "<verified-squad-id>",
  "name": "Support Line"
}
```

Vonage uses the same `credentialId` pattern with `provider: "vonage"`. Never invent or expose the underlying provider credential.

## BYO Carrier or SIP Trunk

Use `provider: "byo-phone-number"` only with an existing `byo-sip-trunk` credential ID and a number shape accepted by the current schema. Keep the default E.164 validation unless the user has a documented advanced reason to disable it.

## Routing Update

Read the current object first, then send a provider-specific partial update. For example, route a Telnyx number to a verified assistant with the documented fields:

```json
{
  "provider": "telnyx",
  "assistantId": "<verified-assistant-id>"
}
```

Preserve hooks, server, fallback destination, name, SMS behavior, SIP settings, and other provider-specific configuration. Re-fetch and verify that exactly the intended route is active. If clearing an old destination requires a representation not present in the current public schema, stop and use current official guidance instead of inventing `null` semantics.

## Public Sources

- [Create Phone Number API](https://docs.vapi.ai/api-reference/phone-numbers/create)
- [Phone calling](https://docs.vapi.ai/phone-calling)
- [Import a Twilio number](https://docs.vapi.ai/phone-numbers/import-twilio)

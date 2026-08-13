---
name: create-phone-number
description: Plan, provision, import, route, update, and verify Vapi phone numbers through the public API. Use for Vapi-hosted US PSTN numbers, explicitly requested SIP addresses, Twilio/Vonage/Telnyx or BYO carrier numbers, secure credential handling, assistant or squad routing, area-code requests, outbound limitations, and phone-provider troubleshooting.
license: MIT
compatibility: Internet access and VAPI_API_KEY are required only for live Vapi API operations.
metadata:
  author: vapi
  version: "2.0"
---

# Vapi Phone Number Setup

Default to a payload or implementation plan. Provision, import, route, or release a number only when the user explicitly requests the live mutation. Require a final explicit confirmation immediately before provisioning or another potentially chargeable action.

## Security and Source Rules

- Never ask for carrier passwords, auth tokens, API keys, API secrets, or private keys in chat.
- Use an existing Vapi `credentialId` for provider imports when the current public schema supports it. If a required credential does not exist, stop and state that API prerequisite.
- If the public API requires raw carrier secrets and exposes no credential-based alternative, source them from local environment variables without displaying them, writing them to payload files, or logging the request body.
- Verify provider fields against the current [Create Phone Number API](https://docs.vapi.ai/api-reference/phone-numbers/create) or public OpenAPI schema.
- Never invent phone numbers, SIP realms, credentials, resource IDs, area-code availability, or routing destinations.

## Procedure

1. Determine the execution mode.
   - Return a payload or plan when the user asks for a draft or does not clearly authorize a live mutation.
   - For a live request, confirm that `VAPI_API_KEY` is set without printing it.

2. Choose the transport path.
   - For a nontechnical request for an ordinary number, prefer the documented Vapi-hosted US PSTN path.
   - Use SIP only when the user explicitly asks for SIP. Require an exact supported SIP URI from the user or current public API documentation; if it is unavailable, stop and state the missing prerequisite. Do not invent a regional realm.
   - Use a carrier import only when the user owns the number and the required secure credential path is available.

3. Resolve routing before mutation.
   - List or get assistants and squads through public endpoints. Match a supplied name to one resource.
   - If several resources are plausible, ask the user to choose. Never guess an ID.
   - Route to either one `assistantId` or one `squadId`; clear conflicting destination fields when changing an existing route.

4. Check inventory safely.
   - Review existing phone numbers with `GET /phone-number` to avoid duplicate provisioning.
   - The current public OpenAPI accepts `numberDesiredAreaCode` but does not expose a public available-area-code inventory endpoint. Accept the user's desired three-digit US area code after explaining that fulfillment is not guaranteed.
   - Do not purchase a number merely to test availability. Do not infer global unavailability from one provisioning response.

5. Confirm and execute.
   - Show the provider, area code or exact owned number, routing destination, and whether the action may incur carrier or usage charges.
   - Obtain explicit confirmation immediately before `POST /phone-number` or another potentially chargeable mutation.
   - Validate the response for `id`, provider, number or SIP URI, status when present, and resolved route.

6. Update without destroying configuration.
   - `GET /phone-number/{id}` first.
   - Build the provider-specific update DTO. Change only requested writable fields and preserve the current provider, hooks, server, fallback destination, and provider-specific settings by omission or exact carry-forward as required by the public schema.
   - Do not send response-only fields such as `id`, timestamps, or organization metadata.
   - Re-fetch the number and verify the requested route or setting.

7. Handle failures precisely.
   - `400`: report the rejected field or unavailable request; correct a documented shape error before at most one retry.
   - `401`/`403`: stop for Vapi authentication or permission issues.
   - `404`: report the missing phone number, assistant, squad, or credential.
   - `5xx`: report a Vapi service failure and do not claim success.
   - Separate carrier-side ownership, credential, provisioning, or transport failures from Vapi routing configuration.

## Free Vapi Number Limits

Vapi-hosted free numbers are for US national use and have a limit of five per account. The first free number can be requested without a payment method. Additional free numbers require a payment method on file, but the numbers themselves remain free.

Free Vapi numbers support outbound calls only to US `+1` destinations and do not support international calling. Use an imported provider number or supported SIP/carrier path for international use. Do not describe free numbers as unlimited production telephony.

## Payload-Only Example

This template does not provision anything:

```json
{
  "provider": "vapi",
  "numberDesiredAreaCode": "<confirmed-three-digit-area-code>",
  "assistantId": "<verified-assistant-id>",
  "name": "Main Support Line"
}
```

Read [Provider API Procedures](references/provider-api-procedures.md) for Vapi-hosted, Twilio, Vonage, Telnyx, BYO carrier, and routing examples. Keep placeholders out of live requests.

## Public Sources

- [Phone calling](https://docs.vapi.ai/phone-calling) and [Phone quickstart](https://docs.vapi.ai/quickstart/phone)
- [Create Phone Number API](https://docs.vapi.ai/api-reference/phone-numbers/create)
- [Free Vapi phone numbers](https://docs.vapi.ai/free-telephony)
- [Import a Twilio number](https://docs.vapi.ai/phone-numbers/import-twilio)

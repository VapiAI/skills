# Phone Number API Examples

Use these patterns only after resolving the desired area code, route, charges, and final provisioning confirmation. Recheck the current Create Phone Number schema before sending the request.

The current Vapi docs do not demonstrate a Server SDK resource method for phone-number provisioning. Use the public REST endpoint from TypeScript, Python, or cURL instead of guessing an SDK method.

## Conceptual JSON

```json
{
  "provider": "vapi",
  "numberDesiredAreaCode": "<confirmed-three-digit-area-code>",
  "assistantId": "<verified-assistant-id>",
  "name": "Main Support Line"
}
```

## TypeScript REST

```typescript
const phoneNumberPayload = {
  provider: "vapi",
  numberDesiredAreaCode: process.env.VAPI_DESIRED_AREA_CODE!,
  assistantId: process.env.VAPI_ASSISTANT_ID!,
  name: "Main Support Line",
};

const response = await fetch("https://api.vapi.ai/phone-number", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${process.env.VAPI_API_KEY}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify(phoneNumberPayload),
});

if (!response.ok) throw new Error(await response.text());
const phoneNumber = await response.json();
```

## Python REST

```python
import os
import requests

phone_number_payload = {
    "provider": "vapi",
    "numberDesiredAreaCode": os.environ["VAPI_DESIRED_AREA_CODE"],
    "assistantId": os.environ["VAPI_ASSISTANT_ID"],
    "name": "Main Support Line",
}

response = requests.post(
    "https://api.vapi.ai/phone-number",
    headers={"Authorization": f"Bearer {os.environ['VAPI_API_KEY']}"},
    json=phone_number_payload,
    timeout=30,
)
response.raise_for_status()
phone_number = response.json()
```

## cURL

Write the validated payload to `phone-number-payload.json`, then send it only after final provisioning confirmation:

```bash
curl --fail-with-body -X POST https://api.vapi.ai/phone-number \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @phone-number-payload.json
```

## Public Sources

- [Create Phone Number API](https://docs.vapi.ai/api-reference/phone-numbers/create)
- [Phone quickstart](https://docs.vapi.ai/quickstart/phone)
- [Server SDK quickstart](https://docs.vapi.ai/quickstart/web)

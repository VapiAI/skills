# Assistant Hooks Reference

Use hooks only when the user asks for event-based behavior during calls.

## Safety Rules

- Do not add transfer, function, SMS, notification, or webhook behavior without exact user-provided destinations, server URLs, or saved tool IDs.
- Prefer `say` and `endCall` examples when drafting creation-ready payloads because they do not require external infrastructure.
- Use Vapi API validation errors as the final authority for hook shape.

## Documented Events

| Event | Use |
| --- | --- |
| `call.ending` | Trigger behavior when a call is ending |
| `call.timeElapsed` | Trigger behavior after a specified number of seconds from call start |
| `assistant.speech.interrupted` | React when the assistant is interrupted |
| `customer.speech.interrupted` | React when the customer is interrupted |
| `customer.speech.timeout` | React when the customer does not speak within a timeout |
| `assistant.transcriber.endpointedSpeechLowConfidence` | React to low-confidence final transcripts |

## Hook Shape

```json
{
  "hooks": [
    {
      "on": "customer.speech.timeout",
      "options": {
        "timeoutSeconds": 10,
        "triggerMaxCount": 3,
        "triggerResetMode": "onUserSpeech"
      },
      "do": [
        {
          "type": "say",
          "exact": "Are you still there?"
        }
      ]
    }
  ]
}
```

Hook fields:

- `on`: event name.
- `do`: actions to perform.
- `filters`: optional conditions that must match.
- `options`: optional event-specific settings.
- `name`: optional internal name.

## Safe Actions

Say a fixed message:

```json
{
  "type": "say",
  "exact": "Are you still there?"
}
```

End the call:

```json
{
  "type": "tool",
  "tool": { "type": "endCall" }
}
```

## Exact-Value Actions

Use these only when the user supplies the required real values:

- `transferCall`: requires the exact destination number or destination configuration.
- Function tools: require a real function definition and real `server.url`, or a saved tool ID.
- External notifications: require a real saved tool, endpoint, or integration value.

Do not include placeholder strings such as example URLs, fake phone numbers, or draft IDs in a creation-ready assistant.

## Event Options

For `customer.speech.timeout`:

| Option | Type | Notes |
| --- | --- | --- |
| `timeoutSeconds` | number | Seconds to wait for customer speech |
| `triggerMaxCount` | number | Maximum triggers per call |
| `triggerResetMode` | string | Usually `never` or `onUserSpeech` |

For `call.timeElapsed`:

| Option | Type | Notes |
| --- | --- | --- |
| `seconds` | number | Seconds from call start when the hook should trigger |

For `assistant.transcriber.endpointedSpeechLowConfidence`:

| Option | Type | Notes |
| --- | --- | --- |
| `confidenceMin` | number | Minimum confidence threshold |
| `confidenceMax` | number | Maximum confidence threshold |

## Safe Examples

Prompt the caller after silence:

```json
{
  "hooks": [
    {
      "on": "customer.speech.timeout",
      "options": {
        "timeoutSeconds": 10,
        "triggerMaxCount": 3,
        "triggerResetMode": "onUserSpeech"
      },
      "do": [
        { "type": "say", "exact": "Are you still there?" }
      ]
    }
  ]
}
```

Start wrapping up before a call limit:

```json
{
  "maxDurationSeconds": 600,
  "hooks": [
    {
      "on": "call.timeElapsed",
      "options": { "seconds": 540 },
      "do": [
        { "type": "say", "exact": "We have about one minute left. Is there anything else urgent?" }
      ]
    },
    {
      "on": "call.timeElapsed",
      "options": { "seconds": 590 },
      "do": [
        { "type": "say", "exact": "Thank you for your time. I need to end the call now. Goodbye." },
        { "type": "tool", "tool": { "type": "endCall" } }
      ]
    }
  ]
}
```

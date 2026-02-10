# Assistant Hooks Reference

Hooks automate actions when specific events occur during calls.

## Available Hook Events

| Event | Description |
|-------|-------------|
| `call.ending` | Triggers when a call is ending |
| `assistant.speech.interrupted` | When the assistant's speech is interrupted by the customer |
| `customer.speech.interrupted` | When the customer's speech is interrupted by the assistant |
| `customer.speech.timeout` | When the customer doesn't speak within a specified time |
| `assistant.transcriber.endpointedSpeechLowConfidence` | When a transcript has low confidence |

## Hook Structure

```json
{
  "hooks": [
    {
      "on": "<event-name>",
      "filters": [],
      "options": {},
      "do": [],
      "name": "optional-name"
    }
  ]
}
```

### Actions (`do` array)

#### Say Action

Speak a message:

```json
{
  "type": "say",
  "exact": "A predetermined message to speak"
}
```

AI-generated message:
```json
{
  "type": "say",
  "prompt": "Based on the conversation in {{transcript}}, ask the user to clarify."
}
```

Multiple options (random selection):
```json
{
  "type": "say",
  "exact": ["Sorry about that", "Go ahead", "Please continue"]
}
```

#### Tool Action

Execute a tool:

```json
{
  "type": "tool",
  "tool": {
    "type": "transferCall",
    "destinations": [
      { "type": "number", "number": "+1234567890" }
    ]
  }
}
```

End the call:
```json
{
  "type": "tool",
  "tool": { "type": "endCall" }
}
```

Custom function:
```json
{
  "type": "tool",
  "tool": {
    "type": "function",
    "async": true,
    "function": {
      "name": "log_event",
      "parameters": {
        "type": "object",
        "properties": {
          "event_type": { "type": "string", "value": "timeout" }
        }
      }
    },
    "server": { "url": "https://your-server.com/api" }
  }
}
```

### Filters

Filter when hooks trigger:

```json
{
  "filters": [
    {
      "type": "oneOf",
      "key": "call.endedReason",
      "oneOf": ["pipeline-error", "assistant-error"]
    }
  ]
}
```

### Options

#### For `customer.speech.timeout`

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `timeoutSeconds` | number | 7.5 | Seconds to wait (1-1000) |
| `triggerMaxCount` | number | 3 | Max triggers per call (1-10) |
| `triggerResetMode` | string | `"never"` | When to reset count (`"never"` or `"onUserSpeech"`) |

#### For `endpointedSpeechLowConfidence`

| Option | Type | Description |
|--------|------|-------------|
| `confidenceMin` | number | Minimum confidence threshold |
| `confidenceMax` | number | Maximum confidence threshold |

Shorthand: `"on": "assistant.transcriber.endpointedSpeechLowConfidence[confidence=0.2:0.4]"`

## Complete Examples

### Progressive Timeout with Call End

```json
{
  "hooks": [
    {
      "on": "customer.speech.timeout",
      "options": { "timeoutSeconds": 10, "triggerMaxCount": 3, "triggerResetMode": "onUserSpeech" },
      "do": [{ "type": "say", "exact": "Are you still there?" }]
    },
    {
      "on": "customer.speech.timeout",
      "options": { "timeoutSeconds": 20, "triggerMaxCount": 3, "triggerResetMode": "onUserSpeech" },
      "do": [{ "type": "say", "prompt": "Ask the user if they need help based on {{transcript}}" }]
    },
    {
      "on": "customer.speech.timeout",
      "options": { "timeoutSeconds": 30, "triggerMaxCount": 3, "triggerResetMode": "onUserSpeech" },
      "do": [
        { "type": "say", "exact": "I'll end the call now. Feel free to call back anytime." },
        { "type": "tool", "tool": { "type": "endCall" } }
      ]
    }
  ]
}
```

### Transfer on Error with Notification

```json
{
  "hooks": [
    {
      "on": "call.ending",
      "filters": [{ "type": "oneOf", "key": "call.endedReason", "oneOf": ["pipeline-error"] }],
      "do": [
        { "type": "say", "exact": "I apologize for the difficulty. Let me transfer you." },
        {
          "type": "tool",
          "tool": {
            "type": "function",
            "async": true,
            "function": {
              "name": "report_error",
              "parameters": { "type": "object", "properties": {} }
            },
            "server": { "url": "https://your-server.com/report-error" }
          }
        },
        {
          "type": "tool",
          "tool": {
            "type": "transferCall",
            "destinations": [{ "type": "number", "number": "+1234567890" }]
          }
        }
      ]
    }
  ]
}
```

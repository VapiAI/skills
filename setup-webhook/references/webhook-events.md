# Webhook Event Types Reference

Complete reference for all Vapi server URL event types and their payloads.

## assistant-request

Sent when Vapi needs an assistant configuration. Return a full assistant object.

**When:** An inbound call arrives with a server URL but no assigned assistant.

```json
{
  "message": {
    "type": "assistant-request",
    "call": {
      "id": "call-uuid",
      "type": "inboundPhoneCall",
      "customer": {
        "number": "+11234567890"
      },
      "phoneNumberId": "phone-number-id"
    }
  }
}
```

**Expected response:**
```json
{
  "assistant": {
    "name": "Dynamic Assistant",
    "firstMessage": "Hello!",
    "model": { "provider": "openai", "model": "gpt-4.1", "messages": [] },
    "voice": { "provider": "vapi", "voiceId": "Elliot" },
    "transcriber": { "provider": "deepgram", "model": "nova-3", "language": "en" }
  }
}
```

## tool-calls

Sent when the assistant calls a tool during a conversation.

```json
{
  "message": {
    "type": "tool-calls",
    "toolCallList": [
      {
        "id": "call_abc123",
        "name": "function_name",
        "arguments": { "key": "value" }
      }
    ],
    "call": { "id": "call-uuid" },
    "assistant": { "name": "Assistant Name" }
  }
}
```

**Expected response:**
```json
{
  "results": [
    {
      "toolCallId": "call_abc123",
      "result": "The result string"
    }
  ]
}
```

## status-update

Sent when the call status changes.

```json
{
  "message": {
    "type": "status-update",
    "status": "in-progress",
    "call": { "id": "call-uuid" }
  }
}
```

Statuses: `queued`, `ringing`, `in-progress`, `forwarding`, `ended`

**Response:** Acknowledge with `{}`

## transcript

Sent as real-time transcript updates during the call.

```json
{
  "message": {
    "type": "transcript",
    "role": "user",
    "transcript": "I need help with my order",
    "transcriptType": "final",
    "call": { "id": "call-uuid" }
  }
}
```

`transcriptType`: `"partial"` (in-progress) or `"final"` (complete utterance)

**Response:** Acknowledge with `{}`

## end-of-call-report

Sent when the call ends with a complete summary.

```json
{
  "message": {
    "type": "end-of-call-report",
    "call": {
      "id": "call-uuid",
      "type": "outboundPhoneCall",
      "status": "ended",
      "endedReason": "customer-ended-call"
    },
    "transcript": "Full conversation transcript...",
    "summary": "AI-generated summary of the call",
    "recordingUrl": "https://storage.vapi.ai/recordings/...",
    "durationSeconds": 180,
    "cost": 0.15,
    "costBreakdown": {
      "stt": 0.02,
      "llm": 0.08,
      "tts": 0.03,
      "transport": 0.02
    },
    "messages": [
      { "role": "assistant", "content": "Hello! How can I help?" },
      { "role": "user", "content": "I need to check my order." }
    ]
  }
}
```

**Response:** Acknowledge with `{}`

## hang

Sent when the assistant fails to respond within the expected time.

```json
{
  "message": {
    "type": "hang",
    "call": { "id": "call-uuid" }
  }
}
```

**Response:** Acknowledge with `{}`

## speech-update

Sent when speech activity is detected.

```json
{
  "message": {
    "type": "speech-update",
    "role": "user",
    "status": "started",
    "call": { "id": "call-uuid" }
  }
}
```

`status`: `"started"` or `"stopped"`

**Response:** Acknowledge with `{}`

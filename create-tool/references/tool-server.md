# Tool Server Implementation Guide

Complete guide to building a server that handles Vapi tool calls.

## Request Format

When the assistant calls a tool, Vapi POSTs to your server URL:

```json
{
  "message": {
    "timestamp": 1678901234567,
    "type": "tool-calls",
    "toolCallList": [
      {
        "id": "toolu_01DTPAzUm5Gk3zxrpJ969oMF",
        "name": "get_weather",
        "arguments": {
          "location": "San Francisco"
        }
      }
    ],
    "toolWithToolCallList": [
      {
        "type": "function",
        "name": "get_weather",
        "parameters": {
          "type": "object",
          "properties": {
            "location": { "type": "string" }
          }
        },
        "description": "Get weather for a location",
        "server": { "url": "https://your-server.com/api" },
        "toolCall": {
          "id": "toolu_01DTPAzUm5Gk3zxrpJ969oMF",
          "type": "function",
          "function": {
            "name": "get_weather",
            "parameters": { "location": "San Francisco" }
          }
        }
      }
    ],
    "artifact": {
      "messages": []
    },
    "assistant": {
      "name": "Weather Assistant"
    },
    "call": {
      "id": "call-uuid",
      "orgId": "org-uuid",
      "type": "webCall"
    }
  }
}
```

## Response Format

Your server must return:

```json
{
  "results": [
    {
      "toolCallId": "toolu_01DTPAzUm5Gk3zxrpJ969oMF",
      "result": "San Francisco: 65°F, partly cloudy with a high of 72°F"
    }
  ]
}
```

- `toolCallId` — Must match the `id` from the request
- `result` — String that the assistant uses to respond to the caller

## Express.js Server

```typescript
import express from "express";

const app = express();
app.use(express.json());

app.post("/api/tools", async (req, res) => {
  const { message } = req.body;
  const results = [];

  for (const toolCall of message.toolCallList) {
    try {
      const result = await handleTool(toolCall.name, toolCall.arguments);
      results.push({ toolCallId: toolCall.id, result });
    } catch (error) {
      results.push({
        toolCallId: toolCall.id,
        result: `Error: ${error.message}`,
      });
    }
  }

  res.json({ results });
});

async function handleTool(name: string, args: Record<string, any>): Promise<string> {
  switch (name) {
    case "get_weather":
      return `Weather in ${args.location}: 65°F, sunny`;

    case "book_appointment":
      return `Appointment booked for ${args.date} at ${args.time}`;

    case "lookup_order":
      return `Order ${args.orderNumber}: Shipped, arriving tomorrow`;

    default:
      return `Unknown tool: ${name}`;
  }
}

app.listen(3000, () => console.log("Tool server on port 3000"));
```

## Python Flask Server

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/api/tools", methods=["POST"])
def handle_tools():
    data = request.json
    message = data["message"]
    results = []

    for tool_call in message["toolCallList"]:
        try:
            result = handle_tool(tool_call["name"], tool_call["arguments"])
            results.append({"toolCallId": tool_call["id"], "result": result})
        except Exception as e:
            results.append({"toolCallId": tool_call["id"], "result": f"Error: {str(e)}"})

    return jsonify({"results": results})

def handle_tool(name, args):
    if name == "get_weather":
        return f"Weather in {args['location']}: 65°F, sunny"
    elif name == "book_appointment":
        return f"Appointment booked for {args['date']} at {args['time']}"
    elif name == "lookup_order":
        return f"Order {args['orderNumber']}: Shipped, arriving tomorrow"
    else:
        return f"Unknown tool: {name}"

if __name__ == "__main__":
    app.run(port=3000)
```

## Serverless Function (Vercel)

```typescript
export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const { message } = req.body;
  const results = message.toolCallList.map((toolCall) => ({
    toolCallId: toolCall.id,
    result: handleTool(toolCall.name, toolCall.arguments),
  }));

  res.json({ results });
}

function handleTool(name, args) {
  // Your tool logic here
  return `Handled ${name}`;
}
```

## Error Handling Best Practices

1. Always return a `results` array, even for errors
2. Return user-friendly error messages (the assistant reads them to the caller)
3. Set reasonable timeouts (Vapi has a default tool timeout)
4. For long operations, use async tools so the assistant keeps talking

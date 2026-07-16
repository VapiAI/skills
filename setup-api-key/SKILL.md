---
name: setup-api-key
description: Guide users through obtaining and configuring a Vapi API key. Use when the user needs to set up Vapi, when API calls fail due to missing keys, or when the user mentions needing access to Vapi's voice AI platform.
license: MIT
compatibility: Requires internet access to vapi.ai and api.vapi.ai.
metadata:
  author: vapi
  version: "1.0"
---

# Vapi API Key Setup

Guide the user through obtaining and configuring a Vapi API key for the voice AI platform.

## Workflow

### Step 1: Request the API key

Tell the user:

> To set up Vapi, open the API keys page in the Vapi Dashboard: https://dashboard.vapi.ai/org/api-keys
>
> (Need an account? Create one at https://dashboard.vapi.ai/signup first)
>
> If you don't have an API key yet:
> 1. Click **"Create Key"**
> 2. Name your key (e.g., "development")
> 3. Copy the key immediately — it is only shown once
>
> Do not paste a private API key into this chat. Save it locally using the steps below, then tell me when the file is ready.

Then wait for the user to confirm that the local environment file is ready. Do not ask them to send or display the key.

### Step 2: Validate and configure

Once the user confirms the key is stored locally:

1. **Confirm the key is available without printing it.** Prefer an existing environment variable. Otherwise, ask the user to save it as `VAPI_API_KEY` in a local `.env.local` file using their editor. Never display the file contents.

2. **Validate the key** by making a request from the environment where it is loaded:
   ```bash
    curl -s -o /dev/null -w "%{http_code}" https://api.vapi.ai/assistant \
      -H "Authorization: Bearer $VAPI_API_KEY"
   ```

3. **If validation fails** (non-200 response):
   - Tell the user the API key appears to be invalid
   - Ask them to double-check and try again
   - Remind them of the URL: https://dashboard.vapi.ai/org/api-keys

4. **If validation succeeds**, confirm that the local environment file contains this variable without showing its value:
   ```
   VAPI_API_KEY=<the-api-key>
   ```

5. **Confirm success:**
   > Your Vapi API key is configured locally as `VAPI_API_KEY`.
   >
   > You can now use Vapi's API to create assistants, make calls, and build voice AI agents.
   >
   > Keep this key safe — do not commit it to version control.

### Step 3: Verify .gitignore

Check whether `.gitignore` protects local environment files. If not, add:
```
.env*
!.env.example
```

## Environment Variable

All Vapi skills expect the API key in the `VAPI_API_KEY` environment variable. The base URL for all API requests is:

```
https://api.vapi.ai
```

Authentication is via Bearer token:
```
Authorization: Bearer $VAPI_API_KEY
```

## Additional Resources

Vapi provides a **documentation MCP server** that gives compatible AI agents access to the Vapi knowledge base. Use its documentation search for advanced configuration, troubleshooting, SDK details, and anything beyond this skill.

**Manual setup:** If your agent doesn't auto-detect the config, run:
```bash
claude mcp add vapi-docs -- npx -y mcp-remote https://docs.vapi.ai/_mcp/server
```

See the [Vapi MCP integration guide](https://docs.vapi.ai/cli/mcp) for setup instructions across supported agents.

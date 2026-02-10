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
> Paste your API key here when ready.

Then wait for the user's next message which should contain the API key.

### Step 2: Validate and configure

Once the user provides the API key:

1. **Validate the key** by making a request:
   ```bash
   curl -s -o /dev/null -w "%{http_code}" https://api.vapi.ai/assistant \
     -H "Authorization: Bearer <the-api-key>"
   ```

2. **If validation fails** (non-200 response):
   - Tell the user the API key appears to be invalid
   - Ask them to double-check and try again
   - Remind them of the URL: https://dashboard.vapi.ai/org/api-keys

3. **If validation succeeds** (200 response), save the API key:

   Check if a `.env` file exists. If so, append to it. If not, create one:
   ```
   VAPI_API_KEY=<the-api-key>
   ```

4. **Confirm success:**
   > Your Vapi API key is configured and stored in `.env` as `VAPI_API_KEY`.
   >
   > You can now use Vapi's API to create assistants, make calls, and build voice AI agents.
   >
   > Keep this key safe — do not commit it to version control.

### Step 3: Verify .gitignore

Check if `.gitignore` exists and contains `.env`. If not, add it:
```
.env
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

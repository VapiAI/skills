# Vapi Skills

This repository contains agent skills for building voice AI with Vapi.

## MCP Documentation Server

This project includes a Vapi documentation MCP server (`vapi-docs`). Use the `searchDocs` tool to look up Vapi documentation when:

- A user asks about Vapi features not fully covered by these skills
- You need to verify API parameters, provider options, or current behavior
- You encounter errors or need troubleshooting guidance
- The user asks about SDKs, platform capabilities, or advanced configuration

The skills cover common workflows. The MCP docs server covers everything else.

## Available Skills

- `setup-api-key` — API key configuration
- `create-assistant` — Voice assistant creation
- `create-tool` — Tool/function creation for assistants
- `create-call` — Outbound call initiation
- `create-squad` — Multi-assistant squad setup
- `create-phone-number` — Phone number provisioning
- `setup-webhook` — Webhook/server URL configuration
- `create-workflow` — Conversation workflow builder
- `comm-runner` — Incident communications and update cadence management

## Configuration

All API calls require `VAPI_API_KEY` environment variable. Base URL: `https://api.vapi.ai`

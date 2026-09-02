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
- `create-structured-output` — Reusable post-call data extraction
- `create-tool` — Tool/function creation for assistants
- `create-call` — Outbound call initiation
- `create-campaign` — Persistent outbound campaign creation and management
- `create-squad` — Multi-assistant squad setup
- `create-phone-number` — Phone number provisioning
- `setup-webhook` — Webhook/server URL configuration

## Experimental Reference Workflows

- `vapi-bootstrap-framework` — Opt-in recreation of the Bun + TypeScript architecture used for Vapi's landing-page agents. Do not use it for ordinary Vapi builds; use it only when the user explicitly names the skill or specifically asks to reproduce that architecture.
- `simulations` — Realistic chat and voice simulation testing for assistants and squads

## Configuration

All API calls require `VAPI_API_KEY` environment variable. Base URL: `https://api.vapi.ai`

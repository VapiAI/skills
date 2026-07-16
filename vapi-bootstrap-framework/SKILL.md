---
name: vapi-bootstrap-framework
description: Scaffold a complete Vapi voice-agent project from a ROUGH_DRAFT.md spec. Generates package.json, tsconfig.json, .env.example, .gitignore, and the full TypeScript framework — scenario registry, per-language voice/transcriber stack, prompt composer, assistant builder, and an idempotent bootstrap script — plus one rough first-draft body.md per scenario. Drop this skill in any project's .cursor/skills/ folder (or ~/.cursor/skills/ for global use), write a ROUGH_DRAFT.md at the project root, name the skill, and `bun run bootstrap` puts the entire fleet live in dashboard.vapi.ai. Use when the user asks to scaffold or bootstrap Vapi voice agents from a rough draft, build a Vapi assistant fleet, or invokes this skill by name. Targets Bun + TypeScript + @vapi-ai/server-sdk.
license: MIT
compatibility: Requires Bun, internet access, and a Vapi private API key (VAPI_API_KEY).
metadata:
  author: vapi
  version: "1.0"
---

# Vapi bootstrap framework

Scaffold an entire Vapi voice-agent project from a single `ROUGH_DRAFT.md` spec. Works in an empty folder or alongside an existing Bun + TypeScript project. One `bun run bootstrap` after this skill finishes puts the whole fleet live in `dashboard.vapi.ai`.

## What this skill produces

**Project scaffolding** (only created if absent — never overwritten):
- `package.json` — Bun + `@vapi-ai/server-sdk` + a `bootstrap` script
- `tsconfig.json` — strict no-emit TypeScript validation
- `.env.example` — `VAPI_API_KEY` placeholder + one slot per `(scenario × language)` tuple
- `.gitignore` — `node_modules`, `.env*.local`, OS junk

**Framework spine** (always created — architectural; every later change extends a slot here, never the spine itself):
- `src/assistants/languages.ts` — per-language voice + transcriber stack
- `src/assistants/loadPrompt.ts` — `loadPrompt(scenarioId, languageId)` composer
- `src/assistants/scenarios/index.ts` — the scenario registry
- `src/assistants/buildAssistant.ts` — composes a full Vapi assistant body for any `(scenarioId, languageId)` tuple
- `src/assistants/prompts/shared/preambles/es.md` — Spanish language preamble (extend with more languages later)

**Content** (always created — one set per scenario detected in the rough draft):
- `src/assistants/scenarios/<scenarioId>.ts` — id, name, language-keyed first message
- `src/assistants/prompts/<scenarioId>/body.md` — rough first-draft system prompt
- `src/assistants/prompts/<scenarioId>/off-topic-es.md` — Spanish redirect lines

**Entry point** (always created):
- `src/bootstrap.ts` — idempotent double loop over scenarios × languages

Defaults: languages `en` + `es`. Model `openai gpt-4.1` temperature `0.5`. Voices ElevenLabs `eleven_turbo_v2` (EN) / `eleven_multilingual_v2` (ES). Transcriber Deepgram `nova-3` (EN) / Soniox `stt-rt-v4` (ES). Override these only if the user explicitly asks.

## Workflow

1. **Check for `ROUGH_DRAFT.md`** at the project root.
   - If present → continue with step 2.
   - If missing → tell the user the skill needs a rough draft to work from. Offer the template under "ROUGH_DRAFT.md template" below; either paste it in for them to fill out, or wait for them to provide their own. Don't proceed past this step without one.
2. **Detect scenarios** — every `## N. <scenario name>` heading is one scenario. Derive a snake_case `scenarioId` from the name (e.g. "Lead Qualification & Screening" → `qualification`; "Appointment Scheduling" → `appointment`). When in doubt, pick the shortest unambiguous noun. Keep ids short — they become env var names.
3. **Extract the opening line** — under each scenario, look for `**On the page**`, `**Opening**`, `**Greeting**`, or the first quoted string in the section. That's `firstMessage.en` verbatim.
4. **Distill the flow** — `**What happens**` (or equivalent prose) becomes a rough first-draft `body.md`. Persona-driven, not a contract — no failure rules, no exact wordings, no scripted off-ramps yet. Keep it short.
5. **Scaffold the project root** — for each of `package.json`, `tsconfig.json`, `.env.example`, `.gitignore`: if the file is absent, create it from the template below. If `.env.example` already exists, append any missing `VAPI_ASSISTANT_<SCENARIO>_<LANG>` slots; never reorder or remove existing lines. If `package.json` exists, leave it alone but verify it has `@vapi-ai/server-sdk` in deps plus `bootstrap` and `typecheck` scripts — tell the user if any are missing instead of editing.
6. **Generate the framework spine** — copy the five spine files verbatim from the templates below. They don't change between projects; only the scenario registry's imports do.
7. **Generate per-scenario files** — one `scenarios/<id>.ts`, one `prompts/<id>/body.md`, one `prompts/<id>/off-topic-es.md` per detected scenario.
8. **Wire up the registry** — `scenarios/index.ts` imports every scenario and exports the `SCENARIOS` const, `ScenarioId`, `SCENARIO_IDS`, `scenarioFor`.
9. **Write `src/bootstrap.ts`** with the double-loop template below.
10. **Translate first messages to Spanish** — natural Latin American Spanish, brand names untranslated.
11. **Tell the user how to run it** (see "Verification" below).

Keep each scenario's `clientTools` array empty in this skill — functional capture tools land in a follow-up step. Do **not** rewrite `body.md` as a contract here either — that's a separate step.

## File templates

Templates use these placeholders that you substitute per project:
- `<PROJECT_NAME>` — slug from the rough draft title (`# Rough draft — <X>` → snake/kebab-case of X). Fallback: `vapi-voice-agents`.
- `<SCENARIO_ID>` — snake_case scenario id (e.g. `qualification`)
- `<SCENARIO_NAME>` — human-readable name (e.g. `Lead Qualification`)
- `<FIRST_MESSAGE_EN>` — verbatim opening line from the rough draft
- `<FIRST_MESSAGE_ES>` — natural Spanish translation
- `<BODY_DRAFT>` — distilled rough first-draft prompt
- `<SCENARIO_IMPORTS>` — one `import { <id> } from "./<id>.ts";` per scenario, alphabetized
- `<SCENARIO_KEYS>` — comma-separated scenario ids inside `SCENARIOS = { ... }`
- `<ENV_ASSISTANT_SLOTS>` — one commented line per `(scenario × language)`: `# VAPI_ASSISTANT_<SCENARIO>_<LANG>=`

### `package.json` (only if absent)

```json
{
  "name": "<PROJECT_NAME>",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "bootstrap": "bun run src/bootstrap.ts",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "@vapi-ai/server-sdk": "^1.2.0"
  },
  "devDependencies": {
    "@types/bun": "^1.3.13",
    "typescript": "^5.9.3"
  },
  "packageManager": "bun@1.3.1"
}
```

### `tsconfig.json` (only if absent)

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "allowImportingTsExtensions": true,
    "noEmit": true,
    "strict": true,
    "types": ["bun"]
  },
  "include": ["src/**/*.ts"]
}
```

### `.env.example` (create if absent; extend if present)

```dotenv
# Get this from https://dashboard.vapi.ai/keys
VAPI_API_KEY=

# One slot per (scenario × language). First `bun run bootstrap` prints the
# ids; paste them here, then re-run for idempotent updates.
<ENV_ASSISTANT_SLOTS>
```

### `.gitignore` (only if absent)

```gitignore
# dependencies
node_modules

# env (local-only secrets)
.env*.local

# os junk
.DS_Store

# bun
*.tsbuildinfo
```

### `src/assistants/languages.ts`

```ts
/**
 * Per-language voice + transcriber stack. Adding a 3rd language is one
 * entry in each record below.
 */
import type { LanguageId } from "./loadPrompt.ts";

export type { LanguageId };

interface VoiceConfig {
  provider: "11labs";
  model: string;
  voiceId: string;
}

interface TranscriberConfig {
  provider: "deepgram" | "soniox";
  model: string;
  language: string;
}

const VOICE_BY_LANGUAGE: Record<LanguageId, VoiceConfig> = {
  en: {
    provider: "11labs",
    model: "eleven_turbo_v2",
    voiceId: "ZoiZ8fuDWInAcwPXaVeq",
  },
  es: {
    provider: "11labs",
    model: "eleven_multilingual_v2",
    voiceId: "JYyJjNPfmNJdaby8LdZs",
  },
};

const TRANSCRIBER_BY_LANGUAGE: Record<LanguageId, TranscriberConfig> = {
  en: { provider: "deepgram", model: "nova-3", language: "en" },
  es: { provider: "soniox", model: "stt-rt-v4", language: "es" },
};

export const voiceFor = (languageId: LanguageId): VoiceConfig =>
  VOICE_BY_LANGUAGE[languageId];

export const transcriberFor = (languageId: LanguageId): TranscriberConfig =>
  TRANSCRIBER_BY_LANGUAGE[languageId];
```

### `src/assistants/loadPrompt.ts`

```ts
/**
 * EN returns body.md unchanged. ES prepends a Spanish preamble with the
 * scenario's off-topic redirects spliced into {{OFF_TOPIC_LINES}}.
 * One body.md per scenario drives every language variant.
 */
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

export type LanguageId = "en" | "es";

const PROMPT_DIR = resolve(import.meta.dir, "prompts");

const read = (relativePath: string): string =>
  readFileSync(resolve(PROMPT_DIR, relativePath), "utf8");

export const loadPrompt = (
  scenarioId: string,
  languageId: LanguageId,
): string => {
  const body = read(`${scenarioId}/body.md`);
  if (languageId === "en") return body;

  const offTopic = read(`${scenarioId}/off-topic-${languageId}.md`).trim();
  const preamble = read(`shared/preambles/${languageId}.md`).replace(
    "{{OFF_TOPIC_LINES}}",
    offTopic,
  );
  return `${preamble}\n\n${body}`;
};
```

### `src/assistants/scenarios/index.ts`

```ts
/**
 * Scenario registry. Adding a new scenario is one entry here plus one new
 * file under `./<scenario-id>.ts` and matching prompts under `../prompts/<id>/`.
 */
<SCENARIO_IMPORTS>

export const SCENARIOS = {
  <SCENARIO_KEYS>
} as const;

export type ScenarioId = keyof typeof SCENARIOS;

export const SCENARIO_IDS = Object.keys(SCENARIOS) as ScenarioId[];

export const scenarioFor = (id: ScenarioId) => SCENARIOS[id];
```

### `src/assistants/buildAssistant.ts`

```ts
/**
 * Compose a full Vapi assistant body for a (scenario, language) tuple.
 * Voice + transcriber come from languages.ts; prompt from loadPrompt;
 * name + firstMessage + clientTools from the scenario.
 */
import { transcriberFor, voiceFor } from "./languages.ts";
import { loadPrompt, type LanguageId } from "./loadPrompt.ts";
import { scenarioFor, type ScenarioId } from "./scenarios/index.ts";

export type { LanguageId, ScenarioId };

export const buildAssistant = (
  scenarioId: ScenarioId,
  languageId: LanguageId,
) => {
  const scenario = scenarioFor(scenarioId);
  const systemPrompt = loadPrompt(scenarioId, languageId);

  return {
    name: `${languageId.toUpperCase()} - ${scenario.name}`,
    firstMessage: scenario.firstMessage[languageId],
    voice: voiceFor(languageId),
    transcriber: transcriberFor(languageId),
    model: {
      provider: "openai" as const,
      model: "gpt-4.1",
      temperature: 0.5,
      messages: [{ role: "system" as const, content: systemPrompt }],
      tools: scenario.clientTools,
    },
  };
};
```

### `src/assistants/scenarios/<SCENARIO_ID>.ts`

```ts
/**
 * <SCENARIO_NAME> scenario. Plain data: id, name, language-keyed first
 * message. Later steps add `clientTools` (capture tools fire mid-call).
 */
export const <SCENARIO_ID> = {
  id: "<SCENARIO_ID>" as const,
  name: "<SCENARIO_NAME>",
  firstMessage: {
    en: "<FIRST_MESSAGE_EN>",
    es: "<FIRST_MESSAGE_ES>",
  },
  clientTools: [] as const,
};

export type <PascalCase scenario id>Scenario = typeof <SCENARIO_ID>;
```

If `<FIRST_MESSAGE_EN>` is long, break it across concatenated string segments for readability (one logical clause per line, joined with `" + "`).

### `src/assistants/prompts/<SCENARIO_ID>/body.md`

Rough first draft — persona-driven, not a contract. Suggested shape:

```md
# <SCENARIO_NAME> voice agent

You are the <SCENARIO_NAME> voice agent for Vapi. <One sentence on context — who you're talking to and why.>

<One paragraph distilling **What happens** from the rough draft: the questions to ask, the data to collect, the routing logic, the wrap-up.>

Be warm and curious. Ask one question at a time. If they go off-topic, redirect briefly and return to the next missing field. Keep replies short — you are speaking, not typing.
```

No `## Absolute rules`, no failure rules, no scripted off-ramps. Those are a later step.

### `src/assistants/prompts/<SCENARIO_ID>/off-topic-es.md`

Two short Spanish redirect lines specific to this scenario:

```md
- "Buena pregunta — el equipo te puede ayudar con eso. ¿Podemos seguir con <next field>?"
- "Tomo nota, lo vemos después. Mientras tanto, cuéntame <one short ask tied to the scenario>."
```

### `src/assistants/prompts/shared/preambles/es.md`

```md
# IDIOMA / LANGUAGE OVERRIDE

The contract that follows this preamble is written in English. **This call is in Spanish.**

Override the language rule of the contract:

- ALL agent speech MUST be in natural, conversational Latin American Spanish. Translate the exact wordings, examples, and acks from the contract — don't switch back to English mid-sentence.
- Read brand and product names in their original form. Don't translate them.
- When you call any capture tool, **always pass free-text fields as a short English summary**, regardless of the call language. Cross-language analytics depend on it.

## Off-topic redirects (use verbatim)

If the visitor goes off-topic, pick one of these and then return to the next missing field:

{{OFF_TOPIC_LINES}}

---
```

### `src/bootstrap.ts`

```ts
/**
 * Idempotent upsert across (scenario × language). One entry per tuple, keyed
 * by VAPI_ASSISTANT_<SCENARIO>_<LANG>. First run creates + prints ids;
 * subsequent runs update in place.
 *
 * Run with `bun run bootstrap`. Bun auto-loads .env.local.
 */
import { VapiClient } from "@vapi-ai/server-sdk";

import {
  buildAssistant,
  type LanguageId,
  type ScenarioId,
} from "./assistants/buildAssistant.ts";
import { SCENARIO_IDS } from "./assistants/scenarios/index.ts";

const LANGUAGES: LanguageId[] = ["en", "es"];

const envVarFor = (scenarioId: ScenarioId, languageId: LanguageId): string =>
  `VAPI_ASSISTANT_${scenarioId.toUpperCase()}_${languageId.toUpperCase()}`;

const requireEnv = (name: string): string => {
  const value = process.env[name];
  if (!value) {
    console.error(`✗ Missing env var: ${name}. See .env.example.`);
    process.exit(1);
  }
  return value;
};

const main = async () => {
  const vapi = new VapiClient({ token: requireEnv("VAPI_API_KEY") });
  const created: Array<{ envVar: string; id: string }> = [];

  for (const scenarioId of SCENARIO_IDS) {
    for (const languageId of LANGUAGES) {
      const envVar = envVarFor(scenarioId, languageId);
      const existingId = process.env[envVar];
      const body = buildAssistant(
        scenarioId,
        languageId,
      ) as unknown as Parameters<typeof vapi.assistants.create>[0];

      const label = `${scenarioId}/${languageId}`;
      let updated = false;

      if (existingId) {
        try {
          await vapi.assistants.update({
            id: existingId,
            ...body,
          } as unknown as Parameters<typeof vapi.assistants.update>[0]);
          console.log(`✓ Updated ${label} → ${existingId}`);
          updated = true;
        } catch (err) {
          const statusCode = (err as { statusCode?: number })?.statusCode;
          if (statusCode === 404) {
            console.log(
              `  ${envVar}=${existingId} not found in this org; creating a new assistant.`,
            );
          } else {
            throw err;
          }
        }
      }

      if (!updated) {
        const assistant = await vapi.assistants.create(body);
        console.log(`✓ Created ${label} → ${assistant.id}`);
        created.push({ envVar, id: assistant.id });
      }
    }
  }

  if (created.length > 0) {
    console.log("\nAdd these to .env.local:");
    for (const { envVar, id } of created) {
      console.log(`  ${envVar}=${id}`);
    }
    console.log(
      "\nThen re-run `bun run bootstrap` to confirm idempotent updates.",
    );
  } else {
    console.log(
      `\nAll ${SCENARIO_IDS.length * LANGUAGES.length} assistants updated in place.`,
    );
  }
};

main().catch((err) => {
  console.error("✗ Bootstrap failed:", err);
  process.exit(1);
});
```

## ROUGH_DRAFT.md template

If the user has no rough draft yet, offer this skeleton (they fill in the angle-brackets and the skill scaffolds the project from it):

```md
# Rough draft — <project name>

## 1. <First scenario name>

**On the page**: "<one verbatim opening line the agent will say>"

**What happens**: <One paragraph: the questions the agent asks, the data it collects, what it does with edge cases, how it wraps up.>

## 2. <Second scenario name>

**Opening**: "<one verbatim opening line>"

**What happens**: <One paragraph.>
```

One scenario is fine. Three is fine too. The skill scales the bootstrap loop to whatever's in the rough draft.

## Adapting the defaults

If the user asks for different defaults, change only the matching slot — never the surrounding shape:

- **Different languages**: add an entry to `VOICE_BY_LANGUAGE` and `TRANSCRIBER_BY_LANGUAGE`, extend the `LanguageId` union in `loadPrompt.ts`, add a `prompts/shared/preambles/<lang>.md`, add a `firstMessage.<lang>` per scenario, add the lang to `LANGUAGES` in `bootstrap.ts`, and add the matching `VAPI_ASSISTANT_<SCENARIO>_<LANG>` slots to `.env.example`.
- **Different model / temperature**: change `buildAssistant.ts` only.
- **Different voice provider**: update `VoiceConfig` + `VOICE_BY_LANGUAGE` in `languages.ts` only.

## Verification

After generating files, tell the user to run:

```bash
bun install
bun run typecheck              # validates locally; creates nothing in Vapi
cp .env.example .env.local     # add VAPI_API_KEY from dashboard.vapi.ai/org/api-keys
bun run bootstrap              # creates one assistant per (scenario × language)
# paste the printed VAPI_ASSISTANT_<SCENARIO>_<LANG>=<id> lines into .env.local
bun run bootstrap              # second run prints "Updated ..." for every tuple
```

For N scenarios × 2 languages they should see N × 2 assistants in [dashboard.vapi.ai](https://dashboard.vapi.ai). Each one has a green "Talk to assistant" button — the agents will walk the flow but are still rough (no failure rules, no capture tools yet). That's expected; later prompts harden them.

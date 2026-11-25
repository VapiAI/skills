# Model cards

Each card describes how one target model behaves compared with a starting model, from simulations on several real-world assistants, plus its recommended settings and the fixes that worked. The `model-migration` skill loads the card that matches the migration.

The latest version of this index and of every card is at `https://raw.githubusercontent.com/VapiAI/skills/main/model-migration/references/<file>`. The copies installed with the skill are a fallback.

| Target model ID | Starting model | Card | Last updated |
|---|---|---|---|
| `gpt-5.6-terra` | GPT-4.1 | [model-card-gpt-5.6-terra.md](model-card-gpt-5.6-terra.md) | 2026-11-24 |
| `gpt-5.6-luna` | GPT-4.1 | [model-card-gpt-5.6-luna.md](model-card-gpt-5.6-luna.md) | 2026-11-24 |
| `gpt-6-luna` | GPT-4.1 | [model-card-gpt-6-luna.md](model-card-gpt-6-luna.md) | 2026-11-25 |

A migration with no matching row has no card yet: run the procedure without assuming any patterns, and explain differences only from the transcripts.

## Adding a card

Copy an existing card, keep its sections in the same order, and add a row above. Name the file `model-card-<model ID>.md`, using the exact model ID including the version, so a later version gets its own card. Link the new file from the skill's Model cards section. Every pattern needs evidence from more than one assistant; examples are anonymized.

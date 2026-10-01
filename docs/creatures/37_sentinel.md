# BRG-M37 — sentinel

Brogue kind **37**, `MK_SENTINEL`; runtime class `BrogueMonsterK37`.

## Brogue facts

> An ancient statue of an unrecognizable humanoid figure, the sentinel holds aloft a crystal that gleams with ancient warding magic. Sentinels are always found in groups, and each will attempt to repair any damage done to the others.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1098); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1286).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 3, 3, 30 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `BOLT_HEALING`, `BOLT_SPARK`, `DF_RUBBLE_BLOOD`, `MONST_CAST_SPELLS_SLOWLY`, `MONST_DIES_IF_NEGATED`, `MONST_TURRET`.
- Source action/prose strings: ["focusing on", "Focusing", "hits"]

## Model work card

- Status: authored-skeletal.
- Recipe: `weighted-sentinel`.
- Authored silhouette dimensions: 19.9058 / 26.1467 / 58.3936 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: immobile faceless indigo-stone statue on a plinth, glowing blue warding crystal held aloft, orbiting crystal shards, crystal-thrust casting pulse with a blazing shard ring, low healing ring, shattering collapse into rubble.
- [Runtime model](../../mod/BrogueDoom/models/monsters/37_sentinel.iqm).
- [Editable Blender source](../../assets/monsters/sentinel/sentinel-animated.blend).
- [Animation manifest](../../assets/monsters/sentinel/animation.json); 16 bones.
- [Shared skeletal workflow and verification](../skeletal-enemy-workflow.md).
- [Sentinel authoring and actual verification](../sentinel-animation.md).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| — | No direct table reference; may be created by another Brogue path. | — | — | — | — |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [x] Skeletal clips authored; see animation report for actual verification and approval scope.

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

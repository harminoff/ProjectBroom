# BRG-M61 — eldritch totem

Brogue kind **61**, `MK_ELDRITCH_TOTEM`; runtime class `BrogueMonsterK61`.

## Brogue facts

> This totem sits at the center of a summoning circle that radiates a strange energy.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1149); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1368).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 20, 5, 5 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_RUBBLE_BLOOD`, `MA_CAST_SUMMON`, `MONST_ALWAYS_HUNTING`, `MONST_ALWAYS_USE_ABILITY`, `MONST_GETS_TURN_ON_ACTIVATION`, `MONST_IMMOBILE`, `MONST_IMMUNE_TO_WEBS`, `MONST_INANIMATE`, `MONST_NEVER_SLEEPS`, `MONST_WILL_NOT_USE_STAIRS`.
- Source action/prose strings: ["gazing at", "Gazing", "strikes", "crackles with energy as you touch the glyph!"]

## Model work card

- Status: authored-static.
- Recipe: `totem`.
- Authored silhouette dimensions: 30 / 30 / 56 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: stone, occult, sigils.
- [Runtime model](../../mod/BrogueDoom/models/monsters/61_eldritch_totem.obj).
- [Editable Blender source](../../assets/monsters/sources/61_eldritch_totem.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L821](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L821) | leader/summoner | `MK_ELDRITCH_TOTEM` | `0`–`0` | `0` | `HORDE_IS_SUMMONED  /  HORDE_DIES_ON_LEADER_DEATH` |
| [L822](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L822) | leader/summoner | `MK_ELDRITCH_TOTEM` | `0`–`0` | `0` | `HORDE_IS_SUMMONED  /  HORDE_DIES_ON_LEADER_DEATH` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

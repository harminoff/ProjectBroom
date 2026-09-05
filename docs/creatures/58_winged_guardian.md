# BRG-M58 — winged guardian

Brogue kind **58**, `MK_WINGED_GUARDIAN`; runtime class `BrogueMonsterK58`.

## Brogue facts

> A statue of a sword-wielding angel surveys the room, connected to the glowing glyphs on the floor by invisible strands of enchantment.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1143); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1359).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 0, 0, 100 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `BOLT_BLINKING`, `DF_RUBBLE`, `DF_SILENT_GLYPH_GLOW`, `MA_REFLECT_100`, `MONST_ALWAYS_HUNTING`, `MONST_ALWAYS_USE_ABILITY`, `MONST_DIES_IF_NEGATED`, `MONST_GETS_TURN_ON_ACTIVATION`, `MONST_IMMUNE_TO_FIRE`, `MONST_IMMUNE_TO_WEAPONS`, `MONST_INANIMATE`, `MONST_NEVER_SLEEPS`, `MONST_WILL_NOT_USE_STAIRS`.
- Source action/prose strings: ["gazing at", "Gazing", "strikes"]

## Model work card

- Status: authored-static.
- Recipe: `humanoid`.
- Authored silhouette dimensions: 32 / 60 / 66 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: stone, angel, sword, wings.
- [Runtime model](../../mod/BrogueDoom/models/monsters/58_winged_guardian.obj).
- [Editable Blender source](../../assets/monsters/sources/58_winged_guardian.blend).

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
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

# BRG-M62 — mirrored totem

Brogue kind **62**, `MK_MIRRORED_TOTEM`; runtime class `BrogueMonsterK62`.

## Brogue facts

> A prism of shoulder-high mirrored surfaces gleams in the darkness.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1151); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1373).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 10, 10, 10 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `BOLT_BECKONING`, `DF_MIRROR_TOTEM_STEP`, `DF_RUBBLE_BLOOD`, `MA_REFLECT_100`, `MONST_ALWAYS_HUNTING`, `MONST_ALWAYS_USE_ABILITY`, `MONST_GETS_TURN_ON_ACTIVATION`, `MONST_IMMOBILE`, `MONST_IMMUNE_TO_FIRE`, `MONST_IMMUNE_TO_WEAPONS`, `MONST_IMMUNE_TO_WEBS`, `MONST_INANIMATE`, `MONST_NEVER_SLEEPS`, `MONST_WILL_NOT_USE_STAIRS`.
- Source action/prose strings: ["gazing at", "Gazing", "strikes"]

## Model work card

- Status: authored-skeletal.
- Recipe: `weighted-mirrored_totem`.
- Authored silhouette dimensions: 26.154 / 30.2 / 56.9 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: shoulder-high triangular mirror prism, view-dependent mirror glass, polished silver frames and crown, blue-black lacquer plinth, hidden fullbright flash crystal.
- [Runtime model](../../mod/BrogueDoom/models/monsters/62_mirrored_totem.iqm).
- [Editable Blender source](../../assets/monsters/mirrored_totem/mirrored-totem-animated.blend).
- [Animation manifest](../../assets/monsters/mirrored_totem/animation.json); 12 bones.
- [Shared skeletal workflow and verification](../skeletal-enemy-workflow.md).
- [Mirrored totem authoring and actual verification](../mirrored-totem-animation.md).

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

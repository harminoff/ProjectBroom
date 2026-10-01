# BRG-M56 — spectral sword

Brogue kind **56**, `MK_SPECTRAL_IMAGE`; runtime class `BrogueMonsterK56`.

## Brogue facts

> Eldritch energies bound up in your equipment have leapt forth to project this spectral image.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1139); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1353).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 13, 0, 0 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `MONST_DIES_IF_NEGATED`, `MONST_FLIES`, `MONST_IMMUNE_TO_WEBS`, `MONST_INANIMATE`, `MONST_NEVER_SLEEPS`, `MONST_WILL_NOT_USE_STAIRS`.
- Source action/prose strings: ["gazing at", "Gazing", "hits"]

## Model work card

- Status: authored-skeletal.
- Recipe: `weighted-spectral_image`.
- Authored silhouette dimensions: 3.1231 / 19.6995 / 47.05 map units. Clearance: 16 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: hovering point-down crimson broadsword image, straight double-edged blade with see-through fuller and engraved line, curved crossguard, front gem, wrapped grip and wheel pommel, projection scanlines, two fainter echo after-images that trail its motion, diagonal cleave leaves a fan of three swords, echoes fly apart and vanish as the sword drops flat on the floor.
- [Runtime model](../../mod/BrogueDoom/models/monsters/56_spectral_image.iqm).
- [Editable Blender source](../../assets/monsters/spectral_sword/spectral-sword-animated.blend).
- [Animation manifest](../../assets/monsters/spectral_sword/animation.json); 18 bones.
- [Shared skeletal workflow and verification](../skeletal-enemy-workflow.md).
- [Spectral sword authoring and actual verification](../spectral-sword-animation.md).

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

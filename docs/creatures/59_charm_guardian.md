# BRG-M59 — guardian spirit

Brogue kind **59**, `MK_CHARM_GUARDIAN`; runtime class `BrogueMonsterK59`.

## Brogue facts

> A spectral outline of a knight carrying a battleaxe casts an ethereal light on $HISHER surroundings.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1145); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1362).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 13, 0, 0 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `MA_REFLECT_100`, `MONST_ALWAYS_USE_ABILITY`, `MONST_DIES_IF_NEGATED`, `MONST_IMMUNE_TO_FIRE`, `MONST_IMMUNE_TO_WEAPONS`, `MONST_INANIMATE`, `MONST_NEVER_SLEEPS`.
- Source action/prose strings: ["gazing at", "Gazing", "strikes"]

## Model work card

- Status: authored-skeletal.
- Recipe: `weighted-charm_guardian`.
- Authored silhouette dimensions: 25.3744 / 44.0904 / 61.6279 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: hovering spectral knight outline, translucent crimson spectral light with a bright rim and dim core, closed crested great helm with bright visor slits, great bearded battleaxe held at port, legs and cloak hem fading to nothing, diagonal reaping cut and spike jab, empty armour collapse.
- [Runtime model](../../mod/BrogueDoom/models/monsters/59_charm_guardian.iqm).
- [Editable Blender source](../../assets/monsters/guardian_spirit/guardian-spirit-animated.blend).
- [Animation manifest](../../assets/monsters/guardian_spirit/animation.json); 19 bones.
- [Shared skeletal workflow and verification](../skeletal-enemy-workflow.md).
- [Guardian spirit authoring and actual verification](../guardian-spirit-animation.md).

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

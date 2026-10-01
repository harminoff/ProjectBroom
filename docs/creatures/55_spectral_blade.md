# BRG-M55 — spectral blade

Brogue kind **55**, `MK_SPECTRAL_BLADE`; runtime class `BrogueMonsterK55`.

## Brogue facts

> Eldritch forces have coalesced to form this flickering, ethereal weapon.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1137); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1350).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 15, 15, 60 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `MONST_DIES_IF_NEGATED`, `MONST_FLIES`, `MONST_IMMUNE_TO_WEBS`, `MONST_INANIMATE`, `MONST_NEVER_SLEEPS`, `MONST_NOT_LISTED_IN_SIDEBAR`, `MONST_WILL_NOT_USE_STAIRS`.
- Source action/prose strings: ["gazing at", "Gazing", "nicks"]

## Model work card

- Status: authored-skeletal.
- Recipe: `weighted-spectral_blade`.
- Authored silhouette dimensions: 26.4946 / 48.2482 / 55.3674 map units. Clearance: 16 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: hovering hilt-less curved blade of conjured light, white-hot cutting edge and point, see-through fuller with flickering rune dashes, glowing base knot streaming three flame-wisps, three orbiting motes, slash and whirl light trails, shatters into shards that fall to the floor.
- [Runtime model](../../mod/BrogueDoom/models/monsters/55_spectral_blade.iqm).
- [Editable Blender source](../../assets/monsters/spectral_blade/spectral-blade-animated.blend).
- [Animation manifest](../../assets/monsters/spectral_blade/animation.json); 38 bones.
- [Shared skeletal workflow and verification](../skeletal-enemy-workflow.md).
- [Spectral blade authoring and actual verification](../spectral-blade-animation.md).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L813](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L813) | member | `MK_GOBLIN_CONJURER` | `0`–`0` | `0` | `HORDE_IS_SUMMONED  /  HORDE_DIES_ON_LEADER_DEATH` |
| [L821](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L821) | member | `MK_ELDRITCH_TOTEM` | `0`–`0` | `0` | `HORDE_IS_SUMMONED  /  HORDE_DIES_ON_LEADER_DEATH` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [x] Skeletal clips authored; see animation report for actual verification and approval scope.

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

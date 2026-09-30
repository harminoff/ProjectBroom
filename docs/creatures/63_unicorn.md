# BRG-M63 — unicorn

Brogue kind **63**, `MK_UNICORN`; runtime class `BrogueMonsterK63`.

## Brogue facts

> The unicorn's flowing mane and tail shine with rainbow light, $HISHER horn glows with healing and protective magic, and $HISHER eyes implore you to always chase your dreams. Unicorns are rumored to be attracted to virgins -- is there a hint of accusation in $HISHER gaze?

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1155); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1377).

- Large flag: `true` (not a physical measurement).
- Base glyph RGB: 100, 100, 100 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `BOLT_HEALING`, `BOLT_SHIELDING`, `DF_RED_BLOOD`, `DF_UNICORN_POOP`, `MONST_FEMALE`, `MONST_MAINTAINS_DISTANCE`, `MONST_MALE`.
- Source action/prose strings: ["consecrating", "Consecrating", "pokes", "stabs", "gores"]

## Model work card

- Status: authored-skeletal.
- Recipe: `weighted-unicorn`.
- Authored silhouette dimensions: 57.7732 / 19.6421 / 66.7401 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: slender white equine, gilded spiral horn, rainbow-shaded flowing mane and tail, dark lashed eyes, feathered gilded hooves, limp side collapse.
- [Runtime model](../../mod/BrogueDoom/models/monsters/63_unicorn.iqm).
- [Editable Blender source](../../assets/monsters/unicorn/unicorn-animated.blend).
- [Animation manifest](../../assets/monsters/unicorn/animation.json); 37 bones.
- [Shared skeletal workflow and verification](../skeletal-enemy-workflow.md).
- [Unicorn authoring and actual verification](../unicorn-animation.md).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L936](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L936) | leader/summoner | `MK_UNICORN` | `1`–`DEEPEST_LEVEL` | `0` | `HORDE_MACHINE_LEGENDARY_ALLY  /  HORDE_ALLIED_WITH_PLAYER` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [x] Skeletal clips authored; see animation report for actual verification and approval scope.

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

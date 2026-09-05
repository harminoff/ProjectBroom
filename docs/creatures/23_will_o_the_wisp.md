# BRG-M23 — wisp

Brogue kind **23**, `MK_WILL_O_THE_WISP`; runtime class `BrogueMonsterK23`.

## Brogue facts

> An ethereal blue flame dances through the air, flickering and pulsing in time to an otherworldly rhythm.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1071); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1241).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 75, 100, 250 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_ASH_BLOOD`, `MA_HIT_BURN`, `MONST_DIES_IF_NEGATED`, `MONST_FIERY`, `MONST_FLIES`, `MONST_FLITS`, `MONST_IMMUNE_TO_FIRE`, `MONST_NEVER_SLEEPS`.
- Source action/prose strings: ["consuming", "Feeding", "scorches", "burns"]

## Model work card

- Status: authored-static.
- Recipe: `flame`.
- Authored silhouette dimensions: 20 / 20 / 30 map units. Clearance: 16 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: blue, flame.
- [Runtime model](../../mod/BrogueDoom/models/monsters/23_will_o_the_wisp.obj).
- [Editable Blender source](../../assets/monsters/sources/23_will_o_the_wisp.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L776](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L776) | leader/summoner | `MK_WILL_O_THE_WISP` | `10`–`17` | `0` | `0` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

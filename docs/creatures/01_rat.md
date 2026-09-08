# BRG-M01 — rat

Brogue kind **1**, `MK_RAT`; runtime class `BrogueMonsterK01`.

## Brogue facts

> The rat is a scavenger of the shallows, perpetually in search of decaying animal matter.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1030); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1171).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 50, 50, 50 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_RED_BLOOD`, `DF_URINE`.
- Source action/prose strings: ["gnawing at", "Eating", "scratches", "bites"]

## Model work card

- Status: authored-skeletal.
- Recipe: `weighted-rat`.
- Authored silhouette dimensions: 51.12 / 18.44 / 15 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: gray scavenger, articulated jaw, four-paw scurry, ear twitch, segmented tail.
- [Runtime model](../../mod/BrogueDoom/models/monsters/01_rat.iqm).
- [Editable Blender source](../../assets/monsters/rat/rat-animated.blend).
- [Animation manifest](../../assets/monsters/rat/animation.json); 28 bones.
- [Shared skeletal workflow and verification](../skeletal-enemy-workflow.md).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L746](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L746) | leader/summoner | `MK_RAT` | `1`–`5` | `0` | `0` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [x] Skeletal clips authored; see animation report for actual verification and approval scope.

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

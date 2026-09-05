# BRG-M16 — acid mound

Brogue kind **16**, `MK_ACID_MOUND`; runtime class `BrogueMonsterK16`.

## Brogue facts

> The acid mound squelches softly across the ground, leaving a trail of hissing goo in $HISHER path.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1057); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1220).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 15, 80, 25 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_ACID_BLOOD`, `MA_HIT_DEGRADE_ARMOR`, `MONST_DEFEND_DEGRADE_WEAPON`.
- Source action/prose strings: ["liquefying", "Feeding", "slimes", "douses", "drenches"]

## Model work card

- Status: authored-static.
- Recipe: `slime`.
- Authored silhouette dimensions: 34 / 32 / 20 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: goo, acid.
- [Runtime model](../../mod/BrogueDoom/models/monsters/16_acid_mound.obj).
- [Editable Blender source](../../assets/monsters/sources/16_acid_mound.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L766](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L766) | leader/summoner | `MK_ACID_MOUND` | `6`–`13` | `0` | `0` |
| [L773](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L773) | leader/summoner, member | `MK_ACID_MOUND` | `9`–`13` | `0` | `0` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

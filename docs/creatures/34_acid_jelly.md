# BRG-M34 — acidic jelly

Brogue kind **34**, `MK_ACID_JELLY`; runtime class `BrogueMonsterK34`.

## Brogue facts

> A jelly subsisting on a diet of acid mounds will eventually express the characteristics of $HISHER prey, corroding any unprotected weapons or armor that come in contact with $HIMHER.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1092); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1277).

- Large flag: `true` (not a physical measurement).
- Base glyph RGB: 15, 80, 25 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_ACID_BLOOD`, `MA_CLONE_SELF_ON_DEFEND`, `MA_HIT_DEGRADE_ARMOR`, `MONST_DEFEND_DEGRADE_WEAPON`.
- Source action/prose strings: ["transmuting", "Transmuting", "burns"]

## Model work card

- Status: authored-static.
- Recipe: `slime`.
- Authored silhouette dimensions: 52 / 48 / 32 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: goo, acid, lobes.
- [Runtime model](../../mod/BrogueDoom/models/monsters/34_acid_jelly.obj).
- [Editable Blender source](../../assets/monsters/sources/34_acid_jelly.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L788](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L788) | leader/summoner | `MK_ACID_JELLY` | `14`–`21` | `0` | `0` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

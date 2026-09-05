# BRG-M51 — goblin warlord

Brogue kind **51**, `MK_GOBLIN_CHIEFTAN`; runtime class `BrogueMonsterK51`.

## Brogue facts

> Taller, stronger and smarter than other goblins, the warlord commands the loyalty of $HISHER kind and can summon them into battle.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1127); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1333).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 0, 0, 100 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_RED_BLOOD`, `MA_ATTACKS_PENETRATE`, `MA_AVOID_CORRIDORS`, `MA_CAST_SUMMON`, `MONST_CARRY_ITEM_25`, `MONST_MAINTAINS_DISTANCE`.
- Source action/prose strings: ["chanting over", "Chanting", "slashes", "cuts", "stabs", "skewers", "lets loose a deafening war cry!"]

## Model work card

- Status: authored-static.
- Recipe: `humanoid`.
- Authored silhouette dimensions: 38 / 36 / 51 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: primate, spear, crest, fur.
- [Runtime model](../../mod/BrogueDoom/models/monsters/51_goblin_chieftan.obj).
- [Editable Blender source](../../assets/monsters/sources/51_goblin_chieftan.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L819](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L819) | leader/summoner | `MK_GOBLIN_CHIEFTAN` | `0`–`0` | `0` | `HORDE_IS_SUMMONED  /  HORDE_SUMMONED_AT_DISTANCE` |
| [L847](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L847) | leader/summoner | `MK_GOBLIN_CHIEFTAN` | `2`–`10` | `0` | `HORDE_MACHINE_BOSS` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

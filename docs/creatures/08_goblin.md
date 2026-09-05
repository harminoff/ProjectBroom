# BRG-M08 — goblin

Brogue kind **8**, `MK_GOBLIN`; runtime class `BrogueMonsterK08`.

## Brogue facts

> A filthy little primate, the tribalistic goblin often travels in packs and carries a makeshift stone spear.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1041); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1194).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 44, 33, 22 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_RED_BLOOD`, `MA_ATTACKS_PENETRATE`, `MA_AVOID_CORRIDORS`.
- Source action/prose strings: ["chanting over", "Chanting", "cuts", "stabs", "skewers"]

## Model work card

- Status: authored-static.
- Recipe: `humanoid`.
- Authored silhouette dimensions: 34 / 29 / 40 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: primate, spear, fur.
- [Runtime model](../../mod/BrogueDoom/models/monsters/08_goblin.obj).
- [Editable Blender source](../../assets/monsters/sources/08_goblin.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L757](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L757) | leader/summoner | `MK_GOBLIN` | `3`–`10` | `0` | `0` |
| [L761](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L761) | member | `MK_GOBLIN_TOTEM` | `5`–`13` | `0` | `HORDE_NO_PERIODIC_SPAWN` |
| [L767](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L767) | leader/summoner, member | `MK_GOBLIN` | `6`–`12` | `0` | `0` |
| [L778](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L778) | member | `MK_GOBLIN_TOTEM` | `10`–`17` | `0` | `HORDE_NO_PERIODIC_SPAWN` |
| [L819](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L819) | member | `MK_GOBLIN_CHIEFTAN` | `0`–`0` | `0` | `HORDE_IS_SUMMONED  /  HORDE_SUMMONED_AT_DISTANCE` |
| [L826](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L826) | leader/summoner, member | `MK_GOBLIN` | `3`–`7` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L827](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L827) | member | `MK_OGRE` | `4`–`10` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L847](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L847) | member | `MK_GOBLIN_CHIEFTAN` | `2`–`10` | `0` | `HORDE_MACHINE_BOSS` |
| [L871](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L871) | leader/summoner | `MK_GOBLIN` | `1`–`6` | `STATUE_DORMANT` | `HORDE_MACHINE_STATUE` |
| [L892](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L892) | leader/summoner | `MK_GOBLIN` | `1`–`8` | `MONSTER_CAGE_CLOSED` | `HORDE_MACHINE_KENNEL  /  HORDE_LEADER_CAPTIVE` |
| [L907](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L907) | leader/summoner | `MK_GOBLIN` | `1`–`8` | `MONSTER_CAGE_CLOSED` | `HORDE_VAMPIRE_FODDER  /  HORDE_LEADER_CAPTIVE` |
| [L925](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L925) | leader/summoner | `MK_GOBLIN` | `3`–`10` | `STATUE_INSTACRACK` | `HORDE_SACRIFICE_TARGET` |
| [L942](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L942) | leader/summoner | `MK_GOBLIN` | `1`–`10` | `0` | `HORDE_MACHINE_GOBLIN_WARREN` |
| [L944](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L944) | member | `MK_GOBLIN_TOTEM` | `5`–`13` | `0` | `HORDE_MACHINE_GOBLIN_WARREN` |
| [L945](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L945) | leader/summoner, member | `MK_GOBLIN` | `6`–`12` | `0` | `HORDE_MACHINE_GOBLIN_WARREN` |
| [L947](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L947) | member | `MK_GOBLIN_TOTEM` | `10`–`17` | `0` | `HORDE_MACHINE_GOBLIN_WARREN` |
| [L948](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L948) | leader/summoner, member | `MK_GOBLIN` | `3`–`7` | `0` | `HORDE_MACHINE_GOBLIN_WARREN  /  HORDE_LEADER_CAPTIVE` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

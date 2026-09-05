# BRG-M09 — goblin conjurer

Brogue kind **9**, `MK_GOBLIN_CONJURER`; runtime class `BrogueMonsterK09`.

## Brogue facts

> This goblin is covered with glowing sigils that pulse with power. $HESHE can call into existence phantom blades to attack $HISHER foes.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1043); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1197).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 67, 10, 100 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_RED_BLOOD`, `MA_AVOID_CORRIDORS`, `MA_CAST_SUMMON`, `MONST_CARRY_ITEM_25`, `MONST_CAST_SPELLS_SLOWLY`, `MONST_MAINTAINS_DISTANCE`.
- Source action/prose strings: ["performing a ritual on", "Performing ritual", "thumps", "whacks", "wallops", "gestures ominously!"]

## Model work card

- Status: authored-static.
- Recipe: `humanoid`.
- Authored silhouette dimensions: 24 / 32 / 40 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: primate, sigils, fur.
- [Runtime model](../../mod/BrogueDoom/models/monsters/09_goblin_conjurer.obj).
- [Editable Blender source](../../assets/monsters/sources/09_goblin_conjurer.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L758](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L758) | leader/summoner | `MK_GOBLIN_CONJURER` | `3`–`10` | `0` | `0` |
| [L768](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L768) | leader/summoner, member | `MK_GOBLIN_CONJURER` | `7`–`15` | `0` | `0` |
| [L778](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L778) | member | `MK_GOBLIN_TOTEM` | `10`–`17` | `0` | `HORDE_NO_PERIODIC_SPAWN` |
| [L813](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L813) | leader/summoner | `MK_GOBLIN_CONJURER` | `0`–`0` | `0` | `HORDE_IS_SUMMONED  /  HORDE_DIES_ON_LEADER_DEATH` |
| [L819](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L819) | member | `MK_GOBLIN_CHIEFTAN` | `0`–`0` | `0` | `HORDE_IS_SUMMONED  /  HORDE_SUMMONED_AT_DISTANCE` |
| [L893](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L893) | leader/summoner | `MK_GOBLIN_CONJURER` | `2`–`9` | `MONSTER_CAGE_CLOSED` | `HORDE_MACHINE_KENNEL  /  HORDE_LEADER_CAPTIVE` |
| [L908](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L908) | leader/summoner | `MK_GOBLIN_CONJURER` | `2`–`9` | `MONSTER_CAGE_CLOSED` | `HORDE_VAMPIRE_FODDER  /  HORDE_LEADER_CAPTIVE` |
| [L943](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L943) | leader/summoner | `MK_GOBLIN_CONJURER` | `1`–`10` | `0` | `HORDE_MACHINE_GOBLIN_WARREN` |
| [L946](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L946) | leader/summoner, member | `MK_GOBLIN_CONJURER` | `7`–`15` | `0` | `HORDE_MACHINE_GOBLIN_WARREN` |
| [L947](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L947) | member | `MK_GOBLIN_TOTEM` | `10`–`17` | `0` | `HORDE_MACHINE_GOBLIN_WARREN` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

# BRG-M10 — goblin mystic

Brogue kind **10**, `MK_GOBLIN_MYSTIC`; runtime class `BrogueMonsterK10`.

## Brogue facts

> This goblin carries no weapon, and $HISHER eyes sparkle with golden light. $HESHE can invoke a powerful shielding magic to protect $HISHER escorts from harm.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1045); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1202).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 10, 67, 100 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `BOLT_SHIELDING`, `DF_RED_BLOOD`, `MA_AVOID_CORRIDORS`, `MONST_CARRY_ITEM_25`, `MONST_MAINTAINS_DISTANCE`.
- Source action/prose strings: ["performing a ritual on", "Performing ritual", "slaps", "punches", "kicks"]

## Model work card

- Status: authored-static.
- Recipe: `humanoid`.
- Authored silhouette dimensions: 24 / 32 / 40 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: primate, golden_eyes, fur.
- [Runtime model](../../mod/BrogueDoom/models/monsters/10_goblin_mystic.obj).
- [Editable Blender source](../../assets/monsters/sources/10_goblin_mystic.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L767](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L767) | member | `MK_GOBLIN` | `6`–`12` | `0` | `0` |
| [L768](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L768) | member | `MK_GOBLIN_CONJURER` | `7`–`15` | `0` | `0` |
| [L778](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L778) | member | `MK_GOBLIN_TOTEM` | `10`–`17` | `0` | `HORDE_NO_PERIODIC_SPAWN` |
| [L828](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L828) | leader/summoner | `MK_GOBLIN_MYSTIC` | `5`–`11` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L847](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L847) | member | `MK_GOBLIN_CHIEFTAN` | `2`–`10` | `0` | `HORDE_MACHINE_BOSS` |
| [L861](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L861) | leader/summoner | `MK_GOBLIN_MYSTIC` | `2`–`8` | `0` | `HORDE_MACHINE_CAPTIVE  /  HORDE_LEADER_CAPTIVE` |
| [L894](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L894) | leader/summoner | `MK_GOBLIN_MYSTIC` | `2`–`9` | `MONSTER_CAGE_CLOSED` | `HORDE_MACHINE_KENNEL  /  HORDE_LEADER_CAPTIVE` |
| [L909](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L909) | leader/summoner | `MK_GOBLIN_MYSTIC` | `2`–`9` | `MONSTER_CAGE_CLOSED` | `HORDE_VAMPIRE_FODDER  /  HORDE_LEADER_CAPTIVE` |
| [L945](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L945) | member | `MK_GOBLIN` | `6`–`12` | `0` | `HORDE_MACHINE_GOBLIN_WARREN` |
| [L946](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L946) | member | `MK_GOBLIN_CONJURER` | `7`–`15` | `0` | `HORDE_MACHINE_GOBLIN_WARREN` |
| [L947](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L947) | member | `MK_GOBLIN_TOTEM` | `10`–`17` | `0` | `HORDE_MACHINE_GOBLIN_WARREN` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

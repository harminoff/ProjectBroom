# BRG-M33 — dar battlemage

Brogue kind **33**, `MK_DAR_BATTLEMAGE`; runtime class `BrogueMonsterK33`.

## Brogue facts

> The dar battlemage's eyes glow like embers and $HISHER hands radiate an occult heat.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1090); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1274).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 50, 50, 0 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `BOLT_DISCORD`, `BOLT_FIRE`, `BOLT_SLOW_2`, `DF_RED_BLOOD`, `MA_AVOID_CORRIDORS`, `MONST_CARRY_ITEM_25`, `MONST_FEMALE`, `MONST_MAINTAINS_DISTANCE`, `MONST_MALE`.
- Source action/prose strings: ["transmuting", "Transmuting", "cuts"]

## Model work card

- Status: authored-static.
- Recipe: `humanoid`.
- Authored silhouette dimensions: 28 / 34 / 57 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: elf, ember_eyes, hot_hands, robe.
- [Runtime model](../../mod/BrogueDoom/models/monsters/33_dar_battlemage.obj).
- [Editable Blender source](../../assets/monsters/sources/33_dar_battlemage.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L798](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L798) | member | `MK_DAR_BLADEMASTER` | `18`–`25` | `0` | `0` |
| [L806](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L806) | member | `MK_GOLEM` | `27`–`DEEPEST_LEVEL-1` | `0` | `0` |
| [L842](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L842) | leader/summoner | `MK_DAR_BATTLEMAGE` | `18`–`26` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L843](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L843) | member | `MK_TENTACLE_HORROR` | `20`–`26` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L844](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L844) | member | `MK_GOLEM` | `18`–`25` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L903](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L903) | leader/summoner | `MK_DAR_BATTLEMAGE` | `13`–`AMULET_LEVEL` | `MONSTER_CAGE_CLOSED` | `HORDE_MACHINE_KENNEL  /  HORDE_LEADER_CAPTIVE` |
| [L917](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L917) | leader/summoner | `MK_DAR_BATTLEMAGE` | `13`–`AMULET_LEVEL` | `MONSTER_CAGE_CLOSED` | `HORDE_VAMPIRE_FODDER  /  HORDE_LEADER_CAPTIVE` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

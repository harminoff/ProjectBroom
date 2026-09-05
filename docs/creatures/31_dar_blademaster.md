# BRG-M31 — dar blademaster

Brogue kind **31**, `MK_DAR_BLADEMASTER`; runtime class `BrogueMonsterK31`.

## Brogue facts

> An elf of the deep, the dar blademaster leaps toward $HISHER enemies with frightening speed to engage in deadly swordplay.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1086); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1268).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 100, 0, 100 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `BOLT_BLINKING`, `DF_RED_BLOOD`, `MA_AVOID_CORRIDORS`, `MONST_CARRY_ITEM_25`, `MONST_FEMALE`, `MONST_MALE`.
- Source action/prose strings: ["studying", "Studying", "grazes", "cuts", "slices", "slashes", "stabs"]

## Model work card

- Status: authored-static.
- Recipe: `humanoid`.
- Authored silhouette dimensions: 36 / 34 / 57 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: elf, sword, armor.
- [Runtime model](../../mod/BrogueDoom/models/monsters/31_dar_blademaster.obj).
- [Editable Blender source](../../assets/monsters/sources/31_dar_blademaster.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L775](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L775) | leader/summoner, member | `MK_DAR_BLADEMASTER` | `10`–`14` | `0` | `0` |
| [L792](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L792) | leader/summoner, member | `MK_DAR_BLADEMASTER` | `15`–`17` | `0` | `0` |
| [L798](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L798) | leader/summoner, member | `MK_DAR_BLADEMASTER` | `18`–`25` | `0` | `0` |
| [L833](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L833) | leader/summoner | `MK_DAR_BLADEMASTER` | `12`–`19` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L839](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L839) | leader/summoner | `MK_DAR_BLADEMASTER` | `18`–`26` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L840](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L840) | leader/summoner | `MK_DAR_BLADEMASTER` | `18`–`26` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L843](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L843) | member | `MK_TENTACLE_HORROR` | `20`–`26` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L844](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L844) | member | `MK_GOLEM` | `18`–`25` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L863](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L863) | leader/summoner | `MK_DAR_BLADEMASTER` | `8`–`16` | `0` | `HORDE_MACHINE_CAPTIVE  /  HORDE_LEADER_CAPTIVE` |
| [L901](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L901) | leader/summoner | `MK_DAR_BLADEMASTER` | `9`–`AMULET_LEVEL` | `MONSTER_CAGE_CLOSED` | `HORDE_MACHINE_KENNEL  /  HORDE_LEADER_CAPTIVE` |
| [L915](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L915) | leader/summoner | `MK_DAR_BLADEMASTER` | `9`–`AMULET_LEVEL` | `MONSTER_CAGE_CLOSED` | `HORDE_VAMPIRE_FODDER  /  HORDE_LEADER_CAPTIVE` |
| [L930](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L930) | leader/summoner | `MK_DAR_BLADEMASTER` | `10`–`20` | `STATUE_INSTACRACK` | `HORDE_SACRIFICE_TARGET` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

# BRG-M26 — troll

Brogue kind **26**, `MK_TROLL`; runtime class `BrogueMonsterK26`.

## Brogue facts

> An enormous, disfigured creature covered in phlegm and warts, the troll regenerates very quickly and attacks with astonishing strength. Many adventures have ended at $HISHER misshapen hands.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1076); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1250).

- Large flag: `true` (not a physical measurement).
- Base glyph RGB: 40, 60, 15 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_RED_BLOOD`, `MONST_FEMALE`, `MONST_MALE`.
- Source action/prose strings: ["eating", "Eating", "cudgels", "clubs", "bludgeons", "pummels", "batters"]

## Model work card

- Status: authored-static.
- Recipe: `humanoid`.
- Authored silhouette dimensions: 46 / 50 / 86 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: brute, warts, misshapen.
- [Runtime model](../../mod/BrogueDoom/models/monsters/26_troll.obj).
- [Editable Blender source](../../assets/monsters/sources/26_troll.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L781](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L781) | leader/summoner | `MK_TROLL` | `12`–`19` | `0` | `0` |
| [L830](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L830) | leader/summoner, member | `MK_TROLL` | `14`–`19` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L831](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L831) | member | `MK_CENTAUR` | `12`–`19` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L832](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L832) | leader/summoner | `MK_TROLL` | `17`–`19` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L833](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L833) | member | `MK_DAR_BLADEMASTER` | `12`–`19` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L836](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L836) | leader/summoner | `MK_TROLL` | `13`–`19` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L862](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L862) | leader/summoner | `MK_TROLL` | `10`–`20` | `0` | `HORDE_MACHINE_CAPTIVE  /  HORDE_LEADER_CAPTIVE` |
| [L875](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L875) | leader/summoner | `MK_TROLL` | `14`–`21` | `STATUE_DORMANT` | `HORDE_MACHINE_STATUE` |
| [L896](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L896) | leader/summoner | `MK_TROLL` | `12`–`21` | `MONSTER_CAGE_CLOSED` | `HORDE_MACHINE_KENNEL  /  HORDE_LEADER_CAPTIVE` |
| [L911](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L911) | leader/summoner | `MK_TROLL` | `10`–`19` | `MONSTER_CAGE_CLOSED` | `HORDE_VAMPIRE_FODDER  /  HORDE_LEADER_CAPTIVE` |
| [L927](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L927) | leader/summoner | `MK_TROLL` | `12`–`19` | `STATUE_INSTACRACK` | `HORDE_SACRIFICE_TARGET` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

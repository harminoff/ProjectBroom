# BRG-M18 — ogre

Brogue kind **18**, `MK_OGRE`; runtime class `BrogueMonsterK18`.

## Brogue facts

> This lumbering creature carries an enormous club that $HESHE can swing with incredible force.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1061); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1226).

- Large flag: `true` (not a physical measurement).
- Base glyph RGB: 60, 25, 25 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_RED_BLOOD`, `MA_ATTACKS_STAGGER`, `MA_AVOID_CORRIDORS`, `MONST_FEMALE`, `MONST_MALE`.
- Source action/prose strings: ["examining", "Studying", "cudgels", "clubs", "batters"]

## Model work card

- Status: authored-static.
- Recipe: `humanoid`.
- Authored silhouette dimensions: 44 / 46 / 82 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: brute, club, skin.
- [Runtime model](../../mod/BrogueDoom/models/monsters/18_ogre.obj).
- [Editable Blender source](../../assets/monsters/sources/18_ogre.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L771](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L771) | leader/summoner | `MK_OGRE` | `7`–`13` | `0` | `0` |
| [L782](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L782) | member | `MK_OGRE_TOTEM` | `12`–`19` | `0` | `HORDE_NO_PERIODIC_SPAWN` |
| [L786](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L786) | member | `MK_OGRE_SHAMAN` | `14`–`20` | `0` | `0` |
| [L814](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L814) | member | `MK_OGRE_SHAMAN` | `0`–`0` | `0` | `HORDE_IS_SUMMONED` |
| [L827](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L827) | leader/summoner | `MK_OGRE` | `4`–`10` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L829](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L829) | leader/summoner, member | `MK_OGRE` | `8`–`15` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L832](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L832) | member | `MK_TROLL` | `17`–`19` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L859](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L859) | leader/summoner | `MK_OGRE` | `4`–`13` | `0` | `HORDE_MACHINE_CAPTIVE  /  HORDE_LEADER_CAPTIVE` |
| [L872](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L872) | leader/summoner | `MK_OGRE` | `6`–`12` | `STATUE_DORMANT` | `HORDE_MACHINE_STATUE` |
| [L895](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L895) | leader/summoner | `MK_OGRE` | `7`–`17` | `MONSTER_CAGE_CLOSED` | `HORDE_MACHINE_KENNEL  /  HORDE_LEADER_CAPTIVE` |
| [L910](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L910) | leader/summoner | `MK_OGRE` | `5`–`15` | `MONSTER_CAGE_CLOSED` | `HORDE_VAMPIRE_FODDER  /  HORDE_LEADER_CAPTIVE` |
| [L926](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L926) | leader/summoner | `MK_OGRE` | `7`–`13` | `STATUE_INSTACRACK` | `HORDE_SACRIFICE_TARGET` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

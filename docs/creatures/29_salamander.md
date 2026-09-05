# BRG-M29 — salamander

Brogue kind **29**, `MK_SALAMANDER`; runtime class `BrogueMonsterK29`.

## Brogue facts

> A serpent wreathed in flames and carrying a burning lash, salamanders dwell in lakes of fire and emerge when they sense a nearby victim, leaving behind a trail of glowing embers.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1082); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1261).

- Large flag: `true` (not a physical measurement).
- Base glyph RGB: 40, 10, 0 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_ASH_BLOOD`, `DF_SALAMANDER_FLAME`, `MA_ATTACKS_EXTEND`, `MONST_FIERY`, `MONST_IMMUNE_TO_FIRE`, `MONST_MALE`, `MONST_NEVER_SLEEPS`, `MONST_SUBMERGES`.
- Source action/prose strings: ["studying", "Studying", "whips", "lashes"]

## Model work card

- Status: authored-static.
- Recipe: `serpent`.
- Authored silhouette dimensions: 54 / 50 / 70 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: naga, lash, flame, scales.
- [Runtime model](../../mod/BrogueDoom/models/monsters/29_salamander.obj).
- [Editable Blender source](../../assets/monsters/sources/29_salamander.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L785](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L785) | leader/summoner | `MK_SALAMANDER` | `13`–`20` | `LAVA` | `0` |
| [L834](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L834) | member | `MK_NAGA` | `14`–`20` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L835](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L835) | leader/summoner | `MK_SALAMANDER` | `13`–`20` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L836](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L836) | member | `MK_TROLL` | `13`–`19` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L898](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L898) | leader/summoner | `MK_SALAMANDER` | `9`–`20` | `MONSTER_CAGE_CLOSED` | `HORDE_MACHINE_KENNEL  /  HORDE_LEADER_CAPTIVE` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

# BRG-M28 — naga

Brogue kind **28**, `MK_NAGA`; runtime class `BrogueMonsterK28`.

## Brogue facts

> The serpentine naga live beneath the subterranean waters and emerge to attack unsuspecting adventurers.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1080); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1258).

- Large flag: `true` (not a physical measurement).
- Base glyph RGB: 40, 60, 15 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_GREEN_BLOOD`, `DF_PUDDLE`, `MA_ATTACKS_ALL_ADJACENT`, `MONST_FEMALE`, `MONST_IMMUNE_TO_WATER`, `MONST_NEVER_SLEEPS`, `MONST_SUBMERGES`.
- Source action/prose strings: ["studying", "Studying", "claws", "bites", "tail-whips"]

## Model work card

- Status: authored-static.
- Recipe: `serpent`.
- Authored silhouette dimensions: 50 / 48 / 68 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: naga, claws, scales.
- [Runtime model](../../mod/BrogueDoom/models/monsters/28_naga.obj).
- [Editable Blender source](../../assets/monsters/sources/28_naga.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L784](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L784) | leader/summoner | `MK_NAGA` | `13`–`20` | `DEEP_WATER` | `0` |
| [L834](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L834) | leader/summoner | `MK_NAGA` | `14`–`20` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L835](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L835) | member | `MK_SALAMANDER` | `13`–`20` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L860](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L860) | leader/summoner | `MK_NAGA` | `12`–`20` | `0` | `HORDE_MACHINE_CAPTIVE  /  HORDE_LEADER_CAPTIVE` |
| [L874](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L874) | leader/summoner | `MK_NAGA` | `12`–`19` | `STATUE_DORMANT` | `HORDE_MACHINE_STATUE` |
| [L897](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L897) | leader/summoner | `MK_NAGA` | `13`–`23` | `MONSTER_CAGE_CLOSED` | `HORDE_MACHINE_KENNEL  /  HORDE_LEADER_CAPTIVE` |
| [L912](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L912) | leader/summoner | `MK_NAGA` | `9`–`20` | `MONSTER_CAGE_CLOSED` | `HORDE_VAMPIRE_FODDER  /  HORDE_LEADER_CAPTIVE` |
| [L929](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L929) | leader/summoner | `MK_NAGA` | `13`–`20` | `STATUE_INSTACRACK` | `HORDE_SACRIFICE_TARGET` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

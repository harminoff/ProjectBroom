# BRG-M48 — tentacle horror

Brogue kind **48**, `MK_TENTACLE_HORROR`; runtime class `BrogueMonsterK48`.

## Brogue facts

> This seething, towering nightmare of fleshy tentacles slinks through the bowels of the world. The tentacle horror's incredible strength and regeneration make $HIMHER one of the most fearsome creatures of the dungeon.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1120); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1323).

- Large flag: `true` (not a physical measurement).
- Base glyph RGB: 75, 25, 85 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_PURPLE_BLOOD`.
- Source action/prose strings: ["sucking on", "Consuming", "slaps", "batters", "crushes"]

## Model work card

- Status: authored-skeletal.
- Recipe: `weighted-tentacle_horror`.
- Authored silhouette dimensions: 55.8764 / 56.3155 / 80.9514 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: towering braided tentacle column, eyeless crown with a hooked sucking maw, irregular writhing crown of varied tentacles, bruised veined aubergine flesh, pale sucker-lined undersides, buckled heap death.
- [Runtime model](../../mod/BrogueDoom/models/monsters/48_tentacle_horror.iqm).
- [Editable Blender source](../../assets/monsters/tentacle_horror/tentacle-horror-animated.blend).
- [Animation manifest](../../assets/monsters/tentacle_horror/animation.json); 218 bones.
- [Shared skeletal workflow and verification](../skeletal-enemy-workflow.md).
- [Tentacle horror authoring and actual verification](../tentacle-horror-animation.md).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L802](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L802) | leader/summoner | `MK_TENTACLE_HORROR` | `22`–`DEEPEST_LEVEL-1` | `0` | `0` |
| [L809](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L809) | leader/summoner, member | `MK_TENTACLE_HORROR` | `32`–`DEEPEST_LEVEL-1` | `0` | `0` |
| [L843](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L843) | leader/summoner | `MK_TENTACLE_HORROR` | `20`–`26` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L867](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L867) | leader/summoner | `MK_TENTACLE_HORROR` | `20`–`AMULET_LEVEL` | `0` | `HORDE_MACHINE_CAPTIVE  /  HORDE_LEADER_CAPTIVE` |
| [L878](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L878) | leader/summoner | `MK_TENTACLE_HORROR` | `29`–`DEEPEST_LEVEL` | `STATUE_DORMANT` | `HORDE_MACHINE_STATUE` |
| [L933](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L933) | leader/summoner | `MK_TENTACLE_HORROR` | `21`–`DEEPEST_LEVEL` | `STATUE_INSTACRACK` | `HORDE_SACRIFICE_TARGET` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [x] Skeletal clips authored; see animation report for actual verification and approval scope.

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

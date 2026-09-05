# BRG-M50 — dragon

Brogue kind **50**, `MK_DRAGON`; runtime class `BrogueMonsterK50`.

## Brogue facts

> An ancient serpent of the world's deepest places, the dragon's immense form belies its lightning-quick speed and testifies to $HISHER breathtaking strength. An undying furnace of white-hot flames burns within $HISHER scaly hide, and few could withstand a single moment under $HISHER infernal lash.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1123); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1329).

- Large flag: `true` (not a physical measurement).
- Base glyph RGB: 20, 80, 15 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `BOLT_DRAGONFIRE`, `DF_GREEN_BLOOD`, `MA_ATTACKS_ALL_ADJACENT`, `MONST_CARRY_ITEM_100`, `MONST_IMMUNE_TO_FIRE`.
- Source action/prose strings: ["consuming", "Consuming", "claws", "tail-whips", "bites"]

## Model work card

- Status: authored-static.
- Recipe: `dragon`.
- Authored silhouette dimensions: 62 / 58 / 100 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: serpent, scales, jaws, claws.
- [Runtime model](../../mod/BrogueDoom/models/monsters/50_dragon.obj).
- [Editable Blender source](../../assets/monsters/sources/50_dragon.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L804](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L804) | leader/summoner | `MK_DRAGON` | `24`–`DEEPEST_LEVEL-1` | `0` | `0` |
| [L805](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L805) | leader/summoner, member | `MK_DRAGON` | `27`–`DEEPEST_LEVEL-1` | `0` | `0` |
| [L810](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L810) | leader/summoner, member | `MK_DRAGON` | `34`–`DEEPEST_LEVEL-1` | `0` | `0` |
| [L868](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L868) | leader/summoner | `MK_DRAGON` | `23`–`AMULET_LEVEL` | `0` | `HORDE_MACHINE_CAPTIVE  /  HORDE_LEADER_CAPTIVE` |
| [L877](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L877) | leader/summoner | `MK_DRAGON` | `29`–`DEEPEST_LEVEL` | `STATUE_DORMANT` | `HORDE_MACHINE_STATUE` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

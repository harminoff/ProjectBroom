# BRG-M02 — kobold

Brogue kind **2**, `MK_KOBOLD`; runtime class `BrogueMonsterK02`.

## Brogue facts

> The kobold is a lizardlike humanoid of the upper dungeon.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1031); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1174).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 44, 33, 22 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_RED_BLOOD`.
- Source action/prose strings: ["poking at", "Examining", "clubs", "bashes"]

## Model work card

- Status: authored-skeletal.
- Recipe: `weighted-kobold`.
- Authored silhouette dimensions: 22.4004 / 18.6767 / 40.6239 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: lizard, club, scales.
- [Runtime model](../../mod/BrogueDoom/models/monsters/02_kobold.iqm).
- [Editable Blender source](../../assets/monsters/kobold/kobold-animated.blend).
- [Animation manifest](../../assets/monsters/kobold/animation.json); 24 bones.
- [Shared skeletal workflow and verification](../skeletal-enemy-workflow.md).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L747](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L747) | leader/summoner | `MK_KOBOLD` | `1`–`6` | `0` | `0` |
| [L825](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L825) | member | `MK_MONKEY` | `1`–`5` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L828](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L828) | member | `MK_GOBLIN_MYSTIC` | `5`–`11` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [x] Skeletal clips authored; see animation report for actual verification and approval scope.

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

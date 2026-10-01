# BRG-M47 — revenant

Brogue kind **47**, `MK_REVENANT`; runtime class `BrogueMonsterK47`.

## Brogue facts

> This unholy specter stalks the deep places of the earth without fear, impervious to conventional attacks.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1118); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1320).

- Large flag: `true` (not a physical measurement).
- Base glyph RGB: 45, 20, 55 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_ECTOPLASM_BLOOD`, `MONST_IMMUNE_TO_WEAPONS`.
- Source action/prose strings: ["desecrating", "Desecrating", "hits"]

## Model work card

- Status: authored-skeletal.
- Recipe: `weighted-revenant`.
- Authored silhouette dimensions: 20.5227 / 40.8273 / 61.0307 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: stooped looming hunch under a high mantle, skull deep in a near-black cowl, shredded strips fading before the floor, layered grave-shroud wrappings and binding strips, rot and grave-earth staining, aged bone hands with hooked talons, slow relentless stalk.
- [Runtime model](../../mod/BrogueDoom/models/monsters/47_revenant.iqm).
- [Editable Blender source](../../assets/monsters/revenant/revenant-animated.blend).
- [Animation manifest](../../assets/monsters/revenant/animation.json); 19 bones.
- [Shared skeletal workflow and verification](../skeletal-enemy-workflow.md).
- [Revenant authoring and actual verification](../revenant-animation.md).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L800](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L800) | leader/summoner | `MK_REVENANT` | `19`–`27` | `0` | `0` |
| [L809](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L809) | member | `MK_TENTACLE_HORROR` | `32`–`DEEPEST_LEVEL-1` | `0` | `0` |
| [L932](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L932) | leader/summoner | `MK_REVENANT` | `21`–`DEEPEST_LEVEL` | `STATUE_INSTACRACK` | `HORDE_SACRIFICE_TARGET` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [x] Skeletal clips authored; see animation report for actual verification and approval scope.

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

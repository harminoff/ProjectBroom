# BRG-M30 — explosive bloat

Brogue kind **30**, `MK_EXPLOSIVE_BLOAT`; runtime class `BrogueMonsterK30`.

## Brogue facts

> This rare subspecies of bloat is little more than a thin membrane surrounding a bladder of highly explosive gases. The slightest stress will cause $HIMHER to rupture in spectacular and deadly fashion.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1084); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1264).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 100, 50, 0 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_BLOAT_EXPLOSION`, `DF_RED_BLOOD`, `MA_DF_ON_DEATH`, `MA_KAMIKAZE`, `MONST_FLIES`, `MONST_FLITS`.
- Source action/prose strings: ["gazing at", "Gazing", "bumps", "detonates with terrifying force!"]

## Model work card

- Status: authored-skeletal.
- Recipe: `weighted-explosive_bloat`.
- Authored silhouette dimensions: 28 / 26.3268 / 32 map units. Clearance: 16 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: continuous thin membrane, orange amber pigment, fine dark vessels, pale taut pressure areas, asymmetric spent membrane collapse.
- [Runtime model](../../mod/BrogueDoom/models/monsters/30_explosive_bloat.iqm).
- [Editable Blender source](../../assets/monsters/explosive_bloat/explosive-bloat-animated.blend).
- [Animation manifest](../../assets/monsters/explosive_bloat/animation.json); 7 bones.
- [Shared skeletal workflow and verification](../skeletal-enemy-workflow.md).
- [Explosive bloat authoring and actual verification](../explosive-bloat-animation.md).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L756](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L756) | leader/summoner | `MK_EXPLOSIVE_BLOAT` | `10`–`26` | `0` | `0` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [x] Skeletal clips authored; see animation report for actual verification and approval scope.

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

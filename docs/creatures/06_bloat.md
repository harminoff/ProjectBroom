# BRG-M06 — bloat

Brogue kind **6**, `MK_BLOAT`; runtime class `BrogueMonsterK06`.

## Brogue facts

> A bladder of deadly gas buoys the bloat through the air, $HISHER thin veinous membrane ready to rupture at the slightest stress.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1037); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1186).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 75, 25, 85 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_BLOAT_DEATH`, `DF_PURPLE_BLOOD`, `MA_DF_ON_DEATH`, `MA_KAMIKAZE`, `MONST_FLIES`, `MONST_FLITS`.
- Source action/prose strings: ["gazing at", "Gazing", "bumps", "bursts, leaving behind an expanding cloud of caustic gas!"]

## Model work card

- Status: authored-static.
- Recipe: `bloat`.
- Authored silhouette dimensions: 28 / 28 / 32 map units. Clearance: 16 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: membrane, veins.
- [Runtime model](../../mod/BrogueDoom/models/monsters/06_bloat.obj).
- [Editable Blender source](../../assets/monsters/sources/06_bloat.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L752](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L752) | leader/summoner | `MK_BLOAT` | `2`–`13` | `0` | `0` |
| [L754](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L754) | leader/summoner, member | `MK_BLOAT` | `14`–`26` | `0` | `0` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

# BRG-M07 — pit bloat

Brogue kind **7**, `MK_PIT_BLOAT`; runtime class `BrogueMonsterK07`.

## Brogue facts

> This rare subspecies of bloat is filled with a peculiar vapor that, if released, will cause the floor to vanish out from underneath $HIMHER.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1039); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1190).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 40, 40, 100 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_HOLE_POTION`, `DF_PURPLE_BLOOD`, `MA_DF_ON_DEATH`, `MA_KAMIKAZE`, `MONST_FLIES`, `MONST_FLITS`.
- Source action/prose strings: ["gazing at", "Gazing", "bumps", "bursts, causing the floor underneath $HIMHER to disappear!"]

## Model work card

- Status: authored-static.
- Recipe: `bloat`.
- Authored silhouette dimensions: 28 / 28 / 32 map units. Clearance: 16 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: membrane, veins, pit.
- [Runtime model](../../mod/BrogueDoom/models/monsters/07_pit_bloat.obj).
- [Editable Blender source](../../assets/monsters/sources/07_pit_bloat.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L753](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L753) | leader/summoner | `MK_PIT_BLOAT` | `2`–`13` | `0` | `0` |
| [L755](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L755) | leader/summoner, member | `MK_PIT_BLOAT` | `14`–`26` | `0` | `0` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

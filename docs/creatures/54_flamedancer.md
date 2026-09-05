# BRG-M54 — flamedancer

Brogue kind **54**, `MK_FLAMEDANCER`; runtime class `BrogueMonsterK54`.

## Brogue facts

> An elemental creature from another plane of existence, the infernal flamedancer burns with such intensity that $HESHE is painful to behold.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1133); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1346).

- Large flag: `true` (not a physical measurement).
- Base glyph RGB: 100, 100, 100 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `BOLT_FIRE`, `DF_EMBER_BLOOD`, `DF_FLAMEDANCER_CORONA`, `MA_HIT_BURN`, `MONST_FIERY`, `MONST_IMMUNE_TO_FIRE`, `MONST_MAINTAINS_DISTANCE`.
- Source action/prose strings: ["immolating", "Consuming", "singes", "burns", "immolates"]

## Model work card

- Status: authored-static.
- Recipe: `flame`.
- Authored silhouette dimensions: 40 / 46 / 80 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: humanoid, white_hot.
- [Runtime model](../../mod/BrogueDoom/models/monsters/54_flamedancer.obj).
- [Editable Blender source](../../assets/monsters/sources/54_flamedancer.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L850](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L850) | leader/summoner | `MK_FLAMEDANCER` | `10`–`DEEPEST_LEVEL` | `0` | `HORDE_MACHINE_BOSS` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

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

- Status: authored-skeletal.
- Recipe: `weighted-flamedancer`.
- Authored silhouette dimensions: 45.3604 / 51.2179 / 67.9 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: living column of fire, not a robed figure, white-hot head with dark eye slits and a hot core, spiral of twelve flame tongues with side licks, two ribbon arms ending in finger-flames, swirling flame skirt and drifting sparks, fireball cage that forms between the hands only when casting, fullbright with a view-angle rim and rising shimmer.
- [Runtime model](../../mod/BrogueDoom/models/monsters/54_flamedancer.iqm).
- [Editable Blender source](../../assets/monsters/flamedancer/flamedancer-animated.blend).
- [Animation manifest](../../assets/monsters/flamedancer/animation.json); 153 bones.
- [Shared skeletal workflow and verification](../skeletal-enemy-workflow.md).
- [Flamedancer authoring and actual verification](../flamedancer-animation.md).

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
- [x] Skeletal clips authored; see animation report for actual verification and approval scope.

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

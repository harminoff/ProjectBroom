# BRG-M25 — zombie

Brogue kind **25**, `MK_ZOMBIE`; runtime class `BrogueMonsterK25`.

## Brogue facts

> The zombie is the accursed product of a long-forgotten ritual. Perpetually decaying flesh hangs from $HISHER bones in shreds and releases a flammable stench that will induce violent nausea with one whiff.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1075); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1247).

- Large flag: `true` (not a physical measurement).
- Base glyph RGB: 60, 50, 5 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_ROT_GAS_BLOOD`, `DF_ROT_GAS_PUFF`.
- Source action/prose strings: ["rending", "Eating", "hits", "bites"]

## Model work card

- Status: authored-static.
- Recipe: `humanoid`.
- Authored silhouette dimensions: 32 / 36 / 62 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: undead, ribs, torn_flesh.
- [Runtime model](../../mod/BrogueDoom/models/monsters/25_zombie.obj).
- [Editable Blender source](../../assets/monsters/sources/25_zombie.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L780](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L780) | leader/summoner | `MK_ZOMBIE` | `11`–`18` | `0` | `0` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

# BRG-M17 — centipede

Brogue kind **17**, `MK_CENTIPEDE`; runtime class `BrogueMonsterK17`.

## Brogue facts

> This monstrous centipede's incisors are imbued with a horrible venom that will slowly kill $HISHER prey.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1059); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1223).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 75, 25, 85 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_GREEN_BLOOD`, `MA_CAUSES_WEAKNESS`.
- Source action/prose strings: ["eating", "Eating", "pricks", "stings"]

## Model work card

- Status: authored-static.
- Recipe: `centipede`.
- Authored silhouette dimensions: 56 / 35 / 13 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: segments, incisors, chitin.
- [Runtime model](../../mod/BrogueDoom/models/monsters/17_centipede.obj).
- [Editable Blender source](../../assets/monsters/sources/17_centipede.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L769](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L769) | leader/summoner | `MK_CENTIPEDE` | `7`–`14` | `0` | `0` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

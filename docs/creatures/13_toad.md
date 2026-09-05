# BRG-M13 — toad

Brogue kind **13**, `MK_TOAD`; runtime class `BrogueMonsterK13`.

## Brogue facts

> The enormous, warty toad secretes a powerful hallucinogenic slime to befuddle the senses of any creatures that come in contact with $HIMHER.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1051); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1211).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 40, 65, 30 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_GREEN_BLOOD`, `MA_HIT_HALLUCINATE`.
- Source action/prose strings: ["eating", "Eating", "slimes", "slams"]

## Model work card

- Status: authored-static.
- Recipe: `toad`.
- Authored silhouette dimensions: 38 / 35 / 25 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: warts, slime.
- [Runtime model](../../mod/BrogueDoom/models/monsters/13_toad.obj).
- [Editable Blender source](../../assets/monsters/sources/13_toad.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L759](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L759) | leader/summoner | `MK_TOAD` | `4`–`11` | `0` | `0` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

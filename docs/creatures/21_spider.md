# BRG-M21 — spider

Brogue kind **21**, `MK_SPIDER`; runtime class `BrogueMonsterK21`.

## Brogue facts

> The spider's red eyes pierce the darkness in search of enemies to ensnare with $HISHER projectile webs and dissolve with deadly poison.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1067); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1235).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 100, 100, 100 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `BOLT_SPIDERWEB`, `DF_GREEN_BLOOD`, `MA_POISONS`, `MONST_ALWAYS_USE_ABILITY`, `MONST_CAST_SPELLS_SLOWLY`, `MONST_IMMUNE_TO_WEBS`.
- Source action/prose strings: ["draining", "Feeding", "bites", "stings"]

## Model work card

- Status: authored-static.
- Recipe: `spider`.
- Authored silhouette dimensions: 52 / 58 / 24 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: eight_legs, red_eyes, chitin.
- [Runtime model](../../mod/BrogueDoom/models/monsters/21_spider.obj).
- [Editable Blender source](../../assets/monsters/sources/21_spider.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L774](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L774) | leader/summoner | `MK_SPIDER` | `9`–`16` | `0` | `0` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

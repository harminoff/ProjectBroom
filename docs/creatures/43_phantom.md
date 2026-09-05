# BRG-M43 — phantom

Brogue kind **43**, `MK_PHANTOM`; runtime class `BrogueMonsterK43`.

## Brogue facts

> A silhouette of mournful rage against an empty backdrop, the phantom slips through the dungeon invisibly in clear air, leaving behind glowing droplets of ectoplasm and the cries of $HISHER unsuspecting victims.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1110); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1308).

- Large flag: `true` (not a physical measurement).
- Base glyph RGB: 45, 20, 55 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_ECTOPLASM_BLOOD`, `DF_ECTOPLASM_DROPLET`, `MONST_FLIES`, `MONST_FLITS`, `MONST_IMMUNE_TO_WEBS`, `MONST_INVISIBLE`.
- Source action/prose strings: ["permeating", "Permeating", "hits"]

## Model work card

- Status: authored-static.
- Recipe: `specter`.
- Authored silhouette dimensions: 32 / 38 / 66 map units. Clearance: 16 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: ectoplasm, ragged.
- [Runtime model](../../mod/BrogueDoom/models/monsters/43_phantom.obj).
- [Editable Blender source](../../assets/monsters/sources/43_phantom.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L795](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L795) | leader/summoner | `MK_PHANTOM` | `16`–`23` | `0` | `0` |
| [L816](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L816) | member | `MK_LICH` | `0`–`0` | `0` | `HORDE_IS_SUMMONED` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

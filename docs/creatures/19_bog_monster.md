# BRG-M19 — bog monster

Brogue kind **19**, `MK_BOG_MONSTER`; runtime class `BrogueMonsterK19`.

## Brogue facts

> The horrifying bog monster dwells beneath the surface of mud-filled swamps. When $HISHER prey ventures into the mud, the bog monster will ensnare the unsuspecting victim in $HISHER pale tentacles and squeeze its life away.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1063); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1229).

- Large flag: `true` (not a physical measurement).
- Base glyph RGB: 100, 55, 55 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `MA_SEIZES`, `MONST_FLEES_NEAR_DEATH`, `MONST_FLITS`, `MONST_RESTRICTED_TO_LIQUID`, `MONST_SUBMERGES`.
- Source action/prose strings: ["draining", "Feeding", "squeezes", "strangles", "crushes"]

## Model work card

- Status: authored-static.
- Recipe: `tentacles`.
- Authored silhouette dimensions: 58 / 58 / 42 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: pale, tentacles, mud.
- [Runtime model](../../mod/BrogueDoom/models/monsters/19_bog_monster.obj).
- [Editable Blender source](../../assets/monsters/sources/19_bog_monster.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L770](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L770) | leader/summoner | `MK_BOG_MONSTER` | `7`–`14` | `MUD` | `HORDE_NEVER_OOD` |
| [L783](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L783) | leader/summoner, member | `MK_BOG_MONSTER` | `12`–`26` | `MUD` | `0` |
| [L887](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L887) | leader/summoner | `MK_BOG_MONSTER` | `12`–`26` | `MACHINE_MUD_DORMANT` | `HORDE_MACHINE_MUD` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

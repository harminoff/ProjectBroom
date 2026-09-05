# BRG-M14 — vampire bat

Brogue kind **14**, `MK_VAMPIRE_BAT`; runtime class `BrogueMonsterK14`.

## Brogue facts

> Often hunting in packs, leathery wings and keen senses guide the vampire bat unerringly to $HISHER prey.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1053); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1214).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 50, 50, 50 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_RED_BLOOD`, `MA_TRANSFERENCE`, `MONST_FLIES`, `MONST_FLITS`.
- Source action/prose strings: ["draining", "Feeding", "nips", "bites"]

## Model work card

- Status: authored-static.
- Recipe: `winged`.
- Authored silhouette dimensions: 24 / 58 / 28 map units. Clearance: 16 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: bat, membrane, fangs.
- [Runtime model](../../mod/BrogueDoom/models/monsters/14_vampire_bat.obj).
- [Editable Blender source](../../assets/monsters/sources/14_vampire_bat.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L764](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L764) | leader/summoner | `MK_VAMPIRE_BAT` | `6`–`13` | `0` | `0` |
| [L765](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L765) | leader/summoner, member | `MK_VAMPIRE_BAT` | `6`–`13` | `0` | `HORDE_NEVER_OOD` |
| [L815](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L815) | member | `MK_VAMPIRE` | `0`–`0` | `0` | `HORDE_IS_SUMMONED` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

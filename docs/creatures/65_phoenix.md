# BRG-M65 — phoenix

Brogue kind **65**, `MK_PHOENIX`; runtime class `BrogueMonsterK65`.

## Brogue facts

> This legendary bird shines with a brilliant light, and $HISHER wings crackle and pop like embers as they beat the air. When $HESHE dies, legend has it that an egg will form and a newborn phoenix will rise from its ashes.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1159); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1383).

- Large flag: `true` (not a physical measurement).
- Base glyph RGB: 100, 0, 0 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_ASH_BLOOD`, `MONST_FLIES`, `MONST_IMMUNE_TO_FIRE`, `MONST_NO_POLYMORPH`.
- Source action/prose strings: ["cremating", "Cremating", "pecks", "scratches", "claws"]

## Model work card

- Status: authored-static.
- Recipe: `winged`.
- Authored silhouette dimensions: 42 / 62 / 64 map units. Clearance: 16 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: bird, feathers, embers.
- [Runtime model](../../mod/BrogueDoom/models/monsters/65_phoenix.obj).
- [Editable Blender source](../../assets/monsters/sources/65_phoenix.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L820](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L820) | member | `MK_PHOENIX_EGG` | `0`–`0` | `0` | `HORDE_IS_SUMMONED` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

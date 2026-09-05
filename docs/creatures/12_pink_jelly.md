# BRG-M12 — pink jelly

Brogue kind **12**, `MK_PINK_JELLY`; runtime class `BrogueMonsterK12`.

## Brogue facts

> This mass of caustic pink goo slips across the ground in search of a warm meal.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1049); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1208).

- Large flag: `true` (not a physical measurement).
- Base glyph RGB: 100, 40, 40 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_PURPLE_BLOOD`, `MA_CLONE_SELF_ON_DEFEND`, `MONST_NEVER_SLEEPS`.
- Source action/prose strings: ["absorbing", "Feeding", "smears", "slimes", "drenches"]

## Model work card

- Status: authored-static.
- Recipe: `slime`.
- Authored silhouette dimensions: 50 / 46 / 30 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: goo, lobes.
- [Runtime model](../../mod/BrogueDoom/models/monsters/12_pink_jelly.obj).
- [Editable Blender source](../../assets/monsters/sources/12_pink_jelly.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L760](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L760) | leader/summoner | `MK_PINK_JELLY` | `4`–`13` | `0` | `0` |
| [L793](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L793) | leader/summoner, member | `MK_PINK_JELLY` | `17`–`23` | `0` | `0` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

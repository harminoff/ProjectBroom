# BRG-M67 — mangrove dryad

Brogue kind **67**, `MK_ANCIENT_SPIRIT`; runtime class `BrogueMonsterK67`.

## Brogue facts

> This mangrove dryad is as old as the earth, and $HISHER gnarled figure houses an ancient power. When angered, $HESHE can call upon the forces of nature to bind $HISHER foes and tear them to shreds.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1163); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1391).

- Large flag: `true` (not a physical measurement).
- Base glyph RGB: 80, 67, 15 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `BOLT_ANCIENT_SPIRIT_VINES`, `DF_ASH_BLOOD`, `MONST_ALWAYS_USE_ABILITY`, `MONST_FEMALE`, `MONST_IMMUNE_TO_WEBS`, `MONST_MAINTAINS_DISTANCE`, `MONST_MALE`, `MONST_NO_POLYMORPH`.
- Source action/prose strings: ["absorbing", "Absorbing", "whips", "lashes", "thrashes", "lacerates"]

## Model work card

- Status: authored-static.
- Recipe: `dryad`.
- Authored silhouette dimensions: 48 / 58 / 84 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: bark, roots, branches.
- [Runtime model](../../mod/BrogueDoom/models/monsters/67_ancient_spirit.obj).
- [Editable Blender source](../../assets/monsters/sources/67_ancient_spirit.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L939](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L939) | leader/summoner | `MK_ANCIENT_SPIRIT` | `1`–`DEEPEST_LEVEL` | `0` | `HORDE_MACHINE_LEGENDARY_ALLY  /  HORDE_ALLIED_WITH_PLAYER` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

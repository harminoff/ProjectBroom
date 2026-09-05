# BRG-M64 — ifrit

Brogue kind **64**, `MK_IFRIT`; runtime class `BrogueMonsterK64`.

## Brogue facts

> A whirling desert storm given human shape, the ifrit's twin scimitars flicker in the darkness and $HISHER eyes burn with otherworldly zeal.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1157); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1380).

- Large flag: `true` (not a physical measurement).
- Base glyph RGB: 50, 10, 100 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `BOLT_DISCORD`, `DF_ASH_BLOOD`, `MONST_FLIES`, `MONST_IMMUNE_TO_FIRE`, `MONST_MALE`.
- Source action/prose strings: ["absorbing", "Absorbing", "cuts", "slashes", "lacerates"]

## Model work card

- Status: authored-static.
- Recipe: `humanoid`.
- Authored silhouette dimensions: 42 / 50 / 70 map units. Clearance: 16 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: storm, twin_scimitars, ember_eyes.
- [Runtime model](../../mod/BrogueDoom/models/monsters/64_ifrit.obj).
- [Editable Blender source](../../assets/monsters/sources/64_ifrit.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L937](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L937) | leader/summoner | `MK_IFRIT` | `1`–`DEEPEST_LEVEL` | `0` | `HORDE_MACHINE_LEGENDARY_ALLY  /  HORDE_ALLIED_WITH_PLAYER` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

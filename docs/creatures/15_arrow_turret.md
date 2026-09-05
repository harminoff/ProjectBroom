# BRG-M15 — arrow turret

Brogue kind **15**, `MK_ARROW_TURRET`; runtime class `BrogueMonsterK15`.

## Brogue facts

> A mechanical contraption embedded in the wall, the spring-loaded arrow turret will fire volley after volley of arrows at intruders.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1055); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1217).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 0, 0, 0 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `BOLT_DISTANCE_ATTACK`, `MONST_TURRET`.
- Source action/prose strings: ["gazing at", "Gazing", "shoots"]

## Model work card

- Status: authored-static.
- Recipe: `turret`.
- Authored silhouette dimensions: 30 / 32 / 38 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: mechanism, crossbow.
- [Runtime model](../../mod/BrogueDoom/models/monsters/15_arrow_turret.obj).
- [Editable Blender source](../../assets/monsters/sources/15_arrow_turret.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L762](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L762) | leader/summoner | `MK_ARROW_TURRET` | `5`–`13` | `WALL` | `HORDE_NO_PERIODIC_SPAWN` |
| [L881](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L881) | leader/summoner | `MK_ARROW_TURRET` | `5`–`13` | `TURRET_DORMANT` | `HORDE_MACHINE_TURRET` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

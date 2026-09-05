# BRG-M49 — golem

Brogue kind **49**, `MK_GOLEM`; runtime class `BrogueMonsterK49`.

## Brogue facts

> A statue animated by an ancient and tireless magic, the golem does not regenerate and attacks with only moderate strength, but $HISHER stone form can withstand incredible damage before collapsing into rubble.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1121); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1326).

- Large flag: `true` (not a physical measurement).
- Base glyph RGB: 50, 50, 50 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_RUBBLE_BLOOD`, `MONST_DIES_IF_NEGATED`, `MONST_REFLECT_50`.
- Source action/prose strings: ["cradling", "Cradling", "backhands", "punches", "kicks"]

## Model work card

- Status: authored-static.
- Recipe: `humanoid`.
- Authored silhouette dimensions: 40 / 48 / 88 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: stone, plates, cracks.
- [Runtime model](../../mod/BrogueDoom/models/monsters/49_golem.obj).
- [Editable Blender source](../../assets/monsters/sources/49_golem.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L801](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L801) | leader/summoner | `MK_GOLEM` | `21`–`30` | `0` | `0` |
| [L806](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L806) | leader/summoner, member | `MK_GOLEM` | `27`–`DEEPEST_LEVEL-1` | `0` | `0` |
| [L807](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L807) | leader/summoner, member | `MK_GOLEM` | `30`–`DEEPEST_LEVEL-1` | `0` | `0` |
| [L844](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L844) | leader/summoner | `MK_GOLEM` | `18`–`25` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L866](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L866) | leader/summoner | `MK_GOLEM` | `17`–`23` | `0` | `HORDE_MACHINE_CAPTIVE  /  HORDE_LEADER_CAPTIVE` |
| [L876](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L876) | leader/summoner | `MK_GOLEM` | `21`–`30` | `STATUE_DORMANT` | `HORDE_MACHINE_STATUE` |
| [L931](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L931) | leader/summoner | `MK_GOLEM` | `21`–`DEEPEST_LEVEL` | `STATUE_INSTACRACK` | `HORDE_SACRIFICE_TARGET` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

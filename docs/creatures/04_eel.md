# BRG-M04 — eel

Brogue kind **4**, `MK_EEL`; runtime class `BrogueMonsterK04`.

## Brogue facts

> The eel slips silently through the subterranean lake, waiting for unsuspecting prey to set foot in $HISHER dark waters.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1033); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1180).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 30, 12, 12 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `MONST_FLITS`, `MONST_IMMUNE_TO_WATER`, `MONST_NEVER_SLEEPS`, `MONST_RESTRICTED_TO_LIQUID`, `MONST_SUBMERGES`.
- Source action/prose strings: ["eating", "Eating", "shocks", "bites"]

## Model work card

- Status: authored-static.
- Recipe: `serpent`.
- Authored silhouette dimensions: 54 / 22 / 9 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: eel, fins, scales.
- [Runtime model](../../mod/BrogueDoom/models/monsters/04_eel.obj).
- [Editable Blender source](../../assets/monsters/sources/04_eel.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L750](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L750) | leader/summoner | `MK_EEL` | `2`–`17` | `DEEP_WATER` | `0` |
| [L772](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L772) | leader/summoner, member | `MK_EEL` | `8`–`22` | `DEEP_WATER` | `0` |
| [L853](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L853) | leader/summoner | `MK_EEL` | `2`–`7` | `DEEP_WATER` | `HORDE_MACHINE_WATER_MONSTER` |
| [L854](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L854) | leader/summoner, member | `MK_EEL` | `5`–`15` | `DEEP_WATER` | `HORDE_MACHINE_WATER_MONSTER` |
| [L856](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L856) | member | `MK_KRAKEN` | `12`–`DEEPEST_LEVEL` | `DEEP_WATER` | `HORDE_MACHINE_WATER_MONSTER` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

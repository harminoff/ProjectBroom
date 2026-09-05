# BRG-M39 — kraken

Brogue kind **39**, `MK_KRAKEN`; runtime class `BrogueMonsterK39`.

## Brogue facts

> This tentacled nightmare will emerge from the subterranean waters to ensnare and devour any creature foolish enough to set foot into $HISHER lake.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1102); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1292).

- Large flag: `true` (not a physical measurement).
- Base glyph RGB: 100, 55, 55 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `MA_SEIZES`, `MONST_FLEES_NEAR_DEATH`, `MONST_FLITS`, `MONST_IMMUNE_TO_WATER`, `MONST_NEVER_SLEEPS`, `MONST_RESTRICTED_TO_LIQUID`, `MONST_SUBMERGES`.
- Source action/prose strings: ["devouring", "Feeding", "slaps", "smites", "batters"]

## Model work card

- Status: authored-static.
- Recipe: `tentacles`.
- Authored silhouette dimensions: 60 / 60 / 66 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: mantle, tentacles, suckers.
- [Runtime model](../../mod/BrogueDoom/models/monsters/39_kraken.obj).
- [Editable Blender source](../../assets/monsters/sources/39_kraken.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L794](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L794) | leader/summoner | `MK_KRAKEN` | `15`–`30` | `DEEP_WATER` | `0` |
| [L808](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L808) | leader/summoner, member | `MK_KRAKEN` | `30`–`DEEPEST_LEVEL-1` | `DEEP_WATER` | `0` |
| [L855](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L855) | leader/summoner | `MK_KRAKEN` | `12`–`DEEPEST_LEVEL` | `DEEP_WATER` | `HORDE_MACHINE_WATER_MONSTER` |
| [L856](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L856) | leader/summoner | `MK_KRAKEN` | `12`–`DEEPEST_LEVEL` | `DEEP_WATER` | `HORDE_MACHINE_WATER_MONSTER` |
| [L888](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L888) | leader/summoner | `MK_KRAKEN` | `17`–`26` | `MACHINE_MUD_DORMANT` | `HORDE_MACHINE_MUD` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

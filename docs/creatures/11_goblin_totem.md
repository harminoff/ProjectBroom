# BRG-M11 — goblin totem

Brogue kind **11**, `MK_GOBLIN_TOTEM`; runtime class `BrogueMonsterK11`.

## Brogue facts

> Goblins have created this makeshift totem and imbued $HIMHER with a shamanistic power.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1047); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1205).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 100, 50, 0 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `BOLT_HASTE`, `BOLT_SPARK`, `DF_RUBBLE_BLOOD`, `MONST_IMMOBILE`, `MONST_IMMUNE_TO_WEBS`, `MONST_INANIMATE`, `MONST_NEVER_SLEEPS`, `MONST_WILL_NOT_USE_STAIRS`.
- Source action/prose strings: ["gazing at", "Gazing", "hits"]

## Model work card

- Status: authored-static.
- Recipe: `totem`.
- Authored silhouette dimensions: 24 / 26 / 46 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: wood, bone, shaman.
- [Runtime model](../../mod/BrogueDoom/models/monsters/11_goblin_totem.obj).
- [Editable Blender source](../../assets/monsters/sources/11_goblin_totem.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L761](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L761) | leader/summoner | `MK_GOBLIN_TOTEM` | `5`–`13` | `0` | `HORDE_NO_PERIODIC_SPAWN` |
| [L778](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L778) | leader/summoner, member | `MK_GOBLIN_TOTEM` | `10`–`17` | `0` | `HORDE_NO_PERIODIC_SPAWN` |
| [L944](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L944) | leader/summoner | `MK_GOBLIN_TOTEM` | `5`–`13` | `0` | `HORDE_MACHINE_GOBLIN_WARREN` |
| [L947](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L947) | leader/summoner, member | `MK_GOBLIN_TOTEM` | `10`–`17` | `0` | `HORDE_MACHINE_GOBLIN_WARREN` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

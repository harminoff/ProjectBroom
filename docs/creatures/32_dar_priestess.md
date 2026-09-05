# BRG-M32 — dar priestess

Brogue kind **32**, `MK_DAR_PRIESTESS`; runtime class `BrogueMonsterK32`.

## Brogue facts

> The dar priestess carries a host of religious relics that jangle as $HESHE walks.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1088); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1271).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 0, 50, 50 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `BOLT_HASTE`, `BOLT_HEALING`, `BOLT_NEGATION`, `BOLT_SPARK`, `DF_RED_BLOOD`, `MA_AVOID_CORRIDORS`, `MONST_CARRY_ITEM_25`, `MONST_FEMALE`, `MONST_MAINTAINS_DISTANCE`.
- Source action/prose strings: ["praying over", "Praying", "cuts", "slices"]

## Model work card

- Status: authored-static.
- Recipe: `humanoid`.
- Authored silhouette dimensions: 28 / 32 / 57 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: elf, relics, robe.
- [Runtime model](../../mod/BrogueDoom/models/monsters/32_dar_priestess.obj).
- [Editable Blender source](../../assets/monsters/sources/32_dar_priestess.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L792](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L792) | member | `MK_DAR_BLADEMASTER` | `15`–`17` | `0` | `0` |
| [L793](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L793) | member | `MK_PINK_JELLY` | `17`–`23` | `0` | `0` |
| [L798](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L798) | member | `MK_DAR_BLADEMASTER` | `18`–`25` | `0` | `0` |
| [L806](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L806) | member | `MK_GOLEM` | `27`–`DEEPEST_LEVEL-1` | `0` | `0` |
| [L841](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L841) | leader/summoner | `MK_DAR_PRIESTESS` | `18`–`26` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L843](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L843) | member | `MK_TENTACLE_HORROR` | `20`–`26` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L844](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L844) | member | `MK_GOLEM` | `18`–`25` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L864](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L864) | leader/summoner | `MK_DAR_PRIESTESS` | `8`–`14` | `0` | `HORDE_MACHINE_CAPTIVE  /  HORDE_LEADER_CAPTIVE` |
| [L902](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L902) | leader/summoner | `MK_DAR_PRIESTESS` | `12`–`AMULET_LEVEL` | `MONSTER_CAGE_CLOSED` | `HORDE_MACHINE_KENNEL  /  HORDE_LEADER_CAPTIVE` |
| [L916](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L916) | leader/summoner | `MK_DAR_PRIESTESS` | `12`–`AMULET_LEVEL` | `MONSTER_CAGE_CLOSED` | `HORDE_VAMPIRE_FODDER  /  HORDE_LEADER_CAPTIVE` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

# BRG-M46 — fury

Brogue kind **46**, `MK_FURY`; runtime class `BrogueMonsterK46`.

## Brogue facts

> A creature of inchoate rage made flesh, the fury's moist wings beat loudly in the darkness.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1116); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1317).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 50, 0, 0 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_RED_BLOOD`, `MONST_FLIES`, `MONST_NEVER_SLEEPS`.
- Source action/prose strings: ["flagellating", "Flagellating", "drubs", "fustigates", "castigates"]

## Model work card

- Status: authored-static.
- Recipe: `winged`.
- Authored silhouette dimensions: 30 / 58 / 40 map units. Clearance: 16 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: demon, membrane, claws.
- [Runtime model](../../mod/BrogueDoom/models/monsters/46_fury.obj).
- [Editable Blender source](../../assets/monsters/sources/46_fury.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L799](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L799) | leader/summoner, member | `MK_FURY` | `18`–`26` | `0` | `0` |
| [L817](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L817) | member | `MK_LICH` | `0`–`0` | `0` | `HORDE_IS_SUMMONED` |
| [L822](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L822) | member | `MK_ELDRITCH_TOTEM` | `0`–`0` | `0` | `HORDE_IS_SUMMONED  /  HORDE_DIES_ON_LEADER_DEATH` |
| [L837](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L837) | member | `MK_IMP` | `18`–`26` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L839](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L839) | member | `MK_DAR_BLADEMASTER` | `18`–`26` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L841](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L841) | member | `MK_DAR_PRIESTESS` | `18`–`26` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

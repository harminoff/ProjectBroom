# BRG-M40 — lich

Brogue kind **40**, `MK_LICH`; runtime class `BrogueMonsterK40`.

## Brogue facts

> The desiccated form of an ancient sorcerer, animated by dark arts and lust for power, commands the obedience of the infernal planes. $HISHER essence is anchored to reality by a phylactery that is always in $HISHER possession, and the lich cannot die unless $HISHER phylactery is destroyed.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1104); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1295).

- Large flag: `true` (not a physical measurement).
- Base glyph RGB: 100, 100, 100 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `BOLT_FIRE`, `DF_ASH_BLOOD`, `MA_CAST_SUMMON`, `MONST_CARRY_ITEM_25`, `MONST_MAINTAINS_DISTANCE`, `MONST_NO_POLYMORPH`.
- Source action/prose strings: ["enchanting", "Enchanting", "touches", "rasps a terrifying incantation!"]

## Model work card

- Status: authored-static.
- Recipe: `humanoid`.
- Authored silhouette dimensions: 30 / 36 / 66 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: undead, robe, phylactery, ribs.
- [Runtime model](../../mod/BrogueDoom/models/monsters/40_lich.obj).
- [Editable Blender source](../../assets/monsters/sources/40_lich.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L816](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L816) | leader/summoner | `MK_LICH` | `0`–`0` | `0` | `HORDE_IS_SUMMONED` |
| [L817](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L817) | leader/summoner | `MK_LICH` | `0`–`0` | `0` | `HORDE_IS_SUMMONED` |
| [L818](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L818) | member | `MK_PHYLACTERY` | `0`–`0` | `0` | `HORDE_IS_SUMMONED` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

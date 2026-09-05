# BRG-M66 — phoenix egg

Brogue kind **66**, `MK_PHOENIX_EGG`; runtime class `BrogueMonsterK66`.

## Brogue facts

> Cradled in a nest of cooling ashes, the translucent membrane of the phoenix egg reveals a yolk that glows brighter by the second.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1161); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1386).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 100, 0, 0 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_ASH_BLOOD`, `MA_CAST_SUMMON`, `MA_ENTER_SUMMONS`, `MONST_ALWAYS_HUNTING`, `MONST_IMMOBILE`, `MONST_IMMUNE_TO_FIRE`, `MONST_IMMUNE_TO_WEAPONS`, `MONST_IMMUNE_TO_WEBS`, `MONST_INANIMATE`, `MONST_NEVER_SLEEPS`, `MONST_NO_POLYMORPH`, `MONST_WILL_NOT_USE_STAIRS`.
- Source action/prose strings: ["cremating", "Cremating", "touches", "bursts as a newborn phoenix rises from the ashes!"]

## Model work card

- Status: authored-static.
- Recipe: `egg`.
- Authored silhouette dimensions: 26 / 26 / 25 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: egg, ash, yolk.
- [Runtime model](../../mod/BrogueDoom/models/monsters/66_phoenix_egg.obj).
- [Editable Blender source](../../assets/monsters/sources/66_phoenix_egg.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L820](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L820) | leader/summoner | `MK_PHOENIX_EGG` | `0`–`0` | `0` | `HORDE_IS_SUMMONED` |
| [L938](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L938) | leader/summoner | `MK_PHOENIX_EGG` | `1`–`DEEPEST_LEVEL` | `0` | `HORDE_MACHINE_LEGENDARY_ALLY  /  HORDE_ALLIED_WITH_PLAYER` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

# BRG-M53 — vampire

Brogue kind **53**, `MK_VAMPIRE`; runtime class `BrogueMonsterK53`.

## Brogue facts

> This vampire lives a solitary life deep underground, consuming any warm-blooded creature unfortunate enough to venture near $HISHER lair.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1131); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1341).

- Large flag: `true` (not a physical measurement).
- Base glyph RGB: 100, 100, 100 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `BOLT_BLINKING`, `BOLT_DISCORD`, `DF_BLOOD_EXPLOSION`, `DF_RED_BLOOD`, `MA_CAST_SUMMON`, `MA_DF_ON_DEATH`, `MA_ENTER_SUMMONS`, `MA_TRANSFERENCE`, `MONST_FLEES_NEAR_DEATH`, `MONST_MALE`.
- Source action/prose strings: ["draining", "Drinking", "grazes", "bites", "buries $HISHER fangs in", "spreads his cloak and bursts into a cloud of bats!"]

## Model work card

- Status: authored-static.
- Recipe: `humanoid`.
- Authored silhouette dimensions: 32 / 40 / 64 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: cloak, fangs, pale.
- [Runtime model](../../mod/BrogueDoom/models/monsters/53_vampire.obj).
- [Editable Blender source](../../assets/monsters/sources/53_vampire.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L815](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L815) | leader/summoner | `MK_VAMPIRE` | `0`–`0` | `0` | `HORDE_IS_SUMMONED` |
| [L849](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L849) | leader/summoner | `MK_VAMPIRE` | `10`–`DEEPEST_LEVEL` | `0` | `HORDE_MACHINE_BOSS` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

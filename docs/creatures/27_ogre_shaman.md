# BRG-M27 — ogre shaman

Brogue kind **27**, `MK_OGRE_SHAMAN`; runtime class `BrogueMonsterK27`.

## Brogue facts

> This ogre is bent with age, but what $HESHE has lost in physical strength, $HESHE has more than gained in occult power.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1078); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1253).

- Large flag: `true` (not a physical measurement).
- Base glyph RGB: 0, 100, 0 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `BOLT_HASTE`, `BOLT_SPARK`, `DF_RED_BLOOD`, `MA_AVOID_CORRIDORS`, `MA_CAST_SUMMON`, `MONST_CAST_SPELLS_SLOWLY`, `MONST_FEMALE`, `MONST_MAINTAINS_DISTANCE`, `MONST_MALE`.
- Source action/prose strings: ["performing a ritual on", "Performing ritual", "cudgels", "clubs", "chants in a harsh, guttural tongue!"]

## Model work card

- Status: authored-static.
- Recipe: `humanoid`.
- Authored silhouette dimensions: 42 / 44 / 70 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: brute, hunched, staff, relics.
- [Runtime model](../../mod/BrogueDoom/models/monsters/27_ogre_shaman.obj).
- [Editable Blender source](../../assets/monsters/sources/27_ogre_shaman.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L786](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L786) | leader/summoner | `MK_OGRE_SHAMAN` | `14`–`20` | `0` | `0` |
| [L814](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L814) | leader/summoner | `MK_OGRE_SHAMAN` | `0`–`0` | `0` | `HORDE_IS_SUMMONED` |
| [L832](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L832) | member | `MK_TROLL` | `17`–`19` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

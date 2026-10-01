# BRG-M35 — centaur

Brogue kind **35**, `MK_CENTAUR`; runtime class `BrogueMonsterK35`.

## Brogue facts

> Half man and half horse, the centaur is an expert with the bow and arrow -- hunter and steed fused into a single creature.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1094); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1280).

- Large flag: `true` (not a physical measurement).
- Base glyph RGB: 80, 67, 15 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `BOLT_DISTANCE_ATTACK`, `DF_RED_BLOOD`, `MONST_MAINTAINS_DISTANCE`, `MONST_MALE`.
- Source action/prose strings: ["studying", "Studying", "shoots"]

## Model work card

- Status: authored-skeletal.
- Recipe: `weighted-centaur`.
- Authored silhouette dimensions: 55.0225 / 28.5856 / 76.4161 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: horse, bow, quiver.
- [Runtime model](../../mod/BrogueDoom/models/monsters/35_centaur.iqm).
- [Editable Blender source](../../assets/monsters/centaur/centaur-animated.blend).
- [Animation manifest](../../assets/monsters/centaur/animation.json); 39 bones.
- [Shared skeletal workflow and verification](../skeletal-enemy-workflow.md).

[Centaur authoring and actual verification](../centaur-animation.md).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L787](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L787) | leader/summoner, member | `MK_CENTAUR` | `14`–`21` | `0` | `0` |
| [L831](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L831) | leader/summoner | `MK_CENTAUR` | `12`–`19` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [x] Skeletal clips authored; see animation report for actual verification and approval scope.

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

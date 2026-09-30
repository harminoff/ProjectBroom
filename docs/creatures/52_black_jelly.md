# BRG-M52 — black jelly

Brogue kind **52**, `MK_BLACK_JELLY`; runtime class `BrogueMonsterK52`.

## Brogue facts

> This blob of jet-black goo is as rare as $HESHE is deadly. Few creatures of the dungeon can withstand $HISHER caustic assault. Beware.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1129); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1338).

- Large flag: `true` (not a physical measurement).
- Base glyph RGB: 0, 0, 0 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_PURPLE_BLOOD`, `MA_CLONE_SELF_ON_DEFEND`.
- Source action/prose strings: ["absorbing", "Feeding", "smears", "slimes", "drenches"]

## Model work card

- Status: authored-skeletal.
- Recipe: `weighted-black_jelly`.
- Authored silhouette dimensions: 53.2612 / 50.6634 / 25.2147 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: connected melting ink heap, curtain folds pooling into drips, glossy spill-pool apron, violet-depth inclusions, view-dependent gloss sheen.
- [Runtime model](../../mod/BrogueDoom/models/monsters/52_black_jelly.iqm).
- [Editable Blender source](../../assets/monsters/black_jelly/black-jelly-animated.blend).
- [Animation manifest](../../assets/monsters/black_jelly/animation.json); 58 bones.
- [Shared skeletal workflow and verification](../skeletal-enemy-workflow.md).
- [Black jelly authoring and actual verification](../black-jelly-animation.md).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L848](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L848) | leader/summoner | `MK_BLACK_JELLY` | `5`–`15` | `0` | `HORDE_MACHINE_BOSS` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [x] Skeletal clips authored; see animation report for actual verification and approval scope.

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

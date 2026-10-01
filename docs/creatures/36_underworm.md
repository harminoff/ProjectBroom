# BRG-M36 — underworm

Brogue kind **36**, `MK_UNDERWORM`; runtime class `BrogueMonsterK36`.

## Brogue facts

> A strange and horrifying creature of the earth's deepest places, larger than an ogre but capable of squeezing through tiny openings. When hungry, the underworm will burrow behind the walls of a cavern and lurk dormant and motionless -- often for months -- until $HESHE can feel the telltale vibrations of nearby prey.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1096); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1283).

- Large flag: `true` (not a physical measurement).
- Base glyph RGB: 80, 60, 40 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_WORM_BLOOD`, `MONST_NEVER_SLEEPS`.
- Source action/prose strings: ["consuming", "Consuming", "slams", "bites", "tail-whips"]

## Model work card

- Status: authored-skeletal.
- Recipe: `weighted-underworm`.
- Authored silhouette dimensions: 55.6958 / 55.1619 / 62.1957 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: huge legless annulated worm coiled on the floor, about thirty painted ridge-and-groove segments with wet highlights, pale saddle band behind a blunt swollen head, round toothed maw: lip ring, outer and inner tooth rings, dark throat, hinged lower jaw that opens wide; no eyes, salmon-pink flanks, pale cream belly, dark mauve back.
- [Runtime model](../../mod/BrogueDoom/models/monsters/36_underworm.iqm).
- [Editable Blender source](../../assets/monsters/underworm/underworm-animated.blend).
- [Animation manifest](../../assets/monsters/underworm/animation.json); 40 bones.
- [Shared skeletal workflow and verification](../skeletal-enemy-workflow.md).
- [Underworm authoring and actual verification](../underworm-animation.md).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| — | No direct table reference; may be created by another Brogue path. | — | — | — | — |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [x] Skeletal clips authored; see animation report for actual verification and approval scope.

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

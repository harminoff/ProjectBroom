# BRG-M00 — you

Brogue kind **0**, `MK_YOU`; runtime class `BrogueMonsterK00`.

## Brogue facts

> A naked adventurer in an unforgiving place, bereft of equipment and confused about the circumstances.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1027); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1168).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 100, 90, 30 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_RED_BLOOD`, `MONST_FEMALE`, `MONST_MALE`.
- Source action/prose strings: ["studying", "Studying", "hit"]

## Model work card

- Status: reference-only.
- Recipe: `existing`.
- Authored silhouette dimensions: reference map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: see existing rat authoring guide.
- [Runtime model](../../mod/BrogueDoom/models/monsters/00_you.obj).

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
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

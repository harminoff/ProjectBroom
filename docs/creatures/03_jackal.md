# BRG-M03 — jackal

Brogue kind **3**, `MK_JACKAL`; runtime class `BrogueMonsterK03`.

## Brogue facts

> The jackal prowls the caverns for intruders to rend with $HISHER powerful jaws.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1032); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1177).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 60, 42, 27 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_RED_BLOOD`, `DF_URINE`.
- Source action/prose strings: ["tearing at", "Eating", "claws", "bites", "mauls"]

## Model work card

- Status: authored-static.
- Recipe: `quadruped`.
- Authored silhouette dimensions: 52 / 22 / 32 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: canine, jaws, fur.
- [Runtime model](../../mod/BrogueDoom/models/monsters/03_jackal.obj).
- [Editable Blender source](../../assets/monsters/sources/03_jackal.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L748](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L748) | leader/summoner | `MK_JACKAL` | `1`–`3` | `0` | `0` |
| [L749](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L749) | leader/summoner, member | `MK_JACKAL` | `3`–`7` | `0` | `0` |
| [L767](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L767) | member | `MK_GOBLIN` | `6`–`12` | `0` | `0` |
| [L945](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L945) | member | `MK_GOBLIN` | `6`–`12` | `0` | `HORDE_MACHINE_GOBLIN_WARREN` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

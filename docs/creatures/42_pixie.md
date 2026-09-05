# BRG-M42 — pixie

Brogue kind **42**, `MK_PIXIE`; runtime class `BrogueMonsterK42`.

## Brogue facts

> A tiny humanoid sparkles in the gloom, the hum of $HISHER beating wings punctuated by intermittent peals of high-pitched laughter. What $HESHE lacks in physical endurance, $HESHE makes up for with $HISHER wealth of mischievous magical abilities.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1108); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1305).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 60, 60, 60 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `BOLT_DISCORD`, `BOLT_NEGATION`, `BOLT_SLOW_2`, `BOLT_SPARK`, `DF_GREEN_BLOOD`, `MONST_FEMALE`, `MONST_FLIES`, `MONST_FLITS`, `MONST_MAINTAINS_DISTANCE`, `MONST_MALE`.
- Source action/prose strings: ["sprinkling dust on", "Dusting", "pokes"]

## Model work card

- Status: authored-static.
- Recipe: `winged`.
- Authored silhouette dimensions: 18 / 34 / 20 map units. Clearance: 16 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: fairy, membrane.
- [Runtime model](../../mod/BrogueDoom/models/monsters/42_pixie.obj).
- [Editable Blender source](../../assets/monsters/sources/42_pixie.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L790](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L790) | leader/summoner | `MK_PIXIE` | `14`–`21` | `0` | `0` |
| [L838](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L838) | leader/summoner | `MK_PIXIE` | `14`–`21` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L900](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L900) | leader/summoner | `MK_PIXIE` | `11`–`21` | `MONSTER_CAGE_CLOSED` | `HORDE_MACHINE_KENNEL  /  HORDE_LEADER_CAPTIVE` |
| [L914](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L914) | leader/summoner | `MK_PIXIE` | `11`–`21` | `MONSTER_CAGE_CLOSED` | `HORDE_VAMPIRE_FODDER  /  HORDE_LEADER_CAPTIVE` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

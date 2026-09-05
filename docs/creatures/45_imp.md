# BRG-M45 — imp

Brogue kind **45**, `MK_IMP`; runtime class `BrogueMonsterK45`.

## Brogue facts

> This trickster demon moves with astonishing speed and delights in stealing from $HISHER enemies and blinking away.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1114); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1314).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 100, 60, 66 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `BOLT_BLINKING`, `DF_GREEN_BLOOD`, `MA_HIT_STEAL_FLEE`.
- Source action/prose strings: ["dissecting", "Dissecting", "slices", "cuts"]

## Model work card

- Status: authored-static.
- Recipe: `humanoid`.
- Authored silhouette dimensions: 30 / 30 / 35 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: demon, tail, claws.
- [Runtime model](../../mod/BrogueDoom/models/monsters/45_imp.obj).
- [Editable Blender source](../../assets/monsters/sources/45_imp.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L797](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L797) | leader/summoner | `MK_IMP` | `17`–`24` | `0` | `0` |
| [L837](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L837) | leader/summoner | `MK_IMP` | `18`–`26` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L838](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L838) | member | `MK_PIXIE` | `14`–`21` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L840](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L840) | member | `MK_DAR_BLADEMASTER` | `18`–`26` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L842](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L842) | member | `MK_DAR_BATTLEMAGE` | `18`–`26` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L899](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L899) | leader/summoner | `MK_IMP` | `15`–`26` | `MONSTER_CAGE_CLOSED` | `HORDE_MACHINE_KENNEL  /  HORDE_LEADER_CAPTIVE` |
| [L913](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L913) | leader/summoner | `MK_IMP` | `15`–`AMULET_LEVEL` | `MONSTER_CAGE_CLOSED` | `HORDE_VAMPIRE_FODDER  /  HORDE_LEADER_CAPTIVE` |
| [L921](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L921) | leader/summoner | `MK_IMP` | `15`–`DEEPEST_LEVEL` | `0` | `HORDE_MACHINE_THIEF` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

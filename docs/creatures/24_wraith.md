# BRG-M24 — wraith

Brogue kind **24**, `MK_WRAITH`; runtime class `BrogueMonsterK24`.

## Brogue facts

> The wraith's hollow eye sockets stare hungrily at the world from $HISHER emaciated frame, and $HISHER long, bloodstained nails grope ceaselessly at the air for a fresh victim.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1073); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1244).

- Large flag: `true` (not a physical measurement).
- Base glyph RGB: 66, 66, 25 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_GREEN_BLOOD`, `MONST_FLEES_NEAR_DEATH`.
- Source action/prose strings: ["devouring", "Feeding", "clutches", "claws", "bites"]

## Model work card

- Status: authored-static.
- Recipe: `humanoid`.
- Authored silhouette dimensions: 30 / 32 / 65 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: gaunt, sockets, blood_nails.
- [Runtime model](../../mod/BrogueDoom/models/monsters/24_wraith.obj).
- [Editable Blender source](../../assets/monsters/sources/24_wraith.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L777](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L777) | leader/summoner | `MK_WRAITH` | `10`–`17` | `0` | `0` |
| [L796](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L796) | leader/summoner, member | `MK_WRAITH` | `16`–`23` | `0` | `0` |
| [L865](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L865) | leader/summoner | `MK_WRAITH` | `11`–`20` | `0` | `HORDE_MACHINE_CAPTIVE  /  HORDE_LEADER_CAPTIVE` |
| [L873](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L873) | leader/summoner | `MK_WRAITH` | `10`–`17` | `STATUE_DORMANT` | `HORDE_MACHINE_STATUE` |
| [L928](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L928) | leader/summoner | `MK_WRAITH` | `10`–`17` | `STATUE_INSTACRACK` | `HORDE_SACRIFICE_TARGET` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

# BRG-M05 — monkey

Brogue kind **5**, `MK_MONKEY`; runtime class `BrogueMonsterK05`.

## Brogue facts

> Mischievous trickster that $HESHE is, the monkey lives to steal shiny trinkets from passing adventurers.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1035); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1183).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 60, 25, 25 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_RED_BLOOD`, `DF_URINE`, `MA_HIT_STEAL_FLEE`.
- Source action/prose strings: ["examining", "Examining", "tweaks", "bites", "punches"]

## Model work card

- Status: authored-static.
- Recipe: `humanoid`.
- Authored silhouette dimensions: 40 / 27 / 32 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: primate, tail, fur.
- [Runtime model](../../mod/BrogueDoom/models/monsters/05_monkey.obj).
- [Editable Blender source](../../assets/monsters/sources/05_monkey.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L751](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L751) | leader/summoner | `MK_MONKEY` | `2`–`9` | `0` | `0` |
| [L763](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L763) | leader/summoner, member | `MK_MONKEY` | `5`–`13` | `0` | `0` |
| [L825](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L825) | leader/summoner | `MK_MONKEY` | `1`–`5` | `0` | `HORDE_LEADER_CAPTIVE  /  HORDE_NEVER_OOD` |
| [L891](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L891) | leader/summoner | `MK_MONKEY` | `1`–`5` | `MONSTER_CAGE_CLOSED` | `HORDE_MACHINE_KENNEL  /  HORDE_LEADER_CAPTIVE` |
| [L906](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L906) | leader/summoner | `MK_MONKEY` | `1`–`5` | `MONSTER_CAGE_CLOSED` | `HORDE_VAMPIRE_FODDER  /  HORDE_LEADER_CAPTIVE` |
| [L920](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L920) | leader/summoner | `MK_MONKEY` | `1`–`14` | `0` | `HORDE_MACHINE_THIEF` |
| [L924](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L924) | leader/summoner | `MK_MONKEY` | `1`–`5` | `STATUE_INSTACRACK` | `HORDE_SACRIFICE_TARGET` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

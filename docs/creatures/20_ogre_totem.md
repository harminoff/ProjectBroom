# BRG-M20 — ogre totem

Brogue kind **20**, `MK_OGRE_TOTEM`; runtime class `BrogueMonsterK20`.

## Brogue facts

> Ancient ogres versed in the eldritch arts have assembled this totem and imbued $HIMHER with occult power.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1065); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1232).

- Large flag: `false` (not a physical measurement).
- Base glyph RGB: 0, 100, 0 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `BOLT_HEALING`, `BOLT_SLOW_2`, `DF_RUBBLE_BLOOD`, `MONST_IMMOBILE`, `MONST_IMMUNE_TO_WEBS`, `MONST_INANIMATE`, `MONST_NEVER_SLEEPS`, `MONST_WILL_NOT_USE_STAIRS`.
- Source action/prose strings: ["gazing at", "Gazing", "hits"]

## Model work card

- Status: authored-static.
- Recipe: `totem`.
- Authored silhouette dimensions: 32 / 32 / 60 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: wood, bone, occult.
- [Runtime model](../../mod/BrogueDoom/models/monsters/20_ogre_totem.obj).
- [Editable Blender source](../../assets/monsters/sources/20_ogre_totem.blend).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L782](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L782) | leader/summoner | `MK_OGRE_TOTEM` | `12`–`19` | `0` | `HORDE_NO_PERIODIC_SPAWN` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [ ] Animation refinement if later requested (current pose is static).

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

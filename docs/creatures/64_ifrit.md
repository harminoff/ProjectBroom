# BRG-M64 — ifrit

Brogue kind **64**, `MK_IFRIT`; runtime class `BrogueMonsterK64`.

## Brogue facts

> A whirling desert storm given human shape, the ifrit's twin scimitars flicker in the darkness and $HISHER eyes burn with otherworldly zeal.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1157); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1380).

- Large flag: `true` (not a physical measurement).
- Base glyph RGB: 50, 10, 100 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `BOLT_DISCORD`, `DF_ASH_BLOOD`, `MONST_FLIES`, `MONST_IMMUNE_TO_FIRE`, `MONST_MALE`.
- Source action/prose strings: ["absorbing", "Absorbing", "cuts", "slashes", "lacerates"]

## Model work card

- Status: authored-skeletal.
- Recipe: `weighted-ifrit`.
- Authored silhouette dimensions: 36.9518 / 57.1654 / 66.2329 map units. Clearance: 16 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: very broad dark-violet storm-djinn: torso, neck, shoulders and arms are one fused connected skin with fan-shaped pecs, flat abdominal plate, lats, traps and tapering biceps and forearms, large fanged face under a heavy brow, swept-back horns, full moustache and beard, gold collar, armlets and bracers over a crimson sash, twin curved scimitars with dark spines and ember-forged edge strips, no legs: tapering vortex of layered, ragged smoke sheets around a dark core, sparked with embers, ember eyes, blade edges, crown flame and burst flecks fullbright; skin lighting baked with ember under-glow.
- [Runtime model](../../mod/BrogueDoom/models/monsters/64_ifrit.iqm).
- [Editable Blender source](../../assets/monsters/ifrit/ifrit-animated.blend).
- [Animation manifest](../../assets/monsters/ifrit/animation.json); 36 bones.
- [Shared skeletal workflow and verification](../skeletal-enemy-workflow.md).
- [Ifrit authoring and actual verification](../ifrit-animation.md).

## Brogue encounter-table references

These are nominal table ranges and weights, not guaranteed encounter depths or percentages. Summoning rows use level 0 and name a summoner; captive/machine/out-of-depth selection follows Brogue itself. Expressions such as `DEEPEST_LEVEL-1` are preserved rather than guessed. No spawn rules are changed.

| Source row | Role | Leader/summoner | Nominal range | Terrain | Flags |
| --- | --- | --- | --- | --- | --- |
| [L937](../../src/brogue-mapgen/src/variants/GlobalsBrogue.c#L937) | leader/summoner | `MK_IFRIT` | `1`–`DEEPEST_LEVEL` | `0` | `HORDE_MACHINE_LEGENDARY_ALLY  /  HORDE_ALLIED_WITH_PLAYER` |

## Acceptance gates

Machine-readable results live in [bestiary-index.json](../../assets/monsters/bestiary-index.json). A generated asset is not automatically visually approved. These generated cards are not a hand-edited checklist: record later acceptance under the index entry’s `verification` object, which regeneration preserves.

- [ ] Individual art/signature-feature approval.
- [ ] Normal encounter at gameplay distance and lighting.
- [ ] Turnaround, feet/hover, 64-unit corridor clearance and camera comparison.
- [x] Skeletal clips authored; see animation report for actual verification and approval scope.

Original generated Project Broom mesh/skin: CC-BY-SA-4.0. Brogue text remains under its existing upstream licensing. No third-party artwork imported.

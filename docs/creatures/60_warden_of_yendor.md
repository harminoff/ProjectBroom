# BRG-M60 — Warden of Yendor

Brogue kind **60**, `MK_WARDEN_OF_YENDOR`; runtime class `BrogueMonsterK60`.

## Brogue facts

> An immortal presence stalks through the dungeon, implacably hunting that which was taken... and the one who took it.

Exact upstream placeholders such as `$HISHER` are intentionally preserved. [Catalog source](../../src/brogue-mapgen/src/brogue/Globals.c#L1147); [prose source](../../src/brogue-mapgen/src/brogue/Globals.c#L1365).

- Large flag: `true` (not a physical measurement).
- Base glyph RGB: 50, -100, 30 on Brogue's 0–100 scale; these are identity cues, not literal whole-body materials.
- Catalog tokens: `DF_RUBBLE`, `MONST_ALWAYS_HUNTING`, `MONST_INVULNERABLE`, `MONST_NEVER_SLEEPS`, `MONST_NO_POLYMORPH`.
- Source action/prose strings: ["gazing at", "Gazing", "strikes"]

## Model work card

- Status: authored-skeletal.
- Recipe: `weighted-warden_of_yendor`.
- Authored silhouette dimensions: 21.7553 / 40.4183 / 69.1812 map units. Clearance: 0 units.
- Numerical size and details not explicitly stated by Brogue are artistic interpretation, not new game facts.
- Visual construction cues: towering faceless armoured hunter in dark aubergine-violet plate, tall blank helm with a narrow burning violet visor slit and a fan of crest blades, vast spiked pauldrons over a wasp-waisted plated body and long tassets, massive black-iron gauntlets with knuckle plates, Yendorian violet-magenta light in a chest seam, visor slit, forearm strips and rune lines, low two-handed overhead-to-forward hammer blow, collapses into broken armour and rubble as the light goes out.
- [Runtime model](../../mod/BrogueDoom/models/monsters/60_warden_of_yendor.iqm).
- [Editable Blender source](../../assets/monsters/warden_of_yendor/warden-of-yendor-animated.blend).
- [Animation manifest](../../assets/monsters/warden_of_yendor/animation.json); 39 bones.
- [Shared skeletal workflow and verification](../skeletal-enemy-workflow.md).
- [Warden of Yendor authoring and actual verification](../warden-of-yendor-animation.md).

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

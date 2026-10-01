# Item appearance audit

All audited categories are now implemented. Potions use ABI v22's color index;
ABI v23 adds the assigned appearance string for the remaining categories.
See [implementation and verification](item-appearance-implementation.md).
The table below preserves the original pre-fix findings.

Source audit: 2026-09-09. Scope: randomized item appearances, floor pickup models,
held devices, names, and thrown-item model selection. No gameplay or asset changes
were made by this audit. Findings below are source-confirmed; they have not been
reproduced in a new runtime capture.

## Confirmed mismatches

| Category | Brogue appearance | Current presentation | Finding |
| --- | --- | --- | --- |
| Potions | 21 shuffled color names | Every bottle body uses the same blue-green glass material (base RGB 77, 137, 144) | Bottle color does not track the named color. Identified models add effect-based seals, not the shuffled color. |
| Wands | 12 shuffled metals | Floor models have wooden shafts and brass ferrules; held models use brass | Named metal is not represented; floor and held materials also disagree. |
| Staves | 21 shuffled woods | Generic wood on floor and held models | Wood appearance is not selected from the authoritative flavor. |
| Rings | 18 shuffled gemstones | Generic blue-green stone when unidentified; ruby/jade/azure accent selected by kind when known | Stone does not track the named gem. |
| Scrolls | Shuffled titles | Repeated decorative ink strokes | Physical lettering does not reproduce the title; textual naming is supplied by Brogue. |

The pinned potion colors are crimson, scarlet, orange, yellow, green, blue,
indigo, violet, puce, mauve, burgundy, turquoise, aquamarine, gray, pink, white,
lavender, tan, brown, cyan, and black.

## Identity handling

The bridge obtains `displayName` and `detailText` through Brogue's `itemName()`
and `itemDetails()`. Floor pickup selection correctly uses a generic model for
unidentified potions, scrolls, staves, wands, and rings. These are useful existing
guards, but generic models discard the visible flavor differences.

Thrown-item selection is inconsistent with that guard:
`BeginProjectileAnimation()` selects `BroguePickupC%04dK%02d` directly from event
category and kind. `recordItemEvent()` exports the raw kind, and carried items
receive the Throw action. This is a source-confirmed route to an effect-specific
model without a knowledge check. Decorations could disclose identity even while
the item's name remains unidentified. Runtime visibility of that disclosure has
not been measured.

## Root cause and correction design

`BrogueBridgeItemState` has no separate appearance descriptor. Brogue's
`shuffleFlavors()` owns the per-game color/material/title assignments; the
frontend only selects category/kind models and their shared atlas.

Export a copied, frontend-neutral appearance descriptor from Brogue independently
of effect identity. Use it consistently for floor, held, and thrown presentation.
Do not infer color from hidden effect kind, recreate the shuffle in UZDoom, or
parse display names: identification and player Call names can replace the flavor
in that text. Identification should preserve the item's physical appearance.

This requires a versioned bridge-contract change with all consumers updated.
Projectile presentation should retain the item's knowledge-safe appearance even
if the authoritative item is consumed by impact before animation completes.

Verification for a subsequent fix should cover every flavor, multiple seeds,
identification, Call naming, pickup/drop, throwing, and save/load. Compare Brogue
state hashes to confirm presentation does not change simulation or RNG, then
capture floor/held/projectile appearances in the packaged runtime.

## Source evidence

- `src/brogue-mapgen/src/brogue/Globals.c`: reference flavor catalogs.
- `src/brogue-mapgen/src/brogue/Items.c`: `shuffleFlavors()` and `itemName()`.
- `src/brogue-mapgen/src/brogue/BrogueBridge.h`: item copied-data contract.
- `src/brogue-mapgen/src/brogue/BrogueBridge.c`: item export, action flags,
  `recordItemEvent()`, and authoritative throw dispatch.
- `src/gzdoom-bridge/brogue_bridge_frontend.cpp`: `PickupVisualKind()`,
  `PickupClassName()`, `SyncItems()`, and `BeginProjectileAnimation()`.
- `tools/pickup_models/generate.py`: delegates to the detailed model generator.
- `tools/pickup_models/detailed.py`: shared glass, wood, accents, and lettering.
- `tools/weapon_models/devices.py`: fixed held-device materials.
- `mod/BrogueDoom/models/pickups/MODELDEF.txt`: shared `BRGPICKS.png` skin.

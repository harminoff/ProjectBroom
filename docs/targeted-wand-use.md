# Targeted wand use

Contribution category: bridge parity. No new gameplay rules or assets are
introduced; Brogue CE remains authoritative.

Select a wand in inventory and press Enter/U. Move the cursor or press Tab to
cycle Brogue-eligible targets. Enter/click uses the wand; Escape/right-click
cancels without submitting an action. Brogue's own item description continues
to report identification knowledge and the number of discharges.

## Implementation

API v15 adds `BROGUE_COMMAND_USE_WAND`, `BROGUE_ITEM_ACTION_TARGET_WAND`, and
`brogue_bridge_preview_wand()`. `BrogueBridgeWandPreview` shares the staff
preview's copied-data layout. Both public preview entry points validate the
carried stable ID and their own item category, then call one internal adapter.
The DLL exports, frontend loader, harness, and catalog version metadata are
updated together. Old API versions and stale revisions are rejected.

The device entry point is now named `applyDeviceAtTarget()` and accepts staffs
and wands. It calls the existing `useStaffOrWand()` and `playerTurnEnded()`
paths. Brogue alone decides effects, reflection, auto-identification, charge
depletion, and turns. A charged wand use decrements `charges` and increments
`enchant2`, Brogue's discharge counter. An unknown depleted wand fizzles and
consumes a turn without incrementing that counter. A known depleted wand
returns without a turn. Wands do not inherit staff recharge or blinking-range
rules.

`previewDeviceTarget()` reuses `nextTargetAfter()`, `getLineCoordinates()`, and
the rendering-disabled `hiliteTrajectory()` from the staff work. Unknown
effects use the neutral guide. Previews neither execute bolts nor consume
substantive RNG. This is a shared device implementation, not completion of the
separate generalized interaction/target-preview backlog item.

## Verification

- Bridge executable/DLL: `powershell -ExecutionPolicy Bypass -File scripts/build-bridge.ps1` passed.
- Standalone/exporter: `powershell -ExecutionPolicy Bypass -File scripts/build-mapgen.ps1` passed.
- Native GZDoom: `cmake --build .build/gzdoom --config Release -j 4 -- /nodeReuse:false` passed.
  The child environment had one case-insensitive PATH entry and
  `MSBUILDDISABLENODEREUSE=1`, as required by this host's MSBuild behavior.
- `python -m unittest tools.test_brogue_bridge tools.test_broguedoom_resources tools.mapcompiler.test_compile`:
  **71 tests passed**.
- The `--wand-smoke` harness covers all nine wand kinds, obstruction, guaranteed
  reflection, known/unknown depletion, and auto-identification: 14 scenarios on
  seeds **1, 2, 42, 12345, 99999**, each repeated for deterministic output.
- Every scenario compares the bridge command against normal Brogue
  `apply()` -> `chooseTarget()` with mouse/escape events supplied through the
  terminal platform callback. Both routes continue with the same WAIT action;
  gameplay hashes, turns, substantive RNG counts, charges, and discharge
  counters match. Preview/cancel purity, invalid/self-targets, missing IDs,
  wrong item categories, old ABI versions, and stale revisions are checked.
- The seed-1 300-action long-run check reaches Brogue's normal death at turn
  195, with unchanged final hash `605cf66657aa5f8e`.
- `scripts/launch-source-bridge.ps1 -Seed 19` prepared the 40-map campaign and
  passed topology/package verification, then launched the rebuilt GZDoom.
- `powershell -ExecutionPolicy Bypass -File scripts/test-wand-ui.ps1` passed.
  The frontend picks up seed 19's brass wand at **70,14** through 47 ordinary
  Brogue actions. Inventory/targeting cancellation preserves **revision 48,
  turn 47**; firing reaches **revision 49, turn 48**. Actual engine framebuffer
  captures and logs are under ignored `artifacts/wand-ui/`.
- The seed-14 staff UI regression also passes against API v15: cancellation
  retains revision 43/turn 42, and firing reaches revision 44/turn 43.

The native UI smoke uses `brg_wand_smoke` and the same input handlers as normal
inventory targeting. It requires an existing carried wand; it does not create
equipment or bypass simulation rules. `scripts/test-staff-ui.ps1` retains the
seed-14 staff regression; the wand wrapper selects the wand route and evidence
directory through its `-Wand` option.

## Limits

The standalone-path comparison is deterministic and runs real Brogue input
and effect code in the headless harness. It is not a separately launched
graphical Brogue recording comparison. Physical keyboard/mouse injection was
not tested; native input handlers and rendered frames were exercised directly.
General target contracts, complete interaction state machines, exported device
charge fields, and 3D bolt animations remain separate backlog work.

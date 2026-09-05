# Targeted staff use

Current preview contract: [generalized targeting, API v16](generalized-targeting-preview.md).
The implementation notes below describe the original v14/v15 delivery.

Contribution category: bridge parity. Gameplay declaration: no new rules;
Brogue CE remains authoritative. No new assets or licenses are introduced.

In the inventory, select a staff and press Enter/U. Move the target cursor,
use Tab to cycle Brogue-eligible targets, then press Enter or click to use the
staff. Escape/right-click cancels without submitting a command. Existing
Brogue blinking warnings use the native confirmation overlay.

## Authority and scope

API v14 adds `BROGUE_COMMAND_USE_STAFF`, the `TARGET_STAFF` inventory action
flag, and `brogue_bridge_preview_staff()`. The DLL export list, native loader,
headless consumer, and monster catalog/registry version metadata are updated.

The standalone call chain is `apply()` -> `useStaffOrWand()` -> `chooseTarget()`
-> `playerCancelsBlinking()` -> `zap()`, followed by Brogue's charge accounting
and `playerTurnEnded()`. `applyDeviceAtTarget()` supplies a semantic target to
the same `useStaffOrWand()` implementation and uses the same turn-ending path.
Standalone callers still pass no supplied target and retain their terminal UI.
No bolt, reflection, recharge, identification, or damage rules are duplicated.

The preview calls `nextTargetAfter()` and `getLineCoordinates()` and reuses
`hiliteTrajectory()` with rendering disabled. Known effects use their Brogue
bolt definition; unknown effects use the neutral aiming guide. Known blinking
range comes from `staffBlinkDistance(netEnchant(...))`. Range is a visual cue,
not a frontend rejection rule. The preview never executes `zap()`, asks a
confirmation, or consumes substantive RNG. Cancel discards the frontend cursor.

Commands validate the ABI version, carried stable ID, staff category, target
coordinates, and expected revision before executing. Self-targets are rejected.
Brogue decides whether use consumes time: a known empty staff consumes none;
an unknown empty staff fizzles, updates knowledge, and consumes a turn.

## Verification

- `powershell -ExecutionPolicy Bypass -File scripts/build-bridge.ps1`: executable
  and DLL compile successfully.
- `powershell -ExecutionPolicy Bypass -File scripts/build-mapgen.ps1`: the
  standalone/exporter executable also compiles with the shared item changes.
- `python -m unittest tools.test_brogue_bridge tools.test_broguedoom_resources tools.mapcompiler.test_compile`:
  70 tests pass. The staff regression repeats six scenarios on each of seeds
  1, 2, 42, 12345, and 99999 and requires identical output, hashes, and RNG counts.
  Fixtures cover damage, obstruction, guaranteed reflection, known/unknown empty
  staffs, and an unknown-range blinking warning. They also check preview purity,
  cancelled warnings, stale revisions, old ABI versions, and invalid targets.
- `powershell -ExecutionPolicy Bypass -File scripts/run-bridge-test.ps1 -Seed 1 -LongRun 300 -VerboseOutput`:
  reaches Brogue's normal death at turn 195; final hash `605cf66657aa5f8e`.
- `cmake --build .build/gzdoom --config Release -j 4 -- /nodeReuse:false`:
  native frontend compiles. This host required a child environment containing
  only one case-insensitive PATH entry and `MSBUILDDISABLENODEREUSE=1`.
- Seed 1 and seed 14 campaigns were prepared and their 40-map packages passed
  topology/integrity verification through `scripts/launch-source-bridge.ps1`.
- `powershell -ExecutionPolicy Bypass -File scripts/test-staff-ui.ps1`:
  the actual GZDoom frontend picks up seed 14's staff at cell 66,6 through 42
  normal actions, opens inventory targeting, cancels, reopens, and fires through
  the same input handlers used by the player. Cancellation retains revision
  43/turn 42; firing reaches revision 44/turn 43. The log and engine framebuffer
  captures are written to ignored `artifacts/staff-ui/`.

`brg_staff_smoke` is a development command, following the existing `brg_actions`
pattern. It waits for the action queue, requires an already-carried staff, and
never creates equipment or changes simulation state outside ordinary commands.
Its copied verification snapshot uses static storage to avoid exhausting the
native engine's stack when the subsequent command enters Brogue's bolt code.

## Remaining boundaries

A generalized interaction/targeting API and 3D bolt animations remain separate
backlog tasks. API v15 extends the device path to [wands](targeted-wand-use.md).
The aiming guide is not a prediction of reflections or
hidden effects. Existing general revision behavior for non-turn-consuming
commands is unchanged. The regression uses controlled headless fixtures plus a
real generated-map frontend run; it does not establish turn-by-turn equivalence
against a separately running standalone Brogue recording. That comparison and
physical keyboard/mouse input verification were not run; the runtime smoke
calls the native input handlers directly and captures actual rendered frames.

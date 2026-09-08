# Held forward movement

Contribution category: presentation/input parity. Brogue CE remains authoritative.

## Source findings

The pinned `src/brogue-mapgen/src/platform/sdl2-platform.c` accepts repeated
SDL key-down events for arrows and repeated text-input events for letter
movement. `pollBrogueEvent()` has no movement-repeat timer or repeat filter.
`IO.c::executeKeystroke()` calls `considerCautiousMode()` and then
`playerMoves(direction)` for unmodified movement. Holding a direction therefore
supplies repeated ordinary moves at the platform keyboard-repeat cadence.

Shift/Ctrl movement instead calls `Movement.c::playerRuns()`. That loop stops
on failed movement, avoided next terrain, disturbance, confusion, and changes
in nearby cardinal passability. Those running rules are separate from holding
an unmodified direction. This change does not add running.

UZDoom's `FKeyboard::PostKeyEvent()` in
`src/common/platform/win32/i_keyboard.cpp` explicitly discards repeated key-down
events. The frontend must therefore track the down/up edges to support a hold.

## Input behavior

Only W repeats. The first available step is immediate; the next waits 500 ms,
then repeats wait 100 ms from the previous bridge call's completion. This is
a fixed frontend input cadence, not an exact copy of OS-configured keyboard
repeat speed. Visible enemy/projectile animations retain their existing input
gate. No missed intervals are accumulated, and held steps are never enqueued
in the discrete-action buffer.

Each attempt reads the current camera octant and submits the existing
`BROGUE_COMMAND_ACTION` through `PerformAction()`, with the newest copied
revision. The bridge's `performCommand()` calls the native `playerMoves()`;
native movement, combat, terrain, hazard confirmation and `playerTurnEnded()`
paths determine the result. Holding against a wall may send further attempts,
but only Brogue decides whether an attempt consumes a turn. The frontend does
not inspect terrain to determine movement legality or predict player position.

Release, another key press, menus/console, focus loss, modal prompts, death,
loading and level teardown cancel the hold. A new W press is required to
resume. A confirmation is never automatically accepted by held movement.
Other movement keys and mouse clicks retain their existing discrete behavior.

`held_movement.h` contains only the input clock and is included in the engine
build fingerprint. `tools.test_held_movement` tests initial delay, duplicate
down events, busy animations, cancellation and slow-frame catch-up prevention.
With `brg_debug`, `brg_forward down|up` supplies W edges through `D_PostEvent`
for runtime verification, retaining focus and modal guards.

## Verification (September 7, 2026)

- `scripts/build-source-bridge.ps1 -SkipTests`: engine and launcher passed.
  The final diagnostic-context addition was rebuilt with the same CMake
  configuration and its engine build fingerprint recorded.
- `scripts/test.ps1`: all 163 tests passed. The 300-action seed-1 endurance
  request ended naturally at turn 195, killed by a rat; not a completed
  300-action survival run.
- `artifacts/held-forward/runtime.py`: actual UZDoom event-queue holds on
  seeds 1, 2, 42, 12345, 99999, with seed 42 on both Vulkan and OpenGL.
  All 115 attempted steps (including 62 blocked attempts) matched headless
  bridge acceptance, turn, coordinate and hash results. Each resulting action
  tape was replayed twice with identical output. Frontend revisions have the
  expected +1 offset for the initial exported-map snapshot.
- Seed 42 produced 24 attempts and turn 9/hash `c910534b97f91845` on both
  renderers. Release and map-open/close intervals produced no further held
  commands. Background-window checks produced zero movement. Captures, logs,
  bridge tapes and the per-seed result table are in `artifacts/held-forward/`.

The runtime probe enters at `D_PostEvent`; physical keyboard hold/release and
mouse turning during a hold remain manual checks. Standalone graphical
side-by-side play and a full release ZIP were not run. Brogue's native
movement implementation was traced directly; the runtime differential is
against the headless bridge, not a separately instrumented standalone build.

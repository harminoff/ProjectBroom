# UZDoom player rollback repair

Category: bridge parity / maintenance. Brogue remains authoritative; simulation
code, command acceptance, turns, RNG and the public ABI are unchanged.

## Expected behavior and reproduction

After an accepted Brogue move, the UZDoom pawn and camera must remain at the
copied Brogue cell, including after UZDoom's prediction/render pass. A minimap
update or accepted-command log alone does not prove that projection succeeded.

The new `scripts/test-player-projection.ps1` sends four north intents on seed 1
through the existing bridge action queue, then observes the pawn at HUD render
time for 35 frames. It does not issue gameplay actions from the render hook.
Before the repair it failed at turn 4: Brogue cell `(38,22)` required world
XY `(2464,416)`, but the pawn was at `(2464,224)`.
Evidence: `artifacts/movement-rollback/reproduction/runtime.log` and its capture.

## Cause and repair

UZDoom 5's `P_PredictClient` backs up the player even in single-player. The next
`P_UnPredictClient` restores that backup after input processing. Our existing
input and `G_BuildTiccmd` hooks had already committed a Brogue action and projected
its coordinates, so rollback restored stale presentation state while Brogue and
the minimap correctly stayed advanced.

The fifth engine integration seam is now `src/playsim/p_user.cpp`:
`P_PredictClient` returns before taking a backup when
`BrogueBridge_OwnsPlayerPosition()` identifies a `BRG` map. Other maps keep normal
UZDoom prediction. Brogue still resolves commands synchronously through the same
bridge entry points. Doom input suppression remains in place. No user setting
or configuration migration is required.

The pinned integration patch and its lockfile hash include this repair. Existing
portable candidates predate it and must be regenerated before distribution.

## Verification

```powershell
powershell -ExecutionPolicy Bypass -File scripts/test-player-projection.ps1 -Renderer Vulkan
powershell -ExecutionPolicy Bypass -File scripts/test-player-projection.ps1 -Renderer OpenGL
```

Post-repair Vulkan and OpenGL both passed: all 35 sampled frames reported
actual XY `(2464,416)`, matching the authoritative cell. Before/after framebuffer
captures show the changed viewpoint. Both runs are under
`artifacts/movement-rollback/fixed-<backend>/`.

All four command acceptance, turn, revision, coordinate and state-hash records
match the failing build exactly (`parity.json`). Staff and wand UI checks passed,
and the complete 111-test suite passed in 66.808 seconds (`tests.log`). The
canonical `.build/uzdoom/Release/uzdoom.exe` was rebuilt and its build receipt
refreshed. The pinned patch validator passed.

Physical-keyboard confirmation remains distinct from the engine action-queue
regression. Portable archives and their corresponding-source builds were not
regenerated for this repair; the old validation archives contain the defect.

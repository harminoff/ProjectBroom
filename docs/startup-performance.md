# New-game startup performance

September 7, 2026. Presentation/tooling optimization; Brogue CE remains the
authority for generation, terrain, turns, and RNG.

Previously both launchers compiled and verified all 40 large addressable maps
before opening UZDoom. Those later maps were redundant: `SyncLevelEvent()`
already calls `PrepareRestoredMap()` to export and compile the live Brogue
depth before changing levels. Native save reconstruction uses the same path.

The new `--startup` compiler/verifier mode retains all 40 MAPINFO entries but
builds and fully verifies only BRG01. Its WAD and MAPINFO are byte-identical to
the full campaign. The ordinary full-campaign and standalone-depth modes remain
available. Startup caches use separate paths, preserving old generated maps.
No Brogue source, gameplay entry point, simulation threading, or RNG changed.

## Measurements

Seed 42, same machine and exporter JSON; subprocess wall time, without the
profiler attached. These are samples, not a multi-machine benchmark.

| Stage | Before | After |
|---|---:|---:|
| Brogue's canonical 40-depth export | 1.47 s | unchanged |
| Python map compilation | 13.28 s | 1.32 s |
| Full verification of prepared maps | 46.94 s | 2.13 s |
| Engine launch to first captured game frame | 3.19 s | 2.86 s |
| Generated package size | 19,413,903 bytes | 491,838 bytes |

Compilation plus verification dropped from 60.22 to 3.45 seconds (about 94%).
Launching the rebuilt `ProjectBroom.exe --seed 42` with a missing seed-42 cache
completed export, compilation, verification, and engine dispatch in 5.67 seconds.
That executable measurement ends at engine dispatch, not the first game frame
or the user's selection in the title menu. The packaged compiler took 2.63 s
to compile and 3.43 s to verify, including its executable extraction/startup,
and produced exactly the same PK3 as Python.

## Verification

- Canonical `scripts/build-source-bridge.ps1 -SkipTests` passed, including the
  launcher. Rebuilt the packaged compiler with the checked-in PyInstaller spec.
- `scripts/test.ps1` passed all 161 tests. Its requested 300-action seed-1 run
  ended naturally at turn 195, killed by a rat; it was not a completed endurance run.
- Startup compile/verify exercised seeds 1, 2, 42, 12345, and 99999. Seed 42's
  first WAD and complete MAPINFO match the pre-change full campaign byte-for-byte.
  Regression coverage also checks repeat determinism, missing depth metadata,
  and preservation of the ordinary full-campaign mode.
- Actual UZDoom new games using full/startup seed-42 packages both ended at
  turn 0, hash `0c342dcf4271326d`.
- Generated a native seed-1 depth-2 save through normal Brogue actions. Loaded
  it using a startup package with no BRG02 WAD, then returned to depth 1 through
  the existing level-change path: final turn 59, hash `01d5814aa9bbc157`.
- Captures, logs, profile data, timing scripts, and JSON measurements are in
  `artifacts/startup-performance/`. The first actual-launcher attempt failed
  because the test process inherited an incompatible PowerShell module path;
  the corrected test environment launched successfully without a project workaround.

Full release-archive assembly and a fresh standalone graphical comparison were
not run. The updated packaged compiler was executed, and the updated launcher
was launched in development mode. Existing shader/model loading costs remain;
later-floor compilation was already performed on entry before this change.

To reproduce the main preparation check against an exported JSON:

```powershell
python tools/mapcompiler/compile.py --input dungeon.json --output startup.pk3 --startup
python tools/mapcompiler/verify.py --input dungeon.json --package startup.pk3 --startup
```

Omit `--startup` from both commands for a full-campaign comparison.

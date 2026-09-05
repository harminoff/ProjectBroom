# Project Broom UZDoom migration

Contribution: maintenance and bridge parity. Brogue CE remains authoritative;
no gameplay outcomes, content, RNG, topology, or public bridge ABI are changed.

## Approved target and baseline

Target UZDoom 5.0.0, commit `292cf4203ebd3ced951cb67f6819180f588c1d44`.
Port first, verify equivalent behavior, then accept only measured performance
improvements. Windows x64, synchronous Brogue DLL, API 15 and compiler 42 remain
the contracts. Historical `gzdoom-bridge`, `BrogueDoom`, and `brg_*` names remain.

The pre-migration project has one initialization commit and predominantly
untracked source. Do not reset/clean it or assume HEAD contains the project.
The preserved 1,072-file source archive, source hashes, engine binaries, bridge
executables and both upstream diffs are in ignored
`artifacts/uzdoom-migration/baseline`. The initial 105-test suite passed.

## Engine change inventory

Both original engine checkouts were GZDoom 4.14.2 at
`99aa489d09015a95bb78df2b30ede29f328cc874`, with the same 15 added lines:

| Upstream file | Purpose | UZDoom adaptation |
| --- | --- | --- |
| src/CMakeLists.txt | Compile external frontend and include copied bridge API | Explicit PROJECT_BROOM_ROOT |
| src/g_game.cpp | Input interception and command suppression | usercmd_t; suppress before caching buttons |
| src/g_statusbar/shared_sbar.cpp | Native HUD hook | Preserve DrawTopStuff ordering |
| src/menu/doommenu.cpp | New Game session cleanup | Shared StartgameConfirmed branch |

The separate native frontend was 3,141 lines. It owns DLL loading, copied-state
projection, stable-ID proxies, targeting, HUD, cosmetic animation and comparison
input. No additional upstream model-loader or renderer patches were found.
UZDoom's SetAnimationNative replaces the old incompatible private declaration;
its tic fraction of 1 preserves the six-clip rat adapter's existing behavior.

## Implementation and acceptance sequence

1. Preserve GZDoom source, binaries, tests and runtime captures for comparison.
2. Pin and patch UZDoom in `.deps/uzdoom-source`; build `.build/uzdoom` with
   VS2022 x64, C++20, Release optimization, Vulkan and USE_UPDATER=OFF.
3. Port hooks and private interfaces without changing Brogue simulation code.
4. Switch all supported launch, test, review, CI and packaging paths. Keep the
   MAP01 utility explicitly inspection-only. No legacy engine fallback.
5. Package matching UZDoom resources, dynamically loaded audio dependencies,
   notices and complete corresponding source. ZMusic is bundled/static.
6. Run source compilation, the complete suite, five-seed deterministic repeated
   traces and 300-action runs; then actual engine, device and comparison tests.
7. Validate an extracted portable package and its corresponding-source build.
8. Benchmark the port before optimizing snapshot reconciliation, item lookup,
   HUD preparation, fullbright-particle lighting and repeat-launch validation.

Performance trials use matching hardware/settings and three repetitions after
warm-up. Record median/p95/p99 frame times, memory, command latency and cold/warm
startup. Accept at least 5% target improvement without a repeatable regression
above 5% elsewhere or lost parity. Preserve full verification on cache changes
or corruption and sequential all-40-depth Brogue generation.

Runtime acceptance includes seeds 1, 2, 42, 12345, 99999; staff seed 14; wand seed
19; repeat New Game, doors/stairs/falls, cancellation, physical input, comparison
focus changes, Vulkan/OpenGL and HUD scales 1-3. Record early authoritative death
honestly. Existing gameplay-parity backlog items are not part of this migration.

Public release remains gated until acceptance evidence is complete. Local
packages are for validation, not automatic publication.

## Sources

- [Release](https://github.com/UZDoom/UZDoom/releases/tag/5.0.0)
- [Pinned build source](https://github.com/UZDoom/UZDoom/blob/5.0.0/CMakeLists.txt)
- [Input](https://github.com/UZDoom/UZDoom/blob/5.0.0/src/g_game.cpp)
- [Animation](https://github.com/UZDoom/UZDoom/blob/5.0.0/src/playsim/p_actionfunctions.cpp)
- [Security advisory](https://github.com/ZDoom/gzdoom/security/advisories/GHSA-prhc-chfw-32jg)

## Movement regression correction

User testing exposed a 3D player rollback defect that the original device tests
did not detect. The current patch adds a fifth seam in `src/playsim/p_user.cpp`
to exclude Brogue maps from client prediction backups. A runtime regression
failed on the old integration and passed after the repair in Vulkan and OpenGL.
See [player projection repair](uzdoom-player-projection-fix.md). Candidates
`0.1.0-uzdoom.1` and `.2` predate this fix; use the rebuilt repository engine
for testing and regenerate packages before distribution.

## Execution evidence

The engine switch and portable packaging are implemented. Acceptance is partial;
the performance stage and public release remain gated. Evidence below was
collected on Windows 11 with an NVIDIA RTX 3080 on 2026-09-05.

| Gate | Result and evidence under `artifacts/uzdoom-migration/` |
| --- | --- |
| Pinned dependency bootstrap | Passed, including repeated patch validation; `bootstrap.log` |
| Custom Release engine | Compiled and linked; `build-dev.log` (launcher restore initially required network access) |
| Self-contained launcher | Built after permitted NuGet restore; `launcher-build.log` |
| Regression suite | 111 tests passed in 66.972 seconds; `tests-final.log` |
| Determinism | Five seeds, short sequence and 300-action request, baseline/port/repeat stdout byte-identical; `determinism/results.json` |
| Device UI | Staff seed 14 and wand seed 19 passed cancellation and one-turn firing; `staff-ui-final.log`, `wand-ui-final.log` |
| Renderer/HUD matrix | Staff check passed Vulkan/OpenGL at scales 1, 2, 3; `port-<backend>-<scale>/` contains logs and captures |
| Missing bridge | Failed closed with the expected diagnostic; `fail-closed/runtime.log` |
| Portable archive | Candidate `0.1.0-uzdoom.2` passed checksums and manifest verification; `verify-package.log` |
| Packaged launcher | Extracted launcher generated and verified all 40 depths for random seed 510742445, then started its packaged UZDoom; `packaged-launcher.log` |
| Packaged device UI | Both staff and wand passed using extracted engine, static PK3 and IWAD; `packaged-staff.log`, `packaged-wand.log` |
| Corresponding source | Fresh VS2022 Release build from candidate source staging succeeded; `source-configure.log`, `source-build.log`; rebuilt engine passed staff UI in `source-rebuilt-staff.log` |
| Interactive input/comparison | Not completed: computer-use app approval timed out |
| Clean Windows VM | Not run; extracted-package validation used the development host |
| Performance | No controlled frame-time/startup trials completed; no performance improvement claimed or speculative runtime optimization enabled |

The long-run harness requests 300 actions but respects authoritative death. Its
final turns and state hashes were:

| Seed | Final turn | State hash |
| --- | ---: | --- |
| 1 | 195 | `605cf66657aa5f8e` |
| 2 | 43 | `4b8100449d7d2a85` |
| 42 | 72 | `8d13a463dae3e192` |
| 12345 | 145 | `93b34275cf604e88` |
| 99999 | 109 | `5c7264608578c3cc` |

The short sequence was `WAIT,N,E,SE,WAIT,W`. Brogue simulation source and ABI
were not changed. The six new regression tests cover pristine/repeated patch
application, preservation of unexpected edits, staged/untracked changes,
modified patch rejection, stale build detection, and complete source packaging.

Additional maintenance fixes discovered during validation:

- Restore PATH after the MinGW build so its Python cannot replace Python 3.11
  for deterministic assets and tests. Normalize Windows native-build environment
  key casing to prevent duplicate `Path`/`PATH` MSBuild errors.
- Copy runtime DLLs only when hashes differ, retaining repeat-launch behavior.
- Preserve `launch-seed -Force` by regenerating through the authoritative launcher.
- Record frontend inputs and engine output hashes; packaging rejects stale builds.
- Include tracked upstream files in corresponding source. The former filter
  incorrectly excluded `buildtexture.cpp`, `buildloader.cpp`, and other required
  build-named source files. Candidate `.1` predates this fix and is superseded.

## Remaining execution handoff

1. Complete keyboard/controller, repeated New Game, doors/stairs/falls,
   six rat animation clips, and standalone comparison/focus checks. Engine-driven
   UI tests do not prove physical device handling or side-by-side parity.
2. Extract the current package on a clean Windows VM; test seed 1 and a random
   seed, warm relaunch, configuration migration, and normal exit. No clean-VM
   claim can be inferred from the development-host tests.
3. Preserve the validated port binary and frame/settings provenance, then run
   the agreed GZDoom/plain-UZDoom/optimized trials. Another legacy GZDoom process
   was already running in the workspace and was left untouched; isolate competing
   workloads before benchmarking.
4. Apply the performance candidates one at a time only after those baselines:
   revision/level-aware proxy reconciliation, stable-ID item lookup, HUD layout
   preparation, fullbright-only particle light exclusion, and shared launch-cache
   receipts with exporter/compiler/registry/verifier/input/package fingerprints.
   Keep player interpolation, visual animation and synchronous commands running
   normally; invalidate on session/map/settings changes. Do not cache gameplay
   decisions or skip topology checks after changes/corruption.
5. Re-run parity/runtime checks for each accepted candidate; discard candidates
   that fail the measurement threshold. Update this evidence and regenerate both
   archives before setting `release.engineMigrationVerified` to true.

Useful reproduction commands:

```powershell
python -m unittest tools.test_engine_source
powershell -ExecutionPolicy Bypass -File scripts/test.ps1
powershell -ExecutionPolicy Bypass -File scripts/test-staff-ui.ps1 -Renderer OpenGL -HudScale 3
powershell -ExecutionPolicy Bypass -File scripts/test-wand-ui.ps1
powershell -ExecutionPolicy Bypass -File scripts/verify-release.ps1 -ReleaseDirectory artifacts/release/0.1.0-uzdoom.2
```

The local validation archives are under `artifacts/release/0.1.0-uzdoom.2`.
They are not a public release. Later handoff/CI documentation edits are in the
workspace; regenerate a candidate after completing the outstanding gates.

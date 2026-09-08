# Native save and load

Project Broom uses Brogue CE's native `.broguesave` suspend/resume format.
UZDoom saves are disabled for Project Broom. Replay controls are outside this
implementation; Brogue's internal recording playback reconstructs saved games.

## Player workflow

Launch `ProjectBroom.exe` to choose Continue, Load/Import, or New Game before
campaign preparation. `--seed` starts a reproducible new game; `--load-save PATH`
imports a native save. The in-game Saves menu provides the same load choices
and Save and Exit. Normal close also saves an active game. Starting another
run offers Save, Abandon, or Cancel. A failed save leaves the game open.

Data lives under `%LOCALAPPDATA%/ProjectBroom`: `saves` contains suspended games,
`working` holds native recordings, and `cache` contains disposable projections.
Imported originals are copied and never deleted. A managed save is consumed
only after Brogue reconstructs it and the frontend synchronizes the destination
map. Cancellation or failure retains the source. Save names are unique; there
is no save-slot editor or replay browser. `--probe-save PATH` checks native
compatibility without launching a game.

## Authority and failure handling

API v18 adds copied persistence requests/status, session generations and
revision checks. `saveGameToPath()` publishes through a sibling temporary file,
flushes it, then atomically replaces the destination before ending the run.
`beginSavedGameLoad()`, `stepSavedGameLoad()` and `finishSavedGameLoad()` are
shared with standalone Brogue. Reconstruction uses native `nextBrogueEvent()`
and `executeEvent()`, at most 32 top-level events per synchronous bridge step.
Nested native prompts still resolve within their event. Intermediate gameplay
snapshots are unavailable. Native version, length and out-of-sync checks reject
incompatible or damaged recordings. WAIT and targeted throws now record their
native input so continuation preserves Brogue's RNG stream.

The active-level exporter reads current Brogue state without generation or RNG.
The existing compiler rebuilds an external WAD while retaining logical BRGnn
map identity, cell addressing and terrain proxies. Initial features synchronize
settled, including remembered door camouflage. Cache hashes include input,
compiler/resources and output integrity; missing or corrupted maps rebuild.
Every depth entry uses this projection. If compilation fails, gameplay input
pauses and the frontend retries while preserving the native run. The compiler
has a bounded timeout. Full unsigned 64-bit seeds pass through the launcher.

## Verification recorded on 2026-09-05

- Canonical bridge, standalone/exporter, source frontend and launcher builds.
- `scripts/test.ps1`: 116 primary tests, 6 engine-source tests and one search
  asset test passed. The eight native-save tests also passed after adding a
  corrupted-cache reconstruction assertion.
- Native round trips cover seeds 1, 2, 42, 12345, 99999 and UINT64_MAX; depth-2
  round trips cover the first five. Recorded actions include movement, WAIT,
  search buildup/completion, throw, equip, remove and drop. Restored player
  state and a subsequent WAIT/RNG continuation match the uninterrupted path.
- Lifecycle tests cover ABI/revision rejection, cancellation, unsuccessful
  publication, Unicode paths, source retention/consumption, repeated resumes,
  bounded loading, corrupt/truncated/version-mismatched streams and native OOS.
- Repeated deterministic sequences and requested 300-action runs on seeds 1,
  2, 42, 12345 and 99999 produced identical output; native death may end a run
  before the requested action count.
- Command-driven UZDoom load/save ran in Vulkan and OpenGL at HUD scales 1–3.
  The turn-3 fixture restored normalized hash `76ea78c8a68a9811` in all six.
  Captures are under `artifacts/save-runtime`; HUD scale 3 retains existing
  footer/message clipping and is not claimed as layout acceptance.
- An extracted release resumed the native depth-2 turn-58 fixture, executed
  WAIT and saved at turn 59 using its packaged compiler. This exposed and fixed
  missing R-key migration when loading with a fresh frontend configuration.
- The final `0.1.0-save-preview3` extracted package passed the native launcher
  probe and restored depth 2 at turn 58 with a fresh configuration. Ordinary N
  movement ascended to depth 1 and saved at turn 59. Loading that save and moving
  N returned to depth 2 and saved at turn 60. Both current maps rebuilt through
  the packaged compiler; captures and logs are in `package-final` and
  `package-return` under the runtime evidence folder. The fresh configuration
  contains `R=brg_search`, and the captured footer displays the binding.

Local logs: `artifacts/save-canonical-build.log`, `save-canonical-tests.log`,
`save-long-runs.log`, `save-package-final.log`, and `save-runtime/`.

## Remaining acceptance

Save/load TODO acceptance boxes remain unchecked. Computer-use app approval
timed out, so physical keyboard/mouse, launcher chooser, rebinding, close-dialog
and focus interactions are not verified by the command-driven runtime checks.
An unmodified standalone application's import/export UI, exhaustive active
status/item/device/confirmation families, and locked-file save-failure UI need
separate comparison evidence. These are verification gaps, not completed gates.
No unrelated targeting, replay or migration acceptance items were changed.

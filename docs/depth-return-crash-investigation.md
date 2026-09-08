# Floor return crash investigation - 2026-09-07

Status: confirmed and fixed after the supplied CrashReport.zip identified the
stale Doom hub-snapshot failure. The earlier investigation below predates that report.

## Confirmed failure and correction

The supplied report used seed 208360664 and a native saved run. On returning to
BRG01, p_saveg.cpp rejected a cached hub snapshot with "Savegame is from a
different level", followed by an access violation in the fatal-error path.
Brogue had already completed the authoritative return successfully.

Generated campaigns are Doom hubs. First visits and native reconstruction use
maps whose geometry/checksum can differ as Brogue terrain or knowledge changes.
Restoring an older Doom snapshot onto the newly compiled WAD is invalid even
when both represent the same Brogue depth. Even when checksums happen to match,
restoring stale actors competes with the complete Brogue snapshot.

The frontend now marks Brogue levels LEVEL2_FORGETSTATE, preventing hub snapshot
creation. Its map override also clears any cached snapshot for the requested
Brogue depth before UZDoom deserializes it. This handles existing campaign PK3s
without forcing regeneration or changing their connectivity, topology or metadata.
No Brogue simulation, native save format, RNG or bridge ABI changes were made.

A 72-command ordinary movement sequence on seed 208360664 reproduced the exact
fatal error on the old executable (queued-before/runtime.log). The new opt-in
regression tools/test_depth_return.py uses that same full queue, avoiding dropped
test inputs during variable-length creature animations. The test returns to depth
1 at absolute turn 72 with hash 6550a30ebb2e5fb8, matching repeated headless bridge
runs. Fixed Vulkan and OpenGL runs passed with captures and normal shutdown.
A copy of the user's latest crash recording also loaded and completed another
1 -> 2 -> 1 trip on Vulkan, ending at turn 333, hash 14d0e58ce27fee5a.

Canonical source/launcher build, engine fingerprint validation and all 166 tests
in scripts/test.ps1 passed. The seed-1 endurance run ended naturally at turn 195
(killed by a rat); it was not a completed 300-action survival scenario.

Reproduce: python -m tools.test_depth_return --backend 1 (or 0). Use --run-label
for a fresh test directory. Requires generated/seed-208360664/startup campaign.
Evidence: artifacts/depth-return/{crash-report,queued-before,fixed-1,fixed-0,fixed-restored}.

## Initial investigation before the crash report

The most recent launcher run used seed 404514297. Its native working recording
and last reconstructed map were copied to isolated evidence. The original recording
was never loaded or consumed. Reconstruction of a disposable copy completed at
absolute turn 362, depth 1, player cell 13,19, hash 63be3db878239b38.
A saved recovery copy is `artifacts/depth-return/recovered-turn362.broguesave`.

The normal bridge action S enters stairs: depth 2 cell 12,16, then S returns to
depth 1. A Vulkan round trip completed at turn 364, hash 24be1dcf64ab7ad7.
Twelve consecutive stair transitions completed on each of OpenGL and Vulkan,
with both ending at turn 374, depth 1, hash 7d65a4076205842c. The Vulkan repeat
used a copy of the user's engine configuration. Tests used isolated save roots,
auto-executed ordinary bridge actions, and the current packaged startup map.
They do not reproduce the preceding 47-minute interactive session or prove that
its crash is fixed. No recent crash dump or fatal-error report was found.

Normal launches previously retained launcher preparation output but not the engine
console. Both launch paths now create a separate log-engine-TIMESTAMP.txt under
LOCALAPPDATA/ProjectBroom/logs. Pinned UZDoom's execLogfile requires a basename,
adds the prefix/suffix itself, and writes relative to working directory. The
engine starts in the log directory with absolute resource/config paths. Actual
engine validation created log-engine-validation.txt and completed another round
trip. Launcher rebuild passed; PowerShell syntax parsing passed. No gameplay,
bridge ABI or asset changes were made for this investigation.

Evidence: artifacts/depth-return/{roundtrip,repeat-opengl,repeat-vulkan,log-validation}.
The subsequently supplied crash report resolved this uncertainty; see the confirmed fix above.

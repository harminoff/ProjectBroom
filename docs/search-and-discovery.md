# Search and physical discovery

Status: implementation and automated parity work are present; acceptance is
incomplete. The two search TODOs remain unchecked until all requested runtime
and packaging acceptance checks pass. This is bridge parity and its associated
presentation, not new gameplay. Brogue CE remains authoritative.

## Controls and Brogue behavior

R searches once; Ctrl+R starts repeated search. Both commands appear in
Customize Controls as `brg_search` and `brg_search_repeat`. S remains backward
movement. Search keys are edge-triggered. Escape cancels repetition; other
gameplay input cancels it before entering the existing input path. Camera motion
does not cancel. Menu, console, lost-focus, death and depth-change paths stop
continuation. The engine's existing WantEscape callback lets cancellation run
before its menu responder. No gameplay thread is introduced.

The development launcher is the repository-root `ProjectBroom.exe`; it runs
`.build/uzdoom/Release/uzdoom.exe` with the live `mod/BrogueDoom` resources.
Existing settings can retain Doom's `R = +reload`, because `defaultbind` does
not override it. A one-time migration replaces that obsolete default only when
Search has no existing binding, preserving custom bindings. The footer displays
the current Search key. A single unsuccessful search need not print a message;
the turn counter advances, and Brogue supplies discovery/completion messages.

`manualSearch()` still records SEARCH_KEY, selects Brogue's ordinary or fifth
search strength, calls `search()` and then `playerTurnEnded()`. `search()` retains
direct-visibility restrictions, awareness adjustment, probabilities and calls to
`discover()`. The fifth-search completion message resets STATUS_SEARCHING to zero
and sets `rogue.disturbed`; a completed sequence does not promise all secrets were
found. Discovery and other Brogue disturbances can stop repetition earlier.

Standalone `executeKeystroke()` and the bridge share `beginRepeatedSearch()`,
`stepRepeatedSearch()` and `finishRepeatedSearch()`. Start performs the first
action; Continue performs exactly one more action. UZDoom schedules each next
call 80 ms after the preceding call finishes, without catch-up actions. The
Searching progress/maximum/active fields come from Brogue. Reveal duration does
not gate search or input.

## API v17 and knowledge

v17 appends SEARCH and SEARCH_START/CONTINUE/CANCEL without changing earlier
command values. Search control commands bypass the carried-item validator.
Old ABI and stale-revision requests are rejected. Continue and Cancel require
an active sequence. Cancellation changes revision and control state, using the
complete copied snapshot without recapturing appearances or consuming even
cosmetic RNG. Search progress, maximum and active state enter normalized hashing.

`BrogueBridgeCellState.terrainFeature` describes physical wall, door, plate,
vent, hole or lever appearance. It is derived from Brogue's highest-priority
visible terrain or its remembered terrain. Secret entries resolve to ordinary
wall or floor. Hidden current layers must not be used to override this field.
Gas trap identities share hardware; Brogue's Look text and minimap retain the
identity. Look cycling reads known door appearance, not raw secret-door flags.

Native door and feature projections reconcile full snapshots at session/depth/
cell coordinates; event delivery is not required for correctness. Initial sync
and remembered features are settled. Changed features supersede unfinished
effects, including actor removal and floor restoration. Runtime geometry is
addressed, not regenerated.

Compiler v43 adds secret-door two-sided camouflage, wall-material aliases and
line IDs `20000 + y*79 + x` with `user_brogue_reveal_cell`. Existing doorway
sectors and Brogue metadata remain. TRAP_DOOR is included in hole classification.
Discovered trapdoor sectors use the bounded -128 recess, BRGVOID floor and
BRGCLIFF adjoining faces. Floor covers dissolve above that recess.

Development cache checks require compiler 43. Packaged launches use a separate
`ProjectBroom-v43-seed-N.pk3` cache name, leaving older cache files untouched.

## Assets and material

`tools/search_models/generate.py` produces original deterministic pressure
plates, nozzles, drains, vents, net/linkage details, levers, rims and a floor
cover. Source geometry is Z-up and explicitly converted to UZDoom's Y-up OBJ
convention. The original gray-brown iron texture and meshes use
[the project's asset license](../ASSETS-LICENSE.md), CC BY-SA 4.0. Camouflage
reuses the existing original rock/stone palette. No third-party assets were
imported and no upstream notices were removed.

The dedicated material shader uses fixed spatial noise with feathered opacity.
Reveals last 21 engine tics; Basic settles immediately, Enhanced and Cinematic
use the same fade. Mechanism actors have NOINTERACTION, NOBLOCKMAP and NOGRAVITY;
they contain no AI, damage, collision decisions, gameplay RNG or turn code.
Settled actors use normal opaque rendering. Temporary floor covers are removed.

## Verification and remaining acceptance

Automated checks include 21 differential scenarios on seeds 1, 2, 42, 12345 and
99999, compared twice for repeatability. They cover all 13 secret catalog
entries, single/repeated search, fifth completion, partial buildup, awareness,
empty searches, cancellation, passive discovery and discovery interruption.
Each differential route compares the subsequent WAIT state/hash, turns, search
progress and substantive RNG continuation. Additional fixtures exercise old ABI,
stale revisions, invalid control requests, event truncation, remembered terrain
and session reset. These do not constitute complete recording-byte parity or
every visibility/depth-revisit case requested in the specification.

Commands and local evidence:

- `scripts/build-source-bridge.ps1`: native frontend, bridge and launcher build.
- `scripts/build-search-standalone.ps1`: SDL build from the modified Brogue source;
  the exporter binary is restored afterward. SDL process launch was checked,
  but interactive standalone comparison is still open.
- `scripts/test.ps1`: final run passed 108 regression tests, 6 engine tests and
  the asset repeatability/orientation test (115 total).
- `scripts/run-bridge-test.ps1 -Seed N -Actions "WAIT,N,E,SE,WAIT,W"` and
  `-Actions "SEARCH,SEARCH,SEARCH,SEARCH,SEARCH,WAIT"`; repeatability evidence is
  under `artifacts/search-determinism/`.
- `--long-run 300` was repeated on the same five seeds. Brogue ended these runs
  in death at turns 195, 43, 72, 145 and 109 respectively; they are not 300-turn
  survival proofs.
- `scripts/test-search-material.ps1 -Renderer Vulkan|OpenGL -HudScale 1|2|3`
  captures material states. Screenshots must be taken after a rendered frame
  reflects the new alpha; the harness now delays capture by two tics. Earlier
  captures were superseded after finding an OBJ-axis and capture-timing defect.
- Final material captures completed on Vulkan and OpenGL at HUD scales 1–3 in
  `artifacts/search-material-final-*`. Settled plate captures were inspected on
  both backends. These are a material smoke test, not all-family acceptance.
- The subsequent saved-binding repair was rebuilt and checked with a legacy
  `R = +reload` fixture: runtime migration logged and the Search footer was
  captured in `artifacts/search-binding-material-Vulkan-1`. The bridge/resource
  regression run passed 48 tests, including generalized targeting on five seeds.
  The earlier preview ZIP predates this binding/footer repair.
- `scripts/package-release.ps1 -Version 0.0.0-search-preview -SkipBuild` passed
  release verification. The extracted runtime launched its own packaged engine
  and generated the v43 seed-1 cache while preserving the old cache byte-for-byte.
  `artifacts/search-package-launch.json` records paths and hashes. This proves
  package startup/cache migration, not interactive gameplay acceptance.

Still required before marking search complete: inspect all final physical
families and camouflage seams/contours in actual discovery scenes on both
backends; verify floor-cover alignment and adjoining-hole cases; exercise
physical keyboard/mouse cancellation, rebinding and focus/menu transitions;
compare standalone visually; traverse discovered doors and holes in ordinary
gameplay; measure frame timing with reveals enabled/disabled. Material smoke
captures alone do not satisfy those gates. Unrelated targeting and general
terrain-migration acceptance items remain unchanged.

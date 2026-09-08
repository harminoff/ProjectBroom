# Dynamic terrain synchronization: geometry foundation

Status: **partial implementation; the dynamic-terrain backlog remains open.**
The settled snapshot reconciler and ABI v20 appearance contract are implemented.
The original geometry probe remains a separate synthetic renderer test.
Compiler version 44 now emits addressable campaign maps. Rich animations and
full terrain-family runtime/parity acceptance remain open.

## Implemented foundation

`make_map_text(..., addressable=True)` emits every one of the 79x29 Brogue
cells, including initially solid cells, with primary tags `10000 + y*79 + x`.
The original traversable-cell material layout and contour selection remain
the reference. A solid neighbor references the reverse of the same contoured
edge, so the newly addressable sector does not introduce a second boundary.
Internal boundaries are permanently two-sided; map perimeter edges remain
one-sided. Startup sectors have positive height for node generation.

Each cell has two detached control sectors, tagged `30000 + cell` for liquid
and `40000 + cell` for deck. `user_brogue_role` is 0 for primary, 1 for liquid,
and 2 for deck; controls carry `user_brogue_owner`, not primary coordinates.
The runtime ZScript validator skips known control roles and rejects unknown
roles instead of interpreting controls as duplicate primary cells.

The pinned engine's `MapLoader::Set3DFloor` initializes type 3 floors with
argument flags 2049 (no shading, no damage transfer), alpha 255, and neither
solidity nor swimming. Their initial floor/ceiling are -520/-512. Rendering
flags remain enabled while the planes are hidden below the bed, allowing the
renderer to allocate its geometry during map load.

`brogue_terrain_geometry_fixture.inc` supplies an explicit developer command,
`brg_terrain_geometry_fixture`. It validates cell-center sector lookup and two
non-solid/non-swimming floors per cell, then changes existing sector and
control planes using `ChangeHeight`, `SetPlaneTexZ`, `SetTexture`, and
`P_RecalculateAttached3DFloors`. It does not use Doom movers or change Brogue
terrain. Settled entity support is held separately from the bed and control
planes. Player, item and creature projection runs after each fixture change.

The fixture exercises closed wall, passage, closed wall, passage, raised
water, a separate placeholder ice/deck plane, bridge over a recess, chasm,
and restored floor. The ice and bridge use existing ground material: these
are plane-existence probes, not approved ice/bridge artwork or animations.
The ice probe deliberately raises support to 8.1 to distinguish projection
from the bed; this is not a production height rule.

## Reproduction and evidence

From the repository root:

```powershell
python -m unittest tools.mapcompiler.test_terrain_geometry
python -m tools.test_terrain_renderer --backend 0
python -m tools.test_terrain_renderer --backend 1
```

The renderer tool requires the existing seed-one export and resource package
under `generated/seed-1`, plus the source-built engine. It creates isolated
config, screenshots, working recordings and saves under its artifact directory.
It exits the engine after the final phase. Backend 0 is OpenGL; 1 is Vulkan.

Both backends were actually selected on an NVIDIA GeForce RTX 3080. Both
reported `bindings=2291`, completed nine stages, and returned a fresh bridge
snapshot with unchanged gameplay hash `c92268ff6250781b`, turn 0, revision 2.
These checks establish no authoritative mutation during this fixture; they
do not establish substantive RNG continuation across gameplay commands.

Artifacts (local, not source assets):

- `artifacts/terrain-foundation/opengl/process.log` and `terrain-00.png` through
  `terrain-08.png`.
- `artifacts/terrain-foundation/vulkan/process.log` and the matching nine captures.
- Each backend's `compiler.json` records geometry counts and verification.
- `artifacts/terrain-engine-build.log` records the source engine build.
- `artifacts/terrain-complete-tests.log` records `scripts/test.ps1` passing.
  The requested 300-action smoke ended naturally at turn 195, killed by a rat;
  it is not a completed 300-action endurance scenario.
- `artifacts/terrain-focused-tests.log` records 61 compiler/resource tests passing.
- `artifacts/terrain-additional-tests.log` records 11 geometry/provenance tests
  passing, including deliberate corruptions of ownership and collision flags.
- `artifacts/terrain-canonical-build-final.log` records the successful canonical
  build with `-SkipTests`; the complete test script was run separately above.
  Earlier `terrain-canonical-build.log` is a failed environment-normalization
  attempt and must not be used as build-success evidence.

The first canonical build reached the launcher and failed on restricted NuGet
access. The dependency restore was subsequently completed. MSBuild also needed
its child environment normalized to one `Path` spelling and node reuse disabled;
no repository build system replacement was made.
The final canonical build needed network access for NuGet signature validation
and then produced both `uzdoom.exe` and `ProjectBroom.exe`. This proves build
and launcher generation, not a packaged gameplay or restored-run launch.

## Settled snapshot implementation

`BridgeTerrainAppearance.inc` copies a 28-byte frontend-neutral appearance record
into each 112-byte cell. ABI v20 leaves v19 reserved for the interaction migration.
Raw terrain and legacy `terrainFeature` remain available separately. Visible
layers come from the pinned catalog, concealed forms are sanitized, memory uses
Brogue's remembered terrain/flags, and unknown cells are opaque. Gas volume is
never used as water depth. Appearance contributes only to presentation hashing.

`terrain_reconciler.h` validates identity, dimensions and row-major coordinates
before comparing all 2,291 cells. It rejects stale revisions, accepts skipped
revisions and new sessions, and treats duplicates as no-ops. Events are absent
from this correctness path. Native rendering commits existing planes and shared
boundaries before committing copied appearance and reconciling owned models.
Player, item and creature support uses the settled target height independently
of liquid/deck planes. A pre-render engine hook binds the initial scene, and
level teardown clears pointers before reconstruction.

`assets/terrain/terrain_presentation.json` covers every pinned symbol with an
explicit existing material/model or documented visual alias. The compiler and
generated native table consume it. No new third-party assets were imported.
Independent owners allow sustained fire, gas, liquid and structural presentation
to coexist. Gas particles read copied catalog color and volume-derived alpha.
Safe `CHASM_EDGE` and `MACHINE_CHASM_EDGE` cells retain ordinary supporting cave
ground; only appearance records carrying Brogue's authoritative auto-descent
hole flag receive the black void floor and lowered bed. The HUD likewise labels
those safe cells as `Chasm edge`, reserving `Chasm` for the actual drop.

Narrow observation hooks in `Time.c` report visible, non-concealed pressure-plate
and promotion activity through bounded `TERRAIN_ACTIVATED` events (amount 1 for
plate, 2 for promotion). They do not invoke simulation or consume randomness.
The cell comparison includes pressure-plate depression without including FOV.

The new focused tests cover ABI sizes/offset, registry coverage and repeatable
output, duplicate/stale/skipped snapshots, malformed coordinates, session/depth
rebinding, secrecy, memory, mapping, flood beds and simultaneous ice/fire/gas.
The harness repeats seeds 1, 2, 42, 12345 and 99999 twice. Four synthetic scenarios
compare bridge dispatch with native `playerMoves()`/`playerTurnEnded()` and
`discover()`, checking state hash, turns and a substantive RNG continuation.
These are direct native-path comparisons, not independent standalone recordings
or comprehensive machine/terrain-family parity. Both observers settle Brogue's
`STABLE_MEMORY` flags before comparing raw hashes.

Current-turn evidence is under `artifacts/terrain-sync/`. Reproduction:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build-source-bridge.ps1 -SkipTests
powershell -ExecutionPolicy Bypass -File scripts/test.ps1
python -m tools.test_terrain_renderer --backend 0 --settled
python -m tools.test_terrain_renderer --backend 1 --settled
```

The settled probe submits `N,N,N`, twenty `W` actions and `S` on seed 1. It checks
that the player immediately matches copied coordinates/support after every
command and that the door at 18,24 loses its panel after Brogue opens it.
The geometry probe remains necessary for wall/flood/ice/deck/recess reversal.
Neither probe by itself proves the full acceptance matrix.

## Verification recorded on 2026-09-06

- `artifacts/terrain-sync/canonical-build-final.log`: canonical source bridge,
  modified UZDoom and self-contained launcher build passed. NuGet required
  network access. `canonical-build.log` is a restricted-network failure and
  must not be used as the successful final build record.
- `artifacts/terrain-sync/complete-tests.log`: `scripts/test.ps1` passed all
  133 tests across its suites. Its requested 300-action smoke ended naturally
  at turn 195, killed by a rat; this is not completed endurance acceptance.
- `artifacts/terrain-sync/final-geometry-tests.log`: 31 compiler/geometry tests
  passed after adding independent cardinal-adjacency verification.
- `artifacts/terrain-sync/final-focused.log`: four focused tests passed,
  including used-plate state, ABI layout, catalog actor existence, repeated
  five-seed direct native-path comparisons and the ABI v20 golden output.
- Final OpenGL and Vulkan settled probes each completed 24 accepted Brogue
  actions, revision 26, hash `56a4ff191789904e`, with no obsolete door panel.
  Their `process.log`, `terrain-initial.png`, `terrain-door-before.png` and
  `terrain-door-after.png` are in the respective `artifacts/terrain-sync/`
  backend folders. The before/after views were visually inspected.
- Both geometry probes in `artifacts/terrain-foundation/` completed all nine
  reversible stages with 2,291 bindings. The pawn immediately reached -128
  for chasm and returned to 0 for restored ground. The fixture leaves Brogue
  at turn 0, revision 2, hash `c92268ff6250781b` throughout.

`brg_terrain_cell x y` reports desired/applied revisions, knowledge/flags,
settled layers, bed/ceiling/liquid/deck heights, support, internal blockers,
owner presence and the selected ground material. This command only reads state.

These results establish the settled foundation and a real door action path.
They do not establish the full animation or packaged/restored-game gates below.

## Remaining implementation and acceptance

No terrain backlog boxes are checked yet. Remaining gates include:

1. Full before/during/after captures for actual Brogue-driven wall, bridge,
   flood, ice, fire, gas, trap and multi-cell machine changes; item and creature
   placement must be inspected as well as the player's position.
2. [Retargetable 12/21-tic animations](terrain-animation-research.md) now include
   discovery reveal, observed activation pulses, original physical forms and
   readable Basic effects. Full Brogue-driven catalog/runtime acceptance
   remains open.
3. Rich physical forms currently represented by documented visual aliases;
   full visible/memory/mapping behavior across every catalog promotion.
4. Multi-depth revisits and falls through the new geometry, interactive
   launcher/restore flows and independent standalone side-by-side comparisons.
   The animation pass verifies an extracted package restoring depth 1 on both
   renderers with complete terrain bindings and native-reference continuation.
5. Fixed-scene frame timing and terrain update cost at all effects settings,
   including dense gas/fire and large machines. Full-size addressable geometry
   reserves 6,873 sectors and needs a measured performance budget.
6. The complete several-hundred-action differential matrix, rejected/cancelled
   terrain interactions, transient activation evidence, and multi-family
   recovery tests. Natural early deaths must be recorded separately.

Contribution categories: bridge parity and presentation. Brogue CE remains the
sole gameplay authority. No animation state enters native save data.

Bloodwort now has original models, snapshot ownership, growth/burst/spore
presentation and dedicated native/renderer/package checks. See
[bloodwort evidence and remaining acceptance](bloodwort-presentation.md).
This does not close unrelated dynamic-terrain backlog items.

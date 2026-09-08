# Terrain animation implementation notes

Scope: presentation only. Brogue's returned geometry and entity support take
effect immediately. No mover, collision query, physics, turn, or Brogue RNG
participates in animation. Initial attachment and newly observed cells settle.

## Research and selected APIs

Context7's `/zdoom/gzdoom` documentation identifies native actor placement,
translucent render styles and plane properties. It does not document the
complete native renderer update sequence, so the pinned UZDoom source is the
implementation authority:

- [Plane and texture height](https://github.com/UZDoom/UZDoom/blob/292cf4203ebd3ced951cb67f6819180f588c1d44/src/gamedata/r_defs.h):
  `ChangeHeight` changes the plane equation; `SetPlaneTexZ(..., true)` also
  dirties renderer vertices and checks plane overlap.
- [Attached 3D floors](https://github.com/UZDoom/UZDoom/blob/292cf4203ebd3ced951cb67f6819180f588c1d44/src/playsim/p_3dfloors.cpp):
  `P_RecalculateAttached3DFloors` rebuilds attached target floor/light lists.
  Recalculation can reorder floors; never cache a floor-list position.
- [F3DFloor](https://github.com/UZDoom/UZDoom/blob/292cf4203ebd3ced951cb67f6819180f588c1d44/src/playsim/p_3dfloors.h):
  find the reserved floor by its control-sector `model`; alpha and
  `FF_TRANSLUCENT` belong to that floor. Preserve render and non-solid flags.
- [Actors](https://github.com/UZDoom/UZDoom/blob/292cf4203ebd3ced951cb67f6819180f588c1d44/src/playsim/actor.h):
  cosmetic models can use origin, scale, angles and translucent alpha. Original
  fragment actors use `NOINTERACTION`, `NOBLOCKMAP`, `NOGRAVITY` and no actions.

The design uses independently retargetable scalar curves evaluated from the
current pose: 12 tics for mechanisms/density, 21 for transformations/discovery.
Transient outgoing models have bounded ownership and are discarded on a new
replacement. The new gas, fire and fragment models use coordinate-derived layouts and analytical motion; they call no RNG at all. Legacy ambient particle streams remain separate.
Basic settles immediately; Enhanced/Cinematic differ in bounded fragment count.
Loss of visibility destroys transient fragments and stops emission immediately.

Expected proof: timeline retarget/settle tests, repeated asset hashes, complete
regressions, real door actions while a panel animates, and synthetic before/
during/after family captures on both renderers. Synthetic snapshots prove
presentation, not standalone terrain gameplay parity. Record these separately.

## Renderer and lifetime details verified during implementation

Animation sampling uses the last applied visual time, rather than assuming that
all engine tics receive a frontend update. Screenshot stalls exposed a missed
endpoint: the curve reached one but the actual 3D floor retained alpha 66/255
and height -5.93. The final sample now commits even after skipped tics; native
probes assert the deck height as well as the timeline endpoint. Plane alpha and
translucency flags are set before attached-floor recalculation, so generated
clipped floors inherit the new appearance.

Every primary cell keeps separate liquid/deck controls. Plane equations,
texture Z, texture references, alpha and attached floor lists update together.
The settled support used by player, creature and item projection never reads a
cosmetic curve. No Doom movers or gameplay specials are introduced.

A removed panel becomes a bounded outgoing owner and rises/fades over 12 tics.
A reversed promotion reuses that panel and samples its current pose. Stone,
wood and ice fragments use analytical paths and expire after 21 tics; a fire
removal immediately removes sustained flames and permits 12-tic ember models.
There are at most 256 fragments globally (6 per changed cell in Enhanced, 12
in Cinematic). Basic keeps static, readable gas/fire and physical mechanisms.
All transient owners are removed on loss of visibility and level teardown.
Gas color and density have independent 12-tic curves and coexist with flames.
Lever angles and pressure-plate depression follow copied state; bounded observed
activation events only add a pulse. Repeated revisions do not restart curves.

Original assets and provenance: [ANIMATION-LICENSE.md](../assets/terrain/ANIMATION-LICENSE.md).
The generator creates wood/stone/ice fragments, a camouflage veil, cage/gate
forms and gas/fire models, plus frost/flame/cloud textures. Registry motion
flags and terrain identifiers are generated into the native lookup from the
same registry used by the Python compiler. Compiler version 45 invalidates
cached maps that predate the frost material.

Two startup failures were corrected: `terrain.zs` is a reserved TERRAIN lump
name (the file is now `brogue_terrain.zs`), and the ZScript spelling `Stencil`
selects the native translucent-stencil style used for colored clouds. Clearing
all expanded cell bindings individually also avoids a Windows stack overflow
from a large aggregate temporary.

## Reproduction

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build-source-bridge.ps1 -SkipTests
powershell -ExecutionPolicy Bypass -File scripts/test.ps1
python -m tools.test_terrain_renderer --animations --backend 0 --quality 1
python -m tools.test_terrain_renderer --animations --backend 1 --quality 1
python -m tools.test_terrain_renderer --input --backend 0
python -m tools.test_terrain_renderer --input --backend 1
python -m tools.test_terrain_renderer --benchmark --backend 0 --quality 1
```

Repeat the matrix/benchmark at quality 0 (Basic), 1 (Enhanced), 2 (Cinematic),
with backend 0 (OpenGL) and 1 (Vulkan). Each matrix produces 69 before/during/
after captures for 23 stages: wall/reveal/door, bridge/falling/chasm/restoration,
flood/retarget/ice/melt/water, simultaneous gas/fire/deck, dissipating gas,
plate/lever/cage, vegetation/fire, and visibility loss. These are deliberately
synthetic copied snapshots on a full-size addressable map, with skipped
revisions and absent events. They must leave the native Brogue hash unchanged.
The separate input probe uses real Brogue moves to open the seed-1 door at
18,24 and submits WAIT while its panel is in flight.

Screenshot matrix frame timings explicitly include capture overhead and are
not performance evidence. `--benchmark` writes no screenshots and holds the
same dense gas/fire scene for six seconds, reporting that interval separately
from the full transition sequence. All runs use isolated configs and save roots
under `artifacts/terrain-animation`.

## Acceptance limits

This implements the cosmetic timeline and representative physical forms, not
completion of the entire dynamic-terrain backlog. Native scenario coverage for
every catalog promotion, pressure-plate event timing, actual wall/bridge/flood
machines, creature/item positioning through those actions, multi-depth restored runs, and standalone side-by-side comparisons remain
separate acceptance gates.
Some catalog forms still use documented visual aliases. Floods currently change
cell surfaces and bank materials; continuous shoreline meshes and waterfall
transition detail are not claimed. The frost surface grows/fades with fragments;
it does not yet have a spreading crack shader. Benchmarks are one fixed machine
and scene, not a supported-hardware performance budget.

## Recorded evidence, 2026-09-06

- Canonical source build: `artifacts/terrain-animation/source-build.log`.
  The network-restricted launcher restore first failed at NuGet; rerunning the
  authorized canonical build with dependency access completed successfully.
- Complete suite: `artifacts/terrain-animation/complete-tests.log`; the new
  launcher ABI drift check is also isolated in `launcher-contract-test.log`.
  The requested 300-action seed-1 smoke ended naturally at turn 195, killed by
  a rat, hash `36b2a00b6543c40a`; this is not completed endurance evidence.
- All six 23-stage matrices passed: 414 full-resolution captures, no remaining
  fragment owners, native Brogue unchanged at turn 0/hash `c92268ff6250781b`.
  Native plane diagnostics confirm final heights and alphas, in addition to
  inspected captures. See `artifacts/terrain-animation/gallery.html` and the
  OpenGL/Vulkan inspection sheets. Existing minimap/menu warnings remain;
  the bridge patch lookup was corrected to its full graphics path.
- Both real door-input probes accepted WAIT while the outgoing panel remained
  active, reaching turn 25/hash `bed89d3579ee76b5`, then removed the panel.
- Original model/texture generation is byte-identical on repeated generation;
  geometry, registry, ABI, save, interaction and map regressions passed.
- Packaging exposed the launcher save consumer's old ABI v18 constant. It now
  requests v20, with a test against the public header. Both development and
  packaged map cache names now select compiler v45.

Screenshot-free measurements on NVIDIA GeForce RTX 3080, 3440x1440, fixed
seed-1 camera, twelve cells of coexisting gas/fire. These are wall-clock
intervals between native frame hooks, not isolated GPU timestamp measurements.
The six-second dense interval is separate from the transition sequence.

| Renderer | Effects | Dense frame mean / p95 ms | Update mean / p95 ms |
|---|---|---:|---:|
| opengl | Basic | 2.636 / 3.370 | 0.442 / 0.442 |
| opengl | Enhanced | 2.688 / 3.356 | 0.481 / 0.616 |
| opengl | Cinematic | 2.667 / 3.317 | 0.493 / 0.578 |
| vulkan | Basic | 2.006 / 2.221 | 0.440 / 0.311 |
| vulkan | Enhanced | 2.006 / 2.200 | 0.472 / 0.415 |
| vulkan | Cinematic | 2.008 / 2.195 | 0.480 / 0.539 |

Raw counts, maxima and sequence frame measurements are in
`artifacts/terrain-animation/timings.json`. Update samples include initial
binding plus 12-cell transitions; they do not prove a full-level machine's
worst-case cost. Cinematic adds fragment detail during transformations, so its
settled dense interval should be similar to Enhanced. These measurements are
local evidence, not a cross-hardware acceptance budget.

### Restored-map integration corrections

The packaged acceptance pass required three existing integration seams to be
updated: launcher save requests now use ABI v20, the frozen compiler includes
the terrain registry and pinned symbol catalog, and runtime reconstruction
selects the addressable projection (projection cache version 3). The save test
now counts all 6,873 restored sectors and checks all three tag ranges.

The pinned engine's [actual level loader](https://github.com/UZDoom/UZDoom/blob/292cf4203ebd3ced951cb67f6819180f588c1d44/src/p_setup.cpp)
calls `P_OpenMapData(..., true)`. In this API `justcheck` controls diagnostic
behavior; it does not mean the call is unused for loading. The previous override
hook skipped that call and silently displayed the original campaign map. The
hook now applies the restored-map override for both values. The integration
patch and its locked digest are updated together.

The native headless control in `artifacts/terrain-animation/native-control.log`
loads the door-route save at turn 25/hash `870f82bbaac11c56` and executes WAIT to
turn 26/hash `917196a3fb138c86`. Both renderer restore runs match those reference
hashes. The raw pre-save hash differs from the raw loaded hash even in that
headless control; this pass does not claim raw save/load hash identity or resolve
that broader normalization gap. Existing native round-trip tests separately
check player state and substantive RNG continuation.

Final local package: `artifacts/release/0.1.0-terrain-preview5/`, with build and
archive verification in `artifacts/terrain-animation/package-verified.log`.
The extracted engine, static resources and frozen compiler restored the native
run on both OpenGL and Vulkan, committed 2,291 cells before exposing the scene,
accepted WAIT and saved at turn 26. Logs and captures are in
`artifacts/terrain-animation/packaged/{0,1}`. The launcher executable's save
probe was exercised; its interactive chooser was not automated. The final
complete `scripts/test.ps1` run passed 136 tests. No backlog boxes are checked.

Bloodwort now has original models, snapshot ownership, growth/burst/spore
presentation and dedicated native/renderer/package checks. See
[bloodwort evidence and remaining acceptance](bloodwort-presentation.md).
This does not close unrelated dynamic-terrain backlog items.

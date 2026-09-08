# Wall torches

Brogue CE already contains `TORCH_WALL`, described in the pinned `Globals.c`
as "a wall-mounted torch" anchored to the wall. Haunted dormant and transitioning
forms retain that ordinary appearance. Only `HAUNTED_TORCH` has the dim purple
flame. These are obstructing terrain, not `T_IS_FIRE` hazards.

The existing copied terrain appearance exports these identities in `structure`.
No ABI extension, simulation hook, turn processing or RNG change is needed.
Knowledge remains controlled by `BridgeTerrainAppearance.inc`. Models consume
the copied appearance, never hidden raw terrain.

`tools/torch_models.py` generates original CC0 iron wall plates, brackets, wooden
shafts, baskets and shaded texture atlases. Crossed transparent flame sheets
have separate warm and purple textures. All mesh faces are triangles or quads.
Generation is deterministic and integrated into `tools/terrain_assets.py`.

The native reconciler mounts each torch on a real shared boundary polygon,
including contoured walls. It chooses the longest exposed known boundary with a
stable coordinate tie-break, places the plate one unit outside the wall, and
points the bracket into the neighboring sector.
Flame height accounts for UZDoom's OBJ pixel-stretch compensation, keeping its
base seated in the basket rather than floating above the model.
Closed wall geometry and Brogue-derived blockers remain intact. With no known exposed boundary, no model
is spawned. Only one face is furnished per torch cell.

The flame is independently owned and visibility-gated. Remembered torches keep
their physical model; unknown cells have neither model nor flame. Replacements
remove obsolete models and flames immediately. Repeated snapshots do not restart
anything. Enhanced and Cinematic add deterministic flame-scale flicker; Basic
retains the flame at a fixed scale. Small non-shadowcasting attached lights use
the existing renderer's cosmetic flicker. No light reveals Brogue map knowledge.
Actors have no interaction, collision, damage, AI or gameplay actions.

Verification commands:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build-source-bridge.ps1 -SkipTests
python -m unittest tools.test_terrain_animation tools.test_broguedoom_resources tools.mapcompiler.test_terrain_geometry
python -m tools.test_terrain_renderer --backend 1 --torches --quality 1 --run-label attached
python -m tools.test_terrain_renderer --backend 0 --torches --quality 1 --run-label attached
```

The explicit presentation fixture covers ordinary, dormant, transitioning,
haunted, remembered, unknown, replaced wall and restored floor states. It checks
flame class, ownership cleanup, wall closure, placement outside the wall sector,
duplicate snapshots and unchanged native turn/hash. These fixtures are renderer
evidence, not a natural gameplay or standalone parity comparison. Captures and
logs are under `artifacts/torches/`. Frame measurements include screenshot
overhead and are not a controlled performance benchmark. Release ZIP packaging
and manual walkthrough remain separate gates.

Verified 2026-09-07: canonical source/launcher build passed, followed by a native
rebuild for the corrected attachment. Engine fingerprint validation passed.
All 165 tests in `scripts/test.ps1` passed; the requested 300-action seed-1 run
ended naturally at turn 195, killed by a rat. The targeted asset/resource/map
suite passed 40 tests, including byte-identical regeneration. Vulkan and OpenGL
Enhanced fixtures passed eight torch states with native turn 0 and hash
`c92268ff6250781b` unchanged. Vulkan Basic and Cinematic also passed. Corrected visual evidence
uses the `attached` directories; earlier `first` and `final` captures predate
the pixel-stretch fix. The debug report's `stages=37` is the exclusive stage
index, not a count of torch cases.

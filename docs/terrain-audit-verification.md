# Terrain catalog correction verification

The complete before/after catalog is in [terrain-description-audit.md](terrain-description-audit.md).
It compares all 215 pinned identities; 91 bindings changed. New models and
materials are authored by `tools/terrain_catalog_assets.py`, invoked from the
canonical terrain generator. License: `assets/terrain/CATALOG-LICENSE.md`.

The existing wood bridge material was already correct. The runtime primary
floor could still use earth at the same height as its deck. Both settled
terrain and shoreline refresh now select the deck material for a flush
bridge/ice primary surface. Hole and liquid beds remain separate; support
heights and Brogue movement remain unchanged. Rope supports are inert props.

The only copied-identity correction is in `appearanceTile`: dormant hidden
bridge stays CHASM, whereas CHASM_WITH_HIDDEN_BRIDGE_ACTIVE projects as
STONE_BRIDGE, matching the visible catalog description. The headless terrain
smoke covers active, dormant, and remembered forms. No Brogue rule or public
ABI was changed.

Passed gates:

- `scripts/build-bridge.ps1` and native Release `cmake --build .build/uzdoom --config Release -j 4` through `tools/run_native.py`.
- 97 tests: `tools.test_terrain_catalog`, `tools.test_terrain_sync`, `tools.test_broguedoom_resources`, `tools.mapcompiler.test_compile`, `tools.test_brogue_bridge`, `tools.mapcompiler.test_terrain_geometry`, `tools.test_terrain_animation`, and `tools.test_shoreline`.
- Terrain smoke repeats seeds 1, 2, 42, 12345, and 99999, compares native/bridge outcomes and RNG continuations, and checks knowledge-safe appearance.
- Terrain generator runs twice with byte-identical output, including nested catalog models and new textures.
- Identical seed-1 map compilation and full addressable geometry verification in `artifacts/terrain-audit/render/geometry.json`.
- Actual Vulkan and OpenGL launches and 15 gallery cases per backend. `brg_catalog_tile` uses copied renderer state and verifies Brogue state hash/turn are unchanged. Captures and logs are in `artifacts/terrain-audit/render/`.
- A requested 300-action headless long run terminates normally on death at turn 195, with final state hash `36b2a00b6543c40a`.
- Local engine fingerprint, DLL, and runtime refreshed.

Limits: the gallery is synthetic presentation evidence, not natural encounter
coverage for every one of the 215 identities. New props establish distinct
silhouettes and materials; transient variants do not all have bespoke
animations. Surface light patches are painted treatments. No release ZIP,
GitHub push, or itch upload was performed.

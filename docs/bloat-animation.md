# Bloat model and animation

BRG-M06 / MK_BLOAT uses an original animated IQM, created through Blender MCP
with the shared enemy workflow. Brogue describes a buoyant bladder with a thin
veinous membrane. The closed, mildly lobed purple body follows that description;
it adds no eyes, limbs or invented attack organs. Seven bones deform one continuous
membrane, with 1,521 runtime vertices and 2,976 triangles. Rest extents are
28 x 26.3268 x 32 map units, with a 16-unit hover gap. Numerical size is an art
choice, not a Brogue rule. The purple diffuse contrast and broad silhouette remain
legible at 64, 128 and 192 units without glow or a visibility override.

The six clips are idle, drift, bump, bump_alt, recoil and collapse. The two bump
clips are cosmetic alternatives, not additional Brogue attacks. Collapse compresses
and lowers the membrane over the existing 18-tic death presentation window.
The old OBJ and static Blender source remain available for comparison.

## Authority

This is presentation-only work. No simulation source, ABI, collision, damage,
AI, gas rules, turn processing or Brogue RNG is changed. The generated profile
registers the model in the existing proxy and native animation machinery.
`Combat.c` handles `MA_KAMIKAZE` through `killCreature`; normal `MA_DF_ON_DEATH`
deaths call the existing `spawnDungeonFeature` with `DF_BLOAT_DEATH`. The frontend
reads the copied result, plays collapse and retains the existing gas presentation.
Administrative removals retain the existing immediate-hide path. Hidden/sensed
creatures retain shared visibility rules. No extra particles or lights were added.

## Verification — September 13, 2026

- `python -m unittest tools.monster_models.test_bloat tools.monster_models.test_skeletal tools.test_broguedoom_resources`
  passed 39 tests. Bloat checks cover closed manifold connectivity, animated seam
  equality, hover/collapse bounds, loop continuity and identical generated model
  and skin bytes.
- Blender MCP created the asset. A clean background rebuild and saved-file reopen
  checked packed texture, rig and six Actions; 18 sampled deformations matched
  the runtime solver. See `artifacts/bloat-animation/blender-verification.json`.
- `python tools/run_native.py cmake --build .build/uzdoom --config Release -j 4`
  passed. The engine source/build fingerprint was refreshed and verified.
- `python -m tools.monster_models.review_skeletal --symbol MK_BLOAT --backend 1 --all-angles --distances --packaged`
  and backend `0` each captured 34 images: static reference, clip samples, four
  angles and three gameplay distances. Representative idle/distance/collapse
  captures were visually inspected. Each PK3's model, skin and bindings were
  checked byte-for-byte against source; both backend packages are identical.
  Evidence: `artifacts/skeletal-review/MK_BLOAT/{vulkan,opengl}/`.
- `python -m tools.monster_models.review_bloat_encounter --backend 1` and backend
  `0` replay ordinary bridge intents in a real seed-4, depth-2 dungeon. A read-only
  route selector links the existing bridge DLL and records commands; it never
  writes creature state. Two headless runs agree. In UZDoom, directly visible
  bloat ID 26 collapses after Brogue resolves its death; the existing purple gas
  remains after the proxy disappears. Final state hash agrees with the headless
  route: `464a4af7a0c08c6b`. The observer only aims a camera from the player's eye;
  it does not reveal or reposition enemies. Captures and logs live in
  `artifacts/bloat-encounter/{1,0}/`. Screenshot waits include frontend queue
  latency; filenames indicate visual stages, not exact simulation timestamps.
- Seed-4 startup compilation and map verification passed with 6,873 sectors.
  This reuses the existing generated dungeon; no generation rules were changed.

Runtime IQM SHA-256:
`35d657507dfafd898a3569413d1fbe8ea25b46b3df4a7027deeff73676933ed8`.

## Rebuild and remaining acceptance

Run `python -m tools.monster_models.bloat_animation`, then
`python -m tools.monster_models.generate` and `python -m tools.monster_models.bestiary`.
Rebuild the editable source with Blender's shared `blender_skeletal.py -- MK_BLOAT`
entry point. The editable file is `assets/monsters/bloat/bloat-animated.blend`.

Individual art approval, physical-input acceptance, standalone visual comparison,
comparative frame-time benchmarking and a full release distribution were not
performed. The normal encounter covers one seed and death sequence, not every
way a bloat can die. A gallery capture is separate from natural encounter proof.
All new mesh, skin and animation content is original Project Broom work under
CC-BY-SA-4.0; no third-party artwork was imported.

# Eel model and aquatic presentation

BRG-M04 / MK_EEL now uses an original weighted IQM, authored and refined in a
dedicated Blender session through Blender MCP. The repeatable source is
`tools/monster_models/eel_animation.py`; the editable asset is
`assets/monsters/eel/eel-animated.blend`. The earlier OBJ and Blender reference
remain available.

The body is a continuous closed ring mesh, with a tapered tail, integrated
dorsal/ventral fin ridges, gill marks, eyes, and an articulated lower jaw.
The 13-bone rig supplies idle, swim, bite, strike, recoil and death clips through
the existing skeletal registry. The two attack clips are cosmetic variants of
resolved attacks; they do not claim to identify Brogue's selected attack verb.
Reddish-brown diffuse skin, a lighter belly and flank gradient make the silhouette
read against blue water without emission, lights or a visibility override.
Rest extents are 54.8 x 7.3019 x 7.1643 map units; numerical dimensions are art
choices. A cell remains 64 units.

## Water and authority

The existing water surface is an opaque render-only 3D floor at Z=0 above the
deep bed at Z=-24. A model this low would otherwise be entirely concealed even
when Brogue reports direct visibility. `MonsterWorldPosition()` uses the
presentation kind, copied visibility, and known liquid appearance to put the
visible eel's center on that surface (model origin = surface minus seven).
Flood water uses the existing 8/24-unit surface levels. Bridge, ice, dry and
unknown appearances retain the ordinary placement. Stationary surfacing also
refreshes height; movement targets use the same calculation.

Hidden eels remain on ordinary bed support with the existing zero-alpha/invisible
flags. Sensed eels retain the shared 0.38 alpha. A hallucinated model is selected
by presentation kind; actual species is not disclosed by this visual offset.
This does not alter Brogue coordinates, visibility decisions, submersion flags,
combat, turns, RNG, movement acceptance or the public ABI. There is no new Doom
AI, collision, damage, glow or autonomous action. This is presentation work.

## Evidence — September 13, 2026

- Native Release build passed with
  `python tools/run_native.py cmake --build .build/uzdoom --config Release -j 4`.
  The wrapper resolves the existing duplicate PATH/Path MSBuild environment error.
- 40 tests passed:
  `python -m unittest tools.monster_models.test_eel tools.monster_models.test_skeletal tools.test_broguedoom_resources tools.test_enemy_movement`.
  Eel checks include closed manifold body seams, repeatable binary/skin bytes,
  clip bounds, and compilation/execution of the actual native projection function
  against direct/hidden/sensed, flood, ice, bridge, unknown and hallucination cases.
- Blender MCP created and refined the rig. A clean background reconstruction
  reopened the saved source, verified its packed skin and six Actions, and
  matched 18 sampled Blender poses to the runtime solver within 0.0001 units.
  See `artifacts/eel-animation/blender-verification.json` and `studio-final.png`.
- `python -m tools.monster_models.review_skeletal --symbol MK_EEL --backend 1 --all-angles`
  and backend `0` captured 31 poses each, including the old static reference.
  See `artifacts/skeletal-review/MK_EEL/{vulkan,opengl}/`.
- `python -m tools.monster_models.review_eel --backend 1` and backend `0`
  passed packaged water captures at 64, 128 and 192 units, hidden and sensed
  display, and an underwater camera. Captures were inspected. The fixture uses
  the canonical opaque non-solid liquid plane, not transparent studio water.
  See `artifacts/eel-water/{1,0}/`. Each review PK3 was checked against the source
  model, skin, MODELDEF and actor bindings. These fixtures exercise rendering;
  they do not simulate an actual eel encounter or call Brogue visibility logic.
- `python -m tools.test_chasm_transition --backend 1` passed an actual seed-1
  dungeon launch, ordinary movement and the depth-2 fall/arrival sequence with
  the expected turn-28 state hash `16b7f15d918ac047`. This verifies the rebuilt
  engine in a natural dungeon, not an encounter with an eel.

Runtime IQM SHA-256:
`e7c4231fcdbec89929b364a0965cf05b8e09fb43d906b6870e4f818443385d05`.

## Remaining acceptance

An actual naturally encountered eel's attack/surface/submerge sequence, physical
input acceptance, standalone visual comparison and full release distribution
have not been verified. The renderer fixtures and native copied-state tests
are separate evidence. Individual art approval remains the maintainer's choice.
No comparative frame-time benchmark was run; the mesh has 6,464 triangles and
adds no particles, dynamic lights or runtime geometry generation.

All new mesh, texture and animation content is original Project Broom work under
CC-BY-SA-4.0. No third-party model, texture, photograph or generated image-service
artwork was imported. Upstream Brogue text and licensing remain unchanged.

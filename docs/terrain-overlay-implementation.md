# Floor-preserving terrain effects

Presentation and copied-state parity work, 2026-09-09. No gameplay outcomes change;
Brogue CE remains authoritative.

The 22 bindings identified in `terrain-overlay-audit.md` now use separate masked
coatings rather than selecting their opaque catalog texture as the floor.
Blood, puddles, residue, ash, growth, hay, glyphs, light and cracks leave the
actual substrate visible. Light patches use soft additive falloff; shadows use
translucent shading. HOLE_EDGE uses dark translucent fissures over the original
floor, rather than opaque marble. It is a stylized treatment, not refractive
glass or a newly opened gameplay hole.

The generator `tools/terrain_overlays.py` creates original CC0 RGBA textures and
a shared floor-aligned quad. All actors inherit NOINTERACTION, NOBLOCKMAP and
NOGRAVITY from BrogueTerrainStone, have no actions, and consume no gameplay RNG.
Quarter-turn variation comes only from cell coordinates. A small height offset
separates coatings from the floor and each other. The substrate resolver also
prevents debris/web model bindings from replacing carpet or marble with earth.

ABI v21 adds three uint16 copied identities to the appearance record: dungeon,
liquid, surface. These are explicitly mapped from Brogue's enum (GAS is slot 2
in Brogue; SURFACE is slot 3). `captureTerrainAppearance()` applies the existing
secret-tile sanitization. Remembered/mapped cells contain only rememberedTerrain
in the first slot; unknown cells have no copied identities. No live hidden layers
are used to reconstruct remembered terrain. Where Brogue remembers only a
surface, the unknown substrate uses the existing neutral floor fallback.

The renderer keeps up to three coating actors per cell. A fresh snapshot removes
missing coatings immediately, supports stacked blood and sunlight, and resolves
the same substrate in settled geometry and shoreline refresh. Full-cell liquids
and bridge/ice decks retain their dedicated rendering paths. The bridge layout
is now 36 bytes per appearance and 120 bytes per cell; C++, harness ABI assertions,
save-test requests, launcher API constant and presentation hash were updated.

The copied layers affect the presentation hash only. Brogue state, dungeon
generation, topology, connectivity, turns and RNG remain unchanged.

## Verification

`tools.test_terrain_overlays` checks transparent surrounds, soft light alpha,
exact preservation of differently colored substrates, and deterministic output.
The terrain smoke harness checks simultaneous marble/sunlight/blood/gas, secret
sanitization, memory and unknown cells, plus existing native-versus-bridge action
and RNG parity across five repeated seeds.

`python -m tools.capture_terrain_overlays --label final-vulkan --backend 1`
and the corresponding `final-opengl --backend 0` run an explicit renderer-only
13-scene gallery. Each stage checks unchanged authoritative state/turn, and the
final stage asserts removal leaves no coating actors. Cases include earth,
marble, carpet, bridge, glyphs, debris, shadows, embers, hole edges and stacked
sunlight/blood. The fixture uses copied presentation state; it does not add
terrain combinations to Brogue. Screenshots and logs are under
`artifacts/terrain-overlays/`; the user's supplied screenshot is the original
reported before view, not a matched gallery capture.

This change does not replace the earlier water/lava shaders or invent new
illumination rules in Brogue. The coatings are local visual approximations;
they do not add screen-space refraction or new dynamic lights.

## Completed checks

- Canonical engine/bridge build succeeded; its launcher restore initially hit
  restricted NuGet access. The authorized network-enabled launcher build then
  succeeded and refreshed the root `ProjectBroom.exe`.
- Main suite: 147 tests passed (`full-tests-final.log`). After adding the new
  generated header to the build-receipt test fixture, the remaining suites passed
  all 42 tests (`remaining-tests.log`). Final animation/overlay checks passed seven
  tests and the added layer-only reconciliation regression passed separately.
- Five seeds (1, 2, 42, 12345, 99999), repeated native/bridge terrain checks passed.
- The requested 300-action simulation ended naturally at turn 195, killed by a
  rat, with gameplay hash `36b2a00b6543c40a`, matching the previous baseline.
- Final OpenGL and packaged-resource Vulkan runs captured all 13 stages:
  `accepted-opengl/` and `accepted-vulkan/`. Each reports unchanged authoritative
  hash; initial/final gameplay hash is `c92268ff6250781b`.
- Overlay generation was byte-identical on repeat. The local validation PK3 is
  `artifacts/terrain-overlays/ProjectBroom-overlay-validation.pk3`; it is a resource
  package, not a new public release ZIP. No listing or release was uploaded.
- Surface changes no longer trigger the generic wood-fragment animation merely
  because a stain appeared or disappeared.

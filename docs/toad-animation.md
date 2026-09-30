# Toad model and animation

Presentation-only work on BRG-M13 / `MK_TOAD`.

## Selection and expected behavior

The first nine catalog creatures already have skeletal profiles. Catalog order
is not encounter order: the next ordinary hostile encounters in the pinned
`GlobalsBrogue.c` table are toad and pink jelly, both nominally depth 4. Toad
appears first (row 759); its ordinary range is 4–11. Machines, captives and
out-of-depth selection can differ. Brogue retains all selection rules.

Brogue describes an enormous, warty toad secreting hallucinogenic slime, with
the attack verbs "slimes" and "slams". The model has a squat broad
body, folded hind legs, four front digits and five rear digits, raised eyes
with horizontal pupils, parotoid glands, a wide mouth and irregular warts.
Anatomical details, olive/buff/copper materials and numerical dimensions are
artistic interpretation. No tongue projectile, glow, new damage or slime
hazard is introduced.

Six presentation roles use `idle`, `crawl`, `slime`, `slam`, `recoil` and
`death`. Only idle/crawl loop. Existing copied movement/attack/hit/death state
selects these clips; the attack alternatives do not assert that the bridge
identifies a precise attack verb. `MA_HIT_HALLUCINATE` and all combat outcomes
remain in Brogue, including `Combat.c::specialHit` and its existing
`MA_HIT_HALLUCINATE` path. No public ABI or simulation code changed.

## Delivered assets

- 17 bones, six clips, 8,090 runtime vertices and 13,254 triangles; the old
  static reference has 9,496 triangles and remains untouched.
- Closed connected body cage: 2,803 vertices, 5,602 triangles, one component.
  Eyes, mouth details and 64 low-profile warts remain separate; wart weights
  derive from the supporting skin triangle. Four front/five rear digits on
  each side, heavy eyelids, horizontal pupils and broad parotoid glands.
- Rest extents: 37.6618 / 44.0596 / 22.7728 map units. Full animation bounds
  remain within a 64-unit lateral envelope; the death pose settles below
  20 units tall. None of these dimensions controls gameplay collision.
- 1024-square olive/buff/copper diffuse and specular maps, plus a flat normal
  map preserving sculpted normals. The pinned UZDoom native material path
  provides restrained highlights from existing scene lights. It adds no light,
  emission, particles or simulation effect. Dark unlit rooms remain subdued.

The source modules are `tools/monster_models/toad_animation.py` and
`toad_materials.py`. The registry drives all native clip names/durations,
MODELDEF and ZScript bindings. Connected-skin selection adds only the toad;
the Blender exporter gains an optional per-profile roughness with its existing
default preserved. All other bestiary entries and verification are retained.

## Verification performed, 2026-09-26

Evidence root: `artifacts/toad-model-20260926/`.

1. Native compilation passed:
   `python tools/run_native.py cmake --build .build/uzdoom --config Release -j4`.
   The sole native source delta is the generated K13 presentation-table row.
2. 53 tests passed:
   `python -m unittest tools.monster_models.test_toad tools.monster_models.test_skeletal tools.monster_models.test_connected_skin tools.monster_models.test_creatures tools.test_broguedoom_resources`.
   This checks closed topology, shared seam weights, normalized influences,
   cyclic loops, diagonal support feet, seated warts, floor/corridor bounds,
   export bytes, roster bindings and all existing resources. The first pass
   caught a stale generated dimension after anatomy refinement; bindings were
   regenerated before the passing final suite.
3. Isolated Blender 5.2.1 rebuilt and freshly reopened the source, checking
   six Actions, packed diffuse and no linked libraries. Eighteen sampled poses
   agree with the runtime solver within 0.00001 map units. Existing desktop
   documents were untouched. Blender's extension-cache permission warning was
   nonfatal; no global settings were changed to suppress it.
4. A second cold, single-thread Blender bake plus runtime rebuild reproduced
   the cage, IQM, diffuse, normal and specular maps byte for byte. Blender file
   bytes themselves are not promised deterministic. See `determinism.json`.
5. Both Vulkan and OpenGL launched the actual packaged resources and captured
   34 gallery views each: static before, all six clips, front/side/rear and
   64/128/192-unit distances. All 34 actors per backend report `blocking=0`.
   Representative views and distance captures were inspected. The two PK3s
   are byte-identical, with model, all three textures and bindings matching
   source; see `package-verification.json`.
6. Seed 26, depth 4: a 219-intent route sees natural toad ID61 at cell 56,24,
   player 56,21. Repeated headless routes and both renderer runs reach hash
   `051bee07f070e809`. Three more ordinary south intents approach to adjacent
   range and hit the toad: HP goes from 18 to 3 and the native event plays
   `recoil`; final renderer hash is `c4f1c2689c37f3e6`. The observer aims from
   the actual player's eye and leaves Brogue visibility intact. No creature
   was spawned, moved, revealed or given altered health to obtain the capture.
   The observer can use copied hidden map knowledge to plan diagnostic intents;
   this is a reproducible test route, not a player-autopilot feature.
7. Seed-26 startup map compiler and topology/package verifier passed. No map
   generation or terrain code changed.

Reproduce the galleries with:

```powershell
python -m tools.monster_models.review_skeletal --symbol MK_TOAD --backend 1 --all-angles --packaged --distances --output artifacts/toad-model-20260926/final-vulkan
python -m tools.monster_models.review_skeletal --symbol MK_TOAD --backend 0 --all-angles --packaged --distances --output artifacts/toad-model-20260926/final-opengl
python -m tools.monster_models.review_toad --backend 1 --package artifacts/toad-model-20260926/final-vulkan/ProjectBroom-review.pk3 --output artifacts/toad-model-20260926/final-natural-vulkan
python -m tools.monster_models.review_toad --backend 0 --package artifacts/toad-model-20260926/final-opengl/ProjectBroom-review.pk3 --output artifacts/toad-model-20260926/final-natural-opengl
```

The encounter runner needs the seed-26 startup package. Build it with the
existing `brogue.exe --export-dungeon-json ... --seed 26 --depths 4`, then
`tools/mapcompiler/compile.py --input ... --output ... --startup` and the
matching `verify.py --input ... --package ... --startup`. See the exact input
and output paths in `review_toad.py`.

Final hashes:

```text
IQM  95cb4dede9900598876917c87f81827370cf0d3352415470a70675896309c962
PNG  7dbaf0d0ff40c76f85ddf44cd7432737576380f0197a1cabeb223dd20dc0bad7
Cage d1c48422e9f4a27220f8200086cf8cf5189586dcb19868387bd96a1cda0d068c
PK3  faeaa251e540947ed703cf5fc940f07f743623eefc07f6687333dde1f9c9448e
```

## Review scope and next work

The natural capture verifies appearance, close approach and a real hit/recoil.
Natural toad attacks, hallucination onset, death and captivity were not captured;
their poses were inspected in the gallery. Full standalone comparison, manual
input acceptance, a controlled frame-time benchmark and release-installer
packaging were not run. This is a presentation change, not new gameplay-parity
proof or final individual art approval. Existing minimap signedness and menu
texture warnings remain; no new missing toad resource was reported.

There are now 10 skeletal entries out of 67 non-player forms; the remaining
57 have static models. Next ordinary encounter priorities are pink jelly
(depth 4), goblin totem and arrow turret (depth 5), then vampire bat, acid mound
and goblin mystic groups (depth 6). These are nominal ranges, not guaranteed
spawn order; the catalog IDs stay stable.

[Engine before/after comparison](../artifacts/toad-model-20260926/before-after.png)
uses the same crop and camera. Full-resolution evidence remains alongside it.
The [studio render](../artifacts/toad-model-20260926/studio-final0001.png) shows
editable-source detail under Blender lighting.

All model and texture artwork is original Project Broom work under
CC-BY-SA-4.0. No third-party assets are imported.

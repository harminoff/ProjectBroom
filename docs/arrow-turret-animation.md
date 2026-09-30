# Arrow turret model and animation

Presentation-only BRG-M15 / MK_ARROW_TURRET. Brogue describes a spring-loaded mechanical contraption embedded in a wall firing repeated arrows. MONST_TURRET is immobile, inanimate and attackable through walls; all firing, targets, damage and turns remain Brogue-owned.

Art plan: fixed iron-rimmed timber mounting plate, pegged braced cantilever, split crossbow limbs, wound spring drums, ratchet teeth, sliding bolt carriage, iron stirrup, a distinct loaded arrow with head and feather vanes, and spare bolt magazine. Weathered oak, dark wrought iron, worn brass bearings and cream fletching are original art decisions. Six roles: idle, literal unused-move rest, release/rearm variants, impact jolt and broken mechanism sag. Mount and anchor bolts remain fixed in every pose. No cosmetic arrow leaves the asset.

Proof planned: rigid part integrity and attachment, fixed mount through every clip, unit-scale bones, rest/loop recovery, bounded mechanism, deterministic IQM/atlas, fresh editable Blender and sampled poses, native compile, packaged 1920x1080 Vulkan/OpenGL before/after/angles/distances, natural ordinary-intent wall encounter and identical state hashes. Inspect current cell-center clipping and attack-yaw before introducing a copied-knowledge-only wall mount projection. No terrain edits, collision, reveal, gameplay or ABI changes. User art approval stays open.

## Delivered artwork and source

The finished mechanism has 103 named parts, 5,033 runtime vertices, 7,866
triangles, eight bones and six clips. Its five oak mounting planks sit within
an iron plate with six forged anchors and fixed diagonal cantilever braces.
Three-layer crossbow limbs, two eight-turn steel springs, 24 ratchet teeth,
brass axle flanges, rails, a sliding cord carriage, sear, stirrup, individually
modelled arrowhead/fletching and four spare bolts supply close-view detail.
The plate, supports and magazine are rigidly fixed to the root in every pose.
Separate pieces represent actual mechanical assembly; no organic cage is used.

The 1024-square original diffuse distinguishes timber, iron, brass, cord,
feathers, polished edges, recesses and cut ends. Palette/padding utilities are
reused from the original goblin family. There is no glow, projectile actor,
normal/specular dependency or imported art. All new artwork is CC-BY-SA-4.0.
The retained loaded arrow is a cosmetic mechanism detail, not an independent
projectile or a guarantee of exact Brogue shot timing.

- Deterministic masters: `tools/monster_models/arrow_turret_animation.py` and
  `arrow_turret_materials.py`.
- Editable source: `assets/monsters/arrow_turret/arrow-turret-animated.blend`.
- Runtime: `mod/BrogueDoom/models/monsters/15_arrow_turret.iqm` and
  `mod/BrogueDoom/graphics/BRGARROW.png`.
- Manifest: `assets/monsters/arrow_turret/animation.json`.
- Rest dimensions: 33.1 / 40.3246 / 41.76 units. Every authored frame stays
  within X -13.1..23.0931, Y -20.4431..20.4431, Z 0.12..41.88.
  These are artistic bounds; they do not change creature collision or size.
- Idle and the unused move role (`rest`) are exact rest. `release` and `rearm`
  move the bolt sled, string, drums and sear, then recover. `recoil` jolts the
  mechanism. `break` sags the crossbow and bent limbs while the wall plate and
  supports stay attached. Only idle/rest loop, and every bone keeps unit scale.

## Wall projection and authority

The pre-change natural Vulkan capture demonstrates a real projection defect:
Brogue reported a directly visible arrow turret at cell 74,24, but the static
model was completely hidden inside its wall. Source facts support the intended
wall mounting: `Globals.c:1217` describes an embedded contraption, and
`MONST_TURRET` includes `MONST_ATTACKABLE_THRU_WALLS`, immobility and inanimation.

The opt-in skeletal profile field `wallMountBack` describes only model geometry.
The new `wall_mount.h` helper chooses among cardinal faces whose neighbouring
copied appearance is known and neither WALL nor OPAQUE. The source cell must
be a copied known wall, and the creature must be directly visible. Only its
displayed identity selects the profile; no hidden underlying kind/flags are
used to reveal a turret. The face toward the copied player cell wins, with
previous-face retention for equal scores. This handles both sides of a thin
wall and corner ties without camera panning or attack targets rotating a mount.

The actor origin is offset by 32 + 13.1 + 0.3 = 45.4 units along that face. Its
rear plane sits 0.3 units outside the cell's face. `BeginMonsterEventAnimations`
retains mounted yaw; existing event selection still chooses cosmetic action
variants. The pure helper is shared with the isolated fixture, not duplicated
in Python. Visibility changes and displayed identity replacement fall back to
ordinary placement when the mount's preconditions no longer hold.

No wall is cut, no hidden cells or creatures are revealed, and no Brogue cell
coordinate, terrain, collision, line-of-sight, RNG, projectile, turn or ABI is
changed. This is not a gameplay visibility/targeting rule. The pending-map
presentation barrier and all earlier transition-repair code are preserved.
A narrow diff against the immediate dirty source is retained as
`artifacts/creature-queue/BRG-M15/native-presentation.diff`.

## Verification, 2026-09-26

Evidence root: `artifacts/creature-queue/BRG-M15/`.

1. **57 tests passed** with
   `python -m unittest tools.monster_models.test_arrow_turret tools.monster_models.test_skeletal tools.monster_models.test_connected_skin tools.monster_models.test_creatures tools.test_broguedoom_resources`.
   The eight arrow-specific tests cover signature construction, exact fixed
   mounting/support coordinates, rest behavior, recovery/unit scales, string
   weights, positive triangle area at every frame, the full animated envelope,
   exact IQM/atlas bytes, source gates and compiled cardinal selection tests.
2. **23 focused tests passed** after the final selector changes:
   `python -m unittest tools.monster_models.test_arrow_turret tools.test_level_transition tools.test_engine_source tools.test_enemy_movement`.
   They include opposite-side approaches, corner ties, unknown/hidden cases,
   unavailable-face fallback and prior transition safety. The fingerprint test
   fixture initially lacked the new header; adding it to both the build-input
   fingerprint and its fixture resolved that test failure.
3. **81 primary tests passed**:
   `python -m unittest tools.test_brogue_bridge tools.test_broguedoom_resources tools.mapcompiler.test_compile`.
   The unchanged seed-26 startup package also passed `tools/mapcompiler/verify.py`
   against `generated/seed-26/brogue-dungeon.json` with `--startup`.
   Counts describe separate overlapping runs, not an aggregate unique-test count.
4. Release compilation passed with
   `python tools/run_native.py cmake --build .build/uzdoom --config Release -j4`.
   The build fingerprint was recorded only after successful compilation and
   `validate_build()` subsequently verified the executable and current inputs.
   `wall_mount.h` is included in fingerprint tracking.
5. Three builds reproduced IQM, PNG and animation-manifest bytes exactly;
   `determinism.json` records all hashes. Blender 5.2.1 in an isolated background
   process saved and freshly reopened the editable source with six Actions,
   eight bones, one packed image and no linked libraries. Eighteen sampled poses
   agree with runtime skinning within 0.000005436 units. The known extension-cache
   permission warning was nonfatal; no global preferences or live document were
   modified. Blender-file byte determinism is not claimed.
6. Packaged Vulkan and OpenGL galleries each captured **34 views at 1920x1080**:
   static before, three samples per role, front/side/rear and 64/128/192-unit
   distances. Both contact sheets and representative full images were inspected.
   The mechanism remains distinct at distance, the rear plate is intentionally
   solid, and broken poses leave the plate/support in place. All 34 subjects per
   renderer log `blocking=0`. Packages are byte-identical; IQM, skin, MODELDEF and
   ZScript contents exactly match source. Only existing menu/minimap warnings
   appear; no new model/resource errors were found.
7. The separate solid-pillar fixture supplies transforms from the actual C++
   selector and tests four cardinal approaches plus two corner approaches, each
   with idle, release and broken poses. Both renderers captured **18 nonblocking
   1920x1080 views**, inspected in `wall-fixture-*-v2`. All sides show the mounted
   mechanism outside the unchanged pillar. First fixture captures applied clips
   during the initial Spawn state and consequently showed idle; the final v2
   fixture waits two tics before applying samples, matching the established
   gallery workflow. Earlier evidence is retained but not used as action proof.
   The fixture is isolated presentation geometry, not a natural encounter.

```text
IQM 349d7472b0cb10a2ccca5b11dc390abf44c17cacd20efaaac4eccf7178585834
PNG 6ad4872f87128c0ae778485c04e8c55a2d43c91a7e1872d149a4ef8fb5233698
PK3 7e11645a82c80f36c0d1bd5f5492fb1175ba9b3816fa7cf66a25e99e3cb9ff4c
```

## Natural encounter and remaining gates

A bounded ordinary-intent route search found seed 26, depth 6, turret ID94 at
74,24 after 323 intents. Repeated headless routes matched hash
`ab31c1c06bb8a76a`. Both packaged renderers reached the same directly visible
wall-mounted turret from the real player eye at 72,24, HP 11/30, absolute turn
318 (native revision 325 includes recording/transition setup). The visual
origin is 82.6 units from the player rather than the wall-cell centre's 128.
The observer only aims its camera; it neither spawns nor moves creatures.

Every one of the **325 action/hash pairs** in each after-run (323 route intents
plus two ordinary waits) matches the pre-change native replay. Follow-up hashes
are `cdc46c052b4c771d` and `33d5dca7b8bf04db`. Five transitions through BRG02–BRG06
passed the no-command/no-proxy-before-map-load audit. Both processes exited 0
and captured encounter/active/resolved views. `runtime-verification.json`
records hashes, queue preservation and package checks. The observer adds only
missing depth-five/six MAPINFO declarations to its overlay, preserving the
original startup package and all Brogue-generated geometry/state.

The two waits did **not** establish a natural firing animation or death; the
natural log remains on idle for this turret. Action/death poses are proven in
the isolated galleries, without claiming exact bolt-event synchronization.
User art approval, natural firing/death event coverage, manual input acceptance,
standalone side-by-side comparison, controlled frame-time measurement and full
release-installer packaging remain open. The shipped scope here is the model,
wall projection, deterministic resource packages and actual renderer evidence.

## Preservation and reproduction

The immediate inventory covers 549 files, plus three supplemental pre-edit
copies for architecture/fingerprint files. Of those **552**, 538 remain
byte-identical; 14 changed baseline files are the intended arrow registration,
shared mount projection/fingerprint or documentation edits. No files disappeared.
All **67 other bestiary entries**, **12 prior skeletal profiles**, other creature
cards and prior model/texture outputs are preserved. The conjurer card was
restored from the immediate pre-task copy after generated-card normalization,
never from HEAD. Original static arrow OBJ/skin/Blend references remain intact.
The queue, previous evidence and review packages were not compacted or deleted.
No commits, publishing or unrelated cleanup were performed.

Shared edits: skeletal profiles/registry/generated table, native frontend and
new `wall_mount.h`, fingerprint helper/test, generated MODELDEF/ZScript/monster
registry, bestiary generator/index/card/index page, and runtime architecture.
New model-specific generators, tests and observers are independently named.
The handoff report does not mark individual user art approval complete.

```powershell
python -m tools.monster_models.review_skeletal --symbol MK_ARROW_TURRET --backend 1 --all-angles --distances --packaged --width 1920 --height 1080 --output artifacts/creature-queue/BRG-M15/gallery-vulkan
python -m tools.monster_models.review_arrow_turret --backend 1 --package artifacts/creature-queue/BRG-M15/gallery-vulkan/ProjectBroom-review.pk3 --output artifacts/creature-queue/BRG-M15/natural-vulkan
python -m tools.monster_models.review_wall_mount --backend 1 --package artifacts/creature-queue/BRG-M15/gallery-vulkan/ProjectBroom-review.pk3 --output artifacts/creature-queue/BRG-M15/wall-fixture-vulkan-v2
```

Substitute backend 0 and fresh output paths for OpenGL. If the coordinator later
archives packages, restore their exact archive manifest before using these paths.

[Engine before/after](../artifacts/creature-queue/BRG-M15/before-after.png),
[natural wall before/after](../artifacts/creature-queue/BRG-M15/wall-before-after.png),
[Vulkan gallery](../artifacts/creature-queue/BRG-M15/gallery-vulkan-contact.jpg),
[OpenGL gallery](../artifacts/creature-queue/BRG-M15/gallery-opengl-contact.jpg),
[wall/corner poses](../artifacts/creature-queue/BRG-M15/wall-fixture-opengl-v2-contact.jpg).

## Coordinator archive note

The two gallery PK3s were losslessly compacted after review. Their `.pk3.archive.json` manifests preserve exact package bytes; screenshots and logs remain in place. Restore before replaying a package path:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M15/gallery-vulkan/ProjectBroom-review.pk3.archive.json
```

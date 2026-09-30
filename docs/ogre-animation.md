# Ogre model and animation

The coordinator losslessly archived the review packages after verification.
Restore the final Vulkan package before replaying the archived evidence:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M18/final-collapse-vulkan/ProjectBroom-review.pk3.archive.json
```

Use the corresponding `final-collapse-opengl` manifest for OpenGL. Screenshots,
logs and archive segments remain available; restoration reproduces exact bytes.

Presentation-only BRG-M18 / MK_OGRE. Brogue CE remains authoritative.

## Source and planned proof

Pinned Brogue describes a lumbering large creature carrying an enormous club
that it swings with incredible force. Its verbs are cudgels, clubs and batters;
staggering and corridor avoidance remain source-owned. No health, damage,
collision, AI, turns, visibility, RNG, spawn rules or ABI will change.

Original art interpretation: a barrel-chested, thick-necked brute with a heavy
belly, blunt brow and jaw, small rounded ears, bowed weight-bearing legs,
broad feet and a knotted wooden club held in a closed right-hand grip. Warm
earth-red skin, coarse brown hide wrap, weathered wood and pale worn teeth
are material choices rather than additional Brogue lore. No goblin scaling,
magic or invented attack is intended. Six cosmetic roles are idle, lumber,
cudgel, batter, recoil and collapse; only the first two loop.

Planned proof: connected manifold anatomy, grip attachment, reachable leg IK,
loop closure, every-frame centered clearance and floor checks, repeated cage
and runtime builds, fresh-open Blender with 18 pose comparisons, native compile,
packaged 1920x1080 Vulkan/OpenGL galleries and the prepared seed169 ordinary
intent encounter. Captive/allied flags must be inspected before making combat
claims. User art approval, physical play and exhaustive natural lifecycle
acceptance are separate gates. Original Project Broom artwork, CC-BY-SA-4.0.

## Delivered model

- Master: `tools/monster_models/ogre_animation.py` and `ogre_materials.py`.
- Connected cage and editable source: `assets/monsters/ogre/connected-skin.json.gz`
  and `assets/monsters/ogre/ogre-animated.blend`; manifest `animation.json` beside them.
- Runtime: `mod/BrogueDoom/models/monsters/18_ogre.iqm` and original 2048-square
  `mod/BrogueDoom/graphics/BRGOGRE.png`. The static OBJ/skin/Blend remain unchanged.
- 19 bones, 35 parts, 21,996 runtime vertices, 14,952 triangles and six clips.
  The closed connected skin carries the body, head, arms, hands, legs and toes;
  eyes, teeth, mouth, worn hide and held club remain separate accessories.
- Rest extents: 21.7472 x 44.9857 x 75.9189 units. These are artistic dimensions.
  Every sampled frame stays within centered X -29.8492 to +17.8001 and
  Y -25.3677 to +21.6291. Minimum Z is 0.1057; maximum height is 76.3951.
  The upright club and restrained swings deliberately preserve corridor
  clearance rather than widening collision or changing Brogue corridor rules.

The walk uses a 60% stance / 40% recovery gait, with reachable two-link IK and
at least one planted support foot. The collapse bows the torso 42 degrees, droops the neck/head and lowers the
club diagonally through the gripping wrist, settling below 54 units with both
feet planted. All six exported clips need **zero automatic floor correction**.
The club bone coincides with the gripping hand throughout every frame; four
curled fingers and a thumb surround the shaft. Idle/lumber loop; cudgel/batter,
recoil and collapse are one-shot presentation roles. The attack variants do
not claim to identify the exact Brogue prose verb.

The first engine pass exposed triangular material patches caused by transferring
individual primitive UVs onto a fused body. The final skin uses padded triangle
islands with continuous rest-position pigment and smooth baked sculpt shading.
This removes the old source-part shade discontinuities. Vertex positions,
normals and weights remain identical across UV seams. The original skin atlas
generator uses only the Python standard library; NumPy/Pillow are not runtime
build dependencies. The club has irregular end wear, wood knots and less
repetitive grain. All shading is painted diffuse; no emissive light or effect.

**Art limitations:** close skin views retain subtle polygon/material banding;
collapsed poses show angular skin deformation at some shoulder/belly folds, and the death pose remains a deeply bowed crouch rather than a prone corpse.
These have not received user art approval. The natural view shows the ogre's
back, so facial assessment comes from the gallery. The old static before model
clips the top of the fixed oblique camera; the final model and three dedicated
distance views fit the frame. No exhaustive self-intersection proof is claimed.

## Verification and final evidence

Evidence root: `artifacts/creature-queue/BRG-M18/`. Authoritative final gallery
directories are **final-collapse-vulkan** and **final-collapse-opengl**; earlier first,
revised and final-vulkan directories contain superseded materials.

- **54 tests passed in 143.579 seconds** (`tests-collapse-final.log`):
  `python -m unittest tools.monster_models.test_ogre tools.monster_models.test_skeletal tools.monster_models.test_connected_skin tools.monster_models.test_creatures tools.test_broguedoom_resources`.
  Five ogre tests check closed connected topology, equal seam geometry/normals/weights,
  all limb chains, normalized influences, every-frame centered bounds, zero floor
  lift, loop closure, both death support feet, attached club grip, material-island
  isolation and exact current IQM/PNG bytes.
- Native Release compilation passed with
  `python tools/run_native.py cmake --build .build/uzdoom --config Release -j4`.
  The successful build fingerprint was then refreshed using
  `python tools/engine_source.py --root . --record-build .build/uzdoom/Release`.
  Only the generated K18 presentation-table row was added; subsequent material
  refinement changes no native contract.
- The canonical `python -m tools.monster_models.skeletal_registry --build`
  passed, followed by generated binding/bestiary refresh. Two cold single-thread
  Blender cage bakes and repeated IQM, skin and manifest builds are identical.
  See `determinism-collapse-final.json`, `cage-revised.log`, `cage-second.log` and
  `canonical-build.log`. Blend-file byte determinism is not claimed.
- Isolated Blender 5.2.1 freshly reopened the final source, six Actions, packed
  skin and zero linked libraries. Eighteen sampled source/runtime poses agree
  within **0.00001971** units (`blender-collapse-final-verification.json` and
  `blender-collapse-final.log`). No live Blender document or global setting changed.
  The existing extension-cache permission warning is nonfatal.
- Both final galleries contain **34 actual 1920x1080 engine captures**: static
  before, sampled clips, four angles and 64/128/192-unit distances. Both contact
  sheets and representative full-size angle/action/death views were inspected.
  Every gallery subject reports `blocking=0`; both engines exit zero without
  new model/resource errors. Existing menu/minimap warnings remain.
- The two final PK3s are byte-identical, and **all 1,142 entries** match current
  source bytes, not only the ogre model. See `package-collapse-final-verification.json`.

```text
IQM  a6f3e3dc13729d3b29025f64e04594ca51e3889082ea94d1383af046ea047296
PNG  3d9a922dd7e1ffe3056fe8e6f9d80b42f4d3e9eae9df342d00c3799618a4bf16
Cage 22fc8d6ba65a90fb295bad68a757f830a05caf0cb93e7bdbe27619a41b681280
PK3  40376a311e6d4a5ae54b55b3aeac527c58cf61f5ef21a6256a293b88bab2d7a8
```

## Natural captive encounter and acceptance limits

`review_ogre.py` replays seed **169**, **247 ordinary intents**, reaching depth5,
turn243, player28,23, HP6/30 and hash **06838c74a89fe52e**. Existing ogre ID99
stands at31,23 with4/55HP, direct visibility2, ally=false and captive=true.
The copied headless bookkeeping flags are4202817, including `MB_CAPTIVE` bit256.
Repeated headless routes are identical. The eye-level observer only aims at
the existing directly visible proxy; no spawn, reveal, health or position
override is used. It leaves Brogue's normal captivity presentation unchanged.

One further ordinary E intent reaches player29,23, turn244 and HP0, hash
**f0669490064171d2**. The ogre remains captive with4HP. Nearby goblins are shown
attacking, but this is **not ogre attack or ogre death proof**. Final evidence is
`natural-collapse-vulkan/` and `natural-collapse-opengl/`, using the exact final packages.
Both captures show the actual HUD turn/HP and copied `brg_monsters` flags.
The startup campaign is generated from ordinary seed169 Brogue output;
`review_campaign.missing_depth_mapinfo` supplies only any absent depth metadata.

Natural hostile locomotion, stagger attacks, hits, death and captive release
remain unverified. Physical keyboard play, standalone side-by-side comparison,
controlled frame-time measurements, full release-installer packaging and user
art approval are also open. Gallery poses and this captive encounter do not
close those gates. No gameplay, ABI, collision, AI, RNG or visibility logic changed.

Reproduce the final renderer checks with:

```powershell
python -m tools.monster_models.review_skeletal --symbol MK_OGRE --backend 1 --all-angles --distances --packaged --width 1920 --height 1080 --output artifacts/creature-queue/BRG-M18/reproduction-vulkan
python -m tools.monster_models.review_ogre --backend 1 --package artifacts/creature-queue/BRG-M18/reproduction-vulkan/ProjectBroom-review.pk3 --output artifacts/creature-queue/BRG-M18/reproduction-natural-vulkan
```

Use backend0 and fresh output directories for OpenGL.

## Preservation and handoff

The immediate narrow baseline contains 1,454 files: **1,445 byte-identical**,
nine intended shared changes and **zero missing files** (`preservation.json`).
All 18 prior skeletal profiles, all 67 other bestiary entries and all 67 other
creature cards are preserved. The goblin-conjurer card's mixed newline bytes
were restored to its exact pre-task SHA, not merely normalized text. No queue,
transition barrier, wall-mount helper, gameplay source or visibility code changed.

Shared changes are the ogre connected-skin selector and bestiary traits,
skeletal/bestiary/monster registries, K18 card, and generated MODELDEF, ZScript
and native table. The generated creature-model index also updates outside the
narrow hash inventory. Coordinator handoff documentation changes are unrelated.
No reset, cleanup, commit or publication was performed.

Reusable lesson: preserve original card bytes before regeneration, including
mixed line endings. Fuse anatomical topology before creating continuous skin
pigment; transferring blockout UV patches alone creates visible triangles.
Test every centered min/max bound, reachable/planted feet and zero floor
compensation. Natural captivity flags and copied turn/health bound what a
capture can prove. Technical review is not user art approval.

[Final Vulkan gallery](../artifacts/creature-queue/BRG-M18/final-collapse-vulkan-contact.jpg),
[final OpenGL gallery](../artifacts/creature-queue/BRG-M18/final-collapse-opengl-contact.jpg),
[natural captive view](../artifacts/creature-queue/BRG-M18/natural-collapse-vulkan/captive-encounter.png).

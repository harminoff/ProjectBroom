# Bog monster model and animation

The coordinator losslessly archived the review packages after verification.
Before replaying the final Vulkan fixture, restore its exact package bytes:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M19/clearance-vulkan/ProjectBroom-review.pk3.archive.json
```

Use the corresponding `clearance-opengl` manifest for OpenGL. All screenshots,
logs and archive segments remain available.

Presentation-only BRG-M19 / MK_BOG_MONSTER. Brogue CE remains authoritative.

## Source and planned proof

Brogue describes a horrifying creature beneath mud-filled swamps with pale
tentacles that ensnare and squeeze prey. Liquid restriction, submersion, fleeing,
flitting and seizing are source-owned. This change adds no gameplay, spawn,
health, trail, collision, AI, RNG or ABI. Existing copied visibility controls
whether the proxy is shown.

Art interpretation: a low buried fleshy mantle, six asymmetric tapering curled
arms, underside gripping folds and fine mottled ivory/pink tissue stained brown
at the mud line. No invented eyes, jaws or glowing magic. Six cosmetic roles:
idle, drift, squeeze, coil, recoil and collapse. Numerical size and anatomy are
art decisions. Original Project Broom artwork, CC-BY-SA-4.0.

Planned proof: connected closed skin, normalized weights, all-frame bounds and
seam integrity; repeated deterministic cage/IQM/skin builds; isolated Blender
fresh reopen and sampled deformation; native compile; packaged 1920x1080
Vulkan/OpenGL clip/angle/distance galleries; bounded ordinary-intent encounter
attempt. Existing seed1–2000 searches did not obtain a visible encounter;
fixtures will never be represented as natural encounters. Art approval, manual
play and exhaustive natural-event acceptance remain separate gates.

## Delivered source and final model

The final model is one closed connected organic skin: 3,174 runtime UV-split
vertices, 5,600 triangles, 38 bones (root, mantle and six six-bone arm chains),
and six clips. Only idle/drift loop. The deterministic connected cage carries
normalized weights with at most four influences and coincident seam weights.
Rest dimensions are 50.9048 x 49.9174 x 29.9561 units. All sampled animation
frames now stay inside the centered cell: X -27.3746 to +31.8690,
Y -28.6123 to +29.6111, with minimum Z 0.09163. The anatomy and rig use a
consistent 0.93 presentation scale. An earlier width-only check missed an
off-center collapse reach; final tests explicitly require every frame to remain
inside +/-32 on both horizontal axes.

- Master: `tools/monster_models/bog_monster_animation.py`.
- Cage: `assets/monsters/bog_monster/connected-skin.json.gz`.
- Editable source: `assets/monsters/bog_monster/bog-monster-animated.blend`.
- Manifest: `assets/monsters/bog_monster/animation.json`.
- Runtime: `mod/BrogueDoom/models/monsters/19_bog_monster.iqm`.
- Original 1024-square diffuse: `mod/BrogueDoom/graphics/BRGBOG.png`.
- Specific checks: `tools/monster_models/test_bog_monster.py`.
- Synthetic mud review: `tools/monster_models/review_bog_monster.py`.

The first gallery exposed spike-like tips and overly uniform pale faces. The
refinement curls the tips inward, uses nearly round 0.98 cross-sections with
thicker distal tissue, and strengthens fleshy folds and rose/ivory mottling.
A rest-height pigment coordinate keeps the mud stain continuous through the
fused mantle/arm geometry instead of terminating at source-part UV islands.
These are art changes only. There are no eyes, teeth, weapons, emission,
particles, autonomous tentacle targets or authoritative grabbing rules.

**Art limitation:** the central mantle junction still reads faceted/patchy in
close-up, including the synthetic mud view. The material/normal transition is
visually apparent despite connected manifold topology and equal seam weights.
It is not hidden by claiming mud occludes it. User art approval remains open.

## Final verification

Evidence is `artifacts/creature-queue/BRG-M19/`. The **clearance** files below are
the final revision; older `vulkan`, `final-vulkan`, `accepted-vulkan` and similar
folders are intermediate evidence, not art approval or final hash evidence.

- **53 tests passed**, 102.267 seconds (`tests-clearance.log`):
  `python -m unittest tools.monster_models.test_bog_monster tools.monster_models.test_skeletal tools.monster_models.test_connected_skin tools.monster_models.test_creatures tools.test_broguedoom_resources`.
  Creature checks prove one closed connected cage spanning all six arms,
  normalized weights and equal UV seam geometry/weights, looping/recovery,
  unit bone scales, every-frame floor/cell bounds, death settling and exact
  runtime/texture bytes. They do not prove exhaustive self-intersection freedom.
- Native Release compilation passed:
  `python tools/run_native.py cmake --build .build/uzdoom --config Release -j4`
  (`native-compile.log`). The build fingerprint was refreshed only afterward.
  The generated K19 clip-table row is the only native change; subsequent art
  refinement does not change that row or the native executable contract.
- Isolated background Blender 5.2.1 freshly reopened the final source, six
  Actions, packed texture and no linked libraries. Eighteen source/runtime
  pose comparisons had maximum vertex error **0.000006965** units. See
  `blender-clearance.log` and `blender-clearance-verification.json`. No live Blender
  document was replaced. The known extension-cache warning is nonfatal.
- Two cold single-thread cage bakes and repeated final IQM, PNG and manifest
  builds are byte-identical (`clearance-determinism.json`). Blend file byte
  determinism is not claimed.
- `clearance-vulkan/` and `clearance-opengl/` each contain **34 actual 1920x1080
  engine captures** covering static before, all six sampled clips, front/side/
  rear views and 64/128/192-unit distances. Both complete contact sheets and
  representative full-size views were inspected. All 34 subjects per backend
  report `blocking=0`. Both runs exit zero with no new model/resource error;
  existing menu/minimap warnings remain.
- Both deterministic runtime PK3s have identical hashes and match the current
  IQM, diffuse, MODELDEF and ZScript source. See
  `clearance-package-verification.json` (including GLDEFS). The parent
  independently confirmed the same bytes in
  `parent-clearance-package-verification.json`.
- `clearance-mud-vulkan/` and `clearance-mud-opengl/` each contain six additional
  1920x1080 captures: 64/128/192-unit views, hidden, sensed and coil. This
  **synthetic renderer fixture** uses a -4-unit mud bed, opaque brown surface,
  nonblocking proxy and explicit display states. Hidden shows no creature;
  sensed shows the shared translucent treatment. It never calls Brogue
  visibility logic and proves neither natural visibility nor seizing behavior.

```text
IQM 9fcae20a75d70efbef488286429a778c04a9eeea052cc24d61862ef91e6213ec
PNG 4de5d289656ba15fce92e514f6753cfa6822331cd00a50d5ce4c9f0967bd05bc
PK3 447a8f8bce5c0aabeeea09dfe8328766ce7a5bb04823e55c0d0e2eae43cdd26a
```

Reproduction (substitute backend 0 and a fresh output folder for OpenGL):

```powershell
python -m tools.monster_models.bog_monster_animation
python -m tools.monster_models.review_skeletal --symbol MK_BOG_MONSTER --backend 1 --all-angles --distances --packaged --width 1920 --height 1080 --output artifacts/creature-queue/BRG-M19/clearance-vulkan
python -m tools.monster_models.review_bog_monster --backend 1 --package artifacts/creature-queue/BRG-M19/clearance-vulkan/ProjectBroom-review.pk3 --output artifacts/creature-queue/BRG-M19/clearance-mud-vulkan
```

## Natural encounter attempt and open gates

**No natural bog-monster encounter was obtained.** The coordinator's existing
standard-route search covered seeds 1-2000, 1,500 actions/depth 15, without a
visible encounter. It was not repeated. The source first horde range is 7-14
with `HORDE_NEVER_OOD`, making early-floor captures unsuitable evidence.

A bounded artifact-only route experiment adds all eight ordinary movement
intents, using copied diagonal blockers on both flank cells and retaining
hazard avoidance. Brogue validates every action. It changes no source-game
health, spawn, reveal, RNG or topology. It can read diagnostic copied hidden
map knowledge and is not a claim of human exploration.

`diagonal-search.json` records 52 attempts (seed1849, seed26 and seeds1-50),
each capped at 1,500 actions/depth15. None found a directly visible bog monster.
Seed1849 died at depth8 after401 actions; its output repeated identically.
Seed24 stopped at depth8 after380 actions with27HP; seed27 stopped at depth7
after279 actions with13HP. A focused ordinary-confirmation experiment on
these three seeds showed the surviving routes blocked with no target present,
not a confirmation prompt. See `diagonal-confirm-search.json` and
`natural-attempt-verification.json`. The coordinator's earlier cardinal
seed1849 route reached depth9 before death; the new route does not improve it.

Natural appearance, mud surfacing/submersion, attacks, seizing, fleeing/flitting,
hits and death remain unverified through a live Brogue encounter. Manual
input/play, standalone side-by-side comparison, controlled frame-time testing,
full release-installer packaging and user art approval also remain open.
The package/gallery and synthetic mud fixture do not close these gates.

## Preservation and reusable lessons

The immediate narrow baseline has 1,446 files: **1,437 byte-identical**, nine
intended shared changes and **zero missing files** (`preservation.json`). All
17 prior skeletal profiles, all 67 other bestiary entries and every other
creature card remain unchanged. Static bog-monster OBJ/skin/Blend references
remain unchanged. No queue/coordinator, transition barrier, wall-mount,
frontend visibility, bridge ABI or gameplay source edits were made.

Shared changes are the new connected-skin selector, bog traits in bestiary,
profile/bestiary/monster registry, K19 card and generated native table,
MODELDEF and ZScript. The generated `docs/creature-model-index.md` is also
updated outside that narrow hash inventory. The root coordinator separately amended
`docs/creature-agent-handoff.md`; that is unrelated coordinator work.

For future tentacle anatomy, inspect multiple angles before concluding a pale
surface is geometrically flat; near-round sections can look like ribbons in
uniform ambient light. Use stronger tissue pigment and modest fold relief,
and avoid source-part UV transitions at fused junctions. Connected topology
is necessary for skin integrity but does not itself prove a polished junction.

[Before/after](../artifacts/creature-queue/BRG-M19/before-after.png),
[Vulkan gallery](../artifacts/creature-queue/BRG-M19/clearance-vulkan-contact.jpg),
[OpenGL gallery](../artifacts/creature-queue/BRG-M19/clearance-opengl-contact.jpg),
[synthetic mud](../artifacts/creature-queue/BRG-M19/clearance-mud-vulkan/one-cell.png).

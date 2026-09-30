# Ogre shaman model and animation

Presentation-only BRG-M27 / MK_OGRE_SHAMAN. Brogue CE remains authoritative.

## Source facts and planned proof

Brogue describes an ogre bent with age whose lost physical strength is outweighed by occult power. Its existing verbs are cudgels and clubs; its summon message says it chants in a harsh, guttural tongue. Haste, spark, summoning, distance preference, corridor avoidance, turns, RNG and all outcomes remain Brogue-owned. No gameplay, AI, collision, damage, spawn, visibility or bridge ABI change.

Original art interpretation: recognizable heavy ogre anatomy narrowed by age. It has a pronounced dorsal hump and forward stoop, a head thrust ahead of the shoulders, bent knees, thin knobbly arms above a sagging paunch, and big flat feet. The face has a low cranium, a heavy overhanging brow, a hooked bulbous nose, sagging jowls, deep-set rheumy yellow eyes, chipped lower tusks, long drooping ears with bone rings, grey brows and moustache, a long divided beard with beads, and a scalp braid. The shaman wears a mossy hide mantle with a fur yoke over the hump and upper arms, a tooth-and-claw necklace, a tattered hide loincloth, a rope belt with a pouch and a small skull fetish. The skin is aged olive-brown with liver spots, and is marked with ash-and-ochre ritual paint: a band across the eyes, forehead dots, a painted eye on the paunch and forearm bands. The shaman holds a crooked forked staff taller than itself, with bound grip and crown lashings, a lashed animal skull, horns, fangs, dangling bone charms and feathers.

The staff, relics and paint emit no light and add no particles, collision or power. The glyph green is a muted identity cue, not literal whole-body paint. Six cosmetic roles are idle, hobble, cudgel, chant_strike, recoil and collapse. Only idle and hobble loop. The planned proof was completed as recorded below.

All new art is original Project Broom content under CC-BY-SA-4.0; no third-party artwork was imported.

## Delivered artwork and rendering

- Master geometry, poses and IK are in `tools/monster_models/ogre_shaman_animation.py`. The original textures are in `ogre_shaman_materials.py`.
- Runtime files are `mod/BrogueDoom/models/monsters/27_ogre_shaman.iqm` and the 2048-square `mod/BrogueDoom/graphics/BRGOGSH.png`.
- Manifest and cage are `assets/monsters/ogre_shaman/animation.json` and `connected-skin.json.gz`. The editable packed source is `assets/monsters/ogre_shaman/ogre-shaman-animated.blend`.
- The static `27_ogre_shaman.obj`, `BRGM27.png` and `sources/27_ogre_shaman.blend` references are byte-unchanged.
- There are 20 bones, 119 source parts, 34,331 runtime vertices, 27,234 triangles and six clips. The bones are root, pelvis, spine, chest, neck, head, jaw, two 3-bone arms, two 3-bone legs and staff.
- The closed connected skin (3,891-vertex cage, 7,798 faces) carries the torso, hump, head, face, nose, jowls, jaw, ears, shoulders, arms, elbow and knee knobs, hands, fingers, legs, heels and toes. Eyes, tusks, teeth, hair, nails, clothing, relics and staff are separate accessories.
- Rest extents are 30.88 x 41.22 x 76.39 units, with the staff crown the highest point. These are artistic dimensions.
- Every frame of every clip stays within X -24.08..30.27 and Y -30.33..23.38. Minimum Z is 0.2198.

The previous agent's scaffold was an ogre clone. Its aged look came from a global warp, and it failed its floor check at exactly the 0.07 threshold. It was replaced rather than patched.

The torso is now lofted along a bent spine path with separate belly and back depths. The mantle is offset from the sampled torso profile, so it hugs the hump. Every pose is solved with two-bone IK in the parent's frame. Soles stay level and planted, knees are driven by an explicit forward/outward pole, and the staff is oriented in world space with the fist fixed around it. The staff axis passes exactly through the closed fist: four curled fingers and a thumb wrap more than 300 degrees.

- **Hobble:** the staff is planted and swung with the opposite leg on a 60% stance / 40% swing gait.
- **Cudgel:** the shaman rears back with the staff over the shoulder, then lunges and chops the crown forward within the cell.
- **Chant_strike:** the head tilts back, the jaw works open and closed, the left palm rises and the staff lifts, followed by a short crown jab. This is a melee variant: the native selector alternates attack clips by event sequence. It is not proof of spell timing.
- **Collapse:** the knees buckle to the floor with the feet laid behind, the torso folds forward with a sideways slump, the head drops and the jaw hangs open. The left hand comes to rest on the floor. The limp right fist keeps its grip, and the staff topples about its tip to rest diagonally across the right knee and left haunch. The body's final maximum height is 37.9 units.
- **Floor clearance:** no clip uses automatic whole-root floor lift. Every exported frame equals its raw pose.

The skin atlas is painted from continuous rest-position coordinates, evaluated on a four-step barycentric lattice per triangle. It is not taken from source-part UVs, so fused joints have no colour seams. Paint is placed using surface normals and appears only on front surfaces.

Authoring note: coordinates are quantised to 1e-6 because Python 3.12's more accurate float `sum()` made Blender's bake fingerprint differ from system Python's. `blender_skin.py` gained an optional per-enemy face budget: 7,800 for the shaman, with the unchanged 5,600 default for every other creature, so earlier bakes are byte-identical.

Early engine review drove these fixes:

- A painted bullseye on the paunch read as an archery target; it was replaced by a weathered painted eye. `early-vulkan-contact.jpg` is the only kept iteration sheet.
- Skin was too uniformly mint; warm weathered blotches and a darker olive base were added.
- A striped fur collar and hair wisps read as horns; they were replaced by fur tufts and two short locks per side.
- The ears were lowered and shrunk.
- The cudgel roll was changed after the shaft crossed the face.
- The chant timing was moved so its ritual peak is the sampled mid-frame.

## Tests

**56 tests passed in 346.378 seconds** (`final-tests.log`):

```powershell
python -m unittest tools.monster_models.test_ogre_shaman tools.monster_models.test_skeletal tools.monster_models.test_connected_skin tools.monster_models.test_creatures tools.test_broguedoom_resources
```

The seven ogre shaman tests cover:

- a closed, single-component connected skin with seam equality and at most four normalised weights;
- six ordered roles and loop rules, every frame inside the centred ±32 cell with minimum Z above 0.07, and raw frames equal to exported frames (zero floor compensation);
- unit scales, loop closure, and action recovery back to rest;
- an unchanged staff bone in every frame, fingers wrapping more than 300 degrees around a centred staff axis;
- both soles planted and level in idle, attack and recoil, and at least one planted while hobbling;
- a limp collapse: head, left hand and knees low, jaw open, body below 40 units, staff tip on the floor and crown lowered;
- front-only paint placement and accessory UV isolation;
- exact runtime IQM and texture bytes.

The first combined run failed one assertion. Its staff-centre check averaged tube-ring vertices that repeat their seam vertex, which biased the result by 0.09 units. The measurement was corrected to use unique vertices; the geometry was unchanged. That run is kept as `pre-final-tests-centroid-bias.log`.

## Frozen-byte verification

Evidence is under `artifacts/creature-queue/BRG-M27/`.

- **Determinism:** two separate single-thread cold connected-skin bakes and runtime exports reproduced the cage, manifest, IQM and diffuse byte-for-byte (`final-determinism.json`, `prove-determinism.py`). Blend-file byte determinism is not claimed.
- **Blender source:** isolated background Blender 5.2.1 rebuilt the source (`final-blender-build.log`). A separate fresh process reopened it and verified 20 bones, six Actions, 18 sampled poses, exact packed skin bytes and no linked libraries (`final-blender-verification.json`). The maximum vertex difference was 0.0000234 units. The known extension-cache warning was nonfatal. No live Blender document or global setting was touched.
- **Native build:** `python tools/run_native.py cmake --build .build/uzdoom --config Release -j4` passed (`native-build.log`). The fingerprint was recorded after linking and then validated (`final-native-fingerprint.json`). Only the generated kind27 profile row changed native input.
- **Galleries:** `final-vulkan/` and `final-opengl/` each hold 34 actual 1920x1080 packaged captures. They cover the static before view, all six clips, front/side/rear/oblique views and the 64/128/192-unit distances. Every stage reported `blocking=0`.
- **Runtime warnings:** the only warnings are the pre-existing minimap script and menu-texture warnings.
- **Packages:** both packages are identical, and all 1,172 entries equal current source (`final-package-verification.json`).

```text
IQM e84bb9f633a35f9f3e09f1f5b16f165afa71f7171086af4f2ba1d08d6321e5b3
PNG fa5e5da60cdf7f0ec28267ccce28bfd1679b466eb6954c66ae1b528a31280c66
PK3 824daebf4f9d144eb77b259119e668086c1aa7deced0281c1c2076c992685fb1
```

[Final Vulkan gallery](../artifacts/creature-queue/BRG-M27/final-vulkan-contact.jpg), [OpenGL gallery](../artifacts/creature-queue/BRG-M27/final-opengl-contact.jpg).

Residual visual flaws, stated honestly:

- The attack clips are restrained: a 76-unit staff must stay inside the ±32 cell, so the forward chop reads modestly from oblique views.
- The dark mantle can read as a shell from the rear three-quarter view.
- The corpse is a kneeling forward fold, whose hump dominates the silhouette. The staff intersects the left haunch where it rests.
- Beard and hair strands are rigid to the jaw and head.
- Engine lighting makes the olive skin read greener than intended.

## Remaining acceptance

No natural ogre shaman encounter was obtained. The completed 1–2000 seed conservative census contains no kind27, and the ordinary horde range starts at depth 14, beyond what that route reached. The unchanged search was not repeated, and no spawn, reveal, health or action override was introduced (`natural-encounter-status.json`). The gallery poses do not prove native attack, hit, death, haste, spark or summon event synchronisation.

Still open: natural lifecycle, physical play, standalone comparison, frame-time benchmarking, release packaging and individual user art approval.

## Reproduction

```powershell
python -m tools.monster_models.ogre_shaman_animation
python -m tools.monster_models.review_skeletal --symbol MK_OGRE_SHAMAN --backend 1 --packaged --all-angles --distances --width 1920 --height 1080 --output artifacts/creature-queue/BRG-M27/reproduction-vulkan
```

Use backend 0 with a separate output directory for OpenGL. Rebake the cage with isolated `--threads 1` Blender and `tools/monster_models/blender_skin.py -- ogre_shaman`. Build the source with `blender_skeletal.py -- MK_OGRE_SHAMAN`.

## Preservation

The immediate raw-byte baseline from the start of this task covered 1,560 files. The final audit shows 1,550 unchanged, 10 intended changes, zero unexpected and zero missing (`preservation.json`).

- All 30 previous skeletal profiles and the other 67 bestiary and monster-registry entries are unchanged, as are the registry headers.
- The only line change in the model index is the BRG-M27 row.
- Regeneration normalised eight other creature cards (09, 10, 11, 18, 20, 21, 28, 29). They were restored from the raw pre-task byte copies, not from git HEAD.

Shared changes:

- the shaman selector in `connected_skin.py`;
- the optional face budget in `blender_skin.py` (pre-edit copy kept in `baseline-bytes/`);
- the kind27 profile row;
- the regenerated MODELDEF, ZScript, native header, monster registry, bestiary entry, card and model-index row.

The native frontend, bridge, queue files and REVIEW.md were not edited. No cleanup of others' files, commit or publication was made, and the next creature was not started.

## Coordinator package archive

Both final review packages (`824daebf4f9d144eb77b259119e668086c1aa7deced0281c1c2076c992685fb1`, 1,172 entries) were independently compared entry-by-entry with current source (`parent-final-package-verification.json`) and losslessly archived after final image inspection. Restore the exact Vulkan package with:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M27/final-vulkan/ProjectBroom-review.pk3.archive.json
```

Use the equivalent final-opengl manifest for that backend. Captures, logs, manifests and shared content blobs are retained.

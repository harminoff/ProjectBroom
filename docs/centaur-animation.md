# Centaur model and animation

Presentation-only BRG-M35 / MK_CENTAUR. Brogue CE remains authoritative.

## Source facts and planned proof

Brogue describes the centaur as half man and half horse, an expert with the bow and arrow: hunter and steed fused into a single creature. Its catalog row gives `BOLT_DISTANCE_ATTACK`, `MONST_MAINTAINS_DISTANCE`, `MONST_MALE`, `DF_RED_BLOOD`, the large flag and the tan glyph colour. Its attack verb is "shoots". The ranged bolt, distance keeping, targeting, turns, damage, RNG and every outcome remain Brogue-owned. There is no gameplay, AI, collision, damage, spawn, visibility or bridge ABI change.

Planned art interpretation (written before implementation):

- A compact light-horse body: barrel, deep chest, sloping croup, a four-jointed foreleg, and a hind leg with a forward stifle and a backward hock. It has hooves, feathered fetlocks and a long tail.
- The horse body is joined at the withers to a lean male archer's torso through one connected skin, with continuous pigment across the join.
- The coat is tan/dun, an identity cue from the glyph colour rather than whole-body paint.
- The archer holds a short composite recurve bow in the left hand. Its separate string stays attached to both limb tips. He carries a back quiver of fletched arrows on a strap, and wears a leather bracer.
- Exact breed, clothing and ornaments are art choices.

Planned roles are idle, gait, shoot, a second shot variant, flinch and death. Only idle and gait loop. The nocked arrow is cosmetic only: it resolves nothing and spawns no projectile, light or particle. The death should read as a fallen horse lying on its side with a limp human torso, not a kneel.

Planned proof:

- every exported frame inside the centred ±32 cell, with minimum Z above 0.07 and no automatic floor compensation;
- planted, level, non-sliding support hooves and reachable IK;
- the bow grip and string attachment checked in every frame;
- a closed, single-component connected skin with seam equality;
- engine inspection from front, profile, rear and oblique views;
- two identical cold bakes and exports, and a fresh Blender reopen;
- the native build and both packaged galleries;
- a preservation audit.

All of this was carried out as recorded below.

All new art is original Project Broom content under CC-BY-SA-4.0. No third-party artwork was imported.

## Delivered artwork and rendering

- Master geometry, rig, IK and poses: `tools/monster_models/centaur_animation.py`. Original textures: `centaur_materials.py`.
- Runtime files: `mod/BrogueDoom/models/monsters/35_centaur.iqm` and the 2048-square `mod/BrogueDoom/graphics/BRGCTR.png`.
- Manifest and cage: `assets/monsters/centaur/animation.json` and `connected-skin.json.gz`. The editable packed source is `assets/monsters/centaur/centaur-animated.blend`.
- The static `35_centaur.obj`, `BRGM35.png` and `sources/35_centaur.blend` references are byte-unchanged.
- There are 39 bones, 171 source parts, 45,948 runtime vertices, 31,064 triangles and six clips.
  - Equine bones: root, pelvis (hindquarters), barrel and withers.
  - Human bones: waist, chest, neck and head.
  - Two 3-bone arms.
  - Four 4-bone legs: scapula or hip, then elbow/stifle, knee/hock and fetlock.
  - Four tail bones.
  - Bow bones: bow grip, top and bottom limb bones and a string bone.
  - One arrow bone.
- The closed connected skin (5,800-vertex cage, 11,600 faces, one component) carries:
  - the horse trunk and the human torso, pectorals, ribcage, lats, neck muscles, trapezius, deltoids, arms, biceps, triceps, palms and left fist;
  - the head and face;
  - the scapula, breast, thigh and buttock masses, and the leg segments down to the pasterns;
  - the tail dock.
- Separate accessories:
  - the right hand's curled fingers and thumb;
  - eyes, eyelids and lash lines;
  - combed hair locks, bun, beard shell and tufts, sideburns, brows and moustache;
  - the withers mane, hooves, fetlock feathering and tail locks;
  - the bracer, quiver, strap, arrows and bow.
- Rest extents are 55.0 x 28.6 x 76.4 units. These are artistic dimensions, not Brogue measurements.
- Every frame of every clip stays within X -31.34..30.20 and Y -31.22..30.70. Minimum Z is 0.093.

### Construction

- **Joined anatomy:** the horse trunk is a squared superellipse loft. The human torso is lofted up a gently bent path starting inside the horse's chest, so the two bodies meet at the withers as one fused volume. Skin weights run along the chain withers, waist, chest, neck and head.
- **Legs:** the leg segments use rigid weighting with blending only near each joint, which keeps the equine joints crisp.
- **Coat and skin:** the atlas is painted from continuous rest coordinates. Each triangle is evaluated on a four-step barycentric lattice. Coat and skin are blended by the continuous per-vertex human-bone weight fraction, not by source-part UVs, so the waist join has no patches.
  - The dun coat has countershading and muscle form: lit shoulder, barrel, haunch and croup; shadowed triceps line, stifle fold, elbow pit, chest groove and quarter groove; faint ribs.
  - Fine hair-flow lines run back along the body and down the legs.
  - Dun markings: a dark dorsal stripe from the withers into the tail, a shoulder bar, darker dun shading over the upper withers, dark stockings above knee and hock with faint barring, and a pale coronet band.
  - A dark crest of hair marks the waist where coat meets skin, heaviest over the back.
  - The skin is a warm tan with pectoral, rib, abdominal, collarbone, brow and lip shading, and stubble.
- **Face:** a heavy brow ridge, bridge and nostril wings, cheekbones, upper and lower eyelids and lash lines, and dark-brown irises. The hair is eleven combed-back locks gathered into a bun over a scalp shell whose fibres radiate from the crown. The short beard is a shell with fibres radiating from the chin, with thirteen broken tufts along the jaw and sideburns.
- **Bow:** a lacquered recurve with horn tips, a cord-wrapped grip and an arrow rest. The left fist wraps the grip axis by more than 300 degrees. The limbs flex through their own bones. The string is two segments whose ends are fully weighted to the limb bones and whose centre is weighted to the string bone. Its rest brace is 2.9 units.
  - In every rest pose the bow is carried low at the side, top limb tipped forward and canted outward, clear of the face. One shared carry helper keeps the clips continuous.
- **Quiver:** a tooled leather quiver with red bands carries six arrows, plus the drawable seventh in slot 0. Its strap runs from the mouth over the right shoulder, across the chest and back under the left arm.

### Clips

- **Idle:** the rider breathes and turns his head, and the tail sways. Mid-cycle the weight shifts off the right hind, which rests on its toe.
- **Trot:** a two-beat diagonal gait with a 56% stance, fetlock curl in swing, counter-bob, and the bow carried steady. It is 32 frames long.
- **Shoot:** the timeline runs as follows:
  1. The right hand reaches over the shoulder and pulls the slot-0 arrow from the quiver.
  2. The rider nocks it on the string.
  3. The horse rocks back over planted hooves, and the rider leans back and turns partly side-on.
  4. The draw brings the nock to an anchor under the right cheek, and the limbs flex.
  5. The rider holds, looses, the bow wobbles, the hand follows through, and the pose settles.

  While the arrow overhangs, the bow is pitched down. It levels only as the draw brings the nock back, so the cosmetic arrow tip never leaves the cell.
- **Rear_shot:** the same draw, with the forehand half-rearing (forelegs folded and pawing) and a slightly downward aim. The native selector alternates attack clips by event sequence; this is not proof of shot timing.
- **Flinch:** the horse shies back and sideways over planted hooves, the rider recoils, the bow arm pulls in and the tail clamps.
- **Fall:**
  1. The knees buckle over planted hooves (IK) while the rider slumps.
  2. The horse rolls 84 degrees onto its right side along a descending path. It rests on its right flank and thigh with loosely folded legs; the upper legs droop onto the lower ones.
  3. The rider folds forward and sideways to the floor in front of the chest, and his head lolls onto the floor.
  4. The left fist still holds the bow, which lies slanted from the hand to the floor.

  The final height is 25.7 units. The pose was fitted numerically so that every vertex stays in the cell and above the floor during the whole roll.
- **Floor clearance:** no clip uses automatic floor lift. Every exported frame equals its raw pose.

The cosmetic arrow leaves the quiver in the hook, rides the string, and on release returns to its quiver slot as "the next arrow". It spawns nothing and implies no hit.

### Review iterations

`early-vulkan-contact.jpg` is the only kept iteration sheet.

The first engine review drove these fixes:

- The coat was too pale. It became a warmer dun.
- The crease paint read as scars and was softened.
- The beard read as a muzzle.
- The tail root stood proud of the croup.
- The head tilted up at full draw.
- The upper legs stuck up in the death pose.
- The bow was canted outward.
- The first build also overwrote the centaur's skin onto the centipede's existing `BRGCENT.png`. The centaur skin was renamed `BRGCTR.png`. The centipede texture was regenerated deterministically and verified equal to its baseline SHA-256.

The coordinator review of the first delivery asked for a focused refinement, which was carried out and inspected in-engine before this final gate:

- **Detail budget:** the per-triangle atlas had capped the fused skin at 8,192 faces, and decimating to that budget flattened the shoulders and face. The centaur atlas now places skin islands in the left half and the previously unused bottom-right quadrant: 12,288 islands at the same 16-pixel density. Accessories keep the top-right quadrant. `blender_skin.py` gives only the centaur an 11,600-face budget; the default and every other creature's bake are unchanged.
- **Upper body:** rounded deltoid caps seated into widened upper-torso rows, front deltoid heads, a gentle trapezius slope and neck muscles. The pectorals and ribcage flare, and the lats narrow into the waist. The upper arm gained triceps, and the elbows now hang closer to the torso. The woad band (the blue fleck on the left shoulder) was removed.
- **Right hand:** separate, slightly curled and spread fingers with knuckles and a thumb replace the fused mitten.
- **Face:** heavier brow, cheekbones and nose, and eyelids with lash lines instead of near-black socket shells. Combed locks replace the striped cap, and a radiating-fibre beard with broken tufts replaces the concentric-striped shell.
- **Coat:** a clearer dorsal stripe, darker and higher points, a withers mane and waist crest, muscle shading and hair flow. The first hair-flow pass read as wood grain and was reduced.
- **Skin tone:** the first warmer skin was too pink and was pulled back to a warm tan that still separates from the coat. This fixed the existing join test honestly rather than loosening its 20-unit threshold.
- **Idle bow:** carried 4 units lower, tipped forward 8°.
- **Dead rider's head:** lowered onto the floor.
- **Determinism:** Blender's Python 3.13 and system Python 3.11 differed by a 2e-16 residue in one chain weight, which made one vertex produce `1` versus `1.0`. Skin weights are now quantised to 1e-6, with the final influence taking the exact complement and a single influence normalised to `1`. Both interpreters now produce identical bake fingerprints for every part.

## Tests

**57 tests passed in 433.381 seconds** (`final-tests.log`):

```powershell
python -m unittest tools.monster_models.test_centaur tools.monster_models.test_skeletal tools.monster_models.test_connected_skin tools.monster_models.test_creatures tools.test_broguedoom_resources
```

The eight centaur tests cover:

- **Connected skin:** a closed, single-component connected skin with seam equality and at most four normalised weights. All arm and leg joints, the trunk, the human bones and the tail are carried by the one skin, within the 12,288-island atlas capacity.
- **Roles and clearance:**
  - six ordered roles with loop rules, and every frame inside the centred ±32 cell with minimum Z above 0.07;
  - raw frames equal to exported frames, unit scales and loop closure;
  - action recovery back to rest.
- **Hooves:**
  - planted hooves are level;
  - in idle, shoot and flinch they are also non-sliding, at their exact rest position;
  - four are planted in shoot and flinch, both hinds in rear_shot, and at least three in idle (all four at its start);
  - trot keeps at least two planted, with diagonal pairs moving together.
- **Bow:**
  - the bow bone is fixed in the fist in every frame, and the fingers wrap more than 300 degrees;
  - both string ends stay within one unit of their limb tips in every frame of every clip.
- **Arrow:**
  - the arrow and string are at rest before the grab and after the release;
  - during the draw the arrow nock is on the string and its tip stays inside the cell;
  - full draw reaches the cheek anchor.
- **Fall:** the horse lies on its right side, with the barrel, head and both hands low and the body below 30 units. The bow lies nearly flat, and every hoof is off its standing support (not a kneel).
- **Pigment:**
  - dark leg points, a dorsal stripe, and a join that changes by more than 20 without any step above 40;
  - UV isolation, with accessories exclusively in the top-right quadrant.
- **Bytes:** exact runtime IQM and texture bytes.

The two test edits in the refinement are exact replacements for the new atlas layout, not relaxations:

- The face-count check moved from a fixed 8,192 to the new 12,288-island capacity.
- The UV check moved from "skin left half" to "accessories exclusively top-right".

## Frozen-byte verification

Evidence is under `artifacts/creature-queue/BRG-M35/`.

- **Determinism:** two separate single-thread cold connected-skin bakes and runtime exports reproduced the cage, manifest, IQM and diffuse byte-for-byte (`final-determinism.json`, `prove-determinism.py`). Blend-file byte determinism is not claimed.
- **Blender source:** isolated background Blender 5.2.1 rebuilt the source (`final-blender-build.log`). A separate fresh process reopened it (`final-blender-verification.json`) and verified:
  - 39 bones and six Actions;
  - 18 sampled poses, with a maximum vertex difference of 0.0000245 units;
  - exact packed skin bytes and no linked libraries.

  No live Blender document or global setting was touched.
- **Native build:** `python tools/run_native.py cmake --build .build/uzdoom --config Release -j4` passed (`native-build.log`). The fingerprint was revalidated after the build (`final-native-fingerprint.json/.txt`). Only the generated kind35 profile row differs from the baseline native inputs.
- **Galleries:** `final-vulkan/` and `final-opengl/` each hold 34 actual 1920x1080 packaged captures. They cover the static before view, all six clips, front/side/rear/oblique views and the 64/128/192-unit distances. Every stage reported `blocking=0`.
- **Runtime warnings:** the only warnings are the pre-existing minimap script warnings.
- **Packages:** both packages are identical, and all 1,174 entries equal current source (`final-package-verification.json`).

```text
IQM   96f008b329eef508db665c05bd6a5124a16ca135958114c806d8a2ded982cb98
PNG   3aafcfac63287268aed96c905511377a169ffb3cde6a9ea15f1460dc9d88bac6
Cage  992305cb266f7c518f3c5cba48061bb8a823705dcafad4339b699e71d797029e
PK3   6e827a769f1c6332784006da8eb0c554407d945f8f2e945d11fdba26b2250363
```

[Final Vulkan gallery](../artifacts/creature-queue/BRG-M35/final-vulkan-contact.jpg), [OpenGL gallery](../artifacts/creature-queue/BRG-M35/final-opengl-contact.jpg).

Residual visual flaws, stated honestly:

- **Shoulders:** they are now rounded muscle masses, but from the low front camera they still read broad and heavy, with a visible step into the upper arm.
- **Face:** simple planes with no mouth interior. The combed locks read as tight rows.
- **Right hand:** the separate fingers are readable only in profile and close views; edge-on from the front they overlap.
- **Arrow on release:** the arrow returns to the quiver in one frame, so a one-frame streak may be visible under frame interpolation. Hiding it needs zero bone scale, which the shared solver and every creature's unit-scale tests deliberately do not support.
- **Trot:** stance hooves slide backward in body space to suggest travel, as the other gaits do. The world travel speed of the tile pacing is not matched.
- **Fall:** the upper hind leg crosses the lower one.
- **Coat detail:** the dorsal stripe and barring remain subtle at the longest gallery distance.

## Remaining acceptance

No natural centaur encounter was obtained. The completed seeds 1–2000 visible census (1,500 actions, depth limit 15) contains no kind35. The conservative route reaches at most depth 9, while the ordinary horde range starts at depth 14 (captive leader rows start at 12). No cheap, genuinely different bounded approach was available, so the unchanged search was not repeated. No spawn, reveal, health or action override was introduced (`natural-encounter-status.json`).

The gallery poses do not prove native bolt, shot, hit or death event synchronisation, or captive presentation.

Still open:

- natural lifecycle and physical play;
- standalone comparison;
- frame-time benchmarking;
- release packaging;
- individual user art approval.

## Reproduction

```powershell
python -m tools.monster_models.centaur_animation
python -m tools.monster_models.review_skeletal --symbol MK_CENTAUR --backend 1 --packaged --all-angles --distances --width 1920 --height 1080 --output artifacts/creature-queue/BRG-M35/reproduction-vulkan
```

- For OpenGL, use backend 0 with a separate output directory.
- Rebake the cage with isolated `--threads 1` Blender and `tools/monster_models/blender_skin.py -- centaur`.
- Build the source with `blender_skeletal.py -- MK_CENTAUR`.

## Preservation

The immediate raw-byte baseline from the start of this task covered 1,628 files. The final audit shows 1,618 unchanged, 10 intended changes, zero unexpected and zero missing (`preservation.json`). The nine new files are listed in the audit.

- All 31 previous skeletal profiles, the other 67 bestiary and monster-registry entries, and the registry headers are unchanged.
- The only line change in the model index is the BRG-M35 row.
- The MODELDEF, ZScript and native header diffs are limited to kind35.
- Regeneration normalised nine other creature cards (09, 10, 11, 18, 20, 21, 27, 28, 29). They were restored from the raw pre-task byte copies, not from git HEAD, and verified by SHA-256.
- The centipede `BRGCENT.png` accidentally overwritten early on was restored by its deterministic generator and matches the baseline hash.

Shared changes:

- the centaur selector in `connected_skin.py`;
- a `centaur: 11600` face budget in `blender_skin.py` (default and all other creatures unchanged);
- the kind35 profile row;
- the regenerated MODELDEF, ZScript, native header, monster registry, bestiary entry, card and model-index row.

The native frontend, bridge, queue files and REVIEW.md were not edited. No cleanup of others' files, commit or publication was made, and the next creature was not started. Superseded review directories were deleted, including the pre-refinement final galleries.

## Coordinator package archive

Both final review packages (`6e827a769f1c6332784006da8eb0c554407d945f8f2e945d11fdba26b2250363`, 1,174 entries) were independently compared entry-by-entry with current source (`parent-final-package-verification.json`) and losslessly archived after coordinator review of the refined art. Restore the exact Vulkan package with:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M35/final-vulkan/ProjectBroom-review.pk3.archive.json
```

Use the equivalent final-opengl manifest for that backend. Captures, logs, manifests and shared content blobs are retained.

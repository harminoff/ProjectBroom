# Pixie model and animation

Presentation-only BRG-M42 / MK_PIXIE. Brogue CE remains authoritative.

## Source facts and planned proof

Brogue describes the pixie as "a tiny humanoid" that sparkles in the gloom, with the hum of beating wings, intermittent high-pitched laughter and a wealth of mischievous magical abilities. Its catalog row (`Globals.c` L1108) gives glyph `G_PIXIE`, `pixieColor` (60/60/60 with 40/40/40 per-channel random variance and the dancing flag), `DF_GREEN_BLOOD`, `PIXIE_LIGHT`, the bolts `BOLT_NEGATION`, `BOLT_SLOW_2`, `BOLT_DISCORD` and `BOLT_SPARK`, and the flags `MONST_MAINTAINS_DISTANCE`, `MONST_FLIES`, `MONST_FLITS`, `MONST_MALE` and `MONST_FEMALE` (Brogue picks either pronoun). Its strings are "sprinkling dust on"/"Dusting" and the single attack verb "pokes". Flight, flitting, distance keeping, every bolt, status effect, light, blood, turn, damage, RNG and outcome remain Brogue-owned. There is no gameplay, AI, collision, damage, spawn, visibility, light or bridge ABI change.

Planned art interpretation (written before implementation):

- A tiny, deliberately stylised humanoid about half the humanoid art reference: an enlarged heart-shaped head with long swept pointed ears, big almond eyes with bright irises, lids and lash lines, angled mischievous brows and a painted grin, so the face still reads at 128 and 192 units. The build is slender and androgynous because Brogue gives the pixie either pronoun.
- Connected skin joins head, ears, neck, torso, arms, palms, legs and pointed feet. Fingers, thumbs, eyes, lash lines, brows, hair locks, clothing and wings are separate accessories seated on the skin, as their anatomy or material requires.
- Original clothing (an art choice, not a Brogue fact): a fitted petal bodice painted on the torso, a flared skirt of overlapping pointed petals, a small petal collar, a twisted vine belt and a tiny dust pouch as a nod to Brogue's "sprinkling dust" string. Wild pale silver-lilac hair in spiky locks.
- Four insect-like membrane wings (larger forewings, smaller hindwings) rooted in the upper back, painted opaque with dark branching veins, a darker leading edge, pearly cells and an iridescent cyan-violet-gold gradient with painted glints. The multicolour shimmer is a nod to the grey glyph colour's large random variance and dancing flag, not a literal material claim. No emission, translucency, render-style change, light, particle, projectile or sparkle mesh is added, so the displayed-class visibility restoration for hidden and sensed monsters is untouched.
- Hover clearance: the rest mesh keeps the documented 16-unit flight gap below the pointed toes.
- Six cosmetic roles: hover (idle, fast wing beats, bob and dangling legs), flit (forward-pitched darting loop), poke (lunge and index-finger jab, Brogue's attack verb), hex (a two-handed spell gesture; cosmetic only and not a claim about discord, negation, slowness or spark), flinch (knocked back with crumpling wings) and fall (limp drop to the floor, wings stilled and flattened). Only hover and flit loop. Every action clip puts its key pose at its middle frame.

Planned proof:

- one closed connected skin, exact seam weights, at most four quantised normalised influences;
- every frame of every clip inside the centred ±32 X/Y cell, minimum Z above 0.07, zero automatic floor lift, hover gap near 16 units in the loops, and a grounded death with inactive wings;
- wing roots staying seated on the back and fingers seated in the palms in every frame;
- positive triangle orientation in every frame, loop closure and action recovery;
- identical runtime bytes from two cold single-thread bakes and exports;
- fresh Blender 5.2 reopen with 18 sampled poses, packed skin, no linked libraries;
- native compile and fingerprint, packaged Vulkan and OpenGL 34-view galleries, inspected at gameplay distance;
- preservation audit against the immediate raw-byte baseline.

All new art is original Project Broom content under CC-BY-SA-4.0. No third-party artwork is imported.

## Delivered artwork and rendering

- Master geometry, rig and poses: `tools/monster_models/pixie_animation.py`. Original paint: `pixie_materials.py`. Tests: `test_pixie.py`.
- Runtime files: `mod/BrogueDoom/models/monsters/42_pixie.iqm` and the 2048-square `mod/BrogueDoom/graphics/BRGPIXIE.png`.
  - The lump name was checked against every existing graphic before the first write; no other texture was touched.
  - No GLDEFS material, brightmap, render style, alpha, light or particle is added.
- Manifest and cage: `assets/monsters/pixie/animation.json` and `connected-skin.json.gz`. Editable packed source: `assets/monsters/pixie/pixie-animated.blend`.
- The static `42_pixie.obj`, `BRGM42.png` and `sources/42_pixie.blend` references are byte-unchanged; the legacy `winged` recipe row is untouched.
- 33 bones, 77 runtime parts (one connected skin plus 76 accessories), 36,957 runtime vertices, 32,480 triangles and six clips.
- The closed connected skin (3,955-vertex cage, 7,906 faces, one component) is baked with a pixie-only 0.1 voxel size and 7,900-face budget, so ears, wrists and ankles keep their shape at this small scale.
- Rest extents are 11.6 x 29.0 x 31.5 units: toe tips at 16.2 (the documented flight gap), crown at 47.7, forewing span 29. The figure is about half the 58-unit humanoid reference. These are art choices, not Brogue measurements.
- Every frame of every clip stays within X -19.29..18.33 and Y -18.54..20.17. Minimum Z is 0.153 and nothing uses automatic floor lift.

### Construction

- **Body:** one skin carries the enlarged cranium, heart-shaped face with a pointed chin and small upturned nose, long swept pointed ears (with their own bones), neck and trapezius, torso, shoulders, arms, palms, legs and pointed feet.
- **Face (separate, seated on the skin):**
  - large eyeballs with a painted green iris, dark limbal ring, pupil and two glints;
  - violet upper lids tilted up at the outer corner, a thick dark lash line with an outer flick;
  - an arched left brow and a lower, angled right brow for a mischievous asymmetry.
  - Painted on the skin: violet eyeshadow with a dark outer wing, blush, a rosy nose tip, a lifted smirk over a rosy lower lip, and silver glitter freckles on the cheekbones.
- **Hair:** a scalp cap with 29 swept locks that follow the scalp and rise off it, a side-swept fringe of three locks, and low nape locks so a fallen head rests on its cap.
- **Hands:** separate index finger (its own bone for the jab), two further fingers (a shared curl bone) and a thumb, each seated inside the palm.
- **Clothing (art choice):** a painted teal petal-scale bodice with a gold front seam; a half collar of five pale upturned petals; ten overlapping pointed skirt petals in two layers (violet-magenta outer, indigo inner) carried by four skirt bones; a twisted green vine belt; a small leather dust pouch with a gold rim of painted glitter on the left hip (a nod to Brogue's "sprinkling dust" string); leaf anklets.
- **Wings:** two forewings and two hindwings, each a closed thin cambered membrane with a root knob seated in the upper back, one rigid bone each.
  - Paint: an iridescent pearl gradient (gold root, cyan-blue middle, violet-magenta outer), veins fanning from the root with staggered cross veins, a dark costa and margin, a gold-ringed eye-spot and white glints.
- **Skin atlas:** each of the 7,906 skin triangles has a 16-pixel island in the left half, painted from continuous rest positions, normals and bone-weight fractions (head, arm, leg and torso), so the face, bodice and limbs have no source-part seams. Islands are laid out in spatial (Morton) order so mipmapped island borders blend neighbouring surface colours instead of speckling.
- **Accessories:** 16 role cells in the top-right quadrant; both wings share the bottom-right quadrant at higher resolution.
- **Lighting:** paint is baked for the engine's flat light (top/front light, strong value contrast, dark lashes, violet lids). The actor keeps the gameplay-inert `BrogueMonsterProxyBase` with its default opaque render style, so hidden/sensed visibility restoration is untouched.

### Clips

Only idle and flit loop. Every action starts from and returns to a shared carry ("attitude": right hand on the hip, left hand loose, right leg tucked), so actions do not pop out of the hover. Each action peaks at its sampled middle frame.

- **Idle (48 frames, 24 fps):** eight fast wing beats per loop with lagging hindwings, a bob of about ±1 unit around the flight gap, head tilts, ear twitches, skirt flutter and a sassy hand-on-hip hover.
- **Flit (24 frames, 30 fps):** pitched 20° forward about the pelvis, weaving and dipping, legs trailing, arms swept back, hair and ears streaming, larger six-beat wing strokes.
- **Poke (24 frames, attack, Brogue's "pokes"):** the right arm cocks back, then the pixie darts forward and jabs with a straight arm and extended index finger (tip beyond X 13 at the middle frame), left arm back for balance, legs kicked back, wings swept back.
- **Hex (30 frames, alternate):** a cosmetic two-handed spell gesture. The hands gather at the chest with knees tucked and wings folded, then fling up and out with open fingers, the head thrown back and wings spread flat. A short finger wiggle follows. It asserts nothing about discord, negation, slowness or spark.
- **Flinch (16 frames, hit):** knocked back and tipped, arms guarding the face, knees tucked, wings crumpled down, skirt blown up; it recovers.
- **Fall (40 frames, death):**
  1. A stiff jolt (arms flung, head back).
  2. A limp, accelerating drop that rotates onto its back. The middle frame is still mid-air.
  3. The pixie lands with a small bounce and settles lying along the cell's Y axis, face up and turned toward the camera side.
  4. One arm lies flung beside the head, the other across the hip, and one knee is drawn up and fallen outward. The skirt spreads flat and the ears fold back.
  5. All four wings stop and flatten onto the floor, splayed asymmetrically and drooping slightly toward their tips.

  The final pose is 8.46 units high (median 2.86). The pelvis, chest and head bones all lie below 5 units.
- **Native selection:** the native selector alternates the two attack clips; the bridge does not distinguish Brogue's bolts or verbs.

### Review iterations

`early-vulkan-contact.jpg` is the only kept iteration sheet. Isolated Blender previews and the early engine review drove these fixes:

- A stray fringe lock (from a surface lookup outside the head) was shortened.
- The spiky "thistle crown" hair became swept locks.
- The helmet-like back of the head gained nape locks and a lighter cap.
- The heavy lids were lifted and the eyes enlarged.
- The neck was thickened, with trapezius masses added.
- The skirt top was tightened so a lying body rests on it without penetration.
- The wing cross veins were changed from a brick-like grid to staggered cells.
- The collar was lightened.
- Arm glitter that read as dirt was removed, and island bleeding speckles were reduced by spatial island ordering.
- The death pose was fitted to the floor.
- The idle clip was renamed from `hover` to `idle`, because the shared Blender exporter selects an action named `idle`.

## Tests

**57 tests passed in 518.972 seconds** (`tests.log`):

```powershell
python -m unittest tools.monster_models.test_pixie tools.monster_models.test_skeletal tools.monster_models.test_connected_skin tools.monster_models.test_creatures tools.test_broguedoom_resources
```

The eight pixie tests cover:

- **Connected skin:** closed, single-component manifold; exact seam positions, weights and normals; at most four normalised weights; every arm, leg, ear and trunk bone carried; island capacity; the signature separate parts (eyes, lids, lashes, brows, index fingers, thumbs, four wings, ten skirt petals, five collar petals, at least 20 hair locks, pouch).
- **Roles and clearance:**
  - six ordered roles with loop rules;
  - every frame inside ±31.5 X/Y with minimum Z above 0.07;
  - raw frames equal to exported frames (no floor compensation) at unit scale;
  - the 16-unit rest gap, with the idle bob staying above 15 and flit above 16;
  - loop closure; actions recover and start within 3.5 units of the idle carry.
- **Key poses:** each action's middle frame travels more than 7 units from the carry and is at least 80% of the clip's largest excursion; the poke finger tip reaches X > 13.
- **Attachment and orientation:**
  - no degenerate triangle in any frame;
  - rigid accessories never invert;
  - folded skin triangles stay at or below 0.5% per frame;
  - wing and finger bones never leave their roots.
- **Wings:** they beat more than 20° in idle, more in flit, are identical over the last 22% of the fall and lie below 2.2 units in the final frame.
- **Fall:** grounded and limp (maximum 8.5, a contact below 0.4, and skirt, cap and wings near the floor), with a mid-air middle frame.
- **Paint:** pale skin against a dark teal bodice, a green iris, a near-black pupil and lashes, bright wings, UV quadrant isolation and a unique skin path.
- **Bytes:** exact runtime IQM and texture bytes.

## Frozen-byte verification

Evidence is under `artifacts/creature-queue/BRG-M42/`.

- **Determinism:** two cold single-thread Blender bakes and runtime exports reproduced the cage, manifest, IQM and diffuse byte-for-byte (`determinism.json`, `prove-determinism.py`). Blend-file byte determinism is not claimed.
- **Blender source:** isolated background Blender 5.2.1 built the source (`blender-build.log`). A separate fresh process reopened it (`blender-verification.json`) and verified:
  - 33 bones and six Actions;
  - 18 sampled poses, with a maximum vertex difference of 0.0000155 units;
  - exact packed skin bytes and no linked libraries.

  No live Blender document or global setting was touched.
- **Native build:** `python tools/run_native.py cmake --build .build/uzdoom --config Release -j4` passed (`native-build.log`). The fingerprint was recorded after linking (`native-fingerprint.json/.txt`). The only native input change is the generated kind42 row.
- **Galleries:** `final-vulkan/` and `final-opengl/` each hold 34 actual 1920x1080 packaged captures. They cover:
  - the static before view;
  - three samples of every clip;
  - front, side, rear and oblique views;
  - the 64/128/192-unit distances.

  Every stage reported `blocking=0`. Both contact sheets and the full-size front idle, poke, hex, fall and distance captures were inspected.
- **Runtime warnings:** the only warnings are the pre-existing minimap script warnings.
- **Packages:** both packages are identical, and all 1,180 entries equal current source (`package-verification.json`).

```text
IQM   387fdf6ea7f1b3ac8d9e884f6be6f58c30b7d45ed4d08bf9d9ae5c8290facd9d
PNG   a2bd434214bf7530fa03e04718f0708a20cf1a73c333a68fb6dbbc06b5903916
Cage  8aba978d57139d38bd6bfa9a0270f339e6490b12a65178a12810fafe2f954906
PK3   7eabc214e2c23968cc1d26615233fedf955e539a36f598f0c9b29bf0edb0bd0b
```

[Vulkan gallery](../artifacts/creature-queue/BRG-M42/final-vulkan-contact.jpg), [OpenGL gallery](../artifacts/creature-queue/BRG-M42/final-opengl-contact.jpg), [early review](../artifacts/creature-queue/BRG-M42/early-vulkan-contact.jpg).

Residual visual flaws, stated honestly:

- **Size:** the pixie is genuinely tiny. At 128 and 192 units it reads as a bright winged figure, and the face is only a hint of green eyes and pale skin. The face reads clearly at 64 units and in the front gallery views.
- **Skin folds:** the akimbo shoulder and the tightly bent elbows in flinch and hex fold up to about 0.5% of skin triangles at their peak (a small crease inside the shoulder and elbow).
- **Speckles:** a few island-border speckles remain on the arms in close views, even with spatial island ordering.
- **Hair:** from behind, the scalp cap still reads a little like a smooth helmet under the locks. In the death pose the hair is the brightest mass and draws the eye.
- **Wings:** they are opaque painted membranes, not translucent, and have no specular response, so they do not shimmer with motion.
- **Paint and light:** skin reads pink-lavender under engine light, and eye glints are painted.
- **Clipping:** thin accessories (skirt petals against the thighs, collar against the chin) can touch in extreme poses.
- **Face:** eyes do not close, so the fallen pixie stares.

## Remaining acceptance

No natural pixie encounter was obtained.

- The completed seeds 1-2000 visible census contains no kind42. The only kinds it saw are 1-18, 55 and 62.
- The conservative route reaches at most depth 9. The ordinary rows (GlobalsBrogue.c L790 and the captive imp-escort row L838) span depths 14-21, and the caged kennel and vampire-fodder rows (L900, L914) start at 11.
- No cheap, genuinely different bounded approach was available, so the unchanged search was not repeated.
- No spawn, reveal, health or action override was introduced (`natural-encounter-status.json`).

The gallery does not prove:

- natural flitting or movement;
- native negation, slowness, discord or spark bolt synchronisation;
- natural poke, hit or death event timing;
- captive presentation;
- live hidden or sensed transitions for kind42. The render style is the unchanged opaque default, so there is no new visibility path, but this was not separately exercised.

Still open:

- natural lifecycle and physical play;
- standalone comparison;
- frame-time benchmarking;
- release packaging;
- individual user art approval.

## Reproduction

```powershell
python -m tools.monster_models.pixie_animation
python -m tools.monster_models.review_skeletal --symbol MK_PIXIE --backend 1 --packaged --all-angles --distances --width 1920 --height 1080 --output artifacts/creature-queue/BRG-M42/reproduction-vulkan
```

- For OpenGL, use backend 0 with a separate output directory.
- Rebake the cage with isolated `--threads 1` Blender and `tools/monster_models/blender_skin.py -- pixie`.
- Build the source with `blender_skeletal.py -- MK_PIXIE`.

## Preservation

An immediate raw-byte baseline (1,646 files, 121 raw copies) was taken before any edit.

**Baseline incident.** After the first edits and regeneration, `take-baseline.py` was accidentally run a second time, which overwrote that record with post-edit bytes. The baseline was then reconstructed by `reconstruct-baseline.py` (`baseline-reconstruction.json`) from independent evidence, and every assertion passed:

- **Cards:** the ten normalised cards and card 42 were taken from BRG-M34's SHA-verified raw start copies.
- **Shared tool hooks:** `connected_skin.py` and `blender_skin.py` were rebuilt by exact inversion of the pixie hooks and equal their BRG-M34 start hashes.
- **Profiles and bestiary.py:** the pixie row and lines were removed. The remainder differs from BRG-M34's start copy only by BRG-M34's own acidic jelly additions.
- **Native header:** regenerated from the pre-task rows; it differs from BRG-M34's start copy only by the kind34 row.
- **MODELDEF, ZScript and GLDEFS:** exact entries of BRG-M34's archived, coordinator-verified final package.
- **Bestiary index, monster registry and model index:** the current files with only the kind42 entry or row taken from BRG-M34's start copy. They differ from that copy only by entry 34.
- **Acidic jelly runtime bytes:** still equal BRG-M34's determinism record.
- **Everything else:** current bytes. A comparison with BRG-M34's start hashes showed that only the coordinator's queue and handoff edits and this task's own changes differ.

The reconstruction reproduces the original counts exactly: 1,646 files and 121 raw copies. The one file whose pre-task bytes could not be independently hash-verified is card 34, which was kept as current generator output of unchanged kind34 data. `take-baseline.py` now refuses to overwrite an existing baseline.

The final audit (`preservation.json`) shows:

- 1,635 unchanged, 11 intended changes, zero unexpected and zero missing;
- all 33 previous skeletal profiles, the other 67 bestiary and monster-registry entries, and the registry headers unchanged;
- a model-index line change for the BRG-M42 row only;
- MODELDEF, ZScript and native header diffs limited to kind42;
- one line in `connected_skin.py`, and a `'pixie'` entry added to both the voxel-size and face-budget expressions in `blender_skin.py` (the default and every other creature are unchanged).

After every regeneration, the ten other normalised cards (09, 10, 11, 18, 20, 21, 27, 28, 29 and 35) were restored from the raw baseline copies, not from git HEAD, and verified by SHA-256.

Shared changes:

- the pixie selector in `connected_skin.py`;
- the pixie voxel size and face budget in `blender_skin.py`;
- the kind42 profile row;
- the pixie traits and report link in `bestiary.py`;
- the regenerated MODELDEF, ZScript, native header and monster registry;
- the bestiary entry with its verification record, the card and the model-index row.

The native frontend, bridge, GLDEFS, queue files and REVIEW.md were not edited. No other contributor's files were cleaned up, nothing was committed or published, and the next creature was not started. The superseded second review gallery, the early gallery folder and all scratch previews were deleted.

## Coordinator package archive

Both final review packages (`7eabc214e2c23968cc1d26615233fedf955e539a36f598f0c9b29bf0edb0bd0b`, 1,180 entries) were independently compared entry-by-entry with current source (`parent-final-package-verification.json`) and losslessly archived after coordinator image review. Restore the exact Vulkan package with:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M42/final-vulkan/ProjectBroom-review.pk3.archive.json
```

Use the equivalent final-opengl manifest for that backend. Captures, logs, manifests and shared content blobs are retained.

# Acidic jelly model and animation

Presentation-only BRG-M34 / MK_ACID_JELLY. Brogue CE remains authoritative.

## Source facts and planned proof

Brogue names the creature "acidic jelly" (glyph `G_JELLY`, colour `acidBackColor`
15/80/25 with dancing variance) and describes a jelly that has fed on acid mounds
until it expresses their characteristics, corroding unprotected weapons or armor
that touch it. Its catalog row gives `DF_ACID_BLOOD`, the large flag,
`MONST_DEFEND_DEGRADE_WEAPON`, `MA_HIT_DEGRADE_ARMOR` and `MA_CLONE_SELF_ON_DEFEND`.
Its strings are "transmuting"/"Transmuting" and the single attack verb "burns".
Corrosion, acid blood, splitting into clones, turns, damage, RNG, spawn and every
outcome remain Brogue-owned. There is no gameplay, AI, collision, damage, spawn,
visibility or bridge ABI change.

Planned art interpretation (written before implementation):

- A large, heavy connected gel mass, taller and lumpier than the pink jelly: a
  broad slumped base carrying three fused swollen crown lobes of unequal size
  with deep creases between them, so the outline is multi-peaked rather than the
  pink jelly's single dome or the acid mound's low pancake.
- A thick rolled contact rim with drip beads under vertical runnels that run from
  the lobe valleys down the flanks, and shallow acid-etched craters sculpted into
  the lobe tops. All relief belongs to one closed skin; nothing is detached.
- Original opaque pigment: a deep bottle-green/emerald gel (the glyph colour is an
  identity cue, not literal paint), darker and denser low down, with mottled
  hue variance as a nod to the dancing colour, yellow-lime acid film pooling in
  the creases and runnels, pale corroded pit rims, dark density veins and small
  trapped bubbles. Painted soft occlusion in creases and a lighter translucent-
  looking rim give depth under the flat gallery light. No emission, fullbright,
  translucency, aura, droplets, eyes, mouth, bones or limbs.
- Six cosmetic roles: idle (lobes pulse in sequence), creep (a rear-to-front
  peristaltic wave; loops), burn (gather back then a forward engulfing surge of
  the front lobe), engulf (rear up, then slam and spread), recoil (a damped
  wobble back) and dissolve (lobes deflate and the mass spreads into a spent,
  low puddle). Only idle and creep loop. The native selector alternates attack
  clips; the bridge does not distinguish Brogue verbs.
- Hit and death are cosmetic only. Clones exist only when Brogue creates them
  and arrive through existing stable bridge IDs; no clip implies or spawns one.

Planned proof:

- one closed connected manifold, Euler characteristic 2, exact UV seams;
- positive triangle area and orientation in every authored frame;
- every frame inside the centred ±32 X/Y cell, contact skirt at the floor, zero
  automatic floor lift, settled low death;
- loop closure, action recovery, translation-only unit-scale normalized weights;
- identical runtime bytes from two cold single-thread builds;
- fresh Blender 5.2 reopen with 18 sampled poses, packed skin, no linked libraries;
- native compile and fingerprint, packaged Vulkan and OpenGL 34-view galleries;
- hidden/sensed visibility unaffected (opaque default render style);
- preservation audit against the immediate raw-byte baseline.

Original CC-BY-SA-4.0 artwork. No third-party artwork imported.

## Delivered artwork and rendering

This is the refined delivery. The coordinator rejected the first delivery because from the gameplay camera it read as a smooth, round green apple or cabbage. See [Coordinator refinement](#coordinator-refinement).

- Master sculpt, rig and poses: `tools/monster_models/acid_jelly_shape.py` and `acid_jelly_animation.py`. Original paint: `acid_jelly_materials.py`. Tests: `test_acid_jelly.py`.
- Runtime files: `mod/BrogueDoom/models/monsters/34_acid_jelly.iqm`, the 1024-square `graphics/BRGACJLY.png` diffuse and `BRGACJLY_S.png` specular maps, and a flat `BRGACJLY_N.png` normal map.
  - The lump names were checked against every existing graphic before the first write.
  - No other creature's texture was touched.
- Manifest: `assets/monsters/acid_jelly/animation.json`. Editable packed source: `assets/monsters/acid_jelly/acid-jelly-animated.blend`.
- The static `34_acid_jelly.obj`, `BRGM34.png` and `sources/34_acid_jelly.blend` references are byte-unchanged. The legacy `slime` recipe row in `bestiary.py` is untouched.
- The mesh is one closed, connected analytic skin: 10,297 runtime vertices, 20,448 triangles, 27 bones and six clips. It needs no remesh cage or bake.
- Rest extents are 54.24 x 47.88 x 21.29 units. The body is about 2.5 times wider than it is tall. These are artistic dimensions, not Brogue measurements.
- In every frame of every clip, X stays within -30.21..30.53 and Y within -26.43..27.52. Minimum Z is 0.12, with zero automatic floor lift.

### Construction

- **Surface:** a latitude/longitude skin. Its azimuth is U, and its latitude runs from a flat underside pole to the crown. 30% of the rings describe the underside and skirt; 70% describe the body. Every detail is an offset of that one surface, so nothing can separate during animation.
- **Silhouette:** a heavy gel slumping under its own weight.
  - A low sagging dome sits on a bulging skirt lip, which overhangs its floor contact by more than 0.8 units all round. A belly swell sits just above the lip.
  - Three swollen lobes sit low and far apart, with deep valleys between them. They break the outline from the front, side and three-quarter views. A small lobe sits on the crown.
  - Three satellite blobs bud from the skirt as rounded caps on the same skin. They are cosmetic, stay inside the cell, and protrude by more than 1.5 units.
- **Acid relief:**
  - seven wavy runnels descend from the lobe valleys;
  - thick drips hang from the skirt lip towards the floor;
  - six shallow etched craters sit on the lobes;
  - low sagging folds run around the flanks.
- **Paint:** opaque, with no emission.
  - **Base gel:** deep bottle-green.
  - **Fake subsurface:** the thick lobes, buds and belly glow lighter and warmer. Thin skirt edges and valleys stay dark and dense.
  - **Colour variance:** broad blue-green and yellow-green mottles, a nod to the dancing variance in `acidBackColor`.
  - **Inclusions:** 48 suspended inclusions are painted with depth. Deep ones are larger, softer and fainter, and shallow ones are crisp. Each has a faint refracted crescent beneath it.
  - **Bubbles:** a dozen faint trapped bubbles.
  - **Acid film:** bold yellow-lime film pools in the valleys. It runs down every runnel, beads bright at the skirt drips, and marbles across the upper gel.
  - **Craters:** each holds pooled acid inside a faint corroded lip.
  - **Wet highlights:** bright painted specular pools on every lobe and bud, a broken rim sheen along the skirt lip, and glossy lines down every drip.
  - **Baked light:** occlusion and a top light are baked from the surface's own normals and concavity.
  - The fine white speckles are gone.
- **Material:** the GLDEFS entry only adds the specular and normal maps (glossiness 42, level 0.52). Specular follows the film and highlights, and is suppressed in pits and inclusions.
  - The actor keeps the existing gameplay-inert `BrogueMonsterProxyBase` class with its default opaque render style.
  - The visibility restoration for hidden and sensed monsters is therefore untouched.
  - No render style, alpha, brightmap, light or particle is introduced.

### Rig

- **Bones:** 27 translation-only bones, all at unit scale:
  - the root;
  - a skirt ring and a belly ring of eight anchors each;
  - a lobe ring of nine anchors, one under each lobe and two in each valley;
  - the crown.
- **Height blending:** follows the monotone base profile, not the posed height, so the underside stays on the root and the floor.
- **Weights:** quantized to 1e-6, with the last influence taking the exact remainder.

### Clips

Only idle and creep loop. The action clips peak at their middle frame, which is the frame the gallery samples.

- **Idle (48 frames):** a visible breathing wobble. The lobes swell up to about 2 units in sequence, and the mass sways.
- **Creep (32 frames):** a rear-to-front peristaltic wave. The skirt reaches ahead and the lobes roll in turn.
- **Burn (26 frames, attack):** the mass rears back and rises, lifting its front lobe. It then slaps forward and down, spreading sideways, and recovers.
- **Engulf (32 frames, alternate):** it rises tall and narrow, then lunges down and spreads wide in every direction. It wobbles and settles.
- **Recoil (16 frames, hit):** knocked back and squashed, followed by a clear side-to-side jiggle.
- **Dissolve (40 frames, death):** the lobes deflate first. The mass then spreads with an irregular, angle-varying edge, slumps slightly and settles into a spent acid puddle.
  - The highest residual fold is 5.66 units.
  - The median height is 1.84, and the 90th percentile is 4.33.

How the death pose was fitted:

- The death offsets are a least-squares fit of the anchor translations towards a near-affine, irregular spread-and-flatten map, solved once from the rest vertices.
- A ring-ordering clamp stops an upper ring from sinking more than 93% of its band below the ring beneath it. It prevents steep valley walls from folding.
- Every frame of every clip keeps its triangle orientation.

Authority notes:

- Hit and death are cosmetic and imply no split. Clones exist only when Brogue creates them, and they arrive through the existing stable bridge IDs.
- The native selector alternates the two attack clips. The bridge does not distinguish Brogue's verbs.

### Review iterations

**First delivery.** Blender previews and three packaged Vulkan reviews drove these fixes:

- **Crown shape:** a horned "bucket" crown was replaced by fused lobes.
- **Hard creases:** hard cap-edge crease lines, including one that looked like a seam, were smoothed out.
- **Pits:** polka-dot, bullet-hole and eye-like pits were calmed.
- **Veins:** filaments that read like cabbage leaves became density clouds.
- **Paint:** the paint was deepened, and acid marbling was added.
- **Fins:** base fins were broadened into drips.

### Coordinator refinement

The coordinator found that the first delivery read as a smooth apple or cabbage at gameplay distance. Its lobes did not read, its material looked like painted fruit skin, and its attack clips were nearly indistinguishable from idle. This pass changed:

- **Silhouette:** the height fell from 28.65 to 21.29 and the width rose from 49.6 to 54.2, for a width-to-height ratio above 2.2. The pass added the overhanging skirt, the sagging belly, low separated lobes with deep valleys, three budding satellite blobs and hanging skirt drips.
- **Gel material:**
  - a fake-subsurface core with dense dark edges;
  - suspended inclusions painted with depth;
  - specular pools, rim sheen and wet drip highlights;
  - the white speckles removed.
- **Acid:** bolder pooled film, brighter runnels and bright bead drips.
- **Animation:** the idle wobble is two to three times larger. Burn now rears back and slaps, engulf spreads in a lunge, and recoil jiggles. Each action peaks at its sampled middle frame.
- **Death:** an irregular, spread-out spent puddle, at most 5.66 units high instead of 8.43.

The kept `pre-refinement-vulkan-contact.jpg` documents the rejected first delivery. Its superseded galleries and the review iterations were deleted.

## Tests

**58 tests passed in 431.051 seconds** (`tests.log`):

```powershell
python -m unittest tools.monster_models.test_acid_jelly tools.monster_models.test_skeletal tools.monster_models.test_connected_skin tools.monster_models.test_creatures tools.test_broguedoom_resources
```

The family's `test_pink_jelly` and `test_acid_mound` also pass unchanged, with 12 tests (`family-tests.log`).

The nine acidic jelly tests cover:

- **Topology:** one closed, connected manifold with Euler characteristic 2.
- **Orientation:** every triangle keeps positive area and its orientation in every authored frame.
- **Bounds:** every frame stays inside ±31.5 X/Y, the contact stays at the floor (minimum Z 0.07–0.15), and exported roots equal the raw poses.
- **Size:** the living mass is taller than 19 units and more than 2.2 times as wide as it is tall.
- **Death:** the spent puddle is below 9 units and below 32% of the living height, with a median below 3.5 and a 90th percentile below 7.
- **Lobes:** three lobes rise above 5.5 units, and the upper outline bulges at each lobe relative to its valleys.
- **Skirt and buds:** the skirt lip overhangs its floor contact by more than 0.8 units at every 15 degrees, and the three buds protrude by more than 1.5 units.
- **Loops and seams:** loops close, every action clip starts at rest, seam positions and weights match exactly, and the texture meridian is seamless.
- **Weights:** at most four normalized influences, translation-only unit-scale frames, and out-of-phase idle lobe swelling.
- **Paint:** green-dominant, with more than 6% yellow-lime film.
- **Bytes:** exact IQM and all three map bytes.

The first delivery's "living height above 27" assertion described the rejected tall silhouette. It was replaced by the stricter width-to-height and minimum-height pair. No other threshold was relaxed, and the overhang and bud test was added.

## Frozen-byte verification

Evidence is under `artifacts/creature-queue/BRG-M34/`.

- **Determinism:** two fresh single-thread runtime exports reproduced the accepted IQM, all three maps and the manifest byte-for-byte (`determinism.json`, `prove-determinism.py`). There is no remesh bake. Blend-file byte determinism is not claimed.
- **Blender source:** isolated background Blender 5.2.1 rebuilt the source (`blender-build.log`). A separate fresh process reopened it (`blender-verification.json`) and verified:
  - 27 bones and six Actions;
  - 18 sampled poses, with a maximum vertex difference of 0.0000035 units;
  - exact packed skin bytes and no linked libraries.

  No live Blender document or global setting was touched.
- **Native build:** `python tools/run_native.py cmake --build .build/uzdoom --config Release -j4` passed (`native-build.log`). The fingerprint was recorded after linking (`native-fingerprint.json/.txt`). The only native input change is the generated kind34 row.
- **Galleries:** `final-vulkan/` and `final-opengl/` each hold 34 actual 1920x1080 packaged captures. They cover:
  - the static before view;
  - three samples of every clip;
  - front, side, rear and oblique views;
  - the 64/128/192-unit distances.

  Every stage reported `blocking=0`. Both contact sheets and the full-size idle, burn, engulf, recoil, dissolve and distance captures were inspected.
- **Runtime warnings:** the only warnings are the pre-existing minimap script warnings.
- **Packages:** both packages are identical, and all 1,178 entries equal current source (`package-verification.json`).

```text
IQM   bf113a030f90127ca57b1efd5bbdbb10d47a30872e8d423562f6edb42cc8e9b6
PNG   c9e70c2809e4c2611c5d3bef16250f2a783f46ffadca07f2899438ee4f95a14c
SPEC  bac0b6e978542ab0c471d5241a0c23b07126a145fc5f7e9d78fcbbf1b2a5c9fb
PK3   b96b3df51bec4e2d35b543d9092953e6e39649341291c5e595092e71ee3c3bd6
```

[Vulkan gallery](../artifacts/creature-queue/BRG-M34/final-vulkan-contact.jpg), [OpenGL gallery](../artifacts/creature-queue/BRG-M34/final-opengl-contact.jpg), [rejected first delivery](../artifacts/creature-queue/BRG-M34/pre-refinement-vulkan-contact.jpg).

Residual visual flaws, stated honestly:

- **Brightness:** engine light makes the gel brighter and more saturated than the Blender previews. The deep, dense edges read less dark in the gallery.
- **Painted gloss:** the specular pools and sheen are painted, so they do not move with the light. From some angles a highlight sits on a surface turned away from the light.
- **Bubbles:** a few faint trapped-bubble rings are still visible close up.
- **Death:** the spent puddle keeps low pillow-like folds where the lobes were. It reads as a melted, collapsed mass rather than a perfectly flat pool.
- **Attack readability:** from the head-on camera the burn slap is still partly foreshortened. It reads mainly through the rear-back and the flatten-and-widen.
- **Front valley:** a narrow dark crease remains where the front valley, a runnel and a bud meet.

## Remaining acceptance

No natural acidic jelly encounter was obtained.

- The completed seeds 1–2000 visible census contains no kind34. The only kinds it saw are 1–18, 55 and 62.
- The conservative route reaches at most depth 9, while the only ordinary horde row (GlobalsBrogue.c L788) spans depths 14–21.
- No cheap, genuinely different bounded approach was available, so the unchanged search was not repeated.
- No spawn, reveal, health or action override was introduced (`natural-encounter-status.json`).

The gallery does not prove:

- natural clone-on-defend presentation through real stable IDs;
- corrosion, hit or death event timing;
- hidden or sensed transitions for kind34 in a live session. The render style is the unchanged opaque default, so there is no new visibility path, but this was not separately exercised.

Still open:

- natural lifecycle and physical play;
- standalone comparison;
- frame-time benchmarking;
- release packaging;
- individual user art approval.

## Reproduction

```powershell
python -m tools.monster_models.acid_jelly_animation
python -m tools.monster_models.review_skeletal --symbol MK_ACID_JELLY --backend 1 --packaged --all-angles --distances --width 1920 --height 1080 --output artifacts/creature-queue/BRG-M34/reproduction-vulkan
```

- For OpenGL, use backend 0 with a separate output directory.
- Build the editable source with isolated background Blender and `blender_skeletal.py -- MK_ACID_JELLY`.

## Preservation

The immediate raw-byte baseline covered 1,636 files, including 120 raw byte copies of shared generated files and cards. The final audit, rerun after the refinement, shows 1,626 unchanged, 10 intended changes, zero unexpected and zero missing (`preservation.json`). The audit lists the 11 new files.

- All 32 previous skeletal profiles, the other 67 bestiary and monster-registry entries, and the registry headers are unchanged.
- The only line change in the model index is the BRG-M34 row.
- The MODELDEF, ZScript and native header diffs are limited to kind34.
- The GLDEFS change is one added material block, with its CRLF line endings preserved.
- Each regeneration normalized ten other creature cards (09, 10, 11, 18, 20, 21, 27, 28, 29 and 35). On card 35 it also dropped a hand-added report link. After every regeneration, all ten were restored from the raw pre-task byte copies, not from git HEAD, and verified by SHA-256.
- The bestiary verification record for kind34 was rewritten for the refined bytes and keeps the original static-asset chain.

Shared changes:

- the kind34 profile row;
- the acidic jelly traits and report link in `bestiary.py`;
- one GLDEFS material;
- the regenerated MODELDEF, ZScript, native header and monster registry;
- the bestiary entry with its verification record, the card and the model-index row.

The native frontend, bridge, queue files and REVIEW.md were not edited. No other contributor's files were cleaned up, nothing was committed or published, and the next creature was not started. Superseded galleries, review iterations and scratch previews were deleted.

## Coordinator package archive

The coordinator rejected the first delivery (compact apple-like form, fruit-skin paint, barely distinguishable action clips) and accepted the refined bytes. Both final review packages (`b96b3df51bec4e2d35b543d9092953e6e39649341291c5e595092e71ee3c3bd6`, 1,178 entries) were independently compared entry-by-entry with current source (`parent-final-package-verification.json`) and losslessly archived. Restore the exact Vulkan package with:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M34/final-vulkan/ProjectBroom-review.pk3.archive.json
```

Use the equivalent final-opengl manifest for that backend. Captures, logs, manifests and shared content blobs are retained.

# Black jelly model and animation

This is presentation-only work for BRG-M52 / `MK_BLACK_JELLY` (runtime class `BrogueMonsterK52`). Brogue CE remains authoritative. This is the Phase 1 authoring delivery described in [creature-pipeline.md](creature-pipeline.md). The coordinator still has to integrate, gate and review it, and art approval belongs to the user.

## Source facts

The pinned catalog row is [Globals.c L1129](../src/brogue-mapgen/src/brogue/Globals.c#L1129). The prose is at [Globals.c L1338](../src/brogue-mapgen/src/brogue/Globals.c#L1338).

- **Identity:** the "black jelly" uses glyph `G_JELLY`, colour `&black`, 120 HP, defense 0, accuracy 130 and damage 3–8.
- **Tokens:** `DF_PURPLE_BLOOD`, the large flag and `MA_CLONE_SELF_ON_DEFEND`.
- **Prose:** a blob of jet-black goo whose caustic assault few creatures withstand.
- **Strings:** "absorbing" and "Feeding". The attack verbs are "smears", "slimes" and "drenches".

Brogue owns everything that happens: the damage, the clone split on defense, purple blood, turns, RNG and spawning. The model adds no power and no split action. Colour cues are identity cues only:

- black becomes the body;
- the purple blood token becomes a deep violet interior depth.

Neither cue implies an ability.

## Art interpretation

The design problem is a near-black blob on a dark floor, which reads as a hole. The design answer is a glossy melting ink heap whose readability comes from gloss, not from lighter paint.

### Silhouette

The silhouette is a tiered, lopsided ink heap. It is distinct from the pink jelly's single dome and from the acidic jelly's three low lobes.

- **Spill pool:** an irregular ink spill, not a disc.
  - Broad lobes, six narrow drip tongues and a forward feeding tongue.
  - Three places where the pool retreats almost to the heap.
  - A thickness that varies from thin sheets to beaded lobes.
- **Pour fillet:** a concave curve rising from the pool.
- **Flanks:** steep and sagging.
- **Curtain folds:** eight melting folds of varied width and length. They meander down the flanks and each drops a heavy teardrop pile onto the pool.
- **Crest:** it leans back and to one side. There is a second heap at the back right and a broad slump bulge on the camera flank.
- **Tar blisters:** five small blisters.

The rest extents are 53.26 x 50.66 x 25.21 units: wide, low and heavy. Every size is an art choice, not a Brogue fact.

### Paint

The paint is opaque, 1024², and evaluated on the sculpt's own (azimuth, V) parameters.

- **Body:** near-black ink. The median texel luminance is about 14.
- **Fake subsurface:** a deep violet core sits in the thick belly, piles and folds, clouded by near-black density.
- **Inclusions:** suspended black inclusions with violet halos, plus a few faint bubbles.
- **Painted occlusion:** grooves beside the folds, fold roots, the crest crease and the pour fillet are the darkest ink.
- **Reflections:**
  - banded ceiling reflections on upward faces;
  - crisp white-lavender specular pools, broken into curved "vault rib" bands so a broad lobe never carries one flat blob, and halved on the broad slump bulge;
  - glossy lines down each fold that bead on its pile;
  - faint teal/magenta thin-film fringes around the highlights.
- **Spill pool:** a dark mirror.
  - Its meniscus catches light only in scattered glints along the edge, which separates the ink from the floor without a continuous rim.
  - The specular map is dull across the pool and bright only at those glints, so the shader sheen follows the same pattern.

### Material and shader

The runtime material is the new owned shader [`shaders/black-jelly-sheen.fp`](../mod/BrogueDoom/shaders/black-jelly-sheen.fp), declared in `ownedFiles`. It combines normal and specular maps (glossiness 64, level 1.1, so UZDoom's specular light mode is used) with two terms added to the lit base colour:

- a view-dependent Fresnel rim sheen;
- a soft reflected-vault term.

Both terms are gated by the squared specular map. There is no `Bright`, no emission, no timer and no RNG, so the sheen darkens with sector light like the rest of the scene.

The actor uses the default gameplay-inert `BrogueMonsterProxyBase`. There are no render-style, alpha, light or particle changes.

## Construction and rig

- **Surface:** `build_parts()` emits one analytic closed latitude/longitude surface (192 x 112, with the UV seam at the back). The shared connected-skin bake fuses and decimates it into 7,084 runtime vertices and 14,000 triangles (`SKIN_FACE_BUDGET=14000`, default voxel size).
- **Deterministic cleanup:** `geometry()` then post-processes the bake without moving any vertex.
  - **Cap flips:** a longest-edge flip removes decimation cap triangles, meaning any angle above about 153°. A flip is kept only when both new triangles are well shaped and keep the surface orientation, so every flip strictly reduces the number of caps.
  - **Exact weights:** weights are recomputed analytically from each baked vertex's rest position. The shared bake's five-pass weight relaxation blurred the height blend enough to fold about 2,000 triangles in the flattening death. Position-only weights are exact and identical at every UV-seam copy.
- **Bones:** 58 translation-only bones, all at unit scale:
  - the root;
  - three 16-anchor rings at heights 2.5, 9 and 15.4, fine enough for a narrow pseudopod;
  - an 8-anchor ring at 21.2;
  - a leaning crest pole at 24.8.
- **Weights:** linear in rest height between rings and bilinear in azimuth, with at most four influences. They are quantized to 1e-6 with `math.fsum`, and the last influence takes the remainder. System Python and Blender's Python gave different `sum()` roundings here.

## Clips

Idle and ooze loop. Every action clip's key pose sits on its gallery-sampled middle frame.

- **idle (48):** heavy breathing, with slump-and-bulge, a ripple down the flanks and crest sway.
- **ooze (32):** a front-to-back peristaltic wave; the tongue reaches ahead.
- **slime (26, attack):**
  - The heap rears back.
  - At mid-clip a long pseudopod lunges out of the front to X = 29.9, near the +X cell limit. It is lifted off the pool and pinches at the tip.
  - The heap crouches low behind it (mid height 17.9 against 25.2 at rest), leans in and thins at the flanks.
  - The surge is broad, so the gallery's front and side sample (frame 9) already shows most of the lunge.
- **drench (30, alternate attack):**
  - The heap squats, then at mid-clip rears into a narrowing wave 44.7 units tall, 1.77 times its rest height.
  - The crest hooks forward over its own front, so its underside shows.
  - It then slaps down and spreads.
- **recoil (16):** at mid-clip it is squashed down and back, then jiggles.
- **collapse (40, death):** the crest folds first, and at mid-clip the heap is half slumped. It then spreads into a flat ink puddle.
  - Each anchor moves to its own image under a monotone map: height becomes 0.75 + 0.17z, the spread grows with height, and the edge is irregular.
  - Because the weights are linear in rest height, no flank folds through another.

Hit and death are cosmetic. Clones appear only when Brogue creates them, through the existing stable bridge IDs. The native selector alternates the two attack clips, and the bridge does not distinguish Brogue's verbs.

## Verification (Phase 1)

Evidence is in `artifacts/creature-queue/BRG-M52/`.

- **Cold connected-skin bakes:** two runs with Blender 5.2.1 and `--threads 1` produced identical `connected-skin.json.gz` sha256 `0724723347a90336aafeef7173adf92871f4855beff17e4edd0e1cca6c3b3c97` (`cold-bake-1.log`, `cold-bake-2.log`).
- **Blender source:** `blender_skeletal.py` built `assets/monsters/black_jelly/black-jelly-animated.blend` with 58 bones, one part and six clips, and a fresh reopen succeeded (`blender-build.log`).
- **Runtime bytes (sha256 prefixes):**

  | File | sha256 prefix |
  | --- | --- |
  | `52_black_jelly.iqm` | `303fa5c2dd199f6c` |
  | `BRGBKJLY.png` | `a483001f0ccde437` |
  | `BRGBKJLY_N.png` | `b528931a799ed831` |
  | `BRGBKJLY_S.png` | `566d304f80d1776a` |
  | `black-jelly-sheen.fp` | `afa33ab70f502d9b` |

- **Previews:** `review_skeletal --preview --all-angles --distances` at 1920x1080 captured 34 poses on each backend. The results are `preview-vulkan-contact.jpg` and `preview-opengl-contact.jpg`. `preview-vulkan-keyposes.jpg` crops:
  - the front idle;
  - the oblique slime key, plus the front and side slime frames;
  - the drench, recoil and collapse keys;
  - the 192-unit view.
- **Early review:** `early-review-violet-vulkan-contact.jpg` is the rejected first pass. It read as a lavender/amethyst jelly with a pale plate apron.
- **Tests:** `python -m unittest tools.monster_models.test_black_jelly` ran 11 tests and all passed, in 94 s (`tests.log`). They cover:
  - a closed connected manifold, and a bake that matches the current sculpt;
  - no triangle degenerating or flipping in any frame of any clip;
  - a ±31.5 cell bound for every frame, floor contact, and roots equal to the raw poses;
  - proportions and the spent puddle;
  - folds, piles and the spill lip between folds;
  - an irregular pool: outline range above 4 units, lip thickness ratio above 1.8, and at least six drip lobes;
  - key poses on the middle frames:
    - slime reaches beyond X = 29, crouches more than 4 units and leans the upper mass forward;
    - drench is 1.6–2 times the rest height, with more than 40 downward-facing triangles high on its front;
  - loops, rest starts, weights and identical seam copies;
  - jet-black but readable paint, and a seamless meridian;
  - the shader contains no `Bright` and no timer, and the pending row and GLDEFS snippet are consistent;
  - exact bytes.
- **Not run (coordinator Phase 3):** shared suites, regeneration, native build, packaged galleries, determinism records, preservation audit and the natural encounter.

## Revision after coordinator review

The coordinator accepted the look and asked for two fixes:

1. **Attacks that read.** The slime pseudopod and the tall curling drench wave above replace the earlier modest smear and rise.
2. **A spill pool that is not a saucer.** The pool now has an irregular outline and variable thickness, and its meniscus shows only as broken glints.

The slump-bulge highlight was also halved, which was optional.

Along the way I found and fixed a bug: a reused variable name had silently cancelled the pool's thickness variation. Three checks in my own tests were re-scoped for the new design:

- **Gloss fraction:** lowered to above 0.15% of texels over 170, after the slump-highlight reduction. The check for more than 1.5% above 120 is unchanged.
- **Slime upper-mass lean:** now more than 3.0 units, because the lunge is now carried low by the pseudopod.
- **Lip-over-flank check:** now skips the deliberate pool retreats.

## Files

- **Source:** `tools/monster_models/black_jelly_animation.py`, `black_jelly_materials.py` and `test_black_jelly.py`.
- **Assets:** `assets/monsters/black_jelly/`, holding `animation.json`, `connected-skin.json.gz` and the `.blend`.
- **Runtime:** `mod/BrogueDoom/models/monsters/52_black_jelly.iqm`, `mod/BrogueDoom/graphics/BRGBKJLY.png` with its `_N` and `_S` maps, and `mod/BrogueDoom/shaders/black-jelly-sheen.fp`. All names were checked for collisions first.
- **Pending registration:** `assets/monsters/skeletal_pending/MK_BLACK_JELLY.json` and `MK_BLACK_JELLY.gldefs`.

## Known limitations

- **Head-on slime:** from the front camera the pseudopod is foreshortened. The slime reads there mainly as a low, wide crouch with a forward bulge. It reads as a clear pointed lunge from the oblique and side cameras.
- **Drench from the side:** the gallery samples drench only at the oblique angle. The curl is proven numerically (the underside-triangle test) but has no dedicated side capture.
- **Violet in rear views:** rear views read more violet than black, because fewer painted highlights face them.
- **Fixed highlights:** painted highlights are fixed on the texture. Only the shader rim and vault terms respond to the view.
- **Bake weights unused:** runtime weights are analytic. The bake supplies only the fused topology and pigment UVs.

## Coordinator package archive

The coordinator returned the first delivery (attacks indistinguishable from idle at gameplay scale, a pale saucer-like spill rim) and accepted the lunging pseudopod, curling drench wave and irregular wet meniscus. At gate time the creature test was changed to read its profile through `skeletal_registry.find` and to fall back to the integrated `mod/BrogueDoom/GLDEFS`, because integration consumes the pending row and snippet. Round A was integrated and gated as pipeline batch `A` with the dar priestess, dar battlemage, goblin warlord, black jelly and unicorn (`artifacts/creature-queue/batches/A/gate-summary.json`: 87 tests OK, preservation audit with zero unexpected changes). Both final review packages (`761572a54dbd32a91407ca9cc82a4a7f5c6007f9919d70a01de10d5acc193dba`, 1,199 entries, shared by the batch) were compared entry-by-entry with current source (`parent-final-package-verification.json`) and losslessly archived after coordinator review of the final Vulkan and OpenGL galleries. Natural encounter gates are deferred to the later deeper-route census. Restore the exact Vulkan package with:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M52/final-vulkan/ProjectBroom-review.pk3.archive.json
```

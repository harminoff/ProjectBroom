# Unicorn model and animation

Presentation-only BRG-M63 / MK_UNICORN (queue #53). Brogue CE remains authoritative.

## Source facts

Brogue's prose: the unicorn's flowing mane and tail shine with rainbow light, its horn glows with healing and protective magic, and its eyes implore you to always chase your dreams ([Globals.c L1377](../src/brogue-mapgen/src/brogue/Globals.c#L1377)). The catalog row ([L1155](../src/brogue-mapgen/src/brogue/Globals.c#L1155)) gives white glyph colour, the large flag, `BOLT_HEALING`, `BOLT_SHIELDING`, `MONST_MAINTAINS_DISTANCE`, `DF_RED_BLOOD` and `DF_UNICORN_POOP`; its attack verbs are "pokes", "stabs" and "gores". Its only horde row is a legendary ally allied with the player.

Healing and shielding bolts, allegiance, distance keeping, the unicorn light, turns, damage and RNG are all Brogue-owned. Nothing here changes gameplay, AI, collision, spawn, visibility or the bridge ABI. The horn's gilded paint and the rainbow mane are paint only: no light, particle, brightmap or emissive shader is added.

Art interpretation (not Brogue facts): a slender white equine built from the accepted centaur's horse half, with a refined, collected head, a gilded two-start spiral horn, rainbow-shaded mane and tail (from the prose), dark lashed eyes (from "eyes implore"), gilded hooves with a painted cleft and silky fetlock feathering. The glyph's white is the coat.

## Delivered files

- Generator: `tools/monster_models/unicorn_animation.py`; materials: `tools/monster_models/unicorn_materials.py`; tests: `tools/monster_models/test_unicorn.py`.
- Runtime: `mod/BrogueDoom/models/monsters/63_unicorn.iqm`, `mod/BrogueDoom/graphics/BRGUNI.png` (2048², new lump; checked free of collisions).
- Manifest, cage and source: `assets/monsters/unicorn/animation.json`, `connected-skin.json.gz`, `unicorn-animated.blend`.
- Pending profile row: `assets/monsters/skeletal_pending/MK_UNICORN.json`. No GLDEFS snippet.
- The static `63_unicorn.obj`, `BRGM63.png` and `sources/63_unicorn.blend` are untouched.
- No shared module was edited. Family helpers (`torso_loft`, easing, `hash3`/`vnoise`/`encode_png`) are imported read-only from `centaur_animation`/`centaur_materials`. The connected-skin selection, voxel size (0.2) and face budget (9,800) are declared in the unicorn module.

## Construction

- **Rig:** 37 bones:
  - root, pelvis, barrel and withers;
  - three neck bones, the head (at the poll) and two ear bones;
  - six mane bones, three per side, each a child of its neck bone, for secondary sway;
  - four 4-bone legs, as on the centaur;
  - five tail bones.
- **Clips:** six clips (see Clips below). Rest extents are about 57.9 × 18.8 × 66.7 units.
- **Connected skin:** one closed component (4,923-vertex cage, 9,850 faces) carries:
  - a rounder, lighter lofted trunk with a deep girth, a belly line that curves up into a tucked flank, and a rounded croup;
  - an arched neck;
  - a head lofted along a 60°-down face axis: dished profile, round jowls, cheek ridges, orbit ridges, soft nostrils, lip and chin;
  - shoulders, breast, thighs, buttocks and slender legs. The forearm and gaskin tops are lofted up into the body so there is no ball-joint read at elbow or stifle.
- **Accessories:**
  - eyes with an iris, a glint, upper and lower lids, a lash line and four lashes;
  - cupped ears with pink-grey inner ears;
  - the horn: 56 rows by 24 sides with a helical ridge, and a painted groove on the same helix phase;
  - 16 broad, overlapping, flattened mane locks, most on the left, and a four-lock forelock parted round the horn;
  - a 15-lock tail;
  - gilded hooves and nine feather strands per fetlock.
- **Coat paint** (rest-coordinate, per-triangle islands, as the centaur): painted top light, a barrel value gradient from a bright back to a lavender-grey lower flank, and deep occlusion under the belly, inside the legs, in the armpit, groin and throat. Other features:
  - dark separation lines behind the shoulder blade and in front of the haunch;
  - a triceps line, flank fold, quarter groove and jugular groove;
  - a darker barrel-to-leg band;
  - lower legs graded darker from knee and hock down to the fetlock;
  - faint pearl dapples and a slight rose/blue sheen.

  The face has dark grey eye rings, a grey-lilac muzzle, nostrils, a mouth line, jowl edges and under-jaw shadow. Measured pigment brightness: back 246, mid flank 190, belly 127, upper cannon 211, fetlock 146.
- **Mane and tail:** locks shade from pearl roots through pastel rainbow hues. The three hue phases are within 0.1 of each other, and all locks share one sheen band and a shadowed inner face, so overlapping locks read as one hair mass rather than feathers.

## Clips

Each action's key pose is on its middle frame (the gallery samples first, middle and last).

- **idle (48 frames, loops):** breathing, head turn and nod, and an ear flick. The weight shifts off the right hind, which rests on its toe, and the tail and mane sway.
- **trot (32 frames, loops):** an elevated two-beat diagonal trot with 56% stance, high knee action, head bob, tail and mane sway.
- **gore (36 frames):** gathers back, then the head tucks and the neck turns aside so the horn levels into a hooking thrust (middle frame). All four hooves stay planted. If the tip would pass x = 30.6, the body is automatically pulled back.
- **rear_strike (40 frames):** rears about 30° on planted hinds, forelegs IK-tucked under the chest and pawing (middle frame). It then drops and drives the horn low and aside.
- **flinch (14 frames):** shies back and sideways, with the head thrown up and away, ears pinned and tail clamped.
- **fall (46 frames):**
  1. The knees buckle over planted hooves, head tucked aside.
  2. The body rolls 84° onto its right side along a lifted path.
  3. It ends with all four legs lying limp toward the gallery camera, knees loosely bent, upper pair ahead of the lower pair.
  4. The neck lies limp along the floor, the head on its cheek with the horn flat, and the mane settles over the uppermost neck side.

  The final maximum height is under 19 units.
- Gore, rear_strike and flinch settle exactly into idle's first frame.
- No clip uses automatic floor lift: every exported frame equals its raw pose, stays inside the centred ±32 cell, and has minimum Z ≥ 0.07.

## Review iterations

The first engine preview drove these changes:

- A painting defect let the face paint reach the back, which read as a hollow back. It was fixed by bounding the head frame.
- The feather-like mane of 28 narrow ribbons became 16 broad overlapping locks with a shared sheen.
- The gore's horn overhung the cell. The thrust became a head tuck with a neck turn, plus the automatic pull-back.
- Rear-strike forelegs dipped through the floor during the descent. They were changed to IK tucks.
- The death first showed only the back (a white lump with the horn). The roll side was flipped and the legs laid out limp.

The coordinator then asked for stronger value contrast, which was done by:

- adding the flank gradient and belly occlusion;
- adding the muscle separation lines and the barrel-to-leg band;
- darkening the leg grading;
- curving the belly line.

## Verification (phase 1)

Evidence is in `artifacts/creature-queue/BRG-M63/`.

- **Cold bakes:** two isolated `--threads 1` Blender 5.2.1 bakes (`cold-bake-0.log`, `cold-bake-1.log`) produced byte-identical `connected-skin.json.gz`, SHA-256 `c87d24e207f16fd93449198801df2c7cc3c69bfed3474fe44434e0b551c5144f`, with identical cage hashes at every stage.
- **Exports:** two fresh-process exports were byte-identical (`export-0.sha256`, `export-1.sha256`):
  - IQM `624338cc3e4fc432f59917a6e12a4b4b21f4a9fc5714f3e62a68c360a4914335`
  - PNG `1b5850134aec92ee3f2d348a57da32040632ca3eeadc8f39eef972ce3698fa2b`
- **Blender source:** `blender_skeletal.py -- MK_UNICORN` built and fresh-reopened the source: 37 bones, six clips, `freshReopen: true` (`blender-build.log`).
- **Tests:** `python -m unittest tools.monster_models.test_unicorn`: **7 tests passed in 119.5 s** (`tests.log`). The tests cover:
  - a closed connected skin with seam equality and at most four normalised weights;
  - the six roles, loop closure, action recovery, cell clearance and no floor compensation;
  - planted, level, non-sliding hooves, with lifted hooves above their support, diagonal trot pairs and high rearing forelegs;
  - the horn tip inside the cell in every frame, and the gore's middle frame levelled at least 35° below rest;
  - the fall on its right side with the head on the floor and every hoof off its support;
  - painted underside, flank and leg grading, and accessory UV isolation;
  - exact runtime bytes.
- **Previews:** 34 preview captures per backend at 1920×1080, fixture-local, unpackaged:
  - Vulkan: `preview-vulkan/`, `preview-vulkan-contact.jpg`
  - OpenGL: `preview-opengl/`, `preview-opengl-contact.jpg`
  - Front idle `31-idle-0.png`, attack `08-gore-18.png`, death `18-fall-45.png`.

Not run in phase 1 (coordinator gate): integration, the native build, packaged galleries, shared suites and the preservation audit. No natural encounter, standalone comparison or user art approval.

## Known flaws

- Under the engine's bright flat light the coat still reads light overall at 192 units. Form now comes mainly from the lavender flank and the dark underside rather than muscle detail.
- From the oblique gallery camera the right side is visible, so most of the mane (on the left) shows only past the neck.
- The mane is rigid per lock between mane bones. At extreme neck yaw (gore, rear_strike) some locks shear slightly.
- The trot slides stance hooves backward in body space, as the centaur and other gaits do. It does not match world travel speed.
- In the fall, the head lies partly under the horn line from the rear view, and the upper and lower legs overlap near the knees.
- The idle hind hoof toe rest is subtle at distance.

All art is original Project Broom content under CC-BY-SA-4.0; no third-party assets were imported.

## Reproduction

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --threads 1 --factory-startup --disable-autoexec --python-exit-code 1 --python tools/monster_models/blender_skin.py -- unicorn
python -m tools.monster_models.unicorn_animation
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --factory-startup --disable-autoexec --python-exit-code 1 --python tools/monster_models/blender_skeletal.py -- MK_UNICORN
python -m tools.monster_models.review_skeletal --symbol MK_UNICORN --backend 1 --preview --all-angles --distances --width 1920 --height 1080 --output artifacts/creature-queue/BRG-M63/preview-vulkan
python -m unittest tools.monster_models.test_unicorn
```

## Coordinator package archive

The coordinator returned the first delivery (near-flat white coat reading as a tube, straight belly, feather-like mane, a compact death lump hiding the legs) and accepted the painted coat form, curved belly, broad mane masses and limp side-lying death with visible legs. Round A was integrated and gated as pipeline batch `A` with the dar priestess, dar battlemage, goblin warlord, black jelly and unicorn (`artifacts/creature-queue/batches/A/gate-summary.json`: 87 tests OK, preservation audit with zero unexpected changes). Both final review packages (`761572a54dbd32a91407ca9cc82a4a7f5c6007f9919d70a01de10d5acc193dba`, 1,199 entries, shared by the batch) were compared entry-by-entry with current source (`parent-final-package-verification.json`) and losslessly archived after coordinator review of the final Vulkan and OpenGL galleries. Natural encounter gates are deferred to the later deeper-route census. Restore the exact Vulkan package with:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M63/final-vulkan/ProjectBroom-review.pk3.archive.json
```

# Salamander model and animation

Presentation-only BRG-M29 / MK_SALAMANDER. Brogue CE remains authoritative.

The source describes a serpent wreathed in flames carrying a burning lash, dwelling in lava and leaving embers. Existing verbs are whips/lashes. Fire immunity, submergence, extended attacks, terrain embers, damage, AI, visibility, collision and RNG remain Brogue-owned. No gameplay or ABI change.

Original art interpretation: coal-dark copper-scaled serpent, broad swept reptilian skull, ember eyes, a thick asymmetrical grounded coil, narrower upright torso and two arms inferred to physically hold the named lash. The right hand closes around its dark handle; a jointed glowing lash curls ahead of it. Separate licking flame volumes wreath the back, shoulder and coil. Opaque body and mesh-local emissive flame atlas regions retain Normal actor style; no world light, additive whole-body transparency or persistent trails.

Six cosmetic roles: idle, slither, whip, lash, recoil, collapse. Only idle/slither loop. The upper anatomy folds into the coil; flames contract fully and the held lash settles. Unit-scale bones and no automatic whole-root floor lift are required.

Planned proof: closed fused organic skin, normalized weights, centered every-frame bounds, grip attachment/recovery/extinction and grounded collapse; two cold single-thread bakes/exports; fresh Blender 18 poses; native compile/fingerprint; early front/lash/death engine review followed by both packaged 34-view galleries and clearly synthetic lava fixtures. Unchanged 2000-seed census found no kind29 and is not repeated. Natural lifecycle, standalone comparison, physical play, frame-time benchmark and user art approval remain separate open gates.

All new art is original Project Broom content under CC-BY-SA-4.0.

## Delivered artwork and rendering

Master geometry, original texture and poses are in `tools/monster_models/salamander_animation.py`.
The source body uses a closed fused organic cage. The broad swept skull, closed right-hand grip,
dark articulated cord and eighteen overlapping curled flame volumes distinguish it from naga.
The 104-bone rig has six clips and 12,648 runtime UV-split vertices / 24,084 triangles.
Rest extents are 43.6199 x 44.3444 x 62.7797 map units; these are artistic dimensions.

The 1024-square diffuse uses continuous surface-aware ventral coordinates and tail-centerline
scale placement. The narrow flame atlas region alone receives mesh-local emission from
`mod/BrogueDoom/shaders/salamander-flame.fp`. The actor remains Normal/1.0; its opaque body,
hand and cord do not inherit additive flame rendering. No separate light, trail actor,
collision, damage, AI or Brogue RNG call is introduced. Renderer-time flicker changes only
flame brightness. The existing displayed-class visibility restoration remains unchanged.

Each flame pair uses an eight-corner affine cage, at most four normalized influences and
unit bone scale. All flame volumes contract below 0.003 units during death. The final corpse
is a **folded coil** with lowered head and tucked limbs, not a flat stretched snake. Its
maximum height is 24.5469 units. Every raw pose stays above the floor, and every exported
root transform equals its raw transform exactly: zero automatic whole-root lift. Upper-body
contact correction is limited to the folding waist; the grounded lower coil is unchanged.
Every frame remains within X -19.55791..31.43833 and Y -23.63972..22.09342; minimum Z is 0.22711.

Early review changed candle-like isolated flames into broad embedded paired tongues with
red/orange edges and yellow interiors, made the cord non-emissive brown, and lowered the
initial high-arched corpse. The initial flame cage also exposed out-of-box weights; the
larger explicit affine cage now satisfies normalization and near-zero extinction checks.
A later raw-pose regression caught slight floor contact and corrected the upper anatomy
rather than hiding it with a root lift. Intermediate art-test failure logs are retained; they are not final proof.
The first combined run additionally caught a legacy-static construction-cue change.
The original cue was restored without regenerating the old OBJ; this failure is summarized
in `pre-final-metadata-failure.txt` because its full log was overwritten by an interrupted rerun. The coordinator accepted the final wreath and folded-coil death for
technical freeze. Close-up scale stretching, flame gradient banding and layered flame
surfaces remain visible; individual user art approval is still pending.

Editable packed source is `assets/monsters/salamander/salamander-animated.blend`.
`tools/monster_models/blender_salamander.py` uses the shared isolated authoring path then
adds a matching atlas-local emission preview. Blender remains a preview rather than a
pixel-identical reproduction of the engine material.

## Tests

**58 tests passed in 290.904 seconds** (`final-tests.log`):

```powershell
python -m unittest tools.monster_models.test_salamander tools.monster_models.test_skeletal tools.monster_models.test_connected_skin tools.monster_models.test_creatures tools.test_broguedoom_resources
```

The nine Salamander tests cover closed connected anatomy/open coil/separate hands,
normalized weights and seam equality, every raw/exported frame's centered bounds and
zero root lift, six role/loop/recovery rules, lowered head/tucked limbs, ventral and
centerline pigment mapping, exact runtime/texture bytes, the held closed grip and
atlas-local opaque-body/emissive-flame contract with complete visual extinction.

## Frozen-byte verification

Evidence is under `artifacts/creature-queue/BRG-M29/`. Only `final-*` files apply to the
accepted bytes; early/refined/wreath/collapse/grounded galleries document iteration.

- Two separate single-thread cold connected-skin bakes and runtime builds reproduced the
  cage, IQM, diffuse, manifest, shader and GLDEFS byte-for-byte (`final-determinism.json`).
  Blend-file byte determinism is not claimed.
- Isolated Blender 5.2.1 rebuilt the source. A separate fresh process reopened the final
  file and verified all six Actions, 104 bones, 18 poses, exact packed skin bytes and no
  linked libraries. Maximum vertex difference was 0.0000241487 units
  (`final-blender-verification.json`). The known extension-cache warning was nonfatal;
  no live user Blender document or global setting was changed.
- Native compilation passed with `python tools/run_native.py cmake --build .build/uzdoom
  --config Release -j4` (`native-build.log`). The build fingerprint was recorded after
  linking and validated against final native inputs/outputs (`final-native-fingerprint.json`).
  Only the generated kind29 profile row changed native input; no bridge, ABI, frontend
  visibility, wall-mount or pending-map lifetime code changed.
- `final-vulkan/` and `final-opengl/` each contain 34 actual 1920x1080 packaged captures:
  static before, all six clips, front/side/rear/oblique and 64/128/192-unit views. Both
  exited zero and all subjects reported `blocking=0`. Both full contact sheets plus
  representative full-size front, action, death and lava images were inspected.
  There were no new model/material/resource errors; existing engine menu/minimap warnings
  remain. Both deterministic packages match, and every one of their 1,170 entries equals
  current source (`final-package-verification.json`). The coordinator independently
  confirmed all entries (`parent-final-package-verification.json`).
- Both `final-lava-*` fixtures produced six actual captures: three distances, hidden,
  sensed and sampled lash. The opaque non-solid lava surface occludes the lower coil;
  hidden removes the actor and sensed uses translucent presentation. The fixture reuses
  the canonical liquid construction and -12-unit lava bed in an isolated ART01 room.
  It sets presentation flags directly; it does not exercise native Brogue visibility
  transitions, actual lava emergence, burning terrain or combat timing.

```text
IQM 1a1eccc70e63fdc698b96f967b12c2eda507c285b985878dad96b4988699103f
PNG ecf3bf10d2f40ff34ed1b1b90dec7aba036b4a245338a086c3ee2d67c9fe0b85
PK3 b26bbe7c6c9a243d5f72526272d00319ffa225d87ea13989a4727cb87922403d
```

## Remaining acceptance

No natural Salamander encounter was obtained. The existing completed census covers
seeds 1-2000 and contains no kind29; its conservative surviving route did not reach the
ordinary hostile range of depths13-20. The unchanged search was not repeated, and no
health, spawn, reveal, terrain or action overrides were introduced. This is recorded in
`natural-encounter-status.json`. Gallery lash poses do not prove native combat event timing.

Natural emergence/submergence, fire/ember trails, actual attacks/hits/death, physical input
and play, standalone comparison, controlled frame-time benchmarking, full release-installer
packaging and user art approval remain open. The evidence proves deterministic authored
assets and synthetic renderer presentation, not those broader acceptance gates.

## Reproduction

```powershell
python -m tools.monster_models.salamander_animation
python -m tools.monster_models.review_skeletal --symbol MK_SALAMANDER --backend 1 --packaged --all-angles --distances --width 1920 --height 1080 --output artifacts/creature-queue/BRG-M29/reproduction-vulkan
python -m tools.monster_models.review_salamander --backend 1 --package artifacts/creature-queue/BRG-M29/reproduction-vulkan/ProjectBroom-review.pk3 --output artifacts/creature-queue/BRG-M29/reproduction-lava-vulkan
```

Use backend0 with separate output directories for OpenGL. The artifact-local
`prove-determinism.py`, `verify-fresh-blender.py` and `final-evidence.py` reproduce their
respective checks. Build the editable source with isolated background Blender and
`--python tools/monster_models/blender_salamander.py`.

[Final Vulkan gallery](../artifacts/creature-queue/BRG-M29/final-vulkan-contact.jpg),
[OpenGL gallery](../artifacts/creature-queue/BRG-M29/final-opengl-contact.jpg),
[synthetic lava](../artifacts/creature-queue/BRG-M29/final-lava-opengl-contact.jpg).

## Preservation

The immediate raw-byte baseline covered 681 files. Final audit shows 671 unchanged,
10 intended shared/assigned changes, zero missing (`preservation.json`). All 29 previous
skeletal profiles, 67 other bestiary/monster-registry entries, every other raw creature
card and every other model-index row remain intact. Prior mixed line endings were
preserved from the immediate byte backups; nothing was restored from git HEAD.
The old Salamander static OBJ/PNG/Blend references remain byte-identical.

Shared changes are limited to the salamander connected-skin selector, assigned bestiary
verification/card/model-index row, skeletal profile/monster registry and generated
MODELDEF/ZScript/native clip row, plus the selective-emission GLDEFS declaration. All new
model source, tests, shader, texture, IQM, packed Blend, cage and report are Salamander-only.
The native frontend, bridge, model-queue files and coordinator REVIEW.md were not edited.
No cleanup, commit, publication or next creature was started.

## Coordinator package archive

Both final review packages were losslessly archived after independent comparison of all 1,170 entries and final image inspection. Restore the exact Vulkan package with:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M29/final-vulkan/ProjectBroom-review.pk3.archive.json
```

Use the equivalent final-opengl manifest for that backend. Archive reconstruction was hash-verified before compacting; captures, logs, manifests and shared content blobs are retained.

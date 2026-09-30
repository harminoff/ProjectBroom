# Dar blademaster model and animation

Presentation-only BRG-M31 / MK_DAR_BLADEMASTER. Brogue CE remains authoritative.

## Source, art and planned proof

Pinned Globals.c describes an elf of the deep, frightening leaps and deadly
swordplay, with grazes/cuts/slices/slashes/stabs. Magenta is its glyph identity,
not a whole-body material. Blinking, corridor avoidance, combat, turns, health,
visibility and RNG remain entirely in Brogue. No native behavior or ABI change
is planned.

Original art: a lean ash-skinned elf with a narrow sculpted face, swept pointed
ears, dark swept hair, fitted charcoal armor, silver edges, magenta sash and
a narrow steel sword held by four curled fingers and a thumb. Clothing, skin,
armor, handedness and dimensions are artistic interpretations. Connected body
anatomy establishes reusable dar proportions without authoring other dar forms.
Six cosmetic roles: idle (studying), advance, slash, thrust, recoil and fall. Only the
first two loop. Movement and attacks never launch gameplay independently.

Planned proof: closed connected anatomy and continuous pigment; normalized
weights, attached grip, planted support, every-frame centered clearance;
two cold cage/runtime builds; fresh-open background Blender with 18 sampled
pose comparisons; native build/fingerprint; early engine art review followed
by packaged 1920x1080 Vulkan/OpenGL 34-view galleries. Natural encounter is
unresolved after the coordinator's ordinary-intent search through seeds 1–2000;
the unchanged route will not be repeated. User art approval remains separate.

All new geometry and textures are original Project Broom art, CC-BY-SA-4.0.
No third-party artwork is imported.

## Delivered art and motion

Master sources are `tools/monster_models/dar_blademaster_animation.py` and
`dar_materials.py`. The module contains reusable ring-sculpt and two-link leg
solver functions; its explicit lean dar proportions, facial contours and ear
construction can support future family work without copying ogre proportions.
No priestess or battlemage asset was authored.

The editable source and connected cage are under
`assets/monsters/dar_blademaster/`; runtime resources are
`mod/BrogueDoom/models/monsters/31_dar_blademaster.iqm` and
`mod/BrogueDoom/graphics/BRGDAR.png`. The static OBJ/skin/Blend remain unchanged.
There are 18 bones, 44 parts, 23,062 runtime vertices and 16,902 triangles;
the closed fused cage has 2,803 vertices and 5,602 triangles. Eyes, mouth,
hair, armor, sash and sword remain separate where their anatomy requires it.
The original 2048-square diffuse atlas uses continuous rest-position pigment
and sculpt shading across the connected skin; there is no emission or light.

Rest dimensions are 12.2682 / 21.1153 / 60.6471 map units, purely art choices.
Every animation frame remains within centered X -22.4756 to +26.4542 and
Y -11.4988 to +11.6143; minimum floor height is 0.1734. Maximum height is
60.8205. No exported frame uses automatic floor compensation or bone scaling.
The 60% stance / 40% recovery advance keeps at least one support foot planted.
Both feet remain supported in the collapsed pose, with a bowed torso, drooped
head, hanging arms and the sword lowered behind the body. Its settled height
is 32.4299; this is a collapsed kneel, not a prone corpse. Sword and gripping
hand share an attachment transform throughout all clips.

The idle uses a shallow bent-knee staggered stance. Slash and thrust are
cosmetic alternatives and do not claim an exact Brogue attack verb. They do
not create a blink, choose a target, launch damage or consume a turn.

Early actual-engine review found the mouth recessed into the face, upper
cuirass overlap and a flat hair crown. Final art moves the mouth to the visible
surface, expands the plates and adds a fitted collar, corrects torso weights,
and tapers the rounded swept hair. Deltoid skin remains exposed around the
separate shoulder plates by design. Subtle polygon banding remains at very
close range; no exhaustive self-intersection or individual user art approval
is claimed.

## Reproduction

```powershell
python -m tools.monster_models.dar_blademaster_animation
python -m tools.monster_models.skeletal_registry
python -m tools.monster_models.generate
python -m tools.monster_models.bestiary
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --disable-autoexec --threads 1 --python-exit-code 1 --python tools/monster_models/blender_skeletal.py -- MK_DAR_BLADEMASTER
python -m tools.monster_models.review_skeletal --symbol MK_DAR_BLADEMASTER --backend 1 --packaged --all-angles --distances --width 1920 --height 1080 --output artifacts/creature-queue/BRG-M31/reproduction-vulkan
```

Use backend 0 and a fresh output directory for OpenGL. Regenerating bestiary
cards must preserve unrelated raw bytes from the immediate pre-task backup,
including mixed line endings. Do not restore cards from Git HEAD.

## Verification and evidence

Final evidence lives in `artifacts/creature-queue/BRG-M31/final-vulkan/` and
`final-opengl/`; `early-vulkan`, `refined-vulkan` and `approval-vulkan` are
superseded art-review evidence. Coordinator technical review accepted the
refinements; individual user art approval remains open.

- **54 tests passed in 170.157 seconds** (`tests-final-refreshed.log`):
  `python -m unittest tools.monster_models.test_dar_blademaster tools.monster_models.test_skeletal tools.monster_models.test_connected_skin tools.monster_models.test_creatures tools.test_broguedoom_resources`.
  Five dar tests cover closed manifold skin/seams, all four limb chains,
  normalized weights, every-frame centered bounds, zero floor compensation,
  loop closure, support feet, sword attachment and exact IQM/PNG bytes.
  The first run caught stale generated dimension metadata after refinement;
  regenerated bindings/registry fixed it before this passing rerun.
- Native Release compilation passed with
  `python tools/run_native.py cmake --build .build/uzdoom --config Release -j4`.
  The successful fingerprint was refreshed with
  `python tools/engine_source.py --root . --record-build .build/uzdoom/Release`.
  The only native source change is the generated K31 clip table row; subsequent
  art refinement changes no native contract. See `native-build.log`.
- Two cold single-thread Blender cage bakes and scoped runtime builds produce
  byte-identical cage, IQM, diffuse and animation manifest (`determinism.json`).
  No supplemental maps are used. Blender-file byte determinism is not claimed.
- Background Blender 5.2.1 freshly reopened the final source, six Actions,
  packed skin and zero linked libraries. All 18 source/runtime sample poses
  agree within 0.000011134 map units. See `blender-final.log` and
  `blender-verification.json`. The extension-cache permission warning is
  nonfatal; no live Blender document or global setting was changed.
- Both final galleries contain 34 actual 1920x1080 captures: static reference,
  sampled six clips, front/side/rear/oblique and 64/128/192-unit distances.
  Both contact sheets and representative full-size views were inspected.
  All 34 subjects per backend report `blocking=0`; both engines exit zero.
  Existing menu/minimap warnings remain; no new model/resource errors occurred.
- Both final packages are byte-identical and all 1,150 entries match current
  source bytes (`package-verification.json`). Before/after comparison and
  labeled contact sheets are saved alongside the full-size captures.

```text
IQM  0ca0ef10fb14d0266d29ccbdea9d81fbbd43ad0620656af78517cea00af5a444
PNG  b27224267dd3c3f22a6edd6ab19f4e1d030c10d3d562f3109936c19cac623dd4
Cage 796c6c443504d15d17f532fa7a9d45fb9de4893f49e7b4a7eed956b2ac274032
PK3  34a9cc7059af639898040eb9aa6beb893caeea22d3e339ebdc006e252e49cb11
```

## Natural encounter and acceptance limits

The coordinator's standard copied-snapshot route covers seeds 1–2000 with
1,500-action/depth-15 limits and found no directly visible kind31 candidate.
The 1,500-seed extension is recorded in
`encounter-preparation/dar_blademaster-search-501-2000.json`; this pass reads
and fingerprints that evidence in `natural-search-status.json` and does not
repeat the identical search. Brogue's ordinary dar hordes begin nominally at
depth10; ordinary survival and conservative route progression remain the
obstacle. This bounded failure does not prove encounters impossible.

No natural renderer encounter, creature HP/turn/hash, hostile lifecycle,
blinking, hit or death is claimed. No spawn, reveal, health or movement override
was used. Gallery poses prove rendering and attachment only. Natural encounter,
physical keyboard acceptance, standalone comparison, controlled frame-time
measurements, exhaustive animation/terrain coverage, release-installer package
and individual user art approval remain open. The full source-bridge batch
was not rerun for this scoped model addition; the handoff permits focused
model/resource suites plus the native compile. Launcher/network work is outside
this model task and was untouched.

## Preservation

The immediate baseline contains 1,479 files: 1,469 byte-identical, ten intended
shared changes and zero missing files. All 21 prior skeletal profiles, all 67
other bestiary entries and all 67 other creature cards are preserved. Card
backups and restorations preserve raw bytes including mixed newlines.
See `preservation.json`.

Shared changes are the dar connected-skin selector, dar-only bestiary traits
and report link, skeletal/bestiary/monster registries, K31 card/model index,
and generated MODELDEF, ZScript and native table. The native pending-map
barrier and wall-mount helper remain byte-identical. No queue, gameplay,
visibility, ABI, collision, AI, RNG or source generation rule changed. No
reset, broad cleanup, commit or publication was performed.

Reusable family lessons: keep the torso rigid through the armored chest and
blend at the neck; check connected-skin silhouette before attachment placement;
use continuous pigment across fused anatomy; round hair per strand across the
crown; test actual centered limits and real support rather than total width
or automatic floor correction.

## Review package archive

Coordinator independently checked final model, skin and bindings against both packages. Review packages are losslessly archived with SHA256-verified manifests; captures and logs remain directly available. Restore the final Vulkan package with:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M31/final-vulkan/ProjectBroom-review.pk3.archive.json
```

Use the corresponding final-opengl manifest for OpenGL.

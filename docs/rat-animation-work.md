# BRG-M01 rat: skeletal presentation work

Contribution: presentation only. Preserve the original rat reference and all
other creatures/weapons. Brogue's `Combat.c::attack`, `inflictDamage`, and
`killCreature` already report attempted attacks, damage and death through
`brogue_bridge_note_attack/damage/death`. `SyncMonsters` supplies authoritative
destination cells. No new ABI or gameplay hook is needed.

Expected behavior: rest -> scurry only after a copied position changes;
attempted attack -> bite/scratch cosmetic variation; damage -> recoil;
authoritative death -> collapse and removal. Animation cannot submit commands,
damage, collide, choose targets, consume turns or touch Brogue RNG. Preserve
the existing command-buffer/gating counters; a longer death visual must not
hold input or keep a gameplay creature alive. Hallucinated forms follow the
presentation kind, not undisclosed real identity. Level changes remove old
proxies. Hidden models remain hidden.

Proof planned: IQM structural/weight/clip/grounding tests; deterministic binary
regeneration; Blender fresh-open rig/action/packed-texture verification; native
compilation; existing resource/bridge/map suites; repeatable bridge sequences;
isolated engine clip captures and normal seed-one move/combat/death captures.
Before resources are preserved in ignored `artifacts/rat-animation/baseline/`.

The authored numerical scale remains about 51 x 18 x 15 map units in rest.
Idle sniff/breathing, a four-foot scurry, jaw bite, forepaw scratch, recoil and
side collapse are visual interpretations, not added Brogue abilities.

## Delivered implementation

- `tools/monster_models/rat_animation.py`: original anatomical rig, skin weights,
  120 sampled skeletal frames and deterministic generation.
- `tools/monster_models/iqm.py`: IQM v2 writer and independent binary-section
  reader. File axes stay X/Y/Z; V is flipped once. Clockwise file triangles are
  required because GZDoom reverses OBJ triangles but not IQM triangles.
- `assets/monsters/rat/rat-animated.blend`: 28 bones, 80 named anatomical parts,
  packed original diffuse texture, six editable Actions and separate studio.
  The original static `rat.blend`, OBJ and skin were preserved.
- `mod/BrogueDoom/models/monsters/01_rat.iqm`: 8,991 vertices, 15,916 triangles,
  at most two weights per vertex. The modest increase over the static reference
  provides a separate lower jaw, mouth recess and lower incisors.
- `generate.py` registers the IQM, `BaseFrame` and `DECOUPLEDANIMATIONS`. Missing
  authored files fail explicitly. Direct invocation used by the canonical
  Windows build now resolves the project package imports correctly.
- `brogue_bridge_frontend.cpp` calls the pinned engine's `SetAnimationInternal`
  after copied Brogue events and authoritative position changes. Existing
  movement/pulse/death gate counters remain unchanged. New pose/retention
  counters are excluded from `MonsterAnimationsActive()` and its `active` return.
  Administrative removal hides the rat without an additional physical collapse.

| Clip | Frames | Default FPS | Trigger / interpretation |
| --- | --- | --- | --- |
| idle | 40 | 20 | Cosmetic sniff/head motion, jaw and ear twitches, subtle tail motion; loops without consuming turns. |
| scurry | 16 | 40 in source | Copied destination changes; runtime cadence follows travel distance and the visual duration (`brg_rat_walk_tics` for visible ordinary steps), not simulation time. Alternating paws use a two-joint solve. |
| bite | 14 | 35 | Attempted attack, with an articulated jaw and forward head reach. |
| scratch | 16 | 35 | Cosmetic alternate attempted-attack pose, with a raised/reaching forepaw. |
| recoil | 10 | 35 | Copied damage event; subsequent ordered events may supersede it. |
| death | 24 | 35 | Copied physical death, flank collapse with turned neck and settling tail. Visual retained 26 tics including blending; original gate remains 7. |

No copied attack-verb field exists. The event sequence chooses between bite and
scratch purely for presentation; it is not claimed to match the randomly chosen
message verb. There is no attack hitbox, damage callback or independent AI.
Root grounding adjusts the whole skeleton, never individual mesh vertices.
It does not alter the actor's authoritative cell or create root-motion movement.

## Verification results

- Canonical Brogue/GZDoom source build passed. The initial direct CMake attempt
  hit Windows' duplicate `Path`/`PATH` environment issue; the canonical build
  script handles that normalization. No build-system replacement was introduced.
- **96 tests passed**, including six new skeletal tests: deterministic IQM bytes,
  reader structure, normalized weights, parent ordering, bind-pose reconstruction,
  quantized animation channels, clip coverage, bounds, normals/triangles, paw
  planting, bindings and exclusion of pose timers from gameplay input gates.
- Blender 5.2.1 LTS freshly reopened the source with all six Actions, one packed
  file image and no linked libraries. Eighteen sampled Blender poses match the
  Python skin deformation within 0.0001 map unit. All 120 frames were also
  rendered into local motion previews.
- **22 after and 22 matching before gallery captures**, including all clips'
  start/mid/end and four cardinal views. The before model is static; its repeated
  clip labels indicate matching review slots, not preexisting animations.
- **55 normal floor-one captures**: seed 1, three N, 25 W, N W, two WAIT, four W.
  Brogue rat ID 11 exercises scurry, scratch, bite, recoil and death. Turn 35
  reports the kill; the next normal command advances to turn 36 while the
  cosmetic collapse finishes. There are no moved/spawned/revealed test enemies.
- All **36 engine turn hashes, revisions and player coordinates** match the
  same headless Brogue sequence; repeated headless output is byte-identical.
  Final hash: `b7a257f2ef90e55f`.
- The requested 300-action headless long-run completed at Brogue's genuine death
  on turn 195 (revision 197), hash `605cf66657aa5f8e`. This is not 300 survived turns.
- Verified static-mod package: `artifacts/rat-animation/ProjectBroom-rat-animated.pk3`.
  It contains matching IQM/skin bytes and no Blender files. No release installer
  was rebuilt. Other creatures and held weapons retain their existing assets.

The gallery is a private `ART01` room with no Brogue session. Its camera and
sampled poses are diagnostic. The ordinary encounter uses the real player-eye
position and Brogue visibility; its separate camera hides only the player's own
reference model to avoid viewing it from inside. Contact sheets are central
crops; full engine images remain available. Blender studio lighting is distinct
from the flatter GZDoom environment lighting.

During review, a collapsed tail/whisker grounding defect and the IQM triangle
winding mismatch were corrected. Failed diagnostic-script launches were not
counted as evidence. Existing gallery texture/minimap warnings are separate
from new-asset failures; the completed runs had no missing animation/model errors.

## Review and reproduction

- [Scurry motion preview](../artifacts/rat-animation/scurry-preview.gif) (Blender studio).
- [Bite preview](../artifacts/rat-animation/bite-preview.gif),
  [scratch preview](../artifacts/rat-animation/scratch-preview.gif),
  [death preview](../artifacts/rat-animation/death-preview.gif).
- [Engine clip sheet](../artifacts/rat-animation/gallery-sheet-1.png),
  [collapse and turnaround sheet](../artifacts/rat-animation/gallery-sheet-2.png).
- [Normal encounter frames](../artifacts/rat-animation/normal-sheet-1.png),
  [normal collapse sequence](../artifacts/rat-animation/normal-sheet-2.png).
- [Machine-readable verification](../artifacts/rat-animation/verification.json),
  [persistent source manifest](../assets/monsters/rat/animation.json), and
  [indexed work card](creatures/01_rat.md).

```powershell
python -m tools.monster_models.rat_animation
python -m tools.monster_models.generate
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background --factory-startup --disable-autoexec --python-exit-code 1 --python tools\monster_models\blender_rat_animation.py -- --render
powershell -ExecutionPolicy Bypass -File scripts/build-source-bridge.ps1
python -m unittest tools.test_brogue_bridge tools.test_broguedoom_resources tools.monster_models.test_rat tools.monster_models.test_rat_animation tools.monster_models.test_creatures tools.weapon_models.test_viewmodel tools.mapcompiler.test_compile
python -m tools.monster_models.review_rat_animation
powershell -ExecutionPolicy Bypass -File scripts/review-rat-animation.ps1 -Phase gallery
powershell -ExecutionPolicy Bypass -File scripts/review-rat-animation.ps1 -Phase normal
python -m tools.monster_models.review_rat_animation --sheets
python -m tools.monster_models.verify_rat_review
```

The optional `-Phase before` uses the preserved local creature-rollout package;
normal review uses the preserved seed-one `artifacts/rat-model/floor1.pk3`.
Evidence is ignored, not required release content. Run the final verification
recorder only after inspecting the captures. Changed asset hashes invalidate
previous verification; identical deterministic rebuilds preserve it.

## Remaining approval scope

### Readable tile travel follow-up

The original five-tic tile interpolation compressed a complete scurry cycle
into about 0.14 seconds (112 source frames/second). Visible rats now cross a
cardinal tile in 28 tics (0.8 seconds), playing two scurry cycles at 40 source
frames/second. Diagonal steps take 40 tics, with cadence adjusted for their
longer distance. `brg_rat_walk_tics` controls the cardinal presentation duration
(5–70 tics); slower generic monster timing remains respected. Hidden rats and
long displacements retain generic pacing. This is a timing adjustment to the
existing model, not a new foot-locking solver or a change to Brogue's movement
speed. The existing one-action buffer waits for visual arrival; attack and death
pose counters still do not independently gate input.

The pre-change encounter captures/log and frontend source are preserved locally
under `artifacts/rat-walk-timing/`. The normal review now allows the slower
approach to finish before capturing combat, and records travel distance,
duration and clip rate for regression verification.

Follow-up verification: the source build and all **97 tests** passed. The same
36-action encounter still matches every headless Brogue hash and repeats
byte-identically. Runtime arrival diagnostics measure actual level-tic elapsed
time, not just the requested clip duration. Contact sheets are sampled visual
evidence, not real-time video; screenshot capture stalls can skip intermediate
poses. No geometry, skin or packaged asset bytes changed in this timing pass.

The rat animation implementation is ready for user art review. No claim is made
of final user approval, a controlled frame-time benchmark, all mutation/status
combinations, or animated side-by-side standalone captures. The normal encounter
and headless differential checks are separate from those gates. Current diffuse
shading is retained; this pass does not add PBR materials or dynamic fur.
The next creature is [BRG-M02 kobold](creatures/02_kobold.md).

## API/format sources

Context7's current Blender API references guided armature creation, deformation
weights and named Action handling; the installed Blender validated them.
[Blender armature edit bones](https://docs.blender.org/api/current/bpy.types.ArmatureEditBones.html),
[Action slots](https://docs.blender.org/api/current/bpy.types.ActionSlot.html).
The original writer follows the [IQM v2 format definition](https://github.com/lsalzman/iqm/blob/master/iqm.h).
Engine behavior was checked against pinned GZDoom 4.14.2:
[IQM loader/skinning](https://github.com/ZDoom/gzdoom/blob/99aa489d09015a95bb78df2b30ede29f328cc874/src/common/models/models_iqm.cpp),
[animation API](https://github.com/ZDoom/gzdoom/blob/99aa489d09015a95bb78df2b30ede29f328cc874/src/playsim/p_actionfunctions.cpp).

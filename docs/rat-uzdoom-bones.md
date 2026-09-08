# Rat enhancement using UZDoom 5.0 bone controls

Presentation-only work, researched 2026-09-06. The pinned engine is UZDoom
5.0.0 (`292cf4203ebd3ced951cb67f6819180f588c1d44`).

## What is new

The rat already used a 28-joint IQM skeleton, weighted skin and six clips before
the migration. Basic skeletal playback (`SetAnimation`, IQM and decoupled
animations) was available in GZDoom. This change uses the newer runtime bone
controls; it does not claim to introduce skeletal animation for the first time.

Context7 resolved GZDoom as the closest indexed library and described bone
rotation, animation layers and `AnimateBones`. Its example was treated as a
starting point, then checked against the actual pinned UZDoom source:

- [Actor animation and bone APIs](https://github.com/UZDoom/UZDoom/blob/292cf4203ebd3ced951cb67f6819180f588c1d44/wadsrc/static/zscript/actors/actor.zs):
  `AnimateBones`, `PrecalculatedAnimationFrame`, `OverwriteBonesMask` and
  `AnimationLayer`, annotated 4.15.1 in the source. `SetAnimation` is annotated 4.12.
- [Native implementation](https://github.com/UZDoom/UZDoom/blob/292cf4203ebd3ced951cb67f6819180f588c1d44/src/playsim/p_actionfunctions.cpp):
  the overwrite API accepts a cached local TRS array and mask without invoking
  `CalcBones` for each joint. `ClearBoneOffsets` indexes slot zero without a
  size check, so this controller deliberately avoids it for unrendered rats.
- [Bone composition](https://github.com/UZDoom/UZDoom/blob/292cf4203ebd3ced951cb67f6819180f588c1d44/src/common/models/bonecomponents.h):
  additive rotation composes a normalized quaternion with the authored pose.

The web wiki was access-blocked; the matching local checkout supplied the
version-specific implementation evidence. No external assets were imported.

## Result and authority

`brogue_rat_skeleton.zs` adds a cached, masked bone offset batch over the existing
clip: subtle head scanning/sniffing, independent ear flicks, a traveling tail
sway, and damped tail flex following changes in the already-projected facing.
Each rat's initial presentation position supplies a stable phase offset.
There is no target selection, AI, physics, RNG or movement command.

Only head, ears and tail receive offsets. Root, pelvis, spine, neck, jaw and all
leg joints remain in the authored clips. Basic uses identity offsets. Enhanced
enables detail; Cinematic increases its amplitude by 25%. Attacks, recoil and
death use the original clips with identity offsets. Hidden/sensed rats reset
the turning response; every offset is replaced on the next visible render.

The native `PlayRatClip` writes the existing presentation clip number into an
optional script field. Old resource packages without that field still work.
This does not change the bridge ABI or input gating. Brogue's existing
`attack`, `inflictDamage`, `killCreature` and copied cell changes still supply
all event and movement decisions. The original mesh, IQM, skin and Blender
rig/actions are unchanged; runtime procedural offsets are not baked into the
Blender file. ZScript now declares version 5.0 for the pinned runtime.

The new source follows the repository's AGPL-3.0-or-later license. Existing
original rat artwork remains CC-BY-SA-4.0, Project Broom contributors.

## Evidence

- Native Release compilation passed with `cmake --build .build/uzdoom --config
  Release -j 4 -- /nr:false`, using normalized Windows environment keys.
- `powershell -ExecutionPolicy Bypass -File scripts/test.ps1`: 139 tests passed.
  Its requested 300-action run ended naturally at turn 195, killed by a rat;
  this is not a completed endurance run. After the hidden-rat cleanup adjustment,
  the 39 focused rat-animation/resource tests passed again.
- Rig tests pin the mask to the correct 28-joint ordering and verify byte-identical
  IQM generation. Original IQM SHA256:
  `87512b1684f200d69a64e71697988a5f4f96b7c32852ebb8fd6f14c22b7779b7`.
- Vulkan/OpenGL bone probes verified nonzero detail offsets in Enhanced and
  Cinematic, identity offsets in Basic/combat/death, and unchanged actor positions.
  The fixture freezes selected base clips to isolate procedural bone effects.
- Real seed-1 encounter captures include scurry, bite, scratch, recoil and death.
  Both renderers returned the same 36 command records, including turns, positions
  and normalized hashes. Each captured 55 frames. The native render-only clip
  handoff is exercised here, not just the diagnostic actor.
- Static mod packaging reproduces byte for byte. The packaged rat is also
  launched by the fixed-scene benchmark, using isolated settings.

Reproduce the diagnostic with the already-built local engine:

```powershell
python -m tools.monster_models.review_rat_bones 1
python -m tools.monster_models.review_rat_bones 0
python -m unittest tools.monster_models.test_rat_animation tools.test_broguedoom_resources
```

Artifacts and logs are under `artifacts/rat-uzdoom/`. The directory also holds
the baseline source archive, encounter capture scripts and benchmark script.
The initial normal encounter exposed the unallocated-offset-slot issue above;
the corrected controller subsequently completed both encounter runs.

## Limits

The fixed one-rat scene at 3440x1440 on the RTX 3080 produced these engine
`bench` smoke samples (Basic / Enhanced / Cinematic): Vulkan 985 / 987 / 986 fps;
OpenGL 989 / 990 / 988 fps. Reported renderer `All` times were 0.347 / 0.369 /
0.359 ms and 0.310 / 0.292 / 0.333 ms respectively. These are single samples
near the engine frame-rate ceiling, not a statistical overhead or crowded-scene
benchmark. Raw reports are in `bench-vulkan/benchmarks.txt` and
`bench-opengl/benchmarks.txt`.

See the [captured encounter animation](../artifacts/rat-uzdoom/rat-encounter.gif)
and [probe overview](../artifacts/rat-uzdoom/preview.png).

This enhances the existing rig rather than replacing its mesh or authored clips.
It does not add runtime IK, ragdolls, root motion or gameplay-facing bone queries.
The runtime offsets are deliberately small to retain the paw grounding and
readability of the existing rat. No release installer or full player-facing
package was rebuilt, and no new standalone side-by-side session was run.

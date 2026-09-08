# Updating a skeletal enemy

The shared pipeline now drives the rat, kobold, jackal and monkey. Adding an enemy does not
require another native animation switch or a separate IQM exporter.

1. Start from the pinned creature card in `docs/creatures/`. Preserve its identity,
   source appearance and attack verbs; infer anatomy only for presentation.
2. Implement an anatomy module beside `kobold_animation.py`. Supply `BONES`,
   `REST`, `CLIPS`, `geometry()`, `animation_data()`, `deform()` and `build()`.
   Use `skeletal.Rig`, chain weights, shared mesh assembly and clip sampling.
   The shared solver currently assumes unit bone scale and animates rotation
   and translation; non-unit scale requires extending the solver and its tests.
   Bones must be parent-before-child, with at most four normalized influences.
3. Add a row to `assets/monsters/skeletal_profiles.json`. The six ordered roles
   are idle, walk, attack, alternate attack, hit and death. Names may differ by
   enemy. Idle/walk loop; action clips do not. Durations are cosmetic engine tics,
   long enough to finish the clip. Supply the source walk frame count.
4. Run `python -m tools.monster_models.skeletal_registry --build`, then
   `python -m tools.monster_models.generate` and
   `python -m tools.monster_models.bestiary`. The canonical source build includes
   the first two commands. The generated native header and MODELDEF/ZScript
   bindings must travel with the asset. Existing static reference assets remain.
5. Build editable source with background Blender:
   `blender --background --factory-startup --disable-autoexec --python-exit-code 1 --python tools/monster_models/blender_skeletal.py -- MK_KOBOLD`.
   Replace the symbol. The exporter checks sampled vertex deformation against
   the shared solver and reopens the saved file to check Actions and packed skin.
   It never operates on a live Blender document. Python remains the master.
6. Run `python -m unittest tools.monster_models.test_skeletal` and enemy-specific
   tests. Rebuild runtime assets twice and compare bytes. Runtime IQM generation
   is deterministic; Blender source bytes are not promised identical.
7. Run `python -m tools.monster_models.review_skeletal --symbol MK_KOBOLD --backend 1`
   and again with backend 0. Inspect the actual captures under
   `artifacts/skeletal-review/`. This isolated gallery tests rendering, not AI.
   Also exercise normal Brogue events in a fixed-seed dungeon, package the mod,
   launch it, measure the same scene/settings, and record any untested gates.

`PlayMonsterClip` selects clips and durations from the generated profile. Existing
snapshot/event handling owns movement, hits, death retention and visibility;
new enemies do not gain Doom AI, solidity or action timing. Some native storage
and enum names retain historical `rat` naming for compatibility. Camera-visible travel now uses shared tile pacing; skeletal enemies select their
registered walk clips. Off-camera movement settles immediately. Rat cadence keeps
its existing two cycles per tile, while the other rigs use one. Pose/death durations do not add an input gate. Optional per-rig
bone offsets can use a custom base class; never hardcode its bone mask for other
skeletons. The default proxy is sufficient for the kobold.

The generic Blender exporter uses current Action slots and explicit armature
parent transforms. References: [Blender bones](https://docs.blender.org/api/current/bpy.types.Bone.html),
[Action slots](https://docs.blender.org/api/current/bpy.types.ActionSlot.html),
[armature editing](https://docs.blender.org/api/current/info_gotchas_armatures_and_bones.html),
[IQM format](https://github.com/lsalzman/iqm/blob/master/iqm.h).
Runtime behavior is checked against this checkout's pinned UZDoom 5.0.0 source.

Current implementation reports: [rat](rat-animation-work.md) and [kobold](kobold-animation.md).

An enemy may specify `referenceSkin` in its profile when its active skin differs
from the static reference. Keep dedicated skins separate from static generators;
`kobold_materials.py` demonstrates padded semantic regions and UV validation.

The [jackal implementation](jackal-animation.md) demonstrates adding another
quadruped through the registry without new hand-written native enemy code.

## Connected anatomy and scale

The rat, kobold, jackal and monkey now use a connected skin cage. Separate overlapping
primitives are only the blockout; `assemble()` alone does not join their skin.
After editing their blockout or weights, run isolated Blender 5.2.1 with
`--threads 1 --python tools/monster_models/blender_skin.py -- kobold`
(substitute `rat` or `jackal`). This fuses the enclosed body volumes, relaxes
junctions, reduces the mesh, and transfers the existing UVs and bone weights.
Commit the resulting `connected-skin.json.gz` beside the editable `.blend`.
Normal builds require no Blender installation: they check the source fingerprint
and load this deterministic cage. A changed blockout fails with a stale-bake error.

Keep teeth, eyes, claws and held objects separate where their anatomy calls for
it. Do not fuse unrelated accessories or substitute body connectivity with joint
spheres alone. The Blender source reconstructs shared vertices and loop UVs;
runtime UV splits share identical positions and normalized weights. Run
`python -m unittest tools.monster_models.test_connected_skin` to check closed
manifold connectivity, all four limb chains, and animated seam equality.

`visualScale` in the skeletal profile controls MODELDEF and the editable Blender
rig together, without changing the proxy's gameplay properties. The kobold uses
1.28 (about 47 units to the head versus the 58-unit humanoid art reference).
These are art choices, not dimensions supplied by Brogue. Water hides the portion
below its separate surface; don't shorten legs to compensate for submersion.

Use `review_skeletal --all-angles --before-iqm <previous.iqm> --output <directory>`
for actual front, side, rear and oblique comparisons. See
[anatomy repair and verification](enemy-anatomy-repair.md).


Captivity is an optional profile extension: `captivity` names a separate actor
class/model, looping bound clip, non-looping release clip and duration. Supply
normal and captive models with identical body geometry and rig; put bindings
only in the captive variant. `blender_skeletal.py -- MK_MONKEY --captive` writes
the second editable source. `review_skeletal --symbol MK_MONKEY --backend 1
--captivity` captures bound, releasing and settled poses.

The native selector reads copied `MB_CAPTIVE`, while release additionally requires
an observed captive-to-ally change, a live result and direct visibility before
and after. Rebinding, repeated snapshots and unseen releases settle. The actor
class must match the displayed identity so hallucination cannot reveal captivity.
Cages remain terrain-owned. `brg_actions` and `brg_confirm yes|no` exercise existing
intent and confirmation paths for development captures; they do not bypass
Brogue validation. `brg_monsters` reports bound state, class, clip and remaining
tics. The [monkey report](monkey-animation.md) records concrete evidence.

See [visible enemy movement](enemy-movement.md) for camera gating and the
top-of-screen movement progress indicator.

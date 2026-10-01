# Naga model and animation

Presentation-only BRG-M28 / MK_NAGA. Brogue CE remains authoritative.

## Source and planned proof

The source describes serpentine naga beneath subterranean waters emerging to attack; claws, bites and tail-whips are existing action strings. Female, large, water immunity, submergence and all-adjacent attacks are source facts, not frontend rules. No gameplay, AI, collision, health, visibility, RNG, spawning or ABI changes are planned.

Art interpretation: an olive-green scaled serpent with a heavy ground coil, tapered curling tail, narrow upright torso, connected claw-bearing arms, ridged reptilian head, amber eyes, articulated jaw and pale ventral scutes. Size, proportions, pigmentation and anatomy are original art decisions. Six cosmetic clips are idle, slither, claw, tailwhip, recoil and collapse; only idle/slither loop. Attack variants do not identify Brogue attack verbs or select targets.

Proof planned before editing: closed connected organic cage, normalized four-influence/unit-scale rig, centered +/-32 bounds for every frame, recovery and collapsed death; repeated cold exports; fresh Blender source and 18 poses; native compile/fingerprint; early engine front/action/death review followed by both packaged 34-view galleries and opaque-water synthetic fixtures. Natural encounter/lifecycle, physical play, standalone comparison and user art approval remain open. The completed 2000-seed ordinary-route census found no naga and will not be repeated unchanged.

All new artwork is original Project Broom content under CC-BY-SA-4.0.

## Delivered art and scope

The model has a closed fused skin, an open coil center, tapered curled tip,
rounded shoulder transitions, four articulated claws per hand, separate jaw,
fangs, nostrils and dark sockets around amber slit eyes. The 24-bone rig supports
six roles. Original 1024-square diffuse uses orientation-aware ventral mapping
and longitudinal tail coordinates. The head/back remain olive while the throat
and belly carry broad pale transverse scutes. The numeric proportions are art.

Source is `tools/monster_models/naga_animation.py`; cage, manifest and fresh
editable source are in `assets/monsters/naga/`. Runtime files are
`mod/BrogueDoom/models/monsters/28_naga.iqm` and `graphics/BRGNAGA.png`.
Creature regression and synthetic water tools are `test_naga.py` and
`review_naga.py` in `tools/monster_models/`.

Early engine review corrected angular shoulder junctions, pale dorsal coloring,
compressed tail scales, and the collapse hands crossing the outer coil. The
final hands fold into the open center. Residual close-up texture stretching and
banding remain at some curved transitions; this is not hidden by the technical
verification. User art approval remains open.

## Natural encounter and remaining acceptance

No natural naga encounter was obtained. The completed shared census searched
seeds 1-2000 using up to 1500 ordinary intents/depth15 and found no kind28.
That unchanged search was not repeated. The ordinary hostile horde range is
13-20, beyond the depth reached by the conservative surviving route. No health,
spawn, reveal, visibility or Brogue action overrides were introduced.

The water fixture places a gallery proxy on the ordinary -24-unit water bed
beneath an opaque non-solid surface. It explicitly sets hidden/sensed display
states and samples a resolved-action animation. It does not call native Brogue
visibility transitions and does not prove natural emergence, submergence,
all-adjacent combat, hits or death. Natural lifecycle, physical input/play,
standalone comparison, controlled frame-time benchmarking, full release
installer packaging and individual user art approval remain open.

## Tests

**57 tests passed in 247.154 seconds** (`grounded-tests.log`):

```powershell
python -m unittest tools.monster_models.test_naga tools.monster_models.test_skeletal tools.monster_models.test_connected_skin tools.monster_models.test_creatures tools.test_broguedoom_resources
```

The eight naga tests cover closed connected anatomy/open coil and separate hands,
normalized weights/seams/required rig chains, every raw/exported frame's floor
and centered bounds, loop/recovery and action displacement, collapsed head/hands,
ventral versus dorsal/arc mapping, and exact exported binary/texture bytes.
Intermediate suites failed against stale assets while art changed; only the
completed frozen-byte run above is final proof. The initial Blender attempt
also exposed a missing shared `sub` helper import, fixed before the passing
fresh reconstruction. No remaining test failure is claimed waived.

## Final technical evidence

Final corrected evidence uses only `artifacts/creature-queue/BRG-M28/grounded-*`.
Earlier early/refined/freeze/final/accepted files are intermediate art evidence,
not final-byte verification. The native compile log and fingerprint apply to the
unchanged generated clip contract throughout these asset-only refinements.

- **Geometry:** 5,720 runtime UV-split vertices, 11,008 triangles, 24 bones and
  six clips. The organic cage has 2,802 topological vertices/5,600 triangles.
  Rest dimensions are 43.5641 x 44.2237 x 57.3528 units. Across every frame,
  X is -19.55751 to +24.98706, Y is -23.63972 to +26.74785, and minimum
  Z is 0.22711. Only idle/slither loop; attacks/recoil recover to rest.
- **Grounded collapse:** the shared sampler initially raised the whole corpse
  4.37 units to clear the hands. Final authoring adjusts only the collapsing
  waist from explicit hand/jaw contact vertices. Every raw frame stays above
  the floor, exported root transforms equal raw root transforms exactly, and
  the ground coil never inherits that automatic lift. The regression checks
  this for every sampled frame, not merely the final screenshot. Final head
  height is below one-third of rest height and hands remain within the open
  center; no exhaustive mathematical self-intersection claim is made.
- **Determinism:** cold single-thread connected-skin bakes and repeated final
  IQM, PNG and manifest exports are byte-identical (`grounded-determinism.json`).
  Blend-file byte determinism is not claimed.
- **Blender:** isolated Blender 5.2.1 reconstructed and freshly reopened the
  packed source, six Actions, no linked libraries and 18 sampled poses.
  Maximum vertex error is **0.0000180551** units. See
  `grounded-blender.log` and `grounded-blender-verification.json`. The known
  extension-cache warning is nonfatal; no live Blender document was replaced.
- **Native compilation:** `python tools/run_native.py cmake --build
  .build/uzdoom --config Release -j4` passed. Build fingerprint was recorded
  afterward and `validate_build` confirms all current native inputs/outputs.
  The generated K28 profile row is the sole native change; no frontend
  visibility, wall placement, transition repair, bridge or gameplay code changed.
- **Renderer/package:** `grounded-vulkan/` and `grounded-opengl/` each contain
  34 actual 1920x1080 captures: static before, all six clips, front/side/rear,
  and 64/128/192-unit distances. Complete contact sheets and representative
  full-size images were inspected. Both exit zero, all 34 subjects report
  `blocking=0`, and no new model/resource errors occurred. Existing engine
  menu/minimap warnings remain. Both deterministic PK3s are identical and
  critical IQM/skin/MODELDEF/ZScript/GLDEFS bytes match source; see
  `grounded-package-verification.json`.
- **Synthetic water:** each `grounded-water-*` folder has six actual 1920x1080
  images at three distances, hidden, sensed and tailwhip. Both contact sheets
  and representative views were inspected: the opaque water correctly occludes
  the lower coil, hidden shows no actor, and sensed uses translucency. Every
  proxy reports nonblocking. Scope remains the renderer fixture described above.

```text
IQM 91da906faaf90a8452035d23c18a9d94e7bce1636bbfc2af30c2b6c12d0c5ffa
PNG 30557fe2a73e3f0a981d29066678b4c1ac7442d65d2f9f59d198caff9cd70e18
PK3 2f314a93b0fb1ab7c699473bba7727993113c4957c64af5505d8d67fffa41c6e
```

Reproduce the final galleries with:

```powershell
python -m tools.monster_models.naga_animation
python -m tools.monster_models.review_skeletal --symbol MK_NAGA --backend 1 --all-angles --distances --packaged --width 1920 --height 1080 --output artifacts/creature-queue/BRG-M28/reproduction-vulkan
python -m tools.monster_models.review_naga --backend 1 --package artifacts/creature-queue/BRG-M28/reproduction-vulkan/ProjectBroom-review.pk3 --output artifacts/creature-queue/BRG-M28/reproduction-water-vulkan
```

Use backend0 and a fresh output path for OpenGL.

## Preservation

The immediate 672-file baseline has 663 byte-identical files, nine intended
shared changes and zero missing files (`preservation.json`). All 28 prior
skeletal profiles, 67 other bestiary entries and all other raw creature-card
bytes are preserved, including pre-existing mixed line endings. Static naga
OBJ/skin/Blend references remain unchanged. Queue and model index are owned
by the coordinator and were not changed by this agent.

Shared changes: connected-skin naga selector; naga bestiary traits; skeletal
profile, registry and bestiary entry; K28 card; generated MODELDEF, inert actor
binding and native clip table. New assets/generator/test/fixture/report are
confined to naga. No commit, publish, broad clean, or next model was started.

The coordinator independently verified all 1,167 entries in each final package
against current mod source (`parent-all-package-entries.json`), plus critical
resource comparisons in
`parent-grounded-package-verification.json` and inspected the corrected final
OpenGL death plus both water examples. This is technical art review, not user
art approval.

[Final Vulkan gallery](../artifacts/creature-queue/BRG-M28/grounded-vulkan-contact.jpg),
[OpenGL gallery](../artifacts/creature-queue/BRG-M28/grounded-opengl-contact.jpg),
[synthetic water](../artifacts/creature-queue/BRG-M28/grounded-water-opengl-contact.jpg).

Coordinator closeout also updated only the generated model-index kind28 row to the final skeletal metadata, preserving every other byte. This documentation-only change is separate from the agent baseline above.

## Review package restoration

The coordinator losslessly archived review packages after technical acceptance. Restore the final grounded Vulkan package byte-for-byte with:

```powershell
python -m tools.monster_models.review_archive restore artifacts/creature-queue/BRG-M28/grounded-vulkan/ProjectBroom-review.pk3.archive.json
```

Use the corresponding `grounded-opengl` manifest for OpenGL. Only grounded final packages establish acceptance; earlier art and lifted-coil revisions are superseded. Screenshots and verification manifests remain directly available.

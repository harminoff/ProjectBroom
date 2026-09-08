# Connected enemy anatomy

Presentation-only repair for the rat, kobold and jackal. Brogue CE remains
authoritative; no native bridge, creature catalog, collision, AI, turn processing
or gameplay RNG code changes are part of this repair.

## Problem and resulting presentation

The kobold's arms began at capped tubes outside the ribcage. The torso, pelvis,
neck and limb surfaces were separate meshes with independent weights. Numeric
skinning tests did not catch the visible gaps. The shared pipeline now fuses the
body blockout into a closed skin cage, including shoulders, hips, ankles and tail
roots. Kobold deltoids supply anatomical volume at the shoulder junctions. The
rat and jackal receive the same connected-body treatment; eyes, jaws, teeth,
claws and the kobold's club remain separately owned details.

Weights are transferred from the original rig, relaxed locally over shared mesh
edges and normalized to at most four influences. UV seams duplicate only runtime
vertices; both copies have exactly the same position and weights. Editable
Blender files retain shared body vertices with UVs on face corners. Linear
skinning is used in Blender to match the pinned UZDoom IQM renderer; enabling
Blender's quaternion Preserve Volume option alone would produce a misleading
preview of this runtime.

The kobold now uses a uniform visual scale of 1.28: approximately 47 units to the
head, compared with the project's 58-unit humanoid art reference. The old head
height was about 37. Brogue describes a lizardlike humanoid but gives no exact
height; this is a deliberate art proportion. Rat and jackal proportions remain
about 15 units and 34 units high, respectively, with minor surface changes from
fusion. The jackal's height includes its ears. No inference is made from HP.

The user's screenshot also showed submersion: `TerrainSupport()` projects
creatures to the bed, while water renders on a separate surface. Shallow and
deep beds are at -8 and -24. Hidden lower legs in that view were not missing mesh.
This repair does not alter those settled support heights.

## Blender research and implementation

- [Skinning](https://docs.blender.org/manual/en/latest/animation/armatures/skinning/introduction.html):
  an armature modifier deforms a mesh; bone parenting alone moves separate parts.
- [Remeshing and retopology](https://docs.blender.org/manual/en/latest/modeling/meshes/retopology.html):
  voxel fusion removes overlapping enclosed geometry, but raw voxel topology is
  not a finished animation mesh. Here it is relaxed and reduced to a bounded cage,
  then checked against the actual shipped poses. This is a triangulated game cage,
  not a hand-retopologized subdivision character or a general-purpose motion rig.
- [Voxel remesh](https://docs.blender.org/manual/en/latest/sculpt_paint/sculpting/tool_settings/remesh.html):
  remeshing discards original mesh data layers, so UVs and normalized weights are
  explicitly reprojected. Thin claws, teeth and eyes are excluded from fusion.
- [Armature modifier](https://docs.blender.org/manual/en/latest/modeling/modifiers/deform/armature.html):
  Blender's Preserve Volume uses quaternion deformation; the preview must agree
  with the engine's skinning method rather than hide its limitations.

`blender_skin.py` uses Blender 5.2.1 LTS, canonical vertex/face ordering and
deterministic reduction. QuadriFlow was evaluated but rejected because its cold
bakes differed despite a fixed seed. Ordinary builds consume the committed cage
and fail if the source blockout or weights have changed. No Blender process runs
inside the game or ordinary asset build. All new mesh data is original Project
Broom work, CC-BY-SA-4.0 under `ASSETS-LICENSE.md`; no external artwork was used.

## Evidence

Local evidence is under `artifacts/anatomy-repair/`; the starting dirty files are
preserved in `baseline.zip`. `bake-determinism.json` records byte-identical cold
bakes for all three bodies. `source-*.log` records saved and freshly reopened
Blender files plus sampled deformation agreement with the IQM solver.

`test_connected_skin` checks one closed manifold body component, participation
of all four limb chains, UV seam equality through every clip and the kobold scale
binding. Existing tests retain clip, grounding, bone ownership and deterministic
IQM checks. Final build, suite and renderer results are recorded below.

Final verification (2026-09-06):

| Gate | Result |
| --- | --- |
| `scripts/build-source-bridge.ps1 -SkipTests` | Passed; UZDoom and self-contained launcher built. NuGet restore required network access. |
| `scripts/test.ps1` | All 151 tests passed after the final UV correction. The 300-action long-run attempt ended naturally at turn 195, killed by a rat; it is not a completed survival run. |
| Cold Blender bakes | Two fresh bakes per enemy were byte-identical; hashes in `bake-determinism.json`. |
| Editable sources | All three saved and reopened successfully; 18 sampled Blender/IQM deformation comparisons per rig passed, including MODELDEF visual scale. |
| Runtime geometry | Rat 14,060 triangles (previously 15,916); kobold 11,340 (12,636); jackal 9,360 (9,368). |
| Vulkan and OpenGL | 31 captures per enemy per backend: 186 total. Six clips sampled obliquely, plus front/side/rear attachment views and previous-IQM comparisons. All proxies reported non-solid. |
| Resource package | Two complete PK3 builds were byte-identical; `package.json` records the hash. |
| Packaged encounters | Seed 1, kobold and jackal routes on both backends: 48 commands each, 55 captures each. Logs retain normal event-driven clips and match the previous headless route results. |

The kobold route ends at turn 42, hash `69afa7433350e1b6` (six final commands are
blocked); the jackal route ends at turn 48, hash `6bfdb2d8cf5d78be`. These are
recovery/parity checks against the existing headless baselines, not a newly run
standalone side-by-side comparison. Gallery captures provide the anatomy views;
the normal encounter camera can be occluded by dungeon walls.

Before/after examples: `kobold-front-comparison.png`, `rat-side-comparison.png`,
and `jackal-views.png` in the evidence directory. The rat review caught and fixed
an atlas-wrap stripe before final verification. The original dirty baseline and
static reference meshes were preserved.

Limitations: numerical sizes remain art choices; this is a reduced triangulated
cage validated for the shipped clips, not hand-designed subdivision edge flow.
No new frame-timing benchmark or standalone UI comparison was performed. Triangle
counts are within the previous budgets, but that is not a frame-rate claim.
The rebuilt launcher was not separately exercised through its menus; actual
UZDoom launches used the packaged PK3. Final aesthetic approval remains with the
user.

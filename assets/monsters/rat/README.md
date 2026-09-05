# Rat — MK_RAT / BrogueMonsterK01

## Current animated version

The runtime rat is now `models/monsters/01_rat.iqm`, with 28 weighted bones,
80 editable anatomical parts, 15,916 triangles and six named clips: idle,
scurry, bite, scratch, recoil and death. Its original coat/skin and approximate
51 x 18 x 15 map-unit rest size are preserved. The jaw has a separate mandible,
recessed mouth and lower incisors; planted paws use a two-joint leg solve.

- [rat-animated.blend](rat-animated.blend): current editable rig, weights and six
  named Actions; packed diffuse atlas and separate preview collection.
- [animation.json](animation.json): clip rates/counts, hierarchy, bounds, hashes
  and verification against the current model.
- `python -m tools.monster_models.rat_animation`: deterministic IQM rebuild.
- `tools/monster_models/blender_rat_animation.py`: isolated background Blender
  source rebuild and sampled deformation comparison (`-- --render` for images).
- [Implementation and verification report](../../../docs/rat-animation-work.md).

The original `rat.blend`, OBJ and `rat.py` are retained as the static reference,
not the current runtime binding. The sections below document that reference.
The Python anatomical/rig/clip definitions remain the reproducible master;
reconcile manual Blender changes before rebuilding. Do not assume saving a
Blender Action automatically exports it to IQM.

Original Project Broom art, authored by the Project Broom contributors with
Codex-assisted procedural modeling and Blender. Mesh and texture license:
**CC-BY-SA-4.0**, as specified in [ASSETS-LICENSE.md](../../../ASSETS-LICENSE.md).
No external meshes, photographs, downloaded textures, or reference-game assets
were used. Blender is an authoring tool, not an asset source.

## Brogue reference and visual interpretation

Pinned `src/brogue-mapgen/src/brogue/Globals.c` describes the rat as a scavenger
of the shallows searching for decaying animal matter. The catalog specifies gray
and not large. The model interprets this as a crouched coarse-coated gray rat,
with a continuous tapered torso/head, muscular hindquarters, bent forelegs,
four fore toes and five hind toes per paw, claws, small incisors, cupped ears,
dark eyes, whiskers, and a long tapered ringed tail. Anatomical details are
artistic choices, not additional Brogue mechanics.

## Files and rebuilding

- `rat.blend`: editable named anatomical meshes, packed diffuse atlas, separate
  preview floor/lights/camera, and source metadata. Preview objects are not part
  of the exported rat.
- `../../../tools/monster_models/rat.py`: deterministic geometry/UV/normal and
  original texture-stroke source. Uses only Python's standard library.
- `../../../tools/monster_models/blender_rat.py`: constructs the editable source
  scene in Blender without replacing unrelated scenes.
- `../../../mod/BrogueDoom/models/monsters/01_rat.obj`: runtime geometry.
- `../../../mod/BrogueDoom/graphics/BRGRAT.png`: opaque 1024×1024 RGB diffuse atlas.

From the repository root:

```powershell
python -m tools.monster_models.rat
python -m tools.monster_models.generate
python -m unittest tools.monster_models.test_rat tools.test_broguedoom_resources
```

To rebuild the source file, run `tools/monster_models/blender_rat.py` through
Blender's Python environment (or the connected Blender MCP). Its `__file__` must
be set; `runpy.run_path(absolute_script_path)` is supported. It creates a new
scene and writes only that scene and dependencies to `rat.blend`. The runtime
generator is independent of Blender and does not export preview-stage objects.

Blender coordinates use X forward, Z up, feet at zero. The runtime exporter
converts these to OBJ `(X, Z, -Y)` and supplies triangle faces, UVs, and smooth
normals. The kind-1 binding and scale stay in the roster generator. This is a
static pose with the existing bridge-driven movement/attack/death transforms;
skeletal gait, ear motion, and tail animation are absent from that static
reference, but are implemented in the separate current animated version above.

Runtime budget: 14,868 triangles; 8,429 exported vertices including UV seams;
76 editable anatomical parts; one skin/material. Blender-space bounds are
approximately X -31.28 to 19.84, Y -8.29 to 10.15, Z 0.07 to 15.07. The full
51.12-unit nose-to-tail silhouette fits inside a 64-unit Brogue cell.

Source generation first stages an isolated scene, then uses the installed
Blender executable to save a regular file with its active scene configured.
The previous `rat.blend` is replaced only after that save succeeds.

The procedural Python source is currently the reproducible master. Hand edits
in Blender can be exported using the guide's selected-object OBJ workflow, but
rerunning `rat.py` rebuilds from its anatomical definitions. Reconcile such edits
with that source (or explicitly migrate this asset to a `.blend`-master pipeline)
before rebuilding. The general roster generator always preserves the custom OBJ.

See [the model authoring guide](../../../docs/gzdoom-model-authoring.md) for
format choices, verified GZDoom behavior, packaging, and acceptance checks.

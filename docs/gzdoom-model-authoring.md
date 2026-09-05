# Project Broom: authoring models for GZDoom

Research date: 2026-09-04. Target: the repository's pinned GZDoom **4.14.2**
(`99aa489d09015a95bb78df2b30ede29f328cc874`), Brogue CE 1.11, and the locally
verified Blender **5.2.1 LTS**. Recheck exporter options after upgrading Blender.

For per-creature Brogue facts, scale decisions and editable source links, use
the [indexed creature work cards](creature-model-index.md) and
[rollout verification](creature-model-rollout.md).

## Authority and scope

Models are presentation assets. Brogue CE still chooses creature identity,
position, visibility, facing destination, attacks, damage, death, and turns.
Keep `BrogueMonsterProxyBase` and the bridge's stable IDs. A model replacement
must not add Doom AI, collision, pickups, damage, gameplay RNG, or new monsters.
An animation may illustrate a resolved Brogue event; it cannot cause that event.

## Choose the runtime format

| Format | What it carries | Use in this project |
| --- | --- | --- |
| OBJ | Static geometry, UVs, normals; one model frame | Current choice for creatures and props; simplest reproducible Blender pipeline |
| MD3 | Mesh surfaces and vertex animation frames | Consider for short, baked deformation sequences; verify exporter compatibility and per-surface limits |
| IQM | Meshes, skeleton, weights, animation | Verified for the 28-bone rat; use its deterministic writer, tests and event-to-clip adapter as the current reference |
| MD2 / DMD | Older vertex-animated formats | Supported legacy paths; no reason to introduce them for the new rat |

The pinned engine's format dispatch is in `src/common/models/model.cpp` [1].
Do not assume FBX, glTF, or `.blend` is a directly loadable GZDoom runtime model.
Keep `.blend` as the editable authoring source. OBJ has no walk cycle: exporting
an OBJ per Blender animation frame does not create an animated model binding.
The existing bridge already animates whole-proxy transforms for moves, attacks,
hits, and deaths; a static replacement retains those effects.

For IQM background, the format author's development kit includes
exporter code and documents skeleton/mesh/animation export [5]. Its scripts are
version-specific; their existence does not establish compatibility with the
installed Blender. The current rat uses an original project writer verified
against the pinned reader, not an untested third-party Blender add-on. See
[the rat animation report](rat-animation-work.md). Its IQM coordinates remain
X-forward/Y-lateral/Z-up, UV V is flipped once, and triangle winding is reversed
relative to the source meshes. Unlike OBJ, GZDoom's IQM loader does not reverse
triangle indices. Do not copy the OBJ axis/winding conversion into IQM.

## Model from the Brogue source first

1. Find the catalog symbol in `assets/monsters/brogue_monster_catalog.json`.
2. Read its `monsterCatalog` and `monsterText` entries in
   `src/brogue-mapgen/src/brogue/Globals.c`.
3. Separate actual Brogue facts from artistic interpretation. Preserve identity,
   relative size, useful color cues, and the absence/presence of special powers.
4. Check the class/model mapping in `brogue_monster_registry.json` and the native
   `MonsterClassName`/`SyncMonsters` path before changing any resource binding.

For `MK_RAT` (kind 1), Brogue calls it a gray, non-large rat. The exact description
is: “The rat is a scavenger of the shallows, perpetually in search of decaying
animal matter.” Its prose uses scratching and biting. The coarse gray coat,
low searching posture, bare ears/paws/tail, whiskers, and incisors are visual
interpretations of an ordinary scavenging rat, not additional abilities [6].
Replacing kind 1 updates existing rats wherever Brogue generates them, including
floor one; it does not change their spawn depths or population.

## Blender authoring contract

- Work in a separate named scene/collection. Keep unrelated scenes intact.
- Model facing **Blender +X**, with **+Z up** and feet on **Z = 0**.
- Use **one Blender unit per intended Doom map unit** for this pipeline. A Brogue
  cell is 64 map units across. Judge a rat against that cell and the player view,
  not just an isolated close-up.
- Put the origin at the ground projection of the creature's center. Keep the
  rotation pivot useful for the bridge's facing and attack transforms.
- Prefer a connected organic torso silhouette; spend geometry on muzzle, ears,
  joints, paws, and tail curvature. Fur color alone cannot rescue a box silhouette.
- Apply or bake object transforms and export modifiers deliberately. Check
  negative scales, outward face winding, and smooth normals.
- Use UVs for every exported face. Put atlas seams on the underside or back of
  ears, and give islands padding against texture filtering/mip bleeding.
- Use an opaque skin initially. Thick enough whisker geometry and silhouette
  tufts avoid alpha sorting problems; do not export particle hair as if it were
  regular mesh geometry.
- Keep named anatomical parts editable in the `.blend`; they may share one
  atlas/material and be exported together to one OBJ.

Suggested starting budgets (project targets, **not engine limits**): 5–15k
triangles for a small detailed creature, one 1024×1024 diffuse skin, and one
runtime material. Validate several visible creatures at gameplay distance before
raising these budgets. Keep finer strands in the texture and reserve geometry
for features that survive at that distance.

## Texture and material handling

Blender's Principled BSDF and procedural nodes are not GZDoom materials. Produce
an actual UV-mapped PNG containing the intended base color. Bake procedural
color/high-poly details when used, and inspect the resulting image without its
Blender lighting. Keep lighting direction out of the diffuse except for restrained
artistic cavity shading.

For the single-skin path, set `export_materials=False` and bind the PNG explicitly
with MODELDEF `Skin`. The pinned OBJ loader recognizes `usemtl` as a texture
lookup; it does not parse an MTL material graph. A Blender material name such as
`Material.001` can therefore produce a missing-material warning even if an MTL
file sits beside the OBJ. Multiple OBJ materials require intentional texture
paths and surface checks; do not assume Blender's MTL is sufficient [2].

Normal/specular/PBR maps need their own supported GZDoom material setup and
renderer testing. A viewport bump node alone is not a shipped normal map.
The first detailed rat uses a diffuse atlas and mesh normals; its source material
is arranged to preview the same color image that the game loads.

## Export OBJ with explicit axes

Blender's native OBJ exporter is available as `bpy.ops.wm.obj_export` in the
verified installation [4]. Run from Object Mode with only the asset selected:

```python
bpy.ops.wm.obj_export(
    filepath=output_path,
    export_selected_objects=True,
    forward_axis='NEGATIVE_Z',
    up_axis='Y',
    global_scale=1.0,
    apply_modifiers=True,
    export_uv=True,
    export_normals=True,
    export_materials=False,
    export_triangulated_mesh=True,
)
```

With the +X-facing authoring convention, this converts Blender `(X, Y, Z)` to
OBJ `(X, Z, -Y)`: OBJ **Y is height**. GZDoom's OBJ `RealignVector` negates the
third component, and its renderer uses an internal Y-up model transform [2,3].
Thus the existing +X-forward actors do not need an extra quarter-turn. OBJ's
normal/UV indices are separate from position indices; don't merge vertices by
position and discard UV seams. Export conventional UVs: the loader handles its
own V conversion.

Triangulate before shipping. This loader reads three or four sides per face;
general Blender n-gons are not a safe interchange contract [2]. Export normals
and inspect all sides with backface culling enabled. Fix winding rather than
using `DontCullBackfaces` to conceal inverted meshes.

The installed exporter accepts the options above, verified from its live RNA.
Python tooling can also read `Mesh.from_pydata` and per-loop UVs directly [4].
When a deterministic project exporter is used, it must implement this same axes,
triangulation, UV, normal, and winding contract and be checked in-engine.

## Runtime binding and packaging

The existing kind-1 actor is `BrogueMonsterK01`. Its inherited spawn state is
`BRM0 A -1`, with the existing fallback sprite. A static binding is:

```text
Model BrogueMonsterK01
{
    Path "models/monsters"
    Model 0 "01_rat.obj"
    Skin 0 "graphics/BRGRAT.png"
    Scale 1.0 1.0 1.0
    FrameIndex BRM0 A 0 0
}
```

`FrameIndex` means sprite name, sprite frame, model slot, model frame. Slot and
frame are both zero for this static OBJ. The class and actual sprite/frame must
match. `Path` prefixes the model path; `LoadSkin` first tries that prefix and can
fall back to the full resource path used above [3]. Use exact case and forward
slashes throughout the package.

The root `mod/BrogueDoom/MODELDEF` includes `models/monsters/MODELDEF.txt`.
The root ZSCRIPT includes `brogue_monsters.zs`. Preserve the existing actor flags
`NOBLOCKMAP`, `NOGRAVITY`, `NOINTERACTION`, and `NOTONAUTOMAP`.

The generator owns the roster and bindings. Register a custom asset explicitly
and skip its placeholder geometry in `tools/monster_models/generate.py`; editing
only the generated MODELDEF or OBJ makes the upgrade disappear on regeneration.
Missing registered custom output should fail with a useful rebuild instruction.

In a PK3, paths start at the archive root:

```text
MODELDEF
ZSCRIPT
brogue_monsters.zs
models/monsters/MODELDEF.txt
models/monsters/01_rat.obj
graphics/BRGRAT.png
```

Development loads the `mod/BrogueDoom` directory together with a generated map
PK3. Release packaging includes that static resource tree. Do not nest the mod
under an extra `BrogueDoom/` folder inside the archive, or accidentally load a
later package containing an older copy of the rat. Keep `.blend`, authoring
scripts, preview stages, and diagnostic cameras out of runtime resource packages.

`Scale`, `Offset`, and `AngleOffset` are presentation transforms. Do not change
actor collision dimensions to resize art. `CorrectPixelStretch` controls when
aspect compensation is applied, especially for rotated models; it is not a
blanket instruction to multiply every model's height by 1.2 [3]. The rat follows
the existing monster scale and map pixel settings.

## Verification and handoff

1. Record the previous model/skin and take a before capture.
2. Export twice with identical inputs and compare OBJ/PNG SHA-256 hashes.
   `.blend` save bytes can contain nondeterministic application metadata; compare
   runtime outputs rather than claiming all Blender saves are byte-identical.
3. Check finite vertices, positive valid indices, triangle winding/area, normals,
   UV bounds, floor origin, silhouette bounds, and resource references.
4. Run `python -m unittest tools.test_broguedoom_resources` and the new asset's
   focused tests; verify roster regeneration retains custom models and skins.
5. Package the static assets and check the archive members and hashes.
6. Launch the pinned GZDoom frontend with seed 1. Check the log for missing model,
   material, texture, frame, or script errors. Check orientation, feet, scale,
   lighting, and silhouette from multiple angles, including gameplay distance.
7. Take an after capture with the same camera/settings. Any developer visibility
   override or inspection camera must be identified as such and kept out of the
   production asset. Inspect a normal floor-one view as a separate check.
8. Report compilation, tests, deterministic export, packaging, launch, captures,
   and gameplay-parity checks separately. A static art replacement requires no
   gameplay change. Preserve source/licensing notes and name any untested gate.

## Sources and evidence quality

### Blender MCP connection notes

Live scene inspection, code execution, and rendering worked through the installed
MCP. Its optional `*_for_cli` tools returned “Blender executable not found at
'blender'” because their server environment lacked `BLENDER_PATH`. That is
separate from the working live connection. For background source verification,
invoke the actual installed Blender executable explicitly; add
`--python-exit-code 1` so a Python failure cannot look like a successful process.
Use the file path returned by an MCP render: the installed server staged its
image in a temporary directory even when an output path was supplied.

The rat builder uses the connected Blender's own `bpy.app.binary_path` for its
isolated save step, so it does not depend on the MCP server's CLI path setting.

### Research references

Context7 was queried for GZDoom and Blender. Its Blender results supplied the
mesh/UV/export API reference; its GZDoom results did not cover MODELDEF. The
ZDoom wiki's model pages returned an access-denied page during this research.
Engine-specific statements above were therefore checked directly in the local
pinned source checkout, with permanent upstream links below. The wiki remains
a useful starting point when accessible, not the evidence for these details.

1. [GZDoom 4.14.2 format dispatch and skin lookup](https://github.com/ZDoom/gzdoom/blob/99aa489d09015a95bb78df2b30ede29f328cc874/src/common/models/model.cpp).
2. [GZDoom 4.14.2 OBJ parser, normals, axes and UV handling](https://github.com/ZDoom/gzdoom/blob/99aa489d09015a95bb78df2b30ede29f328cc874/src/common/models/models_obj.cpp).
3. [GZDoom 4.14.2 MODELDEF parser and model transforms](https://github.com/ZDoom/gzdoom/blob/99aa489d09015a95bb78df2b30ede29f328cc874/src/r_data/models.cpp).
4. [Blender Mesh API](https://docs.blender.org/api/current/bpy.types.Mesh.html),
   [OBJ exporter API](https://docs.blender.org/api/current/bpy.ops.wm.html#bpy.ops.wm.obj_export),
   and [Blender OBJ manual](https://docs.blender.org/manual/en/latest/files/import_export/obj.html).
   API behavior was also inspected in the connected Blender 5.2.1 instance.
5. [IQM development kit and exporter notes, by the format author](https://github.com/lsalzman/iqm).
6. [Pinned Brogue CE catalog and monster prose](https://github.com/tmewett/BrogueCE/blob/7f52dd93b7fa553dd6e354ccd44229a3c22d8a76/src/brogue/Globals.c);
   local authority: `src/brogue-mapgen/src/brogue/Globals.c`, rat catalog at line
   1030 and monster prose at line 1171 when researched.

Original Project Broom model/texture assets use the repository's
[CC-BY-SA-4.0 asset license](../ASSETS-LICENSE.md). Record author/provenance and
modified files beside each source asset. Engine/Brogue sources keep their own
licenses. Do not download models or copy reference-game resources without
explicit redistribution terms.

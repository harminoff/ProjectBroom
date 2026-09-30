"""Fresh-process check of any saved skeletal enemy source.

Run in a separate background Blender with the saved .blend already opened:
blender --background --factory-startup --disable-autoexec --python-exit-code 1 <source.blend>
        --python tools/monster_models/blender_verify.py -- MK_NAME <result.json>

Checks every clip's first/middle/last frame against the Python master deformer,
the packed skin bytes, the bone and action counts, and that no library is linked.
"""
from pathlib import Path
import json, math, sys
import bpy

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from importlib import import_module
from tools.monster_models.skeletal_registry import find

args = sys.argv[sys.argv.index('--')+1:]
symbol, result_path = args[0], Path(args[1])
profile = find(symbol)
data = import_module('tools.monster_models.'+profile['module'])
rig = next(o for o in bpy.data.objects if o.name.endswith('_RIG'))
label = rig.name[:-4]
parts, vertices, normals, uv, triangles, influences = data.geometry()
clips, bounds = data.animation_data(vertices, influences)
objects = [bpy.data.objects[p.name] for p in parts]
scale = profile.get('visualScale', 1.0)
scene = bpy.context.scene
checks = []
for clip in clips:
    action = bpy.data.actions[label+'_'+clip['name']]
    rig.animation_data.action = action
    rig.animation_data.action_slot = action.slots[0]
    for f in sorted({1, len(clip['frames'])//2, len(clip['frames'])}):
        scene.frame_set(f)
        deps = bpy.context.evaluated_depsgraph_get()
        actual = []
        for obj in objects:
            evaluated = obj.evaluated_get(deps); mesh = evaluated.to_mesh()
            actual.extend(tuple(evaluated.matrix_world@mesh.vertices[i].co) for i in obj['runtime_vertex_map'])
            evaluated.to_mesh_clear()
        expected = [tuple(c*scale for c in v) for v in data.deform(vertices, influences, clip['frames'][f-1])]
        error = max(math.dist(a, b) for a, b in zip(actual, expected))
        assert len(actual) == len(expected) and error < .0001, (clip['name'], f, error)
        checks.append(dict(clip=clip['name'], frame=f, error=error))
skin = (ROOT/'mod/BrogueDoom'/profile['skin']).read_bytes()
assert any(i.packed_file and bytes(i.packed_file.data) == skin for i in bpy.data.images), 'packed skin differs'
assert not bpy.data.libraries, 'linked libraries present'
assert len(rig.data.bones) == len(data.BONES)
assert len(bpy.data.actions) == len(clips) and len(checks) == len({(c['clip'], c['frame']) for c in checks})
result = dict(freshProcess=True, source=bpy.data.filepath, bones=len(rig.data.bones), actions=len(bpy.data.actions),
              sampledPoses=len(checks), maxError=max(c['error'] for c in checks), packedSkinMatches=True,
              linkedLibraries=0, poses=checks)
result_path.write_text(json.dumps(result, indent=2)+'\n')
print('FRESH_OK', symbol, result['maxError'], len(checks))

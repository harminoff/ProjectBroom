"""Build/verify the editable rat skeleton without touching live Blender work.

blender --background --factory-startup --disable-autoexec --python-exit-code 1
        --python tools/monster_models/blender_rat_animation.py -- --render
"""
from pathlib import Path
import sys
import json
import math
import bpy

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from tools.monster_models import rat_animation as rigdata


def build(render=False):
    if not bpy.app.background: raise RuntimeError('Use isolated background Blender; live sessions are preserved')
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/monsters/rat/rat.blend'))
    scene=bpy.context.scene
    scene.name='Project Broom - Animated rat'
    anatomy=next(c for c in bpy.data.collections if any(o.name.startswith('Rat_continuous_coat') for o in c.objects))
    material=next(o.data.materials[0] for o in anatomy.objects if o.type=='MESH')
    for obj in list(anatomy.objects): bpy.data.objects.remove(obj,do_unlink=True)
    parts,vertices,normals,uv,triangles,influences=rigdata.geometry()
    clips,bounds=rigdata.animation_data(vertices,influences)
    arm=bpy.data.armatures.new('Rat anatomical skeleton')
    rig=bpy.data.objects.new('Rat_RIG',arm); anatomy.objects.link(rig)
    bpy.context.view_layer.objects.active=rig; rig.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    for i,(name,parent,local) in enumerate(rigdata.BONES):
        bone=arm.edit_bones.new(name)
        bone.head=rigdata.REST[i]; bone.tail=rigdata.add(bone.head,(0,1.25,0))
        if parent>=0: bone.parent=arm.edit_bones[rigdata.BONES[parent][0]]
    bpy.ops.object.mode_set(mode='OBJECT')
    rig.show_in_front=True; arm.display_type='STICK'
    objects=[]; base=0
    for part in parts:
        mesh=bpy.data.meshes.new(part.name)
        mesh.from_pydata(part.vertices,[],list(part.triangles())); mesh.update()
        layer=mesh.uv_layers.new(name='Rat atlas UV')
        for loop in mesh.loops: layer.data[loop.index].uv=part.uv[loop.vertex_index]
        for polygon in mesh.polygons: polygon.use_smooth=True
        mesh.normals_split_custom_set_from_vertices(part.normals())
        obj=bpy.data.objects.new(part.name,mesh); anatomy.objects.link(obj)
        mesh.materials.append(material)
        groups=[obj.vertex_groups.new(name=name) for name,p,v in rigdata.BONES]
        for vi,weights in enumerate(influences[base:base+len(part.vertices)]):
            for bone,weight in weights: groups[bone].add([vi],weight,'REPLACE')
        modifier=obj.modifiers.new('Rat skeletal deformation','ARMATURE'); modifier.object=rig
        obj.parent=rig; obj['license']='CC-BY-SA-4.0'; objects.append(obj)
        base+=len(part.vertices)
    actions={}; verification=[]
    evidence=ROOT/'artifacts/rat-animation'; evidence.mkdir(parents=True,exist_ok=True)
    scene.render.resolution_x=960; scene.render.resolution_y=720
    for clip in clips:
        rig.animation_data_clear()
        for f,frame in enumerate(clip['frames'],1):
            for b,(name,parent,local) in enumerate(rigdata.BONES):
                pose=rig.pose.bones[name]; row=frame[b]
                pose.rotation_mode='QUATERNION'
                pose.location=rigdata.sub(row[:3],local)
                pose.rotation_quaternion=(row[6],*row[3:6])
                pose.keyframe_insert(data_path='location',frame=f,group=name)
                pose.keyframe_insert(data_path='rotation_quaternion',frame=f,group=name)
        action=rig.animation_data.action; action.name='Rat_'+clip['name']; action.use_fake_user=True
        action['iqm_clip']=clip['name']; action['loop']=clip['loop']; action['fps']=clip['fps']
        actions[clip['name']]=action
        scene.frame_start=1; scene.frame_end=len(clip['frames']); scene.render.fps=int(clip['fps'])
        for f in sorted({1,len(clip['frames'])//2,len(clip['frames'])}):
            scene.frame_set(f); deps=bpy.context.evaluated_depsgraph_get()
            actual=[]
            for obj in objects:
                evaluated=obj.evaluated_get(deps); mesh=evaluated.to_mesh()
                actual.extend(tuple(evaluated.matrix_world@v.co) for v in mesh.vertices)
                evaluated.to_mesh_clear()
            expected=rigdata.deform(vertices,influences,clip['frames'][f-1])
            error=max(math.dist(a,b) for a,b in zip(actual,expected))
            assert len(actual)==len(expected) and error<.0001,(clip['name'],f,error)
            verification.append({'clip':clip['name'],'frame':f,'maxVertexError':error})
            if render:
                scene.render.filepath=str(evidence/f"studio-{clip['name']}-{f:02d}.png")
                bpy.ops.render.render(write_still=True)
    rig.animation_data.action=actions['idle']
    rig.animation_data.action_slot=actions['idle'].slots[0]
    scene.frame_start=1; scene.frame_end=40; scene.render.fps=20; scene.frame_set(1)
    rig['clips']=json.dumps([{k:v for k,v in c.items() if k!='frames'} for c in clips])
    rig['rebuild']='python -m tools.monster_models.rat_animation'
    scene['runtime_export']='python -m tools.monster_models.rat_animation (IQM v2)'
    scene['runtime_axes']='IQM X forward / Y lateral / Z up; not OBJ axes'
    for obj in bpy.context.selected_objects: obj.select_set(False)
    rig.select_set(True); bpy.context.view_layer.objects.active=rig
    for img in bpy.data.images:
        if img.packed_file: img.filepath='//../../../mod/BrogueDoom/graphics/BRGRAT.png'
    bpy.context.preferences.filepaths.save_version=0
    destination=ROOT/'assets/monsters/rat/rat-animated.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(destination),check_existing=False,compress=True)
    # Fresh-open proof, not a successful save return alone.
    bpy.ops.wm.open_mainfile(filepath=str(destination))
    rig=bpy.data.objects['Rat_RIG']
    assert len(rig.data.bones)==28
    assert all(bpy.data.actions.get('Rat_'+n) for n,c,f,l in rigdata.CLIPS)
    assert len([i for i in bpy.data.images if i.source=='FILE' and i.packed_file])==1
    assert len(bpy.data.libraries)==0
    result={'source':str(destination.relative_to(ROOT)).replace('\\','/'),'bones':28,'parts':len(parts),
            'clips':list(actions),'freshReopen':True,'sampledPoseChecks':verification}
    (evidence/'blender-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print('RAT_RIG_SOURCE_OK',json.dumps({k:v for k,v in result.items() if k!='sampledPoseChecks'}))


if __name__=='__main__': build('--render' in sys.argv)

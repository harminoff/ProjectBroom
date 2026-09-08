"""Build and fresh-open-check any registered enemy in isolated background Blender.

blender --background --factory-startup --disable-autoexec --python-exit-code 1
        --python tools/monster_models/blender_skeletal.py -- MK_KOBOLD --render
"""
from pathlib import Path
import sys
import json
import math
import bpy

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from importlib import import_module
from tools.monster_models.skeletal_registry import profiles
from mathutils import Vector
key=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'MK_KOBOLD'
profile=next(row for row in profiles() if row['symbol']==key)
rigdata=import_module('tools.monster_models.'+profile['module'])
label=key.removeprefix('MK_').title()


def build(render=False):
    if not bpy.app.background: raise RuntimeError('Use isolated background Blender; live sessions are preserved')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene; scene.name='Project Broom - Animated '+label
    anatomy=bpy.data.collections.new(label+' anatomy');scene.collection.children.link(anatomy)
    material=bpy.data.materials.new(label+' original diffuse');material.use_nodes=True
    image=bpy.data.images.load(str(ROOT/'mod/BrogueDoom'/profile['skin']));image.pack()
    texture=material.node_tree.nodes.new('ShaderNodeTexImage');texture.image=image
    bsdf=material.node_tree.nodes['Principled BSDF'];bsdf.inputs['Roughness'].default_value=.8
    material.node_tree.links.new(texture.outputs['Color'],bsdf.inputs['Base Color'])
    camera=bpy.data.objects.new('Review camera',bpy.data.cameras.new('Review camera'));scene.collection.objects.link(camera)
    camera.location=(58,-76,43);camera.rotation_euler=(Vector((0,0,19))-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.lens=52;scene.camera=camera
    for name,location,power in [('Key',(25,-35,65),90000),('Fill',(-25,35,35),60000)]:
        light=bpy.data.lights.new(name,'AREA');light.energy=power;light.size=40
        obj=bpy.data.objects.new(name,light);scene.collection.objects.link(obj);obj.location=location
        obj.rotation_euler=(Vector((0,0,20))-obj.location).to_track_quat('-Z','Y').to_euler()
    scene.world=bpy.data.worlds.new('Studio');scene.world.color=(.04,.04,.04)
    scene.render.engine='BLENDER_EEVEE';scene.view_settings.view_transform='AgX'
    captive='--captive' in sys.argv
    parts,vertices,normals,uv,triangles,influences=rigdata.geometry(True) if captive else rigdata.geometry()
    clips,bounds=rigdata.animation_data(vertices,influences)
    arm=bpy.data.armatures.new(label+' anatomical skeleton')
    rig=bpy.data.objects.new(label+'_RIG',arm); anatomy.objects.link(rig)
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
        runtime_map=getattr(part,'skin_topology',list(range(len(part.vertices))))
        first={}
        for i,index in enumerate(runtime_map):first.setdefault(index,i)
        source_indices=[first[i] for i in range(len(first))]
        source_triangles=list(part.triangles())
        mesh=bpy.data.meshes.new(part.name)
        mesh.from_pydata([part.vertices[i] for i in source_indices],[],
                         [tuple(runtime_map[i] for i in tri) for tri in source_triangles]); mesh.update()
        layer=mesh.uv_layers.new(name=label+' atlas UV')
        for polygon,tri in zip(mesh.polygons,source_triangles):
            for loop,i in zip(polygon.loop_indices,tri):layer.data[loop].uv=part.uv[i]
        for polygon in mesh.polygons: polygon.use_smooth=True
        normals=part.normals()
        mesh.normals_split_custom_set_from_vertices([normals[i] for i in source_indices])
        obj=bpy.data.objects.new(part.name,mesh); anatomy.objects.link(obj)
        obj['runtime_vertex_map']=runtime_map
        mesh.materials.append(material)
        groups=[obj.vertex_groups.new(name=name) for name,p,v in rigdata.BONES]
        for vi,index in enumerate(source_indices):
            weights=influences[base+index]
            for bone,weight in weights: groups[bone].add([vi],weight,'REPLACE')
        modifier=obj.modifiers.new(label+' skeletal deformation','ARMATURE'); modifier.object=rig
        obj.parent=rig; obj['license']='CC-BY-SA-4.0'; objects.append(obj)
        base+=len(part.vertices)
    visual_scale=profile.get('visualScale',1.0)
    rig.scale=(visual_scale,)*3
    rig['MODELDEF_visual_scale']=visual_scale
    actions={}; verification=[]
    evidence=ROOT/'artifacts'/((key.removeprefix('MK_').lower())+'-animation'); evidence.mkdir(parents=True,exist_ok=True)
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
        action=rig.animation_data.action; action.name=label+'_'+clip['name']; action.use_fake_user=True
        action['iqm_clip']=clip['name']; action['loop']=clip['loop']; action['fps']=clip['fps']
        actions[clip['name']]=action
        scene.frame_start=1; scene.frame_end=len(clip['frames']); scene.render.fps=int(clip['fps'])
        for f in sorted({1,len(clip['frames'])//2,len(clip['frames'])}):
            scene.frame_set(f); deps=bpy.context.evaluated_depsgraph_get()
            actual=[]
            for obj in objects:
                evaluated=obj.evaluated_get(deps); mesh=evaluated.to_mesh()
                actual.extend(tuple(evaluated.matrix_world@mesh.vertices[i].co) for i in obj['runtime_vertex_map'])
                evaluated.to_mesh_clear()
            expected=rigdata.deform(vertices,influences,clip['frames'][f-1])
            expected=[tuple(c*visual_scale for c in v) for v in expected]
            error=max(math.dist(a,b) for a,b in zip(actual,expected))
            assert len(actual)==len(expected) and error<.0001,(clip['name'],f,error)
            verification.append({'clip':clip['name'],'frame':f,'maxVertexError':error})
            if render:
                scene.render.filepath=str(evidence/f"studio-{clip['name']}-{f:02d}.png")
                bpy.ops.render.render(write_still=True)
    initial='captive' if captive else 'idle'
    rig.animation_data.action=actions[initial]
    rig.animation_data.action_slot=actions[initial].slots[0]
    scene.frame_start=1; scene.frame_end=len(clips[0]['frames']); scene.render.fps=20; scene.frame_set(1)
    rig['clips']=json.dumps([{k:v for k,v in c.items() if k!='frames'} for c in clips])
    rig['rebuild']='python -m tools.monster_models.'+profile['module']
    scene['runtime_export']='python -m tools.monster_models.'+profile['module']+' (IQM v2)'
    scene['runtime_axes']='IQM X forward / Y lateral / Z up; not OBJ axes'
    for obj in bpy.context.selected_objects: obj.select_set(False)
    rig.select_set(True); bpy.context.view_layer.objects.active=rig
    for img in bpy.data.images:
        if img.packed_file: img.filepath='//../../../mod/BrogueDoom/'+profile['skin']
    bpy.context.preferences.filepaths.save_version=0
    destination=ROOT/profile['source']
    if captive:destination=destination.with_name(destination.stem+'-captive.blend')
    bpy.ops.wm.save_as_mainfile(filepath=str(destination),check_existing=False,compress=True)
    # Fresh-open proof, not a successful save return alone.
    bpy.ops.wm.open_mainfile(filepath=str(destination))
    rig=bpy.data.objects[label+'_RIG']
    assert len(rig.data.bones)==len(rigdata.BONES)
    assert all(bpy.data.actions.get(label+'_'+n) for n,c,f,l in rigdata.CLIPS)
    assert len([i for i in bpy.data.images if i.source=='FILE' and i.packed_file])==1
    assert len(bpy.data.libraries)==0
    result={'source':str(destination.relative_to(ROOT)).replace('\\','/'),'bones':len(rigdata.BONES),'parts':len(parts),
            'clips':list(actions),'freshReopen':True,'sampledPoseChecks':verification}
    (evidence/('blender-captive-verification.json' if captive else 'blender-verification.json')).write_text(json.dumps(result,indent=2)+'\n')
    print('SKELETAL_SOURCE_OK',json.dumps({k:v for k,v in result.items() if k!='sampledPoseChecks'}))


if __name__=='__main__': build('--render' in sys.argv)

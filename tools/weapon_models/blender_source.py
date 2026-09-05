"""Create editable per-weapon Blender scenes with animated vertex-pose keys.

Run in the live Blender MCP with runpy.run_path(absolute_path), or in a fresh
background Blender. A separate process saves the deliverable so unrelated user
scenes and the current Blender save path are never overwritten.
"""
from pathlib import Path
import importlib
import math
import shutil
import subprocess
import sys
import tempfile
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from tools.weapon_models import viewmodel as vm
importlib.reload(vm)
from tools.weapon_models.generate import WEAPONS


def make_source():
    image=bpy.data.images.load(str(ROOT/'mod/BrogueDoom/graphics/BRGHANDS.png'),check_existing=False)
    image.pack(); image.name='Project Broom - original glove and weapon atlas'
    material=bpy.data.materials.new('Project Broom - game diffuse')
    material.use_nodes=True
    bsdf=material.node_tree.nodes['Principled BSDF'];bsdf.inputs['Roughness'].default_value=.65
    texture=material.node_tree.nodes.new('ShaderNodeTexImage');texture.image=image
    material.node_tree.links.new(texture.outputs['Color'],bsdf.inputs['Base Color'])
    scenes=[]; count=0
    for kind,(weapon,family) in enumerate(WEAPONS):
        scene=bpy.data.scenes.new(f'{kind:02d} - {weapon.title()}')
        bpy.context.window.scene=scene; scenes.append(scene)
        parts_collection=bpy.data.collections.new(weapon+' - editable mesh and pose keys')
        scene.collection.children.link(parts_collection)
        frames=[vm.build_parts(kind,i) for i in range(len(vm.POSE_NAMES))]
        for pi,part in enumerate(frames[0]):
            mesh=bpy.data.meshes.new(weapon+' '+part.name)
            mesh.from_pydata(part.vertices,[],part.faces);mesh.update()
            uv=mesh.uv_layers.new(name='Game atlas')
            for loop in mesh.loops: uv.data[loop.index].uv=part.uv[loop.vertex_index]
            for polygon in mesh.polygons: polygon.use_smooth=True
            mesh.normals_split_custom_set_from_vertices(part.normals())
            obj=bpy.data.objects.new(part.name,mesh);parts_collection.objects.link(obj)
            mesh.materials.append(material);obj['material_region']=part.material
            obj['license']='CC-BY-SA-4.0';obj['brogue_weapon_kind']=kind
            obj.shape_key_add(name='Ready (basis)')
            for index in range(1,len(vm.POSE_NAMES)):
                key=obj.shape_key_add(name=vm.POSE_NAMES[index])
                for vert,co in zip(key.data,frames[index][pi].vertices): vert.co=co
                for t,value in ((1,0),(index*3,0),(index*3+1,1),(index*3+4,0)):
                    key.value=value;key.keyframe_insert('value',frame=t)
            count+=1
        camera_data=bpy.data.cameras.new(weapon+' first-person camera')
        camera=bpy.data.objects.new('First-person preview',camera_data)
        scene.collection.objects.link(camera);camera.location=(0,0,0)
        camera.rotation_euler=Vector((1,0,0)).to_track_quat('-Z','Y').to_euler()
        camera_data.lens=24;camera_data.clip_start=.5;camera_data.clip_end=1000;scene.camera=camera
        world=bpy.data.worlds.new(weapon+' studio');world.use_nodes=True
        world.node_tree.nodes['Background'].inputs[0].default_value=(.045,.052,.061,1)
        world.node_tree.nodes['Background'].inputs[1].default_value=.55;scene.world=world
        for label,loc,power,color in (('Warm key',(15,-30,45),26000,(1,.85,.68)),('Cool fill',(10,35,20),16000,(.7,.83,1))):
            data=bpy.data.lights.new(label,'AREA');data.energy=power;data.size=35;data.color=color
            obj=bpy.data.objects.new(label,data);scene.collection.objects.link(obj);obj.location=loc
            obj.rotation_euler=(Vector((35,0,-10))-obj.location).to_track_quat('-Z','Y').to_euler()
        scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=1440;scene.render.resolution_y=1080
        scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX'
        scene.render.image_settings.file_format='PNG';scene.render.filepath=str(ROOT/f'artifacts/weapon-models/source-{kind:02d}.png')
        scene.frame_end=46;scene.render.fps=35;scene.frame_set(1)
        for i,name in enumerate(vm.POSE_NAMES): scene.timeline_markers.new(name,frame=1+i*3)
        scene['runtime_export']='python -m tools.weapon_models.generate'
        scene['authority']='Presentation only. Brogue CE resolves all actions before animation.'
        scene['pose_keys']='Editable MD3 pose samples. Timeline is a pose review, not exact runtime state durations.'
    bpy.context.window.scene=scenes[0]
    evidence=ROOT/'artifacts/weapon-models';evidence.mkdir(parents=True,exist_ok=True)
    output=ROOT/'assets/weapons/hero-weapons.blend'
    with tempfile.TemporaryDirectory(prefix='weapons-source-',dir=evidence) as temporary:
        library=Path(temporary)/'weapons-library.blend'
        bpy.data.libraries.write(str(library),set(scenes),path_remap='RELATIVE_ALL',fake_user=True,compress=True)
        completed=subprocess.run([bpy.app.binary_path,'--background','--factory-startup','--disable-autoexec',
                                 '--python-exit-code','1','--python',str(Path(__file__).resolve()),'--',
                                 '--finalize',str(library),str(output)],capture_output=True,text=True)
        if completed.returncode: raise RuntimeError(completed.stdout+'\n'+completed.stderr)
    return dict(scenes=len(scenes),objects=count,source=str(output),active_scene=scenes[0].name)


def finalize(library,output):
    with bpy.data.libraries.load(str(library),link=False) as (available,loaded): loaded.scenes=available.scenes
    scenes=sorted(loaded.scenes,key=lambda s:s.name)
    for window in bpy.context.window_manager.windows: window.scene=scenes[0]
    for old in list(bpy.data.scenes):
        if old not in scenes: bpy.data.scenes.remove(old)
    bpy.data.orphans_purge(do_recursive=True)
    for image in bpy.data.images:
        if image.packed_file: image.filepath='//../../mod/BrogueDoom/graphics/BRGHANDS.png'
    for scene in scenes:
        scene.render.filepath='//../../artifacts/weapon-models/source-'+scene.name[:2]+'.png'
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.region_3d.view_perspective='CAMERA'
                area.spaces.active.shading.type='MATERIAL'
    bpy.context.preferences.filepaths.save_version=0
    with tempfile.TemporaryDirectory(prefix='weapons-save-',dir=ROOT/'artifacts/weapon-models') as temporary:
        finished=Path(temporary)/'hero-weapons.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(finished),compress=True,check_existing=False,relative_remap=False)
        # Copy, not rename: do not transfer a private temp directory's Windows ACL.
        shutil.copyfile(finished,output)


if '--finalize' in sys.argv:
    args=sys.argv[sys.argv.index('--finalize')+1:];finalize(Path(args[0]),Path(args[1]))
else:
    result=make_source()

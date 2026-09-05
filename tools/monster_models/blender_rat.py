"""Build the editable rat source in a separate Blender scene.

Blender: exec(compile(open(absolute_script_path).read(), absolute_script_path, 'exec'))
Uses the deterministic anatomical mesh/UV data from rat.py, preserving other scenes.
"""
from pathlib import Path
import sys
import math
import subprocess
import tempfile
import importlib
import shutil
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.monster_models import rat
importlib.reload(rat)


def create_source():
    # Unique scene avoids modifying a user's current Blender work.
    scene = bpy.data.scenes.new("Project Broom - Rat")
    bpy.context.window.scene = scene
    anatomy = bpy.data.collections.new("Rat - editable anatomy")
    scene.collection.children.link(anatomy)
    image = bpy.data.images.load(str(ROOT/"mod/BrogueDoom/graphics/BRGRAT.png"), check_existing=False)
    image.name = "BRGRAT - original fur and skin atlas"
    image.pack()
    material = bpy.data.materials.new("Rat - game diffuse atlas")
    material.use_nodes = True
    nodes=material.node_tree.nodes
    bsdf=nodes.get("Principled BSDF")
    bsdf.inputs["Roughness"].default_value=.76
    texture=nodes.new("ShaderNodeTexImage")
    texture.image=image
    material.node_tree.links.new(texture.outputs["Color"],bsdf.inputs["Base Color"])
    objects=[]
    for part in rat.build_parts():
        mesh=bpy.data.meshes.new(part.name)
        mesh.from_pydata(part.vertices, [], list(part.triangles()))
        mesh.update()
        uv=mesh.uv_layers.new(name="Rat atlas UV")
        for loop in mesh.loops:
            uv.data[loop.index].uv=part.uv[loop.vertex_index]
        for polygon in mesh.polygons:
            polygon.use_smooth=True
        mesh.normals_split_custom_set_from_vertices(part.normals())
        obj=bpy.data.objects.new(part.name,mesh)
        anatomy.objects.link(obj)
        obj.data.materials.append(material)
        obj["asset_kind"]="MK_RAT"
        obj["license"]="CC-BY-SA-4.0"
        objects.append(obj)
    stage=bpy.data.collections.new("Preview only - excluded from export")
    scene.collection.children.link(stage)
    mesh=bpy.data.meshes.new("Preview floor")
    mesh.from_pydata([(-200,-200,-.04),(200,-200,-.04),(200,200,-.04),(-200,200,-.04)],[],[(0,1,2,3)])
    floor=bpy.data.objects.new("Preview floor",mesh)
    stage.objects.link(floor)
    floor_mat=bpy.data.materials.new("Preview slate")
    floor_mat.diffuse_color=(.047,.055,.062,1)
    floor_mat.use_nodes=True
    floor_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=(.047,.055,.062,1)
    floor_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value=.9
    floor.data.materials.append(floor_mat)
    world=bpy.data.worlds.new("Rat studio world")
    world.use_nodes=True
    world.node_tree.nodes["Background"].inputs[0].default_value=(.085,.1,.12,1)
    world.node_tree.nodes["Background"].inputs[1].default_value=.45
    scene.world=world
    def aim(obj, target):
        obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    for name,loc,power,size,color in [
        ("Key",(15,-30,50),24000,35,(1,.87,.74)),
        ("Fill",(10,35,25),12000,30,(.69,.8,1)),
        ("Rim",(-35,10,32),26000,25,(1,.92,.82))]:
        data=bpy.data.lights.new(name,'AREA')
        data.energy=power
        data.shape='DISK'
        data.size=size
        data.color=color
        obj=bpy.data.objects.new(name,data)
        stage.objects.link(obj)
        obj.location=loc
        aim(obj,(-2,0,6))
    camera_data=bpy.data.cameras.new("Rat portrait camera")
    camera=bpy.data.objects.new("Rat portrait camera",camera_data)
    stage.objects.link(camera)
    camera.location=(43,-63,35)
    aim(camera,(-4,0,6))
    camera_data.type='ORTHO'
    camera_data.ortho_scale=66
    scene.camera=camera
    scene.render.engine='BLENDER_EEVEE'
    scene.render.resolution_x=1440
    scene.render.resolution_y=1080
    scene.render.resolution_percentage=100
    scene.view_settings.view_transform='AgX'
    scene.render.image_settings.file_format='PNG'
    scene.render.filepath=str(ROOT/"artifacts/rat-model/rat-blender.png")
    scene["description"]="Gray scavenger of the shallows. Presentation only; Brogue remains authoritative."
    scene["runtime_export"]="python -m tools.monster_models.rat"
    scene["runtime_axes"]="Blender X forward / Z up => OBJ X forward / Y up / -Z lateral"
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.region_3d.view_distance=65
                area.spaces.active.region_3d.view_location=(-3,0,6)
                area.spaces.active.region_3d.view_rotation=camera.rotation_euler.to_quaternion()
                area.spaces.active.shading.type='MATERIAL'
    source=ROOT/"assets/monsters/rat/rat.blend"
    source.parent.mkdir(parents=True,exist_ok=True)
    # Write only this scene and its dependencies, keeping the user's current
    # unrelated scene out of the delivered file. Does not change their save path.
    # Library-only files have no saved active window/scene. Convert in an
    # isolated background Blender so double-clicking the deliverable opens the
    # rat normally, without saving unrelated scenes from the user's session.
    evidence = ROOT/'artifacts/rat-model'
    evidence.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='rat-authoring-', dir=evidence) as temporary:
        library = Path(temporary)/'rat-library.blend'
        bpy.data.libraries.write(str(library), {scene}, path_remap='RELATIVE_ALL', fake_user=True, compress=True)
        subprocess.run([bpy.app.binary_path, '--background', '--factory-startup',
                        '--disable-autoexec', '--python-exit-code', '1', '--python', str(Path(__file__).resolve()),
                        '--', '--finalize', str(library), str(source)], check=True, capture_output=True, text=True)
    return {"scene":scene.name,"objects":len(objects),"blend":str(source),"preview":scene.render.filepath}


def finalize_source(library, path):
    with bpy.data.libraries.load(str(library), link=False) as (available, loaded):
        loaded.scenes = available.scenes
    scene = loaded.scenes[0]
    for window in bpy.context.window_manager.windows:
        window.scene = scene
    for old_scene in list(bpy.data.scenes):
        if old_scene != scene:
            bpy.data.scenes.remove(old_scene)
    bpy.data.orphans_purge(do_recursive=True)
    scene.name = 'Project Broom - Rat'
    scene.render.filepath = '//../../../artifacts/rat-model/rat-blender.png'
    for image in bpy.data.images:
        if image.packed_file:
            image.filepath = '//../../../mod/BrogueDoom/graphics/BRGRAT.png'
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces.active.region_3d.view_distance = 65
                area.spaces.active.region_3d.view_location = (-3,0,6)
                area.spaces.active.region_3d.view_rotation = scene.camera.rotation_euler.to_quaternion()
                area.spaces.active.shading.type = 'MATERIAL'
    bpy.context.preferences.filepaths.save_version = 0
    # Blender forbids saving over a file still registered as an appended
    # library. Save a normal file to an owned temporary path, then publish it.
    with tempfile.TemporaryDirectory(prefix='rat-finalize-', dir=ROOT/'artifacts/rat-model') as temporary:
        finished = Path(temporary)/'rat.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(finished), compress=True, check_existing=False,
                                   relative_remap=False)
        # Copy the finished bytes into the destination directory. Renaming a
        # file from Python's private temp directory can carry its restrictive
        # Windows ACL into the user-facing asset, making Blender unable to read
        # a file generated by a sandbox account.
        shutil.copyfile(finished, path)


if '--finalize' in sys.argv:
    arguments = sys.argv[sys.argv.index('--finalize')+1:]
    finalize_source(Path(arguments[0]), Path(arguments[-1]))
else:
    result=create_source()

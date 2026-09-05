"""Isolated editable pickup source: one origin-centered scene per runtime model."""
import json
import sys
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from tools.pickup_models.generate import CATEGORIES, class_name
from tools.pickup_models.detailed import build_parts


def main():
    if not bpy.app.background: raise RuntimeError('Use an isolated background Blender process, not a live scene')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version=0
    image=bpy.data.images.load(str(ROOT/'mod/BrogueDoom/graphics/BRGPICKS.png'));image.pack()
    mat=bpy.data.materials.new('Project Broom pickup diffuse');mat.use_nodes=True
    shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Roughness'].default_value=.7
    tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image
    mat.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color'])
    floor_mat=bpy.data.materials.new('Preview slate');floor_mat.diffuse_color=(.065,.075,.085,1)
    world=bpy.data.worlds.new('Review world');world.use_nodes=True
    world.node_tree.nodes['Background'].inputs[0].default_value=(.17,.2,.25,1)
    world.node_tree.nodes['Background'].inputs[1].default_value=.5
    stage=bpy.data.collections.new('PREVIEW ONLY - shared floor lights and camera')
    floor=bpy.data.meshes.new('64-unit floor reference')
    floor.from_pydata([(-32,-32,0),(32,-32,0),(32,32,0),(-32,32,0)],[],[(0,1,2,3)])
    obj=bpy.data.objects.new('64-unit floor reference',floor);stage.objects.link(obj);floor.materials.append(floor_mat)
    def aim(obj): obj.rotation_euler=(Vector((0,0,3))-obj.location).to_track_quat('-Z','Y').to_euler()
    camera=bpy.data.objects.new('Pickup review camera',bpy.data.cameras.new('Pickup review camera'))
    stage.objects.link(camera);camera.location=(38,-52,44);aim(camera);camera.data.type='ORTHO';camera.data.ortho_scale=65
    for name,position,energy,size in [('Key',(25,-40,65),65000,45),('Fill',(-35,-10,35),30000,40),('Rim',(10,35,45),55000,35)]:
        light=bpy.data.lights.new(name,'AREA');light.energy=energy;light.size=size
        obj=bpy.data.objects.new(name,light);stage.objects.link(obj);obj.location=position;aim(obj)
    records=[]; first=bpy.context.scene
    for category in CATEGORIES:
        for kind in ([None] if category.hidden_identity else [])+list(range(len(category.names))):
            cls=class_name(category.value,kind)
            scene=bpy.data.scenes.new(cls);scene.world=world;scene.camera=camera;scene.collection.children.link(stage)
            asset=bpy.data.collections.new(cls+' - ASSET ONLY');scene.collection.children.link(asset)
            parts=build_parts(category,kind)
            for part in parts:
                mesh=bpy.data.meshes.new(part.name);mesh.from_pydata(part.vertices,[],part.faces);mesh.update()
                uv=mesh.uv_layers.new(name='Runtime atlas')
                for loop in mesh.loops: uv.data[loop.index].uv=part.uv[loop.vertex_index]
                for polygon in mesh.polygons: polygon.use_smooth=True
                mesh.normals_split_custom_set_from_vertices(part.normals())
                obj=bpy.data.objects.new(part.name,mesh);asset.objects.link(obj);mesh.materials.append(mat)
            scene['runtime_class']=cls;scene['export_collection']=asset.name
            scene['name']=category.names[kind] if kind is not None else 'unidentified '+category.symbol.lower()
            scene['license']='CC-BY-SA-4.0; original Project Broom geometry and diffuse'
            scene['source_of_truth']='tools/pickup_models/detailed.py; reconcile manual edits before regeneration'
            scene['scale']='Map units. 64-unit cell; dimensions are artistic inference, not Brogue rules.'
            scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=700;scene.render.resolution_y=700;scene.render.resolution_percentage=100
            scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG'
            scene.render.filepath=str(ROOT/f'artifacts/pickup-models/studio/{cls}.png')
            records.append({'class':cls,'parts':len(parts),'vertices':sum(len(p.vertices) for p in parts)})
    bpy.data.scenes.remove(first)
    bpy.context.window.scene=bpy.data.scenes['BroguePickupC0016Generic']
    path=ROOT/'assets/items/pickups.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
    bpy.ops.wm.open_mainfile(filepath=str(path))
    assert len(bpy.data.scenes)==105 and not bpy.data.libraries
    assert sum(bool(i.packed_file) for i in bpy.data.images)==1
    for r in records:
        scene=bpy.data.scenes[r['class']];asset=bpy.data.collections[scene['export_collection']]
        assert len(asset.objects)==r['parts']
        assert sum(len(o.data.vertices) for o in asset.objects)==r['vertices']
    out=ROOT/'artifacts/pickup-models';out.mkdir(parents=True,exist_ok=True)
    (out/'blender-verification.json').write_text(json.dumps({'freshReopen':True,'scenes':105,'packedImages':1,'models':records},indent=2)+'\n')
    if '--render' in sys.argv:
        (out/'studio').mkdir(exist_ok=True)
        for category in CATEGORIES:
            # Show the unknown version players actually see for hidden categories.
            variants=[None] if category.hidden_identity else [0]
            if category.symbol in ('ARMOR','KEY','FOOD'): variants=list(range(len(category.names)))
            for kind in variants:
                scene=bpy.data.scenes[class_name(category.value,kind)];bpy.context.window.scene=scene
                bpy.ops.render.render(write_still=True)
    print('PICKUP_SOURCE_VERIFIED scenes=105 packedImages=1')


main()

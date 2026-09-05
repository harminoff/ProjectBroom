"""Build isolated, editable creature .blend files and calibrated review renders.

Run only in a separate background Blender process. Never clears a live session.
Usage: blender --background --factory-startup --python-exit-code 1 --python
       tools/monster_models/blender_creatures.py -- --kind 2 [--render]
Omit --kind to build all 66 replacements. --before renders preserved placeholders.
"""
from pathlib import Path
import argparse
import json
import math
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from tools.monster_models import rat, creatures
from tools.monster_models.bestiary import source_records


def material(name,color):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*color,1)
    m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8
    return m


def object_from_part(part,collection,mat):
    mesh=bpy.data.meshes.new(part.name)
    mesh.from_pydata(part.vertices,[],list(part.triangles()))
    mesh.update()
    uv=mesh.uv_layers.new(name='Game diffuse UV')
    for loop in mesh.loops: uv.data[loop.index].uv=part.uv[loop.vertex_index]
    for face in mesh.polygons: face.use_smooth=True
    mesh.normals_split_custom_set_from_vertices(part.normals())
    obj=bpy.data.objects.new(part.name,mesh)
    collection.objects.link(obj)
    mesh.materials.append(mat)
    return obj


def placeholder_parts(path):
    # Existing placeholder OBJ has one UV; parse it without introducing exporter dependencies.
    p=rat.Part('Preserved_placeholder')
    coords=[]; uv=[]
    for line in path.read_text().splitlines():
        f=line.split()
        if not f: continue
        if f[0]=='v': coords.append(tuple(map(float,f[1:])))
        elif f[0]=='vt': uv.append(tuple(map(float,f[1:])))
        elif f[0]=='f': p.faces.append(tuple(int(v.split('/')[0])-1 for v in f[1:]))
    p.vertices=[(x,-z,y) for x,y,z in coords]
    p.uv=[uv[0]]*len(coords)
    return [p]


def build_one(record,render=False,before=False):
    if not bpy.app.background:
        raise RuntimeError('This isolated builder must never reset an interactive Blender session')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    k=record['kind']; slug=record['symbol'].removeprefix('MK_').lower()
    scene.name=f'BRG-M{k:02d} - {record["name"]}'
    anatomy=bpy.data.collections.new('ASSET - editable anatomy (export only this)')
    stage=bpy.data.collections.new('PREVIEW ONLY - 64-unit grid and 58-unit scale staff')
    scene.collection.children.link(anatomy); scene.collection.children.link(stage)
    if before:
        parts=placeholder_parts(ROOT/f'artifacts/creature-models/baseline/monsters/{k:02d}_{slug}.obj')
        skin=ROOT/'artifacts/creature-models/baseline/BRGMON.png'
    else:
        parts=rat.build_parts() if k==1 else creatures.build_parts(record)
        skin=ROOT/f'mod/BrogueDoom/graphics/{"BRGRAT" if k==1 else f"BRGM{k:02d}"}.png'
    image=bpy.data.images.load(str(skin),check_existing=False)
    image.pack()
    mat=material('Original game diffuse',(.45,.45,.45))
    tex=mat.node_tree.nodes.new('ShaderNodeTexImage'); tex.image=image
    mat.node_tree.links.new(tex.outputs['Color'],mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
    objects=[]
    for part in parts:
        obj=object_from_part(part,anatomy,mat)
        obj['brogue_kind']=k; obj['work_id']=f'BRG-M{k:02d}'
        obj['license']='CC-BY-SA-4.0'
        objects.append(obj)
    floor_mesh=bpy.data.meshes.new('Preview floor')
    floor_mesh.from_pydata([(-160,-160,-.1),(160,-160,-.1),(160,160,-.1),(-160,160,-.1)],[],[(0,1,2,3)])
    floor=bpy.data.objects.new('Preview floor',floor_mesh); stage.objects.link(floor)
    floor.data.materials.append(material('Preview slate',(.045,.052,.058)))
    gridmat=material('Scale grid',(.24,.31,.34))
    ref=creatures.Sculpt()
    for axis in (0,1):
        for n in (-32,32):
            controls=[(-96,n,.1,.15),(96,n,.1,.15)] if axis==0 else [(n,-96,.1,.15),(n,96,.1,.15)]
            ref.strand(f'64_unit_cell_edge_{axis}_{n}',controls,'bone',6,1)
    ref.strand('58_unit_humanoid_scale_staff',[(-35,32,0,.45),(-35,32,58,.45)],'bone',8,1)
    for z in range(0,59,8): ref.strand(f'Staff_tick_{z}',[(-37,32,z,.22),(-33,32,z,.22)],'bone',6,1)
    for p in ref.parts: object_from_part(p,stage,gridmat)
    def text(name,value,location,size=3):
        data=bpy.data.curves.new(name,'FONT'); data.body=value; data.size=size
        obj=bpy.data.objects.new(name,data); stage.objects.link(obj)
        obj.location=location
        data.materials.append(gridmat)
    text('Index_label',f'BRG-M{k:02d}  {record["name"]}',(-31,-37,.2),3)
    text('Grid_label','64 map units',(-31,-42,.2),2.5)
    world=bpy.data.worlds.new('Creature review studio'); world.use_nodes=True
    world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.15,.18,1)
    world.node_tree.nodes['Background'].inputs[1].default_value=.5
    scene.world=world
    def aim(obj,target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    for name,location,energy,size in [('Key',(70,-90,130),140000,90),('Fill',(50,80,85),90000,80),('Rim',(-70,20,120),140000,70)]:
        data=bpy.data.lights.new(name,'AREA'); data.energy=energy; data.shape='DISK'; data.size=size
        obj=bpy.data.objects.new(name,data); stage.objects.link(obj); obj.location=location; aim(obj,(0,0,30))
    camera=bpy.data.objects.new('Calibrated three-quarter camera',bpy.data.cameras.new('Calibrated three-quarter camera'))
    stage.objects.link(camera); camera.location=(132,-172,113); aim(camera,(0,0,36))
    camera.data.type='ORTHO'; camera.data.ortho_scale=145
    scene.camera=camera
    scene.render.engine='BLENDER_EEVEE'
    scene.render.resolution_x=900; scene.render.resolution_y=900; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.view_settings.view_transform='AgX'
    scene['brogue_description']=record['description']; scene['brogue_isLarge']=record['isLarge']
    scene['scale_policy']='Map units, not real meters. 64-unit grid, 58-unit humanoid staff. Numeric sizes are art inference.'
    scene['source_of_truth']='Python procedural source; reconcile Blender hand edits before regeneration'
    scene['export_collection']=anatomy.name
    scene['runtime_axes']='Blender (X,Y,Z) => OBJ (X,Z,-Y)'
    for obj in objects: obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.region_3d.view_distance=140
                area.spaces.active.region_3d.view_location=(0,0,32)
                area.spaces.active.region_3d.view_rotation=camera.rotation_euler.to_quaternion()
                area.spaces.active.shading.type='MATERIAL'
    scene.render.filepath=str(ROOT/f'artifacts/creature-models/{"before" if before else "after"}/{k:02d}_{slug}.png')
    Path(scene.render.filepath).parent.mkdir(parents=True,exist_ok=True)
    if not before and k>1:
        out=ROOT/f'assets/monsters/sources/{k:02d}_{slug}.blend'; out.parent.mkdir(parents=True,exist_ok=True)
        image.filepath=f'//../../../mod/BrogueDoom/graphics/BRGM{k:02d}.png'
        bpy.context.preferences.filepaths.save_version=0
        bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True,check_existing=False)
    if render: bpy.ops.render.render(write_still=True)
    return {'kind':k,'parts':len(parts),'images':len(bpy.data.images),'packed':sum(bool(i.packed_file) for i in bpy.data.images),'libraries':len(bpy.data.libraries)}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--kind',type=int,action='append')
    parser.add_argument('--render',action='store_true')
    parser.add_argument('--before',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    results=[]
    for record in source_records():
        if record['kind']<1: continue
        if args.kind and record['kind'] not in args.kind: continue
        if record['kind']==1 and args.before: continue
        results.append(build_one(record,args.render,args.before))
        print('CREATURE_SOURCE '+json.dumps(results[-1]),flush=True)
    (ROOT/f'artifacts/creature-models/blender-{"before" if args.before else "after"}.json').write_text(json.dumps(results,indent=2)+'\n')


if __name__=='__main__': main()

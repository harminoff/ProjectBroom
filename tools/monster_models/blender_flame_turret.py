"""Isolated flame turret authoring with the runtime atlas-local fire emission preview."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
if '--' not in sys.argv:sys.argv+=['--','MK_FLAME_TURRET']
import bpy
from tools.monster_models import blender_skeletal
from tools.monster_models.flame_turret_materials import EMISSIVE_U
blender_skeletal.build()
mat=bpy.data.materials['Flame_Turret original diffuse'];nodes=mat.node_tree.nodes;links=mat.node_tree.links
tex=next(n for n in nodes if n.type=='TEX_IMAGE');bsdf=nodes['Principled BSDF']
coord=nodes.new('ShaderNodeTexCoord');split=nodes.new('ShaderNodeSeparateXYZ');links.new(coord.outputs['UV'],split.inputs[0])
mask=nodes.new('ShaderNodeMath');mask.operation='GREATER_THAN';mask.inputs[1].default_value=EMISSIVE_U
links.new(split.outputs['X'],mask.inputs[0]);links.new(mask.outputs[0],bsdf.inputs['Emission Strength']);links.new(tex.outputs['Color'],bsdf.inputs['Emission Color'])
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets/monsters/flame_turret/flame-turret-animated.blend'),check_existing=False,compress=True)
print('FLAME_TURRET_SOURCE_SAVED')

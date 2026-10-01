"""Isolated salamander authoring with the runtime atlas-local flame preview."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
if '--' not in sys.argv:sys.argv+=['--','MK_SALAMANDER']
import bpy
from tools.monster_models import blender_skeletal
blender_skeletal.build()
mat=bpy.data.materials['Salamander original diffuse'];nodes=mat.node_tree.nodes;links=mat.node_tree.links
tex=next(n for n in nodes if n.type=='TEX_IMAGE');bsdf=nodes['Principled BSDF']
coord=nodes.new('ShaderNodeTexCoord');split=nodes.new('ShaderNodeSeparateXYZ');links.new(coord.outputs['UV'],split.inputs[0])
masks=[]
for operation,value in [('GREATER_THAN',.79),('LESS_THAN',.83)]:
 node=nodes.new('ShaderNodeMath');node.operation=operation;node.inputs[1].default_value=value;links.new(split.outputs['X'],node.inputs[0]);masks.append(node.outputs[0])
mask=nodes.new('ShaderNodeMath');mask.operation='MULTIPLY'
links.new(masks[0],mask.inputs[0]);links.new(masks[1],mask.inputs[1]);links.new(mask.outputs[0],bsdf.inputs['Emission Strength']);links.new(tex.outputs['Color'],bsdf.inputs['Emission Color'])
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets/monsters/salamander/salamander-animated.blend'),check_existing=False,compress=True)

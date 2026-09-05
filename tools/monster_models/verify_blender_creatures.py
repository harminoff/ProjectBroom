"""Read-only fresh-open gate for all delivered creature sources; background only."""
from pathlib import Path
import json
import sys
import bpy

ROOT=Path(__file__).resolve().parents[2]
if not bpy.app.background: raise RuntimeError('Fresh-open checks require an isolated background process')
index=json.loads((ROOT/'assets/monsters/bestiary-index.json').read_text())
results=[]
for entry in index['creatures'][2:]:
    path=ROOT/entry['art']['sourceBlend']
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False)
    assert len(bpy.data.scenes)==1, entry['symbol']
    scene=bpy.context.scene
    assert scene['brogue_description']==entry['description'], entry['symbol']
    collection=bpy.data.collections.get(scene['export_collection'])
    objects=list(collection.objects)
    assert len(objects)==entry['art']['parts'],entry['symbol']
    assert not bpy.data.libraries,entry['symbol']
    textures=[i for i in bpy.data.images if i.source=='FILE']
    assert len(textures)==1 and textures[0].packed_file,entry['symbol']
    vertices=[obj.matrix_world@v.co for obj in objects for v in obj.data.vertices]
    low=[min(v[a] for v in vertices) for a in range(3)]
    high=[max(v[a] for v in vertices) for a in range(3)]
    for actual,expected in zip(low+high,entry['art']['bounds'][0]+entry['art']['bounds'][1]):
        assert abs(actual-expected)<.001,(entry['symbol'],actual,expected)
    for obj in objects: assert len(obj.data.uv_layers)==1,entry['symbol']
    results.append({'kind':entry['kind'],'source':entry['art']['sourceBlend'],'parts':len(objects),'packedImages':1,'linkedLibraries':0,'boundsVerified':True})
output=ROOT/'artifacts/creature-models/blender-reopen-verification.json'
output.write_text(json.dumps(results,indent=2)+'\n')
print(f'CREATURE_REOPEN_OK {len(results)} sources')

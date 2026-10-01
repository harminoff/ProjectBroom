"""Original CC-BY-SA-4.0 named materials. No game RNG or effect-kind selection."""
import io
import json
import math
import re
from PIL import Image
from tools.pickup_models import detailed
from tools.weapon_models import viewmodel

PALETTES={
 'Staff':[(137,95,50),(156,117,67),(145,61,39),(168,111,77),(175,151,102),(99,43,29),(200,167,108),(209,176,120),(183,170,74),(69,51,35),(171,117,74),(221,208,174),(167,82,57),(168,152,113),(87,56,40),(153,81,43),(95,40,41),(179,122,61),(177,132,74),(153,117,78),(162,133,88)],
 'Wand':[(150,98,48),(139,151,162),(187,148,58),(132,132,123),(172,168,147),(187,104,62),(203,210,214),(80,87,92),(116,132,147),(67,94,153),(224,228,232),(190,196,205)],
 'Ring':[(224,236,244),(224,198,195),(111,27,49),(193,27,55),(133,65,178),(224,163,36),(20,23,27),(49,128,107),(30,68,179),(35,28,40),(45,142,75),(88,199,213),(20,161,80),(113,172,115),(72,119,135),(175,143,106),(35,78,47),(162,68,41)]}

def catalog(root):
    source=(root/'src/brogue-mapgen/src/brogue/Globals.c').read_text()
    return {kind:dict(zip(re.findall(r'"([a-z]+)"',source.split('const char '+ref)[1].split('};')[0]),PALETTES[kind]))
            for kind,ref in [('Staff','itemWoodsRef'),('Wand','itemMetalsRef'),('Ring','itemGemsRef')]}

def skin(image, materials, changes, flavor, gem=False):
    image=image.copy(); tile=image.width//4; tile_height=image.height//(len(materials)//4)
    for material,color in changes.items():
        index=materials.index(material); x0=index%4*tile; y0=index//4*tile_height
        pixels=image.load()
        for y in range(tile_height):
            for x in range(tile):
                noise=((x*73856093 ^ y*19349663)&255)/255-.5
                grain=math.sin(x*.31+math.sin(y*.025)*4)
                metal=flavor in ('bronze','steel','brass','pewter','nickel','copper','aluminum','tungsten','titanium','cobalt','chromium','silver')
                delta=noise*7+grain*8 if material=='wood' and not metal else noise*4+math.sin(x*.026)*16
                if flavor=='bamboo': delta-=18*(y%64<5)
                if flavor=='birch': delta-=40*(math.sin(x*.09+y*.5)>.94)
                rgb=[v+delta for v in color]
                if gem:
                    stripe=math.sin(y*.08+math.sin(x*.04)*3)
                    if flavor in ('malachite','agate','jasper'): rgb=[v+stripe*22 for v in rgb]
                    if flavor=='bloodstone' and noise>.43: rgb=[139,35,28]
                    if flavor in ('opal','alexandrite','diamond'): rgb=[v+math.sin((x+y)*.08+c*2)*25 for c,v in enumerate(rgb)]
                pixels[x0+x,y0+y]=tuple(max(0,min(255,round(v))) for v in rgb)
    out=io.BytesIO(); image.save(out,format='PNG',compress_level=9); return out.getvalue()

def generate(root):
    colors=catalog(root); out=root/'mod/BrogueDoom'; definitions=[]; classes=[]; records=[]
    floor=Image.open(io.BytesIO(detailed.atlas_bytes())); held=Image.open(io.BytesIO(viewmodel.atlas_bytes()))
    for kind,palette in colors.items():
        for flavor,rgb in palette.items():
            cls=f'BrogueFlavor{kind}{flavor}'; filename=f'BRGFL_{kind}_{flavor}.png'
            changes={'wood':rgb} if kind=='Staff' else {'wood':rgb,'brass':rgb} if kind=='Wand' else {'glass':rgb}
            (out/'graphics'/filename).write_bytes(skin(floor,detailed.MATERIALS,changes,flavor,kind=='Ring'))
            classes.append(f'class {cls} : BroguePickupProxyBase {{}}')
            definitions.append(f'Model {cls}\n{{ Path "models/pickups"\n Model 0 "{kind.lower()}_generic.obj"\n Skin 0 "graphics/{filename}"\n FrameIndex ITM0 A 0 0\n}}')
            if kind!='Ring':
                view=f'BrogueFlavorView{kind}{flavor}'; viewskin='VIEW_'+filename
                (out/'graphics'/viewskin).write_bytes(skin(held,viewmodel.MATERIALS,{'wood' if kind=='Staff' else 'brass':rgb},flavor))
                classes.append(f'class {view} : BrogueView{kind} {{}}')
                sprite='BDST' if kind=='Staff' else 'BDWA'
                frames='\n'.join(f' FrameIndex {sprite} {chr(65+i)} 0 {i}' for i in range(9))
                definitions.append(f'Model {view}\n{{ Path "models/devices"\n Model 0 "{kind.lower()}.md3"\n Skin 0 "graphics/{viewskin}"\n ScaleWeaponFOV\n{frames}\n}}')
            records.append({'category':kind,'appearance':flavor,'rgb':rgb,'class':cls})
    (out/'brogue_flavors.zs').write_text('\n'.join(classes)+'\n')
    (out/'models/pickups/FLAVORS.txt').write_text('\n'.join(definitions)+'\n')
    (root/'assets/items/flavor-materials.json').write_text(json.dumps(records,indent=2)+'\n')
    cases=[f'{{{dict(Staff=32,Wand=64,Ring=128)[r["category"]]},"{r["appearance"]}"}}' for r in records]
    cases += ['{16,"ABRA KADABRA"}','{16,"ZELGO MER"}','{16,"READ ME"}']
    (root/'src/gzdoom-bridge/flavor_cases.generated.h').write_text('static const struct { int category; const char *name; } FlavorCases[]={'+','.join(cases)+'};\n')
    print(f'Generated {len(records)} assigned materials and 33 held variants')

if __name__=='__main__':
    from pathlib import Path
    generate(Path(__file__).resolve().parents[2])

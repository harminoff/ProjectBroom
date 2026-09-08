"""Original deterministic terrain fragments, frost and mechanism forms (CC0)."""
from pathlib import Path
import sys
from PIL import Image, ImageDraw
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.search_models.generate import box

def generate():
    from tools.shoreline_assets import generate as generate_shorelines
    generate_shorelines()
    out = ROOT/'mod/BrogueDoom/models/terrain'
    out.mkdir(parents=True, exist_ok=True)
    models = {}
    for name in ('wood', 'ice', 'stone', 'veil', 'cage', 'gate', 'fire', 'gas'):
        vertices, faces = [], []
        if name == 'wood':
            box(vertices,faces,-15,-3,-1,30,6,2)
            for x in (-12, 10): box(vertices,faces,x,-2,1,1,4,.3)
        elif name == 'ice':
            vertices = [(-9,-5,0),(8,-3,0),(1,10,0),(-6,-4,2),(5,-2,3),(1,7,2)]
            faces = [(1,3,2),(4,5,6),(1,2,5,4),(2,3,6,5),(3,1,4,6)]
        elif name == 'stone':
            vertices = [(-5,-4,0),(6,-3,0),(4,5,0),(-4,4,0),(-2,-2,7),(3,1,5)]
            faces = [(1,4,3,2),(1,2,6,5),(2,3,6),(3,4,5,6),(4,1,5)]
        elif name == 'veil': box(vertices,faces,-32,-32,0,64,64,224)
        elif name == 'fire':
            for i in range(7):
                x,y=(i*17)%39-19,(i*23)%39-19
                first=len(vertices)+1
                vertices.extend([(x-4,y-3,0),(x+4,y-3,0),(x+3,y+3,0),(x-3,y+3,0),(x+2,y,12+i*3)])
                faces.extend([(first,first+1,first+4),(first+1,first+2,first+4),(first+2,first+3,first+4),(first+3,first,first+4)])
        elif name == 'gas':
            from tools.gas_assets import cloud_geometry
            vertices, faces = cloud_geometry()
        else:
            for x in range(-28,29,8): box(vertices,faces,x,-2,0,2,4,96)
            for z in (0,44,92): box(vertices,faces,-30,-3,z,60,6,4)
            if name == 'cage':
                for y in range(-28,29,8):
                    for x in (-28,28): box(vertices,faces,x,y,0,2,2,64)
                box(vertices,faces,-28,-28,64,58,58,3)
        text = '# Original Project Broom terrain geometry, CC0-1.0\n'
        text += ''.join(f'v {x:.4f} {z:.4f} {-y:.4f}\n' for x,y,z in vertices)
        text += 'vt 0 0\nvt 1 0\nvt 1 1\nvt 0 1\n'
        text += ''.join('f '+' '.join(f'{v}/{i%4+1}' for i,v in enumerate(face))+'\n' for face in faces)
        (out/f'{name}.obj').write_text(text, newline='\n')
        models[name] = {'wood':'BRGBRIDGE', 'ice':'BRGICE', 'stone':'BRGROCK', 'veil':'BRGROCK', 'cage':'BRGSEARCH','gate':'BRGSEARCH','fire':'BRGTFLAM','gas':'BRGTCLOUD'}[name]
    frost = Image.new('RGB',(128,128))
    frost.putdata([(105+n,160+n,182+n) for y in range(128) for x in range(128)
                   for n in [((x*37+y*61+x*y*3)%37)-18]])
    draw = ImageDraw.Draw(frost)
    for i in range(17):
        x,y=(i*43)%128,(i*71)%128
        draw.line([(x,y),((x+13)%128,(y+9)%128),((x+27)%128,(y+4)%128)],fill=(196,226,232),width=1)
    frost.save(ROOT/'mod/BrogueDoom/graphics/BRGICE.png', optimize=False)
    for name in ('BRGTFLAM','BRGTCLOUD'):
        texture=Image.new('RGBA',(64,64))
        texture.putdata([(255,100+y*2,25,220) if name=='BRGTFLAM' else (220,230,220,50+((x*7+y*11)%70))
                         for y in range(64) for x in range(64)])
        if name == 'BRGTCLOUD':
            from tools.gas_assets import cloud_texture
            texture = cloud_texture()
        texture.save(ROOT/f'mod/BrogueDoom/graphics/{name}.png',optimize=False)
    defs = ''
    from tools.statue_models import generate as generate_statues
    from tools.torch_models import generate as generate_torches
    from tools.manacle_models import generate as generate_manacles
    from tools.bloodwort_models import generate as generate_bloodwort
    for name, (mesh, skin) in {**generate_statues(), **generate_torches(), **generate_manacles(), **generate_bloodwort()}.items():
        defs += f'Model BrogueTerrain{name}\n{{\n Path "models/terrain"\n Model 0 "{mesh}.obj"\n Skin 0 "graphics/{skin}.png"\n Scale 1 1 1\n FrameIndex BRGD A 0 0\n}}\n'
    models['ember'] = 'BRGTFLAM'
    for name, skin in models.items():
        mesh = 'stone' if name == 'ember' else name
        defs += f'Model BrogueTerrain{name.title()}\n{{\n Path "models/terrain"\n Model 0 "{mesh}.obj"\n Skin 0 "graphics/{skin}.png"\n Scale 1 1 1\n FrameIndex BRGD A 0 0\n}}\n'
    (out/'MODELDEF.txt').write_text(defs,newline='\n')

if __name__ == '__main__': generate()

"""Original CC0 bloodwort forms; deterministic, cell-local Z-up geometry."""
import math
from pathlib import Path
from PIL import Image
from tools.statue_models import rings

ROOT = Path(__file__).resolve().parents[1]


def geometry(kind):
    v, f = [], []
    if kind == 'stalk':
        rings(v, f, [(0,0,0,3,3), (2,1,17,2,2), (-2,0,35,1.6,1.6),
                     (1,-1,52,1,.9), (4,0,65,.3,.3)], 10)
        for i in range(6):
            a = i*2.4
            x,y = 18*math.cos(a),18*math.sin(a)
            z = 13+i*6
            rings(v,f,[(0,0,z,1.5,1.5),(x*.6,y*.6,z+7,.8,.8),
                       (x,y,z+15,.2,.2)],8)
    elif kind == 'pod':
        rings(v,f,[(0,0,0,2,2),(1,0,11,1.5,1.5)],10)
        # Fluted, pointed shell: separate from the tall, open stalk silhouette.
        rings(v,f,[(1,0,8,2,2),(0,0,13,9,8),(0,0,23,13,11),
                   (1,0,34,10,9),(2,0,43,2,.9),(2,0,45,.3,.3)],24,.10)
    elif kind == 'shell':
        v=[(-3,-2,0),(3,-2,0),(4,0,5),(2,2,11),(-2,2,11),(-4,0,5),
           (-2,-1,1),(2,-1,1),(3,0,5),(1,1,10),(-1,1,10),(-3,0,5)]
        f=[(1,2,3,6),(6,3,4,5),(7,12,9,8),(12,11,10,9)]
        for i in range(6):
            j=(i+1)%6
            f.append((i+1,i+7,j+7,j+1))
    else:
        # A bounded cloud of solid specks, tinted from copied Brogue gas color.
        for i in range(32):
            x,y,z=(i*17)%51-25,(i*29)%51-25,5+(i*13)%38
            # Keep specks inside the cell at every cosmetic yaw and drift pose.
            shrink=min(1,23/max(1,math.hypot(x,y)))
            x,y=x*shrink,y*shrink
            r=.55+(i%3)*.25
            rings(v,f,[(x,y,z,r,r),(x,y,z+1.5,r*.6,r*.6)],5)
        # Feathered cards share the ordinary gas silhouette; solid specks remain.
        from tools.gas_assets import cloud_geometry
        cloud_v, cloud_f = cloud_geometry()
        offset = len(v)
        v.extend(cloud_v)
        f.extend(tuple(i+offset for i in face) for face in cloud_f)
    return v,f


def generate():
    out=ROOT/'mod/BrogueDoom/models/terrain'
    out.mkdir(parents=True,exist_ok=True)
    result={}
    for kind,color,skin in [('stalk',(91,35,76),'BRGBWST'),('pod',(148,39,74),'BRGBWPD'),
                             ('shell',(124,31,55),'BRGBWSH'),('spores',(255,255,255),'BRGBWSP')]:
        v,f=geometry(kind)
        text='# Original Project Broom bloodwort, CC0-1.0\n'
        text+=''.join(f'v {x:.4f} {z:.4f} {-y:.4f}\n' for x,y,z in v)
        text+='vt 0 0\nvt 0.49 0\nvt 0.49 1\nvt 0 1\nvt 0.51 0\nvt 1 0\nvt 1 1\nvt 0.51 1\n'
        text+=''.join('f '+' '.join(f'{p}/{i+1+(4 if kind=="spores" and n>=len(f)-9 else 0)}' for i,p in enumerate(face))+'\n' for n,face in enumerate(f))
        mesh='bloodwort_'+kind
        (out/f'{mesh}.obj').write_text(text,newline='\n')
        im=Image.new('RGB',(64,64))
        im.putdata([tuple(max(0,min(255,c+int(12*math.sin(x*.4))+((x*7+y*11)%9)-4))
                          for c in color) for y in range(64) for x in range(64)])
        if kind=='spores':
            from tools.gas_assets import cloud_texture
            im=Image.new('RGBA',(256,128),(255,255,255,255))
            im.paste(cloud_texture(),(128,0))
        im.save(ROOT/f'mod/BrogueDoom/graphics/{skin}.png',optimize=False)
        result['Bloodwort'+kind.title()]=(mesh,skin)
    return result

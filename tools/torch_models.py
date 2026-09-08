"""Original CC0 wall bracket and layered flame, deterministic Z-up meshes."""
import math
from pathlib import Path
from PIL import Image
from tools.search_models.generate import box
from tools.statue_models import rings

ROOT = Path(__file__).resolve().parents[1]


def generate():
    out = ROOT/'mod/BrogueDoom/models/terrain'
    out.mkdir(parents=True, exist_ok=True)
    v, f, colors = [], [], []

    def part(color, build):
        first = len(f)
        build()
        colors.extend([color]*(len(f)-first))

    part((65,62,55), lambda: box(v,f,0,-4,44,2,8,19))
    part((89,80,63), lambda: box(v,f,1,-1.5,48,9,3,3))
    part((117,69,32), lambda: rings(v,f,[(8,0,46,1.8,1.8),(8,0,68,2.2,2.2)],12))
    for z in (51,63):
        part((78,75,64), lambda z=z: rings(v,f,[(8,0,z,2.6,2.6),(8,0,z+2,2.6,2.6)],12))
    part((84,73,56), lambda: rings(v,f,[(8,0,64,2.8,2.8),(8,0,68,4,4),(8,0,69,4,4)],12))
    for y in (-2.5,2.5):
        for z in (46,60):
            part((139,127,100), lambda y=y,z=z: box(v,f,2,y-.6,z, .8,1.2,1.2))
    # A per-face shaded atlas keeps the small ironwork readable in sector light.
    atlas=Image.new('RGB',(256,256))
    text='# Original Project Broom wall torch, CC0-1.0\n'
    text+=''.join(f'v {x:.4f} {z:.4f} {-y:.4f}\n' for x,y,z in v)
    for i,face in enumerate(f):
        x,y=(i%16)*16,(i//16)*16
        a,b,c=[v[j-1] for j in face[:3]]
        u=[b[k]-a[k] for k in range(3)]; w=[c[k]-a[k] for k in range(3)]
        n=(u[1]*w[2]-u[2]*w[1],u[2]*w[0]-u[0]*w[2],u[0]*w[1]-u[1]*w[0])
        length=math.sqrt(sum(t*t for t in n))
        shade=.72+.28*max(0,(n[0]*.6-n[1]*.3+n[2]*.74)/length)
        for py in range(16):
            for px in range(16):
                wood=colors[i]==(117,69,32)
                grain=(math.sin(px*2.3+i)*7 if wood else ((px*13+py*7+i)%7)-3)
                atlas.putpixel((x+px,y+py),tuple(max(0,min(255,int(t*shade+grain))) for t in colors[i]))
        for s,t in ((2,2),(14,2),(14,14),(2,14)):
            text+=f'vt {(x+s)/256:.6f} {1-(y+t)/256:.6f}\n'
    text+=''.join('f '+' '.join(f'{v}/{i*4+j+1}' for j,v in enumerate(face))+'\n' for i,face in enumerate(f))
    (out/'torch.obj').write_text(text,newline='\n')
    atlas.save(ROOT/'mod/BrogueDoom/graphics/BRGTORCH.png',optimize=False)
    # Four crossed, double-sided flame sheets; head is a separate owned actor.
    text='# Original Project Broom torch flame, CC0-1.0\n'
    for a in (0,math.pi/4,math.pi/2,3*math.pi/4):
        for r,z in ((-5,0),(5,0),(5,18),(-5,18)):
            text+=f'v {r*math.cos(a):.4f} {z} {-r*math.sin(a):.4f}\n'
    text+='vt 0 0\nvt 1 0\nvt 1 1\nvt 0 1\n'
    for i in range(4):
        corners=[f'{i*4+j+1}/{j+1}' for j in range(4)]
        text+='f '+' '.join(corners)+'\nf '+' '.join(reversed(corners))+'\n'
    (out/'torch_flame.obj').write_text(text,newline='\n')
    for name,purple in (('BRGTORFL',False),('BRGTHAFL',True)):
        im=Image.new('RGBA',(64,128))
        for y in range(128):
            t=1-y/127
            center=31.5+5*math.sin(t*7)*t
            width=25*(1-t)**.65*min(1,(t+.04)*9)
            for x in range(64):
                edge=max(0,min(1,(width-abs(x-center))/4))
                core=max(0,1-abs(x-center)/max(1,width))*(1-t)
                rgb=(int(153+102*core),int(55+170*core),255) if purple else (255,int(90+165*core),int(12+185*core))
                im.putpixel((x,y),(*rgb,int(220*edge)))
        im.save(ROOT/f'mod/BrogueDoom/graphics/{name}.png',optimize=False)
    return {'Torch':('torch','BRGTORCH'),'TorchFlame':('torch_flame','BRGTORFL'),
            'HauntedTorchFlame':('torch_flame','BRGTHAFL')}

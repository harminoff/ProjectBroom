"""Original CC0 iron manacles corresponding to Brogue's eight terrain symbols."""
import math
from pathlib import Path
from PIL import Image
from tools.search_models.generate import box

ROOT=Path(__file__).resolve().parents[1]

def ring(v,f,center,rx,rz,tube=.7,alternate=False):
    start=len(v)+1
    for i in range(16):
        a=i*math.tau/16
        for j in range(8):
            b=j*math.tau/8
            x=(rx+tube*math.cos(b))*math.cos(a)
            y=tube*math.sin(b)
            z=(rz+tube*math.cos(b))*math.sin(a)
            if alternate:x,y=y,x
            v.append((center[0]+x,center[1]+y,center[2]+z))
    for i in range(16):
        for j in range(8):
            f.append(tuple(start+ii*8+jj for ii,jj in ((i,j),((i+1)%16,j),((i+1)%16,(j+1)%8),(i,(j+1)%8))))

def generate():
    out=ROOT/'mod/BrogueDoom/models/terrain';out.mkdir(parents=True,exist_ok=True)
    models={}
    for name,height in [('Floor',0),('Ceiling',224),('CeilingDeep',352),('Wall',0)]:
        v,f=[],[]
        if name=='Wall':
            box(v,f,0,-5,34,2,10,12)
            for i in range(7):ring(v,f,(5,0,36-i*3.5),2,2.7,alternate=bool(i%2))
            ring(v,f,(5,0,11),4,4,1)
        elif height:
            box(v,f,-5,-5,height-2,10,10,2)
            for i,z in enumerate(range(44,height-2,4)):ring(v,f,(0,0,z),2,2.8,alternate=bool(i%2))
            ring(v,f,(0,0,38),4,4,1)
        else:
            box(v,f,-5,-5,0,10,10,2)
            for i in range(7):ring(v,f,(0,0,4+i*3.5),2,2.7,alternate=bool(i%2))
            ring(v,f,(0,0,31),4,4,1)
        text='# Original Project Broom iron manacles, CC0-1.0\n'
        text+=''.join(f'v {x:.4f} {z:.4f} {-y:.4f}\n' for x,y,z in v)
        text+='vt 0 0\nvt 1 0\nvt 1 1\nvt 0 1\n'
        text+=''.join('f '+' '.join(f'{n}/{i+1}' for i,n in enumerate(face))+'\n' for face in f)
        mesh='manacle_'+name.lower();(out/(mesh+'.obj')).write_text(text,newline='\n')
        models['Manacle'+name]=(mesh,'BRGIRON')
    im=Image.new('RGB',(64,64))
    im.putdata([(n,n+2,n+3) for y in range(64) for x in range(64) for n in [90+int(25*math.sin(x*math.pi/63))+((x*7+y*13)%13)-6]])
    im.save(ROOT/'mod/BrogueDoom/graphics/BRGIRON.png',optimize=False)
    return models

"""Original blue flame volumes and motion; no simulation or gameplay effects."""
import hashlib
import json
import math
import struct
import zlib
from . import iqm
from .rat import ROOT, Part, add, sub
from .skeletal import Rig, assemble, sample_clips

SKIN='graphics/BRGWISP.png'
# Each tongue is one continuous, closed tapered volume, not an organic limb.
# x/y offset, base, length, radius, curl direction, curl amount, atlas stripe.
TONGUES=[(0,0,17,34,6.1,.3,5.5,0),
 (5,1,19,25,3.5,1.1,6,1),(-4,-1,18,28,3.8,3.7,5,2),
 (0,5,19,22,3.7,2.1,5.5,3),(1,-5,18,26,3.8,5.0,5,4),
 (5,-4,22,18,2.2,5.8,5,5),(-5,4,23,18,2.1,2.8,4,6),
 (8,1,41,5.5,.8,.8,1,7),(-6,-4,46,4.5,.7,3.8,1,7)]
HEIGHTS=(16,22,28,34,40,46,54)
def center(spec,t):
    x,y,z,h,r,a,c,s=spec
    bend=c*t*t+3*math.sin(t*math.tau)*t
    spread=.45+.55*math.sin(math.pi*t)
    return (x*spread+math.cos(a)*bend+2.0*math.sin(t*math.tau+a)*t,
            y*spread+math.sin(a)*bend+1.6*math.sin(t*math.tau+a)*t,z+h*t)
SPECS=[('root',None,(0,0,0))]
for j,z in enumerate(HEIGHTS):
    for y in range(2):
        for x in range(2):SPECS.append((f'field_{j}_{y}_{x}','root',(-16+32*x,-16+32*y,z)))
RIG=Rig.from_world(SPECS);BONES,REST=RIG.bones,RIG.rest
CLIPS=[('idle',48,24,True),('drift',32,35,True),('flare',20,35,False),
       ('lash',22,35,False),('recoil',14,35,False),('extinguish',30,35,False)]

def geometry():
    parts=[]
    for k,s in enumerate(TONGUES):
        p=Part(f'blue_flame_tongue_{k}'); rings=32;segments=40
        for j in range(rings+1):
            t=j/rings;c=center(s,t)
            radius=s[4]*math.sin(math.pi*t)**.8*(1-.64*t)
            for i in range(segments+1):
                a=math.tau*i/segments
                r=radius*(1+.12*math.cos(3*a+5*t+k))
                p.vertices.append((c[0]+r*math.cos(a),c[1]+r*math.sin(a),c[2]))
                p.uv.append(((s[7]+.03+.94*i/segments)/8,.02+.96*t))
        for j in range(rings):
            for i in range(segments):
                a=j*(segments+1)+i;b=a+segments+1
                if j==0:p.faces.append((a,b+1,b))
                elif j==rings-1:p.faces.append((a,a+1,b))
                else:p.faces.append((a,a+1,b+1,b))
        p.flame_index=k;parts.append(p)
    return assemble(parts,weights)

def weights(part,p,uv):
    # Freudenthal tetrahedra reproduce each position exactly with <=4 weights.
    # Moving the cage inward therefore extinguishes volume without bone scaling.
    j=max(0,min(len(HEIGHTS)-2,next((i for i in range(len(HEIGHTS)-1) if p[2]<=HEIGHTS[i+1]),len(HEIGHTS)-2)))
    f=[(p[0]+16)/32,(p[1]+16)/32,(p[2]-HEIGHTS[j])/(HEIGHTS[j+1]-HEIGHTS[j])]
    order=sorted(range(3),key=lambda a:f[a],reverse=True)
    cells=[(0,0,0)];corner=[0,0,0]
    for a in order:corner=corner.copy();corner[a]=1;cells.append(tuple(corner))
    amounts=[1-f[order[0]],f[order[0]]-f[order[1]],f[order[1]]-f[order[2]],f[order[2]]]
    return [(1+(j+z)*4+y*2+x,w) for (x,y,z),w in zip(cells,amounts) if w>1e-12]

def pose(name,t):
    phase=math.tau*t;pulse=math.sin(math.pi*t)**2;rows=[]
    for b,(n,parent,loc) in enumerate(BONES):
        delta=(0,0,0)
        if b:
            k=(b-1)%4;u=(loc[2]-16)/38
            flicker=math.sin(phase*2-u*4)-math.sin(-u*4)
            if name in ('idle','drift'):
                strength=(1 if name=='idle' else 1.7)
                radial=.05*math.sin(phase*2-u*3)
                delta=(strength*(1.3*math.sin(phase)+u*2.3*flicker)+loc[0]*radial,
                       strength*u*1.5*math.sin(phase*2-u*4)+loc[1]*radial,1.3*math.sin(phase)+u*1.2*flicker)
            elif name in ('flare','lash'):
                delta=(pulse*(4+u*(5 if name=='lash' else 1)),
                       pulse*(math.sin(k)*2+(3*u if name=='lash' else 0)),pulse*u*3)
            elif name=='recoil':delta=(-pulse*(2+u*4),pulse*math.sin(k),-pulse*u*3)
            elif name=='extinguish':
                f=max(0,min(1,(t-.08)/.83));f=f*f*(3-2*f)
                destination=(loc[0]*.0001,loc[1]*.0001,25+(loc[2]-25)*.0001)
                delta=tuple((destination[a]-loc[a])*f for a in range(3))
        rows.append((*add(loc,delta),0,0,0,1,1,1,1))
    return rows

def matrices(frame):return RIG.matrices(frame)
def deform(v,w,frame):return RIG.deform(v,w,frame)
def animation_data(v,w):return sample_clips(RIG,CLIPS,pose,v,w)

def texture_bytes():
    size=1024;pixels=bytearray()
    for y in range(size):
        pixels.append(0);v=1-y/(size-1)
        for x in range(size):
            band=x*8//size;u=(x*8/size)%1
            streak=(.5+.5*math.sin(u*math.tau*3+v*13+band))**5
            heart=math.exp(-((v-.3)/.28)**2)
            centerlight=(.5+.5*math.cos((u-.5)*math.tau))**2
            hot=min(1,heart*(.40+.6*centerlight)+.18*streak)
            rgb=(16+175*hot,50+188*hot,190+65*hot)
            pixels.extend(round(min(255,c)) for c in rgb)
    def chunk(k,d):return struct.pack('>I',len(d))+k+d+struct.pack('>I',zlib.crc32(k+d)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',size,size,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(pixels,9))+chunk(b'IEND',b'')

def build():
    skin=texture_bytes();(ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts,v,n,uv,tris,w=geometry();clips,bounds=animation_data(v,w)
    data=iqm.encode(v,n,uv,tris,w,BONES,clips,bounds,mesh_label='Project_Broom_will_o_the_wisp',material_path=SKIN)
    path=ROOT/'mod/BrogueDoom/models/monsters/23_will_o_the_wisp.iqm';path.write_bytes(data)
    manifest=dict(schemaVersion=1,workId='BRG-M23',format='IQM v2',runtimeModel=path.relative_to(ROOT).as_posix(),
      sha256=hashlib.sha256(data).hexdigest(),skin=SKIN,skinSha256=hashlib.sha256(skin).hexdigest(),
      dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],
      parts=len(parts),vertices=len(v),triangles=len(tris),boneCount=len(BONES),bones=[dict(name=n,parent=p,local=v) for n,p,v in BONES],
      clips=[{k:v for k,v in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],
      poseBounds=bounds,authoringSource='assets/monsters/wisp/wisp-animated.blend')
    out=ROOT/'assets/monsters/wisp';out.mkdir(exist_ok=True);(out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest

if __name__=='__main__':print(build()['sha256'])


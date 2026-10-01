"""Connected sculpted pink gel. Original art; Brogue owns causticity and cloning.

A latitude/longitude skin has broad folds and a spreading contact skirt. Four
influences blend adjacent height/angle anchors; translating those anchors gives
viscous deformation without unsupported bone scale or disconnected body balls.
"""
import hashlib
import json
import math
from . import iqm, pink_jelly_materials as materials
from .rat import ROOT, add, sub, ellipsoid
from .skeletal import Rig, assemble, sample_clips

SKIN=materials.SKIN
LEVELS=(.12,10,21,30.92)
SEGMENTS=96
RINGS=48
SPECS=[('root',None,(0,0,0))]
for level,z in enumerate(LEVELS[1:3],1):
    radius=(20,20,14,3)[level]
    for side in range(8):
        a=math.tau*side/8
        SPECS.append((f'gel_{level}_{side}','root',(radius*math.cos(a),radius*math.sin(a),z)))
SPECS.append(('crown','root',(-3,1.7,LEVELS[-1])))
RIG=Rig.from_world(SPECS)
BONES,REST=RIG.bones,RIG.rest
CLIPS=[('idle',40,20,True),('flow',28,35,True),('smear',20,35,False),
       ('drench',24,35,False),('recoil',14,35,False),('collapse',30,35,False)]


def surface(theta,v):
    theta%=math.tau
    radial=math.sqrt(max(0,1-(2*v-1)**2))
    skirt=math.exp(-((v-.25)/.19)**2)
    shoulder=math.exp(-((v-.67)/.25)**2)
    # Large nonuniform lobes merge into one surface; relief fades at both poles.
    lobes=1+skirt*(.12*math.cos(theta*5+.6)+.045*math.sin(theta*3))
    lobes+=shoulder*(.06*math.sin(theta*3+v*8)+.04*math.cos(theta*7-v*11))
    folds=.033*math.cos(theta*11+v*15)*math.sin(math.pi*v)**2
    front=math.exp((math.cos(theta)-1)*5)*skirt*3.7
    x=23*radial*(lobes+folds)*math.cos(theta)+front-3*v*v
    y=21*radial*(lobes+folds)*math.sin(theta)+1.7*v*v
    # A rounded high mass over a flattened skirt. Ridges and blisters are
    # sculpted directly into the closed skin; none can float away in animation.
    relief=(1.3*math.sin(theta*4+v*9)+.7*math.sin(theta*9-v*13))*shoulder*radial
    blisters=.8*max(0,math.sin(theta*13+v*41)*math.cos(theta*9-v*29))**3*radial
    z=.12+30.8*v*v+relief+blisters
    return x,y,z


def weights(part,p,uv):
    # Skin parameter U fixes angle even where the crown leans asymmetrically.
    angle=(uv[0]%1)*8
    side=int(angle)%8;fraction=angle-int(angle)
    z=max(LEVELS[0],min(LEVELS[-1],p[2]))
    lower=next((i for i in range(3) if z<=LEVELS[i+1]),2)
    high=(z-LEVELS[lower])/(LEVELS[lower+1]-LEVELS[lower])
    values={}
    for ring,amount in ((lower,1-high),(lower+1,high)):
        for j,t in ((side,1-fraction),((side+1)%8,fraction)):
            bone=0 if ring==0 else 17 if ring==3 else 1+(ring-1)*8+j
            if amount*t>1e-12:values[bone]=values.get(bone,0)+amount*t
    return list(values.items())


def geometry():
    body=ellipsoid('pink_jelly_connected_gel',(0,0,0),(1,1,1),segments=SEGMENTS,rings=RINGS)
    for i in range(len(body.vertices)):
        if i==0: u,v=.5,0
        elif i==len(body.vertices)-1:u,v=.5,1
        else:
            ring=(i-1)//(SEGMENTS+1)+1
            u=((i-1)%(SEGMENTS+1))/SEGMENTS
            v=(1-math.cos(math.pi*ring/RINGS))/2
        body.vertices[i]=surface(u*math.tau,v)
        body.uv[i]=(u,v)
    return assemble([body],weights)


def smooth(t):
    t=max(0,min(1,t));return t*t*(3-2*t)


def pose(name,t):
    phase=math.tau*t
    shifts=[(0,0,0) for _ in BONES]
    action=math.sin(math.pi*t)**2
    for level,z in enumerate(LEVELS[1:],1):
        height=(z-.12)/30.88
        for side in range(8):
            if level==3 and side>0:continue
            a=math.tau*side/8
            dx=dy=dz=0
            if name in ('idle','flow'):
                wave=math.sin(phase-a-height*2.5)
                spread=(.38 if name=='idle' else 1.05)*wave
                dx=math.cos(a)*spread
                dy=math.sin(a)*spread
                dz=(.3 if name=='idle' else .95)*height*math.sin(phase-height*3+a*.0)
                if name=='flow':
                    dx+=1.4*height*math.sin(phase-height*2)
                    dy+=.45*height*math.sin(phase+.7)
            elif name=='smear':
                front=max(0,math.cos(a))
                dx=action*(5.3*height+3.1*front*(1-height))
                dy=action*math.sin(a)*(.9-height)
                dz=-action*height*5.5
            elif name=='drench':
                # Broad surge rises from the middle and folds forward. No
                # detached droplets or projectile collision are produced.
                dx=action*(6*height+1.4*math.cos(a))
                dy=action*math.sin(a)*2
                dz=action*(2*math.sin(height*math.pi)-4*height)
            elif name=='recoil':
                dx=-action*(3.5*height+max(0,math.cos(a))*2)
                dy=action*math.sin(a)*1.1
                dz=-action*height*3.8
            elif name=='collapse':
                settle=smooth((t-.08)/.82)
                dx=math.cos(a)*(1.2+height)*settle
                dy=math.sin(a)*(1.2+height)*settle
                dz=-(z-.12)*.88*settle
            if level==3:
                # A shared pole prevents the final latitude rings folding over
                # when a directional recoil pushes their neighboring anchors.
                if name in ('idle','flow'):
                    dx=1.4*math.sin(phase-2) if name=='flow' else 0
                    dy=.45*math.sin(phase+.7) if name=='flow' else 0
                elif name=='smear':dx,dy=5.3*action,0
                elif name=='drench':dx,dy=6*action,0
                elif name=='recoil':dx,dy=-3.5*action,0
                elif name=='collapse':dx,dy=0,0
            shifts[17 if level==3 else 1+(level-1)*8+side]=(dx,dy,dz)
    return [(*add(local,shifts[i]),0,0,0,1,1,1,1) for i,(n,p,local) in enumerate(BONES)]


def matrices(frame):return RIG.matrices(frame)
def deform(v,w,frame):return RIG.deform(v,w,frame)
def animation_data(v,w):return sample_clips(RIG,CLIPS,pose,v,w)


def build():
    maps={SKIN:materials.texture_bytes(),**materials.surface_maps()}
    for path,data in maps.items():(ROOT/'mod/BrogueDoom'/path).write_bytes(data)
    parts,v,n,uv,t,w=geometry();clips,bounds=animation_data(v,w)
    data=iqm.encode(v,n,uv,t,w,BONES,clips,bounds,mesh_label='Project_Broom_pink_jelly',material_path=SKIN)
    path=ROOT/'mod/BrogueDoom/models/monsters/12_pink_jelly.iqm';path.write_bytes(data)
    manifest=dict(schemaVersion=1,workId='BRG-M12',format='IQM v2',
        runtimeModel=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(data).hexdigest(),
        skin=SKIN,skinSha256=hashlib.sha256(maps[SKIN]).hexdigest(),
        materialMaps={p:hashlib.sha256(b).hexdigest() for p,b in maps.items()},
        dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],
        parts=len(parts),vertices=len(v),triangles=len(t),boneCount=len(BONES),
        bones=[dict(name=n,parent=p,local=v) for n,p,v in BONES],
        clips=[{k:v for k,v in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],
        poseBounds=bounds,authoringSource='assets/monsters/pink_jelly/pink-jelly-animated.blend')
    out=ROOT/'assets/monsters/pink_jelly';out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__':
    result=build();print({k:result[k] for k in ('sha256','dimensions','vertices','triangles')})

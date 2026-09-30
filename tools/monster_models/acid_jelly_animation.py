"""Connected lobed acidic jelly. Original art; Brogue owns corrosion and cloning.

One closed latitude/longitude skin (see `acid_jelly_shape`) is weighted to three
rings of eight translation anchors plus a crown. Height blending follows the
monotone base profile, so the underside stays on the root and the floor while
crown lobes, flanks and rim move as a viscous mass. There is no unsupported
bone scale, no detached droplet and no independently spawned clone.
"""
import hashlib
import json
import math
from . import iqm, acid_jelly_materials as materials, acid_jelly_shape as shape
from .rat import ROOT, add, sub, ellipsoid
from .skeletal import Rig, assemble, sample_clips

SKIN=materials.SKIN
LEVELS=(shape.FLOOR,3.8,9.0,13.5,shape.FLOOR+shape.ZC+shape.HT)
LEVEL_PHI=(None,-.30,.15,.50,None)
SEGMENTS=144
RINGS=72
SPECS=[('root',None,(0,0,0))]
# The lobe ring places anchors under each crown lobe and in each valley, so
# lobe relief can deflate without per-vertex scaling.
_L=[a for a,*_ in shape.LOBES]
TOP=sorted(_L+[round(a+(b-a)*f,6) for a,b in zip(_L,_L[1:]+[_L[0]+math.tau]) for f in (1/3,2/3)])
TOP=[round(a%math.tau,6) for a in TOP];TOP.sort()
COUNT=(1,8,8,len(TOP),1)


def azimuth(level,side):
    return TOP[side%len(TOP)] if level==3 else math.tau*side/8


for level in (1,2,3):
    radius=shape.base(LEVEL_PHI[level])[0]*.82
    for side in range(COUNT[level]):
        a=azimuth(level,side)
        SPECS.append((f'gel_{level}_{side}','root',(round(radius*math.cos(a),6),
                      round(radius*math.sin(a)*shape.Y_SCALE,6),LEVELS[level])))
SPECS.append(('crown','root',(0,0,LEVELS[-1])))
RIG=Rig.from_world(SPECS)
BONES,REST=RIG.bones,RIG.rest
CROWN=len(BONES)-1
CLIPS=[('idle',48,20,True),('creep',32,35,True),('burn',26,35,False),
       ('engulf',32,35,False),('recoil',16,35,False),('dissolve',40,35,False)]
LOBE_ANGLES=[a for a,*_ in shape.LOBES]


def bone(level,side):
    return 0 if level==0 else CROWN if level==4 else 1+(level-1)*8+side%COUNT[level]


def bracket(level,theta):
    """Neighbouring anchors and blend fraction for one azimuth."""
    theta%=math.tau
    if level!=3:
        angle=theta/math.tau*8;side=int(angle)%8
        return side,side+1,angle-int(angle)
    n=len(TOP);rel=(theta-TOP[0])%math.tau
    offsets=[t-TOP[0] for t in TOP]+[math.tau]
    i=max(k for k in range(n) if offsets[k]<=rel)
    return i,i+1,(rel-offsets[i])/(offsets[i+1]-offsets[i])


def quantize(values):
    """Deterministic 1e-6 weights; the last influence takes the remainder."""
    items=sorted((b,w) for b,w in values.items() if w>1e-7)
    if len(items)==1:return [(items[0][0],1)]
    total=sum(w for _,w in items)
    out=[(b,round(w/total,6)) for b,w in items[:-1]]
    out.append((items[-1][0],round(1-sum(w for _,w in out),6)))
    return out


def weights(part,p,uv):
    theta=math.tau*(uv[0]%1)
    z=max(LEVELS[0],min(LEVELS[-1],shape.base_height(uv[1])))
    lower=next((i for i in range(4) if z<=LEVELS[i+1]),3)
    high=(z-LEVELS[lower])/(LEVELS[lower+1]-LEVELS[lower])
    values={}
    for ring,amount in ((lower,1-high),(lower+1,high)):
        side,other,fraction=bracket(ring,theta)
        for j,t in ((side,1-fraction),(other,fraction)):
            b=bone(ring,j)
            if amount*t>1e-12:values[b]=values.get(b,0)+amount*t
    return quantize(values)


def geometry():
    body=ellipsoid('acid_jelly_connected_gel',(0,0,0),(1,1,1),segments=SEGMENTS,rings=RINGS)
    for i in range(len(body.vertices)):
        if i==0:u,v=.5,0
        elif i==len(body.vertices)-1:u,v=.5,1
        else:
            ring=(i-1)//(SEGMENTS+1)+1
            u=((i-1)%(SEGMENTS+1))/SEGMENTS
            v=ring/RINGS
        body.vertices[i]=tuple(round(c,6) for c in shape.surface(u*math.tau,v))
        body.uv[i]=(u,v)
    return assemble([body],weights)


_SETTLE={}
PUDDLE=.06        # spent relief kept as deflated folds
SPREAD=1.03       # the spent gel spreads over the floor
SLUMP=(.5,-.5)   # it slumps slightly to one side
BAND=.93           # steepest allowed sink of a ring below the ring beneath


def puddle_target(p):
    """Near-affine spent pose: widened, flattened, slumped; never inverted."""
    lean=min(1,p[2]/20)
    x,y=p[0]-shape.X_SHIFT,p[1]-shape.Y_SHIFT
    theta=math.atan2(y,x)
    spread=SPREAD+.07*math.sin(3*theta+1.0)+.045*math.sin(5*theta+2.3)
    return (spread*x+shape.X_SHIFT+SLUMP[0]*lean,
            spread*y+shape.Y_SHIFT+SLUMP[1]*lean,.9+PUDDLE*p[2])


def settle_shifts():
    """Least-squares anchor translations that best reproduce the spent pose.

    Translation anchors cannot scale relief inside their region, so every
    non-root anchor's final offset is solved once from the rest vertices.
    Fitting all three axes towards one near-affine map keeps triangles
    oriented while the mass flattens.
    """
    if not _SETTLE:
        _,v,_,uv,_,w=geometry()
        n=len(BONES);A=[[0.]*n for _ in range(n)];B=[[0.]*3 for _ in range(n)]
        for p,influences in zip(v,w):
            target=puddle_target(p)
            row=[(b,x) for b,x in influences if b]
            for b,x in row:
                for k in range(3):B[b][k]+=x*(target[k]-p[k])
                for c,y in row:A[b][c]+=x*y
        idx=list(range(1,n))
        M=[[A[i][j]+(1e-3 if i==j else 0) for j in idx]+B[i] for i in idx]
        size=len(idx)
        for c in range(size):
            pivot=max(range(c,size),key=lambda r:abs(M[r][c]));M[c],M[pivot]=M[pivot],M[c]
            for r in range(size):
                if r!=c:
                    f=M[r][c]/M[c][c]
                    M[r]=[x-f*y for x,y in zip(M[r],M[c])]
        solved={b:[M[k][size+a]/M[k][k] for a in range(3)] for k,b in enumerate(idx)}
        # Steep walls stay ordered: an upper ring may not sink more than 80%
        # of the band height below the ring beneath it (checked per azimuth).
        for level in (2,3):
            band=BAND*(LEVELS[level]-LEVELS[level-1])
            for side in range(COUNT[level]):
                i,j,f=bracket(level-1,azimuth(level,side))
                below=(1-f)*solved[bone(level-1,i)][2]+f*solved[bone(level-1,j)][2]
                shift=solved[bone(level,side)]
                shift[2]=max(shift[2],below-band)
        _SETTLE.update({b:tuple(round(x,6) for x in shift) for b,shift in solved.items()})
    return _SETTLE


def smooth(t):
    t=max(0,min(1,t));return t*t*(3-2*t)


def bell(t):
    t=max(0,min(1,t));return math.sin(math.pi*t)**2


def lobe_near(a):
    """How strongly an anchor azimuth sits under each crown lobe."""
    return [math.exp(-(shape.wrap(a-c)/.62)**2) for c in LOBE_ANGLES]


def pose(name,t):
    phase=math.tau*t
    shifts=[(0,0,0) for _ in BONES]
    settles=settle_shifts() if name=='dissolve' else None
    for level in (1,2,3,4):
        h=(LEVELS[level]-LEVELS[0])/(LEVELS[-1]-LEVELS[0])
        for side in range(COUNT[level]):
            a=azimuth(level,side)
            ca,sa=math.cos(a),math.sin(a)
            near=lobe_near(a) if level==3 else [0,0,0]
            front=max(0,ca)
            dx=dy=dz=0
            if name=='idle':
                # Lobes swell in sequence; the whole mass breathes and wobbles.
                swell=sum(n*math.sin(phase-i*math.tau/3) for i,n in enumerate(near))
                breathe=math.sin(phase-h*2.2)
                wob=math.sin(2*phase+a)*h
                dx=ca*(.9*breathe*(1-h*.4)+.8*swell)+.5*wob*math.cos(phase)
                dy=sa*(.9*breathe*(1-h*.4)+.8*swell)
                dz=1.1*h*math.sin(phase+.5)+1.8*swell
                if level==1:dz=max(-.3,.25*math.sin(phase-a))
                if level==4:dx,dy,dz=.6*math.sin(phase),.45*math.cos(phase),1.2*math.sin(phase+.5)
            elif name=='creep':
                # A rear-to-front peristaltic wave; the skirt reaches ahead.
                wave=math.sin(phase-h*2.4)
                dx=2.2*h*wave+1.2*front*math.sin(phase+.9)*(level==1)
                dy=.7*h*math.sin(phase+.7)+ca*sa*.6*math.sin(phase)*(level==1)
                dz=1.3*h*math.sin(2*phase-h*3)+1.2*sum(n*math.sin(phase-i*2.1) for i,n in enumerate(near))
                if level==1:dz=max(-.3,.4*math.sin(2*phase-a))
                if level==4:dx,dy,dz=2.2*math.sin(phase-2.4),.7*math.sin(phase+.7),1.3*math.sin(2*phase-3)
            elif name=='burn':
                # Rear back and rise, then slap the front lobe down at the target.
                gather=bell(t/.40)
                surge=bell((t-.20)/.64)
                dx=-gather*(3.8*h+.8)+surge*(5.4*h+2.4*front*(1-h))
                dy=-gather*sa*1.6*(1-h)+surge*sa*(3.0-1.8*h)
                dz=gather*(5.5*h)-surge*h*5.2
                if level==3:
                    lift=near[0]
                    dx+=surge*2.6*lift-gather*1.2*lift;dz+=gather*3.0*lift-surge*3.2*lift
                if level==1:
                    dx+=surge*1.8*front;dz=max(-.5,dz)
                if level==4:dx,dy,dz=-gather*4.2+surge*5.8,0,gather*6.0-surge*5.6
            elif name=='engulf':
                # Rise tall and narrow, then lunge down and spread wide.
                rise=bell(t/.40)
                slam=bell((t-.22)/.60)
                wobble=math.sin(math.tau*1.5*max(0,t-.5)/.5)*(1-smooth((t-.5)/.5))*smooth((t-.5)/.15)
                dx=-rise*ca*2.6*(1-h)+slam*(ca*3.9*(1.1-h)+3.4*h)
                dy=-rise*sa*2.6*(1-h)+slam*sa*4.2*(1.1-h)
                dz=rise*7.0*h-slam*5.8*h+wobble*1.6*h
                if level==1:dz=max(-.5,dz)
                if level==4:dx,dy,dz=slam*3.6,0,rise*7.6-slam*6.0+wobble*1.8
            elif name=='recoil':
                # Knocked back and squashed, then a clear side-to-side jiggle.
                push=bell(t)
                wobble=math.sin(math.tau*1.5*t)*(1-t)**2
                sway=math.sin(math.tau*2*t)*(1-t)**2
                dx=-push*(3.6*h+1.6*front*(1-h))+wobble*1.8*h
                dy=push*sa*1.2*(1-h)+sway*3.0*h
                dz=-push*h*4.0+wobble*1.6*h
                if level==1:dz=max(-.3,dz)
                if level==4:dx,dy,dz=-push*3.8+wobble*2.0,sway*3.2,-push*4.2+wobble*1.8
            elif name=='dissolve':
                # Lobes deflate first, then the spent mass spreads and settles.
                sag=smooth(t/.45)
                settle=smooth((t-.10)/.80)
                lead=.35*sag+.65*settle if level>=3 else settle
                dx,dy,dz=(c*lead for c in settles[bone(level,side)])
            shifts[bone(level,side)]=(dx,dy,dz)
    return [(*add(local,shifts[i]),0,0,0,1,1,1,1) for i,(n,p,local) in enumerate(BONES)]


def matrices(frame):return RIG.matrices(frame)
def deform(v,w,frame):return RIG.deform(v,w,frame)
def animation_data(v,w):return sample_clips(RIG,CLIPS,pose,v,w)


def build():
    maps={SKIN:materials.texture_bytes(),**materials.surface_maps()}
    for path,data in maps.items():(ROOT/'mod/BrogueDoom'/path).write_bytes(data)
    parts,v,n,uv,t,w=geometry();clips,bounds=animation_data(v,w)
    data=iqm.encode(v,n,uv,t,w,BONES,clips,bounds,mesh_label='Project_Broom_acid_jelly',material_path=SKIN)
    path=ROOT/'mod/BrogueDoom/models/monsters/34_acid_jelly.iqm';path.write_bytes(data)
    manifest=dict(schemaVersion=1,workId='BRG-M34',format='IQM v2',
        runtimeModel=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(data).hexdigest(),
        skin=SKIN,skinSha256=hashlib.sha256(maps[SKIN]).hexdigest(),
        materialMaps={p:hashlib.sha256(b).hexdigest() for p,b in maps.items()},
        dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],
        parts=len(parts),vertices=len(v),triangles=len(t),boneCount=len(BONES),
        bones=[dict(name=n,parent=p,local=v) for n,p,v in BONES],
        clips=[{k:v for k,v in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],
        poseBounds=bounds,authoringSource='assets/monsters/acid_jelly/acid-jelly-animated.blend')
    out=ROOT/'assets/monsters/acid_jelly';out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__':
    result=build();print({k:result[k] for k in ('sha256','dimensions','vertices','triangles')})

"""Sagging tar-heap black jelly. Original art; Brogue owns its caustic attacks and cloning.

The body is one analytic latitude/longitude surface (U azimuth with the seam at
the back, V from the underside pole to the crest pole) that is fused by the
shared connected-skin bake. Unlike the pink jelly's single dome and the acidic
jelly's three low lobes, this jelly is a tiered heap of ink: a thin glossy
spill-pool apron with a forward feeding tongue, an undercut waist, a heavy
sagging belly with hanging drapes that end in teardrop drips, tar blisters,
and a crest that leans back while a melted slump lobe folds over one side.

Translation-only anchors (four rings of eight plus a crest pole) deform the
mass; the underside stays on the root and the floor. Every size here is an art
choice, not a Brogue fact. There is no gameplay, AI, collision or RNG.
"""
import functools
import hashlib
import json
import math
from . import iqm, connected_skin
from .rat import ROOT, Part, add, sub, cross
from .skeletal import Rig, assemble, sample_clips

TAU=math.tau
SKIN='graphics/BRGBKJLY.png'
NORMAL='graphics/BRGBKJLY_N.png'
SPECULAR='graphics/BRGBKJLY_S.png'
SHADER='shaders/black-jelly-sheen.fp'

# ---------------------------------------------------------------- sculpt
FLOOR=.12
X_SHIFT=-1.3
Y_SHIFT=.4
Y_SCALE=.95
# Base profile knots along V: (v, radius, height). Underside, a rounded spill
# lip, a concave pour fillet rising from the pool, steep flowing flanks and a
# low lopsided crest.
PROFILE=((0,0,FLOOR),(.08,15.0,FLOOR),(.13,23.4,.28),(.16,24.4,.95),(.19,23.4,1.65),
         (.24,20.8,2.5),(.30,19.6,4.0),(.37,20.0,6.4),(.45,19.6,9.4),(.53,18.2,12.7),
         (.61,16.6,15.9),(.70,14.2,19.0),(.79,10.9,21.6),(.88,6.8,23.5),(.95,3.1,24.5),(1,0,24.8))
# Melting curtain folds: azimuth, angular width, relief, V where the fold
# starts high on the heap, V of the heavy pile it drops onto the pool.
FOLDS=((0.25,.19,3.2,.72,.300),(1.02,.14,2.5,.60,.285),(1.88,.20,3.5,.74,.310),
       (2.72,.15,2.6,.64,.290),(3.45,.19,3.3,.76,.305),(4.22,.14,2.4,.58,.285),
       (4.95,.18,3.1,.70,.300),(5.62,.13,2.3,.62,.290))
# Tar blisters: azimuth, V, radius in V units, height.
BLISTERS=((0.62,.80,.036,1.3),(2.75,.66,.040,1.4),(4.05,.84,.034,1.1),(5.35,.62,.038,1.3),(3.55,.55,.030,1.0))
# Spill-pool drip tongues and retreats: azimuth, amount, angular width.
SPILL_DRIPS=((0.75,.09,.10),(2.30,.10,.14),(2.85,.07,.08),(4.20,.08,.11),(4.65,.07,.07),(5.60,.09,.11))
SPILL_RETREATS=((1.12,.14,.24),(3.55,.13,.28),(5.05,.11,.20))
# A melted slump lobe folds over the camera-facing flank below the leaning
# crest; a smaller second heap sits back-right.
SLUMP=(1.35,.60,2.4,.10,.70)   # azimuth, V, bulge, V reach, angular reach
HUMP=(4.30,.78,5.4,.085,.70)
LEAN=(-2.2,-1.6)                  # crest leans back and away from the slump


def wrap(a):return (a+math.pi)%TAU-math.pi
def smooth(t):t=max(0.,min(1.,t));return t*t*(3-2*t)
def gauss(x):return math.exp(-x*x)
def theta_of(u):return (TAU*u+math.pi)%TAU   # UV seam at the back (-X)


def profile(v):
    """Monotone-height Hermite interpolation of the base profile."""
    v=max(0.,min(1.,v));k=PROFILE
    i=max(j for j in range(len(k)-1) if k[j][0]<=v) if v<1 else len(k)-2
    (v0,r0,z0),(v1,r1,z1)=k[i],k[i+1];h=v1-v0;t=(v-v0)/h
    def slope(j,a):
        lo,hi=k[max(0,j-1)],k[min(len(k)-1,j+1)]
        return (hi[a]-lo[a])/(hi[0]-lo[0])
    out=[]
    for a,(p0,p1) in ((1,(r0,r1)),(2,(z0,z1))):
        m0,m1=slope(i,a)*h,slope(i+1,a)*h
        if a==2:  # heights never overshoot: the floor stays flat
            d=p1-p0;m0=max(0,min(m0,3*d));m1=max(0,min(m1,3*d))
        t2,t3=t*t,t*t*t
        out.append((2*t3-3*t2+1)*p0+(t3-2*t2+t)*m0+(-2*t3+3*t2)*p1+(t3-t2)*m1)
    return max(0.,out[0]),max(FLOOR,out[1])


def cap(theta,v,a,e,reach,angular):
    return gauss(wrap(theta-a)/angular)*gauss((v-e)/reach)


def fields(theta,v):
    """Named relief fields at one surface parameter; reused by the paint."""
    theta%=TAU
    r0,z0=profile(v)
    apron=1-smooth((v-.20)/.10)
    # An irregular ink spill: broad lobes, narrow drip tongues and places
    # where the pool retreats almost to the heap, never an even disc.
    spill=(.05*math.sin(3*theta+.7)+.04*math.sin(5*theta+2.1)+.03*math.sin(7*theta+.3)
           +.07*gauss(wrap(theta)/.26))
    for a,amount,width in SPILL_DRIPS:spill+=amount*gauss(wrap(theta-a)/width)
    for a,amount,width in SPILL_RETREATS:spill-=amount*gauss(wrap(theta-a)/width)
    thick=max(.5,min(1.65,1+.35*math.sin(4*theta+1.3)+.22*math.sin(7*theta+.4)+2.2*max(0.,spill-.06)))
    fold=pile=groove=0.
    for a,w,amount,top,end in FOLDS:
        d=wrap(theta-a)
        # The flow meanders a little as it runs down the heap.
        d-=.05*math.sin(v*23+a*2)
        along=smooth((top-v)/.14)*smooth((v-end+.01)/.035)
        taper=.55+.45*smooth((top-v)/.35)
        fold+=amount*taper*gauss(d/w)*along
        pile+=1.45*amount*gauss(d/(1.5*w))*gauss((v-end)/.028)
        groove+=gauss((abs(d)-1.9*w)/(.7*w))*along
    scale=max(.3,r0/17)
    blister=0.
    for a,e,size,height in BLISTERS:
        d=math.hypot(wrap(theta-a)*scale*.6,v-e)/size
        if d<1:blister+=height*(1-d*d)**1.5
    slump=SLUMP[2]*cap(theta,v,SLUMP[0],SLUMP[1],SLUMP[3],SLUMP[4])
    crease=.35*gauss(wrap(theta-SLUMP[0])/(SLUMP[4]*1.05))*gauss((v-SLUMP[1]-.078)/.024)
    hump=HUMP[2]*cap(theta,v,HUMP[0],HUMP[1],HUMP[3],HUMP[4])
    lip=2.4*gauss(wrap(theta)/.34)*gauss((v-.27)/.04)
    lean=smooth((v-.45)/.55)**1.5
    return dict(r0=r0,z0=z0,apron=apron,spill=spill,thick=thick,fold=fold,pile=pile,groove=groove,
                blister=blister,slump=slump,crease=crease,hump=hump,lip=lip,lean=lean)


def surface(theta,v,info=None):
    f=fields(theta,v)
    r=f['r0']*(1+f['spill']*f['apron'])
    body=1-f['apron']
    up=smooth((v-.62)/.3)
    r+=body*(f['fold']+f['pile']+f['lip']+f['slump']-f['crease'])+f['blister']*(1-.7*up)+f['hump']*(1-.6*up)
    # Piles and the slump lobe hang: they sag down as they bulge; the second
    # heap and blisters rise near the crest.
    # The pool's thickness varies: beaded lobes swell, thin sheets run out.
    z=FLOOR+(f['z0']-FLOOR)*(1+(f['thick']-1)*f['apron'])
    z+=-.55*f['pile']-.8*f['slump']+f['blister']*up*.9+f['hump']*up*.8
    z=max(FLOOR,z) if v>.08 else FLOOR
    r=max(0.,r)
    x=r*math.cos(theta)+X_SHIFT+LEAN[0]*f['lean']
    y=r*math.sin(theta)*Y_SCALE+Y_SHIFT+LEAN[1]*f['lean']
    if info is not None:info.update(f)
    return (x,y,z)


# ---------------------------------------------------------------- rig
SEGMENTS=192
RINGS=112
LEVELS=(FLOOR,2.5,9.0,15.4,21.2,24.8)
COUNT=(1,16,16,16,8,1)   # anchors per ring: fine lower rings allow a narrow tongue
SPECS=[('root',None,(0,0,0))]
for _level in (1,2,3,4):
    _z=LEVELS[_level]
    _v=min((k/2000 for k in range(2001)),key=lambda q:abs(profile(q)[1]-_z) if q>.1 else 99)
    _r=profile(_v)[0]*.82
    for _side in range(COUNT[_level]):
        _a=TAU*_side/COUNT[_level]
        SPECS.append((f'gel_{_level}_{_side}','root',(round(_r*math.cos(_a)+X_SHIFT,6),round(_r*math.sin(_a)*Y_SCALE+Y_SHIFT,6),_z)))
SPECS.append(('crest','root',(round(X_SHIFT+LEAN[0],6),round(Y_SHIFT+LEAN[1],6),LEVELS[-1])))
RIG=Rig.from_world(SPECS)
BONES,REST=RIG.bones,RIG.rest
CREST=len(BONES)-1
CLIPS=[('idle',48,20,True),('ooze',32,35,True),('slime',26,35,False),
       ('drench',30,35,False),('recoil',16,35,False),('collapse',40,35,False)]
# Connected-skin bake configuration (module-local, see creature-pipeline.md).
CONNECTED_SKIN=lambda name:name=='black_jelly_gel'
SKIN_FACE_BUDGET=14000


def bone(level,side):
    return 0 if level==0 else CREST if level==5 else 1+sum(COUNT[1:level])+side%COUNT[level]


def quantize(values):
    """Deterministic 1e-6 weights; the last influence takes the remainder."""
    items=sorted((b,w) for b,w in values.items() if w>1e-7)
    if len(items)==1:return [(items[0][0],1)]
    # fsum is exact, so Blender's and the system Python agree bit for bit.
    total=math.fsum(w for _,w in items)
    out=[(b,round(w/total,6)) for b,w in items[:-1]]
    out.append((items[-1][0],round(1-math.fsum(w for _,w in out),6)))
    return out


def blend(theta,z):
    """Bilinear ring/azimuth blend, linear in rest height between rings."""
    z=max(LEVELS[0],min(LEVELS[-1],z))
    lower=next((i for i in range(5) if z<=LEVELS[i+1]),4)
    high=(z-LEVELS[lower])/(LEVELS[lower+1]-LEVELS[lower])
    values={}
    for ring,amount in ((lower,1-high),(lower+1,high)):
        n=COUNT[ring];angle=(theta%TAU)/TAU*n;side=int(angle)%n;fraction=angle-int(angle)
        for j,t in ((side,1-fraction),(side+1,fraction)):
            b=bone(ring,j)
            if amount*t>1e-12:values[b]=values.get(b,0)+amount*t
    return quantize(values)


def weights(part,p,uv):
    # Bake input: actual rest height (sagging piles hang below the pool
    # surface they overhang and must move with it) and the skin azimuth.
    return blend(theta_of(uv[0]),p[2])


@functools.lru_cache(maxsize=None)
def lean_at(z):
    """Crest lean offset as a function of rest height (matches the sculpt)."""
    v=min((k/400 for k in range(401)),key=lambda q:abs(profile(q)[1]-z) if q>.08 else 99)
    return smooth((v-.45)/.55)**1.5


def runtime_weights(p):
    """Exact position-only weights for the baked cage.

    The shared bake relaxes transferred weights across neighbours, which
    blurs the height blend; the flattening death needs the weighted anchor
    height to equal the vertex height exactly so no flank folds. Depending on
    position alone also keeps coincident UV-seam copies identical.
    """
    lean=lean_at(round(p[2],3))
    cx=X_SHIFT+LEAN[0]*lean;cy=Y_SHIFT+LEAN[1]*lean
    return blend(math.atan2((p[1]-cy)/Y_SCALE,p[0]-cx),p[2])


def build_parts():
    """The analytic closed gel surface the connected-skin bake fuses."""
    part=Part('black_jelly_gel')
    part.vertices.append(tuple(round(c,6) for c in surface(0.,0.)));part.uv.append((.5,0.))
    for ring in range(1,RINGS):
        v=ring/RINGS
        for s in range(SEGMENTS+1):
            u=s/SEGMENTS
            part.vertices.append(tuple(round(c,6) for c in surface(theta_of(u),v)))
            part.uv.append((round(u,6),round(v,6)))
    part.vertices.append(tuple(round(c,6) for c in surface(0.,1.)));part.uv.append((.5,1.))
    top=len(part.vertices)-1
    for s in range(SEGMENTS):part.faces.append((0,2+s,1+s))
    for ring in range(RINGS-2):
        for s in range(SEGMENTS):
            a=1+ring*(SEGMENTS+1)+s
            part.faces.append((a,a+1,a+SEGMENTS+2,a+SEGMENTS+1))
    start=1+(RINGS-2)*(SEGMENTS+1)
    for s in range(SEGMENTS):part.faces.append((start+s,start+s+1,top))
    return [part]


_GEOMETRY={}


def _angle_cos(p,a,b):
    u=sub(a,p);w=sub(b,p)
    return sum(x*y for x,y in zip(u,w))/math.sqrt(sum(x*x for x in u)*sum(x*x for x in w))


def flip_caps(part,limit=-.89):
    """Flip the long edge of decimation cap triangles (an angle above ~153°).

    A near-collinear cap flips orientation under any shear. Swapping its long
    edge with the neighbour across it removes it without moving a vertex. A
    flip is kept only when both new triangles are well shaped (no angle above
    ~153°) and keep the surface orientation, so every flip strictly reduces
    the number of caps and the passes terminate. Deterministic index order.
    """
    V=part.vertices;faces=[list(f) for f in part.faces]
    def normal(f):return cross(sub(V[f[1]],V[f[0]]),sub(V[f[2]],V[f[0]]))
    def worst(f):return max(-_angle_cos(V[f[k]],V[f[(k+1)%3]],V[f[(k+2)%3]]) for k in range(3))
    edges={}
    for i,f in enumerate(faces):
        for k in range(3):edges[(f[k],f[(k+1)%3])]=i
    changed=True
    while changed:
        changed=False
        for i in range(len(faces)):
            f=faces[i]
            for k in range(3):
                c,a,b=f[k],f[(k+1)%3],f[(k+2)%3]
                if _angle_cos(V[c],V[a],V[b])>limit:continue
                j=edges.get((b,a))
                if j is None:continue
                g=faces[j];d=next(x for x in g if x not in (a,b))
                if (c,d) in edges or (d,c) in edges:continue
                new1,new2=[c,a,d],[c,d,b]
                old=normal(f)
                if any(sum(x*y for x,y in zip(normal(n),old))<=0 for n in (new1,new2)):continue
                if max(worst(new1),worst(new2))>=-limit:continue
                for q in (f,g):
                    for m in range(3):edges.pop((q[m],q[(m+1)%3]),None)
                faces[i],faces[j]=new1,new2
                for idx,q in ((i,new1),(j,new2)):
                    for m in range(3):edges[(q[m],q[(m+1)%3])]=idx
                changed=True;break
    part.faces=[tuple(f) for f in faces]


def geometry():
    if 'g' not in _GEOMETRY:
        parts=connected_skin.attach('black_jelly',build_parts(),weights)
        cache={}
        for part in parts:
            flip_caps(part)
            part.skin_weights=[cache.setdefault(tuple(p),runtime_weights(p)) for p in part.vertices]
        _GEOMETRY['g']=assemble(parts,weights)
    return _GEOMETRY['g']


# ---------------------------------------------------------------- clips
_SETTLE={}


def puddle_target(p):
    """Spent pose: flattened, widened ink with an irregular, slumped edge.

    Heights map affinely (0.75 + 0.17 z) and the spread grows smoothly with
    height, so the map is monotone in every direction.
    """
    x,y=p[0]-X_SHIFT,p[1]-Y_SHIFT
    theta=math.atan2(y,x)
    spread=1.02+.24*smooth(p[2]/22)+.05*math.sin(3*theta+.4)+.035*math.sin(5*theta+1.9)
    fold=smooth((p[2]-12)/14)
    return (spread*x+X_SHIFT+1.6*fold,spread*y+Y_SHIFT+2.0*fold,.75+.17*p[2])


def settle_shifts():
    """Each anchor travels to its image under the spent-puddle map.

    Weights are linear in rest height between rings, so the weighted anchor
    height equals the vertex height and the flatten stays exactly ordered:
    no flank can fold through another. The root and floor never move.
    """
    if not _SETTLE:
        for b,(name,parent,local) in enumerate(BONES):
            if b==0:continue
            target=puddle_target(REST[b])
            _SETTLE[b]=tuple(round(t-r,6) for t,r in zip(target,REST[b]))
    return _SETTLE


def bell(t):
    t=max(0.,min(1.,t));return math.sin(math.pi*t)**2


def pose(name,t):
    phase=TAU*t
    shifts=[(0,0,0) for _ in BONES]
    settles=settle_shifts() if name=='collapse' else None
    for level in (1,2,3,4,5):
        h=(LEVELS[level]-LEVELS[0])/(LEVELS[-1]-LEVELS[0])
        for side in range(COUNT[level]):
            a=TAU*side/COUNT[level] if level<5 else 0.
            ca,sa=(math.cos(a),math.sin(a)) if level<5 else (0.,0.)
            front=max(0.,ca);behind=max(0.,-ca)
            dx=dy=dz=0.
            if name=='idle':
                # Heavy breathing: the heap slumps and bulges, a ripple runs
                # down the flanks and the leaning crest sways.
                slump=math.sin(phase-1.6*h)
                ripple=math.sin(2*phase+3*a-2*h)*4*h*(1-h)
                radial=.9*(1-.4*h)*slump+.7*ripple
                dx=ca*radial+1.3*h*h*math.sin(phase)
                dy=sa*radial+1.0*h*h*math.cos(phase)
                dz=-1.6*h*slump
                if level==1:dx,dy,dz=ca*.5*math.sin(phase-a),sa*.5*math.sin(phase-a),max(0.,.2*math.sin(phase-a))
            elif name=='ooze':
                # A peristaltic wave rolls front to back; the tongue reaches.
                wave=math.sin(phase-2.4*h)
                dx=2.3*h*wave+ca*.8*math.sin(phase+a)*(1-h)
                dy=.8*h*math.sin(phase+.7)+sa*.6*math.sin(phase+a)*(1-h)
                dz=1.4*h*math.sin(2*phase-3*h)
                if level==1:
                    dx=ca*.4*math.sin(phase-a)+1.6*front*math.sin(phase+.9)
                    dy=sa*.4*math.sin(phase-a);dz=max(0.,.3*math.sin(2*phase-a))
            elif name=='slime':
                # Rear back, then (middle frame) a long pseudopod lunges out of
                # the heap's front toward the target while the body leans in
                # after it and thins at the flanks; recover.
                gather=bell(t/.30)
                surge=bell((t-.04)/.92)
                tongue=gauss(wrap(a)/.34) if level<4 else 0.
                behind=max(0.,-ca)
                reach=(0,2.0,10.0,10.0,0,0)[level]
                dx=-gather*(2.6*h+.5)+surge*(reach*tongue+2.4*behind*(level in (2,3))+4.6*h*h)
                dy=-surge*sa*(1-tongue)*(3.4 if level in (2,3) else 1.8 if level==4 else 0.)
                # The pseudopod lifts off the pool and its tip pinches down.
                # The crouch eases over the pseudopod so its rings never cross.
                dz=gather*3.2*h*h+surge*(tongue*(2.0 if level==2 else -.6 if level==3 else 0.)-7.5*h*h*(1-.6*tongue))
                if level==1:dz=max(0.,.3*surge*tongue)
            elif name=='drench':
                # Squat, then (middle frame) rear into a tall breaking wave
                # whose crest curls forward over its own front, underside
                # showing; slap down and spread.
                squat=bell(t/.30)
                wave=bell((t-.14)/.72)
                slap=bell((t-.56)/.44)
                narrow=(0,0,2.4,3.2,2.0,0)[level]
                lift=(0,0,5.0,13.0,20.0,19.5)[level]
                ahead=(0,0,-1.0,3.0+1.5*front,8.0+5.0*front,16.5)[level]
                dx=wave*(ahead-ca*narrow)+slap*(ca*2.2*(1-h)+2.0*h)
                dy=-wave*sa*narrow+slap*sa*2.2*(1-h)
                dz=-squat*3.0*h+wave*(lift+(2.0*behind if level==4 else 0.))-slap*3.8*h
                if level==1:dx,dy,dz=slap*ca*1.8,slap*sa*1.8,0.
            elif name=='recoil':
                # Knocked back and squashed at the middle frame, then jiggles.
                push=bell(t)
                jig=math.sin(TAU*1.5*t)*(1-t)**2
                dx=-push*(4.8*h+1.6*front*(1-h))+jig*1.8*h
                dy=push*sa*2.0*(1-h)+math.sin(TAU*2*t)*(1-t)**2*2.4*h
                dz=-push*6.0*h+jig*1.4*h
                if level==1:dx,dy,dz=-push*.8*front,push*sa*.6,0.
            elif name=='collapse':
                # The crest folds first; by the middle frame the heap is half
                # slumped, then it spreads into a spent ink puddle.
                sag=smooth(t/.5)
                settle=smooth((t-.08)/.84)
                lead=.45*sag+.55*settle if level>=3 else settle
                dx,dy,dz=(c*lead for c in settles[bone(level,side)])
            shifts[bone(level,side)]=(dx,dy,dz)
    return [(*add(local,shifts[i]),0,0,0,1,1,1,1) for i,(n,p,local) in enumerate(BONES)]


def matrices(frame):return RIG.matrices(frame)
def deform(v,w,frame):return RIG.deform(v,w,frame)
def animation_data(v,w):return sample_clips(RIG,CLIPS,pose,v,w)


def build():
    from . import black_jelly_materials as materials
    maps={SKIN:materials.texture_bytes(),**materials.surface_maps()}
    for path,data in maps.items():(ROOT/'mod/BrogueDoom'/path).write_bytes(data)
    parts,v,n,uv,t,w=geometry();clips,bounds=animation_data(v,w)
    data=iqm.encode(v,n,uv,t,w,BONES,clips,bounds,mesh_label='Project_Broom_black_jelly',material_path=SKIN)
    path=ROOT/'mod/BrogueDoom/models/monsters/52_black_jelly.iqm';path.write_bytes(data)
    manifest=dict(schemaVersion=1,workId='BRG-M52',format='IQM v2',
        runtimeModel=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(data).hexdigest(),
        skin=SKIN,skinSha256=hashlib.sha256(maps[SKIN]).hexdigest(),
        materialMaps={p:hashlib.sha256(b).hexdigest() for p,b in maps.items()},
        shader=SHADER,shaderSha256=hashlib.sha256((ROOT/'mod/BrogueDoom'/SHADER).read_bytes()).hexdigest(),
        dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],
        parts=len(parts),vertices=len(v),triangles=len(t),boneCount=len(BONES),
        bones=[dict(name=n,parent=p,local=v) for n,p,v in BONES],
        clips=[{k:v for k,v in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],
        poseBounds=bounds,authoringSource='assets/monsters/black_jelly/black-jelly-animated.blend')
    out=ROOT/'assets/monsters/black_jelly';out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__':
    result=build();print({k:result[k] for k in ('sha256','dimensions','vertices','triangles')})

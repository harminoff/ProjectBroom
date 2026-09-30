"""Original storm-djinn ifrit for Brogue's MK_IFRIT (presentation only).

Brogue: "A whirling desert storm given human shape, the ifrit's twin scimitars flicker
in the darkness and [its] eyes burn with otherworldly zeal." It is a violet-blue
(ifritColor) flier, immune to fire, fast-moving with strong melee, and casts discord.

The model is a very broad, heavy-shouldered djinn with a sculpted torso (pecs, abdominal
blocks, lats, traps), tapered forearms and biceps, a large fanged face under a heavy brow
with swept-back horns, a full moustache and beard, gold collar, armlets and bracers, and
twin curved scimitars with dark spines and ember-forged edge strips. It has no legs: the
body narrows into a vortex of layered, ragged, twisting smoke sheets around a dark core,
tapering to a point at the floor and sparked with embers.

Skin lighting is baked from the geometry (key, fill, crevice occlusion, ember under-glow;
see `bake_skin`), so the flat engine light still shows muscle. Eyes, edge strips, crown
flame, burst flecks and smoke sparks are fullbright (painted ember key). Rigid parts and
chain weights over 44 bones; no connected skin. Brogue owns flight, speed, melee, discord
and timing; this file only draws.
"""
import hashlib,json,math
from . import iqm
from .rat import ROOT,Part,add,sub,mul,cross,unit,spline
from .skeletal import Rig,axis,qmul,inverse,rotate,assemble,sample_clips
from . import ifrit_materials as materials
from .connected_skin import attach

SKIN='graphics/BRGIFRIT.png'
MODEL='mod/BrogueDoom/models/monsters/64_ifrit.iqm'
SHADER='mod/BrogueDoom/shaders/ifrit-embers.fp'
SKIN_VOXEL_SIZE=.26
SKIN_FACE_BUDGET=11000


def CONNECTED_SKIN(name):
    """Torso, neck, shoulders, arms and hands fuse into one skin; every other part is a rigid attachment."""
    return name.startswith('skin_')


def mirror(p,s):return (p[0],p[1]*s,p[2])


K=.88
HEAD_C=(3.0,0.0,58.0);HEAD_S=1.26;HEAD_LIFT=2.4
SH=(0.0,19.0,47.0);EL=(3.0,26.5,35.5);WR=(9.0,24.0,43.5)
BURST=16
SPECS0=[('root',None,(0,0,0)),('hips','root',(0,0,25)),('t1','hips',(0,0,17)),('t2','t1',(0,0,10)),('t3','t2',(0,0,4)),
        ('spine','hips',(1,0,32)),('chest','spine',(1.5,0,42)),('neck','chest',(2.5,0,52)),('head','neck',(3,0,57.5)),
        ('eye_L','head',(8.4,-3.2,59.6)),('eye_R','head',(8.4,3.2,59.6)),('crown','head',(.8,0,65.4))]
for s,n in ((-1,'L'),(1,'R')):
    SPECS0+=[(f'sh_{n}','chest',mirror(SH,s)),(f'el_{n}',f'sh_{n}',mirror(EL,s)),(f'wr_{n}',f'el_{n}',mirror(WR,s)),
             (f'edge_{n}',f'wr_{n}',mirror(WR,s))]
BURST_REST=[(1.0+.4*(k%2),((k%3)-1)*3.6,37.5+1.9*(k//3)) for k in range(BURST)]
SPECS0+=[(f'burst_{k}','chest',BURST_REST[k]) for k in range(BURST)]
SPECS=[(n,par,tuple(round(K*c,6) for c in loc)) for n,par,loc in SPECS0]
RIG=Rig.from_world(SPECS);BONES,REST=RIG.bones,RIG.rest
IDS={n:i for i,(n,_,_) in enumerate(BONES)}
CLIPS=[('idle',48,24,True),('fly',32,35,True),('slash',26,35,False),('discord',28,35,False),
       ('recoil',14,35,False),('collapse',40,35,False)]


def quantize(weights):
    weights=[(b,w) for b,w in weights if w>5e-7]
    head=[(b,round(w,6)) for b,w in weights[:-1]]
    rows=head+[(weights[-1][0],round(1-math.fsum(w for _,w in head),6))]
    return [(b,w) for b,w in rows if w>0]


class Piece(Part):
    """Part with paint role and per-vertex paint coordinates (pa around, pv along)."""
    def __init__(self,name,role):
        super().__init__(name);self.role=role;self.pa=[];self.pv=[]
    def add(self,co,a=0,v=0):
        self.vertices.append(tuple(round(c,6) for c in co));self.pa.append(a);self.pv.append(v);return len(self.vertices)-1


def rings(p,rows,closed_start=True,closed_end=True):
    point=lambda row:len({p.vertices[i] for i in row})==1
    for r0,r1 in zip(rows,rows[1:]):
        for j in range(len(r0)-1):
            if point(r0):p.faces.append((r0[j],r1[j+1],r1[j]))
            elif point(r1):p.faces.append((r0[j],r0[j+1],r1[j]))
            else:p.faces.append((r0[j],r0[j+1],r1[j+1],r1[j]))
    for ring,start in ((rows[0],True),(rows[-1],False)):
        if (closed_start if start else closed_end) and not point(ring):
            c=[p.vertices[i] for i in ring[:-1]]
            centre_=p.add(tuple(math.fsum(x)/len(c) for x in zip(*c)),p.pa[ring[0]],p.pv[ring[0]])
            for j in range(len(ring)-1):p.faces.append((centre_,ring[j+1],ring[j]) if start else (centre_,ring[j],ring[j+1]))


def tube_frames(pts,up):
    prev=None;out=[]
    for i,row in enumerate(pts):
        c,r=row[:3],max(.02,row[3]);t=unit(sub(pts[min(i+1,len(pts)-1)][:3],pts[max(0,i-1)][:3]))
        if prev is None:n=unit(cross(t,cross(up,t))) if abs(sum(a*b for a,b in zip(t,unit(up))))<.95 else unit(cross(t,(0,1,0)))
        else:n=unit(sub(prev,mul(t,sum(a*b for a,b in zip(prev,t)))))
        prev=n;out.append((c,r,n,unit(cross(t,n))))
    return out


def tube(name,controls,role,sides=10,samples=3,flatten=1.0,up=(0,0,1)):
    """Swept ellipse; controls (x,y,z,radius). Paint: a around (0 = +up side), v along."""
    p=Piece(name,role);pts=spline(controls,samples) if samples>1 else [tuple(c) for c in controls];rows=[]
    for i,(c,r,n,bn) in enumerate(tube_frames(pts,up)):
        u=i/(len(pts)-1)
        rows.append([p.add(add(c,add(mul(n,r*math.cos(math.tau*j/sides)),mul(bn,r*flatten*math.sin(math.tau*j/sides)))),j/sides,u)
                     for j in range(sides+1)])
    rings(p,rows)
    return p


def ball(name,c,r,role,seg=12,rings_=6):
    """Ellipsoid, paint a=longitude (.5 faces +X), v top 0 to bottom 1."""
    p=Piece(name,role);rows=[]
    for i in range(rings_+1):
        ph=-math.pi/2+math.pi*i/rings_;row=[]
        for j in range(seg+1):
            th=math.tau*j/seg+math.pi
            row.append(p.add((c[0]+r[0]*math.cos(ph)*math.cos(th),c[1]+r[1]*math.cos(ph)*math.sin(th),c[2]+r[2]*math.sin(ph)),j/seg,1-i/rings_))
        rows.append(row)
    rings(p,rows,False,False)
    return p


def paint(p,a,v):
    p.pa=[a]*len(p.pa);p.pv=[v]*len(p.pv);return p


def loft(name,sections,role,sides=28):
    """Elliptic sections (z,cx,cy,rx,ry), paint a around (0 faces +X), v along."""
    p=Piece(name,role);pts=spline(sections,3);rows=[]
    for i,(z,cx,cy,rx,ry) in enumerate(pts):
        u=i/(len(pts)-1)
        rows.append([p.add((cx+rx*math.cos(math.tau*j/sides),cy+ry*math.sin(math.tau*j/sides),z),j/sides,u) for j in range(sides+1)])
    rings(p,rows)
    return p


def ribbon(name,centre,halfwidth,thick,role,rows=24,sides=8):
    """Thin ragged sheet swept along centre(s): the wide axis stays tangential to the vortex."""
    p=Piece(name,role);pts=[centre(i/rows) for i in range(rows+1)];out=[]
    for i,c in enumerate(pts):
        t=unit(sub(pts[min(i+1,rows)],pts[max(0,i-1)]));rad=(c[0],c[1],0.0)
        rad=rad if math.hypot(rad[0],rad[1])>1e-6 else (1.0,0.0,0.0)
        wv=cross((0,0,1),rad);wv=unit(sub(wv,mul(t,sum(a*b for a,b in zip(wv,t)))));th=unit(cross(t,wv))
        s=i/rows;hw=halfwidth(s);tk=thick(s)
        out.append([p.add(add(c,add(mul(wv,hw*math.cos(math.tau*j/sides)),mul(th,tk*math.sin(math.tau*j/sides)))),j/sides,s) for j in range(sides+1)])
    rings(p,out)
    return p


def circle(c,rx,ry,n=24):
    return [(c[0]+rx*math.cos(math.tau*i/n),c[1]+ry*math.sin(math.tau*i/n),c[2]) for i in range(n+1)]


def around_axis(a,b,t,radius,thick,role,sides=8,flat=1.0,name='ring'):
    d=unit(sub(b,a));c=add(a,mul(sub(b,a),t));u=unit(cross(d,(0,0,1)));v=cross(d,u)
    pts=[add(c,add(mul(u,radius*math.cos(math.tau*i/16)),mul(v,radius*math.sin(math.tau*i/16)))) for i in range(17)]
    return tube(name,[(*q,thick) for q in pts],role,sides,1,flat)


def surface_x(y,z,center=HEAD_C,r=(5.6,5.0,6.4),lift=.2):
    q=1-(y/r[1])**2-((z-center[2])/r[2])**2
    return center[0]+r[0]*math.sqrt(max(0,q))+lift


BLADE_R=[2.7,3.3,4.1,4.4,.25]


def blade_path(s):
    return [(9,24*s,47),(9.4,25*s,55),(11.8,25.6*s,63),(17.5,24.6*s,69),(25.5,22.2*s,71.6)]


def tooth(name,x,y,z0,z1,r=.5):
    return tube(name,[(x,y,z0,r),(x,y,z1,.03)],'ivory',5,1,1.0)


def oval(name,centre,major,front,radii,role,seg=14,rings_=8):
    """Elongated flattened ellipsoid: radii = (along `major`, across it in the surface plane, thickness along `front`)."""
    a=unit(major);f=unit(sub(front,mul(a,sum(x*y for x,y in zip(front,a)))));t=cross(a,f)
    p=Piece(name,role);rows=[]
    for i in range(rings_+1):
        ph=-math.pi/2+math.pi*i/rings_;row=[]
        for j in range(seg+1):
            th=math.tau*j/seg;X=math.cos(ph)*math.cos(th);Y=math.cos(ph)*math.sin(th);Z=math.sin(ph)
            row.append(p.add(add(centre,add(add(mul(a,radii[0]*X),mul(t,radii[1]*Y)),mul(f,radii[2]*Z))),j/seg,1-i/rings_))
        rows.append(row)
    rings(p,rows,False,False)
    return p


def weights(part,v,uv):
    return part.wfn(v)


def build_parts():
    out=[];head_parts=[]
    def put(p,bone=None,chain=None,head=False):
        if head:head_parts.append(p);p.bone=bone;return p
        finish(p,bone,chain);return p
    def finish(p,bone=None,chain=None):
        p.vertices=[tuple(round(K*c,6) for c in v) for v in p.vertices]
        p.uv=[(a,b) for a,b in zip(p.pa,p.pv)]                       # raw paint coordinates; the skin re-bakes its own
        if chain:
            ids=[IDS[c] for c in chain];p.wfn=lambda v,ids=ids:quantize(RIG.chain_weights(v,ids))
        else:p.wfn=lambda v,b=IDS[bone]:[(b,1)]
        p.skin_weights=[p.wfn(v) for v in p.vertices]
        out.append(p)
    trunk=['hips','spine','chest','neck'];tail=['t3','t2','t1','hips','spine']
    # ---- Torso, neck and shoulders: one fused skin built from overlapping elongated, flattened masses.
    put(loft('skin_torso',[(26,0,0,9.5,10.6),(31,.3,0,9.6,10.5),(36,.7,0,10.4,12.4),(41,1.2,0,11.4,15.8),(45.5,1.6,0,11.6,18.0),
                           (49,1.8,0,9.8,17.2),(51.6,2.0,0,7.2,11.0),(54.6,2.6,0,5.4,6.2)],'skin',28),chain=trunk)
    put(oval('skin_abs_plate',(9.6,0,35.6),(0,0,1),(1,0,0),(7.8,6.6,1.9),'skin',16,10),'spine')
    put(oval('skin_abs_lower',(9.2,0,29.6),(0,0,1),(1,0,0),(4.0,5.4,1.6),'skin',12,8),'spine')
    for s_ in (-1,1):
        put(oval(f'skin_pec_{s_}',(8.2,6.8*s_,44.2),(0,.93*s_,.37),(1,0,0),(8.8,4.7,3.5),'skin',16,10),'chest')
        put(oval(f'skin_trap_{s_}',(1.0,9.6*s_,50.4),(0,.97*s_,-.22),(1,0,0),(10.4,3.7,3.6),'skin',14,8),'chest')
        put(oval(f'skin_lat_{s_}',(-2.0,14.0*s_,40.0),(0,.2*s_,-.98),(1,0,0),(8.4,4.4,3.0),'skin',12,8),'chest')
        put(tube(f'skin_neck_cord_{s_}',[(1.8,4.6*s_,58.0,1.5),(3.4,4.3*s_,54.0,1.9),(4.2,4.8*s_,50.5,2.3)],'skin',8,3),chain=['neck','chest'])
    # ---- Smoke vortex tail: dark core plus layered ragged sheets twisting down to a point.
    put(loft('vortex_core',[(27,0,0,9.0,9.8),(20,0,0,9.4,10.0),(13,0,0,6.6,6.9),(7,0,0,3.6,3.7),(2.6,0,0,1.5,1.5),(.9,0,0,.3,.3)],'core',24),chain=tail)
    tips=[2.0,4.6,1.6,6.4,3.0,8.2,2.6,5.4,1.2]
    for k,zt in enumerate(tips):
        th0=k*.698132+.3;turns=1.9+.22*(k%3);ztop=26.6-.5*(k%3);layer=.84+.1*(k%4)
        def centre(s,th0=th0,turns=turns,ztop=ztop,zt=zt,k=k,layer=layer):
            rho=(10.6*(1-s)**.9+.7)*layer+.8*math.sin(6*s+k)*s
            a=th0+turns*math.tau*s;return (rho*math.cos(a),rho*math.sin(a),ztop+(zt-ztop)*s)
        def hw(s,k=k):
            rag=1+.45*math.sin(7*s+k*1.7)+.25*math.sin(19*s+k)
            return 3.9*(1-.5*s)*rag*min(1,max(.05,(1-s)*3.4))**.6
        put(ribbon(f'smoke_sheet_{k}',centre,hw,lambda s:.7+.4*(1-s),'smoke',26,8),chain=tail)
    for k,(zt,turns,th0) in enumerate([(5.0,1.7,.4),(9.0,1.4,1.5),(3.4,1.9,2.6),(12.0,1.2,3.7),(6.6,1.6,4.8),(10.0,1.5,5.7)]):
        def centre(s,th0=th0,turns=turns,zt=zt):
            rho=7.0+10.0*math.sin(math.pi*min(1.0,s*1.12))**.75-2.5*s
            a=th0+turns*math.tau*s;return (rho*math.cos(a),rho*math.sin(a),25.6+(zt-25.6)*s)
        def hw(s,k=k):
            rag=1+.4*math.sin(10*s+k*2.3)+.2*math.sin(27*s+k)
            return 2.6*(1-.6*s)*rag*min(1,max(.05,(1-s)*3.0))**.6
        put(ribbon(f'smoke_wisp_{k}',centre,hw,lambda s:.45,'smoke',22,7),chain=tail)
    # ---- Gold belt and crimson sash wrap.
    put(tube('belt',[(*q,1.55) for q in circle((0,0,27.6),10.6,11.5)],'gold',8,1,.9),chain=['hips','spine'])
    put(ball('belt_boss',(10.4,0,27.8),(1.9,3.0,2.3),'gold',10,6),'hips')
    put(tube('sash_wrap',[(*q,2.0) for q in circle((0,0,24.6),10.9,11.9)],'cloth',8,1,1.15),chain=['hips','spine'])
    put(tube('collar',[(*q,1.5) for q in circle((2.4,0,51.4),7.4,9.6)],'gold',8,1,.8),chain=['chest','neck'])
    # ---- Head (built about HEAD_C, enlarged as a group): skull, heavy brow, cheeks, jaw, fangs, hair, horns, flame.
    put(ball('head',HEAD_C,(5.6,5.0,6.4),'skin',22,11),'head',head=True)
    put(ball('jaw',(5.4,0,52.6),(4.8,4.5,3.1),'skin',12,7),'head',head=True)
    put(ball('brow_ridge',(6.4,0,62.4),(3.0,5.4,1.05),'skin',14,7),'head',head=True)
    for s in (-1,1):
        put(ball(f'brow_{s}',(6.3,2.2*s,61.4),(2.6,2.4,1.0),'skin',10,6),'head',head=True)
        put(ball(f'brow_outer_{s}',(5.4,4.4*s,62.6),(2.2,2.0,1.1),'skin',10,6),'head',head=True)
        put(ball(f'cheek_{s}',(6.2,4.1*s,56.4),(2.7,2.2,1.8),'skin',10,6),'head',head=True)
    put(ball('nose',(8.0,0,57.0),(1.9,1.3,2.0),'skin',8,5),'head',head=True)
    put(paint(ball('mouth',(7.2,0,54.4),(2.2,3.6,1.9),'hair',10,6),.5,.3),'head',head=True)
    for i in range(7):
        y=-3.0+i*1.0;x=surface_x(y,54.5,lift=-.3)+.2
        put(tooth(f'tooth_up_{i}',x,y,55.6,53.9+ (0 if i in (1,5) else .6),.5),'head',head=True)
    for i in range(5):
        y=-2.0+i*1.0;put(tooth(f'tooth_low_{i}',7.4,y,52.9,54.6,.5),'head',head=True)
    for s in (-1,1):
        put(tooth(f'fang_up_{s}',8.3,2.1*s,56.0,51.8,.85),'head',head=True)
        put(tooth(f'fang_low_{s}',8.0,2.6*s,52.4,57.0,.8),'head',head=True)
        put(tube(f'ear_{s}',[(1.5,5.2*s,58.5,1.9),(-.5,8.4*s,60.5,1.5),(-2.6,10.6*s,63.8,.25)],'skin',8,3,.6),'head',head=True)
        put(tube(f'earring_{s}',[(*q,.42) for q in ((1.6+1.9*math.cos(a),(5.7 if s>0 else -5.7),56.4+1.9*math.sin(a)) for a in [math.tau*i/14 for i in range(15)])],'gold',6,1),'head',head=True)
        put(tube(f'horn_{s}',[(2.4,3.8*s,62.2,2.7),(-1.8,7.4*s,68.0,2.4),(-7.6,9.6*s,66.6,1.6),(-11.6,8.6*s,61.2,.3)],'horn',10,4),'head',head=True)
        for j,(dy,dz,rr) in enumerate(((0,0,1.55),(.6,-1.2,1.25))):
            put(tube(f'moustache_{s}_{j}',[(7.4,3.6*s,56.6+dz*.3,rr*.9),(7.0,5.6*s,54.6+dz*.4,rr*.85),(5.6,8.2*s,50.8+dz,rr*.6),(3.2,9.6*s,47.0+dz,.2)],'hair',8,3,.85),'head',head=True)
        # Slit eye that hugs the skull under the brow; emissive by the painted key.
        pts=[(surface_x(y*s,z),y*s,z) for y,z in ((1.2,58.4),(2.8,59.0),(4.3,60.0))]
        put(tube(f'eye_{s}',[(*q,.95) for q in pts],'fire',7,3,.8),'eye_L' if s<0 else 'eye_R',head=True)
    put(ball('goatee',(7.0,0,47.6),(2.3,2.4,3.7),'hair',10,6),'head',head=True)
    put(tube('beard_tuft',[(6.4,0,50.0,2.0),(7.2,0,46.0,1.8),(6.4,0,42.4,.25)],'hair',8,3),'head',head=True)
    for k,(dx,tz,tx) in enumerate([(1,69.5,-2.0),(1,66.6,2.4),(-1,66.0,-5.0)]):
        put(tube(f'crown_flame_{k}',[(.8+dx*.4*k,(-1.6 if k==1 else 1.6 if k==2 else 0),63.6,2.0-.35*k),(.3,0,(63.6+tz)/2+.6,1.6-.3*k),(tx*.6,0,tz-1,.8),(tx,0,tz,.15)],'fire',8,3,.6,(0,1,0)),'crown',head=True)
    for p in head_parts:
        p.vertices=[tuple(round(HEAD_C[a]+(v[a]-HEAD_C[a])*HEAD_S+(HEAD_LIFT if a==2 else 0),6) for a in range(3)) for v in p.vertices]
        finish(p,p.bone)
    # ---- Arms: shaped masses, gold bands and bracers, fists and scimitars with edge strips.
    for s,n in ((-1,'L'),(1,'R')):
        sh,el,wr=(mirror(SH,s),mirror(EL,s),mirror(WR,s));mid=mul(add(sh,el),.5)
        sd=unit(sub(el,sh))
        put(oval(f'skin_deltoid_{n}',add(sh,mul(sub(el,sh),.2)),sd,(1,0,0),(10.6,7.4,7.4),'skin',16,10),f'sh_{n}')
        put(tube(f'skin_upper_arm_{n}',[(*sh,6.8),(*add(mid,(1.2,s*.9,0)),7.0),(*el,5.6)],'skin',14,3),chain=[f'sh_{n}',f'el_{n}'])
        def along(t,off):return add(add(sh,mul(sub(el,sh),t)),off)
        put(tube(f'skin_biceps_{n}',[(*along(.1,(4.2,s*.4,0)),2.4),(*along(.35,(5.2,s*.5,0)),5.0),(*along(.7,(4.4,s*.4,0)),3.8),(*along(.92,(3.0,s*.3,0)),2.0)],'skin',12,3),chain=[f'sh_{n}',f'el_{n}'])
        put(tube(f'skin_triceps_{n}',[(*along(.12,(-3.8,s*1.4,0)),2.6),(*along(.45,(-5.0,s*1.8,0)),4.8),(*along(.85,(-3.6,s*1.2,0)),2.8)],'skin',12,3),chain=[f'sh_{n}',f'el_{n}'])
        put(ball(f'skin_elbow_{n}',el,(5.6,5.6,5.8),'skin',12,7),f'el_{n}')
        fm=add(mul(add(el,wr),.5),(.6,0,0))
        put(tube(f'skin_forearm_{n}',[(*el,6.2),(*add(el,mul(sub(wr,el),.28)),6.8),(*fm,5.6),(*add(el,mul(sub(wr,el),.8)),4.4),(*wr,3.8)],'skin',12,3),chain=[f'el_{n}',f'wr_{n}'])
        def fore(t,off):return add(add(el,mul(sub(wr,el),t)),off)
        put(tube(f'skin_brachioradialis_{n}',[(*fore(.06,(2.6,0,0)),2.2),(*fore(.3,(4.0,0,0)),3.8),(*fore(.62,(3.0,0,0)),2.0)],'skin',10,3),chain=[f'el_{n}',f'wr_{n}'])
        put(around_axis(sh,el,.42,8.0,1.3,'gold',8,name=f'ringband_{n}'),f'sh_{n}')
        put(tube(f'bracer_{n}',[(*add(el,mul(sub(wr,el),.34)),7.2),(*add(el,mul(sub(wr,el),.72)),5.6)],'gold',12,2,1.0),f'wr_{n}')
        put(ball(f'skin_fist_{n}',add(wr,(0,0,-.3)),(4.8,4.7,5.0),'skin',12,7),f'wr_{n}')
        b=blade_path(s);pommel=(b[0][0],b[0][1],b[0][2]-8.4)
        put(ball(f'pommel_{n}',pommel,(1.9,1.9,1.9),'gold',8,4),f'wr_{n}')
        put(tube(f'grip_{n}',[(*pommel,1.25),(b[0][0],b[0][1],b[0][2]-1.0,1.35)],'cloth',7,1,1.0),f'wr_{n}')
        put(tube(f'guard_{n}',[(b[0][0],b[0][1]-4.8,b[0][2]-.4,1.15),(b[0][0],b[0][1]+4.8,b[0][2]-.4,1.15)],'gold',7,1,1.0,(1,0,0)),f'wr_{n}')
        ctrl=[(*q,r) for q,r in zip(b,BLADE_R)]
        put(tube(f'scimitar_{n}',ctrl,'steel',10,6,.17,(-1,0,0)),f'wr_{n}')
        # Ember-forged cutting-edge strip riding just inside the convex edge; it sinks into the blade on the corpse.
        frames=tube_frames(spline(ctrl,6),(-1,0,0))
        strip=[(*add(c,mul(nn,r*.985)),.55*min(1,r/1.5)) for c,r,nn,bn in frames]
        put(tube(f'edge_strip_{n}',strip,'fire',5,1,1.0),f'edge_{n}')
    # ---- Burst flecks: hidden inside the chest until discord flings them out in a swirl.
    for k in range(BURST):
        put(paint(ball(f'fleck_{k}',BURST_REST[k],(1.3,1.3,2.1),'fire',6,3),.5,.75),f'burst_{k}')
    return out


# ---------------------------------------------------------------- baked skin light
KEY=unit((.55,.25,.8));FILL=unit((-.45,-.55,.35))


def concavity(p,normals):
    """Crevice measure per vertex from the surface itself: mean sine of the angle to 2-ring neighbours.

    Positive where the surface curves inward (the groove between pec and deltoid, armpit, elbow crease),
    zero or negative on convex muscle. Welds coincident (UV-split) vertices so seams shade identically.
    """
    key=[tuple(round(c,4) for c in v) for v in p.vertices];rep={};ids=[]
    for k in key:ids.append(rep.setdefault(k,len(rep)))
    pos=[None]*len(rep);nrm=[None]*len(rep)
    for i,r in enumerate(ids):pos[r]=p.vertices[i];nrm[r]=normals[i]
    adj=[set() for _ in rep]
    for a,b,c in p.triangles():
        a,b,c=ids[a],ids[b],ids[c]
        for x,y in ((a,b),(b,c),(c,a)):
            if x!=y:adj[x].add(y);adj[y].add(x)
    out=[]
    for r in range(len(rep)):
        ring=set(adj[r]);second=set()
        for n in adj[r]:second|=adj[n]
        ring|=second;ring.discard(r);total=0.0;count=0
        for n in sorted(ring):
            d=sub(pos[n],pos[r]);dist=math.sqrt(sum(x*x for x in d))
            if dist>1e-9:total+=sum(x*y for x,y in zip(d,nrm[r]))/dist;count+=1
        out.append(max(0.0,min(1.0,total/count*2.6)) if count else 0.0)
    return [out[r] for r in ids]


def groove(v):
    """Shallow abdominal grooves and the centre line, painted as extra occlusion on the fused skin (design units)."""
    x,y,z=v[0]/K,v[1]/K,v[2]/K
    if x<7.6 or not 27.5<z<41.5 or abs(y)>7.0:return 0.0
    g=max(0.0,1-abs(y)/.55)
    for zk in (33.4,37.6):g=max(g,max(0.0,1-abs(z-zk)/.5))
    return g*.55


def bake_skin(parts):
    """Per-vertex shade and ember under-glow for every 'skin' part, from geometry alone.

    shade = key + fill + sky, darkened by occlusion: vertices of other parts nearby, the surface's own
    concavity (so the fused skin gets creases where muscles meet) and the abdominal grooves.
    Pure Python with a spatial hash; results are quantized so different interpreters agree.
    """
    skin=[p for p in parts if p.role=='skin'];R=2.2;cell=R;grid={}
    for pi,p in enumerate(skin):
        for v in p.vertices:grid.setdefault((int(v[0]//cell),int(v[1]//cell),int(v[2]//cell)),[]).append((pi,v))
    for pi,p in enumerate(skin):
        normals=p.normals()
        cen=tuple(math.fsum(v[a] for v in p.vertices)/len(p.vertices) for a in range(3))
        flip=-1 if math.fsum(sum((v[a]-cen[a])*n[a] for a in range(3)) for v,n in zip(p.vertices,normals))<0 else 1
        conc=concavity(p,[mul(n,flip) for n in normals]);pa=[];pv=[]
        for v,n,cc in zip(p.vertices,normals,conc):
            n=mul(n,flip);cx,cy,cz=int(v[0]//cell),int(v[1]//cell),int(v[2]//cell);count=0
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    for dz in (-1,0,1):
                        for oj,w in grid.get((cx+dx,cy+dy,cz+dz),()):
                            if oj!=pi and (w[0]-v[0])**2+(w[1]-v[1])**2+(w[2]-v[2])**2<R*R:count+=1
            ao=min(1.0,max(min(1.0,count/22.0),cc*.95,groove(v) if n[0]>.35 else 0.0))
            lit=max(0.0,sum(a*b for a,b in zip(n,KEY)))*.58+max(0.0,sum(a*b for a,b in zip(n,FILL)))*.14+.14+.10*max(0.0,n[2])
            shade=max(0.0,min(1.0,lit*(1-.7*ao)))
            glow=max(0.0,min(1.0,(-n[2]-.05)*1.5))*(1-.5*ao)
            pa.append(round(glow*32)/32);pv.append(round(shade*64)/64)
        p.pa,p.pv=pa,pv


def geometry():
    parts=attach('ifrit',build_parts(),weights)
    for p in parts:
        if p.name=='Connected_skin':p.role='skin';p.pa=[0]*len(p.vertices);p.pv=[0]*len(p.vertices)
    bake_skin(parts)
    for p in parts:
        p.uv=[materials.uv(p.role,a,b) for a,b in zip(p.pa,p.pv)]
        p.vertices=[(min(31.5,max(-31.5,x)),min(31.5,max(-31.5,y)),max(.05,z)) for x,y,z in p.vertices]
    return assemble(parts,None)


# ---------------------------------------------------------------- motion
def qrot(ax,deg):return axis(ax,math.radians(deg))
def chain(*qs):
    q=(0,0,0,1)
    for x in qs:q=qmul(q,x)
    return q
def smooth(x):
    q=min(1,max(0,x));return q*q*(3-2*q)
def bump(t,c,w):return math.cos(min(1,abs(t-c)/w)*math.pi/2)**2
def lerp(a,b,t):return tuple(x+(y-x)*t for x,y in zip(a,b))
X,Y,Z=(1,0,0),(0,1,0),(0,0,1)


class Pose:
    def __init__(self):self.q={};self.d={}
    def rot(self,bone,*qs):self.q[bone]=chain(self.q.get(bone,(0,0,0,1)),*qs)
    def move(self,bone,d):self.d[bone]=add(self.d.get(bone,(0,0,0)),mul(d,K))


def arm_pose(P,n,s,pitch=0,abduct=0,elbow=0,twist=0,wrist=0,wrist_roll=0):
    P.rot(f'sh_{n}',qrot(Y,-pitch),qrot(X,s*abduct),qrot(Z,twist))
    P.rot(f'el_{n}',qrot(Y,-elbow))
    P.rot(f'wr_{n}',qrot(Y,-wrist),qrot(X,s*wrist_roll))


REST_DIRS={n:(unit(sub(mirror(EL,q),mirror(SH,q))),unit(sub(mirror(WR,q),mirror(EL,q))),unit(sub(blade_path(q)[1],blade_path(q)[0]))) for n,q in (('L',-1),('R',1))}
SLASH_DIRS=((.42,.01,-.91),(.79,.15,.59),(.2,.3,-.93))   # blades chop down into a low, wide V
WIND_DIRS=((.2,.26,-.94),(.5,.08,.86),(-.84,-.12,.54))    # blades cocked back before the chop
ARC_DIRS=((.56,.65,-.52),(.63,-.77,.1),(-.05,-.46,-.89))  # blades sweep forward and inward through the arc
def slash_keys():return [(0,None),(.16,WIND_DIRS),(.40,ARC_DIRS),(.54,SLASH_DIRS),(.68,ARC_DIRS),(.90,None),(1,None)]
DROP_DIRS=((.1,.3,-.95),(.1,.0,.3),(-.9,-.3,.2))          # the blades drop back rather than out to the sides
FLAT_DIRS=((.0,.35,-.94),(.0,.0,-1.0),(.1,-.95,-.2))     # collapsed: arms and blades lie along the body
COLLAPSE=(-13.5,11.3,-30,-10,95.1,0)                      # hips x shift, spine, neck, head pitch and hips pitch at the floor
FLY_DIRS=((-.15,.5,-.85),(.0,.05,1.0),(-.5,.1,.86))        # arms tucked back, blades trailing the fast flight
CAST_DIRS=((-.36,-.33,-.87),(.76,-.51,.41),(-.01,.87,.5))  # discord: torso rears back, blades fling out level in a wide T
def cast_keys():return [(0,None),(.24,None),(.54,CAST_DIRS),(.72,CAST_DIRS),(.94,None),(1,None)]


def keyed_dirs(t,keys):
    for (t0,d0),(t1,d1) in zip(keys,keys[1:]):
        if t<=t1:
            u=smooth((t-t0)/(t1-t0)) if t1>t0 else 1
            a=d0 if d0 else REST_DIRS['R'];b=d1 if d1 else REST_DIRS['R']
            return tuple(tuple(x+(y-x)*u for x,y in zip(a[k],b[k])) for k in range(3))
    return keys[-1][1] or REST_DIRS['R']


def aim(P,n,s,dirs):
    """Aim upper arm, forearm and blade along torso-space directions (right-arm values; left mirrors y)."""
    from .skeletal import between
    rest=REST_DIRS[n];want=[unit((d[0],d[1]*s,d[2])) for d in dirs]
    q_sh=between(rest[0],want[0]);Q_el=between(rest[1],want[1]);Q_wr=between(rest[2],want[2])
    P.rot(f'sh_{n}',q_sh);P.rot(f'el_{n}',qmul(inverse(q_sh),Q_el));P.rot(f'wr_{n}',qmul(inverse(Q_el),Q_wr))


def burst_target(k,t):
    """Chest-space (unscaled) position of ember fleck k in the discord swirl."""
    th=math.tau*k/BURST+math.tau*.6*t
    return (20*math.cos(th)+4,26*math.sin(th),-13+2.6*k)


def pose(name,t):
    P=Pose();w=math.tau*t
    def tail(amp_y,amp_z,phase=0,lean=0):
        for k,b in enumerate(('t1','t2','t3')):P.rot(b,qrot(Y,lean+amp_y*math.sin(w-.7*k)),qrot(Z,amp_z*(1+.35*k)*math.sin(w-.9*k+phase)))
    if name=='idle':
        P.move('hips',(0,0,1.3*math.sin(w)));P.rot('hips',qrot(Y,2.5*math.sin(w+.5)),qrot(Z,2*math.sin(w)))
        P.rot('spine',qrot(Y,1.5*math.sin(w+.9)));P.rot('chest',qrot(Y,-1.5*math.sin(2*w)));P.rot('neck',qrot(Z,4*math.sin(w+1.0)))
        P.rot('head',qrot(Z,5*math.sin(w+1.0)),qrot(Y,2.5*math.sin(w+2)))
        tail(4,13)
        for s,n in ((-1,'L'),(1,'R')):
            arm_pose(P,n,s,3*math.sin(w+(.6 if s>0 else 0)),2.5*math.sin(w+1),2*math.sin(w),0,2.5*math.sin(w+1.3),3*math.sin(w))
    elif name=='fly':
        P.move('hips',(0,0,1.6*abs(math.sin(2*w))));P.rot('hips',qrot(Y,16),qrot(Z,3*math.sin(2*w)))
        P.rot('spine',qrot(Y,6));P.rot('neck',qrot(Y,-8));P.rot('head',qrot(Z,3*math.sin(2*w)))
        for k,b in enumerate(('t1','t2','t3')):P.rot(b,qrot(Y,18),qrot(Z,16*(1+.3*k)*math.sin(2*w-.9*k)))
        for s,n in ((-1,'L'),(1,'R')):
            aim(P,n,s,tuple(tuple(x+.05*math.sin(2*w+k) for x in d) for k,d in enumerate(FLY_DIRS)))
    elif name=='slash':
        wind=bump(t,.2,.2);strike=bump(t,.54,.2)
        P.move('hips',(-3*wind+4*strike,0,-2*strike));P.rot('hips',qrot(Y,-6*wind+18*strike))
        P.rot('spine',qrot(Z,-10*wind+12*strike),qrot(Y,-3*wind+6*strike));P.rot('head',qrot(Y,-6*strike))
        for k,b in enumerate(('t1','t2','t3')):P.rot(b,qrot(Y,8*strike+6*wind),qrot(Z,10*math.sin(w*2-.9*k)*.3))
        for s,n in ((-1,'L'),(1,'R')):aim(P,n,s,keyed_dirs(t,slash_keys()))
    elif name=='discord':
        cast=bump(t,.6,.24)*min(1,1.1);e=smooth(min(1,max(0,(t-.2)/.28)))*(1-smooth((t-.72)/.22))
        P.move('hips',(-2*e,0,-1.0*e));P.rot('hips',qrot(Y,-14*e));P.rot('spine',qrot(Y,-8*e),qrot(Z,6*math.sin(w*2)*e))
        P.rot('chest',qrot(Y,-4*e));P.rot('neck',qrot(Y,-6*e));P.rot('head',qrot(Y,-6*e))
        for k,b in enumerate(('t1','t2','t3')):P.rot(b,qrot(Y,-6*e),qrot(Z,16*math.sin(w*3-.9*k)*e))
        for s,n in ((-1,'L'),(1,'R')):aim(P,n,s,keyed_dirs(t,cast_keys()))
        for k in range(BURST):
            rest=sub(BURST_REST[k],(1.5,0,42));tgt=burst_target(k,t);rel=sub(tgt,rest)
            # each fleck leaves the chest in turn, so the swirl builds outward
            f=smooth(min(1,max(0,(e*1.25-k*.02))))
            P.move(f'burst_{k}',mul(rel,f))
    elif name=='recoil':
        g=bump(t,.5,.5);sh=math.sin(t*math.pi*4)*g
        P.move('hips',(-4*g,2*sh,-1.5*g));P.rot('hips',qrot(Y,-12*g),qrot(Z,6*sh));P.rot('spine',qrot(Y,-7*g));P.rot('neck',qrot(Y,-5*g));P.rot('head',qrot(Y,-3*g),qrot(Z,8*sh))
        for k,b in enumerate(('t1','t2','t3')):P.rot(b,qrot(Y,-10*g),qrot(Z,12*sh))
        for s,n in ((-1,'L'),(1,'R')):arm_pose(P,n,s,-10*g,10*g,8*g,0,-10*g,0)
    elif name=='collapse':
        stag=bump(t,.16,.16);fall=smooth((t-.22)/.5);curl=smooth((t-.45)/.5);settle=smooth((t-.72)/.28)
        hx,sp,nk,hd,hp,yaw=COLLAPSE
        P.move('hips',(hx*fall-3*stag,0,-13*fall+2*stag));P.rot('hips',qrot(Z,yaw*fall),qrot(Y,-14*stag+hp*fall))
        P.rot('spine',qrot(Y,sp*fall));P.rot('neck',qrot(Y,nk*fall));P.rot('head',qrot(Y,hd*fall),qrot(Z,14*curl))
        P.rot('t1',qrot(Y,-40*fall),qrot(Z,60*curl));P.rot('t2',qrot(Y,-14*fall),qrot(Z,66*curl));P.rot('t3',qrot(Z,60*curl))
        for s,n in ((-1,'L'),(1,'R')):
            aim(P,n,s,keyed_dirs(t,[(0,None),(.08,None),(.2,DROP_DIRS),(.36,FLAT_DIRS),(1,FLAT_DIRS)]))
            # the ember-forged edges gutter out: the strips sink into the blades
            P.move(f'edge_{n}',(3.4*settle,0,0))
        P.move('eye_L',(-3.4*settle,0,0));P.move('eye_R',(-3.4*settle,0,0));P.move('crown',(0,0,-10.5*settle))
    else:raise KeyError(name)
    rows=[]
    for b,(nm,parent,local) in enumerate(BONES):
        d=P.d.get(nm,(0,0,0));q=P.q.get(nm,(0,0,0,1))
        rows.append((*(round(l+e,6) for l,e in zip(local,d)),*q,1,1,1))
    return rows


def matrices(frame):return RIG.matrices(frame)
def deform(v,w,frame):return RIG.deform(v,w,frame)
def animation_data(v,w):return sample_clips(RIG,CLIPS,pose,v,w)
def texture_bytes():return materials.texture_bytes()


def build():
    skin=texture_bytes();(ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts,v,n,uv,t,w=geometry();clips,bounds=animation_data(v,w)
    data=iqm.encode(v,n,uv,t,w,BONES,clips,bounds,mesh_label='Project_Broom_ifrit',material_path=SKIN)
    path=ROOT/MODEL;path.write_bytes(data)
    manifest=dict(schemaVersion=1,workId='BRG-M64',format='IQM v2',runtimeModel=MODEL,
        sha256=hashlib.sha256(data).hexdigest(),skin=SKIN,skinSha256=hashlib.sha256(skin).hexdigest(),
        dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],
        parts=len(parts),vertices=len(v),triangles=len(t),boneCount=len(BONES),
        bones=[dict(name=n_,parent=p,local=l) for n_,p,l in BONES],
        clips=[{k:x for k,x in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],
        poseBounds=bounds,emberShader='shaders/ifrit-embers.fp',
        authoringSource='assets/monsters/ifrit/ifrit-animated.blend')
    out=ROOT/'assets/monsters/ifrit';out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__':
    from tools.monster_models import ifrit_animation as _self
    print(_self.build()['sha256'])

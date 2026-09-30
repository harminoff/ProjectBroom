"""Original mangrove dryad for Brogue's MK_ANCIENT_SPIRIT (presentation only).

Brogue: "This mangrove dryad is as old as the earth, and its gnarled figure houses an ancient
power. When angered, it can call upon the forces of nature to bind its foes and tear them to
shreds." It is drawn in tanColor: weathered khaki bark, wide in value (dark fissures, pale ridges).

The model is a twisted, spirally fluted bark trunk held up by eight knobbly prop roots that leave
the trunk high above the floor, bow outward in arches with open gaps beneath, fork once and plant
wide. Trunk, burls, long thin gnarled arms with twig fingers and the roots are one fused connected
skin; head (heavy brow over deep sunken glowing eyes, splintered mouth), crown of bare twisted
branches with a few leaves, moss, broken shoulder stubs, bark shards and the two vine lashes at the
arm tips are rigid attachments. Skin light is baked from the geometry (see `bake_skin`). Brogue owns
melee, the vines bolt, movement and timing; this file only draws.
"""
import hashlib,json,math
from . import iqm
from .rat import ROOT,Part,add,sub,mul,cross,unit,spline
from .skeletal import Rig,axis,qmul,inverse,rotate,assemble,sample_clips,between
from . import mangrove_dryad_materials as materials
from .connected_skin import attach
from .flame_turret_materials import noise

SKIN='graphics/BRGDRYAD.png'
MODEL='mod/BrogueDoom/models/monsters/67_mangrove_dryad.iqm'
SKIN_VOXEL_SIZE=.3
SKIN_FACE_BUDGET=16000


def CONNECTED_SKIN(name):
    """Trunk, burls, arms, twig fingers and prop roots fuse into one skin; everything else is a rigid attachment."""
    return name.startswith('skin_')


def mirror(p,s):return (p[0],p[1]*s,p[2])


HIPS=(0,0,24);SPINE=(0,0,33);CHEST=(1,0,42);NECK=(2,0,51);HEADB=(3.5,0,56)
HC=(3.5,0,57.4)
SH=(0,9.5,46.5);EL=(2.5,16.5,38.5);WR=(6.5,20.5,30.5);V1=(9.5,22.5,23.5);V2=(13,23,16.5);V3=(17.5,21.5,9.5);TIP=(23,17.5,2.5)
ARM_PTS=[SH,EL,WR,V1,V2,V3,TIP]
# (angle, planted radius, height where the root leaves the trunk): irregular, not a ring
ROOTS=[(38,22,30),(-40,20,27),(80,26,42),(-84,25,34),(122,25,44),(-128,23,37),(165,21,31),(-166,25,41)]
FORKS=[(0,1),(2,-1),(3,1),(5,-1),(6,1),(4,1)]
CROWN0=[
    [(-1,-2,61,2.4),(-3,-5,66,2.0),(-5,-7,71,1.4),(-6,-8.5,75,.8),(-5,-9,77.5,.25)],
    [(1,3,61.5,2.0),(0,6,64,1.6),(-1,9,65.5,1.0),(-1,11.5,64,.3)],
    [(1,-3,61,2.0),(0,-7,63,1.7),(1,-11,63.5,1.1),(3,-14.5,61,.3)],
    [(-1,0,61,2.4),(-5,1,64.5,1.8),(-8.5,3,67,1.1),(-11,3.5,68.5,.3)],
    [(2.5,3,61.5,1.5),(3.5,5,64.5,1.0),(2.4,6,67,.5),(1.4,6.4,68.5,.15)],
    [(-2,-3,60,1.8),(-6,-8,61,1.3),(-9,-12,59,.7),(-9.5,-15,55.5,.2)],
]


def lowered(ctl):return [(x,y,61+(z-61)*.62,r) for x,y,z,r in ctl]
CROWN=[lowered(c) for c in CROWN0]


def polar(rho,ang,z):a=math.radians(ang);return (rho*math.cos(a),rho*math.sin(a),z)


def root_ctrl(k):
    """Quarter-ellipse arch: leaves the trunk horizontally at height zs, bows outward, lands vertically at radius R."""
    ang,R,zs=ROOTS[k];sg=1 if k%2 else -1;pts=[]
    for a_,rad,off in ((0,3.8,0),(28,3.3,4),(52,2.8,-8),(74,2.6,7),(90,1.7,0)):
        a=math.radians(a_);pts.append((4+(R-4)*math.sin(a),1.7+(zs-1.7)*math.cos(a),rad,off*sg))
    return [(*polar(r,ang+off,z),rad) for r,z,rad,off in pts]


def fork_ctrl(k,sgn):
    ang,R,zs=ROOTS[k];pts=spline(root_ctrl(k),3);p0=pts[7]
    tip=polar(min(R*.98,26.5),ang+sgn*(24+3*k%3),1.6);mid=add(mul(add(p0[:3],tip),.5),(0,0,3.5))
    return [(*p0[:3],1.9),(*mid,1.5),(*tip,1.1)]


TRUNK=[(18,0,0,8.6,8.8),(24,0,-.8,7.6,8.0),(30,.2,1.2,7.0,7.4),(36,.6,-1.4,7.6,8.6),(42,1.0,.8,8.6,10.0),(46,1.4,-.8,9.0,10.6),
       (49.5,1.8,1.0,7.8,8.6),(52,2.2,0,5.8,6.2),(55,2.6,0,4.6,4.8)]
RIBS=((.24,5,.16,0),(.13,8,-.22,1.3),(.08,3,.07,.6))
SHARDS=[(1.0,-1.5,32),(-1.0,1.8,35),(1.5,1.0,38),(-1.5,-1.2,41),(.5,2.0,44),(1.0,-2.2,36),(-.5,-.4,30),(1.6,.2,42),(-1.2,1.0,39)]

SPECS=[('root',None,(0,0,0)),('hips','root',HIPS),('spine','hips',SPINE),('chest','spine',CHEST),('neck','chest',NECK),('head','neck',HEADB),
       ('eye_L','head',(9.2,-3.2,58.2)),('eye_R','head',(9.2,3.2,58.2))]
SPECS+=[(f'cr_{k}','head',tuple(c[:3] for c in CROWN[k])[1]) for k in range(len(CROWN))]
for s,n in ((-1,'L'),(1,'R')):
    SPECS+=[(f'sh_{n}','chest',mirror(SH,s)),(f'el_{n}',f'sh_{n}',mirror(EL,s)),(f'wr_{n}',f'el_{n}',mirror(WR,s)),
            (f'v1_{n}',f'wr_{n}',mirror(V1,s)),(f'v2_{n}',f'v1_{n}',mirror(V2,s)),(f'v3_{n}',f'v2_{n}',mirror(V3,s))]
for k,(ang,R,zs) in enumerate(ROOTS):
    c=root_ctrl(k)
    SPECS+=[(f'ra_{k}','hips',c[2][:3]),(f'rb_{k}',f'ra_{k}',(*polar(R-1.2,ang,2.2),))]
SPECS+=[(f'shard_{k}','spine',p) for k,p in enumerate(SHARDS)]
RIG=Rig.from_world(SPECS);BONES,REST=RIG.bones,RIG.rest
IDS={n:i for i,(n,_,_) in enumerate(BONES)}
CLIPS=[('idle',48,24,True),('stride',32,35,True),('lash',26,35,False),('vines',28,35,False),('recoil',14,35,False),('collapse',40,35,False)]


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


def tube(name,controls,role,sides=10,samples=3,flatten=1.0,up=(0,0,1),rib=None,twist=0.0):
    """Swept ellipse; controls (x,y,z,radius). rib=(amplitude,lobes) flutes the bark. Paint: a around, v along."""
    p=Piece(name,role);pts=spline(controls,samples) if samples>1 else [tuple(c) for c in controls];rows=[]
    for i,(c,r,n,bn) in enumerate(tube_frames(pts,up)):
        u=i/(len(pts)-1);row=[]
        for j in range(sides+1):
            th=math.tau*j/sides;m=1.0
            if rib:m=1+rib[0]*math.cos(rib[1]*th+twist*u*math.tau)
            row.append(p.add(add(c,add(mul(n,r*m*math.cos(th)),mul(bn,r*m*flatten*math.sin(th)))),j/sides,u))
        rows.append(row)
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


def oval(name,centre,major,front,radii,role,seg=14,rings_=8):
    """Flattened ellipsoid: radii = (along `major`, across it in the surface plane, thickness along `front`)."""
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


def rloft(name,sections,role,sides=36,ribs=()):
    """Elliptic sections (z,cx,cy,rx,ry) fluted by spiralling ribs (amp,lobes,twist per unit z): gnarled trunk."""
    p=Piece(name,role);pts=spline(sections,3);rows=[]
    for i,(z,cx,cy,rx,ry) in enumerate(pts):
        u=i/(len(pts)-1);row=[]
        for j in range(sides+1):
            th=math.tau*j/sides;m=1+sum(a*math.cos(k*th+tw*z+ph) for a,k,tw,ph in ribs)
            row.append(p.add((cx+rx*m*math.cos(th),cy+ry*m*math.sin(th),z),j/sides,u))
        rows.append(row)
    rings(p,rows)
    return p


def dirvec(yaw,pitch):
    y,p=math.radians(yaw),math.radians(pitch);return (math.cos(p)*math.cos(y),math.cos(p)*math.sin(y),math.sin(p))


def weights(part,v,uv):
    return part.wfn(v)


def build_parts():
    out=[]
    def finish(p,bone=None,chain=None):
        p.vertices=[tuple(round(c,6) for c in v) for v in p.vertices]
        p.uv=[(a,b) for a,b in zip(p.pa,p.pv)]
        if chain:
            ids=[IDS[c] for c in chain];p.wfn=lambda v,ids=ids:quantize(RIG.chain_weights(v,ids))
        else:p.wfn=lambda v,b=IDS[bone]:[(b,1)]
        p.skin_weights=[p.wfn(v) for v in p.vertices]
        out.append(p);return p
    trunk=['hips','spine','chest','neck']
    # ---- fused trunk: spiralling fibre ridges, burls, a knot hollow on the chest, asymmetric shoulders
    finish(rloft('skin_trunk',TRUNK,'skin',36,RIBS),chain=trunk)
    for name,c,r,bone in (('skin_burl_b',(6.6,5.6,30.8),(3.6,3.0,2.6),'spine'),
                          ('skin_burl_c',(-6.6,3.4,40.0),(4.4,4.4,3.8),'spine'),('skin_burl_d',(4.2,-9.4,45.4),(3.0,3.2,2.6),'chest'),
                          ('skin_burl_f',(-2.6,-7.2,34.0),(3.8,3.4,3.6),'spine'),('skin_burl_g',(-3.6,9.4,46.4),(5.2,4.4,4.0),'chest'),
                          ('skin_burl_h',(3.0,8.4,49.6),(3.6,3.2,2.6),'chest'),('skin_burl_i',(5.2,-6.6,28.4),(2.8,2.6,3.6),'spine'),
                          ('skin_rim_a',(7.0,-4.4,38.6),(2.6,1.6,4.8),'spine'),('skin_rim_b',(7.2,2.0,38.0),(2.4,1.5,4.4),'spine')):
        finish(ball(name,c,r,'skin',12,7),bone)
    finish(ball('hollow',(7.3,-1.2,38.2),(1.8,2.9,4.2),'dark',12,8),'spine')
    finish(tube('skin_stub',[(-4,-7.5,38,3.0),(-7.6,-11.5,41.6,2.4),(-10,-14.4,44,1.7)],'skin',8,3,1,(0,0,1),(.16,3),.5),'spine')
    # ---- prop roots: knobbly arches leaving the trunk high, bowing out and down, forking once
    for k in range(len(ROOTS)):
        finish(tube(f'skin_root_{k}',root_ctrl(k),'skin',10,3,.95,(0,0,1),(.24,5),1.4),chain=['hips',f'ra_{k}',f'rb_{k}'])
    for j,(k,sgn) in enumerate(FORKS):
        finish(tube(f'skin_fork_{j}',fork_ctrl(k,sgn),'skin',8,3,.95,(0,0,1),(.2,4),.8),chain=['hips',f'ra_{k}',f'rb_{k}'])
    # ---- long thin gnarled arms: knotted joints, twig fingers
    for s,n in ((-1,'L'),(1,'R')):
        sh,el,wr=(mirror(q,s) for q in (SH,EL,WR));mid=mul(add(sh,el),.5)
        finish(tube(f'skin_upper_arm_{n}',[(*sh,3.5),(*add(mid,(1.6,s*1.2,.6)),2.6),(*el,2.2)],'skin',9,3,1,(0,0,1),(.22,3),1.4),chain=[f'sh_{n}',f'el_{n}'])
        finish(ball(f'skin_elbow_{n}',el,(3.2,3.2,3.1),'skin',12,7),f'el_{n}')
        finish(ball(f'skin_knot_{n}',add(mid,(1.6,s*1.2,.6)),(2.9,2.7,2.7),'skin',10,6),f'sh_{n}')
        finish(tube(f'skin_forearm_{n}',[(*el,2.2),(*add(mul(add(el,wr),.5),(-1.2,s*1.0,0)),1.9),(*wr,1.6)],'skin',8,3,1,(0,0,1),(.22,3),-1.2),chain=[f'el_{n}',f'wr_{n}'])
        finish(ball(f'skin_wrist_{n}',wr,(2.5,2.5,2.4),'skin',10,6),f'wr_{n}')
        for j,(ty,tz,ln) in enumerate(((.7,1.5,1),(-.1,-.2,1.2),(-.8,-1.6,.95))):
            a1=(wr[0]+2.8*ln,wr[1]+s*ty*1.9,wr[2]+tz*2.0);a2=(wr[0]+6.0*ln,wr[1]+s*ty*3.8,wr[2]+tz*4.0)
            finish(tube(f'skin_finger_{n}_{j}',[(*wr,1.3),(*a1,.95),(*a2,.55),(a2[0]+3.0*ln,a2[1]+s*ty*1.4,a2[2]-1.2+tz,.3)],'skin',5,2,1,(0,0,1)),f'wr_{n}')
    # ---- head (rigid): angular skull, heavy overhanging brow, sunk slit eyes, ridged nose, splintered mouth, knotted chin
    hd=lambda p,b='head':finish(p,b)
    hd(ball('head_skull',HC,(5.7,5.1,6.5),'skin',22,11))
    hd(ball('head_forehead',(5.8,0,62.4),(3.4,4.6,2.2),'skin',12,7))
    for s in (-1,1):
        hd(oval(f'head_brow_{s}',(8.2,3.3*s,60.4),(0,s*math.cos(.35),math.sin(.35)),(1,0,0),(3.9,1.9,1.9),'skin',12,7))
        hd(ball(f'head_brow_knot_{s}',(7.0,5.2*s,59.4),(2.4,2.0,1.6),'skin',10,6))
        hd(oval(f'head_cheek_{s}',(6.4,4.6*s,54.6),(0,s*.6,-.8),(1,0,0),(3.0,2.0,1.4),'skin',10,6))
        hd(ball(f'head_socket_{s}',(7.4,3.3*s,58.0),(2.0,2.8,2.1),'dark',12,7))
        hd(ball(f'head_temple_{s}',(3.0,5.4*s,58.5),(3.0,1.6,3.6),'skin',10,6))
        finish(oval(f'eye_{s}',(8.9,3.4*s,58.0),(0,s*math.cos(.4),math.sin(.4)),(1,0,0),(1.7,.75,.6),'glow',10,6),'eye_L' if s<0 else 'eye_R')
    hd(tube('head_nose',[(8.2,0,60.0,1.6),(9.4,0,56.6,2.0),(9.0,0,54.4,2.5)],'skin',9,3,.9))
    hd(ball('head_nose_knot',(9.2,0,54.8),(2.0,2.4,1.6),'skin',10,6))
    hd(ball('head_mouth',(8.2,0,52.2),(1.6,3.6,.85),'dark',12,6))
    hd(ball('head_lip_up',(8.0,0,53.4),(1.5,3.7,.9),'skin',12,6))
    hd(ball('head_lip_low',(7.6,0,51.3),(1.6,3.5,.9),'skin',12,6))
    hd(ball('head_chin',(6.0,0,49.6),(2.6,2.6,2.3),'skin',10,6))
    for i in range(5):
        y=-2.6+i*1.3;hd(tube(f'head_tooth_up_{i}',[(8.9,y,53.0,.5),(9.2,y,51.2-(.6 if i%2 else 0),.05)],'splinter',5,1))
    for i in range(4):
        y=-2.0+i*1.3;hd(tube(f'head_tooth_low_{i}',[(8.5,y,51.3,.5),(9.0,y,52.9,.05)],'splinter',5,1))
    # ---- asymmetric crown of bare twisted branches, many small forks, a few leaves, a trailing moss strand
    leaf_at=[]
    for k,ctl in enumerate(CROWN):
        chain_=['head',f'cr_{k}']
        finish(tube(f'crown_{k}',ctl,'skin',7,4,1.0,(0,0,1),(.16,3),1.0),chain=chain_)
        pts=spline(ctl,4);tip=ctl[-1][:3]
        for j,(frac,sg,ln) in enumerate(((.4,1,4.4),(.55,-1,5.0),(.7,1,4.2),(.85,-1,3.4))):
            base=pts[int(len(pts)*frac)];d=unit(sub(tip,base));side=unit(cross(d,(0,0,1)))
            e=add(base,add(mul(d,ln*.8),mul(side,sg*ln*.75)));e=(e[0],e[1],e[2]+.9*ln*.3)
            finish(tube(f'twig_{k}_{j}',[(*base,.95-.12*j),(*add(mul(add(base,e),.5),(0,0,.4)),.55),(*e,.12)],'skin',5,3),chain=chain_)
            if (j==1 and k%2==0) or (j==2 and k in (1,3)):leaf_at.append((k,e,side,sg))
        leaf_at.append((k,tip,unit(cross(unit(sub(tip,pts[-3])),(0,0,1))),1))
    for i,(k,pt,side,sg) in enumerate(leaf_at):
        major=unit(add(side,(0,0,.35*(-1)**i)))
        finish(oval(f'leaf_{i}',add(pt,mul(major,1.4)),major,(0,0,1),(1.8,.9,.2),'leaf',8,5),f'cr_{k}')
    t5=CROWN[5][-1]
    finish(tube('moss_trail',[(t5[0],t5[1],t5[2],.9),(t5[0]-.6,t5[1]-.6,t5[2]-6,.75),(t5[0]-1.0,t5[1]-1.2,t5[2]-12,.45),(t5[0]-1.4,t5[1]-1.6,t5[2]-17,.1)],'moss',6,3),chain=['head','cr_5'])
    for i,(x,y,z) in enumerate(((3.5,-5.6,62.0),(-2.0,6.0,61.0),(5.6,6.6,60.5))):
        finish(tube(f'moss_{i}',[(x,y,z,1.0),(x-.6,y*1.08,z-3.2,.8),(x-1.1,y*1.14,z-6.4,.15)],'moss',6,3),'head')
    # ---- one short broken stub on the big-burl (right) shoulder, bent outward and back
    finish(tube('stub_R',[(-3.0,9.5,47.5,3.0),(-5.6,12.8,49.6,2.5),(-7.6,15.4,50.8,2.0)],'skin',7,3,1,(0,0,1),(.16,3),1.0),'chest')
    finish(tube('stub_tip_R',[(-7.6,15.4,50.6,1.8),(-8.6,16.6,51.8,1.0),(-9.4,17.4,52.8,.2)],'splinter',5,2),'chest')
    # ---- vine lashes (rigid): thin, sinuous, thorned
    for s,n in ((-1,'L'),(1,'R')):
        base=[mirror(q,s) for q in (WR,V1,V2,V3,TIP)];radii=(1.9,1.55,1.2,.85,.3)
        pts=[add(q,(1.3*math.sin(i*2.1)*(i>0),0,0)) for i,q in enumerate(base)]
        chain_=[f'wr_{n}',f'v1_{n}',f'v2_{n}',f'v3_{n}']
        finish(tube(f'vine_{n}',[(*q,r) for q,r in zip(pts,radii)],'vine',8,4,1.0,(0,0,1),None),chain=chain_)
        for j,(pt,out_) in enumerate(((pts[1],(0,s,.35)),(pts[2],(.3,s,.35)),(pts[3],(.45,s,.3)))):
            o=unit(out_);b0=add(pt,mul(o,radii[j+1]*.8))
            finish(tube(f'thorn_{n}_{j}',[(*b0,.6),(*add(b0,mul(o,2.8)),.05)],'splinter',5,1),chain=chain_)
    # ---- bark shards: hidden inside the trunk until the collapse throws them onto the floor
    for k,(x,y,z) in enumerate(SHARDS):
        finish(tube(f'shard_{k}',[(x,y,z-3.4,.3),(x,y,z,1.2),(x,y,z+3.4,.2)],'splinter',5,1,.5),f'shard_{k}')
    return out


# ---------------------------------------------------------------- baked skin light
KEY=unit((.55,.25,.8));FILL=unit((-.45,-.55,.35))
HOLES=[((9.6,-1.2,38.2),3.8),((-9.0,-1.5,40.0),3.0),((7.4,5.6,27.6),2.4),((-3.0,9.6,48.0),2.0)]


def concavity(p,normals):
    """Crevice measure per vertex: mean sine of the angle to 2-ring neighbours (positive in grooves)."""
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
        out.append(max(0.0,min(1.0,total/count*3.4)) if count else 0.0)
    return [out[r] for r in ids]


def section(z):
    """Interpolated trunk ellipse (cx,rx,ry) at height z."""
    pts=TRUNK
    for (z0,c0,_,rx0,ry0),(z1,c1,_,rx1,ry1) in zip(pts,pts[1:]):
        if z<=z1:
            u=max(0.0,(z-z0)/(z1-z0));return (c0+(c1-c0)*u,rx0+(rx1-rx0)*u,ry0+(ry1-ry0)*u)
    return (pts[-1][1],pts[-1][3],pts[-1][4])


def flute(v):
    """Darkness in the troughs of the trunk's spiralling ribs, computed from the same formula as the geometry."""
    x,y,z=v
    if not 18<z<56:return 0.0
    cx,rx,ry=section(z);qx,qy=(x-cx)/rx,y/ry;rr=math.hypot(qx,qy)
    if not .8<rr<1.3:return 0.0
    th=math.atan2(qy,qx)%math.tau
    m=sum(a*math.cos(k*th+tw*z+ph) for a,k,tw,ph in RIBS)
    return max(0.0,min(1.0,(-m-.0)/.16))


_RF=[]


def root_frames():
    if not _RF:
        for k in range(len(ROOTS)):
            pts=spline(root_ctrl(k),3);_RF.append([(c,r,n,bn,i/(len(pts)-1)) for i,(c,r,n,bn) in enumerate(tube_frames(pts,(0,0,1)))])
    return _RF


def root_rib(v):
    """(trough, crest) of the fluting on the nearest prop root, from the same formula that shapes it."""
    best=None
    for fr in root_frames():
        for c,r,n,bn,u in fr:
            d=math.dist(v,c)
            if best is None or d<best[0]:best=(d,c,r,n,bn,u)
    d,c,r,n,bn,u=best
    if d>r*1.8+1.0:return 0.0,0.0
    dv=sub(v,c);th=math.atan2(sum(a*b for a,b in zip(dv,bn))/.95,sum(a*b for a,b in zip(dv,n)))%math.tau
    m=.24*math.cos(5*th+1.4*math.tau*u)
    return max(0.0,min(1.0,-m/.2)),max(0.0,min(1.0,(m-.03)/.18))


def ridge(v):
    """Pale crest of the same ribs (0..1)."""
    x,y,z=v
    if not 18<z<56:return 0.0
    cx,rx,ry=section(z);qx,qy=(x-cx)/rx,y/ry;rr=math.hypot(qx,qy)
    if not .85<rr<1.35:return 0.0
    th=math.atan2(qy,qx)%math.tau;m=sum(a*math.cos(k*th+tw*z+ph) for a,k,tw,ph in RIBS)
    return max(0.0,min(1.0,(m-.03)/.15))


def face_cracks(v):
    """Vertical bark cracks over the brow and cheeks, and deep creases under the brow."""
    x,y,z=v
    if x<3.5 or not 49<z<66:return 0.0
    g=0.0
    for k,y0 in enumerate((-3.8,-1.6,.4,2.2,4.0)):
        yy=y0+.7*math.sin(z*.9+k*1.7);g=max(g,max(0.0,1-abs(y-yy)/.35)*(.85 if z>60.6 else .5 if z>53 else .0))
    g=max(g,max(0.0,1-abs(z-59.4)/.55)*(1.0 if abs(y)>1.6 and x>6 else 0.0))
    return g


def fissure(v):
    """Dark cracks, ribs and knot holes painted as extra occlusion (design units)."""
    x,y,z=v;g=max(flute(v),face_cracks(v))
    if 27<z<50 and abs(y)<11:
        for off,ph in ((-3.4,0),(3.0,1.7)):
            cy=off+1.6*math.sin(z*.31+ph);g=max(g,max(0.0,1-abs(y-cy)/.6)*(.8 if x>3 else .4))
    for c,r in HOLES:
        d=math.dist(v,c);g=max(g,max(0.0,1-d/r)**.7*.95)
    return min(1.0,g)


def bake_skin(parts):
    """Per-vertex shade (pv) and moss (pa) for every 'skin' part, from geometry alone."""
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
            ao=min(1.0,max(min(1.0,count/24.0)*.8,cc*1.0,fissure(v)))
            lit=max(0.0,sum(a*b for a,b in zip(n,KEY)))*.62+max(0.0,sum(a*b for a,b in zip(n,FILL)))*.14+.16+.10*max(0.0,n[2])
            ang=math.atan2(v[1],v[0]);grain=noise(ang*3.2+v[2]*.03,v[2]*.35,61)
            rt,rc=root_rib(v) if (v[2]<46 and math.hypot(v[0],v[1])>7.5) else (0.0,0.0)
            ao=max(ao,rt*.9);rg=max(ridge(v),rc)
            under=max(0.0,-n[2]-.15)*(1.0 if 14<v[2]<44 else .3)
            shade=lit*(1-.88*ao)*(.62+.8*grain)*(1-(.9 if v[2]<30 else .55)*under)+.26*rg*(1-ao)
            shade=max(0.0,min(1.0,(shade*1.5)**1.05))
            moss=max(0.0,n[2])*max(0.0,noise(v[0]*.11,v[1]*.11+v[2]*.05,63)-.55)*2.0*(1.0 if v[2]<32 else .5)
            streak=noise(v[0]*.9+v[1]*.8+v[2]*.02,v[2]*.09+v[0]*.05,65)
            pa.append(round((.9+.1*min(1.0,moss*1.5))*64)/64 if moss>.12 else round(streak*.86*64)/64);pv.append(round(shade*64)/64)
        p.pa,p.pv=pa,pv


def geometry():
    parts=attach('mangrove_dryad',build_parts(),weights)
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
X,Y,Z=(1,0,0),(0,1,0),(0,0,1)


class Pose:
    def __init__(self):self.q={};self.d={};self.delta={}
    def rot(self,bone,*qs):self.q[bone]=chain(self.q.get(bone,(0,0,0,1)),*qs)
    def move(self,bone,d):self.d[bone]=add(self.d.get(bone,(0,0,0)),d)


REST_SEG=[unit(sub(b,a)) for a,b in zip(ARM_PTS,ARM_PTS[1:])]
ARM_BONES=['sh','el','wr','v1','v2','v3']
ROOT_TAN=[(-math.sin(math.radians(a)),math.cos(math.radians(a)),0) for a,_,_ in ROOTS]
ROOT_RAD=[(math.cos(math.radians(a)),math.sin(math.radians(a)),0) for a,_,_ in ROOTS]
FRONT=[k for k,(a,_,_) in enumerate(ROOTS) if abs(a)<70]
SNAP=(1,4,6)


def aim(P,n,s,dirs):
    """Aim the six arm segments along chest-space directions (right-arm values; the left arm mirrors y)."""
    want=[unit((d[0],d[1]*s,d[2])) for d in dirs];prev=(0,0,0,1)
    for i,b in enumerate(ARM_BONES):
        rest=(REST_SEG[i][0],REST_SEG[i][1]*s,REST_SEG[i][2]);Q=between(rest,want[i])
        P.rot(f'{b}_{n}',qmul(inverse(prev),Q));prev=Q


def blend(keys,t):
    for (t0,d0),(t1,d1) in zip(keys,keys[1:]):
        if t<=t1:
            u=smooth((t-t0)/(t1-t0)) if t1>t0 else 1
            return [unit(tuple(x+(y-x)*u for x,y in zip(a,b))) for a,b in zip(d0,d1)]
    return keys[-1][1]


def D(*yp):return [dirvec(y,p) for y,p in yp]
def P_(*pts):
    """Segment directions of an arm path through six points after the shoulder (chest space, right arm)."""
    path=[SH,*pts];return [unit(sub(b,a)) for a,b in zip(path,path[1:])]
REST_ARM=[tuple(d) for d in REST_SEG]
WIND_R=D((10,50),(130,40),(165,30),(-175,20),(-150,6),(-120,-5))
WIND_L=D((15,48),(135,38),(170,28),(-170,18),(-145,6),(-115,-5))
STRIKE_R=D((60,3),(90,3),(50,5),(-80,3),(-20,0),(-120,0))
FLING_L=D((40,50),(110,45),(160,35),(-175,22),(-150,8),(-120,-5))
CAST_R=P_((6,13,38),(12.5,14.5,31.5),(18,14.5,25.5),(22,14,19),(25,13.5,12),(27,13,4))
CAST_UP=P_((2,12,54),(0,14,62),(-4,15,67),(-9,13,68),(-13,10,66),(-16,6,62))
TUCK=D((10,-60),(-20,-45),(-60,-20),(-100,0),(-140,20),(180,40))
FLAT_R=D((30,-20),(105,-8),(160,-4),(-175,-3),(-150,-2),(-120,-1))


def waves(P,w,amp,lag=.9,axis_=Z):
    for s,n in ((-1,'L'),(1,'R')):
        for k,b in enumerate(('v1','v2','v3')):
            P.rot(f'{b}_{n}',qrot(axis_,amp*(1+.3*k)*math.sin(w-lag*k+(0 if s>0 else 1.7))))


def crown_sway(P,w,amp=3.0,extra=0.0,tilt=0.0):
    for k in range(len(CROWN)):
        P.rot(f'cr_{k}',qrot(Y,amp*math.sin(w+.9*k)+extra),qrot(X,amp*.8*math.sin(w+1.3*k)+tilt))


def pin_roots(P):
    """Keep every root pinned to its planted world position whatever the trunk does (roots stretch, feet stay put)."""
    hq=P.q.get('hips',(0,0,0,1));hp=add(HIPS,P.d.get('hips',(0,0,0)));ih=inverse(hq)
    for k in range(len(ROOTS)):
        nm=f'ra_{k}';i=IDS[nm];want=add(REST[i],P.delta.get(k,(0,0,0)))
        P.d[nm]=sub(rotate(ih,sub(want,hp)),BONES[i][2]);P.q[nm]=qmul(ih,P.q.get(nm,(0,0,0,1)))


def torso_q(P):
    q=(0,0,0,1)
    for b in ('hips','spine','chest'):q=qmul(q,P.q.get(b,(0,0,0,1)))
    return q


def aim_world(P,n,s,dirs,u):
    """Blend the arm from rest to world-space directions (lying on the floor) with weight u, whatever the torso does."""
    ic=inverse(torso_q(P));rest=[(d[0],d[1]*s,d[2]) for d in REST_SEG]
    tgt=[rotate(ic,unit((d[0],d[1]*s,d[2]))) for d in dirs]
    want=[unit(tuple(x+(y-x)*u for x,y in zip(r,t))) for r,t in zip(rest,tgt)]
    prev=(0,0,0,1)
    for i,b in enumerate(ARM_BONES):
        Q=between(rest[i],want[i]);P.rot(f'{b}_{n}',qmul(inverse(prev),Q));prev=Q


SHARD_FLOOR=[(math.radians(a),r) for a,r in ((20,19),(75,26),(130,17),(190,24),(245,20),(300,27),(345,15),(40,12),(160,10))]


def place_shards(rows,u):
    """Throw the hidden bark shards from the trunk onto the floor: world-space arcs blended by u."""
    if u<=0:return
    mats=RIG.matrices(rows)
    for k in range(len(SHARDS)):
        i=IDS[f'shard_{k}'];pl,pq=mats[BONES[i][1]];ang,r=SHARD_FLOOR[k]
        W=(r*math.cos(ang),r*math.sin(ang),1.5+16*4*u*(1-u)*(1-.3*k/9))
        Qw=qmul(axis(Z,ang*2.3),axis(Y,math.pi/2+.25*math.sin(k)))
        tl=rotate(inverse(pq),sub(W,pl));tq=qmul(inverse(pq),Qw)
        row=rows[i];loc=tuple(a+(b-a)*u for a,b in zip(row[:3],tl))
        q=tuple(a+(b-a)*u for a,b in zip(row[3:7],tq if sum(x*y for x,y in zip(row[3:7],tq))>=0 else tuple(-x for x in tq)))
        n_=math.sqrt(sum(x*x for x in q));rows[i]=(*loc,*(x/n_ for x in q),1,1,1)


def pose(name,t):
    P=Pose();w=math.tau*t;shard_u=0.0
    if name=='idle':
        P.move('hips',(0,0,.5*math.sin(w)));P.rot('hips',qrot(Y,1.2*math.sin(w+.5)),qrot(Z,1.5*math.sin(w)))
        P.rot('spine',qrot(Y,1.5*math.sin(w+.9)),qrot(Z,2*math.sin(w+.4)));P.rot('chest',qrot(Y,-1.5*math.sin(2*w)));P.rot('neck',qrot(Z,4*math.sin(w+1.0)))
        P.rot('head',qrot(Z,6*math.sin(w+1.0)),qrot(Y,2.5*math.sin(w+2)))
        crown_sway(P,w,2.5);waves(P,w,7,1.0)
        for s,n in ((-1,'L'),(1,'R')):
            P.rot(f'sh_{n}',qrot(Y,-2.5*math.sin(w+(.6 if s>0 else 0))),qrot(X,s*2*math.sin(w+1)))
            P.rot(f'el_{n}',qrot(Y,2*math.sin(w)))
        for k in range(len(ROOTS)):P.rot(f'rb_{k}',axis(ROOT_TAN[k],math.radians(2.5*math.sin(w+k))))
    elif name=='stride':
        bob=abs(math.sin(w));P.move('hips',(1.0*math.sin(w),0,1.2*bob));P.rot('hips',qrot(Y,4),qrot(Z,4*math.sin(w)))
        P.rot('spine',qrot(Z,-5*math.sin(w)),qrot(Y,-2));P.rot('neck',qrot(Y,-3));P.rot('head',qrot(Z,3*math.sin(w+.5)))
        crown_sway(P,w*2,3.0,-3)
        for k,(ang,R,zs) in enumerate(ROOTS):
            ph=w+math.pi*(k%2)+(0 if k<4 else .5);lift=max(0,math.sin(ph))
            P.rot(f'ra_{k}',axis(ROOT_TAN[k],math.radians(-3*lift)))
            P.move(f'rb_{k}',(2.2*lift*ROOT_RAD[k][0],2.2*lift*ROOT_RAD[k][1],2.4*lift))
        for s,n in ((-1,'L'),(1,'R')):
            ph=w+(0 if s>0 else math.pi)
            P.rot(f'sh_{n}',qrot(Y,-3*math.sin(ph)-1.5),qrot(X,s*1));P.rot(f'el_{n}',qrot(Y,-2-1.5*math.sin(ph)))
        waves(P,w*2,6,.9)
    elif name=='lash':
        wind=bump(t,.2,.2);strike=bump(t,.5,.2)
        P.move('hips',(-1*wind+.5*strike,-1.5*strike,-1.5*strike))
        P.rot('hips',qrot(Y,-3*wind+5*strike),qrot(X,-7*strike),qrot(Z,-2*strike));P.rot('spine',qrot(Z,8*wind-14*strike),qrot(Y,-3*wind+6*strike),qrot(X,-6*strike))
        P.rot('chest',qrot(Z,6*wind-6*strike),qrot(X,-4*strike));P.rot('neck',qrot(Z,6*strike),qrot(Y,-3*strike));P.rot('head',qrot(Z,6*strike),qrot(X,4*strike))
        crown_sway(P,w*2,1.6,-3*strike+3*wind,-26*strike)
        aim(P,'R',1,blend([(0,REST_ARM),(.07,TUCK),(.24,WIND_R),(.36,TUCK),(.47,STRIKE_R),(.53,STRIKE_R),(.64,TUCK),(.94,REST_ARM),(1,REST_ARM)],t))
        aim(P,'L',-1,blend([(0,REST_ARM),(.07,TUCK),(.2,WIND_L),(.5,FLING_L),(.62,FLING_L),(.72,WIND_L),(.84,TUCK),(.94,REST_ARM),(1,REST_ARM)],t))
        if strike>.05:
            # S-curve through the air: the vine bones alternate their bend
            for k,b in enumerate(('v1','v2','v3')):P.rot(f'{b}_R',qrot(Y,(-1)**k*8*strike))
        for k in range(len(ROOTS)):P.rot(f'ra_{k}',axis(ROOT_TAN[k],math.radians(-5*strike*(1 if abs(ROOTS[k][0])<90 else -1))))
    elif name=='vines':
        rear=bump(t,.22,.22);cast=bump(t,.52,.2)
        P.move('hips',(-2*rear+1.2*cast,0,-1.0*cast));P.rot('hips',qrot(Y,-5*rear+9*cast))
        P.rot('spine',qrot(Y,-4*rear+8*cast));P.rot('neck',qrot(Y,-3*rear+5*cast));P.rot('head',qrot(Y,-4*rear+4*cast),qrot(Z,3*math.sin(w*2)*cast))
        crown_sway(P,w*3,2.4,-6*cast+5*rear)
        for s,n in ((-1,'L'),(1,'R')):
            aim(P,n,s,blend([(0,REST_ARM),(.07,TUCK),(.24,CAST_UP),(.42,TUCK),(.54,CAST_R),(.72,CAST_R),(.86,TUCK),(.96,REST_ARM),(1,REST_ARM)],t))
        waves(P,w*3,14*cast,.9,Y)
        for k in range(len(ROOTS)):
            reach=cast if k in FRONT else .35*cast
            P.rot(f'ra_{k}',axis(ROOT_TAN[k],math.radians((-20 if k in FRONT else 8)*reach)))
            P.move(f'rb_{k}',(3*reach*ROOT_RAD[k][0],3*reach*ROOT_RAD[k][1],6*reach if k in FRONT else 0))
    elif name=='recoil':
        g=bump(t,.5,.5);sh_=math.sin(t*math.pi*4)*g
        P.move('hips',(-3*g,2*sh_,-1*g));P.rot('hips',qrot(Y,-9*g),qrot(Z,5*sh_));P.rot('spine',qrot(Y,-6*g))
        P.rot('neck',qrot(Y,-5*g));P.rot('head',qrot(Y,-4*g),qrot(Z,8*sh_));crown_sway(P,w*4,3.5,-5*g)
        for s,n in ((-1,'L'),(1,'R')):
            P.rot(f'sh_{n}',qrot(Y,-8*g),qrot(X,s*5*g));P.rot(f'el_{n}',qrot(Y,6*g))
        waves(P,w*3,8*g,.9)
    elif name=='collapse':
        stag=bump(t,.12,.12);fall=smooth((t-.18)/.55);settle=smooth((t-.7)/.3);lie=smooth((t-.3)/.4);shard_u=smooth((t-.34)/.5)
        P.move('hips',(-12*fall-2*stag,0,-15*fall+1.5*stag));P.rot('hips',qrot(Y,-8*stag+24*fall))
        P.rot('spine',qrot(Y,40*fall+8*settle));P.rot('chest',qrot(Y,24*fall+8*settle));P.rot('neck',qrot(Y,10*fall+14*settle));P.rot('head',qrot(Y,10*settle),qrot(Z,18*settle))
        for k in range(len(CROWN)):P.rot(f'cr_{k}',qrot(Y,-60*fall),qrot(X,(-1)**k*22*settle))
        for s_,n in ((-1,'L'),(1,'R')):aim_world(P,n,s_,FLAT_R,lie)
        for k in range(len(ROOTS)):
            rz=REST[IDS[f'ra_{k}']][2];rad=ROOT_RAD[k]
            if k in SNAP:
                ex=min(5.0,29-ROOTS[k][1]);P.delta[k]=add(mul(rad,(ex+2)*fall),(0,0,(3.5-rz)*fall));tipd=mul(rad,ex*fall)
            else:
                P.delta[k]=add(mul(rad,-7*fall-2*settle),(0,0,(6-rz)*fall));tipd=mul(rad,-4*fall)
            P.move(f'rb_{k}',sub(tipd,P.delta[k]))
            P.rot(f'rb_{k}',axis(ROOT_TAN[k],math.radians((-8 if k in SNAP else -20)*settle)),qrot(Z,(-1)**k*(6 if k in SNAP else 24)*settle))
        P.move('eye_L',(-3*settle,0,0));P.move('eye_R',(-3*settle,0,0))
    else:raise KeyError(name)
    pin_roots(P)
    rows=[]
    for b,(nm,parent,local) in enumerate(BONES):
        d=P.d.get(nm,(0,0,0));q=P.q.get(nm,(0,0,0,1))
        rows.append((*(round(l+e,6) for l,e in zip(local,d)),*q,1,1,1))
    place_shards(rows,shard_u)
    return rows


def matrices(frame):return RIG.matrices(frame)
def deform(v,w,frame):return RIG.deform(v,w,frame)
def animation_data(v,w):return sample_clips(RIG,CLIPS,pose,v,w)
def texture_bytes():return materials.texture_bytes()


def build():
    skin=texture_bytes();(ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts,v,n,uv,t,w=geometry();clips,bounds=animation_data(v,w)
    data=iqm.encode(v,n,uv,t,w,BONES,clips,bounds,mesh_label='Project_Broom_ancient_spirit',material_path=SKIN)
    path=ROOT/MODEL;path.write_bytes(data)
    manifest=dict(schemaVersion=1,workId='BRG-M67',format='IQM v2',runtimeModel=MODEL,
        sha256=hashlib.sha256(data).hexdigest(),skin=SKIN,skinSha256=hashlib.sha256(skin).hexdigest(),
        dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],
        parts=len(parts),vertices=len(v),triangles=len(t),boneCount=len(BONES),
        bones=[dict(name=n_,parent=p,local=l) for n_,p,l in BONES],
        clips=[{k:x for k,x in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],
        poseBounds=bounds,authoringSource='assets/monsters/mangrove_dryad/mangrove-dryad-animated.blend')
    out=ROOT/'assets/monsters/mangrove_dryad';out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__':
    from tools.monster_models import mangrove_dryad_animation as _self
    print(_self.build()['sha256'])

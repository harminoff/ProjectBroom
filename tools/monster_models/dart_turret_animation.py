"""Original wall-mounted spring gun for Brogue's dart turret (presentation only).

A diamond blackened-iron plate carries forged yoke brackets and trunnion pins.
On them pivots a violet-enamelled launcher: breech block, guide rods, a sliding
crosshead with a striker, two exposed tension coil springs, a short open
launching channel with a spurred brass muzzle collar, a slatted magazine hopper
of poison-tipped darts, a violet poison vial with a drip spout, and a side
ratchet, pawl and cocking lever. The chamber dart sits in an affine corner cage
so it stays attached, can shrink to a point at the muzzle and re-form hidden in
the hopper throat with unit bone scales. Brogue owns the dart bolt, poison,
weakness, targets and timing; nothing here is a projectile or an outcome.
"""
import hashlib,json,math
from . import iqm,dart_turret_materials as materials
from .rat import ROOT,Part,add,sub,mul,cross,unit
from .skeletal import Rig,axis,qmul,rotate,assemble,sample_clips

SKIN='graphics/BRGDTUR.png'
AXIS_Z=22.0              # launch axis height
PIVOT=(-5.0,0,AXIS_Z)    # trunnion axis (head bone)
BACK=-10.0               # rear plane on the wall face
DART_LEN=13.6
DART_X0=7.2              # chamber dart nock at rest
THROAT_Z=25.1            # hidden re-forming height inside the closed hopper throat
STACK_X0=9.6;STACK_Z=(27.5,29.4,31.3)
SPRING_Y=6.8;SPRING_REAR=-0.8;SPRING_FRONT=19.0
SHOT=7.2                 # crosshead and striker travel
LID_HINGE=(6.6,0,33.4)
BEAD_C=(23.4,0,33.0);BEAD_R=.55
DART_BOX=(7.0,21.0,-1.2,1.2,AXIS_Z-1.2,AXIS_Z+1.2)
BEAD_BOX=(22.8,24.0,-.62,.62,32.35,33.65)
SPECS=[('root',None,(0,0,0)),('head','root',PIVOT),('crosshead','head',(-2.0,0,AXIS_Z)),
       ('hook_L','crosshead',(SPRING_REAR,SPRING_Y,AXIS_Z)),('hook_R','crosshead',(SPRING_REAR,-SPRING_Y,AXIS_Z)),
       ('lever','head',(-5.0,-8.9,AXIS_Z)),('pawl','root',(-6.8,-7.7,26.3)),('lid','head',LID_HINGE)]
for cage,parent,box in (('dart','head',DART_BOX),('bead','lid',BEAD_BOX)):
    for z in range(2):
        for y in range(2):
            for x in range(2):SPECS.append((f'{cage}_{z}{y}{x}',parent,(box[x],box[2+y],box[4+z])))
RIG=Rig.from_world(SPECS);BONES,REST=RIG.bones,RIG.rest
IDS={n:i for i,(n,_,_) in enumerate(BONES)}
CLIPS=[('idle',40,20,True),('rest',20,20,True),('loose',24,35,False),('snap',28,35,False),('jar',14,35,False),('jam',36,35,False)]
LIGHT=unit((.42,0,.91))


def quantize(weights):
    """Round to 1e-6; the last influence takes the exact remainder."""
    weights=[(b,w) for b,w in weights if w>5e-7]
    head=[(b,round(w,6)) for b,w in weights[:-1]]
    rows=head+[(weights[-1][0],round(1-sum(w for _,w in head),6))]
    return [(b,w) for b,w in rows if w>0]


def cage_weights(prefix,box,v):
    """Freudenthal simplex weights in a corner cage: four affine-exact influences."""
    f=[min(1,max(0,(v[a]-box[2*a])/(box[2*a+1]-box[2*a]))) for a in range(3)]
    order=sorted(range(3),key=lambda a:(f[a],-a),reverse=True);corners=[(0,0,0)];corner=[0,0,0]
    for a in order:corner=corner.copy();corner[a]=1;corners.append(tuple(corner))
    amounts=[1-f[order[0]],f[order[0]]-f[order[1]],f[order[1]]-f[order[2]],f[order[2]]]
    return quantize([(IDS[f'{prefix}_{z}{y}{x}'],w) for (x,y,z),w in zip(corners,amounts)])


class Piece(Part):
    """Part with material role and painting parameters; UVs are finished later."""
    def __init__(self,name,role,mode='shade'):
        super().__init__(name);self.role=role;self.mode=mode;self.pa=[];self.pv=[]
    def add(self,co,a=0,v=0):
        self.vertices.append(tuple(round(c,6) for c in co));self.pa.append(a);self.pv.append(v);return len(self.vertices)-1


def geometry():
    parts=[]
    def put(p,bone='root',weights=None):
        p.bone=bone
        p.skin_weights=[weights(v) for v in p.vertices] if weights else [[(IDS[bone],1)]]*len(p.vertices)
        parts.append(p);return p
    def rings(p,rows,closed_start=True,closed_end=True):
        """rows: vertex-index lists (equal length, last duplicates first for the UV seam)."""
        point=lambda row:len({p.vertices[i] for i in row})==1
        for r0,r1 in zip(rows,rows[1:]):
            for j in range(len(r0)-1):
                # A collapsed pole row gets triangles, never zero-area quad halves.
                if point(r0):p.faces.append((r0[j],r1[j+1],r1[j]))
                elif point(r1):p.faces.append((r0[j],r0[j+1],r1[j]))
                else:p.faces.append((r0[j],r0[j+1],r1[j+1],r1[j]))
        for ring,rev in ((rows[0],True),(rows[-1],False)):
            if (closed_start if rev else closed_end) and not point(ring):
                c=[p.vertices[i] for i in ring[:-1]];center=p.add(tuple(sum(x)/len(c) for x in zip(*c)),p.pa[ring[0]],.5)
                for j in range(len(ring)-1):p.faces.append((center,ring[j+1],ring[j]) if rev else (center,ring[j],ring[j+1]))
    def lathe(name,profile,role,center,ax='x',sides=24,bone='root',caps=(True,True),weights=None,start=0,build_only=False):
        """Surface of revolution; profile entries are (along, radius)."""
        p=Piece(name,role);lengths=[0]
        for a,b in zip(profile,profile[1:]):lengths.append(lengths[-1]+math.dist(a,b))
        rows=[]
        for (s,r),l in zip(profile,lengths):
            row=[]
            for j in range(sides+1):
                t=start+math.tau*j/sides;c,sn=r*math.cos(t),r*math.sin(t)
                if ax=='x':co=(center[0]+s,center[1]+c,center[2]+sn)
                elif ax=='y':co=(center[0]+sn,center[1]+s,center[2]+c)
                else:co=(center[0]+c,center[1]+sn,center[2]+s)
                row.append(p.add(co,l/lengths[-1],j/sides))
            rows.append(row)
        rings(p,rows,caps[0] and profile[0][1]>0,caps[1] and profile[-1][1]>0)
        return p if build_only else put(p,bone,weights)
    def sweep(name,pts,role,radius,sides=8,bone='root',weights=None,up=(0,0,1)):
        """Tube along explicit centreline points with parallel-transport frames."""
        p=Piece(name,role);rows=[];prev=None;L=[0]
        for a,b in zip(pts,pts[1:]):L.append(L[-1]+math.dist(a,b))
        for i,c in enumerate(pts):
            t=unit(sub(pts[min(i+1,len(pts)-1)],pts[max(0,i-1)]))
            if prev is None:n=unit(cross(t,up if abs(sum(a*b for a,b in zip(t,up)))<.9 else (0,1,0)))
            else:n=unit(sub(prev,mul(t,sum(a*b for a,b in zip(prev,t)))))
            prev=n;bn=unit(cross(t,n));r=radius(i/(len(pts)-1)) if callable(radius) else radius
            rows.append([p.add(add(c,add(mul(n,r*math.cos(math.tau*j/sides)),mul(bn,r*math.sin(math.tau*j/sides)))),L[i]/L[-1],j/sides) for j in range(sides+1)])
        rings(p,rows)
        return put(p,bone,weights)
    def ball(name,c,r,role,bone='root',seg=10,rings_=5,weights=None):
        p=Piece(name,role);rows=[]
        for i in range(rings_+1):
            ph=-math.pi/2+math.pi*i/rings_;row=[]
            for j in range(seg+1):
                th=math.tau*j/seg
                row.append(p.add((c[0]+r[0]*math.cos(ph)*math.cos(th),c[1]+r[1]*math.cos(ph)*math.sin(th),c[2]+r[2]*math.sin(ph)),j/seg,i/rings_))
            rows.append(row)
        rings(p,rows,False,False)
        return put(p,bone,weights)
    def prism(name,outline,depth,role,frame=((1,0,0),(0,1,0),(0,0,1)),bevel=.4,bone='root',weights=None,origin=(0,0,0)):
        """Star-shaped outline (s,t) extruded along frame[0] from depth[0] to depth[1] with a chamfered front."""
        p=Piece(name,role);d0,d1=depth;ex,ey,ez=frame
        cs=sum(s for s,t in outline)/len(outline);ct=sum(t for s,t in outline)/len(outline)
        smin=min(s for s,t in outline);smax=max(s for s,t in outline);tmin=min(t for s,t in outline);tmax=max(t for s,t in outline)
        def at(d,s,t):return add(origin,add(add(mul(ex,d),mul(ey,s)),mul(ez,t)))
        def inset(s,t,k):
            L=math.hypot(s-cs,t-ct);return (s-(s-cs)/L*k,t-(t-ct)/L*k) if L>1e-9 else (s,t)
        per=[0]
        for a,b in zip(outline+outline[:1],outline[1:]+outline[:1]):per.append(per[-1]+math.dist(a,b))
        layers=[(d0,0),(d1-bevel,0),(d1,bevel)] if bevel>0 else [(d0,0),(d1,0)];rows=[]
        for k,(d,ins) in enumerate(layers):
            row=[]
            for (s,t),l in zip(outline+outline[:1],per):
                s2,t2=inset(s,t,ins);row.append(p.add(at(d,s2,t2),l/per[-1],.15+.35*k))
            rows.append(row)
        for r0,r1 in zip(rows,rows[1:]):
            for j in range(len(r0)-1):p.faces.append((r0[j],r0[j+1],r1[j+1],r1[j]))
        for ring,d,rev,ins in ((rows[0],d0,True,0),(rows[-1],d1,False,layers[-1][1])):
            cap=[]
            for s,t in outline:
                s2,t2=inset(s,t,ins);cap.append(p.add(at(d,s2,t2),(s2-smin)/(smax-smin),(tmax-t2)/(tmax-tmin)))
            c=p.add(at(d,cs,ct),(cs-smin)/(smax-smin),(tmax-ct)/(tmax-tmin));m=len(cap)
            for j in range(m):p.faces.append((c,cap[(j+1)%m],cap[j]) if rev else (c,cap[j],cap[(j+1)%m]))
        return put(p,bone,weights)
    def box(name,lo,hi,role,bone='root',bevel=.3,axis_='x',weights=None):
        """Axis-aligned chamfered box; its chamfered face points along +axis_."""
        frames={'x':((1,0,0),(0,1,0),(0,0,1)),'-x':((-1,0,0),(0,-1,0),(0,0,1)),'y':((0,1,0),(0,0,1),(1,0,0)),'-y':((0,-1,0),(1,0,0),(0,0,1)),
                'z':((0,0,1),(1,0,0),(0,1,0)),'-z':((0,0,-1),(1,0,0),(0,-1,0))}
        ex,ey,ez=frames[axis_];dot=lambda a,b:sum(x*y for x,y in zip(a,b))
        def rng(e):
            vals=[dot(e,lo),dot(e,hi)];return min(vals),max(vals)
        s0,s1=rng(ey);t0,t1=rng(ez);d0,d1=rng(ex)
        return prism(name,[(s0,t0),(s1,t0),(s1,t1),(s0,t1)],(d0,d1),role,(ex,ey,ez),min(bevel,(d1-d0)*.45),bone,weights=weights)
    def dart(prefix,x0,y0,z0,roll,bone='head',weights=None):
        """Steel dart along +X: nock, shaft, brass ferrule, barbed poison-dipped head, four flights."""
        prof=[(0,0),(0,.3),(.35,.36),(9.4,.3),(9.55,.44),(10.25,.44),(10.4,.5),(11.5,.64),(11.62,.3),(DART_LEN,0)]
        p=lathe(prefix+'_shaft',[(x0+s,r) for s,r in prof],'dart',(0,y0,z0),'x',10,bone,weights=weights,start=roll)
        for k in range(4):
            a=roll+k*math.pi/2;rad=(0,math.cos(a),math.sin(a));nrm=(0,-math.sin(a),math.cos(a))
            outline=[(x0+.3,.28),(x0+3.6,.28),(x0+2.2,1.08),(x0+.5,1.08)]
            prism(f'{prefix}_flight_{k}',outline,(-.07,.07),'flight',(nrm,(1,0,0),rad),0,bone,weights,origin=(0,y0,z0))
        return p

    # ---- Fixed mount (root): diamond blackened-iron plate, enamel panel, rivets, anchors.
    diamond=[(-3,5.0),(3,5.0),(16.5,21.5),(16.5,26.5),(3,43.0),(-3,43.0),(-16.5,26.5),(-16.5,21.5)]
    prism('diamond_backplate',diamond,(BACK,-8.1),'plate',bevel=.7)
    inner=[(s*.78,24+(t-24)*.78) for s,t in diamond]
    prism('enamel_plate_panel',inner,(-8.1,-7.55),'panel',bevel=.3)
    ring_pts=[]
    for (a,b),(c,d) in zip(diamond,diamond[1:]+diamond[:1]):
        L=math.dist((a,b),(c,d));n=max(1,round(L/3.6))
        for k in range(n):ring_pts.append((a+(c-a)*k/n,b+(d-b)*k/n))
    for k,(s,t) in enumerate(ring_pts):
        ball(f'plate_rivet_{k}',(-8.0,s*.9,24+(t-24)*.9),(.45,.55,.55),'bolt',seg=8,rings_=4)
    for k,(y,z) in enumerate(((0,9.6),(0,38.6),(12.6,24),(-12.6,24))):
        lathe(f'anchor_washer_{k}',[(0,0),(0,1.9),(.3,1.9),(.4,1.6),(.4,0)],'steel',(-7.55,y,z),sides=16)
        lathe(f'anchor_hex_bolt_{k}',[(0,1.3),(1.0,1.3),(1.2,1.0),(1.25,0)],'bolt',(-7.15,y,z),sides=6,start=math.pi/6)
    # Forged yoke brackets carry the trunnion pins; a braced cradle pad sits under the breech.
    for side,s in (('L',1),('R',-1)):
        prism(f'yoke_bracket_{side}',[(-7.55,14.6),(-4.2,19.2),(-3.4,22.0),(-4.2,24.8),(-7.55,29.4)],(-5.6,-4.2) if s>0 else (4.2,5.6),'plate',
              ((0,-1,0),(1,0,0),(0,0,1)),.2)
        for k,(x,z) in enumerate(((-6.8,16.6),(-6.8,27.4))):ball(f'yoke_rivet_{side}_{k}',(x,s*5.72,z),(.35,.3,.35),'bolt',seg=8,rings_=4)
        if s>0:lathe(f'trunnion_boss_{side}',[(0,0),(0,1.55),(.5,1.55),(.6,1.3),(.6,0)],'brass',(-5.0,5.6,AXIS_Z),'y',16)
        else:lathe(f'trunnion_boss_{side}',[(0,0),(0,1.3),(.1,1.55),(.6,1.55),(.6,0)],'brass',(-5.0,-6.2,AXIS_Z),'y',16)
    sweep('cradle_strut',[(-7.55,0,12.6),(-6.6,0,14.8),(-5.9,0,17.4)],'plate',.7,8)
    box('cradle_pad',(-6.5,-2.6,17.6),(-5.1,2.6,18.55),'steel',axis_='z',bevel=.15)
    # Pawl on a root stud engages the launcher's ratchet (it ticks in idle).
    sweep('pawl_stud',[(-6.8,-5.55,26.3),(-6.8,-8.3,26.3)],'bolt',.35,8)
    prism('ratchet_pawl',[(-7.2,25.9),(-4.95,24.35),(-4.7,24.55),(-6.4,26.7),(-7.2,26.8)],(7.45,7.95),'steel',((0,-1,0),(1,0,0),(0,0,1)),.1,'pawl')

    # ---- Launcher (head): breech block, trunnion pins, ratchet wheel, guide rods.
    box('breech_block',(-6.2,-4.4,19.05),(-2.8,4.4,25.0),'enamel','head',.45)
    for s in (-1,1):
        box(f'breech_strap_{s}',(-5.4,-4.55,s*3.2+AXIS_Z-.4),(-3.6,4.55,s*3.2+AXIS_Z+.4),'brass','head',.12,'z' if s>0 else '-z')
        sweep(f'trunnion_pin_{s}',[(-5.0,s*4.3,AXIS_Z),(-5.0,s*7.35,AXIS_Z)],'steel',.7,10,'head')
        lathe(f'guide_rod_{s}',[(-2.8,.42),(6.2,.42)],'steel',(0,s*3.0,AXIS_Z),'x',10,'head')
    lathe('trunnion_cap_L',[(7.35,0),(7.35,1.0),(7.7,1.0),(7.9,.7),(7.95,0)],'brass',(-5.0,0,AXIS_Z),'y',12,'head')
    teeth=[]
    for k in range(24):
        a=math.tau*k/24;r=2.05 if k%2==0 else 2.45
        teeth.append((-5.0+r*math.cos(a),AXIS_Z+r*math.sin(a)))
    prism('ratchet_wheel',teeth,(7.35,8.1),'brass',((0,-1,0),(1,0,0),(0,0,1)),.12,'head')
    # Cocking lever on the outboard end of the trunnion, with a hardwood grip.
    lathe('lever_hub',[(0,0),(0,1.1),(1.2,1.1),(1.2,0)],'steel',(-5.0,-9.4,AXIS_Z),'y',12,'lever')
    box('lever_arm',(-5.55,-9.25,AXIS_Z),(-4.45,-8.55,AXIS_Z+8.2),'steel','lever',.12,'-y')
    lathe('lever_grip',[(0,0),(0,.62),(.4,.78),(2.6,.72),(3.0,.5),(3.1,0)],'wood',(-5.0,-8.9,AXIS_Z+7.6),'z',10,'lever')
    ball('lever_knob',(-5.0,-8.9,AXIS_Z+10.9),(.62,.62,.5),'brass','lever',8,4)

    # ---- Crosshead, striker and the two tension coil springs.
    box('sliding_crosshead',(-2.8,-7.45,21.0),(-1.2,7.45,23.0),'steel','crosshead',.25)
    lathe('striker_rod',[(-1.2,.45),(DART_X0-.05,.45),(DART_X0,.25)],'steel',(0,0,AXIS_Z),'x',10,'crosshead')
    for s,side in ((1,'L'),(-1,'R')):
        ball(f'crosshead_eye_{side}',(-1.0,s*SPRING_Y,AXIS_Z),(.55,.55,.55),'brass','hook_'+side,8,4)
        # Front post lugs with knurled brass tension knobs.
        box(f'spring_post_lug_{side}',(18.9,s*2.4 if s>0 else -7.9,21.3),(20.1,7.9 if s>0 else -2.4,22.7),'channel','head',.2,'y' if s>0 else '-y')
        if s>0:lathe(f'tension_knob_{side}',[(0,0),(0,1.15),(.9,1.15),(1.0,.8),(1.0,0)],'brass',(19.5,7.9,AXIS_Z),'y',14,'head')
        else:lathe(f'tension_knob_{side}',[(0,0),(0,.8),(.1,1.15),(1.0,1.15),(1.0,0)],'brass',(19.5,-8.9,AXIS_Z),'y',14,'head')
        turns=16;pts=[];N=turns*14
        for i in range(N+1):
            u=i/N;x=SPRING_REAR+(SPRING_FRONT-SPRING_REAR)*u;a=math.tau*turns*u
            r=1.3 if .03<u<.97 else 1.3*min(u,1-u)/.03*.6+.52
            pts.append((round(x,6),round(s*SPRING_Y+r*math.cos(a),6),round(AXIS_Z+r*math.sin(a),6)))
        pts=[(SPRING_REAR-.3,s*SPRING_Y,AXIS_Z)]+pts+[(SPRING_FRONT+.3,s*SPRING_Y,AXIS_Z)]
        def blend(v,side=side):
            f=min(1,max(0,(v[0]-SPRING_REAR)/(SPRING_FRONT-SPRING_REAR)))
            return quantize([(IDS['hook_'+side],1-f),(IDS['head'],f)])
        sweep(f'tension_spring_{side}',pts,'spring',.33,7,weights=blend,up=(1,0,0))

    # ---- Short open launching channel, breech ring and spurred brass muzzle collar.
    box('channel_floor',(6.5,-2.4,19.6),(22.4,2.4,20.8),'channel','head',.25)
    for s in (-1,1):
        box(f'channel_wall_{s}',(6.5,s*1.3 if s>0 else -2.4,20.8),(22.4,2.4 if s>0 else -1.3,23.8),'channel','head',.2,'z')
    lathe('breech_ring',[(0,.75),(0,2.5),(.6,2.6),(.9,2.3),(.9,.75),(0,.75)],'brass',(5.9,0,AXIS_Z),'x',20,'head',caps=(False,False))
    lathe('muzzle_collar',[(0,1.55),(0,3.1),(.35,3.35),(1.6,3.35),(2.0,3.0),(2.0,1.55),(1.2,1.45),(0,1.55)],'brass',(22.3,0,AXIS_Z),'x',24,'head',caps=(False,False))
    for k in range(6):
        a=math.pi/2+k*math.tau/6;ca,sa=math.cos(a),math.sin(a)
        sweep(f'muzzle_spur_{k}',[(24.1,2.55*ca,AXIS_Z+2.55*sa),(24.9,2.85*ca,AXIS_Z+2.85*sa),(25.7,3.2*ca,AXIS_Z+3.2*sa)],'steel',lambda u:.42*(1-u)+.02,6,'head')

    # ---- Magazine hopper: closed throat, posts, slats and the stacked dart feed.
    box('hopper_throat',(7.0,-2.9,23.8),(22.0,2.9,26.4),'enamel','head',.3)
    box('hopper_rear_wall',(7.0,-2.9,26.4),(7.7,2.9,32.4),'enamel','head',.2)
    for kx,x in enumerate((7.0,21.2)):
        for s in (-1,1):box(f'hopper_post_{kx}_{s}',(x,s*2.1 if s>0 else -2.9,26.4),(x+.8,2.9 if s>0 else -2.1,32.4),'brass','head',.15)
    for kz,z in enumerate((28.45,30.35)):
        for s in (-1,1):box(f'hopper_slat_{kz}_{s}',(7.7,s*2.45 if s>0 else -2.85,z-.22),(21.3,2.85 if s>0 else -2.45,z+.22),'steel','head',.08)
        box(f'hopper_front_bar_{kz}',(21.35,-2.2,z-.22),(21.85,2.2,z+.22),'steel','head',.08)
    box('hopper_floor_shadow',(7.7,-2.1,26.4),(21.2,2.1,26.6),'soot','head',.05,'z')
    for k,z in enumerate(STACK_Z):dart(f'stack_dart_{k}',STACK_X0,0,z,math.pi/4)
    # Hinged lid, poison vial, feed neck and drip spout with its hanging bead.
    box('hopper_lid',(6.6,-3.3,32.4),(22.4,3.3,33.4),'enamel','lid',.3,'z')
    box('lid_rim_band',(20.9,-3.4,32.3),(22.5,3.4,33.5),'brass','lid',.15)
    sweep('lid_hinge_knuckle',[(6.6,-3.0,33.4),(6.6,3.0,33.4)],'brass',.45,8,'head')
    vial=[(0,1.8),(.7,1.9),(.8,2.1),(1.9,2.45),(3.1,2.5),(4.3,2.2),(5.1,1.4),(5.5,.9),(6.6,.85),(6.7,0)]
    lathe('poison_vial',vial,'vial',(14.2,0,33.4),'z',20,'lid',caps=(False,True))
    lathe('vial_collar',[(-.05,2.15),(.85,2.2),(1.05,2.0),(-.05,2.0)],'brass',(14.2,0,33.4),'z',20,'lid',caps=(False,False))
    # Brass wire guard around the glass: four ribs and an equator hoop.
    for k in range(4):
        a=math.pi/4+k*math.pi/2
        rib=[(14.2+(r+.14)*math.cos(a),(r+.14)*math.sin(a),33.4+h) for h,r in vial[2:7]]
        sweep(f'vial_guard_rib_{k}',rib,'brass',.13,5,'lid')
    hoop=[(14.2+2.66*math.cos(math.tau*k/28),2.66*math.sin(math.tau*k/28),36.5) for k in range(29)]
    sweep('vial_guard_hoop',hoop,'brass',.14,5,'lid')
    lathe('vial_stopper',[(6.3,1.12),(7.3,1.2),(7.55,.95),(7.6,0)],'brass',(14.2,0,33.4),'z',12,'lid')
    sweep('drip_feed_line',[(16.6,0,34.2),(18.6,0,34.4),(20.6,0,34.35),(22.5,0,34.25),(23.4,0,34.05)],'brass',.26,7,'lid')
    sweep('drip_spout_tip',[(23.4,0,34.15),(23.4,0,33.6)],'brass',lambda u:.36-.12*u,8,'lid')
    ball('poison_bead',BEAD_C,(BEAD_R,BEAD_R,BEAD_R*1.1),'poison','lid',10,6,weights=lambda v:cage_weights('bead',BEAD_BOX,v))
    # Chamber dart in the channel; its corner cage keeps it attached.
    dart('chamber_dart',DART_X0,0,AXIS_Z,0,'head',weights=lambda v:cage_weights('dart',DART_BOX,v))
    finish_uvs(parts)
    return assemble(parts,lambda p,v,u:[(0,1)])


def finish_uvs(parts):
    for p in parts:
        normals=p.normals();p.uv=[]
        for i,(v,n) in enumerate(zip(p.vertices,normals)):
            light=.5+.5*sum(a*b for a,b in zip(n,LIGHT))
            ao=.16*min(1,max(0,(-5.2-v[0])/2.4))
            b=.04+.72*(1-light)+.08*(.5-.5*math.cos(math.tau*p.pv[i]))+ao
            p.uv.append(materials.uv(p.role,p.pa[i],b))


def pose(name,t):
    f=[[*local,0,0,0,1,1,1,1] for _,_,local in BONES]
    rot={}
    def turn(b,deg,ax=(0,1,0)):rot.setdefault(b,[]).append((ax,deg))
    def move(b,d):
        for a in range(3):f[IDS[b]][a]+=d[a]
    smooth=lambda x:(lambda q:q*q*(3-2*q))(min(1,max(0,x)))
    def bump(t,c,w):return 0.0 if abs(t-c)>=w else math.cos(abs(t-c)/w*math.pi/2)**2
    def cage(prefix,box_,parent,target):
        """target(corner)->head-space point; parent is the rest pivot of the cage bones' parent."""
        for z in range(2):
            for y in range(2):
                for x in range(2):
                    c=(box_[x],box_[2+y],box_[4+z]);f[IDS[f'{prefix}_{z}{y}{x}']][:3]=list(sub(target(c),parent))
    shot=0.0;head=0.0;lever=0.0;pawl=0.0;lid=0.0;hookL=(0,0,0);hookR=(0,0,0)
    dart=('rest',0.0);bead=1.0;bead_drop=0.0
    if name=='idle':
        # Pawl clicks over a ratchet tooth twice per loop; the poison bead slowly swells and eases.
        pawl=5*(bump(t,.25,.06)+bump(t,.75,.06));swell=.5-.5*math.cos(math.tau*t)
        bead=1+.14*swell;bead_drop=.16*swell
    elif name in ('loose','snap'):
        amp=SHOT if name=='loose' else 5.6
        rel=(.3,.42) if name=='loose' else (.38,.46)
        back=(.6,.8) if name=='loose' else (.62,.8)
        fire=smooth((t-rel[0])/(rel[1]-rel[0]));ret=smooth((t-back[0])/(back[1]-back[0]))
        shot=amp*fire*(1-ret)
        kick=bump(t,rel[1]+.04,.14)
        head=-2.6*kick if name=='loose' else 7.5*smooth((t-.08)/.3)*(1-smooth((t-.62)/.3))-2.0*kick
        buzz=math.sin(t*95)*bump(t,rel[1]+.08,.2)
        hookL=(0,.28*buzz,.34*buzz);hookR=(0,-.28*buzz,-.34*buzz)
        lever=58*bump(t,.7,.14);pawl=6*bump(t,.7,.1)
        # Dart: driven by the striker, it shrinks onto its own tip at the muzzle (no
        # translation), jumps only while fully collapsed, re-forms inside the closed hopper
        # throat out of sight and then drops into the channel.
        if t<.585:dart=('push',amp*fire)
        elif t<.64:dart=('shrink',amp,1-smooth((t-.585)/.055))
        elif t<.68:dart=('shrink',amp,0.0)
        elif t<.8:dart=('throat',smooth((t-.7)/.08))
        else:dart=('drop',smooth((t-.8)/.185))
        bead=1-.25*kick
    elif name=='jar':
        g=bump(t,.5,.42);s=math.sin(t*math.pi*4)*g
        head=-5.0*g+1.2*s;lever=14*s;pawl=10*g;lid=6*abs(s)
        hookL=(0,.4*s,.5*s);hookR=(0,-.5*s,.4*s);shot=.6*g;dart=('push',.6*g);bead=1-.3*g
    elif name=='jam':
        jerk=smooth((t-.06)/.12);snapL=smooth((t-.2)/.2);droop=smooth((t-.28)/.36)
        shot=6.0*jerk
        head=24*droop+3*math.sin(min(1,max(0,(t-.64)/.3))*math.pi)
        lever=84*smooth((t-.36)/.32)
        pawl=38*smooth((t-.3)/.24)
        lid=42*smooth((t-.42)/.2)-7*math.sin(min(1,max(0,(t-.62)/.3))*math.pi)
        # The left spring's hook tears free: its end drops and sags beside the channel.
        sag=snapL*(1+.18*math.sin(min(1,max(0,(t-.4)/.4))*math.pi*2)*(1-smooth((t-.7)/.25)))
        hookL=(2.2*sag,1.9*sag,-6.4*sag)
        dart=('jam',6.0*jerk,smooth((t-.16)/.3))
        bead=1-smooth((t-.44)/.3)
    # Crosshead and hooks; hooks are children of the crosshead.
    move('crosshead',(shot,0,0));move('hook_L',hookL);move('hook_R',hookR)
    turn('head',head);turn('lever',lever);turn('pawl',pawl,(0,-1,0));turn('lid',-lid)
    # Chamber dart cage.
    parent=REST[IDS['head']]
    tip=(DART_X0+DART_LEN,0,AXIS_Z)
    if dart[0]=='push':cage('dart',DART_BOX,parent,lambda c:add(c,(dart[1],0,0)))
    elif dart[0]=='shrink':
        p=add(tip,(dart[1],0,0));cage('dart',DART_BOX,parent,lambda c:add(p,mul(sub(add(c,(dart[1],0,0)),p),dart[2])))
    elif dart[0]=='throat':
        # Re-formed about the throat centre, entirely inside the closed hopper throat.
        home=(DART_X0+DART_LEN/2,0,THROAT_Z)
        cage('dart',DART_BOX,parent,lambda c:add(home,mul(sub(add(c,(0,0,THROAT_Z-AXIS_Z)),home),dart[1])))
    elif dart[0]=='drop':
        cage('dart',DART_BOX,parent,lambda c:add(c,(0,0,(THROAT_Z-AXIS_Z)*(1-dart[1]))))
    elif dart[0]=='jam':
        piv=(22.3,0,AXIS_Z);q=qmul(axis((0,0,1),math.radians(-5*dart[2])),axis((0,1,0),math.radians(4*dart[2])))
        cage('dart',DART_BOX,parent,lambda c:add(piv,rotate(q,sub(add(c,(dart[1],0,0)),piv))))
    else:cage('dart',DART_BOX,parent,lambda c:c)
    lidp=REST[IDS['lid']]
    top=(BEAD_C[0],0,BEAD_BOX[5])
    # The bead hangs from the spout: its top stays attached and only the lower half stretches.
    cage('bead',BEAD_BOX,lidp,lambda c:add(add(top,mul(sub(c,top),bead)),(0,0,-bead_drop*(c[2]<top[2])*bead)))
    for b,items in rot.items():
        q=(0,0,0,1)
        for ax,deg in items:q=qmul(q,axis(ax,math.radians(deg)))
        f[IDS[b]][3:7]=q
    return [tuple(r) for r in f]


def matrices(frame):return RIG.matrices(frame)
def deform(v,w,frame):return RIG.deform(v,w,frame)
def animation_data(v,w):return sample_clips(RIG,CLIPS,pose,v,w)
def build():
    skin=materials.texture_bytes();(ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts,v,n,uv,t,w=geometry();clips,bounds=animation_data(v,w)
    data=iqm.encode(v,n,uv,t,w,BONES,clips,bounds,mesh_label='Project_Broom_dart_turret',material_path=SKIN)
    path=ROOT/'mod/BrogueDoom/models/monsters/38_dart_turret.iqm';path.write_bytes(data)
    manifest=dict(schemaVersion=1,workId='BRG-M38',format='IQM v2',runtimeModel=path.relative_to(ROOT).as_posix(),
        sha256=hashlib.sha256(data).hexdigest(),skin=SKIN,skinSha256=hashlib.sha256(skin).hexdigest(),
        dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],
        parts=len(parts),vertices=len(v),triangles=len(t),boneCount=len(BONES),
        bones=[dict(name=n,parent=p,local=v) for n,p,v in BONES],
        clips=[{k:v for k,v in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],
        poseBounds=bounds,authoringSource='assets/monsters/dart_turret/dart-turret-animated.blend')
    out=ROOT/'assets/monsters/dart_turret';out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__':print(build()['sha256'])

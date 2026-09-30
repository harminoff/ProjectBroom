"""Original wall-mounted furnace mechanism for Brogue's flame turret (presentation only).

A tall cast-iron backplate carries a riveted firebox with an infernal furnace mask,
a heat-tempered finned nozzle, twin hinged mouth shutters, two banded fuel canisters
with a pressure dial, and a leather bellows. The only emissive surfaces are the
pilot flame, the ember eyes and a nozzle blast tongue that exists only during the
attack clips; each sits in an affine corner cage so death collapses it to zero area
with unit bone scales. Brogue owns the fire bolt, burning, targets and timing.
"""
import hashlib,json,math
from . import iqm,flame_turret_materials as materials
from .rat import ROOT,Part,add,sub,mul,cross,unit
from .skeletal import Rig,axis,qmul,assemble,sample_clips

SKIN='graphics/BRGFTUR.png'
AXIS_Z=17.3            # nozzle axis height
BLAST_P=(22.6,0,AXIS_Z)  # collapse point inside the bell mouth
PILOT_P=(23.35,0,15.55)  # pilot jet tip
EYES={'L':(4.8,24.4),'R':(-4.8,24.4)}
EYE_R=2.2
# Corner cages (world rest): x0,x1,y0,y1,z0,z1.
BLAST_BOX=(22.8,31.2,-3.9,3.9,AXIS_Z-3.9,AXIS_Z+3.9)
PILOT_BOX=(22.5,25.6,-1.7,1.7,14.9,21.4)
LID_OPEN=-80.0     # rest half-lidded visor angle about +Y (negative swings outward)
DAMPER_OPEN=128.0  # rest swing of each half shutter, forward and outward
BELLOWS_OPEN=16.0  # authored bind opening of the bellows top board
SPECS=[('root',None,(0,0,0)),('body','root',(-3,0,12)),('barrel','body',(3.4,0,AXIS_Z)),
       ('damper_L','barrel',(23.95,5.25,AXIS_Z)),('damper_R','barrel',(23.95,-5.25,AXIS_Z)),('lid_L','body',(4.75,4.8,27.2)),('lid_R','body',(4.75,-4.8,27.2)),
       ('bellows','body',(-8,0,32.3)),('needle','root',(1.05,14.2,25.5))]
for cage,box in (('blast',BLAST_BOX),('pilot',PILOT_BOX)):
    for z in range(2):
        for y in range(2):
            for x in range(2):SPECS.append((f'{cage}_{z}{y}{x}','barrel',(box[x],box[2+y],box[4+z])))
for side,(cy,cz) in EYES.items():
    for z in range(2):
        for y in range(2):SPECS.append((f'eye{side}_{z}{y}','body',(3.8,cy+(y*2-1)*EYE_R,cz+(z*2-1)*EYE_R)))
RIG=Rig.from_world(SPECS);BONES,REST=RIG.bones,RIG.rest
IDS={n:i for i,(n,_,_) in enumerate(BONES)}
CLIPS=[('idle',40,20,True),('rest',20,20,True),('spit',24,35,False),('gout',28,35,False),('jolt',14,35,False),('extinguish',36,35,False)]
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


def eye_weights(side,v):
    cy,cz=EYES[side];fy=min(1,max(0,(v[1]-cy+EYE_R)/(2*EYE_R)));fz=min(1,max(0,(v[2]-cz+EYE_R)/(2*EYE_R)))
    return quantize([(IDS[f'eye{side}_00'],(1-fy)*(1-fz)),(IDS[f'eye{side}_01'],fy*(1-fz)),
                     (IDS[f'eye{side}_10'],(1-fy)*fz),(IDS[f'eye{side}_11'],fy*fz)])


class Piece(Part):
    """Part with material role and painting parameters; UVs are finished later."""
    def __init__(self,name,role,mode='shade'):
        super().__init__(name);self.role=role;self.mode=mode;self.pa=[];self.pv=[]
    def add(self,co,a=0,v=0):
        self.vertices.append(tuple(round(c,6) for c in co));self.pa.append(a);self.pv.append(v);return len(self.vertices)-1


def rotate_about(p,center,axis_vec,deg):
    from .skeletal import rotate
    return add(center,rotate(axis(axis_vec,math.radians(deg)),sub(p,center)))


def geometry():
    parts=[]
    def put(p,bone='root',weights=None):
        p.bone=bone
        p.skin_weights=[weights(v) for v in p.vertices] if weights else [[(IDS[bone],1)]]*len(p.vertices)
        parts.append(p);return p
    def rings(p,rows,closed_start=True,closed_end=True):
        """rows: list of vertex-index lists (equal length, last duplicates first for UV seam)."""
        point=lambda row:len({p.vertices[i] for i in row})==1
        for r0,r1 in zip(rows,rows[1:]):
            for j in range(len(r0)-1):
                # A collapsed pole row gets triangles, never zero-area quad halves.
                if point(r0):p.faces.append((r0[j],r1[j+1],r1[j]))
                elif point(r1):p.faces.append((r0[j],r0[j+1],r1[j]))
                else:p.faces.append((r0[j],r0[j+1],r1[j+1],r1[j]))
        for ring,rev in ((rows[0],True),(rows[-1],False)):
            if (closed_start if rev else closed_end):
                c=[p.vertices[i] for i in ring[:-1]];center=p.add(tuple(sum(x)/len(c) for x in zip(*c)),p.pa[ring[0]],.5)
                for j in range(len(ring)-1):p.faces.append((center,ring[j+1],ring[j]) if rev else (center,ring[j],ring[j+1]))
    def lathe(name,profile,role,center,ax='x',sides=24,bone='root',caps=(True,True),mode='shade',weights=None,start=0):
        """Surface of revolution; profile entries are (along, radius)."""
        p=Piece(name,role,mode);lengths=[0]
        for a,b in zip(profile,profile[1:]):lengths.append(lengths[-1]+math.dist(a,b))
        rows=[]
        for (s,r),l in zip(profile,lengths):
            row=[]
            for j in range(sides+1):
                t=start+math.tau*j/sides;c,sn=r*math.cos(t),r*math.sin(t)
                co=(center[0]+s,center[1]+c,center[2]+sn) if ax=='x' else (center[0]+c,center[1]+sn,center[2]+s)
                row.append(p.add(co,l/lengths[-1],j/sides))
            rows.append(row)
        rings(p,rows,caps[0] and profile[0][1]>0,caps[1] and profile[-1][1]>0)
        return put(p,bone,weights)
    def tube(name,controls,role,sides=10,samples=3,bone='root',weights=None,mode='shade',flatten=1.0,ribbed=0,twist=0.0,up=(0,0,1)):
        from .rat import spline
        p=Piece(name,role,mode);pts=spline(controls,samples);rows=[];prev=None
        for i,row in enumerate(pts):
            c,r=row[:3],max(.02,row[3]);t=unit(sub(pts[min(i+1,len(pts)-1)][:3],pts[max(0,i-1)][:3]))
            if prev is None:n=unit(cross(t,up if abs(sum(a*b for a,b in zip(t,up)))<.9 else (0,1,0)))
            else:n=unit(sub(prev,mul(t,sum(a*b for a,b in zip(prev,t)))))
            prev=n;bn=unit(cross(t,n));u=i/(len(pts)-1)
            if ribbed:r*=1+.09*math.cos(u*math.tau*ribbed)
            idx=[]
            for j in range(sides+1):
                ang=math.tau*j/sides+twist*u
                idx.append(p.add(add(c,add(mul(n,r*math.cos(ang)),mul(bn,r*flatten*math.sin(ang)))),u,j/sides))
            rows.append(idx)
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
    def prism(name,outline,depth,role,frame=((1,0,0),(0,1,0),(0,0,1)),bevel=.4,bone='root',mode='shade',weights=None):
        """Convex outline (s,t) extruded along frame[0] from depth[0] to depth[1] with a chamfered front."""
        p=Piece(name,role,mode);d0,d1=depth;ex,ey,ez=frame
        cs=sum(s for s,t in outline)/len(outline);ct=sum(t for s,t in outline)/len(outline)
        smin=min(s for s,t in outline);smax=max(s for s,t in outline);tmin=min(t for s,t in outline);tmax=max(t for s,t in outline)
        def at(d,s,t):return add(add(mul(ex,d),mul(ey,s)),mul(ez,t))
        def inset(s,t,k):
            L=math.hypot(s-cs,t-ct);return (s-(s-cs)/L*k,t-(t-ct)/L*k) if L>1e-9 else (s,t)
        per=[0]
        for a,b in zip(outline+outline[:1],outline[1:]+outline[:1]):per.append(per[-1]+math.dist(a,b))
        layers=[(d0,0),(d1-bevel,0),(d1,bevel)];rows=[]
        for k,(d,ins) in enumerate(layers):
            row=[]
            for (s,t),l in zip(outline+outline[:1],per):
                s2,t2=inset(s,t,ins);row.append(p.add(at(d,s2,t2),l/per[-1],.15+.35*k))
            rows.append(row)
        for r0,r1 in zip(rows,rows[1:]):
            for j in range(len(r0)-1):p.faces.append((r0[j],r0[j+1],r1[j+1],r1[j]))
        for ring,d,rev,ins in ((rows[0],d0,True,0),(rows[-1],d1,False,bevel)):
            cap=[]
            for s,t in outline:
                s2,t2=inset(s,t,ins);cap.append(p.add(at(d,s2,t2),(s2-smin)/(smax-smin),(tmax-t2)/(tmax-tmin)))
            c=p.add(at(d,cs,ct),(cs-smin)/(smax-smin),(tmax-ct)/(tmax-tmin));m=len(cap)
            for j in range(m):p.faces.append((c,cap[(j+1)%m],cap[j]) if rev else (c,cap[j],cap[(j+1)%m]))
        return put(p,bone,weights)
    def box(name,lo,hi,role,bone='root',bevel=.3,axis_='x',weights=None):
        """Axis-aligned chamfered box; its chamfered face points along +axis_."""
        frames={'x':((1,0,0),(0,1,0),(0,0,1)),'y':((0,1,0),(0,0,1),(1,0,0)),'z':((0,0,1),(1,0,0),(0,1,0)),
                '-z':((0,0,-1),(1,0,0),(0,-1,0))}
        ex,ey,ez=frames[axis_];dot=lambda a,b:sum(x*y for x,y in zip(a,b))
        def rng(e):
            vals=[dot(e,(lo[0],lo[1],lo[2])),dot(e,(hi[0],hi[1],hi[2]))];return min(vals),max(vals)
        s0,s1=rng(ey);t0,t1=rng(ez);d0,d1=rng(ex)
        return prism(name,[(s0,t0),(s1,t0),(s1,t1),(s0,t1)],(d0,d1),role,(ex,ey,ez),min(bevel,(d1-d0)*.45),bone,weights=weights)

    # ---- Fixed cast-iron backplate (root): convex shield, stepped panel, anchors, rivets.
    shield=[(-16,4),(16,4),(17.5,8),(17.5,36),(11.5,43.5),(0,46.5),(-11.5,43.5),(-17.5,36),(-17.5,8)]
    prism('shield_backplate',shield,(-11,-8.8),'plate',bevel=.8)
    inner=[(s*.8,10+(t-10)*.84) for s,t in shield]
    prism('stepped_plate_panel',inner,(-8.8,-8.3),'plate',bevel=.35)
    ring_pts=[]
    for (a,b),(c,d) in zip(shield,shield[1:]+shield[:1]):
        L=math.dist((a,b),(c,d));n=max(1,round(L/4.2))
        for k in range(n):ring_pts.append((a+(c-a)*k/n,b+(d-b)*k/n))
    cs=sum(s for s,t in shield)/len(shield);ct=sum(t for s,t in shield)/len(shield)
    for k,(s,t) in enumerate(ring_pts):
        s2,t2=cs+(s-cs)*.9,ct+(t-ct)*.9
        ball(f'plate_rivet_{k}',(-8.6,s2,t2),(.5,.62,.62),'bolt',seg=8,rings_=4)
    for k,(y,z) in enumerate(((-13.5,8.5),(13.5,8.5),(-14.5,33),(14.5,33),(-7.5,41.5),(7.5,41.5))):
        lathe(f'anchor_washer_{k}',[(0,0),(0,2.1),(.35,2.1),(.45,1.8),(.45,0)],'steel',(-8.5,y,z),sides=16)
        lathe(f'anchor_hex_bolt_{k}',[(0,1.45),(1.1,1.45),(1.35,1.1),(1.4,0)],'bolt',(-8.05,y,z),sides=6,start=math.pi/6)
    # Gusset brackets and shelf carry the cantilevered firebox.
    for y in (-6.5,6.5):
        prism(f'gusset_bracket_{"L" if y>0 else "R"}',[(-8.6,3.6),(-3.2,11.2),(-8.6,11.2)],(-y-.7,-y+.7),'iron',
              ((0,-1,0),(1,0,0),(0,0,1)),.25)
        for k,(x,z) in enumerate(((-7.6,5.5),(-7.6,9.6),(-5.2,10.2))):ball(f'gusset_rivet_{y}_{k}',(x,y+(.72 if y>0 else -.72),z),(.35,.3,.35),'bolt',seg=8,rings_=4)
    box('support_shelf',(-8.6,-9.2,11.2),(-3.0,9.2,12.0),'iron',axis_='z')

    # ---- Fuel canisters, valves, pressure dial and feed pipes (fixed to the plate).
    for side,y in (('L',14.2),('R',-14.2)):
        lathe(f'fuel_canister_{side}',[(6.2,0),(6.2,2.2),(6.7,2.95),(7.4,3.1),(30.8,3.1),(31.6,2.9),(32.6,2.3),(33.3,1.3),(33.5,0)],'tank',(-4.8,y,0),'z',20)
        for k,z in enumerate((9.2,19.5,29.6)):
            lathe(f'canister_band_{side}_{k}',[(z-.6,3.12),(z-.45,3.42),(z+.45,3.42),(z+.6,3.12)],'brass',(-4.8,y,0),'z',20,caps=(False,False))
        for k,z in enumerate((12.5,27.0)):
            box(f'canister_strap_{side}_{k}',(-8.8,y-.9,z-.6),(-6.4,y+.9,z+.6),'steel')
        lathe(f'valve_stem_{side}',[(33.3,.45),(35.4,.45),(35.4,0)],'brass',(-4.8,y,0),'z',8)
        tube(f'valve_wheel_{side}',[(-4.8+1.5*math.cos(a*math.tau/12),y+1.5*math.sin(a*math.tau/12),35.4,.28) for a in range(13)],'steel',6,1)
        for k in range(4):
            a=k*math.pi/2+math.pi/4
            tube(f'valve_spoke_{side}_{k}',[(-4.8,y,35.4,.16),(-4.8+1.4*math.cos(a),y+1.4*math.sin(a),35.4,.16)],'steel',5,1)
        s=1 if y>0 else -1
        # Feed pipes bend from the fixed canisters into the firebox; weights blend root to body.
        feed=[(-2.1,y-s*1.0,15.2,.55),(-.6,y-s*1.4,15.2,.55),(.4,y-s*2.6,15.2,.55),(.3,s*10.4,15.2,.55),(-1.2,s*10.2,15.2,.55)]
        def blend(v):
            f=min(1,max(0,(12.4-abs(v[1]))/1.6))
            return quantize([(IDS['root'],1-f),(IDS['body'],f)])
        tube(f'copper_feed_pipe_{side}',feed,'copper',8,3,weights=blend)
        lathe(f'feed_flange_{side}',[(-.25,0),(-.25,1.0),(.25,1.0),(.25,0)],'brass',(-1.9,y-s*1.2,15.2),'x',10)
        lathe(f'feed_valve_{side}',[(-.3,0),(-.3,.9),(.3,.9),(.3,0)],'brass',(.45,y-s*2.2,15.2),'x',10)
    # Pressure dial on the left canister; the needle is the only moving fixed-mount part.
    tube('dial_stem',[(-2.0,14.2,25.5,.45),(.3,14.2,25.5,.45)],'brass',8,1)
    lathe('dial_bezel',[(0,0),(0,2.3),(.55,2.35),(.8,2.05),(.7,1.9),(.55,0)],'brass',(.3,14.2,25.5),'x',20)
    p=lathe('dial_face',[(.72,1.9),(.72,0)],'gauge',(.3,14.2,25.5),'x',20,caps=(False,False),mode='planar')
    p.plane=((0,1,0),(0,0,1),(14.2,25.5),2.0)
    box('dial_needle',(1.02,14.1,25.3),(1.12,14.3,27.1),'bolt','needle',bevel=.03)
    ball('dial_hub',(1.1,14.2,25.5),(.18,.28,.28),'brass','needle',6,3)

    # ---- Firebox (body): riveted box, straps, side louvres.
    box('riveted_firebox',(-8.6,-10.5,12.0),(2.0,10.5,31.5),'iron','body',.6)
    for k,x in enumerate((-6.2,-1.4)):
        box(f'firebox_strap_top_{k}',(x-.5,-10.9,31.3),(x+.5,10.9,31.9),'steel','body',.15,'z')
        for s in (-1,1):
            box(f'firebox_strap_side_{k}_{s}',(x-.5,s*10.5-.4,11.8),(x+.5,s*10.5+.4,31.9),'steel','body',.15,'y' if s>0 else 'y')
            for j,z in enumerate((14.5,19.5,24.5,29.5)):ball(f'strap_rivet_{k}_{s}_{j}',(x,s*10.95,z),(.32,.28,.32),'bolt','body',6,3)
    for s in (-1,1):
        for j in range(4):
            z=17.2+j*2.7
            prism(f'side_louvre_{s}_{j}',[(-5.2,z),(-2.4,z),(-2.4,z+.5),(-5.2,z+1.1)],(-11.3,-10.5) if s>0 else (10.5,11.3),'iron',
                  ((0,-1,0),(1,0,0),(0,0,1)),.12,'body')

    # ---- Infernal cast mask: brow, crest, cheeks, fanged mouth ring, sockets, horns.
    mask_outline=[(-4.6,12.4),(4.6,12.4),(8.4,16),(11.2,27),(10.5,31.5),(-10.5,31.5),(-11.2,27),(-8.4,16)]
    prism('infernal_mask_plate',mask_outline,(2.0,3.4),'mask',bevel=.5,bone='body')
    for side,s in (('L',1),('R',-1)):
        tube(f'angry_brow_{side}',[(3.5,s*1.0,25.9,1.0),(3.9,s*3.2,27.0,1.15),(3.8,s*6.4,28.3,.95),(3.4,s*9.4,29.6,.55)],'mask',10,3,'body')
        ball(f'cheek_boss_{side}',(3.35,s*6.6,19.6),(.9,2.3,1.9),'mask','body',12,6)
        tube(f'cheek_ridge_{side}',[(3.4,s*9.8,23.0,.6),(3.7,s*8.6,19.5,.75),(3.5,s*6.2,15.6,.55)],'mask',8,3,'body')
        cy,cz=EYES[side]
        # Raised eye ports: the mask plate is solid, so bezel, well and lens stand proud of it.
        lathe(f'eye_socket_rim_{side}',[(-.2,3.0),(.55,2.95),(1.2,2.7),(1.35,2.45),(1.1,2.2),(.9,2.2)],'mask',(3.4,cy,cz),'x',20,'body',caps=(False,False))
        lathe(f'eye_socket_well_{side}',[(.9,2.2),(.45,2.2),(.12,2.05),(.08,0)],'soot',(3.4,cy,cz),'x',20,'body',caps=(False,True))
        lens=lathe(f'ember_eye_{side}',[(3.52,2.02),(3.9,1.8),(4.15,1.25),(4.3,0)],'ember',(0,cy,cz),'x',20,'body',caps=(False,True),mode='planar',
                   weights=lambda v,side=side:eye_weights(side,v))
        lens.plane=((0,s,0),(0,0,1),(s*cy,cz),2.02)
        # Hinged iron eyelid visor, authored closed over the socket.
        lid=lathe(f'iron_eyelid_{side}',[(0,0),(0,2.55),(.1,2.85),(.3,2.95),(.5,2.65),(.66,1.6),(.72,0)],'steel',(4.85,cy,cz),'x',20,f'lid_{side}')
        tube(f'eyelid_hinge_{side}',[(4.75,cy-1.5,27.2,.34),(4.75,cy+1.5,27.2,.34)],'brass',8,1,f'lid_{side}')
        # Curled ribbed horns sweep up and outwards beside the bellows.
        tube(f'curled_horn_{side}',[(1.0,s*8.6,30.2,1.95),(-.6,s*11.8,34.6,1.65),(-2.6,s*14.4,39.2,1.25),(-2.2,s*15.8,43.2,.8),(.2,s*15.4,45.6,.42),(2.0,s*13.9,46.2,.08)],
             'horn',12,4,'body',ribbed=18)
    tube('snout_crest',[(3.2,0,31.2,.8),(3.8,0,28.6,1.0),(4.2,0,25.4,1.2),(4.3,0,22.6,1.0)],'mask',10,3,'body')
    lathe('fanged_mouth_ring',[(-1.2,4.5),(0,4.45),(1.0,4.35),(1.35,3.95),(1.1,3.55),(0,3.45),(-1.2,3.4)],'mask',(3.4,0,AXIS_Z),'x',28,'body',caps=(False,False))
    for k in range(8):
        a=math.radians(90+(k-3.5)*22) if k<4 else math.radians(270+(k-5.5)*26)
        base=(4.55,4.1*math.cos(a),AXIS_Z+4.1*math.sin(a));tip=(5.7,3.55*math.cos(a),AXIS_Z+3.55*math.sin(a))
        tube(f'mouth_fang_{k}',[(*base,.42),(*add(mul(base,.5),mul(tip,.5)),.28),(*tip,.03)],'bolt',6,2,'body')

    # ---- Bellows: fixed lower board, hinged top board, pleated leather.
    box('bellows_lower_board',(-8.2,-5.6,31.5),(.8,5.6,32.3),'steel','body',.2,'z')
    hinge=(-8.0,0,32.3)
    def open_board(p,deg=BELLOWS_OPEN):return rotate_about(p,hinge,(0,1,0),-deg)
    top=box('bellows_top_board',(-8.2,-5.9,32.4),(1.2,5.9,33.1),'steel','bellows',.2,'z')
    top.vertices=[tuple(round(c,6) for c in open_board(v)) for v in top.vertices]
    handle=tube('bellows_handle',[(0.6,-2.2,33.1,.3),(1.6,-2.2,33.8,.3),(1.9,0,34.0,.3),(1.6,2.2,33.8,.3),(.6,2.2,33.1,.3)],'brass',6,2,'bellows')
    handle.vertices=[tuple(round(c,6) for c in open_board(v)) for v in handle.vertices]
    leather=Piece('pleated_leather_bellows','leather');rows=[];K=10
    outline=[]
    for (y0,x0),(y1,x1) in (((-5.2,-7.6),(-5.2,.2)),((-5.2,.2),(5.2,.2)),((5.2,.2),(5.2,-7.6))):
        for k in range(6):outline.append((x0+(x1-x0)*k/6,y0+(y1-y0)*k/6))
    outline.append((-7.6,5.2))
    for k in range(K+1):
        s=k/K;bulge=.65 if k%2 else 0;row=[]
        for j,(x,y) in enumerate(outline):
            # Pleat folds bulge outwards from the board centre line.
            cx,cy=-3.7,0;dx,dy=x-cx,y-cy;L=math.hypot(dx/4.2,dy/5.6) or 1
            px,py=x+dx/L/4.2*bulge*(x>-7.5),y+dy/L/5.6*bulge*1.2
            pt=rotate_about((px,py,32.3+.02),hinge,(0,1,0),-BELLOWS_OPEN*s)
            row.append(leather.add(pt,j/(len(outline)-1),s))
        rows.append(row)
    for r0,r1 in zip(rows,rows[1:]):
        for j in range(len(r0)-1):leather.faces.append((r0[j],r0[j+1],r1[j+1],r1[j]))
    ang=lambda v:math.degrees(math.atan2(v[2]-hinge[2],v[0]-hinge[0]))
    put(leather,'body',lambda v:quantize([(IDS['body'],1-min(1,max(0,ang(v)/BELLOWS_OPEN))),(IDS['bellows'],min(1,max(0,ang(v)/BELLOWS_OPEN)))]))
    tube('bellows_outlet_spout',[(.8,0,31.9,.55),(1.8,0,31.9,.55),(2.4,0,31.2,.5)],'brass',8,2,'body')

    # ---- Nozzle (barrel): tempered finned barrel, flared bell, bands, pilot line, damper.
    prof=[(-2.4,3.3),(1.0,3.3),(1.6,3.35),(8.6,3.0),(15.1,2.75),(17.1,3.0),(18.6,3.8),(19.8,4.7),(20.4,4.95),(20.7,4.8),
          (20.6,4.4),(19.6,3.9),(18.1,2.9),(15.6,2.35),(8.6,2.5),(4.6,2.6),(4.2,0)]
    lathe('tempered_nozzle_barrel',prof,'nozzle',(3.4,0,AXIS_Z),'x',28,'barrel')
    for k,x in enumerate((6.2,11.0,15.4)):
        r=3.32-.055*(x-3.4)
        lathe(f'nozzle_band_{k}',[(x-.55,r),(x-.4,r+.42),(x+.4,r+.42),(x+.55,r)],'brass',(0,0,AXIS_Z),'x',28,'barrel',caps=(False,False))
    for k,x in enumerate((8.0,9.0,10.0,12.4,13.4)):
        r=3.32-.055*(x-3.4)
        lathe(f'cooling_fin_{k}',[(x-.18,r),(x-.18,4.2),(x-.05,4.35),(x+.05,4.35),(x+.18,4.2),(x+.18,r)],'fin',(0,0,AXIS_Z),'x',28,'barrel',caps=(False,False))
    tube('copper_pilot_line',[(4.2,0,AXIS_Z-3.75,.36),(12,0,AXIS_Z-3.35,.36),(18.8,0,AXIS_Z-3.2,.36),(21.9,0,AXIS_Z-2.35,.34),(23.0,0,15.3,.3)],'copper',8,3,'barrel')
    tube('pilot_jet_tip',[(22.9,0,15.2,.42),(23.35,0,15.55,.3)],'brass',8,1,'barrel')
    # Twin half shutters hinged at the bell's sides swing forward, never through the barrel.
    for side,sg in (('L',1),('R',-1)):
        bone='damper_'+side
        half=[(0,-5.3)]+[(sg*5.3*math.cos(math.radians(a)),5.3*math.sin(math.radians(a))) for a in range(-75,90,15)]+[(0,5.3)]
        half=[(y+sg*.04,t+AXIS_Z) for y,t in (half if sg>0 else [(y,-t) for y,t in half])]
        prism(f'mouth_shutter_{side}',half,(24.15,24.8),'steel',bevel=.25,bone=bone)
        tube(f'shutter_hinge_knuckle_{side}',[(23.95,sg*5.25,AXIS_Z-2.6,.5),(23.95,sg*5.25,AXIS_Z+2.6,.5)],'brass',8,1,bone)
        tube(f'shutter_hinge_lug_{side}',[(23.2,sg*4.7,AXIS_Z,.55),(23.95,sg*5.25,AXIS_Z,.45)],'steel',6,1,'barrel')
        tube(f'shutter_rib_{side}',[(24.85,sg*.5,AXIS_Z+4.3,.22),(24.95,sg*2.4,AXIS_Z,.3),(24.85,sg*.5,AXIS_Z-4.3,.22)],'brass',6,3,bone)
        ball(f'shutter_pull_knob_{side}',(25.25,sg*1.6,AXIS_Z),(.5,.5,.5),'brass',bone,8,4)
        for k,a in enumerate((-50,0,50)):
            ball(f'shutter_rivet_{side}_{k}',(24.85,sg*3.9*math.cos(math.radians(a)),AXIS_Z+3.9*math.sin(math.radians(a))),(.22,.3,.3),'bolt',bone,6,3)

    # ---- Emissive cages: attack blast tongue, pilot flame, ember lenses (above).
    def flame(name,prefix,box_,pts,sides=12,a0=.5,a1=.5,flatten=1.0,twist=0.0,up=(0,0,1)):
        p=tube(name,pts,'flame',sides,4,'barrel',lambda v:cage_weights(prefix,box_,v),'flame',flatten,0,twist,up)
        p.flame=(a0,a1)
        for v in p.vertices:assert all(box_[2*a]-1e-6<=v[a]<=box_[2*a+1]+1e-6 for a in range(3)),(name,v)
        return p
    z=AXIS_Z
    # Widening plume with ragged outward tongues at its front.
    flame('blast_core','blast',BLAST_BOX,[(23.2,0,z,1.6),(25.0,0,z,2.35),(27.0,0,z+.15,2.75),(28.9,0,z+.35,2.2),(30.3,0,z+.5,.9),(30.9,0,z+.6,.02)],16,.5,.5)
    for k in range(7):
        L=[];reach=(0,.5,.15,.7,.3,.55,.1)[k]
        for j,(x,r,rad) in enumerate(((24.2,1.2,.5),(26.2,2.2,.75),(28.2,2.75,.6),(29.8+reach,3.0,.3),(30.4+reach,3.25,.02))):
            a=k*math.tau/7+.2+.12*j;L.append((x,r*math.cos(a),z+r*math.sin(a),rad))
        flame(f'blast_lick_{k}','blast',BLAST_BOX,L,10,.84,.84,.6)
    flame('pilot_core','pilot',PILOT_BOX,[(23.35,0,15.25,.65),(23.6,0,16.3,.95),(24.3,0,18.0,.75),(24.2,0,19.6,.38),(23.5,0,21.1,.02)],12,.5,.5,.8,0,(1,0,0))
    flame('pilot_lick_0','pilot',PILOT_BOX,[(23.2,.3,15.5,.4),(23.9,.8,16.9,.55),(24.8,.7,18.2,.3),(25.2,.2,19.1,.02)],8,.82,.82,.7,0,(1,0,0))
    flame('pilot_lick_1','pilot',PILOT_BOX,[(23.2,-.3,15.5,.4),(23.3,-.9,16.8,.5),(22.9,-1.0,18.3,.3),(23.1,-.4,19.4,.02)],8,.82,.82,.7,0,(1,0,0))

    finish_uvs(parts)
    return assemble(parts,lambda p,v,u:[(0,1)])


def finish_uvs(parts):
    for p in parts:
        normals=p.normals();p.uv=[]
        for i,(v,n) in enumerate(zip(p.vertices,normals)):
            if p.mode=='flame':
                a0,a1=p.flame;a=a0+.12*math.cos(p.pv[i]*math.tau)*(1 if a0==.5 else .4)
                p.uv.append(materials.uv('flame',a,p.pa[i]*.96+.02))
            elif p.mode=='planar':
                ey,ez,(cy,cz),r=p.plane
                s=sum(a*b for a,b in zip(v,ey))-cy;t=sum(a*b for a,b in zip(v,ez))-cz
                p.uv.append(materials.uv(p.role,.5+s/(2*r),.5-t/(2*r)))
            else:
                light=.5+.5*sum(a*b for a,b in zip(n,LIGHT))
                ao=.14*min(1,max(0,(-6.5-v[0])/2.5))
                b=.04+.7*(1-light)+.16*p.pv[i]+ao
                p.uv.append(materials.uv(p.role,p.pa[i],b))


def pose(name,t):
    f=[[*local,0,0,0,1,1,1,1] for _,_,local in BONES]
    rot={}
    def turn(b,deg,ax=(0,1,0)):rot.setdefault(b,[]).append((ax,deg))
    def move(b,d):
        for a in range(3):f[IDS[b]][a]+=d[a]
    def cage(prefix,box_,point,k,extra=None):
        parent=REST[IDS['barrel']]
        for z in range(2):
            for y in range(2):
                for x in range(2):
                    b=IDS[f'{prefix}_{z}{y}{x}'];c=(box_[x],box_[2+y],box_[4+z])
                    kk=k(x,y,z) if callable(k) else k
                    target=add(point,mul(sub(c,point),kk))
                    if extra:target=add(target,extra(x,y,z))
                    f[b][:3]=list(sub(target,parent))
    def eyes(k):
        body=REST[IDS['body']]
        for side,(cy,cz) in EYES.items():
            for z in range(2):
                for y in range(2):
                    c=(3.8,cy+(y*2-1)*EYE_R,cz+(z*2-1)*EYE_R);target=add((3.8,cy,cz),mul(sub(c,(3.8,cy,cz)),k))
                    f[IDS[f'eye{side}_{z}{y}']][:3]=list(sub(target,body))
    smooth=lambda x:(lambda q:q*q*(3-2*q))(min(1,max(0,x)))
    def bump(t,c,w):return math.cos(min(1,abs(t-c)/w)*math.pi/2)**2
    lid=LID_OPEN;damper=DAMPER_OPEN;bellows=0.0;needle=0.0
    blast=0.0;pilot_k=1.0;eye_k=1.0;pilot_sway=(0,0,0)
    if name=='idle':
        w=math.tau*t
        pilot_sway=(.22*math.sin(3*w),.32*(math.sin(2*w+.7)-math.sin(.7)),.45*(math.sin(4*w+1.3)-math.sin(1.3)))
        needle=2.2*math.sin(5*w)
    elif name=='spit':
        g=bump(t,.52,.3);ext=smooth((t-.24)/.26)*(1-smooth((t-.68)/.24))
        bellows=12*smooth((t-.08)/.34)*(1-smooth((t-.62)/.3))
        lid=LID_OPEN-36*g;damper=DAMPER_OPEN+14*g*(1+.2*math.sin(t*40))
        blast=ext;needle=-38*g
        move('barrel',(-.9*bump(t,.5,.18),0,0));turn('barrel',-2.2*bump(t,.5,.16));turn('body',-1.2*bump(t,.5,.2))
        pilot_sway=(.9*g,0,-.5*g)
    elif name=='gout':
        pump=bump(t,.24,.18);press=bump(t,.52,.22)
        bellows=-7*pump+12*press
        ext=max(.78*bump(t,.52,.2),.42*bump(t,.8,.1))
        blast=ext;lid=LID_OPEN+22*press;needle=-26*press+10*pump
        turn('barrel',7*bump(t,.52,.3));damper=DAMPER_OPEN+8*press
        pilot_sway=(.6*press,.3*pump,-.3*press)
    elif name=='jolt':
        g=bump(t,.5,.42);s=math.sin(t*math.pi*3)*g
        turn('body',-4.5*g);turn('barrel',2.5*s);move('barrel',(-.5*g,0,0))
        lid=LID_OPEN+42*g;damper=DAMPER_OPEN-13*g+6*s
        needle=24*s;pilot_sway=(-1.0*g,.4*s,-.9*g)
    elif name=='extinguish':
        pilot_k=1-smooth(t/.4);eye_k=1-smooth((t-.12)/.46)
        lid=LID_OPEN*(1-smooth((t-.18)/.42))
        close=smooth((t-.32)/.28);damper=DAMPER_OPEN*(1-close)+6*math.sin(min(1,max(0,(t-.6)/.2))*math.pi)*(close>=1)
        tear=smooth((t-.5)/.42)
        turn('body',7*tear);turn('barrel',18*smooth((t-.44)/.5))
        bellows=14*smooth((t-.4)/.5);needle=72*smooth((t-.2)/.6)
        pilot_sway=(0,0,0)
    # Shared rest configuration and cages.
    turn('lid_L',lid);turn('lid_R',lid);turn('damper_L',damper,(0,0,1));turn('damper_R',-damper,(0,0,1));turn('bellows',bellows);turn('needle',needle,(1,0,0))
    if blast>1e-9:
        cage('blast',BLAST_BOX,BLAST_P,lambda x,y,z:blast if x else min(1,1.6*blast))
    else:
        cage('blast',BLAST_BOX,BLAST_P,0.0)
    cage('pilot',PILOT_BOX,PILOT_P,pilot_k,lambda x,y,z:mul(pilot_sway,z*pilot_k))
    eyes(eye_k)
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
    data=iqm.encode(v,n,uv,t,w,BONES,clips,bounds,mesh_label='Project_Broom_flame_turret',material_path=SKIN)
    path=ROOT/'mod/BrogueDoom/models/monsters/44_flame_turret.iqm';path.write_bytes(data)
    manifest=dict(schemaVersion=1,workId='BRG-M44',format='IQM v2',runtimeModel=path.relative_to(ROOT).as_posix(),
        sha256=hashlib.sha256(data).hexdigest(),skin=SKIN,skinSha256=hashlib.sha256(skin).hexdigest(),
        dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],
        parts=len(parts),vertices=len(v),triangles=len(t),boneCount=len(BONES),
        bones=[dict(name=n,parent=p,local=v) for n,p,v in BONES],
        clips=[{k:v for k,v in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],
        poseBounds=bounds,emissive=dict(atlasU=materials.EMISSIVE_U,shader='shaders/flame-turret-fire.fp'),
        authoringSource='assets/monsters/flame_turret/flame-turret-animated.blend')
    out=ROOT/'assets/monsters/flame_turret';out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__':print(build()['sha256'])

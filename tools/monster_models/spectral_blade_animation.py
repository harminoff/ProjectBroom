"""Original flickering spectral blade for Brogue's MK_SPECTRAL_BLADE (presentation only).

Brogue conjures these hilt-less weapons with a staff of conjuration or a goblin
conjurer's or eldritch totem's summoning: "Eldritch forces have coalesced to form this
flickering, ethereal weapon." The model is a curved, single-edged blade of indigo
and electric-blue light with a white-hot edge, a see-through rune fuller and no
hilt. Its base is a glowing knot from which three flame-wisps stream like a comet
tail, and three motes orbit the blade. It is drawn additively and fullbright.

The blade is five jagged shards (one bone each) so death can shatter it and drop
the pieces on the floor. The slash and whirl light trails sit in affine corner
cages (the flame turret's technique): they exist only inside attack clips and
otherwise collapse to zero area with unit bone scales. Brogue owns summoning,
flight, lifespan, negation, attacks, targets and timing; this file only draws.
"""
import hashlib,json,math
from . import iqm
from .rat import ROOT,Part,add,sub,mul,cross,unit,spline
from .skeletal import Rig,axis,qmul,inverse,rotate,assemble,sample_clips
from . import spectral_blade_materials as materials

SKIN='graphics/BRGSBLAD.png'
MODEL='mod/BrogueDoom/models/monsters/55_spectral_blade.iqm'
SHADER='mod/BrogueDoom/shaders/spectral-blade-glow.fp'
BASE=(0.0,0.0,15.5)          # blade root (knot) at rest
LENGTH=39.0;CURVE=5.6        # sabre sweep: the point curves back toward -Y
EDGE=[(0,3.3),(.12,3.9),(.45,5.1),(.68,5.4),(.84,4.2),(.94,1.9),(1,0)]
SPINE=[(0,2.7),(.6,2.6),(.8,2.0),(.92,.9),(1,0)]
THICK=[(0,.95),(.6,.72),(.9,.4),(1,0)]
SHARDS=(0,.24,.44,.62,.79,1.0);JAG=(0,.07,-.08,.07,-.06,0)
# Closed section: spine front, ridge front, cutting edge, ridge back, spine back.
SECTION=((0,1),(.44,.8),(1,0),(.44,-.8),(0,-1),(0,1))
WISPS=[[(-.3,0,15.4,2.0),(-1.6,.3,11.2,1.75),(-3.8,-.8,7.4,1.35),(-7.6,.7,4.6,.8),(-12.6,-.3,3.4,.05)],
       [(-.4,1.0,15.6,1.4),(-2.6,2.0,12.4,1.2),(-5.6,2.6,9.8,.85),(-9.4,1.6,8.4,.5),(-13.0,2.8,8.0,.04)],
       [(-.4,-1.0,15.6,1.4),(-2.4,-2.2,12.8,1.2),(-5.2,-2.8,10.6,.85),(-8.8,-1.8,9.4,.5),(-12.2,-3.0,9.2,.04)]]
MOTE_R=7.5;MOTES=[(0.0,23.5),(2.1,34.5),(4.2,45.5)]   # (orbit angle, rest height)
# Slash: the blade swings about an axis facing the camera; this is the middle-frame pose.
SLASH_AXIS=unit((1,0,.22));SLASH_PIVOT=(4.0,-11.5,25.0);PHI_UP=40.0;PHI_KEY=-86.0
# Whirl: pinwheel about +X through the blade's middle, pushed toward the camera.
WHIRL_PUSH=(7.0,0.0,4.0)


def table(points,s):
    for (s0,v0),(s1,v1) in zip(points,points[1:]):
        if s<=s1:return v0+(v1-v0)*(s-s0)/(s1-s0)
    return points[-1][1]


def centre(s):return (0.0,-CURVE*s*s,BASE[2]+LENGTH*s)
def across(s):
    t=unit((0,-2*CURVE*s,LENGTH));return (0.0,t[2],-t[1])


def blade_point(s,a,k):
    e,p,th=table(EDGE,s),table(SPINE,s),table(THICK,s)
    return add(add(centre(s),mul(across(s),-p+a*(p+e))),(th*k,0,0))


def boundary(i,a):return SHARDS[i]+JAG[i]*(a-.5)


def shard_centre(i):
    s=(SHARDS[i]+SHARDS[i+1])/2;return tuple(round(c,6) for c in blade_point(s,.4,0))


def mote_local(k,w):
    ang,h=MOTES[k];s=(h-BASE[2])/LENGTH;a=ang+w
    return (MOTE_R*math.cos(a),centre(s)[1]+MOTE_R*math.sin(a),h-BASE[2])


def qrot(ax,deg):return axis(ax,math.radians(deg))
def chain(*qs):
    q=(0,0,0,1)
    for x in qs:q=qmul(q,x)
    return q
def nlerp(a,b,t):
    if sum(x*y for x,y in zip(a,b))<0:b=tuple(-x for x in b)
    q=tuple(x+(y-x)*t for x,y in zip(a,b));n=math.sqrt(sum(x*x for x in q));return tuple(x/n for x in q)
def lerp(a,b,t):return tuple(x+(y-x)*t for x,y in zip(a,b))
def smooth(x):
    q=min(1,max(0,x));return q*q*(3-2*q)
def bump(t,c,w):return math.cos(min(1,abs(t-c)/w)*math.pi/2)**2


def slash_q(phi):return qmul(qrot(SLASH_AXIS,phi),qrot((0,1,0),8))


def trail_points():
    """Swept band of the slash between blade stations s=.45 and the point."""
    out=[]
    for i in range(15):
        u=i/14;phi=PHI_UP-18+(PHI_KEY-PHI_UP+18)*u;q=slash_q(phi)
        mid=add(SLASH_PIVOT,rotate(q,sub(centre(.76),BASE)))
        out.append((*mid,.25+7.2*u**1.6,phi))
    return out


def carry(t):
    """Idle hover (t in [0,1)): bob, forward lean, slow sway. Returns world loc, q."""
    w=math.tau*t
    loc=(.5*math.sin(w),.6*math.sin(2*w),BASE[2]+1.3*math.sin(w))
    q=chain(qrot((0,0,1),7*math.sin(w+1.9)),qrot((0,1,0),11+3*math.sin(w)),qrot((1,0,0),5*math.sin(w+.8)))
    return loc,q


def whirl_centre(loc,q):return add(loc,rotate(q,sub(centre(.5),BASE)))


RING_R=16.0;RING_W=4.2
LOC0,Q0=carry(0)
RING_C=add(whirl_centre(LOC0,Q0),WHIRL_PUSH)
SPECS=[('root',None,(0,0,0)),('blade','root',BASE)]
SPECS+=[(f'shard_{i}','blade',shard_centre(i)) for i in range(5)]
for k,pts in enumerate(WISPS):
    for j in range(4):SPECS.append((f'wisp_{k}_{j}','blade' if j==0 else f'wisp_{k}_{j-1}',pts[j][:3]))
SPECS+=[(f'mote_{k}','blade',add(BASE,mote_local(k,0))) for k in range(3)]


def _cage_box(points,margin=.6):
    return tuple(v for a in range(3) for v in (min(p[a] for p in points)-margin,max(p[a] for p in points)+margin))


def _trail_extent():
    pts=[]
    for x,y,z,r,phi in trail_points():
        rad=unit(sub((x,y,z),SLASH_PIVOT))
        pts+=[add((x,y,z),mul(rad,r)),add((x,y,z),mul(rad,-r))]
    return pts


TRAIL_BOX=_cage_box(_trail_extent())
RING_BOX=(RING_C[0]-1.2,RING_C[0]+1.2,RING_C[1]-RING_R-RING_W-.6,RING_C[1]+RING_R+RING_W+.6,
          RING_C[2]-RING_R-RING_W-.6,RING_C[2]+RING_R+RING_W+.6)
TRAIL_HEAD=trail_points()[-1][:3]
for cage,box in (('trail',TRAIL_BOX),('ring',RING_BOX)):
    for z in range(2):
        for y in range(2):
            for x in range(2):SPECS.append((f'{cage}_{z}{y}{x}','root',(box[x],box[2+y],box[4+z])))
RIG=Rig.from_world(SPECS);BONES,REST=RIG.bones,RIG.rest
IDS={n:i for i,(n,_,_) in enumerate(BONES)}
CLIPS=[('idle',40,20,True),('drift',24,24,True),('slash',19,35,False),('whirl',21,35,False),('recoil',13,35,False),('shatter',35,35,False)]


def quantize(weights):
    """Round to 1e-6 with math.fsum; the last influence takes the exact remainder."""
    weights=[(b,w) for b,w in weights if w>5e-7]
    head=[(b,round(w,6)) for b,w in weights[:-1]]
    rows=head+[(weights[-1][0],round(1-math.fsum(w for _,w in head),6))]
    return [(b,w) for b,w in rows if w>0]


def cage_weights(prefix,box,v,ids=None):
    """Freudenthal simplex weights in a corner cage: four affine-exact influences."""
    ids=ids or IDS
    f=[min(1,max(0,(v[a]-box[2*a])/(box[2*a+1]-box[2*a]))) for a in range(3)]
    order=sorted(range(3),key=lambda a:(f[a],-a),reverse=True);corners=[(0,0,0)];corner=[0,0,0]
    for a in order:corner=corner.copy();corner[a]=1;corners.append(tuple(corner))
    amounts=[1-f[order[0]],f[order[0]]-f[order[1]],f[order[1]]-f[order[2]],f[order[2]]]
    return quantize([(ids[f'{prefix}_{z}{y}{x}'],w) for (x,y,z),w in zip(corners,amounts)])


class Piece(Part):
    """Part with a paint role and per-vertex paint coordinates (pa, pv)."""
    def __init__(self,name,role):
        super().__init__(name);self.role=role;self.pa=[];self.pv=[]
    def add(self,co,a=0,v=0):
        self.vertices.append(tuple(round(c,6) for c in co));self.pa.append(a);self.pv.append(v);return len(self.vertices)-1


def rings(p,rows,closed_start=True,closed_end=True):
    """Quad strips between equal-length vertex rows; collapsed pole rows become triangles."""
    point=lambda row:len({p.vertices[i] for i in row})==1
    for r0,r1 in zip(rows,rows[1:]):
        for j in range(len(r0)-1):
            if point(r0):p.faces.append((r0[j],r1[j+1],r1[j]))
            elif point(r1):p.faces.append((r0[j],r0[j+1],r1[j]))
            else:p.faces.append((r0[j],r0[j+1],r1[j+1],r1[j]))
    for ring,start in ((rows[0],True),(rows[-1],False)):
        if (closed_start if start else closed_end) and not point(ring):
            c=[p.vertices[i] for i in ring[:-1]]
            centre_=p.add(tuple(math.fsum(x)/len(c) for x in zip(*c)),p.pa[ring[0]],.5)
            for j in range(len(ring)-1):p.faces.append((centre_,ring[j+1],ring[j]) if start else (centre_,ring[j],ring[j+1]))


def tube(name,controls,role,sides=10,samples=3,flatten=1.0,up=(0,0,1),caps=True):
    """Swept ellipse along a Catmull-Rom path; controls are (x, y, z, radius)."""
    p=Piece(name,role);pts=spline(controls,samples) if samples>1 else [tuple(c) for c in controls];rows=[];prev=None
    for i,row in enumerate(pts):
        c,r=row[:3],max(.02,row[3]);t=unit(sub(pts[min(i+1,len(pts)-1)][:3],pts[max(0,i-1)][:3]))
        if prev is None:n=unit(cross(t,up if abs(sum(a*b for a,b in zip(t,up)))<.9 else (0,1,0)))
        else:n=unit(sub(prev,mul(t,sum(a*b for a,b in zip(prev,t)))))
        prev=n;bn=unit(cross(t,n));u=i/(len(pts)-1);idx=[]
        for j in range(sides+1):
            ang=math.tau*j/sides
            idx.append(p.add(add(c,add(mul(n,r*math.cos(ang)),mul(bn,r*flatten*math.sin(ang)))),u,j/sides))
        rows.append(idx)
    rings(p,rows,caps,caps)
    return p


def ball(name,c,r,role,seg=10,rings_=5):
    p=Piece(name,role);rows=[]
    for i in range(rings_+1):
        ph=-math.pi/2+math.pi*i/rings_;row=[]
        for j in range(seg+1):
            th=math.tau*j/seg
            row.append(p.add((c[0]+r[0]*math.cos(ph)*math.cos(th),c[1]+r[1]*math.cos(ph)*math.sin(th),c[2]+r[2]*math.sin(ph)),j/seg,i/rings_))
        rows.append(row)
    rings(p,rows,False,False)
    return p


def build_parts():
    """Source parts with their paint roles and bone bindings (bone, weight function)."""
    out=[]
    def put(p,bone=None,weights=None):
        p.skin_weights=[weights(v) for v in p.vertices] if weights else [[(IDS[bone],1)]]*len(p.vertices)
        out.append(p);return p
    # ---- Five jagged shards form one continuous curved blade at rest.
    for i in range(5):
        p=Piece(f'blade_shard_{i}','blade');n=max(3,round((SHARDS[i+1]-SHARDS[i])*46));rows=[]
        for r in range(n+1):
            row=[]
            for a,k in SECTION:
                s=boundary(i,a)+(boundary(i+1,a)-boundary(i,a))*r/n
                row.append(p.add(blade_point(s,a,k),a,s))
            rows.append(row)
        rings(p,rows)
        put(p,f'shard_{i}')
    # ---- A dim glow envelope hugs each shard so the thin blade keeps presence at distance.
    for i in range(5):
        s0=-.05 if i==0 else SHARDS[i];s1=1.08 if i==4 else SHARDS[i+1]
        p=Piece(f'glow_envelope_{i}','aura');n=max(3,round((s1-s0)*30));rows=[]
        for r in range(n+1):
            s=s0+(s1-s0)*r/n;sc=min(1,max(0,s))
            e,sp=table(EDGE,sc),table(SPINE,sc)
            taper=min(1,max(0,(1.08-s)/.16))**.55*min(1,max(0,(s+.05)/.1))**.5
            mid=(e-sp)/2;hw=((e+sp)/2+1.6)*taper;ht=1.15*taper
            base=add(centre(s),mul(across(sc),mid));row=[]
            for j in range(15):
                ang=math.tau*j/14
                row.append(p.add(add(add(base,mul(across(sc),hw*math.cos(ang))),(-ht*math.sin(ang),0,0)),j/14,min(1,max(0,s))))
            rows.append(row)
        rings(p,rows,i==0,i==4)
        put(p,f'shard_{i}')
    # ---- Hilt-less base: a bright core wrapped by a tilted ring of light.
    put(ball('knot_core',(0,-.1,BASE[2]-.4),(1.9,1.9,2.3),'core',12,6),'blade')
    ring=[(3.6*math.cos(a*math.tau/24),.3+3.6*math.sin(a*math.tau/24),BASE[2]+.2+1.1*math.sin(a*math.tau/24),.5) for a in range(25)]
    put(tube('knot_ring',ring,'core',8,1),'blade')
    # ---- Three streaming flame-wisps: the comet tail that replaces a grip.
    for k,pts in enumerate(WISPS):
        ids=[IDS[f'wisp_{k}_{j}'] for j in range(4)]
        put(tube(f'wisp_{k}',pts,'wisp',10,4,.42,(0,1,0)),None,lambda v,ids=ids:quantize(RIG.chain_weights(v,ids)))
    # ---- Orbiting motes.
    for k in range(3):
        put(ball(f'mote_{k}',add(BASE,mote_local(k,0)),(.75,.75,1.35),'mote',4,2),f'mote_{k}')
    # ---- Attack-only light trails in corner cages.
    tp=trail_points()
    put(tube('slash_trail',[t[:4] for t in tp],'trail',12,3,.05,SLASH_AXIS),None,lambda v:cage_weights('trail',TRAIL_BOX,v))
    circle=[(RING_C[0],RING_C[1]+RING_R*math.cos(a*math.tau/48),RING_C[2]+RING_R*math.sin(a*math.tau/48),RING_W) for a in range(49)]
    put(tube('whirl_ring',circle,'ring',12,1,.05,(1,0,0),caps=False),None,lambda v:cage_weights('ring',RING_BOX,v))
    for p in out:
        for v in p.vertices:
            if p.name=='slash_trail':assert all(TRAIL_BOX[2*a]-1e-6<=v[a]<=TRAIL_BOX[2*a+1]+1e-6 for a in range(3)),v
            if p.name=='whirl_ring':assert all(RING_BOX[2*a]-1e-6<=v[a]<=RING_BOX[2*a+1]+1e-6 for a in range(3)),v
    return out


def geometry():
    parts=build_parts()
    for p in parts:p.uv=[materials.uv(p.role,a,b) for a,b in zip(p.pa,p.pv)]
    return assemble(parts,lambda p,v,u:[(0,1)])


# ---------------------------------------------------------------- poses
FLOOR=[((5.5,-11.5,1.8),28),((-6.0,7.0,1.75),-64),((11.0,9.0,1.65),112),((-10.5,-5.0,1.55),14),((2.0,16.5,1.4),-26)]
BURST=[((.5,-1.0,-.45),11.0,((0,1,0),80)),((.3,1.0,-.15),12.0,((1,0,0),-95)),((.4,-1.0,.3),13.0,((0,0,1),110)),
       ((.2,1.0,.5),12.5,((1,1,0),-120)),((.5,-.2,1.0),9.0,((1,0,1),150))]
Q_FLAT=qrot((0,1,0),-90)
DEATH_CURL=[(62,-4),(40,-10),(40,-10)]   # wisps sag back onto the floor


def pose(name,t):
    f=[[*local,0,0,0,1,1,1,1] for _,_,local in BONES]
    loc,q=carry(t if name=='idle' else 0)
    w=math.tau*(t if name=='idle' else 0)
    wisp=[[0.0,0.0] for _ in range(12)]   # (about local Y, about local Z) per chain bone
    for k in range(3):
        for j in range(4):
            wisp[k*4+j]=[9*math.sin(2*w-.9*j+2.1*k),10*math.sin(3*w-1.1*j+1.3*k)]
    motes=[mote_local(k,w) for k in range(3)]
    trail=0.0;ring=0.0;world={}
    if name=='drift':
        w=math.tau*t
        loc=(1.2*math.sin(w),.8*math.sin(2*w),BASE[2]+2.2+1.0*math.sin(2*w))
        q=chain(qrot((0,0,1),5*math.sin(w)),qrot((0,1,0),40+4*math.sin(2*w)),qrot((1,0,0),7*math.sin(w+.6)))
        for k in range(3):
            for j in range(4):wisp[k*4+j]=[(-16 if j==0 else -6)+11*math.sin(4*w-1.2*j+2.1*k),14*math.sin(2*w-1.3*j+k)]
        motes=[add(mote_local(k,w),(-2.5,0,0)) for k in range(3)]
    elif name=='slash':
        up=smooth(t/.32);swing=min(1,max(0,(t-.32)/.18));follow=smooth((t-.5)/.14);back=smooth((t-.64)/.36)
        if t<=.32:
            phi,pv=PHI_UP,SLASH_PIVOT;cock=(-1.5,1.0,22.0)
            loc=lerp(LOC0,cock,up);q=nlerp(Q0,slash_q(PHI_UP),up)
        else:
            phi=PHI_UP+(PHI_KEY-PHI_UP)*swing**1.35 if t<=.5 else PHI_KEY-22*follow
            loc=lerp((-1.5,1.0,22.0),SLASH_PIVOT,smooth(swing*1.2)) if t<=.5 else add(SLASH_PIVOT,(1.5*follow,1.0*follow,-.8*follow))
            q=slash_q(phi)
            if t>.64:loc=lerp(loc,LOC0,back);q=nlerp(q,Q0,back)
        g=bump(t,.5,.3)
        for k in range(3):
            for j in range(4):wisp[k*4+j][0]+=-18*g;wisp[k*4+j][1]+=(14 if k!=2 else 8)*g
        trail=bump(t,.5,.17)
    elif name=='whirl':
        if t<.18:psi=-25*smooth(t/.18)
        elif t<=.5:u=(t-.18)/.32;psi=-25+565*u**1.5
        elif t<=.8:u=(t-.5)/.3;psi=540+180*(1-(1-u)**2)
        else:psi=720
        push=bump(t,.5,.34);settle=smooth((t-.8)/.2)
        c0=whirl_centre(LOC0,Q0);cq=qrot((1,0,0),-psi)
        centre_now=add(c0,mul(WHIRL_PUSH,push))
        loc=add(centre_now,rotate(cq,sub(LOC0,c0)));q=qmul(cq,Q0)
        if t>.8:loc=lerp(loc,LOC0,settle);q=nlerp(q,Q0,settle)
        g=bump(t,.5,.42)
        for k in range(3):
            for j in range(4):wisp[k*4+j][0]+=(20 if j<2 else 12)*g
        ring=bump(t,.5,.2)
    elif name=='recoil':
        g=bump(t,.5,.5);s=math.sin(t*math.pi*4)*g
        loc=add(LOC0,(-4.5*g,2.2*s,3.5*g));q=chain(qrot((0,1,0),-52*g),qrot((1,0,0),16*s+10*g),Q0)
        for k in range(3):
            for j in range(4):wisp[k*4+j][0]+=24*g*(1 if j<2 else .5)
    elif name=='shatter':
        tremble=smooth(t/.1)*(1-smooth((t-.2)/.06));rise=smooth(t/.2)
        burst=smooth((t-.2)/.3);fall=min(1,max(0,(t-.5)/.32));land=smooth((t-.82)/.18)
        hover=add(LOC0,(0,0,2.6*rise))
        qh=chain(qrot((1,0,0),7*math.sin(t*95)*tremble),qrot((0,0,1),5*math.sin(t*71)*tremble),Q0)
        for i in range(5):
            lb=add(hover,rotate(qh,sub(shard_centre(i),BASE)))
            d,dist,(tax,tdeg)=BURST[i];crack=.35*smooth(t/.2)
            lburst=add(lb,mul(unit(d),crack+dist*burst));qburst=qmul(qrot(tax,tdeg*burst),qh)
            (fx,fy,fz),yaw=FLOOR[i]
            if fall<=0:wl,wq=lburst,qburst
            else:
                hz=lburst[2]+(fz-lburst[2])*fall*fall
                wl=(lburst[0]+(fx-lburst[0])*fall,lburst[1]+(fy-lburst[1])*fall,hz)
                wq=nlerp(qburst,qmul(qrot((0,0,1),yaw),Q_FLAT),smooth(fall*1.1))
            if t>.82:wl=add(wl,(0,0,.9*math.sin(math.pi*min(1,(t-.82)/.12))*(1-land)))
            world[f'shard_{i}']=(wl,wq)
        # The knot flares upward at the burst, then drops; the wisps curl and lie flat.
        pop=bump(t,.46,.14)
        top=add(hover,(0,0,2.0*pop))
        floor_loc=(-1.0,1.5,2.9);floor_q=qrot((0,0,1),20)
        loc=(top[0]+(floor_loc[0]-top[0])*fall,top[1]+(floor_loc[1]-top[1])*fall,top[2]+(floor_loc[2]-top[2])*fall*fall)
        q=nlerp(qh,floor_q,smooth(fall))
        if t>.82:loc=add(loc,(0,0,.5*math.sin(math.pi*min(1,(t-.82)/.12))*(1-land)))
        curl=smooth((t-.3)/.55)
        for k in range(3):
            for j in range(4):
                a0,b0=wisp[k*4+j];wisp[k*4+j]=[a0*(1-curl)+(DEATH_CURL[k][0] if j==0 else DEATH_CURL[k][1])*curl,b0*(1-curl)+(10*(k-1))*curl]
        for k in range(3):
            ang=MOTES[k][0]
            fl=(-3+7*math.cos(ang*2.3),-2+11*math.sin(ang*1.7+.5),.95)
            lb=add(hover,rotate(qh,motes[k]))
            wl=lerp(lb,add(lb,(0,0,1.5)),burst)
            wl=(wl[0]+(fl[0]-wl[0])*fall,wl[1]+(fl[1]-wl[1])*fall,wl[2]+(fl[2]-wl[2])*fall*fall)
            world[f'mote_{k}']=(wl,nlerp(qmul(qh,qrot((0,0,1),40*k)),qmul(qrot((0,0,1),30*k),qrot((1,0,0),90)),smooth(fall)))
    # ---- Write bone rows.
    f[IDS['blade']][:3]=list(loc);f[IDS['blade']][3:7]=list(q)
    for k in range(3):
        for j in range(4):
            a,b=wisp[k*4+j];f[IDS[f'wisp_{k}_{j}']][3:7]=list(chain(qrot((0,0,1),b),qrot((0,1,0),a)))
        f[IDS[f'mote_{k}']][:3]=list(motes[k]);f[IDS[f'mote_{k}']][3:7]=list(qrot((0,0,1),math.degrees(w)*2+40*k))
    for bone,(wl,wq) in world.items():
        iq=inverse(q);f[IDS[bone]][:3]=list(rotate(iq,sub(wl,loc)));f[IDS[bone]][3:7]=list(qmul(iq,wq))
    def cage(prefix,box,point,k):
        for z in range(2):
            for y in range(2):
                for x in range(2):
                    c=(box[x],box[2+y],box[4+z]);f[IDS[f'{prefix}_{z}{y}{x}']][:3]=list(add(point,mul(sub(c,point),k)))
    cage('trail',TRAIL_BOX,TRAIL_HEAD,trail);cage('ring',RING_BOX,RING_C,ring)
    return [tuple(r) for r in f]


def matrices(frame):return RIG.matrices(frame)
def deform(v,w,frame):return RIG.deform(v,w,frame)
def animation_data(v,w):return sample_clips(RIG,CLIPS,pose,v,w)
def texture_bytes():return materials.texture_bytes()


def build():
    skin=texture_bytes();(ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts,v,n,uv,t,w=geometry();clips,bounds=animation_data(v,w)
    data=iqm.encode(v,n,uv,t,w,BONES,clips,bounds,mesh_label='Project_Broom_spectral_blade',material_path=SKIN)
    path=ROOT/MODEL;path.write_bytes(data)
    manifest=dict(schemaVersion=1,workId='BRG-M55',format='IQM v2',runtimeModel=MODEL,
        sha256=hashlib.sha256(data).hexdigest(),skin=SKIN,skinSha256=hashlib.sha256(skin).hexdigest(),
        dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],
        parts=len(parts),vertices=len(v),triangles=len(t),boneCount=len(BONES),
        bones=[dict(name=n_,parent=p,local=l) for n_,p,l in BONES],
        clips=[{k:x for k,x in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],
        poseBounds=bounds,emissive=dict(additive=True,shader='shaders/spectral-blade-glow.fp'),
        authoringSource='assets/monsters/spectral_blade/spectral-blade-animated.blend')
    out=ROOT/'assets/monsters/spectral_blade';out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__':
    from tools.monster_models import spectral_blade_animation as _self
    print(_self.build()['sha256'])

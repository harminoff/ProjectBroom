"""Original living-flame flamedancer for Brogue's MK_FLAMEDANCER (presentation only).

Brogue: "An elemental creature from another plane of existence, the infernal
flamedancer burns with such intensity that [it] is painful to behold." It is a white
'F' with a fire corona, immune to fire, fiery, keeps its distance and casts fire
bolts; its hits burn ("singes", "burns", "immolates"). The model is therefore not a
person painted orange: it is a spiral column of fire, a white-hot core and a bright
head with dark eye slits, two ribbon arms that end in finger-flames, a swirling flame
skirt and drifting sparks, all drawn fullbright.

One 4x4x9 free-form lattice of bones (the wisp / flame turret affine-cage technique)
carries every vertex with exact Freudenthal weights. Every bone keeps unit scale, so a
death can collapse the whole cage to a point: the fire is fully extinguished. Brogue
owns spawning, flight, distance keeping, bolts, burning, damage and timing; nothing
here creates gameplay state.
"""
import hashlib,json,math
from . import iqm
from .rat import ROOT,Part,add,sub,mul,cross,unit,spline
from .skeletal import Rig,assemble,sample_clips
from . import flamedancer_materials as materials

SKIN='graphics/BRGFDANC.png'
MODEL='mod/BrogueDoom/models/monsters/54_flamedancer.iqm'
SHADER='mod/BrogueDoom/shaders/flamedancer-fire.fp'
HEIGHT=68.0
XS=(-32.0,-32/3,32/3,32.0);YS=XS;ZS=tuple(round(HEIGHT*k/8,6) for k in range(9))

SPECS=[('root',None,(0,0,0))]
for k,z in enumerate(ZS):
    for j,y in enumerate(YS):
        for i,x in enumerate(XS):SPECS.append((f'f_{k}_{j}_{i}','root',(round(x,6),round(y,6),z)))
# Cast fireball cage: eight corner bones that collapse to a point (extinguished) in every clip but `bolt`.
FB_C=(17.0,0.0,40.0);FB_BOX=(6.0,28.0,-11.0,11.0,29.0,51.0)
for z in range(2):
    for y in range(2):
        for x in range(2):SPECS.append((f'fb_{z}{y}{x}','root',(FB_BOX[x],FB_BOX[2+y],FB_BOX[4+z])))
RIG=Rig.from_world(SPECS);BONES,REST=RIG.bones,RIG.rest
IDS={n:i for i,(n,_,_) in enumerate(BONES)}
CLIPS=[('idle',48,24,True),('dance',32,35,True),('sear',24,35,False),('bolt',26,35,False),
       ('recoil',14,35,False),('gutter',36,35,False)]


def quantize(weights):
    """Round to 1e-6 with math.fsum; the last influence takes the exact remainder."""
    weights=[(b,w) for b,w in weights if w>5e-7]
    head=[(b,round(w,6)) for b,w in weights[:-1]]
    rows=head+[(weights[-1][0],round(1-math.fsum(w for _,w in head),6))]
    return [(b,w) for b,w in rows if w>0]


def _cell(axis,value):
    i=0
    while i<len(axis)-2 and value>axis[i+1]:i+=1
    return i,min(1,max(0,(value-axis[i])/(axis[i+1]-axis[i])))


def fireball_weights(p):
    f=[min(1,max(0,(p[a]-FB_BOX[2*a])/(FB_BOX[2*a+1]-FB_BOX[2*a]))) for a in range(3)]
    order=sorted(range(3),key=lambda a:(f[a],-a),reverse=True);corner=[0,0,0];cells=[(0,0,0)]
    for a in order:corner=corner.copy();corner[a]=1;cells.append(tuple(corner))
    amounts=[1-f[order[0]],f[order[0]]-f[order[1]],f[order[1]]-f[order[2]],f[order[2]]]
    return quantize([(IDS[f'fb_{z}{y}{x}'],w) for (x,y,z),w in zip(cells,amounts)])


def lattice_weights(p):
    (i,fx),(j,fy),(k,fz)=_cell(XS,p[0]),_cell(YS,p[1]),_cell(ZS,p[2]);f=[fx,fy,fz]
    order=sorted(range(3),key=lambda a:(f[a],-a),reverse=True);corner=[0,0,0];cells=[(0,0,0)]
    for a in order:corner=corner.copy();corner[a]=1;cells.append(tuple(corner))
    amounts=[1-f[order[0]],f[order[0]]-f[order[1]],f[order[1]]-f[order[2]],f[order[2]]]
    return quantize([(IDS[f'f_{k+dz}_{j+dy}_{i+dx}'],w) for (dx,dy,dz),w in zip(cells,amounts)])


class Piece(Part):
    """Part with a paint role and per-vertex paint coordinates (pa, pv)."""
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
            centre_=p.add(tuple(math.fsum(x)/len(c) for x in zip(*c)),p.pa[ring[0]],.5)
            for j in range(len(ring)-1):p.faces.append((centre_,ring[j+1],ring[j]) if start else (centre_,ring[j],ring[j+1]))


def tube(name,controls,role,sides=10,samples=3,flatten=1.0,up=(0,0,1)):
    """Swept ellipse along a Catmull-Rom path; controls are (x, y, z, radius)."""
    p=Piece(name,role);pts=spline(controls,samples);rows=[];prev=None
    for i,row in enumerate(pts):
        c,r=row[:3],max(.02,row[3]);t=unit(sub(pts[min(i+1,len(pts)-1)][:3],pts[max(0,i-1)][:3]))
        if prev is None:n=unit(cross(t,up if abs(sum(a*b for a,b in zip(t,up)))<.9 else (0,1,0)))
        else:n=unit(sub(prev,mul(t,sum(a*b for a,b in zip(prev,t)))))
        prev=n;bn=unit(cross(t,n));u=i/(len(pts)-1);idx=[]
        for j in range(sides+1):
            ang=math.tau*j/sides
            idx.append(p.add(add(c,add(mul(n,r*math.cos(ang)),mul(bn,r*flatten*math.sin(ang)))),u,j/sides))
        rows.append(idx)
    rings(p,rows)
    return p


def ball(name,c,r,role,seg=12,rings_=6,turn=math.pi):
    """Ellipsoid; with turn=pi the paint coordinate a=.5 faces +X."""
    p=Piece(name,role);rows=[]
    for i in range(rings_+1):
        ph=-math.pi/2+math.pi*i/rings_;row=[]
        for j in range(seg+1):
            th=math.tau*j/seg+turn
            row.append(p.add((c[0]+r[0]*math.cos(ph)*math.cos(th),c[1]+r[1]*math.cos(ph)*math.sin(th),c[2]+r[2]*math.sin(ph)),j/seg,1-i/rings_))
        rows.append(row)
    rings(p,rows,False,False)
    return p


def tongue_radius(s,r0):return r0*(1-s**1.35)**.8*(.86+.14*math.sin(7*s+1.0))


def tongue(name,role,path,r0,rows=13,sides=9,flatten=.56):
    ctrl=[]
    for i in range(rows+1):
        s=i/rows;x,y,z=path(s);ctrl.append((x,y,z,tongue_radius(s,r0)))
    return tube(name,ctrl,role,sides,1,flatten)


def envelope(z):return 2.5+8.5*math.sin(math.pi*min(1,max(0,z/62)) ** .8)


def helix(theta0,z0,zt,turns,swell=1.0,lean=(0.0,0.0)):
    def path(s):
        z=z0+(zt-z0)*s;rho=max(.3,envelope(z)*swell*(1-.62*s*s));th=theta0+turns*math.tau*s
        return (rho*math.cos(th)+lean[0]*s*s,rho*math.sin(th)+lean[1]*s*s,z)
    return path


def curve(points):
    dense=spline([tuple(p) for p in points],10)
    def path(s):
        f=min(len(dense)-1.000001,max(0,s*(len(dense)-1)));i=int(f);u=f-i
        return tuple(dense[i][a]+(dense[i+1][a]-dense[i][a])*u for a in range(3))
    return path


def build_parts():
    out=[]
    # ---- Hot core column, mostly hidden inside the spiral tongues but seen through gaps.
    core=[(0,0,3,2.6),(0,0,9,6.2),(0,0,20,7.0),(0,0,33,5.4),(0,0,42,3.4),(1.5,0,47,1.4)]
    out.append(tube('hot_core',core,'core',14,3,1.0,(1,0,0)))
    # ---- Twelve spiralling column tongues of unequal height, tips flicking upward.
    tips=[62,54,58,48,53,44,57,41,50,46,60,38]
    for k,zt in enumerate(tips):
        th=k*2.399963;z0=2+(k*5)%9
        base=helix(th,z0,zt,1.05+.12*(k%4),1.0+.05*(k%3),(-4.5,0))
        def path(s,base=base,zt=zt):
            x,y,z=base(s);return (x,y,z+3.5*s**3)
        out.append(tongue(f'column_tongue_{k}','flame',path,7.4-.22*(k%5),13,9,.5))
    # ---- Side licks: short flames thrown off the column so the silhouette bristles, not drapes.
    for k in range(11):
        z0=8+k*4.4;th=k*2.399963+.7
        def path(s,z0=z0,th=th,k=k):
            rho=envelope(z0)*.8+8.5*s**.9;a=th+.5*s;return (rho*math.cos(a)-1.5*s,rho*math.sin(a),z0+8.5*s**1.2+2.5*math.sin(3*s+k))
        out.append(tongue(f'side_lick_{k}','flame',path,2.9-.06*k,9,7,.55))
    # ---- Bright head with angry dark eye slits (+X front), and back-swept crown flames.
    out.append(ball('head',(2.4,0,49.0),(4.4,4.1,5.6),'head',16,8))
    for k,(ang,tz,tx,ty) in enumerate([(0.0,69,-12,0),(2.1,65,-7,8),(-2.1,64,-7,-8),(1.0,61,-2,5),(-1.0,60,-2,-5)]):
        bx=2.0+2.4*math.cos(ang+math.pi);by=3.6*math.sin(ang)
        def path(s,bx=bx,by=by,tz=tz,tx=tx,ty=ty):
            return (bx+(tx-bx)*s-2.4*math.sin(math.pi*s),by+(ty-by*0.2)*s*(0.6+0.4*s),51+(tz-51)*s+1.2*math.sin(3*s))
        out.append(tongue(f'crown_flame_{k}','flame',path,3.4-.25*k,10,8,.62))
    # ---- Ribbon arms of fire ending in finger-flames: one raised in an arc, one flung wide.
    arms={'L':[(0,-4,40),(-1.5,-11,42),(-3.5,-18,49),(-2,-21,58)],'R':[(0,4,40),(3,12,37),(7,17,33),(9,21,26)]}
    for side,pts in arms.items():
        out.append(tongue(f'arm_{side}','flame',curve(pts+[(pts[-1][0]+(1.2 if side=='L' else 3),pts[-1][1]+(-1 if side=='L' else 2),pts[-1][2]+(4 if side=='L' else -3))]),4.6,14,9,.5))
        tip=pts[-1];sgn=-1 if side=='L' else 1
        for f,(dx,dy,dz) in enumerate([(-1,2.4*sgn,8.5),(3.4,3.8*sgn,6.0),(-4,-.4*sgn,6.2)] if side=='L' else [(4,3.5,-2.5),(8.2,2.0,3.2),(1.0,5.4,3.8)]):
            def path(s,tip=tip,d=(dx,dy,dz)):return (tip[0]+d[0]*s,tip[1]+d[1]*s,tip[2]+d[2]*s+1.5*math.sin(2.5*s))
            out.append(tongue(f'finger_flame_{side}{f}','flame',path,1.9,8,7,.7))
    # ---- Flame skirt: eight low tongues thrown outward in a swirl.
    for k in range(8):
        th=k*math.tau/8+.2
        def path(s,th=th,k=k):
            rho=6+15*s**.85+1.5*math.sin(k);a=th+1.1*s;return (rho*math.cos(a),rho*math.sin(a),2.2+13*s**1.25+1.6*math.sin(4*s+k))
        out.append(tongue(f'skirt_flame_{k}','flame',path,4.6-.12*(k%3),11,8,.5))
    # ---- Cast fireball: sits inside the column at rest (seen only as a hot core through the gaps)
    # and is carried out between the hands by the lattice during `bolt`.
    fb=ball('fireball',FB_C,(4.4,4.4,4.4),'ember',12,6);fb.pa=[.5]*len(fb.pa);fb.pv=[.05]*len(fb.pv);out.append(fb)
    for k,(dx,dy,dz) in enumerate([(1,0,.15),(.7,.7,.2),(.7,-.7,.2),(.6,0,.9),(.6,.5,-.7),(.6,-.5,-.7)]):
        def path(s,d=(dx,dy,dz)):return (FB_C[0]+d[0]*6.8*s,FB_C[1]+d[1]*6.8*s,FB_C[2]+d[2]*6.8*s)
        lick=tongue(f'fireball_lick_{k}','ember',path,2.3,7,7,.8);lick.pa=[.5]*len(lick.pa);lick.pv=[.12]*len(lick.pv);out.append(lick)
    # ---- Drifting sparks.
    for k,(x,y,z,r) in enumerate([(14,-9,22,1.3),(-12,12,33,1.0),(9,13,45,1.2),(-15,-8,49,.9),(12,7,57,1.0),(-6,-16,14,1.1),(11,-14,38,.8),(-9,4,64,1.1)]):
        out.append(ball(f'spark_{k}',(x,y,z),(r,r,r*1.35),'spark',6,3))
    return out


def geometry():
    parts=build_parts()
    for p in parts:
        p.uv=[materials.uv(p.role,a,b) for a,b in zip(p.pa,p.pv)]
        p.vertices=[(min(31.5,max(-31.5,x)),min(31.5,max(-31.5,y)),min(HEIGHT-.05,max(.05,z))) for x,y,z in p.vertices]
    return assemble(parts,lambda part,v,u:fireball_weights(v) if part.name.startswith('fireball') else lattice_weights(v))


# ---------------------------------------------------------------- motion
def smooth(x):
    q=min(1,max(0,x));return q*q*(3-2*q)
def bump(t,c,w):return math.cos(min(1,abs(t-c)/w)*math.pi/2)**2
def lerp(a,b,t):return tuple(x+(y-x)*t for x,y in zip(a,b))
def clamp(x,a=0,b=1):return min(b,max(a,x))


def swirl(p,angle):
    c,s=math.cos(angle),math.sin(angle);return (p[0]*c-p[1]*s,p[0]*s+p[1]*c,p[2])


def arm_weight(p):
    """Lattice nodes carrying the arms: outer columns at shoulder-to-hand height."""
    return clamp((abs(p[1])-6)/14)*clamp((p[2]-22)/12)*clamp((70-p[2])/10)


def field(p,name,t):
    """Displacement-free target position of a lattice node."""
    x,y,z=p;h=z/HEIGHT;ph=math.tau*t
    if name in ('idle','dance'):
        k=1.0 if name=='idle' else 2.4;w=ph if name=='idle' else 2*ph
        x,y,_=swirl(p,.20*k*h*math.sin(w-2.2*h))
        x+=(2.4*h*h*math.sin(w)+(0 if name=='idle' else 4.6*h*h))*k;y+=(2.0*k*h*h)*math.cos(w-.7)+(0 if name=='idle' else 3.0*h*math.sin(w+1.2))
        z+=1.7*k*h*math.sin(2*w-5*h)+(1.6*abs(math.sin(w)) if name=='dance' else 0)
        z+=arm_weight(p)*2.4*k*math.sin(2*w+p[1]*.18)
        return (x,y,z)
    if name=='sear':
        wind=bump(t,.18,.18);strike=bump(t,.52,.2)
        x,y,z=swirl(p,-.55*strike*h+.25*wind*h)
        aw=arm_weight(p)
        x+=-6*wind*h+strike*(9*h**1.2+9*aw);y+=(1 if p[1]>0 else -1)*strike*3.5*aw
        z=z*(1-.30*strike)+strike*(5*aw)
        if p[2]<20:
            r=1+.20*strike;x*=r;y*=r
        return (x,y,z)
    if name=='bolt':
        gather=bump(t,.26,.2);cast=bump(t,.56,.2)
        aw=arm_weight(p);sg=1 if p[1]>0 else -1
        ic=clamp(1-(max(abs(x),abs(y))-32/3)/10)                      # interior column nodes
        x,y,z=p
        r=1+.5*cast*ic+.06*cast*(1-ic)+.08*gather*ic+.16*cast*max(0,1-2.2*h)*(1-ic)
        x*=r;y*=r
        fb=ic*math.exp(-((z-40)/9)**2)*(1 if p[0]>0 else .5)          # front nodes that carry the fireball
        x+=-6*gather*h+cast*(9*h**1.2+14*aw)
        y+=-sg*cast*11*aw
        z=z*(1-.05*cast)+cast*3*aw
        return swirl((x,y,z),.10*cast*h)
    if name=='recoil':
        g=bump(t,.5,.5);s=math.sin(t*math.pi*4)*g
        return (x-8*g*h+2*s,y+3*s*h,z*(1-.16*g)-1.5*g)
    if name=='gutter':
        flare=bump(t,.1,.1);a=smooth((t-.06)/.42);b=smooth((t-.58)/.4)
        x,y,z=swirl(p,.3*a*math.sin(t*9)*h)
        r=1+(.20*a+.08*flare)*(1-.35*h)
        x*=r;y*=r;z=z*(1+.03*flare)*(1-.83*a)+.9*a*abs(math.sin(x*.4+y*.3))
        x+=.6*a*math.sin(t*23+z);
        # Collapse to a point: complete extinction, no living shape remains.
        k=1e-5 if t>=.999 else 1-b*.99999
        return (x*k,y*k,2.0+(z-2.0)*k)
    raise KeyError(name)


def pose(name,t):
    rows=[(0,0,0,0,0,0,1,1,1,1)]
    cast=bump(t,.56,.2) if name=='bolt' else 0.0
    sc=1e-5+1.5*smooth(cast) if cast>.02 else 1e-5
    centre=lerp((3.0,0.0,40.0),(19.5,0.0,42.0),smooth(cast)) if cast>.02 else (0.0,0.0,2.0)
    for b in range(1,len(BONES)):
        if BONES[b][0].startswith('fb_'):
            x,y,z=(centre[a]+(REST[b][a]-FB_C[a])*sc for a in range(3))
        else:x,y,z=field(REST[b],name,t)
        rows.append((round(x,6),round(y,6),round(z,6),0,0,0,1,1,1,1))
    return rows


def matrices(frame):return RIG.matrices(frame)
def deform(v,w,frame):return RIG.deform(v,w,frame)
def animation_data(v,w):return sample_clips(RIG,CLIPS,pose,v,w)
def texture_bytes():return materials.texture_bytes()


def build():
    skin=texture_bytes();(ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts,v,n,uv,t,w=geometry();clips,bounds=animation_data(v,w)
    data=iqm.encode(v,n,uv,t,w,BONES,clips,bounds,mesh_label='Project_Broom_flamedancer',material_path=SKIN)
    path=ROOT/MODEL;path.write_bytes(data)
    manifest=dict(schemaVersion=1,workId='BRG-M54',format='IQM v2',runtimeModel=MODEL,
        sha256=hashlib.sha256(data).hexdigest(),skin=SKIN,skinSha256=hashlib.sha256(skin).hexdigest(),
        dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],
        parts=len(parts),vertices=len(v),triangles=len(t),boneCount=len(BONES),
        bones=[dict(name=n_,parent=p,local=l) for n_,p,l in BONES],
        clips=[{k:x for k,x in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],
        poseBounds=bounds,fullbrightShader='shaders/flamedancer-fire.fp',
        authoringSource='assets/monsters/flamedancer/flamedancer-animated.blend')
    out=ROOT/'assets/monsters/flamedancer';out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__':
    from tools.monster_models import flamedancer_animation as _self
    print(_self.build()['sha256'])

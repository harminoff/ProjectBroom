"""Original crimson spectral sword for Brogue's MK_SPECTRAL_IMAGE (presentation only).

In Brogue a weapon with the multiplicity runic flashes and projects spectral
duplicates of the wielder's weapon ("Eldritch energies bound up in your equipment
have leapt forth to project this spectral image."); the catalog names it "spectral
sword". The model is therefore a recognisable hilted broadsword - straight
double-edged blade, fuller, curved crossguard with a front gem, wrapped grip, wheel
pommel - rendered as a crimson projected image with scanlines, hovering point-down.
Two fainter echo after-images trail it. Each echo sits in an affine corner cage
(the flame turret's technique) and replays the sword's own motion slightly late,
so a fast swing leaves a fan of three swords and a thrust leaves a staggered line.
At death the echoes fly apart and collapse to zero area with unit bone scales
while the sword drops and clatters flat on the floor.

This is visibly distinct from the blue, curved, hilt-less spectral blade. Brogue owns
summoning, lifespan, flight, negation, attacks and timing; this file only draws.
"""
import hashlib,json,math
from . import iqm
from .rat import ROOT,add,sub,mul,unit
from .skeletal import Rig,qmul,inverse,rotate,assemble,sample_clips
from . import spectral_sword_materials as materials
from .spectral_blade_animation import (Piece,rings,tube,ball,quantize,cage_weights,table,
                                       qrot,chain,nlerp,lerp,smooth,bump)

SKIN='graphics/BRGSSWRD.png'
MODEL='mod/BrogueDoom/models/monsters/56_spectral_image.iqm'
SHADER='mod/BrogueDoom/shaders/spectral-sword-glow.fp'
GZ=16.0                 # guard height in the point-up bind pose
PIVOT=(0.0,0.0,GZ)
BLADE_L=33.0
WIDTH=[(0,3.35),(.06,3.2),(.7,2.95),(.86,2.3),(.95,1.0),(1,0)]
THICK=[(0,.75),(.8,.6),(.95,.35),(1,0)]
# Closed CCW section (across y as a fraction of half width, thickness x as a fraction):
SECTION=((0,.55),(.45,1),(1,0),(.45,-1),(0,-.55),(-.45,-1),(-1,0),(-.45,1),(0,.55))
LIGHT=unit((.75,-.25,.6))
Q_DOWN=qrot((1,0,0),180)
ECHOES=(('e1',1),('e2',2))
CLIPS=[('idle',40,20,True),('drift',24,24,True),('cleave',19,35,False),('thrust',21,35,False),('recoil',13,35,False),('fall',35,35,False)]


def blade_point(s,a,k):
    w,th=table(WIDTH,s),table(THICK,s)
    return (th*k,w*a,GZ+.35+BLADE_L*s)


def hilt_parts(prefix,roles):
    """Crossguard, gem, grip and wheel pommel in the point-up bind pose."""
    out=[]
    guard=[(0,-8.8,GZ+1.9,.72),(0,-7.2,GZ+.6,.9),(0,-3.8,GZ-.05,1.0),(0,0,GZ-.15,1.08),(0,3.8,GZ-.05,1.0),(0,7.2,GZ+.6,.9),(0,8.8,GZ+1.9,.72)]
    out.append(tube(prefix+'crossguard',guard,roles['guard'],12,3,.8,(1,0,0)))
    for y in (-8.9,8.9):out.append(ball(f'{prefix}quillon_knob_{"L" if y>0 else "R"}',(0,y,GZ+2.1),(1.05,1.05,1.2),roles['guard'],10,5))
    out.append(ball(prefix+'ecusson',(0,0,GZ+.25),(1.35,2.5,2.1),roles['guard'],12,6))
    out.append(ball(prefix+'guard_gem',(1.25,0,GZ+.35),(.55,.95,1.05),roles['gem'],10,5))
    grip=[(0,0,GZ-1.2-.6*i,1.0 if i%2 else 1.16) for i in range(13)]
    out.append(tube(prefix+'wrapped_grip',grip,roles['grip'],10,2,1.0,(1,0,0)))
    wheel=[(-1.0,0,GZ-10.6,1.7),(-.95,0,GZ-10.6,2.25),(0,0,GZ-10.6,2.4),(.95,0,GZ-10.6,2.25),(1.0,0,GZ-10.6,1.7)]
    out.append(tube(prefix+'wheel_pommel',wheel,roles['pommel'],16,2,1.0,(0,0,1)))
    out.append(ball(prefix+'pommel_gem',(1.05,0,GZ-10.6),(.45,1.05,1.05),roles['gem'],10,5))
    out.append(ball(prefix+'pommel_button',(0,0,GZ-13.1),(.75,.75,.6),roles['pommel'],8,4))
    return out


def sword_parts(prefix,echo=None):
    roles={'blade':'blade','guard':'guard','grip':'grip','pommel':'pommel','gem':'gem'}
    if echo:roles={k:(f'{echo}_blade' if k=='blade' else f'{echo}_hilt') for k in roles}
    p=Piece(prefix+'double_edged_blade',roles['blade']);rows=[];n=48
    for r in range(n+1):
        s=r/n;rows.append([p.add(blade_point(s,a,k),.5+a/2,s) for a,k in SECTION])
    rings(p,rows)
    parts=[p]+hilt_parts(prefix,roles)
    for q in parts[1:]:
        normals=q.normals()
        q.pv=[min(1,max(0,.5-.5*sum(x*y for x,y in zip(nv,LIGHT)))) for nv in normals]
    return parts


def _bbox(parts,margin=.5):
    pts=[v for p in parts for v in p.vertices]
    return tuple(x for a in range(3) for x in (min(v[a] for v in pts)-margin,max(v[a] for v in pts)+margin))


BOX=_bbox(sword_parts(''))
BOX_C=tuple((BOX[2*a]+BOX[2*a+1])/2 for a in range(3))
SPECS=[('root',None,(0,0,0)),('sword','root',PIVOT)]
for echo,_ in ECHOES:
    for z in range(2):
        for y in range(2):
            for x in range(2):SPECS.append((f'{echo}_{z}{y}{x}','root',(BOX[x],BOX[2+y],BOX[4+z])))
RIG=Rig.from_world(SPECS);BONES,REST=RIG.bones,RIG.rest
IDS={n:i for i,(n,_,_) in enumerate(BONES)}


def build_parts():
    out=[]
    for p in sword_parts(''):
        p.skin_weights=[[(IDS['sword'],1)]]*len(p.vertices);out.append(p)
    for echo,_ in ECHOES:
        for p in sword_parts(echo+'_echo_',echo):
            p.skin_weights=[cage_weights(echo,BOX,v,IDS) for v in p.vertices];out.append(p)
    return out


def geometry():
    parts=build_parts()
    for p in parts:p.uv=[materials.uv(p.role,a,b) for a,b in zip(p.pa,p.pv)]
    return assemble(parts,lambda p,v,u:[(0,1)])


# ---------------------------------------------------------------- poses
HOVER=37.0
CLEAVE_HUB=10.0     # sword-space distance from guard to the cleave's turning point
ECHO_OFFSET={'e1':((-1.8,.9,.4),-6.5,0.0),'e2':((-3.6,-.9,.8),6.5,2.1)}   # offset, fan roll, shimmer phase


def carry(t):
    w=math.tau*t
    loc=(.4*math.sin(w),.5*math.sin(2*w),HOVER+1.3*math.sin(w))
    q=chain(qrot((0,0,1),8*math.sin(w+1.2)),qrot((0,1,0),-8+3*math.sin(w)),qrot((1,0,0),4*math.sin(w+.5)),Q_DOWN)
    return loc,q


LOC0,Q0=carry(0)
Q_H=qrot((0,1,0),90)              # bind +Z (point) to +X
def cleave_q(phi):return chain(qrot((1,0,0),phi),qrot((0,1,0),-10))   # flats keep facing the camera
def thrust_q(k):return chain(qrot((0,1,0),9*k),qrot((1,0,0),-70),Q_H)
Q_LIE=chain(qrot((0,0,1),64),qrot((1,0,0),-3),Q_H)   # flats up, lying across the view


def main_state(name,t):
    """World (loc, q) of the sword pivot at clip time t."""
    if name=='idle':return carry(t%1)
    if name=='drift':
        w=math.tau*(t%1)
        loc=(1.0*math.sin(w),.7*math.sin(2*w),HOVER-1+1.0*math.sin(2*w))
        q=chain(qrot((0,0,1),5*math.sin(w)),qrot((0,1,0),-32+4*math.sin(2*w)),qrot((1,0,0),6*math.sin(w+.6)),Q_DOWN)
        return loc,q
    t=max(0,t)
    if name=='cleave':
        # A diagonal cleave facing the camera, turning about the blade's inner third so the
        # whole sword stays in the cell; the late echoes fan out behind it.
        hub=lambda c,q:sub(c,rotate(q,(0,0,CLEAVE_HUB)))
        cock=(-2.0,2.0,32.0);key=(1.0,-2.0,30.0)
        if t<=.3:u=smooth(t/.3);return lerp(LOC0,hub(cock,cleave_q(62)),u),nlerp(Q0,cleave_q(62),u)
        if t<=.5:
            u=(t-.3)/.2;q=cleave_q(62-157*u**1.4);return hub(lerp(cock,key,smooth(u)),q),q
        f=smooth((t-.5)/.14);q=cleave_q(-95-22*f);loc=hub(lerp(key,(1.5,-1.0,29.0),f),q)
        b=smooth((t-.64)/.36);return lerp(loc,LOC0,b),nlerp(q,Q0,b)
    if name=='thrust':
        back=(-14.0,0.0,33.0);key=(-3.2,0.0,30.5)
        if t<=.32:u=smooth(t/.32);return lerp(LOC0,back,u),nlerp(Q0,thrust_q(0),u)
        if t<=.5:u=(t-.32)/.18;return lerp(back,key,u**1.3),thrust_q(u)
        if t<=.62:return key,thrust_q(1)
        b=smooth((t-.62)/.38);return lerp(key,LOC0,b),nlerp(thrust_q(1),Q0,b)
    if name=='recoil':
        g=bump(t,.5,.5);s=math.sin(t*math.pi*4)*g
        return add(LOC0,(-6*g,2*s,3.5*g)),chain(qrot((0,1,0),-56*g),qrot((1,0,0),14*s),Q0)
    if name=='fall':
        tremble=smooth(t/.08)*(1-smooth((t-.24)/.06))
        qh=chain(qrot((1,0,0),6*math.sin(t*90)*tremble),qrot((0,0,1),5*math.sin(t*67)*tremble),Q0)
        tip=smooth((t-.22)/.44);drop=min(1,max(0,(t-.3)/.4))
        z=HOVER+(2.25-HOVER)*drop*drop;xy=lerp(LOC0[:2],(-4.4,-9.0),drop)
        q=nlerp(qh,Q_LIE,tip)
        if t>.7:z+=1.6*math.sin(math.pi*min(1,(t-.7)/.12))*(1-smooth((t-.7)/.2))
        return (xy[0],xy[1],z),q
    raise KeyError(name)


def echo_state(name,t,echo):
    off,roll,phase=ECHO_OFFSET[echo];order=1 if echo=='e1' else 2
    w=math.tau*(t%1 if name in ('idle','drift') else 0)
    lag={'cleave':.045,'thrust':.07,'recoil':.03,'fall':.03}.get(name,0)*order
    ramp=smooth(t/.25) if name not in ('idle','drift') else 0
    loc,q=main_state(name,t-lag*ramp)
    spread=1.0;k=1.0;extra=(0,0,0)
    shimmer=(.5*math.sin(2*w+phase),.6*math.sin(w+phase),.5*math.sin(3*w+phase))
    if name=='drift':extra=(-4.0*order,0,.8*order)
    if name=='recoil':spread=1+2.2*bump(t,.5,.5)
    if name=='thrust':extra=mul((0,3.0 if echo=='e1' else -3.0,2.0*order),bump(t,.5,.3))
    if name=='fall':
        # The after-images fling apart and shrink away while the sword falls.
        fly=smooth((t-.24)/.36);k=1-smooth((t-.3)/.34)
        extra=mul((-3,4.5 if echo=='e1' else -4.5,9),fly);spread=1+fly
    o=add(add(mul(off,spread),shimmer),extra)
    q=qmul(qrot((1,0,0),roll*spread),q)
    return add(loc,o),q,k


def pose(name,t):
    f=[[*local,0,0,0,1,1,1,1] for _,_,local in BONES]
    loc,q=main_state(name,t)
    f[IDS['sword']][:3]=list(loc);f[IDS['sword']][3:7]=list(q)
    for echo,_ in ECHOES:
        el,eq,k=echo_state(name,t,echo)
        centre=add(el,rotate(eq,sub(BOX_C,PIVOT)))
        for z in range(2):
            for y in range(2):
                for x in range(2):
                    c=add(el,rotate(eq,sub((BOX[x],BOX[2+y],BOX[4+z]),PIVOT)))
                    f[IDS[f'{echo}_{z}{y}{x}']][:3]=list(add(centre,mul(sub(c,centre),k)))
    return [tuple(r) for r in f]


def matrices(frame):return RIG.matrices(frame)
def deform(v,w,frame):return RIG.deform(v,w,frame)
def animation_data(v,w):return sample_clips(RIG,CLIPS,pose,v,w)
def texture_bytes():return materials.texture_bytes()


def build():
    skin=texture_bytes();(ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts,v,n,uv,t,w=geometry();clips,bounds=animation_data(v,w)
    data=iqm.encode(v,n,uv,t,w,BONES,clips,bounds,mesh_label='Project_Broom_spectral_image',material_path=SKIN)
    path=ROOT/MODEL;path.write_bytes(data)
    manifest=dict(schemaVersion=1,workId='BRG-M56',format='IQM v2',runtimeModel=MODEL,
        sha256=hashlib.sha256(data).hexdigest(),skin=SKIN,skinSha256=hashlib.sha256(skin).hexdigest(),
        dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],
        parts=len(parts),vertices=len(v),triangles=len(t),boneCount=len(BONES),
        bones=[dict(name=n_,parent=p,local=l) for n_,p,l in BONES],
        clips=[{k:x for k,x in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],
        poseBounds=bounds,emissive=dict(additive=True,shader='shaders/spectral-sword-glow.fp'),
        authoringSource='assets/monsters/spectral_sword/spectral-sword-animated.blend')
    out=ROOT/'assets/monsters/spectral_sword';out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__':
    from tools.monster_models import spectral_sword_animation as _self
    print(_self.build()['sha256'])

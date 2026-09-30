"""Original connected coiled naga. Cosmetic geometry and poses only."""
import hashlib,json,math,struct,zlib
from functools import lru_cache
from . import iqm,connected_skin
from .creatures import Sculpt
from .rat import ROOT,add,sub
from .skeletal import Rig,axis,qmul,assemble,sample_clips

SKIN='graphics/BRGNAGA.png'
TAIL=[(-7,0,17,6.3),(-12,-1,9,6),(-13,-12,6.3,5.8),(-2,-18,5.6,5.4),
      (14,-14,5.1,4.8),(20,0,4.5,4.1),(15,14,3.9,3.5),(1,18,3.4,2.9),
      (-11,14,3,2.3),(-14,6,2.7,1.6),(-7,4,2.4,.85),(-3,8,2.3,.16)]
SPECS=[('root',None,(0,0,0)),('waist','root',(-7,0,17)),('chest','waist',(-6,0,32)),
       ('neck','chest',(-5,0,44)),('head','neck',(-1,0,53)),('jaw','head',(3,0,50))]
for j,p in enumerate(TAIL):SPECS.append((f'tail_{j}','root' if j==0 else f'tail_{j-1}',p[:3]))
for side,sgn in [('L',1),('R',-1)]:
    for j,p in enumerate([(-5,sgn*7,37),(-2,sgn*14,28),(6,sgn*17,27)]):
        SPECS.append((f'arm_{side}_{j}','chest' if j==0 else f'arm_{side}_{j-1}',p))
RIG=Rig.from_world(SPECS);BONES,REST=RIG.bones,RIG.rest
IDS={n:i for i,(n,p,v) in enumerate(BONES)}
CLIPS=[('idle',40,20,True),('slither',28,35,True),('claw',24,35,False),
       ('tailwhip',28,35,False),('recoil',14,35,False),('collapse',36,35,False)]

def build_parts():
    s=Sculpt()
    s.strand('skin_tail',TAIL,'body',sides=28,samples=5)
    s.strand('skin_torso',[(-7,0,15,6),(-7,0,23,5.2),(-6,0,32,6.2),(-5,0,38,7),(-5,0,44,3.4),(-2,0,50,3.2)],'body',sides=30,samples=5)
    s.oval('skin_head',(-.5,0,53),(5.2,5.2,4.6),'body',30,18)
    s.oval('skin_muzzle',(4.2,0,51.5),(4.5,3.8,2.0),'body',28,16)
    s.oval('jaw_lower',(4.3,0,49.2),(4.0,3.4,1.0),'body',28,14)
    s.oval('mouth',(6.1,0,50.1),(2.9,3.2,.25),'dark',24,10)
    for sign in (-1,1):
        s.strand('skin_brow_'+str(sign),[(3.1,sign*1.8,55.2,.6),(2.7,sign*3.8,55.3,.8),(0,sign*4.7,54.5,.45)],'body',14,4)
        s.oval('socket_'+str(sign),(3.43,sign*3.59,54.1),(.65,.65,.74),'dark',18,12)
        s.oval('eye_'+str(sign),(3.65,sign*3.8,54.1),(.42,.42,.49),'accent',18,12)
        s.oval('pupil_'+str(sign),(3.88,sign*3.93,54.15),(.14,.15,.45),'dark',14,10)
        s.oval('nostril_'+str(sign),(8.15,sign*1.75,52.1),(.13,.38,.25),'dark',12,8)
        s.strand('fang_'+str(sign),[(7.1,sign*2.1,50.1,.28),(7.5,sign*2.1,49.1,.21),(7.1,sign*2.1,48.7,.03)],'bone',12,3)
        # Fleshy head crest merges into skull; no invented magic or ornaments.
        s.strand('skin_crest_'+str(sign),[(-3,sign*3,54,1.0),(-5,sign*4,56,1.0),(-6.6,sign*4,57,.16)],'body',14,4)
    for side,sign in [('L',1),('R',-1)]:
        s.oval(f'skin_shoulder_{side}',(-5,sign*6.6,36.6),(3.5,3.6,4.2),'body',26,16)
        points=[REST[IDS[f'arm_{side}_{j}']] for j in range(3)]
        s.strand(f'skin_arm_{side}',[(*p,r) for p,r in zip(points,(3.1,2.4,1.8))],'body',22,6)
        s.oval(f'skin_hand_{side}',(7,sign*17,27),(3,2.5,1.9),'body',20,12)
        for j in range(3):
            y=sign*(15.3+j*1.7)
            s.strand(f'skin_finger_{side}_{j}',[(8,y,27,1),(10.5,y+sign*.4,26.5,.8),(11.8,y+sign*.6,25.1,.55)],'body',12,4)
            s.strand(f'claw_{side}_{j}',[(11.6,y+sign*.6,25.4,.53),(12,y+sign*.7,24,.34),(10.9,y+sign*.8,23.3,.025)],'bone',12,4)
        s.strand(f'skin_thumb_{side}',[(6,sign*15.2,27,1),(7.5,sign*13.5,26.5,.8),(9,sign*13.5,25.5,.45)],'body',12,4)
        s.strand(f'claw_{side}_thumb',[(9,sign*13.5,25.5,.45),(9.5,sign*13.5,24,.02)],'bone',12,3)
    # These UV coordinates are replaced after fusion by continuous world pigment.
    for p in s.parts:
        if p.name.startswith(('skin','jaw')):p.uv=[(.3,.5)]*len(p.vertices)
        else:p.uv=[((.86 if p.name.startswith(('claw','fang')) else .94 if p.name.startswith('eye') else .99),.05)]*len(p.vertices)
    return s.parts

def weights(p,v,u):
    n=p.name
    if n.startswith(('claw','skin_hand','skin_finger','skin_thumb')):
        side=n.split('_')[1] if n.startswith('claw') else n.split('_')[2]
        return [(IDS[f'arm_{side}_2'],1)]
    if n.startswith('skin_shoulder'):return [(IDS['chest'],.4),(IDS[f'arm_{n[-1]}_0'],.6)]
    if n.startswith('skin_arm'):
        return RIG.chain_weights(v,[IDS[f'arm_{n[-1]}_{j}'] for j in range(3)])
    if n=='skin_tail':return RIG.chain_weights(v,[IDS[f'tail_{j}'] for j in range(len(TAIL))])
    if n=='skin_torso':return RIG.chain_weights(v,[IDS[x] for x in ('waist','chest','neck','head')])
    return [(IDS['jaw' if n=='jaw_lower' else 'head'],1)]

def geometry():
    parts=connected_skin.attach('naga',build_parts(),weights)
    for p in parts:
        if p.name in ('Connected_skin','jaw_lower'):
            # Continuous world coordinates avoid part-UV pigment discontinuities.
            p.uv=[pigment(v) for v in p.vertices]
    return assemble(parts,weights)

def pigment(v):
    x,y,z=v
    # Continuous centerline field: anterior torso, underside coil; dorsal head
    # never inherits a lateral-coordinate-only pale stripe.
    cx=-7+2*max(0,min(1,(z-17)/27))+4*max(0,min(1,(z-44)/9))
    front=(x-cx)/max(.01,math.hypot(x-cx,y))
    nearest=None
    for j,(a,b) in enumerate(zip(TAIL,TAIL[1:])):
        d=[b[i]-a[i] for i in range(3)]
        t=max(0,min(1,sum((v[i]-a[i])*d[i] for i in range(3))/sum(q*q for q in d)))
        c=[a[i]+t*d[i] for i in range(3)];distance=math.dist(v,c)
        if nearest is None or distance<nearest[0]:nearest=(distance,c,j+t)
    distance,c,arc=nearest
    underside=(c[2]-z)/max(.01,distance)
    blend=max(0,min(1,(z-10)/8));f=underside*(1-blend)+front*blend
    # Encode the orientation as a symmetric atlas coordinate, keeping scales
    # continuous across fused source-part boundaries.
    angle=math.acos(max(-1,min(1,f)))
    return (.02+.76*(z/62*blend+(.20+.043*arc)*(1-blend)),.5+angle/math.tau)

@lru_cache(maxsize=1)
def collapse_contacts():
    points=[];influences=[]
    for p in build_parts():
        if p.name.startswith(('skin_hand','skin_finger','skin_thumb','claw','jaw','fang')):
            points.extend(p.vertices);influences.extend(weights(p,v,u) for v,u in zip(p.vertices,p.uv))
    return points,influences

def pose(name,t):
    f=[[*local,0,0,0,1,1,1,1] for _,_,local in BONES]
    def turn(n,deg,ax=(0,1,0)):f[IDS[n]][3:7]=axis(ax,math.radians(deg))
    phase=math.tau*t;pulse=math.sin(math.pi*t)**2
    if name in ('idle','slither'):
        turn('chest',.7*math.sin(phase));turn('head',1.5*math.sin(phase+.6),(0,0,1))
        for j in range(2,len(TAIL)):turn(f'tail_{j}',(.45 if name=='idle' else 1.4)*math.sin(phase-j*.65),(0,0,1))
        for side,sgn in [('L',1),('R',-1)]:turn(f'arm_{side}_0',sgn*1.3*math.sin(phase),(1,0,0))
    elif name=='claw':
        turn('chest',8*pulse);turn('head',-5*pulse);turn('jaw',18*pulse)
        for side,sgn in [('L',1),('R',-1)]:
            turn(f'arm_{side}_0',-35*pulse);turn(f'arm_{side}_1',-25*pulse,(0,0,sgn))
    elif name=='tailwhip':
        turn('chest',-7*pulse);turn('head',14*pulse,(0,0,1));turn('jaw',12*pulse)
        for j in range(5,len(TAIL)):turn(f'tail_{j}',10*pulse*math.sin(j*.8),(0,0,1))
    elif name=='recoil':turn('chest',-12*pulse);turn('head',8*pulse)
    elif name=='collapse':
        q=t*t*(3-2*t)
        # Fold each short torso segment instead of rotating the full tall body.
        turn('waist',22*q);turn('chest',73*q);turn('neck',45*q);turn('head',25*q,(1,0,0))
        f[IDS['waist']][2]-=9*q;f[IDS['waist']][0]-=7*q
        for side,sgn in [('L',1),('R',-1)]:
            turn(f'arm_{side}_0',-75*q)
            f[IDS[f'arm_{side}_0']][3:7]=qmul(f[IDS[f'arm_{side}_0']][3:7],axis((1,0,0),math.radians(-40*sgn*q)))
            turn(f'arm_{side}_1',10*q)
        turn('jaw',12*q)
    elif name!='rest':raise ValueError(name)
    if name=='collapse':
        # Correct only the folding upper anatomy; the ground coil stays fixed.
        points,influences=collapse_contacts()
        lowest=min(v[2] for v in RIG.deform(points,influences,f))
        f[IDS['waist']][2]+=max(0,.25-lowest)
    return [tuple(r) for r in f]

def matrices(f):return RIG.matrices(f)
def deform(v,w,f):return RIG.deform(v,w,f)
def animation_data(v,w):return sample_clips(RIG,CLIPS,pose,v,w)

def texture_bytes():
    size=1024;raw=bytearray()
    for y in range(size):
        raw.append(0)
        for x in range(size):
            u=x/(size-1);v=1-y/(size-1)
            if u>.83:base=(192,184,127) if u<.9 else (224,160,40) if u<.97 else (20,23,14);detail=0
            else:
                # Interleaved scalloped scales with fine pores; broad pale ventral field.
                row=int(u*95);a=(v*24+.5*(row%2))%1;b=(u*95)%1
                seam=math.exp(-((b-.15-.58*math.sin(math.pi*a))/.07)**2)
                pale=math.exp(-((v-.5)/.14)**4)*max(0,min(1,(.64-u)/.05))
                base=(58+107*pale,79+77*pale,30+66*pale)
                detail=8*math.sin(u*39)*math.sin(v*31)-20*seam+5*math.sin(math.pi*a)*math.sin(math.pi*b)
                scute=math.exp(-((u*23)%1/.085)**2)
                detail=detail*(1-pale)+pale*(-23*scute+5*math.sin(u*math.tau*23))
                detail+=2*math.sin(x*1.72+y*.8)*math.sin(y*1.9-x*.4)
            raw.extend(max(0,min(255,round(c+detail))) for c in base)
    def chunk(k,d):return struct.pack('>I',len(d))+k+d+struct.pack('>I',zlib.crc32(k+d)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',size,size,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(bytes(raw),9))+chunk(b'IEND',b'')

def build():
    skin=texture_bytes();(ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts,v,n,uv,t,w=geometry();clips,bounds=animation_data(v,w)
    data=iqm.encode(v,n,uv,t,w,BONES,clips,bounds,mesh_label='Project_Broom_naga',material_path=SKIN)
    path=ROOT/'mod/BrogueDoom/models/monsters/28_naga.iqm';path.write_bytes(data)
    manifest=dict(schemaVersion=1,workId='BRG-M28',format='IQM v2',runtimeModel=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(data).hexdigest(),skin=SKIN,skinSha256=hashlib.sha256(skin).hexdigest(),dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],parts=len(parts),vertices=len(v),triangles=len(t),boneCount=len(BONES),bones=[dict(name=n,parent=p,local=v) for n,p,v in BONES],clips=[{k:v for k,v in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],poseBounds=bounds,authoringSource='assets/monsters/naga/naga-animated.blend')
    out=ROOT/'assets/monsters/naga';out.mkdir(exist_ok=True);(out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest
if __name__=='__main__':print(build()['sha256'])

"""Original weighted rat, skeleton and deterministic presentation clips.

Python is the reproducible master; blender_rat_animation.py delivers the same
rig/weights/keyframes as an editable .blend. No simulation or gameplay RNG.
"""
import hashlib
import json
import math
from pathlib import Path

from . import rat, iqm

ROOT=rat.ROOT
add,sub,mul,unit,cross=rat.add,rat.sub,rat.mul,rat.unit,rat.cross


from .skeletal import Rig, qmul, inverse, rotate, axis, between, assemble, sample_clips


def skeleton():
    specs=[('root',None,(0,0,0)),('pelvis','root',(-6,0,7)),
           ('spine','pelvis',(1,0,8)),('neck','spine',(7,0,8)),
           ('head','neck',(11,0,8)),('jaw','head',(14,0,5.4)),
           ('ear_L','head',(8.5,3.5,12.55)),('ear_R','head',(8.5,-3.5,12.55))]
    for label,side in (('L',1),('R',-1)):
        for limb,parent,points in (
            ('Fore','spine',[(4.9,side*2.8,7),(6.2,side*3.8,4),(7.4,side*4.2,.72)]),
            ('Hind','pelvis',[(-6.6,side*4,5.2),(-8.5,side*5,2.2),(-5.4,side*5.1,.72)])):
            for joint,point in zip(('upper','lower','paw'),points):
                name=f'{limb}_{label}_{joint}'
                specs.append((name,parent,point)); parent=name
    tail=[(-13,0,6.1),(-15.5,.1,4),(-19.5,1.1,2),(-24,3,1.15),
          (-28.5,5.1,.8),(-31,8,.6),(-29.2,10,.35),(-26.4,9.1,.22)]
    parent='pelvis'
    for i,p in enumerate(tail):
        name=f'tail_{i:02d}'; specs.append((name,parent,p)); parent=name
    ids={s[0]:i for i,s in enumerate(specs)}
    bones=[(n,ids[p] if p else -1,sub(v,specs[ids[p]][2]) if p else v) for n,p,v in specs]
    return bones,[s[2] for s in specs]


BONES,REST=skeleton()
RIG=Rig(BONES,REST)
IDS={n:i for i,(n,p,v) in enumerate(BONES)}
CLIPS=[('idle',40,20,True),('scurry',16,40,True),('bite',14,35,False),
       ('scratch',16,35,False),('recoil',10,35,False),('death',24,35,False)]


def build_parts():
    parts=rat.build_parts()
    # The original continuous muzzle stays intact; a recessed mouth and thin
    # separate lower mandible make the bite readable without tearing the head.
    parts.append(rat.ellipsoid('Jaw_lower_mandible',(16.7,0,4.85),(2.2,1.35,.38),'fur',24,10,.67))
    parts.append(rat.ellipsoid('Jaw_mouth_recess',(16.8,0,5.18),(1.85,1.08,.16),'eye',20,8))
    for s in (-1,1):
        parts.append(rat.ellipsoid(f'Jaw_lower_incisor_{s}',(18.2,s*.3,5.1),(.25,.2,.38),'claw',12,8))
    return parts


def blend(a,b,t):
    t=max(0,min(1,t))
    return [(IDS[a],1-t),(IDS[b],t)] if 0<t<1 else [(IDS[b] if t else IDS[a],1)]


def weights(part,v,uv):
    name=part.name
    if name.startswith('Tail_'):
        # Project to the anatomical tail chain: two influences, no disconnected
        # sections even where the tip curves back toward the body.
        best=None
        for i in range(7):
            a,b=REST[IDS[f'tail_{i:02d}']],REST[IDS[f'tail_{i+1:02d}']]
            d=sub(b,a); t=max(0,min(1,sum(x*y for x,y in zip(sub(v,a),d))/sum(x*x for x in d)))
            dist=sum(x*x for x in sub(v,add(a,mul(d,t))))
            if best is None or dist<best[0]: best=(dist,i,t)
        return blend(f'tail_{best[1]:02d}',f'tail_{best[1]+1:02d}',best[2])
    if name.startswith('Ear_'):
        side=name.split('_')[1]
        return blend('head','ear_'+side,max(0,min(1,(v[2]-10.3)/1.5)))
    if name.startswith('Jaw_') or name.startswith('Mouth_'): return [(IDS['jaw'],1)]
    if name.startswith(('Fore_','Hind_')):
        limb,side,partname=name.split('_',2); prefix=f'{limb}_{side}'
        if partname.startswith(('palm','toe','claw')): return [(IDS[prefix+'_paw'],1)]
        upper,lower,paw=(REST[IDS[prefix+'_'+j]] for j in ('upper','lower','paw'))
        if partname=='haunch': return blend('pelvis',prefix+'_upper',.8)
        if v[2]>=lower[2]: return blend(prefix+'_lower',prefix+'_upper',(v[2]-lower[2])/(upper[2]-lower[2]))
        return blend(prefix+'_paw',prefix+'_lower',(v[2]-paw[2])/(lower[2]-paw[2]))
    if name in ('Rat_continuous_coat','Coat_guard_hair_tufts'):
        knots=[(-8,'pelvis'),(1,'spine'),(6.5,'neck'),(11,'head')]
        for (a,an),(b,bn) in zip(knots,knots[1:]):
            if v[0]<b: return blend(an,bn,(v[0]-a)/(b-a))
        return [(IDS['head'],1)]
    return [(IDS['head'],1)]


def solve_leg(prefix,target,rotations):
    ids=[IDS[prefix+'_'+j] for j in ('upper','lower','paw')]
    hip,knee,foot=[REST[i] for i in ids]
    a=math.dist(hip,knee); b=math.dist(knee,foot)
    direction=unit(sub(target,hip)); distance=min(a+b-.001,max(abs(a-b)+.001,math.dist(target,hip)))
    along=(a*a-b*b+distance*distance)/(2*distance)
    pole=sub(knee,hip)
    bend=unit(sub(pole,mul(direction,sum(x*y for x,y in zip(pole,direction)))))
    newknee=add(hip,add(mul(direction,along),mul(bend,math.sqrt(max(0,a*a-along*along)))))
    upper=between(sub(knee,hip),sub(newknee,hip))
    lower=between(sub(foot,knee),sub(target,newknee))
    rotations[ids[0]]=upper; rotations[ids[1]]=qmul(inverse(upper),lower)
    rotations[ids[2]]=inverse(lower)  # flat paw during planted phase


def pose(name,t):
    rotation=[(0,0,0,1) for _ in BONES]; displacement=[(0,0,0) for _ in BONES]
    def turn(b,a,angle): rotation[IDS[b]]=axis(a,angle)
    phase=t*math.tau
    if name=='idle':
        turn('neck',(0,1,0),math.radians(1.2)*math.sin(phase))
        turn('head',(0,0,1),math.radians(2)*math.sin(phase))
        turn('jaw',(0,1,0),math.radians(2)*max(0,math.sin(phase*3)))
        for i,s in enumerate(('L','R')):
            turn('ear_'+s,(1,0,0),math.radians(9)*max(0,math.sin(phase+i*1.6))**14)
    elif name=='scurry':
        for limb in ('Fore','Hind'):
            for side in ('L','R'):
                p=phase+(math.pi if (side=='L') != (limb=='Hind') else 0)
                foot=REST[IDS[f'{limb}_{side}_paw']]
                target=add(foot,(1.25*math.cos(p),0,1.35*max(0,math.sin(p))))
                solve_leg(f'{limb}_{side}',target,rotation)
        turn('neck',(0,1,0),math.radians(2.5)*math.sin(phase*2))
    elif name in ('bite','scratch','recoil'):
        strike=math.sin(math.pi*t)**2
        if name=='bite':
            turn('neck',(0,1,0),math.radians(-6)*strike)
            turn('head',(0,1,0),math.radians(10)*strike)
            turn('jaw',(0,1,0),math.radians(28)*math.sin(math.pi*min(1,t*1.8))**2)
            displacement[IDS['head']]=(1.5*strike,0,0)
        elif name=='scratch':
            foot=REST[IDS['Fore_R_paw']]
            solve_leg('Fore_R',add(foot,(2.1*strike,0,3.2*strike)),rotation)
            turn('head',(0,0,1),math.radians(-8)*strike)
            turn('jaw',(0,1,0),math.radians(12)*strike)
        else:
            turn('neck',(0,1,0),math.radians(-14)*strike)
            turn('head',(0,0,1),math.radians(-9)*strike)
            for side in ('L','R'): turn('ear_'+side,(0,1,0),math.radians(-15)*strike)
    elif name=='death':
        settle=min(1,t/0.72); smooth=settle*settle*(3-2*settle)
        turn('root',(1,0,0),-math.pi/2*smooth)
        turn('neck',(0,1,0),math.radians(12)*smooth)
        # Let the neck turn as the flank settles. Long whiskers must not prop
        # the entire corpse above the floor like rigid supports.
        turn('head',(1,0,0),math.radians(70)*smooth)
        turn('jaw',(0,1,0),math.radians(17)*smooth)
        for limb in ('Fore','Hind'):
            for side in ('L','R'):
                turn(f'{limb}_{side}_lower',(0,1,0),math.radians(25)*smooth)
        for i in range(8):
            bone=IDS[f'tail_{i:02d}']
            desired=5.4*min(1,i/2)
            previous=5.4*min(1,(i-1)/2) if i else 0
            displacement[bone]=(0,(desired-previous-BONES[bone][2][1])*smooth,0)
    for i in range(8):
        wave=math.sin(phase-i*.5) if name in ('idle','scurry') else math.sin(math.pi*t)
        turn(f'tail_{i:02d}',(0,0,1),math.radians(1.2 if name=='idle' else 3)*wave)
    return [(*add(local,displacement[i]),*rotation[i],1,1,1) for i,(n,p,local) in enumerate(BONES)]


def matrices(frame): return RIG.matrices(frame)


def deform(vertices,influences,frame): return RIG.deform(vertices,influences,frame)


def geometry():
    from .connected_skin import attach
    return assemble(attach('rat',build_parts(),weights),weights)


def animation_data(vertices,influences):
    return sample_clips(RIG,CLIPS,pose,vertices,influences)


def build():
    parts,vertices,normals,uv,triangles,influences=geometry()
    clips,bounds=animation_data(vertices,influences)
    payload=iqm.encode(vertices,normals,uv,triangles,influences,BONES,clips,bounds)
    path=ROOT/'mod/BrogueDoom/models/monsters/01_rat.iqm'
    if not path.exists() or path.read_bytes()!=payload: path.write_bytes(payload)
    manifest={'schemaVersion':1,'workId':'BRG-M01','format':'IQM v2','runtimeModel':str(path.relative_to(ROOT)).replace('\\','/'),
              'sha256':hashlib.sha256(payload).hexdigest(),'skinSha256':hashlib.sha256((ROOT/'mod/BrogueDoom/graphics/BRGRAT.png').read_bytes()).hexdigest(),
              'parts':len(parts),'vertices':len(vertices),'triangles':len(triangles),'boneCount':len(BONES),
              'bones':[{'name':n,'parent':p,'local':v} for n,p,v in BONES],
              'clips':[{k:v for k,v in c.items() if k!='frames'}|{'frameCount':len(c['frames'])} for c in clips],
              'poseBounds':bounds,'authoringSource':'assets/monsters/rat/rat-animated.blend',
              'staticReference':'assets/monsters/rat/rat.blend','verification':{}}
    previous_path=ROOT/'assets/monsters/rat/animation.json'
    if previous_path.exists():
        previous=json.loads(previous_path.read_text())
        evidence=previous.get('verification',{})
        if evidence:
            manifest['verification']=(evidence if all(previous.get(k)==manifest[k] for k in ('sha256','skinSha256'))
                                      else {'stale':True,'previousAssetVerification':evidence})
    previous_path.write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:v for k,v in manifest.items() if k not in ('bones','poseBounds')},indent=2))
    return manifest


if __name__=='__main__': build()

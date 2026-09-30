"""Original monkey anatomy, normal/captive skins and copied-state release clips."""
import hashlib,json,math
from . import iqm,monkey_materials
from .creatures import Sculpt
from .rat import ROOT,add,sub
from .skeletal import Rig,axis,qmul,assemble,sample_clips

SPECS=[('root',None,(0,0,0)),('pelvis','root',(0,0,12)),('spine','pelvis',(0,0,20)),
       ('neck','spine',(1,0,25)),('head','neck',(2,0,28)),('jaw','head',(4,0,26))]
for side,sign in (('L',1),('R',-1)):
    for limb,parent,points in (
        ('arm','spine',[(0,sign*5.2,23),(2,sign*8,15),(5,sign*8.5,7.5)]),
        ('leg','pelvis',[(0,sign*3,12),(3,sign*3,6),(2,sign*3,1.4)])):
        for joint,p in zip(('upper','lower','end'),points):
            name=f'{limb}_{side}_{joint}';SPECS.append((name,parent,p));parent=name
parent='pelvis'
for i,p in enumerate([(-3,0,13),(-9,0,9),(-16,1,6),(-21,3,8),(-22,4,12)]):
    name=f'tail_{i}';SPECS.append((name,parent,p));parent=name
RIG=Rig.from_world(SPECS);BONES,REST=RIG.bones,RIG.rest;IDS={n:i for i,(n,p,v) in enumerate(BONES)}
CLIPS=[('idle',40,20,True),('walk',20,35,True),('bite',18,35,False),
       ('snatch',20,35,False),('recoil',10,35,False),('death',26,35,False),
       ('captive',40,20,True),('released',21,35,False)]

def build_parts():
    s=Sculpt()
    s.oval('pelvis',(0,0,12),(3.8,4.3,3.6))
    s.strand('torso',[(0,0,12,3.5),(-.6,0,18,3.8),(0,0,23,4.3)],sides=20,samples=4)
    s.strand('neck',[(0,0,22,2.5),(2,0,28,2.5)],sides=16)
    s.oval('head_skull',(1.5,0,28.5),(3.7,3.8,4.2),seg=24,rings=14)
    s.oval('head_face',(4.05,0,28.2),(2.5,3.15,3),'cloth',24,14)
    s.oval('head_muzzle',(5.6,0,26.6),(1.9,2.1,1.3),'cloth',20,12)
    s.oval('jaw_mouth',(6,0,25.6),(1.35,1.4,.22),'dark')
    s.oval('jaw_lower',(5.4,0,25.2),(1.7,1.65,.55),'cloth')
    for side,sign in (('L',1),('R',-1)):
        s.oval('head_ear_'+side,(1,sign*3.75,28.4),(1.5,.8,2),'body')
        s.oval('head_ear_inner_'+side,(1.5,sign*4.15,28.4),(1.05,.48,1.35),'accent')
        s.oval('head_eye_'+side,(5.3,sign*1.8,29.4),(.67,.57,.8),'dark',16,10)
        s.oval('head_glint_'+side,(5.85,sign*1.72,29.65),(.13,.13,.19),'bone',10,6)
        s.oval('head_brow_'+side,(4.9,sign*1.8,30.3),(1,1,.38),'body')
        s.oval('head_nostril_'+side,(7.15,sign*.6,27.05),(.14,.23,.18),'dark',10,6)
        s.oval('shoulder_'+side,(0,sign*4.1,23),(2.3,2.4,2.5))
        for limb in ('arm','leg'):
            points=[REST[IDS[f'{limb}_{side}_{j}']] for j in ('upper','lower','end')]
            s.strand(f'{limb}_{side}',[(*p,r) for p,r in zip(points,(2.1,1.45,.95))],sides=14,samples=4)
        for hand,prefix,end in ((True,'hand','arm'),(False,'foot','leg')):
            c=REST[IDS[f'{end}_{side}_end']]
            s.oval(f'{prefix}_{side}_palm',add(c,(.6,0,-.1)),(1.3,1.3,.85),'cloth')
            for i in range(4):
                y=(i-1.5)*.55
                s.strand(f'{prefix}_{side}_finger{i}',[(*add(c,(.5,y,0)),.32),(*add(c,(1.8,y,-.2)),.29),(*add(c,(2.5,y,-.55)),.16)],'cloth',8,3)
            s.strand(f'{prefix}_{side}_thumb',[(*add(c,(.2,-sign*.9,0)),.45),(*add(c,(1.1,-sign*1.65,-.2)),.35),(*add(c,(1.8,-sign*1.45,-.35)),.19)],'cloth',8,3)
    s.strand('tail',[(*REST[IDS[f'tail_{i}']],r) for i,r in enumerate((1.5,1.2,.8,.5,.12))],sides=12,samples=5)
    return s.parts

def weights(part,v,uv):
    n=part.name
    if n.startswith('head'):return [(IDS['head'],1)]
    if n.startswith('jaw'):return [(IDS['jaw'],1)]
    if n=='binding_link':
        t=max(0,min(1,(v[1]+8.5)/17))
        return [(IDS['arm_R_end'],1-t),(IDS['arm_L_end'],t)]
    if n.startswith(('hand','foot','binding')):
        side=n.split('_')[1];limb='leg' if n.startswith('foot') else 'arm'
        return [(IDS[f'{limb}_{side}_end'],1)]
    if n.startswith('shoulder'):
        t=max(0,min(1,(abs(v[1])-2)/3));return [(IDS['spine'],1-t),(IDS['arm_'+n[-1]+'_upper'],t)]
    if n.startswith(('arm','leg')):return RIG.chain_weights(v,[IDS[n+'_'+j] for j in ('upper','lower','end')])
    if n=='tail':return RIG.chain_weights(v,[IDS[f'tail_{i}'] for i in range(5)])
    return RIG.chain_weights(v,[IDS[n] for n in ('pelvis','spine','neck','head')])

def pose(name,t):
    rot=[(0,0,0,1) for _ in BONES];shift=[(0,0,0) for _ in BONES];phase=t*math.tau
    def turn(n,a,d):rot[IDS[n]]=qmul(rot[IDS[n]],axis(a,math.radians(d)))
    if name=='idle':
        turn('neck',(0,0,1),5*math.sin(phase));turn('head',(0,1,0),2*math.sin(phase*2))
    elif name=='walk':
        for side,offset in [('L',0),('R',math.pi)]:
            p=phase+offset
            turn('leg_'+side+'_upper',(0,1,0),18*math.sin(p));turn('leg_'+side+'_lower',(0,1,0),20*max(0,math.sin(p)))
            turn('arm_'+side+'_upper',(0,1,0),-12*math.sin(p))
        turn('spine',(0,0,1),4*math.sin(phase))
    elif name in ('bite','snatch'):
        p=math.sin(math.pi*t)**2;turn('spine',(0,1,0),14*p);turn('head',(0,1,0),-8*p)
        turn('jaw',(0,1,0),25*p)
        turn('arm_R_upper',(0,1,0),-62*p);turn('arm_R_lower',(0,1,0),-28*p)
        turn('arm_L_upper',(0,1,0),-30*p if name=='snatch' else 12*p)
    elif name=='recoil':
        p=math.sin(math.pi*t)**2;turn('spine',(0,1,0),-16*p);turn('head',(0,0,1),-16*p)
    elif name=='death':
        p=min(1,t/.8);p=p*p*(3-2*p);turn('root',(1,0,0),90*p)
        turn('head',(0,0,1),20*p);turn('jaw',(0,1,0),18*p)
        for side in ('L','R'):turn('leg_'+side+'_lower',(0,1,0),45*p)
    elif name in ('captive','released'):
        p=1 if name=='captive' else 1-t*t*(3-2*t)
        turn('spine',(0,1,0),18*p);turn('head',(0,1,0),15*p)
        for side,sign in [('L',1),('R',-1)]:
            turn('arm_'+side+'_upper',(1,0,0),-sign*30*p)
            turn('arm_'+side+'_lower',(0,1,0),-60*p)
            turn('arm_'+side+'_end',(0,1,0),35*p)
        if name=='captive':turn('head',(0,0,1),3*math.sin(phase))
    tail_strength=1 if name=='captive' else 1+2*t*t*(3-2*t) if name=='released' else 3
    for i in range(5):turn(f'tail_{i}',(0,0,1),tail_strength*math.sin(phase-i*.6))
    return [(*add(local,shift[i]),*rot[i],1,1,1) for i,(n,p,local) in enumerate(BONES)]

def geometry(captive=False):
    from .connected_skin import attach
    parts=attach('monkey',build_parts(),weights)
    if captive:
        # Author the complete restraint assembly in the actual bound pose.
        # Fixed frame/chains use the root, so anchors cannot orbit with a wrist.
        s=Sculpt()
        transforms=matrices(pose('captive',0))
        for side,sign in (('L',1),('R',-1)):
            bone=IDS[f'arm_{side}_end']; wrist=transforms[bone][0]
            s.box(f'frame_{side}_foot',(-2,sign*13,1),(7,3,1),'wood')
            s.box(f'frame_{side}_post',(-2,sign*13,19),(1.5,1.5,18),'wood')
            s.box(f'frame_{side}_iron',(-2,sign*13,21),(1.7,1.7,.8),'glow')
            # A broad cuff encircles the wrist, with a visible attachment eye.
            for k in (-.45,0,.45):
                c=REST[bone]
                pts=[(*add(c,(1.4*math.cos(i*math.tau/20),1.4*math.sin(i*math.tau/20),k)),.4) for i in range(21)]
                s.strand(f'binding_{side}_cuff',pts,'glow',8,1)
            anchor=(-.3,sign*13,21)
            delta=sub(anchor,wrist); length=math.dist(anchor,wrist)
            from .rat import unit,cross,mul
            along=unit(delta); across=unit(cross(along,(0,0,1))); other=cross(along,across)
            count=math.ceil(length/1.25)
            for link in range(count+1):
                t=link/count
                center=add(wrist,mul(delta,t))
                # Slight slack, with both ends exactly at cuff and post.
                center=add(center,(0,0,-1.2*math.sin(math.pi*t)))
                plane=across if link%2 else other
                pts=[(*add(center,add(mul(along,.9*math.cos(i*math.tau/16)),mul(plane,.55*math.sin(i*math.tau/16)))),.22) for i in range(17)]
                s.strand(f'frame_{side}_link{link}',pts,'glow',8,1)
        s.box('frame_crossbar',(-2,0,36),(1.7,15,1.6),'wood')
        for part in s.parts:
            if part.name.startswith('frame_'):
                part.skin_weights=[[(IDS['root'],1)] for _ in part.vertices]
        parts+=s.parts
    return assemble(parts,weights)
def matrices(frame):return RIG.matrices(frame)
def deform(v,w,frame):return RIG.deform(v,w,frame)
def animation_data(v,w):return sample_clips(RIG,CLIPS,pose,v,w)
def restraint_geometry():
    """Detached assembly starts exactly where the captive model left it."""
    from .rat import Part
    source=geometry(True)[0];parts=[]
    for part in source:
        if not part.name.startswith(('binding','frame_')):continue
        influences=getattr(part,'skin_weights',None)
        if influences is None:influences=[weights(part,v,u) for v,u in zip(part.vertices,part.uv)]
        detached=Part(part.name,deform(part.vertices,influences,pose('captive',0)),part.uv,part.faces)
        parts.append(detached)
    for i,part in enumerate(parts):part.skin_weights=[[(i+1,1)] for _ in part.vertices]
    return assemble(parts,lambda p,v,u:[(0,1)])

def collapse_data(parts,v,w):
    from .skeletal import rotate
    collapse_rig=Rig.from_world([('root',None,(0,0,0))]+[(p.name+'_'+str(i),'root',(0,0,0)) for i,p in enumerate(parts)])
    def falling(name,t):
        progress=min(1,t/.85);progress=progress*progress
        frame=[(0,0,0,0,0,0,1,1,1,1)]
        for part in parts:
            # Feet stay planted; boards and loose iron fall independently so
            # the cuffs cannot remain suspended above the fallen frame.
            angle=0 if part.name.endswith('_foot') else -math.pi/2*progress
            q=axis((0,1,0),angle)
            endq=axis((0,1,0),0 if part.name.endswith('_foot') else -math.pi/2)
            final_min=min(rotate(endq,p)[2] for p in part.vertices)
            height=-final_min*progress
            height=max(height,-min(rotate(q,p)[2] for p in part.vertices))
            frame.append((0,0,height,*q,1,1,1))
        return frame
    clips,bounds=sample_clips(collapse_rig,[('collapse',29,35,False)],falling,v,w)
    return collapse_rig,clips,bounds

def build_restraints():
    parts,v,n,uv,tri,w=restraint_geometry()
    rig,clips,bounds=collapse_data(parts,v,w)
    payload=iqm.encode(v,n,uv,tri,w,rig.bones,clips,bounds,mesh_label='Released_monkey_restraints',material_path=monkey_materials.SKIN)
    (ROOT/'mod/BrogueDoom/models/monsters/05_monkey_restraints.iqm').write_bytes(payload)
    return {'model':'05_monkey_restraints.iqm','sha256':hashlib.sha256(payload).hexdigest(),'frames':29}

def build():
    (ROOT/'mod/BrogueDoom'/monkey_materials.SKIN).write_bytes(monkey_materials.texture_bytes())
    variants={}
    for captive in (False,True):
        parts,v,n,uv,tri,w=geometry(captive);clips,bounds=animation_data(v,w)
        model='05_monkey'+('_captive' if captive else '')+'.iqm'
        payload=iqm.encode(v,n,uv,tri,w,BONES,clips,bounds,mesh_label='Project_Broom_monkey',material_path=monkey_materials.SKIN)
        (ROOT/'mod/BrogueDoom/models/monsters'/model).write_bytes(payload)
        variants['captive' if captive else 'normal']={'model':model,'sha256':hashlib.sha256(payload).hexdigest(),'vertices':len(v),'triangles':len(tri)}
        if not captive:
            manifest={'schemaVersion':1,'workId':'BRG-M05','format':'IQM v2','runtimeModel':'mod/BrogueDoom/models/monsters/'+model,'sha256':hashlib.sha256(payload).hexdigest(),'skin':monkey_materials.SKIN,'skinSha256':hashlib.sha256(monkey_materials.texture_bytes()).hexdigest(),'parts':len(parts),'vertices':len(v),'triangles':len(tri),'boneCount':len(BONES),'dimensions':[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],'clips':[{k:v for k,v in c.items() if k!='frames'}|{'frameCount':len(c['frames'])} for c in clips],'bones':[{'name':n,'parent':p,'local':v} for n,p,v in BONES],'poseBounds':bounds,'authoringSource':'assets/monsters/monkey/monkey-animated.blend'}
    manifest['restraints']=build_restraints()
    manifest['variants']=variants;out=ROOT/'assets/monsters/monkey';out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Monkey',variants);return manifest
if __name__=='__main__':build()

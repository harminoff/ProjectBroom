"""Planted makeshift goblin totem: rigid wood/bone joinery and hanging charms.

All mechanics, haste and spark remain Brogue-owned. The unused movement role
rests. Independent hinges are real separated objects, not organic anatomy.
"""
import hashlib
import json
import math
from . import iqm, goblin_totem_materials as materials
from .rat import ROOT, Part, add, sub, mul, tube, ellipsoid
from .skeletal import Rig, axis, assemble, sample_clips

SKIN='graphics/BRGTOTEM.png'
SPECS=[('root',None,(0,0,0)),('stump','root',(0,0,3)),('crown','root',(0,0,20)),
       ('crossbar','crown',(0,0,27)),('charm_L','crossbar',(1,13,27)),
       ('charm_R','crossbar',(1,-12,28)),('charm_mid','crown',(4,0,25)),
       ('rag_L','crossbar',(-1,9,26)),('rag_R','crossbar',(-1,-9,26))]
RIG=Rig.from_world(SPECS);BONES,REST=RIG.bones,RIG.rest
IDS={name:i for i,(name,_,_) in enumerate(BONES)}
CLIPS=[('idle',40,20,True),('rest',20,20,True),('rattle',18,35,False),
       ('shudder',22,35,False),('recoil',12,35,False),('collapse',30,35,False)]


def geometry():
    parts=[]
    def put(p,role,bone='crown',swap=False):
        materials.repack(p,role,swap);p.skin_weights=[[(IDS[bone],1)]]*len(p.vertices);parts.append(p)
    def stick(name,points,role='wood',bone='crown',sides=10,samples=2):
        put(tube(name,points,'tail',sides,samples),role,bone,True)
    def oval(name,center,radius,role,bone='crown',segments=16,rings=8):
        put(ellipsoid(name,center,radius,'paw',segments,rings),role,bone)
    def ring(name,center,a,b,radius,role,bone='crown',steps=20):
        points=[(*add(center,add(mul(a,math.cos(math.tau*j/steps)),mul(b,math.sin(math.tau*j/steps)))),radius) for j in range(steps+1)]
        stick(name,points,role,bone,6,1)
    def plank(name,outline,x,thickness,role='mask',bone='crown'):
        if sum(y*Z-Y*z for (y,z),(Y,Z) in zip(outline,outline[1:]+outline[:1]))<0:
            outline=list(reversed(outline))
        p=Part(name);ymin=min(y for y,z in outline);ymax=max(y for y,z in outline)
        zmin=min(z for y,z in outline);zmax=max(z for y,z in outline)
        for face_x in (x-thickness,x):
            for y,z in outline:p.vertex((face_x,y,z),'paw',(y-ymin)/(ymax-ymin),(z-zmin)/(zmax-zmin))
        # Ear clipping keeps concave ragged hems front-facing. A polygon fan
        # would bridge its notches with backwards triangles.
        def orient(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
        remaining=list(range(len(outline)));triangles=[]
        while len(remaining)>3:
            for k,b in enumerate(remaining):
                a,c=remaining[k-1],remaining[(k+1)%len(remaining)]
                A,B,C=(outline[i] for i in (a,b,c))
                if orient(A,B,C)<=1e-10:continue
                if any(all(orient(U,V,outline[j])>=-1e-10 for U,V in ((A,B),(B,C),(C,A)))
                       for j in remaining if j not in (a,b,c)):continue
                triangles.append((a,b,c));remaining.pop(k);break
            else:raise ValueError('Cannot triangulate plank: '+name)
        triangles.append(tuple(remaining))
        n=len(outline)
        p.faces=[tuple(reversed(t)) for t in triangles]+[tuple(i+n for i in t) for t in triangles]
        p.faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
        put(p,role,bone)
    # Angular footing stones with individual silhouettes, no floating base disc.
    for i in range(9):
        a=i*math.tau/9;r=5.6+.6*math.sin(i*2)
        oval('footing_stone_%02d'%i,(r*math.cos(a),r*math.sin(a),1.5),
             (3.4,2.6,1.38),'stone','root',7,4)
    # Two naturally cracked lengths of timber, with exposed splinter ends.
    stick('stump_timber',[(0,0,.7,3.1),(.3,-.4,7,3),(-.3,0,16,2.6),(.5,.3,23,2.4)],bone='stump',sides=13,samples=3)
    stick('crown_timber',[(.2,0,18,2.5),(-.5,.1,27,2.4),(-1,0,36,2.1),(-.7,.5,43,1.6)],sides=13,samples=3)
    for i in range(5):
        a=i*math.tau/5
        stick('split_splinter_%d'%i,[(-.6+1.2*math.cos(a),.4+1.2*math.sin(a),40,.45),
             (-1+1.6*math.cos(a),.6+1.5*math.sin(a),44+(i%3),.03)],'cut',sides=6,samples=1)
    stick('crooked_crosspiece',[(-.8,-15,28,1),(-.1,-7,28,1.5),(0,0,27,1.7),(-.3,7,27,1.3),(0,15,25.8,.8)],bone='crossbar',sides=11,samples=3)
    stick('lower_brace',[(-2.3,-9,15,.7),(-2,0,20,1),(-2,9,23,.65)],bone='stump',sides=8,samples=2)
    for i,z in enumerate((9,10,11,20,21,22,26,27,28,39,40)):
        ring('post_lashing_%02d'%i,(0,0,z),(2.9,0,.16),(0,3.1,-.16),.25,'cord','stump' if z<24 else 'crown')
    # Broad asymmetric carved plank mask. Recessed dark eyes are carvings,
    # bordered by raised wood brow and cheeks; no live eye or jaw mechanism.
    outline=[(-6.5,27),(-8,31),(-7.4,39),(-5.7,42),(0,43.2),(6.6,41.6),(8.2,37.5),(7.5,30),(4.7,26.2),(0,24.5)]
    # Counterclockwise in the Y/Z plane gives the +X front normal.
    outline=list(reversed(outline))
    plank('carved_mask_board',outline,3.5,2.3)
    for side in (-1,1):
        s='L' if side>0 else 'R'
        oval('mask_socket_'+s,(3.64,side*3.7,36),(.16,2.1,1.36),'dark')
        ring('carved_orbital_rim_'+s,(3.85,side*3.7,36),(0,2.12,.25),(0,0,1.38),.32,'wood')
        stick('angular_brow_'+s,[(3.9,side*.5,39,.6),(4,side*4,38.4,.8),(3.7,side*6.8,39,.4)],'cut',sides=6)
        stick('cheek_ridge_'+s,[(3.9,side*6.1,35,.65),(4.1,side*5,32,.7),(3.6,side*3,29,.35)],'wood',sides=6)
        # Bone crown attached behind mask, intentionally asymmetrical.
        stick('bone_crown_'+s,[(0,side*5.5,40,1.2),(-.2,side*9,43,1),(-.9,side*10.8,47.5,.55),(-1,side*(10 if side>0 else 12),50 if side>0 else 48,.06)],'bone',sides=12,samples=3)
        for j in range(3):
            ring('crown_binding_'+s+str(j),(0,side*5.5,40+j*.45),(1.4,0,0),(0,.6,1),.19,'cord')
    plank('carved_nose',[(-1.4,38),(0,40),(1.6,37),(.9,32),(-.7,31)],5.1,1.5,'cut')
    oval('mask_mouth_recess',(3.7,0,29.7),(.2,3.1,1.5),'dark')
    for i in range(7):
        y=(i-3)*.82
        stick('bone_inlaid_tooth_'+str(i),[(4.03,y,30.6,.29),(4.2,y+.08,28.9+(i%2)*.35,.18)],'bone',sides=6,samples=1)
    # Rigid hanging bone beads have true drilled holes and independent hinges.
    for label,y,z,bone in [('L',13,27,'charm_L'),('R',-12,28,'charm_R'),('mid',0,25,'charm_mid')]:
        x=1 if label!='mid' else 4.2
        stick('hanging_hemp_'+label,[(x,y,z,.17),(x+.2,y+.2,z-4,.17)],'cord',bone,6,2)
        ring('drilled_bone_'+label,(x+.2,y+.2,z-5.1),(0,1.05,0),(0,0,1.25),.48,'bone',bone,18)
        stick('long_bone_'+label,[(x+.2,y+.2,z-6,.64),(x+.4,y+.1,z-9,.44),(x+.3,y+.1,z-11,.67)],'bone',bone,9,3)
        for j in range(2):oval('bone_knuckle_'+label+str(j),(x+.2,y+(-.25 if j else .5),z-11),(.6,.52,.5),'bone',bone,8,4)
    # Ragged cloth strips: thick folded sewn pieces, deliberately mismatched.
    for side in (-1,1):
        s='L' if side>0 else 'R';y=side*9
        outline=[(y-1.8,26),(y+1.8,26),(y+1.5,17),(y+.2,13),(y-.4,15),(y-1.6,12.5)]
        plank('ragged_ochre_strip_'+s,list(reversed(outline)),-.3,.22,'cloth','rag_'+s)
        for j in range(4):
            stick('cloth_stitch_'+s+str(j),[(-.04,y-1.2+j*.75,25,.09),(-.03,y-1.1+j*.75,24.3,.09)],'cord','rag_'+s,5,1)
    # Visible wood pegs, cracked grooves and protruding end grain enrich close views.
    for y,z in [(-5,40),(5,39),(0,26),(-5,31),(5,30)]:
        stick('joinery_peg_%s_%s'%(y,z),[(3.2,y,z,.35),(4.3,y,z,.29)],'cut',sides=7,samples=1)
    for i,y in enumerate((-6,-2.3,2.5,6)):
        stick('scored_mask_split_'+str(i),[(3.55,y,33+i*.7,.055),(3.56,y+.35,36+i*.5,.035),(3.56,y+.1,40,.015)],'dark',sides=4,samples=1)
    return assemble(parts,lambda p,v,u: [(0,1)])


def pose(name,t):
    frame=[[*local,0,0,0,1,1,1,1] for _,_,local in BONES]
    def turn(bone,deg,direction=(1,0,0)):frame[IDS[bone]][3:7]=axis(direction,math.radians(deg))
    if name=='rest':return [tuple(row) for row in frame]
    phase=math.tau*t
    if name=='idle':
        for i,b in enumerate(('charm_L','charm_R','charm_mid','rag_L','rag_R')):turn(b,2*math.sin(phase+i*.6))
    elif name=='collapse':
        s=t*t*(3-2*t)
        turn('stump',68*s,(0,1,0));turn('crown',83*s,(0,1,0))
        frame[IDS['stump']][2]+=2*s
        frame[IDS['crown']][0]-=13*s;frame[IDS['crown']][2]-=14*s
        turn('crossbar',13*s,(0,0,1))
        for i,b in enumerate(('charm_L','charm_R','charm_mid','rag_L','rag_R')):turn(b,(21 if i%2 else -17)*s)
    else:
        pulse=math.sin(math.pi*t)**2
        amplitude={'rattle':4,'shudder':6,'recoil':-8}[name]
        turn('crown',amplitude*pulse,(0,1,0));turn('crossbar',2*pulse)
        for i,b in enumerate(('charm_L','charm_R','charm_mid','rag_L','rag_R')):turn(b,11*pulse*math.sin(phase*2+i))
    return [tuple(row) for row in frame]


def matrices(frame):return RIG.matrices(frame)
def deform(v,w,frame):return RIG.deform(v,w,frame)
def animation_data(v,w):return sample_clips(RIG,CLIPS,pose,v,w)


def build():
    skin=materials.texture_bytes();(ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts,v,n,uv,t,w=geometry();clips,bounds=animation_data(v,w)
    data=iqm.encode(v,n,uv,t,w,BONES,clips,bounds,mesh_label='Project_Broom_goblin_totem',material_path=SKIN)
    path=ROOT/'mod/BrogueDoom/models/monsters/11_goblin_totem.iqm';path.write_bytes(data)
    manifest=dict(schemaVersion=1,workId='BRG-M11',format='IQM v2',runtimeModel=path.relative_to(ROOT).as_posix(),
        sha256=hashlib.sha256(data).hexdigest(),skin=SKIN,skinSha256=hashlib.sha256(skin).hexdigest(),
        dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],
        parts=len(parts),vertices=len(v),triangles=len(t),boneCount=len(BONES),
        bones=[dict(name=n,parent=p,local=v) for n,p,v in BONES],
        clips=[{k:v for k,v in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],
        poseBounds=bounds,authoringSource='assets/monsters/goblin_totem/goblin-totem-animated.blend')
    out=ROOT/'assets/monsters/goblin_totem';out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__':print(build()['sha256'])

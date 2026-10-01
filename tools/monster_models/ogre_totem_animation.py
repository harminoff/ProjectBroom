"""Ancient ogre-built occult assembly. Fixed supports, no locomotion or spells.

Original geometry, distinct from the goblin's carved-mask post. Separate wood,
bone and masonry members are rigid joinery rather than disconnected anatomy.
"""
import hashlib
import json
import math
from .rat import ROOT, Part, add, sub, mul, tube, ellipsoid
from .skeletal import Rig, axis, assemble, sample_clips
from . import iqm, ogre_totem_materials as materials

SKIN='graphics/BRGOGTOT.png'
SPECS=[('root',None,(0,0,0)),('column_L','root',(1,11,14)),
       ('column_R','root',(1,-11,14)),('rear_beam','root',(-6,0,14)),
       ('crown','root',(2,0,46)),('tablet','crown',(6,0,57)),
       ('tally_L','crown',(4,20,35)),('tally_R','crown',(4,-20,35))]
RIG=Rig.from_world(SPECS);BONES,REST=RIG.bones,RIG.rest
IDS={name:i for i,(name,_,_) in enumerate(BONES)}
CLIPS=[('idle',40,20,True),('rest',20,20,True),('toll',22,35,False),
       ('tremor',24,35,False),('recoil',14,35,False),('collapse',34,35,False)]


def geometry():
    parts=[]
    def put(p,role,bone='crown',swap=False):
        materials.repack(p,role,swap);p.skin_weights=[[(IDS[bone],1)]]*len(p.vertices);parts.append(p);return p
    def beam(name,points,role='timber',bone='crown',sides=10,samples=2):
        return put(tube(name,points,'tail',sides,samples),role,bone,True)
    def oval(name,center,radius,role,bone='crown',segments=12,rings=6):
        return put(ellipsoid(name,center,radius,'paw',segments,rings),role,bone)
    def ring(name,center,a,b,radius,role,bone='crown',steps=24):
        # Closed transported tube with real central opening; no disk cap.
        p=Part(name);sides=8
        for i in range(steps+1):
            theta=math.tau*(i%steps)/steps;c=add(center,add(mul(a,math.cos(theta)),mul(b,math.sin(theta))))
            # All rings lie in coordinate planes, so radial/outside and normal
            # are unambiguous; wrap positions exactly at the seam.
            radial=add(mul(a,math.cos(theta)),mul(b,math.sin(theta)))
            length=math.sqrt(sum(x*x for x in radial));radial=mul(radial,1/length)
            normal=(1,0,0) if a[0]==b[0]==0 else (0,0,1)
            for j in range(sides+1):
                q=math.tau*(j%sides)/sides
                p.vertex(add(c,add(mul(radial,radius*math.cos(q)),mul(normal,radius*math.sin(q)))),'tail',i/steps,j/sides)
        for i in range(steps):
            for j in range(sides):
                k=i*(sides+1)+j;p.faces.append((k,k+sides+1,k+sides+2,k+1))
        return put(p,role,bone)
    def slab(name,outline,front,depth,role,bone='crown'):
        # Convex chipped/beveled plate, two contour rings and front/back fans.
        if sum(y*Z-Y*z for (y,z),(Y,Z) in zip(outline,outline[1:]+outline[:1]))<0:outline=list(reversed(outline))
        p=Part(name);cy=sum(y for y,z in outline)/len(outline);cz=sum(z for y,z in outline)/len(outline)
        lo=min(z for y,z in outline);hi=max(z for y,z in outline);left=min(y for y,z in outline);right=max(y for y,z in outline)
        for x,factor in ((front-depth,.9),(front-.5,1),(front,.9)):
            for y,z in outline:p.vertex((x,cy+(y-cy)*factor,cz+(z-cz)*factor),'paw',(y-left)/(right-left),(z-lo)/(hi-lo))
        n=len(outline)
        p.faces=[tuple(reversed(range(n))),tuple(range(n*2,n*3))]
        for row in (0,1):
            for i in range(n):
                a=row*n+i;b=row*n+(i+1)%n;p.faces.append((a,b,b+n,a+n))
        return put(p,role,bone)
    # Broad cracked foundation is fixed, not a mobile actor's foot circle.
    for i,(x,y,rx,ry,rz) in enumerate([(-4,0,11,12,2),(3,12,9,9,1.8),(3,-12,9,9,2),(-8,10,6,6,1.5),(-9,-10,6,7,1.7)]):
        oval('foundation_block_%d'%i,(x,y,rz+.15),(rx,ry,rz),'stone','root',7,4)
    # Three substantial hewn supports, each with a fixed buried stump.
    for side in (-1,1):
        label='L' if side>0 else 'R';bone='column_'+label;y=side*11
        beam('buried_stump_'+label,[(1,y,.7,4.3),(1,y,7,4.4),(.5,y,14,4)],bone='root',sides=8,samples=2)
        beam('hewn_column_'+label,[(.5,y,12,4),(0,y-side*.7,24,4.1),(-.2,y-side*2,34,3.8),(.8,y-side*3,40,3.1)],bone=bone,sides=8,samples=3)
        for j in range(3):
            ring('stump_strap_'+label+str(j),(1,y,5+j*.72),(4.5,0,0),(0,4.5,0),.42,'bronze','root',16)
        for j in range(3):
            ring('leather_wrap_'+label+str(j),(0,y-side,26+j*.65),(4.25,0,0),(0,4.25,0),.38,'leather',bone,16)
        for j in range(3):
            beam('deep_split_'+label+str(j),[(4.32,y-1.8+j*1.65,14,.13),(4.18,y-1.6+j*1.65,20+j*.9,.10),(3.72,y-1.9+j*1.65,24+j*.8,.02)],'incision',bone,4,2)
        # Weathered bone scutes, bound flat to the wood rather than human limbs.
        for j in range(3):
            z=17+j*4.5
            slab('bone_scute_'+label+str(j),[(y-2.5,z-1),(y,z-1.8),(y+2.4,z-.5),(y+1.5,z+1.4),(y-1.6,z+1.7)],5.1,.8,'bone',bone)
            for yy in (y-1.6,y+1.6):oval('scute_pin_'+label+str(j)+str(yy),(5.18,yy,z),(.2,.25,.25),'bronze',bone,8,4)
    beam('buried_rear_stump',[(-6,0,.8,4),(-6,0,14,3.5)],bone='root',sides=8,samples=2)
    beam('rear_hewn_support',[(-6,0,12,3.5),(-4.5,0,23,3.6),(-2,0,36,3)],bone='rear_beam',sides=8,samples=3)
    # A heavy upper crossmember carries the open bone cage and its tablet.
    beam('crown_crossmember',[(1,-21,35,2.8),(0,-10,35,3.5),(0,0,34,4),(1,11,35,3.2),(2,21,35,2.3)],sides=10,samples=2)
    for side in (-1,1):
        label='L' if side>0 else 'R'
        # Two curved long bones on each side create a deep, incomplete arch.
        beam('outer_bone_arch_'+label,[(1,side*17,35,2.1),(1,side*19,44,2.3),(.6,side*15.5,54,1.9),(.5,side*8,60,1.5),(.8,side*2.8,61.4,1)],'bone',sides=13,samples=4)
        beam('rear_bone_arch_'+label,[(-3,side*12,36,1.4),(-4,side*14.2,44,1.6),(-3,side*11,53,1.2),(-1.5,side*5,58,.7)],'bone',sides=11,samples=3)
        # Diagonal braces make the arch read as assembled architecture.
        beam('bone_diagonal_brace_'+label,[(3.8,side*17,36,1),(4,side*10,42,1.1),(3.6,side*7,50,.5)],'bone',sides=9,samples=3)
        for j in range(4):
            ring('arch_hide_binding_'+label+str(j),(1,side*17,36.5+j*.65),(2.5,0,0),(0,2.5,0),.32,'leather',steps=16)
        # Suspended scored tablets below crossbar, with true drilled rings.
        bone='tally_'+label
        ring('hanging_link_'+label,(4,side*20,33),(0,1.1,0),(0,0,1.6),.28,'bronze',bone,18)
        outline=[(side*20-1.7,31.3),(side*20+1.8,31),(side*20+2.1,23),(side*20+.8,21),(side*20-1.9,22.8)]
        slab('bone_tally_'+label,outline,4.8,.7,'bone',bone)
        beam('tally_staple_'+label,[(4.3,side*20,31.7,.2),(5.1,side*20,31.3,.2),
             (5.1,side*20,29.8,.2),(4.5,side*20,29.6,.2)],'bronze',bone,8,2)
        for j in range(5):
            beam('tally_score_'+label+str(j),[(4.84,side*20-1.2,23.5+j*1.3,.07),(4.87,side*20+.9,24+j*1.3,.05)],'incision',bone,4,1)
    # Crown keystone is plainly stone, without a face, living eye or glow.
    slab('crown_keystone',[(-3,57),(-4.7,61),(-3,64.2),(3.3,64.6),(4.8,60),(2.7,57)],3,5,'stone')
    for yy in (-2,2):beam('keystone_pin_'+str(yy),[(3,yy,60.5,.42),(3.8,yy,60.5,.31)],'bronze',sides=8,samples=1)
    beam('crown_suspension_pin',[(2.5,0,57.3,.35),(6.3,0,57.3,.35)],'bronze',sides=10,samples=1)
    # Solid engraved greenstone tablet pivots from its own bronze suspension.
    ring('tablet_hanger',(6,0,55.8),(0,1.2,0),(0,0,1.5),.36,'bronze','tablet',20)
    slab('greenstone_tablet',[(-4,53.6),(-5.7,51.8),(-5.2,41),(0,37.8),(5.2,40.7),(5.7,52),(3.3,54)],6.6,2.1,'tablet','tablet')
    beam('tablet_bronze_staple',[(6.1,0,54.6,.25),(7.1,0,54.2,.25),
         (7.1,0,52.8,.25),(6.2,0,52.5,.25)],'bronze','tablet',8,2)
    # Original geometric score marks, no imported alphabet or asserted lore.
    strokes=[((-2.5,51),(2.5,51)),((0,51),(0,42)),((-3.1,48),(0,45)),((0,45),(3.1,48)),((-2.4,42.5),(0,40.5)),((0,40.5),(2.4,42.5))]
    for i,((y,z),(Y,Z)) in enumerate(strokes):
        beam('tablet_incised_mark_'+str(i),[(6.62,y,z,.11),(6.64,Y,Z,.11)],'incision','tablet',6,1)
        beam('tablet_worn_mark_edge_'+str(i),[(6.65,y+.14,z,.045),(6.66,Y+.14,Z,.045)],'bone','tablet',5,1)
    # Heavy front collar and rivets unify the ancient assembly's materials.
    slab('bronze_collar',[(-11,30),(-11.8,33.5),(-9.5,36),(9,36),(11.5,33.5),(11,30)],5.8,1.3,'bronze')
    for i,y in enumerate((-9,-6,-3,0,3,6,9)):
        oval('collar_rivet_'+str(i),(5.88,y,33.1),(.32,.45,.45),'bronze',segments=8,rings=4)
    return assemble(parts,lambda p,v,u:[(0,1)])


def pose(name,t):
    frame=[[*local,0,0,0,1,1,1,1] for _,_,local in BONES]
    def turn(bone,degrees,direction=(0,1,0)):
        frame[IDS[bone]][3:7]=axis(direction,math.radians(degrees))
    if name=='rest':return [tuple(r) for r in frame]
    phase=math.tau*t
    if name=='idle':
        turn('tablet',1.2*math.sin(phase))
        turn('tally_L',1.8*math.sin(phase+.7),(1,0,0))
        turn('tally_R',1.4*math.sin(phase+1.5),(1,0,0))
    elif name=='collapse':
        smooth=t*t*(3-2*t)
        turn('column_L',83*smooth);turn('column_R',-80*smooth);turn('rear_beam',-92*smooth)
        turn('crown',88*smooth);frame[IDS['crown']][2]-=36*smooth;frame[IDS['crown']][0]+=2*smooth
        turn('tablet',-9*smooth);turn('tally_L',31*smooth,(1,0,0));turn('tally_R',-29*smooth,(1,0,0))
    else:
        pulse=math.sin(math.pi*t)**2
        if name=='toll':turn('tablet',-16*pulse)
        elif name=='tremor':turn('tablet',9*pulse*math.sin(phase*2))
        elif name=='recoil':turn('tablet',19*pulse);turn('crown',-2.2*pulse)
        else:raise ValueError(name)
        for bone,sign in (('tally_L',1),('tally_R',-1)):
            turn(bone,sign*12*pulse*math.sin(phase*1.5),(1,0,0))
    return [tuple(r) for r in frame]


def matrices(frame):return RIG.matrices(frame)
def deform(v,w,frame):return RIG.deform(v,w,frame)
def animation_data(v,w):return sample_clips(RIG,CLIPS,pose,v,w)


def build():
    skin=materials.texture_bytes();(ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts,v,n,uv,t,w=geometry();clips,bounds=animation_data(v,w)
    data=iqm.encode(v,n,uv,t,w,BONES,clips,bounds,mesh_label='Project_Broom_ogre_totem',material_path=SKIN)
    path=ROOT/'mod/BrogueDoom/models/monsters/20_ogre_totem.iqm';path.write_bytes(data)
    manifest=dict(schemaVersion=1,workId='BRG-M20',format='IQM v2',runtimeModel=path.relative_to(ROOT).as_posix(),
        sha256=hashlib.sha256(data).hexdigest(),skin=SKIN,skinSha256=hashlib.sha256(skin).hexdigest(),
        dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],
        parts=len(parts),vertices=len(v),triangles=len(t),boneCount=len(BONES),
        bones=[dict(name=n,parent=p,local=v) for n,p,v in BONES],
        clips=[{k:v for k,v in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],
        poseBounds=bounds,authoringSource='assets/monsters/ogre_totem/ogre-totem-animated.blend')
    out=ROOT/'assets/monsters/ogre_totem';out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__':print(build()['sha256'])

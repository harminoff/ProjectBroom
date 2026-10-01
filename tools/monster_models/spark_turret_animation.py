"""Original wall-mounted electrical contraption with copper coils, crystals and raised sigils."""
import hashlib,json,math
from . import iqm,spark_turret_materials as materials
from .rat import ROOT,Part,add,sub,mul,tube,ellipsoid
from .skeletal import Rig,axis,assemble,sample_clips
SKIN='graphics/BRGSPARK.png'
SPECS=[('root',None,(0,0,0)),('mechanism','root',(-5,0,23)),('core','mechanism',(4,0,23)),('prong_L','mechanism',(1,7,23)),('prong_R','mechanism',(1,-7,23)),('crown','mechanism',(1,0,30))]
RIG=Rig.from_world(SPECS);BONES,REST=RIG.bones,RIG.rest
IDS={n:i for i,(n,_,_) in enumerate(BONES)}
CLIPS=[('idle',40,20,True),('rest',20,20,True),('discharge',22,35,False),('recharge',26,35,False),('impact',12,35,False),('break',32,35,False)]

def geometry():
    parts=[]
    def put(p,role,bone='mechanism'):
        materials.repack(p,role);p.skin_weights=[[(IDS[bone],1)]]*len(p.vertices);parts.append(p);return p
    def stick(name,pts,role='iron',bone='mechanism',sides=10,samples=2):
        return put(tube(name,pts,'tail',sides,samples),role,bone)
    def ball(name,c,r,role='brass',bone='mechanism',seg=12,rings=6):
        return put(ellipsoid(name,c,r,'paw',seg,rings),role,bone)
    def box(name,c,r,role='iron',bone='mechanism'):
        p=Part(name)
        for face in [((1,-1,-1),(1,1,-1),(1,1,1),(1,-1,1)),((-1,1,-1),(-1,-1,-1),(-1,-1,1),(-1,1,1)),
                     ((-1,1,-1),(-1,1,1),(1,1,1),(1,1,-1)),((1,-1,-1),(1,-1,1),(-1,-1,1),(-1,-1,-1)),
                     ((-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)),((-1,1,-1),(1,1,-1),(1,-1,-1),(-1,-1,-1))]:
            start=len(p.vertices)
            for v,uv in zip(face,((0,0),(1,0),(1,1),(0,1))):p.vertex(tuple(c[i]+v[i]*r[i] for i in range(3)),'paw',*uv)
            p.faces.append(tuple(start+i for i in range(4)))
        return put(p,role,bone)
    def coil(name,c,radius,pitch,turns,role='edge',bone='mechanism'):
        pts=[]
        for i in range(turns*18+1):
            a=i*math.tau/18;pts.append((c[0]+radius*math.cos(a),c[1]+pitch*i/18,c[2]+radius*math.sin(a),.24))
        stick(name,pts,role,bone,6,1)
    def crystal(name,c,length,radius,bone):
        p=Part(name)
        for x,r in ((0,radius*.65),(length*.23,radius),(length*.75,radius*.82)):
            for j in range(6):
                a=j*math.tau/6;p.vertex((c[0]+x,c[1]+r*math.cos(a),c[2]+r*math.sin(a)),'paw',j/6,x/length)
        p.vertex((c[0]+length,c[1],c[2]),'paw',.5,1)
        p.faces=[tuple(reversed(range(6)))]
        for k in range(2):
            for j in range(6):p.faces.append((k*6+j,k*6+(j+1)%6,(k+1)*6+(j+1)%6,(k+1)*6+j))
        for j in range(6):p.faces.append((12+j,12+(j+1)%6,18))
        return put(p,'crystal',bone)
    # Octagonal plate with a deep layered bezel, radial buttresses and anchors.
    stick('octagonal_wall_plaque',[(-12,0,23,19.5),(-10,0,23,19.5)],'iron','root',8,1)
    stick('raised_brass_bezel',[(-9.9,0,23,17.8),(-9.3,0,23,17.8)],'brass','root',16,1)
    stick('dark_recessed_face',[(-9.2,0,23,16.6),(-8.9,0,23,16.6)],'dark','root',16,1)
    for j in range(8):
        a=j*math.tau/8;y=17.5*math.cos(a);z=23+17.5*math.sin(a)
        ball('forged_wall_anchor_'+str(j),(-8.6,y,z),(.8,1,1),'edge','root',6,3)
        stick('radial_plate_rib_'+str(j),[(-8.4,10*math.cos(a),23+10*math.sin(a),.5),(-8.4,16*math.cos(a),23+16*math.sin(a),.7)],'brass','root',6,1)
    def ring(name,x,r,role,bone='root',thickness=.3):
        stick(name,[(x,r*math.cos(j*math.tau/48),23+r*math.sin(j*math.tau/48),thickness) for j in range(49)],role,bone,6,1)
    for j,r in enumerate((11,13.8,15.3)):ring('concentric_sigil_ring_'+str(j),-8.15,r,'brass')
    # Twelve individually raised angular sigils, not an image on a flat disk.
    for j in range(12):
        a=j*math.tau/12
        def q(r,d):return (-7.8,r*math.cos(a+d),23+r*math.sin(a+d),.2)
        stick('angular_sigil_'+str(j),[q(11.6,-.08),q(13.1,0),q(11.6,.08),q(12.4,.10)],'sigil','root',5,1)
    # Four ceramic capacitors with tightly wound copper conductors and crystal tips.
    for j in range(4):
        a=(j+.5)*math.tau/4;y=9*math.cos(a);z=23+9*math.sin(a)
        stick('ceramic_insulator_'+str(j),[(-8,y,z,2.4),(-1,y,z,2.4)],'ceramic','root',12,1)
        for k in range(5):
            stick('insulator_ridge_%d_%d'%(j,k),[(-7+k*1.1,y,z,2.8),(-6.6+k*1.1,y,z,2.8)],'ceramic','root',12,1)
        pts=[]
        for k in range(97):
            a2=k*math.tau/16;pts.append((-7+k/16*.85,y+3*math.cos(a2),z+3*math.sin(a2),.18))
        stick('copper_winding_'+str(j),pts,'copper','root',5,1)
        stick('capacitor_socket_'+str(j),[(-1,y,z,2.7),(1,y,z,2.7)],'brass','root',12,1)
        crystal('embedded_capacitor_crystal_'+str(j),(0,y,z),6,1.9,'root')
        stick('copper_feed_'+str(j),[(-6,y,z,.28),(-3,y*.6,23+(z-23)*.6,.28),(0,0,23,.28)],'copper','root',7,2)
    # Heavy central annular bearing and projecting hexagonal focusing crystal.
    stick('core_bearing',[(-8,0,23,6.6),(-4,0,23,6.6)],'iron','root',16,1)
    ring('core_bearing_edge',-3.8,5.4,'brass',thickness=.75)
    stick('core_cradle',[(-4,0,23,4.8),(5,0,23,4.8)],'dark','mechanism',12,1)
    crystal('large_focusing_crystal',(1,0,23),20,4.1,'core')
    for side in (-1,1):
        bone='prong_L' if side>0 else 'prong_R'
        ball('prong_hinge_'+bone,(1,side*7,23),(1.3,1.4,1.4),'brass')
        stick('curved_electrode_'+bone,[(-4,side*7,23,1),(4,side*7,23,.95),(12,side*5,23,.65),(17,side*3.5,23,.3)],'edge',bone,8,3)
        for k in range(3):ball('electrode_rivet_%s_%d'%(bone,k),(k*4,side*7,23.8),(.35,.4,.35),'brass',bone)
    stick('upper_electrode',[(-4,0,30,1),(4,0,31,.9),(12,0,28,.65),(17,0,26.5,.3)],'edge','crown',8,3)
    for y in (-10,10):stick('fixed_lower_brace_'+str(y),[(-9,y,6,1),(-4,y,12,1),(0,y*.5,20,1)],'iron','root',8,2)
    return assemble(parts,lambda p,v,u:[(0,1)])

def pose(name,t):
    f=[[*local,0,0,0,1,1,1,1] for _,_,local in BONES]
    def turn(b,deg,ax=(0,1,0)):f[IDS[b]][3:7]=axis(ax,math.radians(deg))
    if name in ('idle','rest'):return [tuple(r) for r in f]
    if name=='break':
        s=t*t*(3-2*t);turn('mechanism',33*s);turn('core',16*s);turn('prong_L',-32*s,(1,0,0));turn('prong_R',46*s,(1,0,0));turn('crown',-50*s)
    else:
        p=math.sin(math.pi*t)**2
        turn('prong_L',(-10 if name=='discharge' else 7)*p,(0,0,1));turn('prong_R',(10 if name=='discharge' else -7)*p,(0,0,1));turn('crown',7*p)
        f[IDS['core']][0]+=(2.2 if name=='discharge' else -1.2)*p
        if name=='impact':turn('mechanism',-5*p)
    return [tuple(r) for r in f]

def matrices(frame):return RIG.matrices(frame)
def deform(v,w,frame):return RIG.deform(v,w,frame)
def animation_data(v,w):return sample_clips(RIG,CLIPS,pose,v,w)
def build():
    skin=materials.texture_bytes();(ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts,v,n,uv,t,w=geometry();clips,bounds=animation_data(v,w)
    data=iqm.encode(v,n,uv,t,w,BONES,clips,bounds,mesh_label='Project_Broom_spark_turret',material_path=SKIN)
    path=ROOT/'mod/BrogueDoom/models/monsters/22_spark_turret.iqm';path.write_bytes(data)
    manifest=dict(schemaVersion=1,workId='BRG-M22',format='IQM v2',runtimeModel=path.relative_to(ROOT).as_posix(),
        sha256=hashlib.sha256(data).hexdigest(),skin=SKIN,skinSha256=hashlib.sha256(skin).hexdigest(),
        dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],
        parts=len(parts),vertices=len(v),triangles=len(t),boneCount=len(BONES),
        bones=[dict(name=n,parent=p,local=v) for n,p,v in BONES],
        clips=[{k:v for k,v in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],
        poseBounds=bounds,authoringSource='assets/monsters/spark_turret/spark-turret-animated.blend')
    out=ROOT/'assets/monsters/spark_turret';out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__':print(build()['sha256'])


"""Original fixed wall crossbow with coil springs, ratchet and captive bolt sled."""
import hashlib,json,math
from . import iqm,arrow_turret_materials as materials
from .rat import ROOT,Part,add,sub,mul,tube,ellipsoid
from .skeletal import Rig,axis,assemble,sample_clips
SKIN='graphics/BRGARROW.png'
SPECS=[('root',None,(0,0,0)),('mechanism','root',(-6,0,24)),
       ('sled','mechanism',(-1,0,29)),('drum_L','mechanism',(-1,8,26)),
       ('drum_R','mechanism',(-1,-8,26)),('trigger','mechanism',(-5,0,22)),
       ('limb_L','mechanism',(7,4,28)),('limb_R','mechanism',(7,-4,28))]
RIG=Rig.from_world(SPECS);BONES,REST=RIG.bones,RIG.rest
IDS={n:i for i,(n,_,_) in enumerate(BONES)}
CLIPS=[('idle',40,20,True),('rest',20,20,True),('release',20,35,False),('rearm',24,35,False),('recoil',12,35,False),('break',30,35,False)]

def geometry():
    parts=[]
    def put(p,role,bone='mechanism'):
        materials.repack(p,role);p.skin_weights=[[(IDS[bone],1)]]*len(p.vertices);parts.append(p);return p
    def stick(name,pts,role='iron',bone='mechanism',sides=10,samples=2):
        return put(tube(name,pts,'tail',sides,samples),role,bone)
    def ball(name,c,r,role='brass',bone='mechanism',seg=12,rings=6):
        return put(ellipsoid(name,c,r,'paw',seg,rings),role,bone)
    def box(name,c,r,role='wood',bone='mechanism'):
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
    # A broad wall plate, inset oak planks, straps and true projecting fasteners.
    box('iron_mount_plate',(-12,0,21),(1.1,15.7,20.88),'iron','root')
    for j in range(5):box('oak_mount_plank_'+str(j),(-10.6,(j-2)*5.9,21),(.55,2.77,19.9),'wood','root')
    for z in (3,39):
        box('mount_cross_strap_'+str(z),(-9.8,0,z),(.35,15.4,1),'iron','root')
        for y in (-12,0,12):
            stick('anchor_shank_%s_%s'%(y,z),[(-13.1,y,z,.6),(-9,y,z,.6)],'iron','root',8,1)
            ball('square_forged_anchor_%s_%s'%(y,z),(-8.7,y,z),(.7,.95,.95),'edge','root',4,2)
    # Cantilever remains on the wall even when the crossbow is broken.
    for side in (-1,1):
        y=side*8
        stick('fixed_angle_brace_'+str(side),[(-9.5,y,6,1.15),(-3,y,13,1.15),(5,y,23,1.15)],'iron','root',6,1)
        box('fixed_shelf_'+str(side),(-2,y,23),(9,1.4,1.1),'wood','root')
        stick('hinge_pin_'+str(side),[(-6,y-1.6,24,1),(-6,y+1.6,24,1)],'brass','root',12,1)
    box('crossbow_oak_stock',(2,0,27),(13,2.4,1.7))
    for side in (-1,1):
        box('iron_guide_rail_'+str(side),(3,side*2.8,29),(13,.38,.6),'edge')
    box('bolt_channel',(3,0,28.8),(12,.65,.16),'dark')
    box('sliding_string_carriage',(-3,0,29.5),(1.15,3.4,.65),'brass','sled')
    # Two layered sprung limbs arc forward from the stock and sweep rearward.
    for side in (-1,1):
        lab='L' if side>0 else 'R';bone='limb_'+lab
        for layer in range(3):
            stick('laminated_bow_'+lab+str(layer),[(7,side*3,28+layer*.34,.75),(7.8,side*9,28+layer*.34,.69),(5,side*15,28.3+layer*.34,.5),(1,side*20,29+layer*.2,.25)],'iron' if layer==1 else 'wood',bone,8,3)
        for k in range(3):
            y=side*(6+k*5);x=7.4 if k<2 else 4
            box('bow_binding_'+lab+str(k),(x,y,28.4),(.95,.34,1),'iron',bone)
        ball('limb_socket_'+lab,(7,side*4,28),(1.3,1.1,1.2),'brass')
        # A continuous taut cord, weighted between the tip and moving sled.
        p=stick('bowstring_'+lab,[(1,side*20,29.3,.13),(-3,0,30,.13)],'cord','sled',6,12)
        p.skin_weights=[]
        for v in p.vertices:
            t=max(0,min(1,abs(v[1])/20));p.skin_weights.append([(IDS[bone],t),(IDS['sled'],1-t)])
        # Wound steel spring and thick axle collars; original mechanical detail.
        coil('wound_spring_'+lab,(-1,side*8-2.8,26),2.1,.64,8,'edge','drum_'+lab)
        for y in (side*8-3.3,side*8+3.3):
            stick('spring_drum_flange_'+lab+str(y),[(-1,y-.25,26,2.5),(-1,y+.25,26,2.5)],'brass','drum_'+lab,16,1)
        stick('spring_axle_'+lab,[(-1,side*8-4,26,.55),(-1,side*8+4,26,.55)],'iron')
        for j in range(12):
            a=math.tau*j/12
            ball('ratchet_tooth_'+lab+str(j),(-1+2.6*math.cos(a),side*8+3.7,26+2.6*math.sin(a)),(.48,.35,.48),'iron','drum_'+lab,6,3)
        stick('tension_link_'+lab,[(-1,side*8,28,.23),(-3,side*3,30,.23)],'iron','sled',6,1)
    # Arrow cannot fly away cosmetically; it is a retained visual load.
    stick('loaded_arrow_shaft',[(-7,0,30.8,.22),(17,0,30.8,.22)],'cut','sled',8,1)
    p=Part('forged_arrowhead')
    for v in ((20,0,30.8),(15,-1,30.8),(15,0,31.45),(15,1,30.8),(15,0,30.15)):p.vertex(v,'paw',.5,.5)
    p.faces=[(0,1,2),(0,2,3),(0,3,4),(0,4,1),(1,4,3,2)];put(p,'edge','sled')
    for j in range(3):
        a=j*math.tau/3
        p=Part('feather_vane_'+str(j))
        vs=[(-7,0,30.8),(-6,1.3*math.cos(a),30.8+1.3*math.sin(a)),(-2,1.3*math.cos(a),30.8+1.3*math.sin(a)),(-1,0,30.8)]
        for v,uv in zip(vs,((0,0),(0,1),(1,1),(1,0))):p.vertex(v,'paw',*uv)
        p.faces=[(0,1,2,3),(3,2,1,0)];put(p,'feather','sled')
    stick('front_iron_stirrup',[(13,-3,26,.5),(17,-4,25,.5),(19,0,25,.5),(17,4,25,.5),(13,3,26,.5)],'iron',sides=8,samples=2)
    stick('trigger_sear',[(-5,0,23,.65),(-7,0,20,.6),(-6,0,18,.35)],'brass','trigger',8,2)
    # Rear wall-mounted magazine contains individually supported spare bolts.
    box('spare_bolt_rack',(-7,-11,33),(2.2,3,1),'iron','root')
    for j in range(4):
        y=-13+j*1.3
        stick('spare_bolt_'+str(j),[(-8,y,25,.23),(-8,y,37,.23)],'cut','root',7,1)
        ball('spare_bolt_head_'+str(j),(-8,y,38),(.48,.48,1.1),'edge','root',6,3)
    for y in (-2,2):
        for x in (-8,2,11):ball('stock_rivet_%s_%s'%(x,y),(x,y,29),(.4,.4,.25),'brass')
    return assemble(parts,lambda p,v,u:[(0,1)])

def pose(name,t):
    f=[[*local,0,0,0,1,1,1,1] for _,_,local in BONES]
    def turn(b,deg,ax=(0,1,0)):f[IDS[b]][3:7]=axis(ax,math.radians(deg))
    if name in ('idle','rest'):return [tuple(r) for r in f]
    if name=='break':
        s=t*t*(3-2*t);turn('mechanism',35*s);turn('limb_L',-28*s,(1,0,0));turn('limb_R',19*s,(1,0,0));turn('trigger',45*s)
        f[IDS['sled']][0]-=2*s
    else:
        p=math.sin(math.pi*t)**2
        f[IDS['sled']][0]+= (3 if name=='release' else -2.5)*p
        turn('mechanism',(-2 if name=='recoil' else 1)*p)
        turn('drum_L',75*p,(0,1,0));turn('drum_R',75*p,(0,1,0));turn('trigger',-22*p)
        turn('limb_L',-3*p,(0,0,1));turn('limb_R',3*p,(0,0,1))
    return [tuple(r) for r in f]

def matrices(frame):return RIG.matrices(frame)
def deform(v,w,frame):return RIG.deform(v,w,frame)
def animation_data(v,w):return sample_clips(RIG,CLIPS,pose,v,w)
def build():
    skin=materials.texture_bytes();(ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts,v,n,uv,t,w=geometry();clips,bounds=animation_data(v,w)
    data=iqm.encode(v,n,uv,t,w,BONES,clips,bounds,mesh_label='Project_Broom_arrow_turret',material_path=SKIN)
    path=ROOT/'mod/BrogueDoom/models/monsters/15_arrow_turret.iqm';path.write_bytes(data)
    manifest=dict(schemaVersion=1,workId='BRG-M15',format='IQM v2',runtimeModel=path.relative_to(ROOT).as_posix(),
        sha256=hashlib.sha256(data).hexdigest(),skin=SKIN,skinSha256=hashlib.sha256(skin).hexdigest(),
        dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],
        parts=len(parts),vertices=len(v),triangles=len(t),boneCount=len(BONES),
        bones=[dict(name=n,parent=p,local=v) for n,p,v in BONES],
        clips=[{k:v for k,v in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],
        poseBounds=bounds,authoringSource='assets/monsters/arrow_turret/arrow-turret-animated.blend')
    out=ROOT/'assets/monsters/arrow_turret';out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__':print(build()['sha256'])

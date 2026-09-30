"""Source-led warty toad. Connected anatomy and six cosmetic skeletal clips."""
import hashlib
import json
import math
from . import iqm, toad_materials as materials
from .creatures import Sculpt
from .rat import ROOT, add, sub, mul, unit
from .skeletal import Rig, axis, between, inverse, qmul, assemble, sample_clips

SKIN = materials.SKIN
SPECS = [('root',None,(0,0,0)), ('pelvis','root',(-7,0,10)),
         ('spine','pelvis',(0,0,12)), ('head','spine',(9,0,15)),
         ('throat','head',(12,0,9))]
for side, sign in (('L',1),('R',-1)):
    for limb, parent, points in (
        ('fore','spine',[(8,sign*9,12),(11,sign*14,6),(15,sign*13,1.8)]),
        ('hind','pelvis',[(-9,sign*8,11),(-2,sign*15,7),(-13,sign*16,2)])):
        for joint, point in zip(('upper','lower','end'),points):
            name = f'{limb}_{side}_{joint}'
            SPECS.append((name,parent,point)); parent = name
RIG = Rig.from_world(SPECS)
BONES, REST = RIG.bones, RIG.rest
IDS = {name:i for i,(name,parent,local) in enumerate(BONES)}
CLIPS = [('idle',40,20,True), ('crawl',24,35,True), ('slime',18,35,False),
         ('slam',22,35,False), ('recoil',12,35,False), ('death',28,35,False)]


def build_parts():
    s = Sculpt()
    s.oval('body',(-4,0,11),(14,12.5,10),seg=36,rings=22)
    s.oval('belly',(0,0,7.4),(12.5,10.9,5.1),'cloth',32,18)
    # Broad flat head, joined across the shoulders instead of a narrow neck.
    s.oval('head',(8,0,13.7),(11,11,7.2),seg=36,rings=20)
    s.oval('throat',(11,0,8.2),(7.6,8.8,3.7),'cloth',28,16)
    for side,sign in (('L',1),('R',-1)):
        s.oval('head_brow_'+side,(10.9,sign*7.5,19.3),(4.0,3.4,3.15),seg=24,rings=16)
        s.oval('gland_'+side,(1.8,sign*9.0,18.0),(5.6,3.6,1.65),seg=24,rings=14)
        # Eyes sit in the brow, with a horizontal pupil on the forward surface.
        s.oval('eye_iris_'+side,(14.0,sign*7.65,19.7),(.72,1.85,1.22),'accent',24,16)
        s.oval('eye_pupil_'+side,(14.69,sign*7.65,19.72),(.085,1.15,.3),'dark',20,12)
        # Heavy upper/lower lids overlap the eye rim instead of a separate bead.
        for upper in (True,False):
            arc=[]
            for i in range(15):
                a=math.pi*i/14
                arc.append((14.05+.34*math.sin(a),sign*7.65+1.95*math.cos(a),
                            19.7+(1 if upper else -1)*1.10*math.sin(a),.31 if upper else .20))
            s.strand('head_lid_'+side+('_upper' if upper else '_lower'),arc,sides=8,samples=1)
        s.oval('nostril_'+side,(17.72,sign*3.55,15.8),(.35,.52,.27),'dark',12,8)
        for limb in ('fore','hind'):
            points = [REST[IDS[f'{limb}_{side}_{j}']] for j in ('upper','lower','end')]
            radii = (3.2,2.4,1.15) if limb=='fore' else (5.1,3.6,1.45)
            s.strand(f'{limb}_{side}',[(*p,r) for p,r in zip(points,radii)],sides=20,samples=5)
            foot = points[-1]
            if limb=='fore':
                s.oval(f'foot_{limb}_{side}',add(foot,(.65,0,-.25)),(2.5,2.2,1.0),'cloth',20,12)
                for digit in range(4):
                    spread = (digit-1.5)*1.2
                    s.strand(f'toe_{limb}_{side}_{digit}',
                        [(15.5,sign*13+spread,1.45,.58),
                         (18.0+(1-abs(digit-1.5)/2),sign*13+spread*1.55,.85,.44),
                         (20.0-abs(digit-1.5)*.6,sign*13+spread*1.8,.72,.18)],
                        'cloth',8,3)
            else:
                # Tarsus folds forward alongside the calf; five spreading toes.
                s.strand(f'foot_{limb}_{side}',
                         [(*foot,1.6),(-9,sign*18,1.55,1.8),(-4,sign*18.5,1.2,1.45)],
                         'cloth',14,4)
                for digit in range(5):
                    spread = (digit-2)*.95
                    s.strand(f'toe_{limb}_{side}_{digit}',
                        [(-5,sign*18.5+spread,1.15,.5),
                         (-1,sign*18.5+spread*1.5,.75,.39),
                         (2.8-abs(digit-2)*1.2,sign*18.5+spread*1.9,.65,.16)],
                        'cloth',8,3)
    # A continuous smile-shaped mouth seam around the broad muzzle, no teeth.
    lip = []
    for i in range(25):
        a = -1.25 + 2.5*i/24
        lip.append((8+10.75*math.cos(a),10.45*math.sin(a),11.35-.55*math.cos(a),.23))
    s.strand('mouth_seam',lip,'dark',8,1)
    s.strand('mouth_lower',[(x-.12,y,z-.44,.34) for x,y,z,_ in lip],'cloth',10,1)
    # Low-amplitude irregular skin relief breaks the smooth primitive surfaces.
    # All variations are fixed spatial functions, isolated from Brogue RNG.
    for part in s.parts:
        if part.name in ('body','head') or part.name.startswith(('fore_','hind_','gland','head_brow')):
            normals=part.normals()
            part.vertices=[add(v,mul(n,.13*math.sin(v[0]*2.1+math.sin(v[1]*1.7))
                                      *math.sin(v[2]*2.6+v[1]*.8))) for v,n in zip(part.vertices,normals)]
    return materials.repack(s.parts)


def weights(part,v,uv):
    name = part.name
    if name.startswith(('eye','nostril','mouth','head')): return [(IDS['head'],1)]
    if name=='throat': return [(IDS['throat'],1)]
    if name.startswith(('foot','toe')):
        _,limb,side,*_ = name.split('_')
        return [(IDS[f'{limb}_{side}_end'],1)]
    if name.startswith(('fore','hind')):
        return RIG.chain_weights(v,[IDS[name+'_'+j] for j in ('upper','lower','end')])
    return RIG.chain_weights(v,[IDS[n] for n in ('pelvis','spine','head')])


def surface_warts(body):
    """Seat each wart on a baked triangle with exactly its barycentric weights.

    Geometry detail moves with the skin, including at the shoulders. The fixed
    spatial selection is an authoring pattern, not simulation randomness.
    """
    candidates = []
    normals = body.normals()
    for face in body.triangles():
        center = tuple(sum(body.vertices[i][a] for i in face)/3 for a in range(3))
        normal = unit(tuple(sum(normals[i][a] for i in face) for a in range(3)))
        x,y,z = center
        if z<9 or normal[2]<.30 or x>13 or abs(y)>17: continue
        candidates.append((center,normal,face))
    # Irregular golden-ratio ordering avoids horizontal rows of identical beads.
    candidates.sort(key=lambda c: ((c[0][0]*.754877666+c[0][1]*.569840296)%1,c[0]))
    chosen = []; parts = []
    for center,normal,face in candidates:
        if any(math.dist(center,c)<1.85 for c in chosen): continue
        chosen.append(center)
        radius = .55+.38*((center[0]*1.71+center[1]*2.39)%1)
        s = Sculpt()
        p = s.oval(f'wart_{len(parts):02d}',(0,0,0),(radius,radius*.85,radius*.43),
                   'accent',8,5)
        materials.repack(s.parts)
        tangent = unit((normal[2],0,-normal[0]))
        bitangent = (normal[1]*tangent[2],normal[2]*tangent[0]-normal[0]*tangent[2],-normal[1]*tangent[0])
        # The lower half intersects the skin; no detached bead or floating disc.
        p.vertices = [add(center,add(mul(tangent,x),add(mul(bitangent,y),mul(normal,z))))
                      for x,y,z in p.vertices]
        blend = {}
        for i in face:
            for bone,w in body.skin_weights[i]: blend[bone] = blend.get(bone,0)+w/3
        keep = sorted(blend.items(),key=lambda row:(-row[1],row[0]))[:4]
        total = sum(w for _,w in keep)
        p.skin_weights = [[(b,w/total) for b,w in keep] for _ in p.vertices]
        parts.append(p)
        if len(parts)>=64: break
    return parts


def geometry():
    from .connected_skin import attach
    parts = attach('toad',build_parts(),weights)
    return assemble(parts+surface_warts(parts[0]),weights)


def solve_leg(prefix,target,rotations):
    ids = [IDS[prefix+'_'+j] for j in ('upper','lower','end')]
    hip,knee,foot = [REST[i] for i in ids]
    a,b = math.dist(hip,knee),math.dist(knee,foot)
    direction = unit(sub(target,hip))
    distance = min(a+b-.001,max(abs(a-b)+.001,math.dist(target,hip)))
    along = (a*a-b*b+distance*distance)/(2*distance)
    pole = sub(knee,hip)
    bend = unit(sub(pole,mul(direction,sum(x*y for x,y in zip(pole,direction)))))
    newknee = add(hip,add(mul(direction,along),mul(bend,math.sqrt(max(0,a*a-along*along)))))
    upper = between(sub(knee,hip),sub(newknee,hip))
    lower = between(sub(foot,knee),sub(target,newknee))
    rotations[ids[0]] = upper
    rotations[ids[1]] = qmul(inverse(upper),lower)
    rotations[ids[2]] = inverse(lower)


def pose(name,t):
    rotations = [(0,0,0,1) for _ in BONES]
    shifts = [(0,0,0) for _ in BONES]
    phase = math.tau*t
    pulse = math.sin(math.pi*t)**2
    def turn(bone,direction,degrees):
        rotations[IDS[bone]] = axis(direction,math.radians(degrees))
    if name=='idle':
        shifts[IDS['throat']] = (.16*math.sin(phase),0,-.45*math.sin(phase))
        turn('head',(0,1,0),.6*math.sin(phase))
    elif name=='crawl':
        # Alternating diagonal pairs keep support on the ground; no gameplay hop.
        for limb,offset in (('fore',0),('hind',math.pi)):
            for side,extra in (('L',0),('R',math.pi)):
                p = phase+offset+extra
                foot = REST[IDS[f'{limb}_{side}_end']]
                solve_leg(f'{limb}_{side}',add(foot,(-2.6*math.cos(p),0,1.65*max(0,math.sin(p)))),rotations)
        turn('head',(0,1,0),1.6*math.sin(phase*2))
    elif name in ('slime','slam'):
        turn('head',(0,1,0),(-9 if name=='slime' else 12)*pulse)
        shifts[IDS['throat']] = (1.0*pulse,0,-.85*pulse)
        shifts[IDS['spine']] = ((1.9 if name=='slime' else 3.0)*pulse,0,0)
        if name=='slam': turn('spine',(0,0,1),8*math.sin(phase)*pulse)
    elif name=='recoil':
        turn('head',(0,1,0),-12*pulse)
        shifts[IDS['spine']] = (-1.5*pulse,0,-.5*pulse)
    elif name=='death':
        settled = min(1,t/.85)
        settled = settled*settled*(3-2*settled)
        shifts[IDS['pelvis']] = (0,0,-4*settled)
        shifts[IDS['spine']] = (0,0,-1*settled)
        shifts[IDS['head']] = (1.2*settled,0,-1.5*settled)
        turn('head',(0,1,0),8*settled)
        for side,sign in (('L',1),('R',-1)):
            for limb in ('fore','hind'):
                # Compensate the lowered parent so the splayed feet stay on
                # the floor while the belly settles between them.
                foot=REST[IDS[f'{limb}_{side}_end']]
                drop=5 if limb=='fore' else 4
                solve_leg(f'{limb}_{side}',add(foot,(-1*settled,sign*2*settled,drop*settled)),rotations)
    else:
        raise ValueError('Unknown toad clip: '+name)
    return [(*add(local,shifts[i]),*rotations[i],1,1,1) for i,(_,_,local) in enumerate(BONES)]


def matrices(frame): return RIG.matrices(frame)
def deform(v,w,frame): return RIG.deform(v,w,frame)
def animation_data(v,w): return sample_clips(RIG,CLIPS,pose,v,w)


def build():
    skin = materials.texture_bytes()
    (ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    supplemental = {}
    for name,data in materials.surface_maps().items():
        (ROOT/'mod/BrogueDoom'/name).write_bytes(data)
        supplemental[name]=hashlib.sha256(data).hexdigest()
    parts,v,n,uv,t,w = geometry()
    clips,bounds = animation_data(v,w)
    data = iqm.encode(v,n,uv,t,w,BONES,clips,bounds,
                      mesh_label='Project_Broom_toad',material_path=SKIN)
    model = ROOT/'mod/BrogueDoom/models/monsters/13_toad.iqm'
    model.write_bytes(data)
    manifest = dict(schemaVersion=1,workId='BRG-M13',format='IQM v2',
        runtimeModel=model.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(data).hexdigest(),
        skin=SKIN,skinSha256=hashlib.sha256(skin).hexdigest(),surfaceMapSha256=supplemental,
        dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],
        parts=len(parts),vertices=len(v),triangles=len(t),boneCount=len(BONES),
        bones=[dict(name=n,parent=p,local=v) for n,p,v in BONES],
        clips=[{k:v for k,v in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],
        poseBounds=bounds,authoringSource='assets/monsters/toad/toad-animated.blend')
    out = ROOT/'assets/monsters/toad'; out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__': print(json.dumps(build(),indent=2))

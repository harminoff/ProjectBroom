"""Original sigil-covered goblin; no invented blades, spell timing or gameplay.

The shared anatomical blockout is refined locally through Higgsfield Blender.
Sigils duplicate the actual baked skin triangles/weights, not floating rings.
"""
import copy
import hashlib
import json
import math
import struct
import zlib
from . import goblin_animation as goblin, goblin_materials as materials, iqm
from .rat import ROOT, Part, add, sub, mul
from .skeletal import Rig, axis, assemble, sample_clips

SKIN = 'graphics/BRGCONJ.png'
RIG = Rig.from_world(goblin.SPECS[:-1])  # no weapon or unused spear bone
BONES, REST = RIG.bones, RIG.rest
IDS = {name:i for i,(name,parent,local) in enumerate(BONES)}
CLIPS = [('idle',40,20,True),('walk',20,35,True),('thump',18,35,False),
         ('whack',20,35,False),('recoil',10,35,False),('death',26,35,False)]
GLYPH_RECT = (264,690,504,1015)


def build_parts():
    parts = [p for p in goblin.build_parts() if not p.name.startswith(('spear','hand_R'))]
    # The right wrist is higher in the inherited rest pose. Mirror the open
    # left hand into it rather than retain fingers curled around a missing shaft.
    for source in list(parts):
        if source.name.startswith('hand_L'):
            p = copy.deepcopy(source); p.name = p.name.replace('hand_L','hand_R')
            p.vertices = [(x,-y,z+3) for x,y,z in p.vertices]
            p.faces = [tuple(reversed(f)) for f in p.faces]
            parts.append(p)
    return parts


def weights(part, vertex, uv):
    return goblin.weights(part, vertex, uv)


def sigils(body):
    """Skin-conforming alpha-cutout tattoos in six independently mapped patches.

    Every overlay vertex inherits the exact underlying skin vertex weights.
    A 0.035-unit normal offset prevents z fighting, including on bent limbs.
    Empty atlas borders hide the patch outlines; no collision or light actors.
    """
    normals = body.normals()
    # name, projection axes, center, half size, outward normal, predicate
    regions = [
        ('chest',(1,2),(0,26.4),(3.3,3.5),(1,0,0),lambda v:v[0]>0),
        ('forehead',(1,2),(0,37.2),(1.7,1.3),(1,0,0),lambda v:v[0]>2.5),
        ('back',(1,2),(0,26.2),(3.4,3.6),(-1,0,0),lambda v:v[0]<-2),
        ('arm_L',(1,2),(7.7,24),(2.2,3.4),(1,0,0),lambda v:v[0]>1),
        ('arm_R',(1,2),(-7.7,24),(2.2,3.4),(1,0,0),lambda v:v[0]>1),
        ('nape',(1,2),(0,32),(2,2),(-1,0,0),lambda v:v[0]<1),
    ]
    result=[];x0,y0,x1,y1=GLYPH_RECT
    for name,axes,center,half,direction,predicate in regions:
        p=Part('sigil_'+name);p.skin_weights=[];indices={}
        for face in body.triangles():
            vertices=[body.vertices[i] for i in face]
            centroid=tuple(sum(v[a] for v in vertices)/3 for a in range(3))
            if not predicate(centroid):continue
            if sum(normals[face[0]][a]*direction[a] for a in range(3))<.25:continue
            # Include surrounding triangles, with UVs clamped into transparent
            # padding. Do not jump to adjacent atlas regions at patch boundaries.
            if any(abs(centroid[a]-c)>h*1.25 for a,c,h in zip(axes,center,half)):continue
            tri=[]
            for i in face:
                if i not in indices:
                    indices[i]=len(p.vertices)
                    v=body.vertices[i];p.vertices.append(add(v,mul(normals[i],.035)))
                    u,t=[max(0,min(1,.5+(v[a]-c)/(2*h))) for a,c,h in zip(axes,center,half)]
                    p.uv.append(((x0+u*(x1-x0))/1024,1-(y0+(1-t)*(y1-y0))/1024))
                    p.skin_weights.append(body.skin_weights[i])
                tri.append(indices[i])
            p.faces.append(tuple(tri))
        if not p.faces:raise ValueError('Missing anatomical sigil patch: '+name)
        result.append(p)
    return result


def geometry():
    from .connected_skin import attach
    parts=attach('goblin_conjurer',build_parts(),weights)
    return assemble(parts+sigils(parts[0]),weights)


def pose(name,t):
    frame=[list(row) for row in goblin.pose(name if name in ('idle','walk','recoil','death') else 'idle',t)[:-1]]
    def turn(bone,degrees):
        frame[IDS[bone]][3:7]=axis((0,1,0),math.radians(degrees))
    phase=math.tau*t
    if name!='death':
        # Attentive free hands; this ambient pose does not assert a spell cast.
        for side,offset in (('L',0),('R',1.1)):
            turn('arm_'+side+'_upper',-18+3*math.sin(phase+offset))
            turn('arm_'+side+'_lower',-25+3*math.sin(phase+offset))
            turn('arm_'+side+'_end',12)
        if name=='walk':
            for side,sign in (('L',1),('R',-1)):
                turn('arm_'+side+'_upper',-15+sign*8*math.cos(phase))
        elif name in ('thump','whack'):
            strike=math.sin(math.pi*t)**2
            side='R' if name=='thump' else 'L'
            turn('arm_'+side+'_upper',-18-45*strike)
            turn('arm_'+side+'_lower',-25+24*strike)
            turn('spine',8*strike);turn('jaw',7*strike)
    return [tuple(row) for row in frame]


def matrices(frame):return RIG.matrices(frame)
def deform(v,w,frame):return RIG.deform(v,w,frame)
def animation_data(v,w):return sample_clips(RIG,CLIPS,pose,v,w)


def glyph_distance(u,v):
    # Original angular mark: broken diamond, central stroke, two short branches.
    # Not an imported font, religious symbol or claimed Brogue alphabet.
    segments=[((.5,.17),(.23,.43)),((.23,.43),(.5,.7)),
              ((.5,.7),(.77,.43)),((.77,.43),(.61,.28)),
              ((.5,.32),(.5,.85)),((.5,.78),(.32,.89)),
              ((.5,.78),(.68,.89)),((.31,.17),(.39,.24))]
    distances=[]
    for (x,y),(X,Y) in segments:
        dx,dy=X-x,Y-y;t=max(0,min(1,((u-x)*dx+(v-y)*dy)/(dx*dx+dy*dy)))
        distances.append(math.hypot(u-x-t*dx,v-y-t*dy))
    return min(distances)


def texture_bytes():
    size=1024; pixels=bytearray(size*size*4)
    for name,(x0,y0,x1,y1) in materials.RECTS.items():
        for y in range(y0-8,y1+8):
            for x in range(x0-8,x1+8):
                u=max(0,min(1,(x-x0)/(x1-x0)));v=max(0,min(1,(y-y0)/(y1-y0)))
                rgb=materials.shade(name,u,v)
                # Subtle ash-brown family variation, not whole-body violet.
                if name in ('fur','face','hand','mane'):rgb=(rgb[0]*.92,rgb[1]*.93,rgb[2]*1.03)
                pixels[(y*size+x)*4:(y*size+x)*4+4]=bytes([*(max(0,min(255,round(c))) for c in rgb),255])
    x0,y0,x1,y1=GLYPH_RECT
    for y in range(682,1024):
        for x in range(256,512):
            d=glyph_distance((x-x0)/(x1-x0),(y-y0)/(y1-y0))
            core=max(0,1-d/.032)
            pixels[(y*size+x)*4:(y*size+x)*4+4]=bytes((round(161+73*core),round(56+112*core),255,255 if d<.027 else 0))
    def chunk(k,d):return struct.pack('>I',len(d))+k+d+struct.pack('>I',zlib.crc32(k+d)&0xffffffff)
    raw=b''.join(b'\0'+pixels[y*size*4:(y+1)*size*4] for y in range(size))
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',size,size,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b'')


def build():
    skin=texture_bytes();(ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts,v,n,uv,t,w=geometry();clips,bounds=animation_data(v,w)
    data=iqm.encode(v,n,uv,t,w,BONES,clips,bounds,mesh_label='Project_Broom_goblin_conjurer',material_path=SKIN)
    path=ROOT/'mod/BrogueDoom/models/monsters/09_goblin_conjurer.iqm';path.write_bytes(data)
    manifest=dict(schemaVersion=1,workId='BRG-M09',format='IQM v2',runtimeModel=path.relative_to(ROOT).as_posix(),
        sha256=hashlib.sha256(data).hexdigest(),skin=SKIN,skinSha256=hashlib.sha256(skin).hexdigest(),
        dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],
        parts=len(parts),vertices=len(v),triangles=len(t),boneCount=len(BONES),
        bones=[dict(name=n,parent=p,local=v) for n,p,v in BONES],
        clips=[{k:v for k,v in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],
        poseBounds=bounds,authoringSource='assets/monsters/goblin_conjurer/goblin-conjurer-animated.blend')
    out=ROOT/'assets/monsters/goblin_conjurer';out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__':print(build()['sha256'])

"""Original unarmed golden-eyed goblin mystic; cosmetic presentation only.

Connected primate family anatomy is reused without conjurer markings or blades.
Open-hand gestures do not claim a synchronized shielding event.
"""
import copy
import hashlib
import json
import math
import struct
import zlib
from . import goblin_animation as goblin, goblin_materials as materials, iqm
from .rat import ROOT
from .skeletal import Rig, axis, assemble, sample_clips

SKIN = 'graphics/BRGMYST.png'
RIG = Rig.from_world(goblin.SPECS[:-1])  # no weapon or unused spear bone
BONES, REST = RIG.bones, RIG.rest
IDS = {name:i for i,(name,parent,local) in enumerate(BONES)}
CLIPS = [('idle',40,20,True),('walk',20,35,True),('palm',18,35,False),
         ('sweep',20,35,False),('recoil',10,35,False),('death',26,35,False)]


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
    # Slightly fuller irises keep the source signature readable at game scale.
    for p in parts:
        if p.name.startswith('head_eye_iris'):
            sign=1 if p.name.endswith('_1') else -1
            p.vertices=[(x,sign*1.65+(y-sign*1.65)*1.25,35.56+(z-35.56)*1.10) for x,y,z in p.vertices]
    return parts


def weights(part, vertex, uv):
    return goblin.weights(part, vertex, uv)


def geometry():
    from .connected_skin import attach
    parts=attach('goblin_mystic',build_parts(),weights)
    return assemble(parts,weights)


def pose(name,t):
    frame=[list(row) for row in goblin.pose(name if name in ('idle','walk','recoil','death') else 'idle',t)[:-1]]
    def turn(bone,degrees):
        frame[IDS[bone]][3:7]=axis((0,1,0),math.radians(degrees))
    phase=math.tau*t
    if name!='death':
        # Attentive free hands; this ambient pose does not assert a spell cast.
        for side,offset in (('L',0),('R',1.1)):
            turn('arm_'+side+'_upper',-38+2*math.sin(phase+offset))
            turn('arm_'+side+'_lower',-37+3*math.sin(phase+offset))
            turn('arm_'+side+'_end',48)
        if name=='walk':
            for side,sign in (('L',1),('R',-1)):
                turn('arm_'+side+'_upper',-15+sign*8*math.cos(phase))
        elif name in ('palm','sweep'):
            strike=math.sin(math.pi*t)**2
            side='R' if name=='palm' else 'L'
            turn('arm_'+side+'_upper',-38-30*strike)
            turn('arm_'+side+'_lower',-37+32*strike)
            turn('spine',8*strike);turn('jaw',7*strike)
    return [tuple(row) for row in frame]


def matrices(frame):return RIG.matrices(frame)
def deform(v,w,frame):return RIG.deform(v,w,frame)
def animation_data(v,w):return sample_clips(RIG,CLIPS,pose,v,w)


def texture_bytes():
    size=1024; pixels=bytearray(size*size*3)
    for name,(x0,y0,x1,y1) in materials.RECTS.items():
        for y in range(y0-8,y1+8):
            for x in range(x0-8,x1+8):
                u=max(0,min(1,(x-x0)/(x1-x0)));v=max(0,min(1,(y-y0)/(y1-y0)))
                rgb=materials.shade(name,u,v)
                if name in ('fur','face','hand'):
                    rgb=(rgb[0]*1.06,rgb[1]*1.04,rgb[2]*1.03)
                elif name=='mane':rgb=(rgb[0]*1.25,rgb[1]*1.23,rgb[2]*1.2)
                elif name=='hide':rgb=(rgb[0]*.65,rgb[1]*1.25,rgb[2]*2.35)
                elif name=='cord':
                    # Used only by the irises: warm gold with a pale sparkle.
                    spot=math.exp(-((u-.30)/.11)**2-((v-.28)/.11)**2)
                    rgb=(244+11*spot,170+75*spot,30+160*spot)
                pixels[(y*size+x)*3:(y*size+x)*3+3]=bytes(max(0,min(255,round(c))) for c in rgb)
    def chunk(k,d):return struct.pack('>I',len(d))+k+d+struct.pack('>I',zlib.crc32(k+d)&0xffffffff)
    raw=b''.join(b'\0'+pixels[y*size*3:(y+1)*size*3] for y in range(size))
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',size,size,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b'')


def build():
    skin=texture_bytes();(ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts,v,n,uv,t,w=geometry();clips,bounds=animation_data(v,w)
    data=iqm.encode(v,n,uv,t,w,BONES,clips,bounds,mesh_label='Project_Broom_goblin_mystic',material_path=SKIN)
    path=ROOT/'mod/BrogueDoom/models/monsters/10_goblin_mystic.iqm';path.write_bytes(data)
    manifest=dict(schemaVersion=1,workId='BRG-M10',format='IQM v2',runtimeModel=path.relative_to(ROOT).as_posix(),
        sha256=hashlib.sha256(data).hexdigest(),skin=SKIN,skinSha256=hashlib.sha256(skin).hexdigest(),
        dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],
        parts=len(parts),vertices=len(v),triangles=len(t),boneCount=len(BONES),
        bones=[dict(name=n,parent=p,local=v) for n,p,v in BONES],
        clips=[{k:v for k,v in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],
        poseBounds=bounds,authoringSource='assets/monsters/goblin_mystic/goblin-mystic-animated.blend')
    out=ROOT/'assets/monsters/goblin_mystic';out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__':print(build()['sha256'])

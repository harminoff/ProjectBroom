"""Original orange bloat subspecies. Cosmetic membrane; Brogue owns explosion."""
import hashlib
import json
import math
import struct
import zlib
from . import bloat_animation as bloat, iqm
from .rat import ROOT, add, sub
from .skeletal import axis, sample_clips

BONES, REST, CLIPS, RIG = bloat.BONES, bloat.REST, bloat.CLIPS, bloat.RIG
geometry, weights = bloat.geometry, bloat.weights
matrices, deform = bloat.matrices, bloat.deform
SKIN = 'graphics/BRGEXBL.png'


def pose(name, t):
    if name != 'collapse':
        return bloat.pose(name, t)
    # Brief taut expansion gives way to a low, uneven spent membrane. Unit
    # bone scales preserve the shared runtime/Blender deformation contract.
    settle = max(0, min(1, (t-.12)/.64))
    settle = settle*settle*(3-2*settle)
    pressure = math.sin(math.pi*min(1, t/.24))**2 * (1-settle)
    frame = []
    for i, (_, _, local) in enumerate(BONES):
        if i == 0:
            shift = (0, 0, -24*settle)
            rotation = axis((0, 0, 1), math.radians(19*settle))
        else:
            d = bloat.DIRECTIONS[i-1]
            shift = tuple(d[a]*(1.7*pressure-(7 if a<2 else 13.8)*settle) for a in range(3))
            # The crown folds off-center; no disconnected fragments or effects.
            if i == 5: shift = add(shift, (2.2*settle, -1.3*settle, 0))
            rotation = (0, 0, 0, 1)
        frame.append((*add(local, shift), *rotation, 1, 1, 1))
    return frame


def animation_data(vertices, influences):
    return sample_clips(RIG, CLIPS, pose, vertices, influences)


def texture_bytes():
    size=512; pixels=bytearray()
    for y in range(size):
        pixels.append(0)
        v=max(0,min(1,(1-y/(size-1)-.02)/.96))
        cap=math.sin(math.pi*v)**.65
        for x in range(size):
            theta=math.tau*x/(size-1)
            # Periodic longitude keeps the one-piece membrane seam continuous.
            mottling=6*math.sin(theta*9+v*23)*math.sin(theta*4-v*37)
            mottling+=3*math.sin(theta*23+v*91)
            trunk=abs(math.sin(theta*6+.55*math.sin(v*19)+.20*math.sin(theta*3+v*27)))
            branch=abs(math.sin(theta*13+v*29+.65*math.sin(theta*5-v*13)))
            vein=max(math.exp(-(trunk/.045)**2),.55*math.exp(-(branch/.035)**2))*cap
            halo=max(math.exp(-(trunk/.13)**2),.25*math.exp(-(branch/.10)**2))*cap
            taut=(.5+.5*math.cos(theta*5+.35*math.sin(v*17)))**8*cap
            light=11*math.sin(math.pi*v)+4*math.cos(theta*2)
            base=(205+light+mottling+12*taut,111+light+mottling+22*taut,30+light*.7+mottling+16*taut)
            color=[c-halo*10-vein*dark for c,dark in zip(base,(68,57,21))]
            pixels.extend(max(0,min(255,round(c))) for c in color)
    def chunk(k,d):return struct.pack('>I',len(d))+k+d+struct.pack('>I',zlib.crc32(k+d)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',size,size,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(bytes(pixels),9))+chunk(b'IEND',b'')


def build():
    skin=texture_bytes(); (ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts,v,n,uv,t,w=geometry(); clips,bounds=animation_data(v,w)
    data=iqm.encode(v,n,uv,t,w,BONES,clips,bounds,mesh_label='Project_Broom_explosive_bloat',material_path=SKIN)
    path=ROOT/'mod/BrogueDoom/models/monsters/30_explosive_bloat.iqm';path.write_bytes(data)
    manifest=dict(schemaVersion=1,workId='BRG-M30',format='IQM v2',
        runtimeModel=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(data).hexdigest(),
        skin=SKIN,skinSha256=hashlib.sha256(skin).hexdigest(),
        dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],
        parts=len(parts),vertices=len(v),triangles=len(t),boneCount=len(BONES),
        bones=[dict(name=n,parent=p,local=v) for n,p,v in BONES],
        clips=[{k:v for k,v in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],
        poseBounds=bounds,authoringSource='assets/monsters/explosive_bloat/explosive-bloat-animated.blend')
    out=ROOT/'assets/monsters/explosive_bloat';out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__': print(build()['sha256'])

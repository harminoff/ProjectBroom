"""Original blue pit-bloat subspecies; shared membrane rig, no terrain authority."""
import hashlib
import io
import json
import struct
import zlib
from . import bloat_animation as bloat, iqm
from .rat import ROOT, add, sub

BONES, REST, CLIPS = bloat.BONES, bloat.REST, bloat.CLIPS
RIG = bloat.RIG
geometry, weights, pose = bloat.geometry, bloat.weights, bloat.pose
matrices, deform, animation_data = bloat.matrices, bloat.deform, bloat.animation_data
SKIN = 'graphics/BRGPITBL.png'


def texture_bytes():
    from PIL import Image
    # Preserve familial veins and membrane, but use the pinned blue identity cue.
    # Diffuse only: no translucency or emission that could defeat visibility.
    source = Image.open(io.BytesIO(bloat.texture_bytes())).convert('RGB')
    raw = bytearray()
    for y in range(source.height):
        raw.append(0)
        for x in range(source.width):
            r, g, b = source.getpixel((x, y))
            raw.extend((max(0, r-72), min(255, g+17), min(255, b+51)))
    def chunk(kind, data):
        return struct.pack('>I', len(data))+kind+data+struct.pack('>I', zlib.crc32(kind+data)&0xffffffff)
    return (b'\x89PNG\r\n\x1a\n'
            +chunk(b'IHDR', struct.pack('>IIBBBBB', source.width, source.height, 8, 2, 0, 0, 0))
            +chunk(b'IDAT', zlib.compress(bytes(raw), 9))+chunk(b'IEND', b''))


def build():
    skin = texture_bytes()
    (ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts, vertices, normals, uv, triangles, influences = geometry()
    clips, bounds = animation_data(vertices, influences)
    data = iqm.encode(vertices, normals, uv, triangles, influences, BONES, clips, bounds,
                      mesh_label='Project_Broom_pit_bloat', material_path=SKIN)
    path = ROOT/'mod/BrogueDoom/models/monsters/07_pit_bloat.iqm'
    path.write_bytes(data)
    manifest = dict(schemaVersion=1, workId='BRG-M07', format='IQM v2',
        runtimeModel=path.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(data).hexdigest(),
        skin=SKIN, skinSha256=hashlib.sha256(skin).hexdigest(),
        dimensions=[round(max(v[a] for v in vertices)-min(v[a] for v in vertices),4) for a in range(3)],
        parts=len(parts), vertices=len(vertices), triangles=len(triangles), boneCount=len(BONES),
        bones=[dict(name=n,parent=p,local=v) for n,p,v in BONES],
        clips=[{k:v for k,v in c.items() if k!='frames'}|dict(frameCount=len(c['frames'])) for c in clips],
        poseBounds=bounds, authoringSource='assets/monsters/pit_bloat/pit-bloat-animated.blend')
    out=ROOT/'assets/monsters/pit_bloat';out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__':
    print(build()['sha256'])

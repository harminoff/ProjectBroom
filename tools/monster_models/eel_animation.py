"""Original continuous eel, authored/reviewed through Blender MCP. Cosmetic only."""
import hashlib
import json
import math
import struct
import zlib
from . import iqm
from .rat import ROOT, Part, add, sub, ellipsoid
from .skeletal import Rig, axis, assemble, sample_clips

SKIN = 'graphics/BRGEEL.png'
SPECS = [('root', None, (0, 0, 0)), ('head', 'root', (20, 0, 7))]
parent = 'head'
for i in range(10):
    name = f'spine_{i}'
    SPECS.append((name, parent, (16 - i * 5, 0, 7)))
    parent = name
SPECS.append(('jaw', 'head', (20, 0, 5.8)))
RIG = Rig.from_world(SPECS)
BONES, REST = RIG.bones, RIG.rest
IDS = {n: i for i, (n, p, v) in enumerate(BONES)}
CHAIN = [IDS['head']] + [IDS[f'spine_{i}'] for i in range(10)]
CLIPS = [('idle', 40, 20, True), ('swim', 24, 35, True),
         ('bite', 18, 35, False), ('strike', 20, 35, False),
         ('recoil', 12, 35, False), ('death', 28, 35, False)]


def uv(u, v):
    return (.02 + .96 * u, .98 - .70 * v)


def geometry():
    # Shared rings form one closed anatomical skin, including the fin ridge.
    # +X faces forward. The broad flank catches ambient light under water.
    body = Part('eel_connected_body')
    rings, sides = 65, 32
    for i in range(rings):
        t = i / (rings - 1)
        x = -29 + 54 * t
        taper = min(1.0, (1.025 - t) / .12) ** .55
        width = (.06 + 3.65 * math.sin(t * math.pi / 2) ** 1.1) * taper
        height = (.08 + 2.8 * math.sin(t * math.pi / 2) ** .85) * taper
        for j in range(sides + 1):
            a = math.tau * j / sides
            fin = max(0, 1 - abs(math.cos(a)) * 8) ** 2
            fin *= math.sin(math.pi * t) ** .7 * (1.5 if math.sin(a) > 0 else .7)
            body.vertices.append((x, math.cos(a) * width,
                                  7 + math.sin(a) * (height + fin)))
            body.uv.append(uv(t, j / sides))
    for i in range(rings - 1):
        for j in range(sides):
            a = i * (sides + 1) + j
            body.faces.append((a, a + 1, a + sides + 2, a + sides + 1))
    for end, reverse in ((0, True), (rings - 1, False)):
        center = len(body.vertices)
        body.vertices.append((-29 + 54 * end / (rings - 1), 0, 7))
        body.uv.append(uv(end / (rings - 1), .5))
        for j in range(sides):
            a = end * (sides + 1) + j
            body.faces.append((center, a + 1, a) if reverse else (center, a, a + 1))
    parts = [body]
    def oval(name, center, radius, color):
        p = ellipsoid(name, center, radius, segments=16, rings=10)
        p.uv = [(color, .12)] * len(p.vertices)
        parts.append(p)
    oval('jaw_lower', (22.3, 0, 5.85), (3.5, 1.85, .65), .55)
    oval('head_mouth', (23, 0, 6.6), (2.5, 1.9, .17), .15)
    for sign in (-1, 1):
        oval(f'head_eye_{sign}', (21, sign * 2.55, 8.1), (.55, .26, .43), .75)
        oval(f'head_pupil_{sign}', (21.15, sign * 2.78, 8.1), (.25, .10, .30), .15)
        oval(f'head_gill_{sign}', (17.3, sign * 3.36, 7.2), (.18, .12, 1.2), .15)
    return assemble(parts, weights)


def weights(part, v, u):
    if part.name.startswith('jaw'):
        return [(IDS['jaw'], 1)]
    if part.name.startswith('head'):
        return [(IDS['head'], 1)]
    return RIG.chain_weights(v, CHAIN)


def pose(name, t):
    rot = [(0, 0, 0, 1) for _ in BONES]
    shift = [0, 0, 0]
    for i in range(10):
        if name in ('idle', 'swim'):
            amplitude = (1.4 if name == 'idle' else 4.5) * (.5 + i / 10)
            angle = amplitude * math.sin(math.tau * t - i * .60)
        else:
            pulse = math.sin(math.pi * t) ** 2
            angle = (9 if name == 'strike' else 5) * math.sin(i * .65) * pulse
            if name == 'death':
                angle = 4 * math.sin(i * .7) * min(1, t * 2)
        rot[IDS[f'spine_{i}']] = axis((0, 0, 1), math.radians(angle))
    if name in ('bite', 'strike'):
        pulse = math.sin(math.pi * t) ** 2
        shift[0] = (3 if name == 'bite' else 4) * pulse
        rot[IDS['jaw']] = axis((0, 1, 0), math.radians(25 * pulse))
    elif name == 'recoil':
        shift[0] = -2 * math.sin(math.pi * t) ** 2
    elif name == 'death':
        settle = min(1, t / .8)
        settle = settle * settle * (3 - 2 * settle)
        rot[IDS['head']] = axis((1, 0, 0), math.radians(75 * settle))
    return [(*add(local, shift if i == 0 else (0, 0, 0)), *rot[i], 1, 1, 1)
            for i, (n, p, local) in enumerate(BONES)]


def matrices(frame): return RIG.matrices(frame)
def deform(vertices, influences, frame): return RIG.deform(vertices, influences, frame)
def animation_data(v, w): return sample_clips(RIG, CLIPS, pose, v, w)


def texture_bytes():
    size = 512
    pixels = bytearray()
    for y in range(size):
        pixels.append(0)
        for x in range(size):
            u, v = x / size, (y / size - .02) / .70
            if y > size * .76:
                base = (24, 17, 15) if u < .3 else (155, 117, 83) if u < .65 else (171, 127, 54)
                detail = 0
            else:
                dorsal = max(0, math.sin(v * math.tau))
                belly = max(0, -math.sin(v * math.tau))
                base = (124 - 45*dorsal + 42*belly, 69 - 29*dorsal + 51*belly, 48 - 17*dorsal + 43*belly)
                detail = 3*math.sin(u*170 + 2*math.sin(v*80))*math.sin(v*150)
                detail += 5*math.sin(u*29)*math.sin(v*47)
                # Long flank highlight is diffuse paint, never fullbright.
                detail += 15*math.exp(-((v-.48)/.07)**2)
            pixels.extend(max(0, min(255, round(c + detail))) for c in base)
    def chunk(k, d):
        return struct.pack('>I', len(d)) + k + d + struct.pack('>I', zlib.crc32(k+d)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(bytes(pixels), 9)) + chunk(b'IEND', b'')


def build():
    skin = texture_bytes()
    (ROOT / 'mod/BrogueDoom' / SKIN).write_bytes(skin)
    parts, v, n, uv, t, w = geometry()
    clips, bounds = animation_data(v, w)
    data = iqm.encode(v, n, uv, t, w, BONES, clips, bounds,
                      mesh_label='Project_Broom_eel', material_path=SKIN)
    path = ROOT / 'mod/BrogueDoom/models/monsters/04_eel.iqm'
    path.write_bytes(data)
    manifest = dict(schemaVersion=1, workId='BRG-M04', format='IQM v2',
        runtimeModel=path.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(data).hexdigest(),
        skin=SKIN, skinSha256=hashlib.sha256(skin).hexdigest(),
        dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v),4) for a in range(3)],
        parts=len(parts), vertices=len(v), triangles=len(t), boneCount=len(BONES),
        bones=[dict(name=n,parent=p,local=v) for n,p,v in BONES],
        clips=[{k:v for k,v in c.items() if k!='frames'} | dict(frameCount=len(c['frames'])) for c in clips],
        poseBounds=bounds, authoringSource='assets/monsters/eel/eel-animated.blend')
    out = ROOT / 'assets/monsters/eel'
    out.mkdir(exist_ok=True)
    (out / 'animation.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    print(json.dumps(build(), indent=2))

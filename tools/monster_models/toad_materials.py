"""Original padded olive/buff toad atlas; deterministic cosmetic detail only."""
import math
import struct
import zlib
from .rat import TILES

SKIN = 'graphics/BRGTOAD.png'
SIZE = 1024
ROLES = ('skin', 'belly', 'gland', 'iris', 'dark', 'lip')
RECTS = {name: (i % 3 * 340 + 10, i // 3 * 512 + 10,
                i % 3 * 340 + 330, i // 3 * 512 + 502)
         for i, name in enumerate(ROLES)}


def role(name):
    if name.startswith('eye_iris'): return 'iris'
    if name.startswith(('eye_pupil', 'nostril', 'mouth_seam')): return 'dark'
    if name.startswith(('belly', 'throat')): return 'belly'
    if name.startswith(('gland', 'wart')): return 'gland'
    if name.startswith(('mouth', 'toe', 'foot')): return 'lip'
    return 'skin'


def repack(parts):
    for part in parts:
        x0, y0, x1, y1 = RECTS[role(part.name)]
        mapped = []
        for u, v in part.uv:
            x, y = u * SIZE, (1-v) * SIZE
            old = next(r for r in TILES.values()
                       if r[0]-.01 <= x <= r[2]+.01 and r[1]-.01 <= y <= r[3]+.01)
            a, b = (x-old[0])/(old[2]-old[0]), (y-old[1])/(old[3]-old[1])
            mapped.append(((x0+a*(x1-x0))/SIZE, 1-(y0+b*(y1-y0))/SIZE))
        part.uv = mapped
    return parts


def noise(x, y):
    return (((x*1619+y*31337) ^ (x*y*6971)) & 255)/255-.5


def shade(name, u, v):
    grain = noise(int(u*320), int(v*490))
    clouds = math.sin(u*21+2*math.sin(v*13))*math.sin(v*18+math.sin(u*11))
    spots = max(0, math.sin(u*61+math.sin(v*29)*2)*math.sin(v*47+math.sin(u*33))-.24)
    pores = max(0, noise(int(u*123), int(v*183))-.27)*13
    base = dict(skin=(98,112,58), belly=(154,146,98), gland=(115,121,63),
                iris=(182,139,64), dark=(15,21,13), lip=(117,121,70))[name]
    delta = grain*9 + clouds*12 - spots*30 - pores
    if name == 'belly': delta = grain*6 + clouds*5 - spots*12
    if name == 'iris':
        # Variegated copper around a modeled horizontal pupil, never emissive.
        delta = clouds*13 + grain*24
    if name == 'dark': delta = grain*3
    return tuple(max(0, min(255, round(c+delta))) for c in base)


def png(pixels,width=SIZE,height=SIZE):
    def chunk(k,d):
        return struct.pack('>I',len(d))+k+d+struct.pack('>I',zlib.crc32(k+d)&0xffffffff)
    raw=b''.join(b'\0'+pixels[y*width*3:(y+1)*width*3] for y in range(height))
    return (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,2,0,0,0))
            +chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b''))


def texture_bytes():
    pixels = bytearray(SIZE*SIZE*3)
    for name, (x0,y0,x1,y1) in RECTS.items():
        for y in range(y0-10, y1+10):
            for x in range(x0-10, x1+10):
                u = max(0,min(1,(x-x0)/(x1-x0)))
                v = max(0,min(1,(y-y0)/(y1-y0)))
                pixels[(y*SIZE+x)*3:(y*SIZE+x)*3+3] = bytes(shade(name,u,v))
    return png(pixels)


def surface_maps():
    """Native specular material; flat normals retain the actual sculpted relief.

    Wet highlights require existing scene lights. This adds no world light,
    emissive pixels, moving particles or gameplay slime.
    """
    pixels=bytearray(SIZE*SIZE*3)
    for name,(x0,y0,x1,y1) in RECTS.items():
        level=120 if name=='iris' else 78 if name in ('gland','lip') else 48
        for y in range(y0-10,y1+10):
            for x in range(x0-10,x1+10):
                value=round(level+noise(x,y)*10)
                pixels[(y*SIZE+x)*3:(y*SIZE+x)*3+3]=bytes((value,)*3)
    return {'graphics/BRGTOAD_N.png':png(bytes((128,128,255))*16,4,4),
            'graphics/BRGTOAD_S.png':png(pixels)}

"""Original ash-olive skin, dark cavities, stained nails and ragged wrap."""
import math
import struct
import zlib
from .rat import TILES
SIZE=1024
ROLES=('skin','steel','leather','armor','sash','hair','dark','iris')
RECTS={n:(i%4*256+8,i//4*512+8,i%4*256+248,i//4*512+504) for i,n in enumerate(ROLES)}
def role(n):
    if n.startswith('nail'):return 'steel'
    if n.startswith('cloth'):return 'sash'
    if n.startswith('detail_tooth'):return 'iris'
    if n.startswith('detail'):return 'dark'
    return 'skin'

def repack(parts):
    for p in parts:
        rect=RECTS[role(p.name)];mapped=[]
        for u,v in p.uv:
            x,y=u*1024,(1-v)*1024
            r=next(r for r in TILES.values() if r[0]-.01<=x<=r[2]+.01 and r[1]-.01<=y<=r[3]+.01)
            a,b=(x-r[0])/(r[2]-r[0]),(y-r[1])/(r[3]-r[1])
            if p.name.startswith(('arm_','leg_','club_timber')):a,b=b,a
            mapped.append(((rect[0]+a*(rect[2]-rect[0]))/SIZE,1-(rect[1]+b*(rect[3]-rect[1]))/SIZE))
        p.uv=mapped
    return parts
def noise(x,y):return (((x*1619+y*31337)^(x*y*6971))&255)/255-.5
def shade(name,u,v):
    n=noise(int(u*240),int(v*496))
    base={'skin':(157,154,166),'steel':(82,31,25),'leather':(60,44,41),
          'armor':(45,52,65),'sash':(53,48,32),'hair':(31,27,38),
          'dark':(13,14,10),'iris':(160,152,113)}[name]
    delta=n*5
    if name=='steel':delta+=24*abs(2*u-1)+7*math.sin(u*85)
    if name=='armor':delta+=9*math.cos(u*6)+4*math.sin(v*60)
    if name=='sash':delta+=9*math.sin(u*80)+3*math.sin(v*180)
    if name=='hair':delta+=6*math.sin(u*120+v*9)
    return tuple(max(0,min(255,round(c+delta))) for c in base)

def accessory_pixels():
    pixels=bytearray(SIZE*SIZE*3)
    for name,(x0,y0,x1,y1) in RECTS.items():
        for y in range(y0-8,y1+8):
            for x in range(x0-8,x1+8):
                u=max(0,min(1,(x-x0)/(x1-x0)));v=max(0,min(1,(y-y0)/(y1-y0)))
                pixels[(y*SIZE+x)*3:(y*SIZE+x)*3+3]=bytes(shade(name,u,v))
    return pixels

def encode_png(pixels,width,height):
    def chunk(k,d):return struct.pack('>I',len(d))+k+d+struct.pack('>I',zlib.crc32(k+d)&0xffffffff)
    raw=b''.join(b'\0'+pixels[y*width*3:(y+1)*width*3] for y in range(height))
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b'')

def texture_bytes():return encode_png(accessory_pixels(),SIZE,SIZE)

def pigment(point,normal):
    x,y,z=point
    form=.77+.20*max(-.5,normal[0]*.4+normal[1]*-.2+normal[2]*.7)
    subtle=2*math.sin(x*.9+y*.7+z*.6)
    # Continuous anatomical/material coordinates across fused body seams.
    base=(153,148,127)
    # Cold mottling stays continuous across the fused gaunt anatomy.
    subtle+=10*math.sin(z*2.1+y*.7)*math.sin(x*1.3+z*.3)
    crease=10*math.exp(-((z-55.3)/.6)**2-((abs(y)-1.7)/.6)**2)*max(0,min(1,x/4))
    return tuple(c*form+subtle-crease for c in base)

def connected_atlas(parts, pixels=False):
    """Bake continuous rest-position pigment and sculpt shading, never part UVs.

    Per-triangle padded UV islands preserve smooth world-position pigment across
    the fused joints. The original cage/topology/weights are unchanged. Shading
    is painted form definition, not an emitted light or a gameplay effect.
    """
    from .rat import Part
    body=parts[0];normal=body.normals();tris=list(body.triangles())
    assert len(tris)<8192
    if pixels:
        buffer=bytearray(2048*2048*3);accessory=accessory_pixels()
        for y in range(1024):buffer[(y*2048+1024)*3:(y*2048+2048)*3]=accessory[y*3072:(y+1)*3072]
        colors=[pigment(v,n) for v,n in zip(body.vertices,normal)]
    result=Part('Connected_skin');result.skin_weights=[];result.skin_topology=[]
    for index,tri in enumerate(tris):
        x0=(index%64)*16;y0=(index//64)*16
        if pixels:
            color=[colors[i] for i in tri]
            for dy in range(16):
                for dx in range(16):
                    b=(dx-2)/12;c=(dy-2)/12;a=1-b-c
                    offset=((y0+dy)*2048+x0+dx)*3
                    buffer[offset:offset+3]=bytes(max(0,min(255,round(a*color[0][k]+b*color[1][k]+c*color[2][k]))) for k in range(3))
        base=len(result.vertices)
        for i,(dx,dy) in zip(tri,((2,2),(14,2),(2,14))):
            result.vertices.append(body.vertices[i]);result.uv.append(((x0+dx)/2048,1-(y0+dy)/2048))
            result.skin_weights.append(body.skin_weights[i]);result.skin_topology.append(body.skin_topology[i])
        result.faces.append((base,base+1,base+2))
    if pixels:return encode_png(buffer,2048,2048)
    for p in parts[1:]:p.uv=[(.5+u*.5,.5+v*.5) for u,v in p.uv]
    return [result]+parts[1:]

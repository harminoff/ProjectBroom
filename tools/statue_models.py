"""Original carved marble/obsidian statues, deterministic and CC0-1.0.

Source coordinates are Z-up, with the face looking along +X. Intersecting
sculptural masses are intentional stone joins, not articulated body parts.
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance

ROOT = Path(__file__).resolve().parents[1]


def rings(v, f, levels, sides=32, flutes=0):
    start = len(v)+1
    for x,y,z,rx,ry in levels:
        for i in range(sides):
            a = 2*math.pi*i/sides
            flute = 1 + flutes*math.cos(a*8)
            v.append((x+rx*math.cos(a)*flute,y+ry*math.sin(a)*flute,z))
    for j in range(len(levels)-1):
        for i in range(sides):
            n = (i+1)%sides; b = start+j*sides
            f.append((b+i,b+n,b+sides+n,b+sides+i))
    b = start+(len(levels)-1)*sides
    # UZDoom's OBJ loader accepts triangles/quads only, not Blender-style ngons.
    bottom=len(v)+1; v.append(tuple(levels[0][:3]))
    top=len(v)+1; v.append(tuple(levels[-1][:3]))
    for i in range(sides):
        n=(i+1)%sides
        f.append((bottom,start+n,start+i))
        f.append((top,b+i,b+n))


def ellipsoid(v,f,x,y,z,rx,ry,rz):
    # Small capped poles avoid degenerate faces in exported meshes.
    rings(v,f,[(x,y,z+rz*math.sin(a),rx*math.cos(a),ry*math.cos(a))
              for a in [-1.54+i*3.08/12 for i in range(13)]],24)


def sculpture(kind):
    v,f=[],[]
    rings(v,f,[(0,0,0,18,18),(0,0,3,18,18),(0,0,4,16,16),
               (0,0,7,16,16),(0,0,8,14,14)],8)
    broken = kind == 'broken'
    # A continuous fluted robe anchors the figure to its plinth.
    levels=[(0,0,7.5,12,13),(0,0,12,11.5,12),(0,0,25,9,10),
            (0,0,38,7,8),(0,0,47,7.5,11),(0,0,54,7,12),(0,0,58,5,8)]
    if broken: levels=levels[:3]+[(1,0,33,7,8)]
    rings(v,f,levels,48,.08)
    if broken:
        # Deliberately jagged fracture surface and recognisable fallen head.
        for x,y,z in [(3,5,33),(-4,-2,32),(1,-6,33)]:
            ellipsoid(v,f,x,y,z,4,3,2)
        ellipsoid(v,f,11,-7,12,6,5,4)
        return v,f
    ellipsoid(v,f,-1,0,62,6,7,9) # hood, overlapping neck and shoulders
    ellipsoid(v,f,3,0,64,4.8,5,6.5) # face
    ellipsoid(v,f,7.3,0,63,1.7,1.1,2.4) # carved nose
    for y in (-2.3,2.3):
        ellipsoid(v,f,7.1,y,66,1,1.7,.6) # brow ridges
        # Sleeves connect well inside shoulder mass; hands join the sleeves.
        ellipsoid(v,f,1,y*4,48,6,4,10)
        ellipsoid(v,f,6,y*2.5,45,3.5,6,3.5)
        ellipsoid(v,f,8,y*.65,46,2.3,2.4,3)
    # Deep hood rim, collar and rope belt are stone carvings.
    rings(v,f,[(0,0,37,7.8,8.8),(0,0,39,7.8,8.8)],48)
    if kind == 'demon':
        for sign in (-1,1):
            rings(v,f,[(-1,sign*5,68,2.8,2.8),(-2,sign*7,73,2.1,2),
                       (0,sign*8,78,1.2,1.2),(3,sign*7,81,.15,.15)],16)
        ellipsoid(v,f,7,0,60,2,3,2) # broad leering jaw
    return v,f


def generate():
    out=ROOT/'mod/BrogueDoom/models/terrain'; out.mkdir(parents=True,exist_ok=True)
    models={}
    for name in ('marble','cracked','broken','demon'):
        models['Statue'+name.title()] = ('statue_'+name, 'BRGST'+{'marble':'MAR','cracked':'CRK','broken':'BRK','demon':'OBS'}[name])
    for name in ('MAR','CRK','OBS'):
        pixels=[]
        for y in range(256):
            for x in range(256):
                vein=abs(math.sin(x*.058+y*.039+1.8*math.sin(y*.021)+.35*math.sin(x*.11)))
                grain=((x*73+y*31+x*y*7)%17)-8
                shade=int(22*(1-vein)**14)+grain
                base=(185,184,174) if name!='OBS' else (46,43,51)
                pixels.append(tuple(max(0,min(255,c-shade)) for c in base))
        im=Image.new('RGB',(256,256)); im.putdata(pixels)
        if name=='CRK':
            draw=ImageDraw.Draw(im)
            for shift in (0,115):
                points=[((43+shift+19*i+((i*31)%29))%256,i*32) for i in range(9)]
                draw.line(points,fill=(47,44,40),width=3)
                for x,y in points[1:-1]: draw.line([(x,y),(x-12,y+11),(x-29,y+15)],fill=(60,55,49),width=1)
        im.save(ROOT/f'mod/BrogueDoom/graphics/BRGST{name}.png',optimize=False)
    # Doom's sector lighting alone does not reveal model curvature. Bake mild
    # directional stone shading into a face atlas; this is cosmetic albedo,
    # independent of renderer settings and any gameplay light/visibility state.
    bases={k:Image.open(ROOT/f'mod/BrogueDoom/graphics/BRGST{k}.png').copy() for k in ('MAR','CRK','OBS')}
    for name, (mesh,skin) in models.items():
        kind=mesh.removeprefix('statue_'); v,f=sculpture(kind)
        columns=64; tile=16; size=1024
        height=1 << (((len(f)+columns-1)//columns*tile)-1).bit_length()
        atlas=Image.new('RGB',(size,height)); uvs=[]; face_lines=[]
        base=bases['OBS' if kind=='demon' else 'CRK' if kind in ('cracked','broken') else 'MAR']
        for index,face in enumerate(f):
            points=[v[i-1] for i in face]
            p,q,r=points[:3]; a=[q[i]-p[i] for i in range(3)]; b=[r[i]-p[i] for i in range(3)]
            n=(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
            length=math.sqrt(sum(t*t for t in n)); n=[t/length for t in n]
            shade=.62+.30*(n[0]*.60+n[1]*-.35+n[2]*.72)
            center=[sum(p[i] for p in points)/len(points) for i in range(3)]
            if center[0]>6.7 and 64.3<center[2]<65.5 and 1.2<abs(center[1])<3.4:
                shade*=.45 # recessed eyes underneath the carved brows
            x,y=(index%columns)*tile,(index//columns)*tile
            sx,sy=(index*7)%240,(index*11)%240
            patch=ImageEnhance.Brightness(base.crop((sx,sy,sx+tile,sy+tile))).enhance(shade)
            atlas.paste(patch,(x,y))
            indices=[]
            for corner,vertex in enumerate(face):
                if len(face)<=4: u,w=((0,0),(1,0),(1,1),(0,1))[corner]
                else:
                    angle=corner*2*math.pi/len(face); u,w=.5+.48*math.cos(angle),.5+.48*math.sin(angle)
                # Guard pixels protect every face from neighbouring atlas cells.
                uvs.append(((x+1.5+u*(tile-3))/size,1-(y+1.5+w*(tile-3))/height))
                indices.append(f'{vertex}/{len(uvs)}')
            face_lines.append('f '+' '.join(indices)+'\n')
        text='# Original Project Broom shaded statue, CC0-1.0\n'
        text+=''.join(f'v {x:.5f} {z:.5f} {-y:.5f}\n' for x,y,z in v)
        text+=''.join(f'vt {u:.7f} {w:.7f}\n' for u,w in uvs)+'s 1\n'+''.join(face_lines)
        (out/f'{mesh}.obj').write_text(text,newline='\n')
        atlas.save(ROOT/f'mod/BrogueDoom/graphics/{skin}.png',optimize=False)
    return models

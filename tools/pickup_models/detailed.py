"""Original grounded pickup sculptures. Blender X/Y/Z -> OBJ X/Z/-Y.

No random game state, external assets, or item selection logic. The authored
weapon components are reused without their hands or first-person poses.
"""
import hashlib
import io
import math
from tools.weapon_models import viewmodel as geo

MATERIALS = (*geo.MATERIALS, 'paper', 'ink', 'glass', 'cork', 'ruby', 'jade', 'azure', 'fruit')
COLORS = (*geo.COLORS[:4], (94,65,43), *geo.COLORS[5:], (205,180,132), (62,45,37), (77,137,144), (131,93,53),
          (148,49,47), (59,119,73), (70,108,159), (207,141,39))


def tagged(part, material):
    part.material = material
    return part


def tube(name, rows, material='wood', sides=12):
    return tagged(geo.tube(name, rows, 'steel', sides), material)


def orb(name, center, size, material='steel', sides=16, rings=8):
    return tagged(geo.ellipsoid(name, center, size, 'steel', sides, rings), material)


def ring(name, center, radius, wire, material='brass', segments=24):
    return tube(name, [(*geo.add(center,(radius*math.cos(i*math.tau/segments),
                  radius*math.sin(i*math.tau/segments),0)),wire) for i in range(segments+1)], material, 6)


def slab(name, profile, thickness, material='steel'):
    p=tagged(geo.prism(name,profile,thickness,'steel'),material)
    # Extruded vertical profile becomes a horizontal silhouette.
    p.vertices=[(z,y,x) for x,y,z in p.vertices]
    p.faces=[(a,c,b) for a,b,c in p.faces]  # reflection
    return p


def move(p, offset=(0,0,0), angles=(0,0,0)):
    p.vertices=[geo.transform(v,offset,angles) for v in p.vertices]
    return p


def rune(parts, center, kind, radius=2.5, material='ink'):
    """Non-text ornamental strokes, never a claim to Brogue's scroll title."""
    for i in range(3):
        a=(i/3+kind*.071)*math.tau
        x,y,z=center
        parts.append(tube('Engraved ornamental stroke',[(x+radius*math.cos(a),y+radius*math.sin(a),z,.12),
                     (x,y,z,.12),(x+radius*.55*math.cos(a+.7),y+radius*.55*math.sin(a+.7),z,.12)],material,5))


def build_parts(category, kind):
    symbol=category.symbol; k=0 if kind is None else kind; known=kind is not None
    p=[]
    accent=('ruby','jade','azure')[k%3] if known else 'glass'
    if symbol=='WEAPON':
        p=geo.weapon_parts(k)
        # Convert the source atlas UVs to tile-zero local UVs before remapping.
        for part in p:
            old=geo.MATERIALS.index(part.material)
            part.uv=[(u-old%4/4,v+old//4/2) for u,v in part.uv]
            move(part,angles=(0,90,0))
        # Honor the pinned physical prose without changing held-weapon art.
        for part in p:
            if k==0 and 'hilt' in part.name.lower(): part.material='wood'
            if k==9 and 'ash pole' in part.name.lower(): part.material='steel'
            if k==14 and 'ash pole' in part.name.lower(): part.material='steel'
    elif symbol=='POTION':
        # Opaque diffuse approximation of glass: no sorting-dependent shell.
        p.append(tube('Moulded bottle',[(0,0,.25,3.5),(0,0,1,4.5),(0,0,6,4.8),
                   (0,0,9,3.7),(0,0,10.7,1.65),(0,0,13.2,1.65)],'glass',24))
        p.append(ring('Thick bottle lip',(0,0,12.8),1.8,.45,'glass'))
        p.append(tube('Cut cork',[(0,0,12.7,1.4),(0,0,15,1.55)],'cork',16))
        p.append(ring('Neck cord',(0,0,11),1.75,.20,'grip'))
        # Neutral label for all unknown effects; effect ornaments only known.
        label=orb('Parchment label',(0,-4.65,5),(2.6,.13,1.8),'paper',12,6); p.append(label)
        if known:
            p.append(orb('Known-kind wax seal',(0,-4.85,5),(.9,.15,.9),accent,12,6))
            for i in range(1+k//3):
                p.append(orb('Known-kind seal mark',(-.9+i*.35,-5.03,4.6),(.10,.05,.16),'brass',6,4))
    elif symbol=='SCROLL':
        # Curled sheet across X; rolls run along Y, rather than upright posts.
        sheet=geo.Part('Curled parchment','steel')
        for row in range(21):
            x=-8+row*.8; z=.45+.5*(abs(x)/8)**4
            for y in (-5,5): sheet.vertex((x,y,z),(x+8)/16,(y+5)/10)
        for row in range(20):
            a=row*2;sheet.faces.extend(((a,a+2,a+3),(a,a+3,a+1)))
        # Two-sided sheet with physical thickness, not DontCullBackfaces.
        n=len(sheet.vertices); sheet.vertices += [(x,y,z-.18) for x,y,z in sheet.vertices]
        sheet.uv += list(sheet.uv); sheet.faces += [(c+n,b+n,a+n) for a,b,c in list(sheet.faces)]
        for a,b in [(0,1),(40,41)]+[(i,i+2) for i in range(0,40,2)]+[(i+1,i+3) for i in range(0,40,2)]:
            sheet.faces.extend(((a,b,b+n),(a,b+n,a+n)))
        p.append(tagged(sheet,'paper'))
        for x in (-8.4,8.4):
            p.append(tube('Rolled parchment edge',[(x,-5.4,1.65,1.65),(x,5.4,1.65,1.65)],'paper',20))
            for y in (-5.45,5.45):
                spiral=[]
                for i in range(41):
                    a=i*math.tau/20;r=.18+1.20*i/40
                    spiral.append((x+r*math.cos(a),y,1.65+r*math.sin(a),.07))
                p.append(tube('Visible paper spiral',spiral,'ink',4))
        for row in range(5):
            for col in range(6):
                x=-5+col*1.8; y=-3.6+row*1.8
                p.append(tube('Faded ink stroke',[(x,y,.57,.065),(x+.7,y+.15,.57,.065)],'ink',4))
        p.append(orb('Wax seal',(0,-.3,1),(1.25,1.25,.38),accent if known else 'grip',12,6))
        if known: rune(p,(0,-.3,1.4),k,.65,'brass')
    elif symbol in ('STAFF','WAND'):
        length=44 if symbol=='STAFF' else 22
        p.append(tube('Tapered carved shaft',[(-length/2,0,1.6,1),(-length*.15,.35,1.7,1.3),
                 (length*.25,-.2,1.6,1),(length/2,0,1.7,.75)],'wood',14))
        for x in (-length/2+1,-length/2+2,length/2-3,length/2-1):
            p.append(tube('Engraved ferrule',[(x-.35,0,1.7,1.35),(x+.35,0,1.7,1.35)],'brass',14))
        p.append(orb('Bound crystal terminal',(length/2,0,2),(2.2,2.2,2),accent,8,4))
        for i in range(8):
            x=-7+i*.85
            p.append(tube('Grip wrap',[(x,-1.1,1.7,.13),(x+.4,0,3,.13),(x+.8,1.1,1.7,.13)],'grip',5))
        if known: rune(p,(length/2,0,4),k,1,'brass')
    elif symbol in ('RING','CHARM','AMULET'):
        size=4 if symbol=='RING' else 6
        if symbol=='RING':
            p.append(ring('Rounded ring band',(0,0,1),size,.85))
            p.append(ring('Band chased rim',(0,0,1.6),size,.18,'edge'))
            center=(0,-size,2)
        else:
            p.append(tube('Bevelled medallion',[(0,0,.2,size-.5),(0,0,.6,size),(0,0,1.8,size),(0,0,2.2,size-.5)],'brass',24))
            p.append(ring('Raised chased rim',(0,0,2),size-.4,.22,'edge'))
            center=(0,0,2.2)
            p.append(ring('Pendant bail',(0,size+1,1),1.35,.32))
            # Necklace is laid on the floor; it does not float around the gem.
            for i in range(18):
                a=math.pi*i/17
                p.append(ring('Necklace link',(9*math.cos(a),size+2+6*math.sin(a),.55),.85,.18))
        p.append(orb('Faceted inset stone',center,(2.1,2.1,1.35),accent if symbol!='AMULET' else 'jade',8,4))
        for i in range(4):
            a=i*math.pi/2;x,y,z=center
            p.append(tube('Setting claw',[(x+2*math.cos(a),y+2*math.sin(a),z-.4,.25),
                     (x+1.7*math.cos(a),y+1.7*math.sin(a),z+.8,.18)],'brass',6))
        if symbol!='RING' or known: rune(p,(center[0],center[1],center[2]+1.35),k,1.1,'brass')
    elif symbol=='GOLD':
        for i in range(13):
            a=i*2.39996;r=math.sqrt(i)*2.2;x=r*math.cos(a);y=r*math.sin(a);z=.15+(i%3)*.45
            p.append(tube('Struck coin',[(x,y,z,2.1),(x,y,z+.55,2.1)],'brass',16))
            p.append(ring('Coin rim',(x,y,z+.6),1.7,.1,'edge',16))
            p.append(tube('Coin stamp',[(x-.7,y,z+.65,.1),(x+.7,y,z+.65,.1)],'brass',5))
    elif symbol=='GEM' or (symbol=='KEY' and k==2):
        p.append(orb('Faceted lumenstone' if symbol=='GEM' else 'Faceted crystal orb',
                     (0,0,5),(6,5,5),'jade' if symbol=='GEM' else 'azure',10,5))
        if symbol=='GEM':
            p.append(orb('Crystal growth',(4,1,2.3),(2.5,2,3),'azure',6,4))
    elif symbol=='KEY':
        p.append(ring('Worn iron bow',(-7,0,1.3),3.8,.8,'steel'))
        p.append(tube('Forged key stem',[(-4,0,1.3,.85),(9,0,1.3,.7)],'steel',10))
        for i in range(2+k):
            x=4+i*1.8
            p.append(tube('Notched iron tooth',[(x,0,1.3,.55),(x,2.2+i*.55,1.3,.55)],'steel',6))
        if k==0:
            p.append(tube('Battered leather lanyard',[(-10,0,1.2,.28),(-15,-3,.8,.28),(-19,0,.5,.28),
                         (-15,4,.7,.28),(-10,0,1.2,.28)],'grip',6))
        else:
            for i in range(4): p.append(orb('Rust and dried stain',(-6+i*3,-.65,1.7),(.45,.14,.13),'ruby',6,4))
    elif symbol=='FOOD':
        if k==1:
            p.append(orb('Asymmetric mango',(0,0,4.2),(5.8,4,4.2),'fruit',20,12))
            p.append(tube('Mango stem',[(1,0,7.8,.35),(1.8,0,9,.2)],'wood',8))
            p.append(move(orb('Small leaf',(2.4,0,8.5),(2,.7,.12),'jade',10,4),angles=(0,-12,12)))
        else:
            p.append(orb('Wrapped ration',(0,0,3),(7,5,3),'paper',16,8))
            for x in (-3,3):
                p.append(tube('Twine binding',[(x,-4.6,2,.18),(x,-3,5.1,.18),(x,0,6.2,.18),
                             (x,3,5.1,.18),(x,4.6,2,.18)],'grip',6))
            p.append(tube('Tied cord',[(-3,0,6.25,.18),(3,0,6.25,.18),(1,2,6.1,.18)],'grip',6))
    elif symbol=='ARMOR':
        p.append(orb('Laid-out torso',(0,0,3.4),(8,10,3.4),'grip' if k<2 else 'steel',20,10))
        for side in (-1,1):
            p.append(orb('Shoulder panel',(side*8,5,3),(3.8,4.5,2.6),'grip' if k==0 else 'steel',12,6))
        p.append(ring('Open neck rim',(0,7.5,5),2.7,.55,'grip'))
        if k==0:
            for x in (-5,5):
                p.append(tube('Leather seam',[(x,-7,5,.14),(x,0,6.8,.14),(x,5,5.4,.14)],'stitch',6))
            for y in (-5,1): p.append(tube('Fastened belt',[(-7,y,4.8,.5),(0,y,7,.5),(7,y,4.8,.5)],'grip',8))
        elif k in (1,2):
            for row in range(6):
                for col in range(6):
                    x=-5.7+col*2.2+(row%2)*.5;y=-6+row*2.1;z=3.4+3.2*math.sqrt(max(.1,1-(x/9)**2-(y/12)**2))
                    p.append(orb('Overlapping bronze scale',(x,y,z),(1.15,1.65,.27),'brass',8,4) if k==1
                             else ring('Interlocking mail link',(x,y,z),.95,.18,'steel',12))
        elif k==3:
            for y in range(-7,7,2):
                p.append(tube('Overlapping horizontal band',[(-6,y,5,.7),(0,y,7,.7),(6,y,5,.7)],'steel',8))
        elif k==4:
            for x in range(-6,7,2):
                p.append(tube('Vertical splint',[(x,-7,4.5,.65),(x,0,7,.65),(x,6,5,.65)],'steel',8))
        else:
            p.append(orb('Raised breastplate',(0,0,4.4),(7.3,8.5,3.1),'edge',16,8))
            p.append(tube('Breastplate ridge',[(0,-7,6,.24),(0,0,7.6,.24),(0,6,6.8,.24)],'steel',6))
        for x in (-6,6):
            for y in (-5,0,5): p.append(orb('Rivet',(x,y,6),(.28,.28,.2),'brass',6,4))
    else:
        raise ValueError(symbol)

    # Ground and center each asset at its origin. Long floor weapons are
    # uniformly reduced to fit one 64-unit cell, without changing actor bounds.
    vertices=[v for part in p for v in part.vertices]
    lo=[min(v[i] for v in vertices) for i in range(3)];hi=[max(v[i] for v in vertices) for i in range(3)]
    scale=min(1,56/max(hi[0]-lo[0],hi[1]-lo[1]))
    for part_index, part in enumerate(p):
        part.vertices=[((x-(lo[0]+hi[0])/2)*scale,(y-(lo[1]+hi[1])/2)*scale,(z-lo[2])*scale+.12) for x,y,z in part.vertices]
        if any(token in part.name.lower() for token in ('faceted','crystal terminal','crystal growth')):
            # Painted facet values remain readable under flat engine lighting.
            # These are opaque diffuse facets, not runtime lights or emissions.
            faceted=geo.Part(part.name,part.material)
            for face in part.faces:
                a,b,c=[part.vertices[i] for i in face]
                n=geo.unit(geo.cross(geo.sub(b,a),geo.sub(c,a)))
                value=max(.05,min(.95,.5+.3*n[2]+.15*n[0]-.15*n[1]))
                first=len(faceted.vertices)
                faceted.vertices.extend((a,b,c));faceted.uv.extend([(.125,1-(.035+.93*value)/2)]*3)
                faceted.faces.append((first,first+1,first+2))
            part=p[part_index]=faceted
        # All helper geometry starts with the same tile-zero UV coordinates.
        tile=MATERIALS.index(part.material)
        part.uv=[((tile%4+.035+.93*((u*4-.035)/.93))/4,
                  1-(tile//4+.035+.93*(((1-v)*2-.035)/.93))/4) for u,v in part.uv]
        part.faces=[f for f in part.faces if sum(n*n for n in geo.cross(geo.sub(part.vertices[f[1]],part.vertices[f[0]]),geo.sub(part.vertices[f[2]],part.vertices[f[0]])))>1e-16]
    return p


def obj_text(parts):
    lines=['# Original Project Broom pickup; OBJ Y up; CC-BY-SA-4.0'];offset=1
    for p in parts:
        lines.append('o '+p.name.replace(' ','_'))
        lines.extend(f'v {x:.6f} {z:.6f} {-y:.6f}' for x,y,z in p.vertices)
        lines.extend(f'vt {u:.7f} {v:.7f}' for u,v in p.uv)
        lines.extend(f'vn {x:.7f} {z:.7f} {-y:.7f}' for x,y,z in p.normals())
        lines.extend('f '+' '.join(f'{i+offset}/{i+offset}/{i+offset}' for i in face) for face in p.faces)
        offset+=len(p.vertices)
    return '\n'.join(lines)+'\n'


def atlas_bytes():
    from PIL import Image
    image=Image.new('RGB',(1024,1024));pixels=image.load()
    for tile,(name,base) in enumerate(zip(MATERIALS,COLORS)):
        for y in range(256):
            for x in range(256):
                noise=((x*73856093 ^ y*19349663 ^ tile*83492791)&255)/255-.5
                grain=math.sin(x*.34+math.sin(y*.031)*3)
                delta=noise*9
                # A restrained painted value ramp gives volumes legibility in
                # GZDoom's flat ambient model lighting; this is diffuse art.
                delta+=(y/255-.5)*36
                if name in ('wood','cork'): delta+=grain*12+math.sin(x*.1+y*.014)*7
                elif name in ('paper','stitch'): delta+=math.sin(x*2)*2+math.sin(y*2.1)*2-12*(abs(x-128)/128)**5
                elif name in ('grip','glove','sleeve'): delta+=math.sin(x*.6)*math.sin(y*.7)*5
                elif name=='glass': delta+=22*math.exp(-((x-75)/18)**2)+7*math.sin(x*.02)
                elif name in ('steel','edge','brass'): delta+=math.sin(x*.09)*8+math.sin(y*.8)*2
                elif name=='fruit': delta+=math.sin(x*.013)*15+noise*6
                else: delta+=math.sin(x*.026+y*.016)*10
                if name in ('ruby','jade','azure'): delta+=(y/255-.5)*95
                pixels[tile%4*256+x,tile//4*256+y]=tuple(max(0,min(255,round(v+delta))) for v in base)
    stream=io.BytesIO();image.save(stream,format='PNG',compress_level=9)
    return stream.getvalue()


class Model:
    def __init__(self, category, kind): self.parts=build_parts(category,kind)
    def write(self,path): path.write_text(obj_text(self.parts),encoding='ascii',newline='\n')
    def metadata(self):
        vertices=[v for p in self.parts for v in p.vertices]
        low=[min(v[i] for v in vertices) for i in range(3)];high=[max(v[i] for v in vertices) for i in range(3)]
        return {'parts':len(self.parts),'triangles':sum(len(p.faces) for p in self.parts),
                'dimensions':[round(b-a,3) for a,b in zip(low,high)],'groundClearance':.12,
                'sha256':hashlib.sha256(obj_text(self.parts).encode('ascii')).hexdigest()}

"""Original, deterministic first-person arms and weapons; no gameplay logic.

Authoring coordinates are X forward, Y left, Z up. Animated MD3 positions use
these axes directly (OBJ previews use X, Z, -Y). All poses share topology.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import math
import struct
import zlib

TAU = math.tau
MATERIALS = ('steel', 'edge', 'brass', 'wood', 'grip', 'glove', 'sleeve', 'stitch')
COLORS = ((106,118,126),(175,187,191),(140,105,53),(91,58,32),
          (46,29,21),(107,72,45),(46,55,49),(171,139,91))
TWO_HANDED = {2, 8, 9, 11}
FAMILIES = ('thrust','slash','heavy','lash','thrust','flail','heavy','heavy',
            'thrust','thrust','sweep','sweep','throw','throw','throw')
POSE_NAMES = ('ready','anticipate','windup','drive','contact','follow',
              'recover1','recover2','settle','throw_load','throw_back',
              'throw_drive','throw_release','throw_follow','throw_return','throw_settle')


def add(a,b): return tuple(x+y for x,y in zip(a,b))
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def mul(a,s): return tuple(x*s for x in a)
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def unit(a): return mul(a,1/max(math.sqrt(dot(a,a)),1e-12))


def smooth_path(points,steps=4):
    out=[]
    for i in range(len(points)-1):
        controls=(points[max(0,i-1)],points[i],points[i+1],points[min(i+2,len(points)-1)])
        for j in range(steps):
            t=j/steps
            out.append(tuple(.5*(2*b+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)
                             for a,b,c,d in zip(*controls)))
    return out+[points[-1]]


def uv_at(material,u,v):
    tile=MATERIALS.index(material)
    return ((tile%4+(0.035+.93*u))/4, 1-(tile//4+(.035+.93*v))/2)


@dataclass
class Part:
    name: str
    material: str
    vertices: list = field(default_factory=list)
    uv: list = field(default_factory=list)
    faces: list = field(default_factory=list)

    def vertex(self,p,u,v):
        self.vertices.append(tuple(p)); self.uv.append(uv_at(self.material,u,v))
        return len(self.vertices)-1

    def normals(self):
        sums={}
        keys=[tuple(round(v,5) for v in p) for p in self.vertices]
        for a,b,c in self.faces:
            n=cross(sub(self.vertices[b],self.vertices[a]),sub(self.vertices[c],self.vertices[a]))
            for i in (a,b,c): sums[keys[i]]=add(sums.get(keys[i],(0,0,0)),n)
        return [unit(sums.get(k,(0,0,1))) for k in keys]


def tube(name,points,material='glove',sides=10):
    """Variable-radius sweep with parallel-transported cross sections."""
    p=Part(name,material); previous=None
    for i,row in enumerate(points):
        center,radius=row[:3],row[3]
        tangent=unit(sub(points[min(i+1,len(points)-1)][:3],points[max(i-1,0)][:3]))
        normal=unit(cross(tangent,(0,0,1) if abs(tangent[2])<.9 else (0,1,0))) if previous is None else unit(sub(previous,mul(tangent,dot(previous,tangent))))
        previous=normal; binormal=cross(tangent,normal)
        for j in range(sides+1):
            angle=TAU*j/sides
            p.vertex(add(center,add(mul(normal,radius*math.cos(angle)),mul(binormal,radius*math.sin(angle)))),j/sides,i/(len(points)-1))
    for i in range(len(points)-1):
        for j in range(sides):
            a=i*(sides+1)+j; b=a+sides+1
            p.faces.extend(((a,a+1,b+1),(a,b+1,b)))
    for end,reverse in ((0,True),(len(points)-1,False)):
        c=p.vertex(points[end][:3],.5,.5)
        for j in range(sides):
            a=end*(sides+1)+j
            p.faces.append((c,a+1,a) if reverse else (c,a,a+1))
    return p


def ellipsoid(name,center,radius,material='glove',sides=12,rings=8):
    # Keep poles distinct but never produce zero-area pole quads.
    p=Part(name,material); p.vertex(add(center,(0,0,-radius[2])),.5,0)
    for i in range(1,rings):
        phi=-math.pi/2+math.pi*i/rings
        for j in range(sides+1):
            a=TAU*j/sides
            p.vertex(add(center,(radius[0]*math.cos(phi)*math.cos(a),radius[1]*math.cos(phi)*math.sin(a),radius[2]*math.sin(phi))),j/sides,i/rings)
    top=p.vertex(add(center,(0,0,radius[2])),.5,1)
    for j in range(sides): p.faces.append((0,j+2,j+1))
    for i in range(rings-2):
        for j in range(sides):
            a=1+i*(sides+1)+j; b=a+sides+1
            p.faces.extend(((a,a+1,b+1),(a,b+1,b)))
    a=1+(rings-2)*(sides+1)
    for j in range(sides): p.faces.append((a+j,a+j+1,top))
    return p


def prism(name,profile,thickness,material='steel'):
    """Convex blade/head profile in Y/Z, extruded through X, hard face normals."""
    p=Part(name,material)
    def face(coords):
        start=len(p.vertices)
        for i,co in enumerate(coords): p.vertex(co,(i in (1,2))*1.,(i>=2)*1.)
        for i in range(1,len(coords)-1): p.faces.append((start,start+i,start+i+1))
    # profile is counter-clockwise viewed from +X.
    face([(thickness/2,y,z) for y,z in profile])
    face([(-thickness/2,y,z) for y,z in reversed(profile)])
    for i,(y,z) in enumerate(profile):
        y1,z1=profile[(i+1)%len(profile)]
        face([(-thickness/2,y,z),(-thickness/2,y1,z1),(thickness/2,y1,z1),(thickness/2,y,z)])
    return p


def transform(point,offset,angles):
    x,y,z=point
    a,b,c=map(math.radians,angles)
    y,z=y*math.cos(a)-z*math.sin(a),y*math.sin(a)+z*math.cos(a)
    x,z=x*math.cos(b)+z*math.sin(b),-x*math.sin(b)+z*math.cos(b)
    x,y=x*math.cos(c)-y*math.sin(c),x*math.sin(c)+y*math.cos(c)
    return add((x,y,z),offset)


def ring(name,center,radius,wire,material='brass',axis='z'):
    points=[]
    for i in range(25):
        a=TAU*i/24
        delta=(radius*math.cos(a),radius*math.sin(a),0) if axis=='z' else (0,radius*math.cos(a),radius*math.sin(a))
        points.append((*add(center,delta),wire))
    return tube(name,points,material,6)


def weapon_parts(kind,frame=0):
    p=[]
    def shaft(name,z0,z1,r,material='wood'):
        p.append(tube(name,[(0,0,z0,r*.88),(0,0,z0+.5,r),(0,0,z1-.5,r),(0,0,z1,r*.88)],material,12))
    if kind in (0,1,2,4):
        length={0:22,1:34,2:44,4:36}[kind]; width={0:1.65,1:2.2,2:3.0,4:.8}[kind]
        start=10 if kind==2 else 5
        shaft('Leather-bound hilt',-5,start,1.05,'grip')
        for i in range(10 if kind==2 else 6): p.append(ring('Hilt binding %02d'%i,(0,0,-4+i*1.35),1.08,.10,'stitch'))
        p.append(ellipsoid('Peened pommel',(0,0,-5.3),(1.45,1.65,1.25),'brass'))
        p.append(tube('Curved crossguard',[(0,-6,start+.8,.38),(0,-3.5,start,.55),(0,0,start,.65),(0,3.5,start,.55),(0,6,start+.8,.38)],'brass',10))
        # Diamond cross-section gives actual bevels and a readable central ridge.
        blade=Part('Forged bevelled blade','steel')
        for z,w,t in ((start+.6,width,.48),(start+length*.75,width*.72,.32),(start+length,.02,.02)):
            for j,(x,y) in enumerate(((t,0),(0,w),(-t,0),(0,-w))): blade.vertex((x,y,z),j/4,(z-start)/length)
        for row in range(2):
            for j in range(4):
                a=row*4+j;b=row*4+(j+1)%4
                blade.faces.extend(((a,b,b+4),(a,b+4,a+4)))
        blade.faces.extend(((0,3,2),(0,2,1),(8,9,10),(8,10,11)))
        p.append(blade)
        if kind==4:
            p.append(ring('Rapier swept knuckle bow',(-.5,1.5,.5),5,.28,'brass','x'))
    elif kind in (8,9,14):
        end={8:45,9:56,14:32}[kind]
        shaft('Continuous ash pole',-25,end, .83 if kind==14 else 1.05)
        shaft('Steel socket',end-3,end+2,1.25,'steel')
        p.append(prism('Leaf spear point',[(0,end+14),(-2.5,end+5),(-1,end),(1,end),(2.5,end+5)],.65,'edge'))
        for z in (-2,0,2,4,6,8): p.append(ring('Pole grip binding',(0,0,z),1.08,.12,'grip'))
    elif kind in (12,13):
        shaft('Dart shaft',-7,12,.48,'wood')
        p.append(prism('Dart point',[(0,19),(-1.15,12),(1.15,12)],.55,'edge'))
        for angle in (0,120,240):
            fin=prism('Flight vane',[(.3,-7),(.3,-2),(2,-6),(2,-9)],.12,'stitch')
            fin.vertices=[transform(v,(0,0,0),(0,0,angle)) for v in fin.vertices];p.append(fin)
        if kind==13:
            shaft('Incendiary cloth wrap',7,12,1.2,'grip')
            p.append(tube('Unlit fuse',[(0,0,12,.22),(1,0,13,.18),(1.4,0,14,.1)],'stitch',6))
    else:
        end={3:8,5:18,6:22,7:26,10:25,11:34}[kind]
        shaft('Shaped haft',-6,end,1.05)
        shaft('Leather grip',-4,4,1.18,'grip')
        for z in (-4,-2,0,2,4): p.append(ring('Grip seam',(0,0,z),1.19,.09,'stitch'))
        p.append(ellipsoid('Haft butt',(0,0,-6),(1.35,1.35,.8),'brass'))
        if kind==3:
            points=[(0,0,8,.85),(1,-1,13,.72),(2,-4,20,.55),(1,-8,22,.4),(-1,-11,17,.3),(-2,-11,10,.24),(0,-8,5,.14),(3,-5,7,.06)]
            extension=(0,.1,.2,.65,1,.9,.45,.15,0,0,.15,.6,1,.8,.3,0)[frame]
            points=[(x+extension*i*2,y*(1-extension*.7),z+extension*i*2.5,r) for i,(x,y,z,r) in enumerate(points)]
            p.append(tube('Continuous braided lash',smooth_path(points),'grip',10))
        elif kind==5:
            swing=(0,-.1,-.3,.35,1,.85,.4,.1,0,0,-.2,.4,1,.8,.3,0)[frame]
            direction=unit((swing*.7,-.55, -1+1.8*swing))
            attachment=(0,0,19)
            for i in range(7):
                center=add(attachment,mul(direction,i*1.65))
                link=ring('Interlocked chain %02d'%i,center,1.05,.26,'steel','z' if i%2 else 'x');p.append(link)
            center=add(attachment,mul(direction,14))
            p.append(ellipsoid('Flail head',center,(3.7,3.7,3.7),'steel'))
            for i in range(8):
                a=i*TAU/8
                near=add(center,(0,3.1*math.cos(a),3.1*math.sin(a)))
                far=add(center,(0,5.3*math.cos(a),5.3*math.sin(a)))
                p.append(tube('Flail stud',[(*near,.75),(*far,.04)],'edge',6))
        elif kind==6:
            shaft('Mace core',end-3,end+6,2.0,'steel')
            for i in range(6):
                fin=prism('Mace flange',[(1,end-3),(3.5,end-1),(4,end+4),(1,end+7)],.6)
                fin.vertices=[transform(v,(0,0,0),(0,0,i*60)) for v in fin.vertices];p.append(fin)
        elif kind==7:
            p.append(prism('Hammer forged head',[(-6,end-2),(5,end-2),(6,end-1),(6,end+3),(5,end+4),(-6,end+4)],4))
            p.append(prism('Hammer striking face',[(-6.5,end-2.4),(-5.5,end-2.4),(-5.5,end+4.4),(-6.5,end+4.4)],4.8,'edge'))
        else:
            reach=9 if kind==10 else 12
            p.append(prism('Bearded axe head',[(-1,end-2),(reach*.65,end-6),(reach,end-5),(reach+1,end),(reach,end+6),(reach*.65,end+5),(-1,end+2)],1.2))
            p.append(prism('Honed axe edge',[(reach,end-5),(reach+1,end),(reach,end+6),(reach-.8,end+4),(reach-.2,end),(reach-.8,end-4)],1.35,'edge'))
            shaft('Axe eye collar',end-2,end+2,1.55,'steel')
    return p


def grip_parts(side='R',pinch=False,open_amount=0):
    """Closed glove wraps around the hilt, not a fist beside the weapon."""
    p=[ellipsoid(side+' palm',(-2.0,-.4,0),(1.3,2.0,3.5)),
       ellipsoid(side+' thumb web',(-1.3,1.0,2),(1.2,1.35,1.65))]
    for i,z in enumerate((-2.6,-.9,.8,2.5)):
        radius=.65 if not pinch else .58
        spread=open_amount*(2+i*.35)
        points=[(-2.5,-1.0,z,radius),(-1.3,-2.0,z+.1,radius),(.6,-1.95-spread,z+.1,radius*.95),(1.8,-.65-spread,z,radius*.88),(1.35,1.0-spread,z-.1,radius*.72),(.35,1.4-spread,z-.2,.28)]
        if pinch and i<2: points=[(x,y,z-1.2,r) for x,y,z,r in points]
        p.append(tube(side+' articulated finger '+str(i+1),points,'glove',8))
        p.append(ellipsoid(side+' knuckle pad '+str(i+1),(-1.4,-2.05,z+.15),(.8,.36,.63),'grip',10,6))
    p.append(tube(side+' opposing thumb',[(-3,1.0,2,.85),(-1.8,2,2.9,.8),(0,1.8,2.4,.7),(.7,1.0,1.6,.58),(.5,.7,1.1,.3)],'glove',8))
    # Connected palm heel and wrist; sleeve encloses the proximal end.
    p.append(tube(side+' wrist',[(-6,0,-1,1.85),(-4.5,0,-.5,1.8),(-2,0,0,2.1)],'glove',12))
    for z in (-1.7,0,1.7): p.append(tube(side+' glove stitching',[(-3,-1.25,z,.07),(-2.8,-1.7,z,.07),(-2,-1.85,z,.07)],'stitch',5))
    return p


def pose_transform(kind,frame):
    family=FAMILIES[kind]
    offset=(38,-14,-16)
    angles=(-12,18,-6)
    if kind in (8,9,14): angles=(-10,55,-12);offset=(35,-12,-18)
    if kind in (12,13): angles=(-20,40,-8);offset=(36,-14,-18)
    if kind in TWO_HANDED and kind not in (8,9): offset=(39,-9,-19);angles=(-15,16,-8)
    # Offsets are local presentation poses, never player/camera positions.
    if frame<9:
        strength=(0,.32,1,.7,1,.65,.35,.1,0)[frame]
        if family in ('thrust','throw'):
            offsets=((0,0,0),(-2,0,-1),(-5,1,-2),(4,2,0),(13,3,2),(8,3,0),(3,1,-1),(0,0,-.5),(0,0,0))
            reach_angle=25 if kind in (8,9,14) else (35 if kind in (12,13) else 55)
            rot=(0,reach_angle*strength if frame>=3 else -10*strength,0)
        else:
            offsets=((0,0,0),(-1,-2,1),(-3,-5,5),(3,-1,2),(5,13,-3),(2,16,-5),(-1,8,-4),(-1,2,-1),(0,0,0))
            roll=(0,-12,-35,-10,65,78,38,10,0)[frame]
            rot=(roll,(-18 if family=='heavy' else 6)*strength,0)
        offset=add(offset,offsets[frame]);angles=add(angles,rot)
    else:
        i=frame-9
        offset=add(offset,((-3,-2,2),(-6,-4,6),(5,1,3),(13,4,1),(10,5,-3),(1,1,-5),(0,0,0))[i])
        angles=add(angles,((0,-15,0),(0,-30,0),(0,30,0),(0,55,0),(15,45,0),(10,5,0),(0,0,0))[i])
    return offset,angles


def build_parts(kind,frame=0):
    offset,angles=pose_transform(kind,frame)
    p=weapon_parts(kind,frame)
    # In release/follow-through poses the held object leaves the hand below
    # the view; the separate event-driven world projectile owns its flight.
    release=frame in (12,13,14)
    for part in p:
        part.vertices=[transform(v,offset,angles) for v in part.vertices]
        if release: part.vertices=[add(v,(0,0,-180)) for v in part.vertices]
    grips=[('R',(0,0,0),offset,angles)]
    if kind in TWO_HANDED:
        grips.append(('L',(0,0,17 if kind in (8,9) else 6.7),offset,angles))
    else:
        grips.append(('L',(0,0,0),(30,18,-25),(8,10,12)))
    for side,local,position,rotation in grips:
        origin=transform(local,position,rotation)
        parts=grip_parts(side,kind in (12,13) and side=='R',.8 if release and side=='R' else 0)
        for part in parts: part.vertices=[transform(v,origin,rotation) for v in part.vertices]
        p.extend(parts)
        wrist=transform((-5.8,0,-1),origin,rotation)
        root=(5,-27 if side=='R' else 27,-48)
        elbow=(16,-24 if side=='R' else 24,-33)
        near=add(mul(elbow,.35),mul(wrist,.65))
        sleeve_path=[(*root,5.4),(*elbow,4.5)]
        for step in range(1,9):
            t=step/8;center=add(mul(elbow,1-t),mul(wrist,t))
            radius=4.5*(1-t)+2.15*t+.25*math.sin(t*math.pi*7)*math.sin(t*math.pi)
            sleeve_path.append((*center,radius))
        p.append(tube(side+' continuous sleeve',sleeve_path,'sleeve',16))
        direction=unit(sub(wrist,near))
        p.append(tube(side+' leather cuff',[(*add(wrist,mul(direction,-3.2)),2.65),(*add(wrist,mul(direction,-2.8)),2.8),(*wrist,2.6),(*add(wrist,mul(direction,.4)),2.35)],'grip',16))
        # Three seams along the forearm break up the cloth without floating armor.
        for n in (-1,0,1):
            a=add(near,(0,n*.7,2.1));b=add(wrist,(0,n*.5,1.7))
            p.append(tube(side+' sleeve seam '+str(n),[(*a,.08),(*b,.08)],'stitch',5))
    # The HUD view-to-world transform reverses the lateral convention relative
    # to world actors. Mirror Y and winding here so R appears on screen right.
    for part in p:
        part.vertices=[(x,-y,z) for x,y,z in part.vertices]
        part.faces=[(a,c,b) for a,b,c in part.faces]
    return p


def atlas_bytes(size=512):
    raw=bytearray()
    for y in range(size):
        raw.append(0)
        for x in range(size):
            tile=x//(size//4)+4*(y//(size//2));c=COLORS[tile]
            noise=((x*73856093 ^ y*19349663 ^ 83492791)&255)/255-.5
            grain=math.sin(x*.53+math.sin(y*.075)*3)
            value=noise*9
            if tile in (0,1): value+=math.sin(x*.025)*10+math.sin(x*.65)*2
            elif tile==3: value+=grain*11+math.sin(x*.15+y*.012)*6
            elif tile in (4,5):
                u=(x%(size//4))/(size//4)
                value+=math.sin(x*.8)*math.sin(y*.8)*3 + 13*math.cos((u-.45)*TAU)
                value-=8*(math.sin(y*.14+math.sin(x*.08))>.96)
            elif tile==6: value+=((x%3==0)-(y%3==0))*5+7*math.cos((x%(size//4))/(size//4)*TAU)
            raw.extend(max(0,min(255,round(v+value))) for v in c)
    def chunk(tag,data): return struct.pack('>I',len(data))+tag+data+struct.pack('>I',zlib.crc32(tag+data)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>2I5B',size,size,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(bytes(raw),9))+chunk(b'IEND',b'')


def obj_text(parts):
    lines=['# Original Project Broom viewmodel, ready pose. Runtime uses animated MD3.'];base=1
    for p in parts:
        lines.append('o '+p.name.replace(' ','_'))
        lines.extend('v %.5f %.5f %.5f'%(x,z,-y) for x,y,z in p.vertices)
        lines.extend('vt %.6f %.6f'%uv for uv in p.uv)
        lines.extend('vn %.6f %.6f %.6f'%(x,z,-y) for x,y,z in p.normals())
        lines.extend('f '+' '.join(f'{i+base}/{i+base}/{i+base}' for i in f) for f in p.faces)
        base+=len(p.vertices)
    return '\n'.join(lines)+'\n'


def md3_bytes(frames):
    """MD3 v15: one surface per authored part, stable UVs and vertex indices."""
    def name(s,n): return s.encode('ascii')[:n-1].ljust(n,b'\0')
    nf=len(frames); surfaces=[]
    for pi,p in enumerate(frames[0]):
        nv,nt=len(p.vertices),len(p.faces)
        assert nv<=4096 and nt<=8192
        triangles=b''.join(struct.pack('<3i',*f) for f in p.faces)
        shader=name('graphics/BRGHANDS.png',64)+struct.pack('<i',0)
        tex=b''.join(struct.pack('<2f',u,1-v) for u,v in p.uv)
        verts=bytearray()
        for frame in frames:
            q=frame[pi]
            assert q.faces==p.faces and q.uv==p.uv
            for v,n in zip(q.vertices,q.normals()):
                packed=[round(x*64) for x in v]
                assert all(-32768<=x<=32767 for x in packed)
                lat=round(math.atan2(n[1],n[0])*128/math.pi)&255
                lng=round(math.acos(max(-1,min(1,n[2])))*128/math.pi)&255
                verts.extend(struct.pack('<3hH',*packed,(lat<<8)|lng))
        ot=108;os=ot+len(triangles);ou=os+len(shader);ov=ou+len(tex);end=ov+len(verts)
        surfaces.append(struct.pack('<4s64s10i',b'IDP3',name(p.name,64),0,nf,1,nv,nt,ot,os,ou,ov,end)+triangles+shader+tex+verts)
    bounds=bytearray()
    for index,parts in enumerate(frames):
        vertices=[v for p in parts for v in p.vertices]
        lo=[min(v[a] for v in vertices) for a in range(3)];hi=[max(v[a] for v in vertices) for a in range(3)]
        radius=max(math.sqrt(dot(v,v)) for v in vertices)
        bounds.extend(struct.pack('<10f16s',*lo,*hi,0,0,0,radius,name(POSE_NAMES[index],16)))
    of=108;ot=of+len(bounds);end=ot+sum(map(len,surfaces))
    return struct.pack('<4si64s9i',b'IDP3',15,name('Project Broom viewmodel',64),0,nf,0,len(surfaces),0,of,ot,ot,end)+bounds+b''.join(surfaces)

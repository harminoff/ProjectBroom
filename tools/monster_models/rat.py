"""Original Project Broom rat: deterministic mesh and painted diffuse atlas.

Run with Python to rebuild runtime assets; run blender_rat.py in Blender to
create the editable source and preview. No third-party mesh/image inputs.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import hashlib
import json
import math
from pathlib import Path
import random
import struct
import zlib

ROOT = Path(__file__).resolve().parents[2]
TAU = math.tau
Vec = tuple[float, float, float]
# Pixel rectangles, with padding included; image origin is top left.
TILES = {
    "fur": (8, 8, 1016, 632),
    "ear": (8, 652, 372, 828),
    "tail": (392, 652, 1016, 828),
    "paw": (8, 852, 396, 1016),
    "eye": (420, 852, 600, 1016),
    "claw": (628, 852, 804, 1016),
    "whisker": (836, 852, 1016, 1016),
}


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def mul(a, s):
    return tuple(x * s for x in a)


def sub(a, b):
    return add(a, mul(b, -1))


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def unit(a):
    length = math.sqrt(sum(x*x for x in a))
    return mul(a, 1 / length) if length > 1e-12 else (0, 0, 1)


def atlas_uv(tile, u, v):
    x0, y0, x1, y1 = TILES[tile]
    return ((x0 + (x1-x0)*u)/1024, 1-(y0+(y1-y0)*v)/1024)


@dataclass
class Part:
    name: str
    vertices: list[Vec] = field(default_factory=list)
    uv: list[tuple[float, float]] = field(default_factory=list)
    faces: list[tuple[int, ...]] = field(default_factory=list)

    def vertex(self, co, tile, u, v):
        self.vertices.append(tuple(co))
        self.uv.append(atlas_uv(tile, u, v))
        return len(self.vertices) - 1

    def triangles(self):
        for face in self.faces:
            for i in range(1, len(face)-1):
                yield (face[0], face[i], face[i+1])

    def normals(self):
        # Weld only normal accumulation at coincident UV-seam vertices.
        # UV seams themselves stay separate in the exported topology.
        accumulated = {}
        keys = [tuple(round(x, 6) for x in v) for v in self.vertices]
        for a, b, c in self.triangles():
            normal = cross(sub(self.vertices[b], self.vertices[a]), sub(self.vertices[c], self.vertices[a]))
            for i in (a, b, c):
                accumulated[keys[i]] = add(accumulated.get(keys[i], (0, 0, 0)), normal)
        return [unit(accumulated.get(k, (0, 0, 1))) for k in keys]


def spline(points, subdivisions=4):
    """Centrally sampled Catmull-Rom, including both endpoints."""
    out = []
    for i in range(len(points)-1):
        p0, p1 = points[max(i-1, 0)], points[i]
        p2, p3 = points[i+1], points[min(i+2, len(points)-1)]
        for j in range(subdivisions):
            t = j / subdivisions
            out.append(tuple(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)
                             for a, b, c, d in zip(p0, p1, p2, p3)))
    return out + [tuple(points[-1])]


def loft(name, sections, sides=32, samples=3):
    """Anatomical cross sections along +X: x, center Z, half width, half height."""
    p = Part(name)
    rows = spline(sections, samples)
    for i, (x, z, width, height) in enumerate(rows):
        u = i/(len(rows)-1)
        for j in range(sides+1):
            t = j/sides
            angle = t*TAU
            # Subtle continuous coat breakup, not disconnected primitive shapes.
            coat = 1 + .012*math.sin(angle*7+x*1.7)*math.sin(math.pi*u)
            p.vertex((x, math.cos(angle)*width*coat, z+math.sin(angle)*height*coat), "fur", u, t)
    for i in range(len(rows)-1):
        for j in range(sides):
            a = i*(sides+1)+j
            p.faces.append((a, a+1, a+sides+2, a+sides+1))
    for end, reverse in ((0, True), (len(rows)-1, False)):
        x, z, _, _ = rows[end]
        center = p.vertex((x, 0, z), "fur", end/(len(rows)-1), .5)
        for j in range(sides):
            a = end*(sides+1)+j
            p.faces.append((center, a+1, a) if reverse else (center, a, a+1))
    return p


def ellipsoid(name, center, radius, tile="fur", segments=20, rings=12, fur_v=.48):
    p = Part(name)
    bottom = p.vertex(add(center, (0, 0, -radius[2])), tile, .5, fur_v)
    for i in range(1, rings):
        phi = -math.pi/2 + math.pi*i/rings
        for j in range(segments+1):
            theta = TAU*j/segments
            co = add(center, (radius[0]*math.cos(phi)*math.cos(theta),
                              radius[1]*math.cos(phi)*math.sin(theta), radius[2]*math.sin(phi)))
            p.vertex(co, tile, .08+.84*j/segments,
                     fur_v + .18*math.sin(phi) if tile == "fur" else .08+.84*i/rings)
    top = p.vertex(add(center, (0, 0, radius[2])), tile, .5, fur_v)
    for j in range(segments):
        p.faces.append((bottom, 1+j+1, 1+j))
    for i in range(rings-2):
        for j in range(segments):
            a = 1+i*(segments+1)+j
            p.faces.append((a, a+1, a+segments+2, a+segments+1))
    start = 1+(rings-2)*(segments+1)
    for j in range(segments):
        p.faces.append((start+j, start+j+1, top))
    return p


def tube(name, controls, tile="tail", sides=10, samples=3, ribbed=False):
    """Smooth swept tube; control entries contain x/y/z/radius."""
    p = Part(name)
    rows = spline(controls, samples)
    previous_n = None
    for i, row in enumerate(rows):
        c, radius = row[:3], max(.012, row[3])
        tangent = unit(sub(rows[min(i+1, len(rows)-1)][:3], rows[max(0, i-1)][:3]))
        if previous_n is None:
            n = unit(cross(tangent, (0, 0, 1) if abs(tangent[2]) < .9 else (0, 1, 0)))
        else:
            # Parallel-transport the frame; switching reference axes midway
            # through a bend twists the ring and pinches an otherwise smooth leg.
            n = unit(sub(previous_n, mul(tangent, sum(a*b for a,b in zip(previous_n,tangent)))))
        previous_n = n
        b = unit(cross(tangent, n))
        u = i/(len(rows)-1)
        if ribbed:
            radius *= 1 + .045*math.cos(u*TAU*38)
        for j in range(sides+1):
            angle = TAU*j/sides
            co = add(c, add(mul(n, radius*math.cos(angle)), mul(b, radius*math.sin(angle))))
            p.vertex(co, tile, u, j/sides)
    for i in range(len(rows)-1):
        for j in range(sides):
            a = i*(sides+1)+j
            p.faces.append((a, a+1, a+sides+2, a+sides+1))
    for end, reverse in ((0, True), (len(rows)-1, False)):
        center = p.vertex(rows[end][:3], tile, end/(len(rows)-1), .5)
        for j in range(sides):
            a = end*(sides+1)+j
            p.faces.append((center, a+1, a) if reverse else (center, a, a+1))
    return p


def ear(side):
    name = "L" if side > 0 else "R"
    center = (8.5, side*3.5, 12.55)
    across, up = (0, side*.96, .28), (-.30, -side*.27, .916)
    normal = unit(cross(across, up))
    if normal[0] < 0:
        normal = mul(normal, -1)
    p = Part(f"Ear_{name}_cupped")
    steps, seg = 5, 28
    # Two concentric dishes, joined at rim, create actual thickness.
    rim = []
    for back in (False, True):
        pole = p.vertex(add(center, mul(normal, -.45-(.22 if back else 0))), "fur" if back else "ear", .5, .5)
        for i in range(1, steps+1):
            r = i/steps
            for j in range(seg+1):
                a = TAU*j/seg
                irregular = 1-.10*math.exp(-((a-1.5-side*.5)/.20)**2)
                co = add(center, add(mul(across, 2.05*r*math.cos(a)*irregular),
                                     mul(up, 2.4*r*math.sin(a)*irregular)))
                co = add(co, mul(normal, -.45+.85*r*r-(.22 if back else 0)))
                p.vertex(co, "fur" if back else "ear", .5+.47*r*math.cos(a), .5+.47*r*math.sin(a))
                if not back and i == steps and j < seg:
                    rim.append((*co, .14))
        start = pole+1
        for j in range(seg):
            f = (pole, start+j, start+j+1)
            p.faces.append(f if (side > 0) != back else tuple(reversed(f)))
        for i in range(steps-1):
            for j in range(seg):
                a = start+i*(seg+1)+j
                f = (a, a+seg+1, a+seg+2, a+1)
                p.faces.append(f if (side > 0) != back else tuple(reversed(f)))
    stride = 1+steps*(seg+1)
    for j in range(seg):
        a = 1+(steps-1)*(seg+1)+j
        f = (a, a+1, a+1+stride, a+stride)
        p.faces.append(f if side > 0 else tuple(reversed(f)))
    return [p, tube(f"Ear_{name}_rolled_rim", rim+[rim[0]], "paw", 6, 1)]


BODY_SECTIONS = [
        (-13.3,6.1,.7,1.0),(-11.7,7.5,3.3,3.8),(-8.0,8.6,5.45,5.75),
        (-3.0,8.7,5.65,5.5),(2.0,8.3,4.9,4.9),(6.5,8.0,3.7,4.0),
        (10.2,8.0,3.75,3.55),(12.8,7.5,3.4,3.0),(15.7,6.7,2.25,2.0),
        (18.5,6.1,1.05,1.0),(19.1,6.05,.35,.5)]


def build_parts():
    parts = [loft("Rat_continuous_coat", BODY_SECTIONS, 36, 3)]
    parts.append(tube("Tail_tapered_rings", [(-13.0,0,6.1,1.05),(-15.5,.1,4.0,.92),
        (-19.5,1.1,2.0,.75),(-24,3.0,1.15,.58),(-28.5,5.1,.8,.43),
        (-31,8,.6,.28),(-29.2,10,.35,.15),(-26.4,9.1,.22,.025)], "tail", 12, 8, True))
    for side in (-1, 1):
        label = "L" if side > 0 else "R"
        parts.extend(ear(side))
        parts.append(ellipsoid(f"Hind_{label}_haunch", (-6.6,side*4.0,5.2), (3.7,2.0,4.4), segments=20, rings=12))
        parts.append(tube(f"Hind_{label}_hock", [(-8.0,side*4.9,4.3,1.3),(-8.5,side*5.0,2.2,.85),(-6.8,side*5.3,.85,.60)], "fur", 12, 3))
        parts.append(tube(f"Fore_{label}_leg", [(4.9,side*2.8,7.0,1.5),(6.2,side*3.8,4.0,.86),
            (5.9,side*4.0,1.8,.57),(6.9,side*4.2,.75,.49)], "fur", 12, 3))
        for fore, x, y, count in ((True,7.4,4.2,4),(False,-5.4,5.1,5)):
            prefix = ("Fore" if fore else "Hind") + "_" + label
            parts.append(ellipsoid(prefix+"_palm", (x,side*y,.72), (1.55,1.0,.62), "paw", 16, 8))
            for toe in range(count):
                spread = (toe-(count-1)/2)*.47
                length = 1.5+.38*math.sin(math.pi*(toe+1)/(count+1))
                root = (x+.7,side*y+spread,.63,.27)
                tip = (x+length+1,side*y+spread*1.45,.30,.10)
                parts.append(tube(f"{prefix}_toe_{toe+1}", [root,(x+length,side*y+spread*1.2,.47,.22),tip], "paw", 7, 2))
                parts.append(tube(f"{prefix}_claw_{toe+1}", [(*tip[:3],.14),
                    (tip[0]+.38,tip[1],.26,.10),(tip[0]+.68,tip[1],.08,.014)], "claw", 6, 2))
        # Eyelid margin recessed into the continuous head; dark wet eyeballs.
        parts.append(ellipsoid(f"Eye_{label}_socket", (12.2,side*2.94,9.40), (1.1,.42,.98), "fur", 20, 10, .22))
        parts.append(ellipsoid(f"Eye_{label}_onyx", (12.35,side*3.23,9.53), (.68,.37,.64), "eye", 20, 12))
        parts.append(ellipsoid(f"Eye_{label}_glint", (12.58,side*3.54,9.80), (.12,.04,.11), "whisker", 10, 6))
        parts.append(tube(f"Mouth_{label}_crease", [(18.5,side*.65,5.29,.065),
            (16.6,side*1.65,5.08,.08),(14.7,side*2.55,5.25,.025)], "eye", 5, 3))
        parts.append(ellipsoid(f"Nostril_{label}", (19.37,side*.61,6.39), (.25,.18,.16), "eye", 12, 8))
        for w in range(5):
            z = 6.15+w*.28
            parts.append(tube(f"Whisker_{label}_{w+1}", [(16.7-w*.26,side*1.70,z,.060),
                (17.8-w*.68,side*4.7,z+.45,.044),
                (16.2-w*1.0,side*(7.0+w*.32),z+.10-.12*w,.010)], "whisker", 5, 4))
    parts.append(ellipsoid("Nose_leather", (19.03,0,6.02), (.81,1.04,.75), "paw", 24, 14))
    for side in (-1,1):
        parts.append(ellipsoid(f"Incisor_{side}", (18.10,side*.31,5.08), (.36,.24,.54), "claw", 10, 8))
    # Small opaque tapered wedges catch the outline without hair transparency.
    rng = random.Random(1101)
    tufts = Part("Coat_guard_hair_tufts")
    rows = spline(BODY_SECTIONS, 3)
    for i in range(110):
        x = rng.uniform(-10.5,5.5)
        angle = rng.uniform(.10,math.pi-.10)
        ri = next(j for j in range(len(rows)-1) if rows[j][0] <= x <= rows[j+1][0])
        fraction = (x-rows[ri][0])/(rows[ri+1][0]-rows[ri][0])
        _,z,width,height = [a*(1-fraction)+b*fraction for a,b in zip(rows[ri],rows[ri+1])]
        u = (ri+fraction)/(len(rows)-1)
        coat = 1+.012*math.sin(angle*7+x*1.7)*math.sin(math.pi*u)
        root = (x, math.cos(angle)*width*coat*.994, z+math.sin(angle)*height*coat*.994)
        normal = unit((-.20,math.cos(angle),math.sin(angle)))
        a = tufts.vertex(add(root, (0,-.17,.03)), "fur", (x+13.3)/32.4, angle/TAU)
        b = tufts.vertex(add(root, (0,.17,-.03)), "fur", (x+13.3)/32.4, angle/TAU)
        tip = tufts.vertex(add(root, add(mul(normal,rng.uniform(.09,.19)),(-rng.uniform(.35,.65),0,0))), "fur", (x+12.8)/32.4, angle/TAU)
        d = tufts.vertex(add(root,(.2,0,-.15)), "fur", (x+13.4)/32.4, angle/TAU)
        tufts.faces.extend(((a,b,tip),(a,tip,d),(b,d,tip),(a,d,b)))
    parts.append(tufts)
    return parts


def obj_bytes(parts):
    lines = ["# Project Broom original detailed rat; CC-BY-SA-4.0", "# OBJ axes X=forward Y=up Z=-BlenderY; one diffuse skin via MODELDEF"]
    offset = 1
    for part in parts:
        lines.append("o "+part.name)
        for x,y,z in part.vertices:
            lines.append(f"v {x:.6f} {z:.6f} {-y:.6f}")
        lines.extend(f"vt {u:.7f} {v:.7f}" for u,v in part.uv)
        lines.extend(f"vn {x:.7f} {z:.7f} {-y:.7f}" for x,y,z in part.normals())
        lines.append("s 1")
        for face in part.triangles():
            lines.append("f "+" ".join(f"{i+offset}/{i+offset}/{i+offset}" for i in face))
        offset += len(part.vertices)
    return ("\n".join(lines)+"\n").encode("ascii")


def texture_bytes():
    """Paint original fur strokes and skin creases into an opaque RGB atlas."""
    size = 1024
    pixels = bytearray([90,83,79])*(size*size)
    rng = random.Random(1101007)

    def pixel(x,y,color,alpha=1.0):
        if not (0 <= x < size and 0 <= y < size):
            return
        k = (y*size+x)*3
        for c in range(3):
            pixels[k+c] = max(0,min(255,round(pixels[k+c]*(1-alpha)+color[c]*alpha)))

    # Per-pixel coat variation; circumference maps dorsal to dark, belly to ash.
    for tile, (x0,y0,x1,y1) in TILES.items():
        for y in range(y0-7,y1+8):
            v = (y-y0)/(y1-y0)
            for x in range(x0-7,x1+8):
                u = (x-x0)/(x1-x0)
                noise = rng.uniform(-7,7)
                if tile == "fur":
                    dorsal = max(0,math.sin(v*TAU))
                    belly = max(0,-math.sin(v*TAU))**3
                    tone = 119-40*dorsal+29*belly+7*math.sin(u*15+v*19)+noise
                    color = (tone+3,tone+1,tone-3)
                elif tile == "ear":
                    r = min(1,math.hypot((u-.5)*2,(v-.5)*2))
                    crease = 7*math.sin(math.atan2(v-.5,u-.5)*22+r*15)*(1-r)
                    color = (138+20*r+noise+crease,101+15*r+noise,100+13*r+noise)
                elif tile == "tail":
                    ridge = math.cos(u*TAU*42)
                    scales = 4*math.sin(v*TAU*11+int(u*84)*.8)
                    tone = noise+scales+9*ridge+12*math.sin(v*math.pi)
                    color = (138+tone,109+tone,104+tone)
                elif tile == "paw":
                    tone = noise+5*math.sin(u*67+v*20)+6*math.sin(v*35)
                    color = (151+tone,117+tone,111+tone)
                elif tile == "eye":
                    color = (16+noise*.2,14+noise*.2,13+noise*.2)
                elif tile == "claw":
                    tone = 18*v+noise*.4
                    color = (174+tone,163+tone,130+tone)
                else:
                    color = (175+noise,170+noise,155+noise)
                pixel(x,y,color)
    x0,y0,x1,y1 = TILES["fur"]
    for stroke in range(44000):
        x,y = rng.randrange(x0-5,x1+5),rng.randrange(y0-5,y1+5)
        length = rng.randrange(5,25)
        lean = rng.uniform(-.15,.15)
        light = rng.choice((-32,-22,-14,14,23,35))
        k=(y*size+x)*3
        color=tuple(max(0,min(255,pixels[k+c]+light)) for c in range(3))
        for n in range(length):
            xx,yy=x-n,round(y+lean*n+math.sin(n*.18)*.6)
            if x0-6 <= xx <= x1+6 and y0-6 <= yy <= y1+6:
                pixel(xx,yy,color,.65*(1-n/length))
    # Subtle ear capillaries; no painted wounds or fantasy markings.
    for vein in range(28):
        a=rng.uniform(0,TAU)
        for n in range(45):
            t=.15+n/65
            x=round(190+math.cos(a+t*.10)*170*t)
            y=round(740+math.sin(a+t*.10)*82*t)
            pixel(x,y,(121,79,78),.18)
    raw=b"".join(b"\0"+pixels[y*size*3:(y+1)*size*3] for y in range(size))
    def chunk(kind,data):
        return struct.pack(">I",len(data))+kind+data+struct.pack(">I",zlib.crc32(kind+data)&0xffffffff)
    return b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">IIBBBBB",size,size,8,2,0,0,0))+chunk(b"IDAT",zlib.compress(raw,9))+chunk(b"IEND",b"")


def build(output_root=ROOT):
    parts=build_parts()
    model=output_root/"mod/BrogueDoom/models/monsters/01_rat.obj"
    skin=output_root/"mod/BrogueDoom/graphics/BRGRAT.png"
    payloads=((model,obj_bytes(parts)),(skin,texture_bytes()))
    for path,payload in payloads:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(payload)
    vertices=[v for p in parts for v in p.vertices]
    return {"parts":len(parts),"vertices":len(vertices),
            "triangles":sum(1 for p in parts for _ in p.triangles()),
            "blenderBounds": [[round(min(v[i] for v in vertices),4),round(max(v[i] for v in vertices),4)] for i in range(3)],
            "sha256":{str(p.relative_to(output_root)).replace("\\","/"):hashlib.sha256(b).hexdigest() for p,b in payloads}}


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root",type=Path,default=ROOT)
    print(json.dumps(build(parser.parse_args().output_root),indent=2))

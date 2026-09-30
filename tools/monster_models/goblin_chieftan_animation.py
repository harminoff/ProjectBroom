"""Original goblin warlord (MK_GOBLIN_CHIEFTAN); cosmetic skeletal presentation only.

Pinned Brogue (Globals.c L1127/L1333): "Taller, stronger and smarter than other
goblins", commands and summons its kind, penetrating attacks (read here as the
goblin family's spear), blue glyph colour. The iron crested helm, fur mantle,
war cloak, pennant, pauldron and trophy skull are artistic readings of
"warlord"; blue is the glyph identity cue, never a claimed power. Monsters.c
summoning, war cry, distance keeping and corridor avoidance stay Brogue-owned.

Anatomy is authored in goblin-family units (G) and scaled by S at the end, so
the head reuses the accepted goblin craniofacial surface while the body is
rebuilt taller and heavier rather than uniformly enlarged.
"""
import hashlib
import json
import math
from . import iqm, goblin_animation as goblin, goblin_chieftan_materials as materials
from .creatures import Sculpt
from .rat import ROOT, Part, add, sub, mul, unit, cross
from .skeletal import Rig, axis, between, inverse, qmul, rotate, assemble, sample_clips

SKIN = 'graphics/BRGWARLD.png'
MODEL = 'mod/BrogueDoom/models/monsters/51_goblin_chieftan.iqm'
S = 1.15
SKIN_FACE_BUDGET = 6200
HEAD_OFFSET = (.1, 0, 3.2)          # goblin head -> warlord head (G units)
D_REST = unit((.5, -.16, .85))      # spear axis in the rest grip
GRIP = (4.9, -10.35, 18.8)          # shaft centre inside the right fist (G)
PENNANT_T = 12.8                    # pennant root along the shaft (G)


def sc(p): return tuple(round(c*S, 6) for c in p)
def dot(a, b): return sum(x*y for x, y in zip(a, b))
def lerp(a, b, t): return tuple(x+(y-x)*t for x, y in zip(a, b))
def smooth(x): x = max(0., min(1., x)); return x*x*(3-2*x)
def along(t): return add(GRIP, mul(D_REST, t))
PENNANT_DIR = unit(sub((-.5, -.87, 0), mul(D_REST, dot((-.5, -.87, 0), D_REST))))


SPECS_G = [('root', None, (0, 0, 0)), ('pelvis', 'root', (0, 0, 20)),
           ('spine', 'pelvis', (-1.6, 0, 29.5)), ('neck', 'spine', (1.2, 0, 35)),
           ('head', 'neck', (3.1, 0, 38.2)), ('jaw', 'head', (5.1, 0, 35.7))]
for _side, _sign in (('L', 1), ('R', -1)):
    for _limb, _parent, _points in (
            ('arm', 'spine', [(0, _sign*7.4, 31.2), (2.0, _sign*9.9, 25.4), (4.4, _sign*10.0, 20.4)]),
            ('leg', 'pelvis', [(0, _sign*3.6, 20), (4.6, _sign*4.1, 11.2), (2.2, _sign*4.6, 2.4)])):
        for _joint, _point in zip(('upper', 'lower', 'end'), _points):
            _name = f'{_limb}_{_side}_{_joint}'; SPECS_G.append((_name, _parent, _point)); _parent = _name
SPECS_G += [('spear', 'arm_R_end', (4.4, -10.0, 20.4)), ('pennant', 'spear', along(PENNANT_T)),
            ('cape', 'spine', (-4.6, 0, 34.2))]
RIG = Rig.from_world([(n, p, sc(v)) for n, p, v in SPECS_G])
BONES, REST = RIG.bones, RIG.rest
IDS = {n: i for i, (n, p, v) in enumerate(BONES)}
CLIPS = [('idle', 40, 20, True), ('walk', 24, 35, True), ('thrust', 22, 35, False),
         ('cleave', 24, 35, False), ('recoil', 12, 35, False), ('death', 32, 35, False)]
CAGE_PREFIXES = ('arm_', 'leg_', 'shoulder_', 'hand_', 'foot_', 'head_brow_')


def CONNECTED_SKIN(name):
    return (name in ('pelvis', 'torso', 'head_cranium', 'head_ear_1', 'head_ear_-1')
            or name.startswith(CAGE_PREFIXES))


# ---------------------------------------------------------------- primitives
def raw(name):
    p = Part(name); p.local = True; return p


def put(p, co, u, v):
    p.vertices.append(tuple(co)); p.uv.append((u, v)); return len(p.vertices)-1


def local_uv(part):
    """Sculpt primitives store rat-atlas UVs; recover their 0..1 parameters."""
    from .rat import TILES
    out = []
    for u, v in part.uv:
        x, y = u*1024, (1-v)*1024
        r = next(r for r in TILES.values() if r[0]-.01 <= x <= r[2]+.01 and r[1]-.01 <= y <= r[3]+.01)
        out.append(((x-r[0])/(r[2]-r[0]), (y-r[1])/(r[3]-r[1])))
    part.uv = out
    return part


def rings(name, rows, segments=36, shape=None):
    """Closed ring surface: rows are (z, cx, depth, width)."""
    p = raw(name)
    for j, (z, cx, depth, width) in enumerate(rows):
        for i in range(segments):
            a = math.tau*i/segments
            x, y = cx+depth*math.cos(a), width*math.sin(a)
            if shape: x, y, z2 = shape(x, y, z, a)
            else: z2 = z
            put(p, (x, y, z2), i/segments, j/(len(rows)-1))
    for j in range(len(rows)-1):
        for i in range(segments):
            a = j*segments+i; b = j*segments+(i+1) % segments
            p.faces.append((a, b, b+segments, a+segments))
    bottom = put(p, (rows[0][1], 0, rows[0][0]), .5, 0)
    top = put(p, (rows[-1][1], 0, rows[-1][0]), .5, 1)
    last = (len(rows)-1)*segments
    for i in range(segments):
        j = (i+1) % segments
        p.faces.append((bottom, j, i)); p.faces.append((last+i, last+j, top))
    return p


def loop_tube(name, center, radii, z, radius, segments=48, sides=10, wobble=None):
    """Closed torus-like band (belt, rim, mantle)."""
    p = raw(name)
    cx, cy = center; ax, ay = radii
    for i in range(segments):
        a = math.tau*i/segments
        c = (cx+ax*math.cos(a), cy+ay*math.sin(a), z(a) if callable(z) else z)
        out = unit((math.cos(a)/ax, math.sin(a)/ay, 0))
        for j in range(sides):
            b = math.tau*j/sides
            r = radius(a, b) if callable(radius) else radius
            if wobble: r *= wobble(a, b)
            co = add(c, add(mul(out, r*math.cos(b)), (0, 0, r*math.sin(b))))
            put(p, co, i/segments, j/sides)
    for i in range(segments):
        for j in range(sides):
            a = i*sides+j; b = i*sides+(j+1) % sides
            c = ((i+1) % segments)*sides+(j+1) % sides; d = ((i+1) % segments)*sides+j
            p.faces.append((a, d, c, b))
    return p


def slab(name, fn, nu, nv, thickness):
    """Closed thin sheet from a parametric surface; outward winding verified."""
    p = raw(name)
    grid = [[fn(i/nu, j/nv) for j in range(nv+1)] for i in range(nu+1)]
    def normal(i, j):
        du = sub(grid[min(i+1, nu)][j], grid[max(i-1, 0)][j])
        dv = sub(grid[i][min(j+1, nv)], grid[i][max(j-1, 0)])
        return unit(cross(du, dv))
    top = {}; bottom = {}
    for i in range(nu+1):
        for j in range(nv+1):
            n = normal(i, j)
            top[i, j] = put(p, add(grid[i][j], mul(n, thickness/2)), i/nu, j/nv)
    for i in range(nu+1):
        for j in range(nv+1):
            n = normal(i, j)
            bottom[i, j] = put(p, sub(grid[i][j], mul(n, thickness/2)), i/nu, 1-j/nv)
    faces = []
    for i in range(nu):
        for j in range(nv):
            faces.append((top[i, j], top[i+1, j], top[i+1, j+1], top[i, j+1]))
            faces.append((bottom[i, j], bottom[i, j+1], bottom[i+1, j+1], bottom[i+1, j]))
    offset = {top[k]: bottom[k] for k in top}
    directed = set()
    for f in faces[::2]:
        for a, b in zip(f, f[1:]+f[:1]): directed.add((a, b))
    for a, b in sorted(directed):
        if (b, a) not in directed: faces.append((b, a, offset[a], offset[b]))
    p.faces = faces
    if signed_volume(p) < 0: p.faces = [tuple(reversed(f)) for f in p.faces]
    return p


def signed_volume(p):
    return sum(dot(p.vertices[a], cross(p.vertices[b], p.vertices[c])) for a, b, c in p.triangles())/6


def diamond_loft(name, rows, frame):
    """Closed blade/lug: rows (t, half-width, half-thickness) in a (D, W, T) frame."""
    D, W, T = frame; origin, rows = rows[0], rows[1:]
    p = raw(name)
    for k, (t, w, th) in enumerate(rows):
        c = add(origin, mul(D, t))
        for u, (a, b) in enumerate(((1, 0), (0, 1), (-1, 0), (0, -1))):
            put(p, add(c, add(mul(W, a*w), mul(T, b*th))), k/(len(rows)-1), u/4)
    n = len(rows)
    for k in range(n-1):
        for u in range(4):
            a = k*4+u; b = k*4+(u+1) % 4
            p.faces.append((a, b, b+4, a+4))
    base = put(p, add(origin, mul(D, rows[0][0])), 0, .5)
    tip = put(p, add(origin, mul(D, rows[-1][0]+rows[-1][1]*0+.001)), 1, .5)
    for u in range(4):
        p.faces.append((base, (u+1) % 4, u)); p.faces.append(((n-1)*4+u, (n-1)*4+(u+1) % 4, tip))
    if signed_volume(p) < 0: p.faces = [tuple(reversed(f)) for f in p.faces]
    return p


def moved(part, fn):
    part.vertices = [fn(v) for v in part.vertices]; return part


# ---------------------------------------------------------------- anatomy
def head_parts(s):
    off = lambda v: add(v, HEAD_OFFSET)
    cranium = goblin.sculpted_head()
    def heavier(v):
        x, y, z = v
        jaw = smooth((33.7-z)/2.2); front = max(0, x-2)/3
        # A broader, jutting lower face and thicker brow ridge: older, heavier.
        brow = math.exp(-((z-36.3)/.55)**2)*max(0, x-3)/2
        return off((x+.35*jaw*front+.28*brow, y*(1+.16*jaw), z))
    cranium.vertices = [heavier(v) for v in cranium.vertices]
    s.parts.append(cranium)
    for sign in (-1, 1):
        ear = goblin.swept_ear(f'head_ear_{sign}', sign)
        inner = goblin.swept_ear(f'head_ear_inner_{sign}', sign, True)
        for e in (ear, inner):
            # Longer, lower war-swept ears read past the helm rim.
            moved(e, lambda v, sign=sign: off((v[0]-.25*max(0, abs(v[1])-3.3), v[1]*1.0+sign*.12*max(0, abs(v[1])-3.3), v[2]-.18*max(0, abs(v[1])-3.3))))
            s.parts.append(e)
        for name, c, r, mat in ((f'head_eye_socket_{sign}', (4.6, sign*1.65, 35.55), (.17, .72, .27), 'dark'),
                                (f'head_eye_iris_{sign}', (4.77, sign*1.65, 35.58), (.08, .34, .2), 'accent'),
                                (f'head_eye_pupil_{sign}', (4.84, sign*1.65, 35.58), (.03, .1, .17), 'dark')):
            p = s.oval(name, c, r, mat, 12, 7)
            moved(p, lambda v: off((v[0], v[1], v[2]+(abs(v[1])-1.65)*.32)))
        s.strand(f'head_brow_{sign}', [(5.75, sign*.6, 35.95, .5), (5.2, sign*1.65, 36.2, .52), (4.3, sign*2.7, 36.5, .36)], 'cloth', 10)
        moved(s.parts[-1], off)
        s.oval(f'head_nostril_{sign}', (6.5, sign*.45, 34.05), (.1, .18, .11), 'dark', 8, 5)
        moved(s.parts[-1], off)
        # Short lower tusks: heavier jaw anatomy, cosmetic only.
        s.strand(f'jaw_tusk_{sign}', [(5.05, sign*1.35, 32.75, .2), (5.45, sign*1.5, 33.45, .15), (5.5, sign*1.62, 33.95, .035)], 'bone', 8)
        moved(s.parts[-1], off)
    s.strand('jaw_mouth', [(4.95, -1.75, 32.85, .11), (5.55, -.7, 32.72, .12), (5.55, .7, 32.72, .12), (4.95, 1.75, 32.85, .11)], 'dark', 8)
    moved(s.parts[-1], off)
    s.oval('jaw_lower', (4.6, 0, 32.2), (.95, 1.75, .42), 'cloth', 12, 6)
    moved(s.parts[-1], off)


def torso():
    rows = [(18.6, -.2, 3.3, 4.3), (20.5, -.3, 3.4, 4.6), (22.5, -.5, 3.55, 4.55), (24.5, -.9, 3.5, 4.6),
            (26.5, -1.3, 3.6, 5.2), (28.5, -1.7, 3.95, 6.2), (30.4, -2.0, 4.05, 6.8), (32.2, -1.8, 3.65, 6.4),
            (33.7, -.8, 3.0, 4.8), (35, .3, 2.4, 3.2), (36.4, 1.1, 2.1, 2.6)]
    def shape(x, y, z, a):
        front = max(0, math.cos(a))
        pec = .75*math.exp(-((z-29.6)/2.1)**2-((abs(y)-2.7)/1.9)**2)
        belly = .55*math.exp(-((z-22.8)/2.4)**2-(y/3.2)**2)
        sternum = -.28*math.exp(-(y/.7)**2-((z-28)/3.5)**2)
        back = max(0, -math.cos(a))
        lats = .35*math.exp(-((z-28)/3)**2-((abs(y)-4)/1.6)**2)
        return x+front*(pec+belly+sternum)-back*lats, y, z
    return rings('torso', rows, 36, shape)


def right_grip(s):
    """Fingers curl around the actual shaft axis rather than float beside it."""
    q = between((0, 0, 1), D_REST)
    place = lambda v: add(GRIP, rotate(q, v))
    start = len(s.parts)
    s.oval('hand_R_palm', (0, .95, .25), (1.3, .85, 1.85), 'cloth', 16, 10)
    for i, z in enumerate((1.05, .35, -.35, -1.05)):
        pts = [(.95*math.cos(math.radians(a)), .95*math.sin(math.radians(a)), z, r)
               for a, r in ((70, .44), (15, .44), (-45, .42), (-105, .38), (-150, .28))]
        s.strand(f'hand_R_finger{i}', pts, 'cloth', 8, 3)
    s.strand('hand_R_thumb', [(-.2, 1.2, 1.55, .5), (-.95, .45, 1.65, .45), (-.9, -.45, 1.55, .36), (-.3, -.95, 1.45, .25)], 'cloth', 8, 3)
    for p in s.parts[start:]: moved(p, place)


def left_fist(s):
    x, y, z = 4.4, 10.0, 20.4
    s.oval('hand_L_palm', (x+.25, y, z-1.55), (1.45, 1.15, 1.85), 'cloth', 16, 10)
    for i in range(4):
        yy = y+(i-1.5)*.64
        s.strand(f'hand_L_finger{i}', [(x+.6, yy, z-3.0, .46), (x+1.55, yy, z-2.85, .44),
                                       (x+1.95, yy, z-1.95, .4), (x+1.55, yy, z-1.2, .3)], 'cloth', 8, 3)
    s.strand('hand_L_thumb', [(x+.4, y-1.1, z-.9, .52), (x+1.4, y-1.25, z-1.55, .44), (x+2.0, y-.6, z-1.85, .3)], 'cloth', 8, 3)


def limbs(s):
    for side, sign in (('L', 1), ('R', -1)):
        up, lo, en = [dict((n, v) for n, p, v in SPECS_G)[f'arm_{side}_{j}'] for j in ('upper', 'lower', 'end')]
        s.oval(f'shoulder_{side}', (-.5, sign*7.0, 31.0), (2.95, 3.1, 3.05))
        s.oval(f'shoulder_trap_{side}', (-1.3, sign*3.9, 33.4), (2.3, 2.7, 1.7))
        s.strand(f'arm_{side}', [(*up, 2.55), (*lerp(up, lo, .5), 2.6), (*lo, 1.95),
                                 (*lerp(lo, en, .45), 1.95), (*en, 1.42)], sides=18, samples=4)
        hip, knee, ankle = [dict((n, v) for n, p, v in SPECS_G)[f'leg_{side}_{j}'] for j in ('upper', 'lower', 'end')]
        calf = add(lerp(knee, ankle, .35), (-.45, 0, 0))
        s.strand(f'leg_{side}', [(*hip, 2.95), (*lerp(hip, knee, .5), 2.8), (*knee, 2.05),
                                 (*calf, 2.15), (*ankle, 1.42)], sides=18, samples=4)
        s.oval(f'foot_{side}', (3.2, sign*4.6, 1.45), (3.3, 2.1, 1.35), 'cloth')
        for i in range(4):
            s.oval(f'foot_{side}_toe{i}', (6.05, sign*4.6+(i-1.5)*.9, 1.12), (.95, .52, .76), 'cloth', 12, 8)
    right_grip(s); left_fist(s)


# ---------------------------------------------------------------- war gear
def helm(s):
    cranium = next(p for p in s.parts if p.name == 'head_cranium')
    # Rim follows the skull: higher over the brow, lower at the nape.
    rim = lambda a: 40.05+.55*math.cos(a)
    rows = []
    for k, level in enumerate((0, .2, .42, .62, .8, .93, 1)):
        z0 = 40.05; zt = 43.35
        rows.append((z0+(zt-z0)*level, level))
    def radius_at(z):
        pts = [v for v in cranium.vertices if abs(v[2]-z) < .45]
        return (min(v[0] for v in pts), max(v[0] for v in pts), max(abs(v[1]) for v in pts)) if pts else None
    dome = raw('helm_dome'); seg = 32
    base = radius_at(39.8)
    for j, (z, level) in enumerate(rows):
        lo, hi, w = base
        cx = (lo+hi)/2-.05*level; depth = ((hi-lo)/2+.5)*math.cos(level*math.pi/2)**.8
        width = (w+.5)*math.cos(level*math.pi/2)**.8
        for i in range(seg):
            a = math.tau*i/seg
            zz = z+(rim(a)-40.05)*(1-level)
            put(dome, (cx+max(depth, .02)*math.cos(a), max(width, .02)*math.sin(a), zz), i/seg, level)
    for j in range(len(rows)-1):
        for i in range(seg):
            a = j*seg+i; b = j*seg+(i+1) % seg
            dome.faces.append((a, b, b+seg, a+seg))
    # Inner lining closes the shell so it renders from any angle.
    inner = len(dome.vertices)
    for i in range(seg):
        x, y, z = dome.vertices[i]; cx = sum(v[0] for v in dome.vertices[:seg])/seg
        put(dome, (cx+(x-cx)*.9, y*.9, z+.35), i/seg, 0)
    cap = put(dome, (cx, 0, 42.6), .5, .5)
    for i in range(seg):
        j = (i+1) % seg
        dome.faces.append((i, inner+i, inner+j, j)); dome.faces.append((inner+j, inner+i, cap))
    top = (len(rows)-1)*seg; crown = put(dome, (cx, 0, rows[-1][0]+.02), .5, 1)
    for i in range(seg): dome.faces.append((top+i, top+(i+1) % seg, crown))
    if signed_volume(dome) < 0: dome.faces = [tuple(reversed(f)) for f in dome.faces]
    s.parts.append(dome)
    lo, hi, w = base; cx = (lo+hi)/2
    s.parts.append(loop_tube('helm_rim', (cx, 0), ((hi-lo)/2+.62, w+.62), lambda a: rim(a)+.05, .36, 40, 6))
    # Nasal guard from rim to the bridge of the nose.
    front = hi+.55
    s.parts.append(slab('helm_nasal', lambda u, v: (front-.15*u+.1*(1-4*(v-.5)**2), (v-.5)*(.95-.35*u), 40.55-2.35*u), 4, 2, .28))
    # Curved bone horns: the war-band leader's silhouette at any distance.
    for sign in (-1, 1):
        s.strand(f'helm_horn_{sign}', [(1.25, sign*3.95, 41.1, .78), (.7, sign*5.6, 42.15, .64),
                                       (.85, sign*6.75, 44.1, .46), (1.75, sign*6.95, 46.2, .22), (2.7, sign*6.55, 47.4, .03)], 'bone', 9, 3)
    # Blue crest ridge (glyph colour cue) with stiff tufts along its crown.
    crest = raw('crest')
    n = 14
    for i in range(n+1):
        t = i/n; x = 4.1-7.6*t; zc = 43.15+.35*math.sin(math.pi*t)-.8*t*t
        h = .9+3.1*math.sin(math.pi*(.15+.8*t))**.7
        for k, (dy, dz) in enumerate(((-.85, 0), (-.5, h), (.5, h), (.85, 0))):
            put(crest, (x-.35*dz*t, dy, zc+dz-.5), t, k/3)
    for i in range(n):
        for k in range(4):
            a = i*4+k; b = i*4+(k+1) % 4
            crest.faces.append((a, b, b+4, a+4))
    last = n*4
    crest.faces.append((0, 3, 2, 1)); crest.faces.append((last, last+1, last+2, last+3))
    if signed_volume(crest) < 0: crest.faces = [tuple(reversed(f)) for f in crest.faces]
    s.parts.append(crest)
    for i in range(10):
        t = (i+.5)/10; x = 4.1-7.6*t; zc = 43.15+.35*math.sin(math.pi*t)-.8*t*t
        h = .9+3.1*math.sin(math.pi*(.15+.8*t))**.7
        side = (1 if i % 2 else -1)
        base_pt = (x-.35*h*t, side*.35, zc+h-.8)
        s.strand(f'crest_tuft_{i}', [(*base_pt, .42), (base_pt[0]-.6, side*1.25, base_pt[2]+.85, .26), (base_pt[0]-1.3, side*2.1, base_pt[2]+1.2, .03)], 'accent', 5, 2)


def mantle():
    cx = -1.15
    def z(a): return 33.9-.35*math.cos(a)+.25*math.cos(2*a)
    def radius(a, b):
        # Flattened, drooping fur roll: wider outward, heavier over shoulders.
        base = 1.75+.45*abs(math.sin(a))
        return base*(1.2 if math.cos(b) > 0 else .85)
    def wobble(a, b):
        tuft = max(0, math.sin(a*13+1.7*math.sin(b*2)))**2
        return 1+.2*tuft*max(0, math.cos(b)+.4)+.05*math.sin(a*29+b*3)
    return loop_tube('mantle', (cx, 0), (4.0, 6.45), z, radius, 44, 9, wobble)


def cape():
    def fn(u, v):
        # u: across the back (-70..70 deg), v: top -> ragged hem.
        a = math.radians(-68+136*u)
        z = 33.2-v*(20.2+.9*math.sin(u*37)*v+.6*math.sin(u*11))
        cx = -1.9-1.0*v; rx = 4.55+1.7*v; ry = 6.35+1.3*v
        fold = .32*math.sin(u*math.tau*3.5)*v
        return (cx-(rx+fold)*math.cos(a), (ry+fold*.3)*math.sin(a), z)
    return slab('cape', fn, 16, 10, .3)


def pauldron(s):
    c = (-.45, 7.55, 31.55)
    p = raw('pauldron_L'); seg = 22; levels = 6
    for j in range(levels):
        phi = math.radians(-8+92*j/(levels-1))
        for i in range(seg):
            a = math.tau*i/seg
            r = (3.55*math.cos(phi), 3.5*math.cos(phi), 3.1*math.sin(phi))
            put(p, (c[0]+r[0]*math.cos(a), c[1]+r[1]*math.sin(a)+.6*math.sin(phi), c[2]+r[2]), i/seg, j/(levels-1))
    for j in range(levels-1):
        for i in range(seg):
            a = j*seg+i; b = j*seg+(i+1) % seg
            p.faces.append((a, b, b+seg, a+seg))
    top = (levels-1)*seg; crown = put(p, (c[0], c[1]+.6, c[2]+3.12), .5, 1)
    for i in range(seg): p.faces.append((top+i, top+(i+1) % seg, crown))
    inner = len(p.vertices)
    for i in range(seg):
        x, y, z = p.vertices[i]; put(p, (c[0]+(x-c[0])*.86, c[1]+(y-c[1])*.86, z+.3), i/seg, 0)
    cap = put(p, (c[0], c[1]+.4, c[2]+1.4), .5, .5)
    for i in range(seg):
        j = (i+1) % seg
        p.faces.append((i, inner+i, inner+j, j)); p.faces.append((inner+j, inner+i, cap))
    if signed_volume(p) < 0: p.faces = [tuple(reversed(f)) for f in p.faces]
    s.parts.append(p)
    # Two overlapping lames down the upper arm.
    for k, (z, r) in enumerate(((28.4, 2.95), (26.3, 2.7))):
        s.parts.append(slab(f'pauldron_L_lame{k}', lambda u, v, z=z, r=r: (
            .4+r*math.cos(math.radians(-80+160*u)), 8.6+r*math.sin(math.radians(-80+160*u))*.35+(r*.95)*max(0, math.cos(math.radians(-80+160*u)))*0+1.55,
            z+1.1*v-.25*math.cos(math.radians(-80+160*u))), 10, 2, .26))
    # Trophy fangs riveted along the pauldron crest.
    for i in range(4):
        a = math.radians(-50+33*i)
        base = (c[0]+2.9*math.cos(a)*.55, c[1]+1.3, c[2]+2.35+.1*i)
        s.strand(f'pauldron_fang{i}', [(*base, .3), (base[0]-.15, base[1]+.55, base[2]+1.1, .16), (base[0]-.35, base[1]+.8, base[2]+1.75, .03)], 'bone', 7, 2)


def belt_and_kilt(s):
    s.parts.append(loop_tube('belt', (-.55, 0), (3.85, 5.0), lambda a: 22.3+.12*math.sin(2*a), .55, 40, 6))
    s.oval('belt_buckle', (3.62, 0, 22.3), (.45, 1.25, 1.0), 'bone', 14, 8)
    # Layered hide flaps; the front flap sits between the thighs.
    for k, (a0, width, length) in enumerate(((0, 1.35, 7.4), (62, 2.1, 6.4), (-62, 2.1, 6.4),
                                             (100, 2.2, 7.0), (-100, 2.2, 7.0), (140, 2.3, 6.8), (-140, 2.3, 6.8), (180, 2.4, 6.6))):
        a = math.radians(a0)
        out = (math.cos(a), math.sin(a), 0); side = (-math.sin(a), math.cos(a), 0)
        def fn(u, v, a=a, out=out, side=side, width=width, length=length):
            flare = .55+1.5*v
            base = (-.55+(3.95+flare)*math.cos(a), (5.1+flare)*math.sin(a), 22.0-length*v+.35*math.sin(u*9+k)*v)
            return add(base, mul(side, (u-.5)*width*(1+.25*v)))
        s.parts.append(slab(f'kilt_{k}', fn, 3, 4, .24))


def trophy_skull(s):
    c = (1.2, 5.75, 20.4)
    s.oval('trophy_skull', c, (1.05, .9, .95), 'bone', 12, 8)
    s.oval('trophy_snout', (c[0]+1.15, c[1]+.1, c[2]-.35), (.95, .55, .5), 'bone', 10, 6)
    for sign in (-1, 1):
        s.oval(f'trophy_eye_{sign}', (c[0]+.72, c[1]+sign*.42, c[2]+.1), (.28, .26, .28), 'dark', 8, 5)
    s.strand('trophy_cord', [(c[0]-.4, c[1]-.2, c[2]+.9, .12), (c[0]-.2, c[1]-.5, c[2]+1.6, .12), (.4, 5.2, 22.1, .1)], 'accent', 6, 2)


def wraps(s):
    d = dict((n, v) for n, p, v in SPECS_G)
    for side in ('L', 'R'):
        lo, en = d[f'arm_{side}_lower'], d[f'arm_{side}_end']
        s.strand(f'bracer_{side}', [(*lerp(lo, en, .2), 2.27), (*lerp(lo, en, .55), 2.18), (*lerp(lo, en, .88), 1.78)], 'cloth', 16, 3)
        kn, an = d[f'leg_{side}_lower'], d[f'leg_{side}_end']
        calf = add(lerp(kn, an, .35), (-.45, 0, 0))
        s.strand(f'shin_wrap_{side}', [(*lerp(kn, calf, .45), 2.35), (*calf, 2.43), (*lerp(calf, an, .7), 1.78)], 'cloth', 16, 3)


def spear(s):
    W = unit(cross(D_REST, (0, 0, 1))); T = unit(cross(D_REST, W))
    s.strand('spear_shaft', [(*along(-16.8), .5), (*along(-6), .56), (*along(4), .56), (*along(16.4), .5)], 'wood', 12, 3)
    s.strand('spear_butt', [(*along(-17.6), .3), (*along(-17.2), .66), (*along(-16.2), .62)], 'bone', 10, 2)
    s.strand('spear_socket', [(*along(15.9), .6), (*along(16.9), .7), (*along(17.9), .55)], 'bone', 12, 2)
    # Broad leaf blade faces the frontal camera; penetration stays Brogue-owned.
    blade = [GRIP, (17.7, .45, .34), (18.8, 1.25, .36), (20.3, 1.62, .3), (22.0, 1.3, .24), (23.6, .62, .15), (24.6, .05, .05)]
    s.parts.append(diamond_loft('spear_blade', blade, (D_REST, W, T)))
    for sign in (-1, 1):
        s.parts.append(diamond_loft(f'spear_lug_{sign}', [add(along(17.6), mul(W, sign*.55)), (0, .32, .2), (.35, .3, .2), (1.2, .12, .08)],
                                    (unit(add(mul(W, sign), mul(D_REST, -.25))), D_REST, T)))
    # One continuous cord binding (painted twist) below the pennant.
    s.strand('spear_lashing', [(*along(10.7), .62), (*along(11.6), .7), (*along(12.6), .62)], 'accent', 12, 3)
    # Blue war pennant flies outward-back so both front and side views read it.
    F = PENNANT_DIR
    def fn(u, v):
        top = 15.4-1.5*u; bottom = 11.0+1.1*u
        t = bottom+(top-bottom)*v
        ripple = .45*math.sin(u*math.pi*2.2+.4)*u
        N = unit(cross(D_REST, F))
        return add(along(t), add(mul(F, .45+9.6*u), mul(N, ripple)))
    s.parts.append(slab('pennant', fn, 12, 4, .22))


def build_parts():
    s = Sculpt()
    s.oval('pelvis', (0, 0, 20), (3.9, 5.0, 3.6))
    s.parts.append(torso())
    head_parts(s)
    limbs(s)
    helm(s)
    s.parts.append(mantle())
    s.parts.append(cape())
    pauldron(s)
    belt_and_kilt(s)
    trophy_skull(s)
    wraps(s)
    spear(s)
    for p in s.parts:
        if not getattr(p, 'local', False): local_uv(p)
        p.vertices = [sc(v) for v in p.vertices]
        p.uv = [(round(u, 6), round(v, 6)) for u, v in p.uv]
    names = [p.name for p in s.parts]
    if len(set(names)) != len(names): raise ValueError('Duplicate warlord part names')
    return s.parts


# ---------------------------------------------------------------- skinning
def blend_chain(v, names, k=.3):
    """Joint-centred blending: neighbouring bones share 50/50 at each joint."""
    ids = [IDS[n] for n in names]; best = None
    for s_i, (a, b) in enumerate(zip(ids, ids[1:])):
        start, end = REST[a], REST[b]; d = sub(end, start)
        t = max(0, min(1, dot(sub(v, start), d)/dot(d, d)))
        dist = math.dist(v, add(start, mul(d, t)))
        if best is None or dist < best[0]: best = (dist, s_i, t)
    _, s_i, t = best
    w = {}
    own = ids[s_i]; nxt = ids[s_i+1]; prv = ids[s_i-1] if s_i > 0 else None
    to_next = .5*smooth((t-(1-k))/k)
    if s_i == len(ids)-2 and not names[-1].endswith(('end', 'head')): to_next = 0
    to_prev = .5*smooth((k-t)/k) if prv is not None else 0
    w[own] = 1-to_next-to_prev
    if to_next: w[nxt] = w.get(nxt, 0)+to_next
    if to_prev: w[prv] = w.get(prv, 0)+to_prev
    return quantize(w)


def quantize(w):
    items = sorted(((b, x) for b, x in w.items() if x > 1e-6), key=lambda e: (-e[1], e[0]))[:4]
    total = sum(x for b, x in items)
    out = [(b, round(x/total, 6)) for b, x in items[:-1]]
    out.append((items[-1][0], round(1-sum(x for b, x in out), 6)))
    return out


RIGID = (('helm', 'head'), ('crest', 'head'), ('head_', 'head'), ('jaw', 'jaw'), ('mantle', 'spine'),
         ('cape', 'cape'), ('pauldron', 'arm_L_upper'), ('bracer_L', 'arm_L_lower'), ('bracer_R', 'arm_R_lower'),
         ('shin_wrap_L', 'leg_L_lower'), ('shin_wrap_R', 'leg_R_lower'), ('belt', 'pelvis'), ('kilt', 'pelvis'),
         ('trophy', 'pelvis'), ('spear', 'spear'), ('pennant', 'pennant'))


def weights(part, v, uv):
    name = part.name
    if name == 'head_cranium' or name.startswith(('head_ear', 'head_brow')):
        t = smooth((v[2]/S-34.6)/1.4)
        return quantize({IDS['head']: t, IDS['neck']: 1-t})
    if name.startswith(('hand_', 'foot_')):
        limb = 'arm' if name.startswith('hand') else 'leg'
        return [(IDS[f'{limb}_{name.split("_")[1]}_end'], 1)]
    if name.startswith('shoulder_'):
        side = name[-1]; g = abs(v[1])/S
        t = smooth((g-3.2)/4.2)
        return quantize({IDS['spine']: 1-t, IDS[f'arm_{side}_upper']: t})
    if name.startswith(('arm_', 'leg_')):
        return blend_chain(v, [name+'_'+j for j in ('upper', 'lower', 'end')], .28)
    for prefix, bone in RIGID:
        if name.startswith(prefix): return [(IDS[bone], 1)]
    if name == 'pelvis': return [(IDS['pelvis'], 1)]
    return blend_chain(v, ('pelvis', 'spine', 'neck', 'head'), .35)


# ---------------------------------------------------------------- posing
def compose(rot, shift):
    return [(*add(local, shift[i]), *rot[i], 1, 1, 1) for i, (n, p, local) in enumerate(BONES)]


def world(rot, shift): return RIG.matrices(compose(rot, shift))


def solve_leg(rot, shift, side, target):
    T = world(rot, shift)
    ids = [IDS[f'leg_{side}_{j}'] for j in ('upper', 'lower', 'end')]
    qp = T[IDS['pelvis']][1]; hip = T[ids[0]][0]
    av = sub(REST[ids[1]], REST[ids[0]]); bv = sub(REST[ids[2]], REST[ids[1]])
    a, b = math.hypot(*av), math.hypot(*bv)
    d = sub(target, hip); dist = min(a+b-.001, max(abs(a-b)+.001, math.hypot(*d))); n = unit(d)
    knee_dir = rotate(qp, av)
    pole = unit(sub(knee_dir, mul(n, dot(knee_dir, n))))
    along_ = (a*a-b*b+dist*dist)/(2*dist)
    knee = add(hip, add(mul(n, along_), mul(pole, math.sqrt(max(0, a*a-along_*along_)))))
    foot = add(hip, mul(n, dist))
    Wu = qmul(between(rotate(qp, av), sub(knee, hip)), qp)
    Wl = qmul(between(rotate(Wu, bv), sub(foot, knee)), Wu)
    rot[ids[0]] = qmul(inverse(qp), Wu); rot[ids[1]] = qmul(inverse(Wu), Wl)
    rot[ids[2]] = qmul(inverse(Wl), qp)   # keep the sole parallel to the pelvis frame


def perp(v, n): return sub(v, mul(n, dot(v, n)))


def twist_about(q, direction):
    """Twist component of q about a unit direction (swing-twist split)."""
    p = dot(q[:3], direction)
    t = (*mul(direction, p), q[3]); n = math.sqrt(dot(t, t))
    return (0, 0, 0, 1) if n < 1e-9 else tuple(x/n for x in t)


def scale_rotation(q, k):
    if q[3] < 0: q = tuple(-x for x in q)
    angle = 2*math.acos(max(-1, min(1, q[3]))); s = math.sin(angle/2)
    if s < 1e-9: return (0, 0, 0, 1)
    return axis(tuple(x/s for x in q[:3]), angle*k)


def arm_frame(rot, shift, side):
    T = world(rot, shift)
    ids = [IDS[f'arm_{side}_{j}'] for j in ('upper', 'lower', 'end')]
    av = sub(REST[ids[1]], REST[ids[0]]); bv = sub(REST[ids[2]], REST[ids[1]])
    return T, ids, av, bv


def hand_orientation(rot, shift, side, rest_axis, direction, target, hint):
    """Choose the twist about the held axis that lets the forearm meet the hand.

    The forearm direction that would give a straight wrist is rotate(Q, rest
    forearm); pick the twist whose implied elbow is reachable and on the hinted
    side. Coarse deterministic scan plus golden refinement keeps it continuous.
    """
    T, ids, av, bv = arm_frame(rot, shift, side)
    shoulder = T[ids[0]][0]; a, b = math.hypot(*av), math.hypot(*bv); f = unit(bv)
    base = between(rest_axis, direction); axis_ = unit(direction)
    def cost(theta):
        q = qmul(axis(axis_, theta), base)
        elbow = sub(target, mul(rotate(q, f), b)); d = sub(elbow, shoulder)
        return ((math.hypot(*d)-a)/a)**2+.35*(1-dot(unit(d), hint))
    thetas = [math.tau*i/72 for i in range(72)]
    best = min(thetas, key=lambda x: (round(cost(x), 12), x))
    lo, hi = best-math.tau/72, best+math.tau/72; g = (math.sqrt(5)-1)/2
    for _ in range(30):
        c, d = hi-g*(hi-lo), lo+g*(hi-lo)
        if cost(c) < cost(d): hi = d
        else: lo = c
    return qmul(axis(axis_, (lo+hi)/2), base)


def solve_arm(rot, shift, side, target, hint, hand):
    T, ids, av, bv = arm_frame(rot, shift, side)
    qp = T[IDS['spine']][1]; shoulder = T[ids[0]][0]
    a, b = math.hypot(*av), math.hypot(*bv)
    d = sub(target, shoulder); dist = min(a+b-.001, max(abs(a-b)+.001, math.hypot(*d))); n = unit(d)
    ideal = sub(sub(target, mul(rotate(hand, unit(bv)), b)), shoulder)
    pole = perp(ideal, n)
    if math.hypot(*pole) < 1e-6: pole = perp(hint, n)
    bend = unit(add(unit(pole), mul(unit(perp(hint, n)), .25)))
    along_ = (a*a-b*b+dist*dist)/(2*dist)
    elbow = add(shoulder, add(mul(n, along_), mul(bend, math.sqrt(max(0, a*a-along_*along_)))))
    wrist = add(shoulder, mul(n, dist))
    Wu = qmul(between(rotate(qp, av), sub(elbow, shoulder)), qp)
    Wl = qmul(between(rotate(Wu, bv), sub(wrist, elbow)), Wu)
    # Move most forearm twist (pronation) out of the wrist into the forearm.
    residual = qmul(inverse(Wl), hand)
    pron = scale_rotation(twist_about(residual, unit(bv)), .7)
    Wl = qmul(Wl, pron)
    rot[ids[0]] = qmul(inverse(qp), Wu); rot[ids[1]] = qmul(inverse(Wu), Wl)
    rot[ids[2]] = qmul(inverse(Wl), hand)


def G(p): return sc(p)


FEET = {side: G((2.2, sign*4.6, 2.4)) for side, sign in (('L', 1), ('R', -1))}
# (wrist target, elbow hint, held-axis direction)
AKIMBO = (G((.9, 9.2, 23.4)), unit((-.8, .6, 0)), unit((.1, -.8, -.6)))
IDLE_SPEAR = (G((6.2, -10.2, 22.6)), unit((-.4, -.7, -.2)), (.16, -.1, 1))


def finish_arms(rot, shift, spear, left=None):
    for side, rest_axis, (target, hint, direction) in (('L', (0, 0, -1), left or AKIMBO), ('R', D_REST, spear)):
        hand = hand_orientation(rot, shift, side, rest_axis, direction, target, hint)
        solve_arm(rot, shift, side, target, hint, hand)


def turn(rot, bone, direction, degrees, after=True):
    q = axis(direction, math.radians(degrees))
    rot[IDS[bone]] = qmul(rot[IDS[bone]], q) if after else qmul(q, rot[IDS[bone]])


def pose(name, t):
    if name == 'death': return death(t)
    return compose(*_pose(name, t))


def _pose(name, t):
    rot = [(0, 0, 0, 1) for _ in BONES]; shift = [(0, 0, 0) for _ in BONES]
    phase = math.tau*t
    spear = IDLE_SPEAR; left = AKIMBO
    feet = dict(FEET)
    if name == 'idle':
        breath = math.sin(phase)
        turn(rot, 'spine', (0, 1, 0), 1.2*breath); turn(rot, 'neck', (0, 0, 1), 5*math.sin(phase+.6))
        turn(rot, 'head', (0, 1, 0), -1.5*breath)
        shift[IDS['pelvis']] = (0, 0, -.12*S+.08*S*math.cos(phase))
        spear = (add(spear[0], (0, 0, .25*breath)), spear[1], spear[2])
        turn(rot, 'cape', (0, 1, 0), 2*math.sin(phase+1))
        turn(rot, 'pennant', D_REST, 16*math.sin(2*phase))
    elif name == 'walk':
        shift[IDS['pelvis']] = (0, 0, -.35*S+.28*S*math.cos(2*phase))
        for side, offset in (('L', 0), ('R', math.pi)):
            p = phase+offset
            feet[side] = add(FEET[side], (-4.2*S*math.cos(p), 0, 2.9*S*max(0, math.sin(p))))
        turn(rot, 'spine', (0, 0, 1), 4*math.cos(phase)); turn(rot, 'neck', (0, 0, 1), -3*math.cos(phase))
        turn(rot, 'spine', (0, 1, 0), 3)
        spear = (add(spear[0], (1.3*S*math.cos(phase+math.pi), 0, .4*S*math.sin(2*phase))), spear[1],
                 add(spear[2], (.18*math.cos(phase+math.pi), 0, 0)))
        turn(rot, 'cape', (0, 1, 0), -7-4*math.cos(2*phase))
        turn(rot, 'pennant', D_REST, 22*math.sin(2*phase+.5))
    elif name in ('thrust', 'cleave'):
        # Key pose is held around the middle frame (galleries sample it).
        wind = smooth(t/.22)*(1-smooth((t-.22)/.2))
        strike = smooth((t-.28)/.15)*(1-smooth((t-.66)/.34))
        shift[IDS['pelvis']] = (1.7*S*strike-.6*S*wind, 0, -1.3*S*strike-.3*S*wind)
        turn(rot, 'jaw', (0, 1, 0), 28*strike+6*wind)
        turn(rot, 'pennant', D_REST, 30*math.sin(phase*1.5)*(wind+strike))
        turn(rot, 'cape', (0, 1, 0), -10*strike+6*wind)
        if name == 'thrust':
            # Torso yaw and spear angle sit off the 3/4 camera axis on purpose.
            turn(rot, 'spine', (0, 0, 1), -16*wind+27*strike); turn(rot, 'spine', (0, 1, 0), -4*wind+12*strike)
            turn(rot, 'head', (0, 0, 1), 4*wind-16*strike); turn(rot, 'head', (0, 1, 0), -10*strike)
            keys = ((wind, (G((-1.0, -12.5, 27.5)), unit((-.5, -.8, -.2)), (.5, .05, .87))),
                    (strike, (G((5.6, -7.8, 25.5)), unit((-.3, -.9, -.2)), (.85, .45, .12))))
        else:
            # Overhead war-cry raise is held across the middle frame: spear arm
            # fully extended above the helm, chest arched, roaring jaw, wide
            # stance, flared cloak. The chop lands after it. Cosmetic only: not
            # a summon or war-cry event.
            wind = smooth(t/.34)*(1-smooth((t-.62)/.12))
            strike = smooth((t-.62)/.12)*(1-smooth((t-.78)/.22))
            shift[IDS['pelvis']] = (1.5*S*strike-.4*S*wind, 0, -1.2*S*strike-.9*S*wind)
            for side, sign in (('L', 1), ('R', -1)):
                feet[side] = add(FEET[side], (sign*.6*S*wind, sign*2.2*S*wind, 0))
            rot[IDS['jaw']] = axis((0, 1, 0), math.radians(40*wind+18*strike))
            rot[IDS['cape']] = axis((0, 1, 0), math.radians(30*wind-6*strike))
            turn(rot, 'spine', (0, 0, 1), -6*wind+26*strike); turn(rot, 'spine', (0, 1, 0), -17*wind+18*strike)
            turn(rot, 'neck', (0, 1, 0), -8*wind); turn(rot, 'head', (0, 1, 0), -20*wind-6*strike)
            turn(rot, 'head', (0, 0, 1), -14*strike)
            left = (lerp(AKIMBO[0], G((2.2, 12.8, 30.5)), wind), unit(lerp(AKIMBO[1], (-.3, .6, -.7), wind)),
                    unit(lerp(AKIMBO[2], (.1, .8, .55), wind)))
            keys = ((wind, (G((1.4, -6.4, 42.8)), unit((-.2, -.95, .1)), (-.85, -.1, .3))),
                    (strike, (G((7.4, -4.0, 24.0)), unit((-.3, -.9, -.2)), (.68, .5, -.53))))
        target, hint, direction = spear
        for w, (kt, kh, kd) in keys:
            target = lerp(target, kt, w); hint = lerp(hint, kh, w); direction = lerp(direction, kd, w)
        spear = (target, unit(hint), direction)
    elif name == 'recoil':
        pulse = math.sin(math.pi*t)**2
        turn(rot, 'spine', (0, 1, 0), -15*pulse); turn(rot, 'spine', (1, 0, 0), 6*pulse)
        turn(rot, 'head', (0, 1, 0), -14*pulse); turn(rot, 'head', (0, 0, 1), -12*pulse)
        turn(rot, 'jaw', (0, 1, 0), 14*pulse)
        shift[IDS['pelvis']] = (-1.4*S*pulse, 0, -.7*S*pulse)
        spear = (lerp(spear[0], G((3.5, -11.5, 25.5)), pulse), spear[1], lerp(spear[2], (-.1, -.3, 1), pulse))
        left = (lerp(AKIMBO[0], G((2.5, 11.4, 25.5)), pulse), AKIMBO[1], AKIMBO[2])
        turn(rot, 'cape', (0, 1, 0), 8*pulse)
    for side in ('L', 'R'): solve_leg(rot, shift, side, feet[side])
    finish_arms(rot, shift, spear, left)
    return rot, shift


DEATH_ROOT = (0, 28.4, 8.8)
DEATH_ROLL = -60
DEATH_CAPE = 60
DEATH_HEAD = 14
# Limp targets: upper-arm directions in the torso frame chosen so that, once the
# body lies on its right side rolled face-up, both arms rest on the floor; then
# slack bends. Legs flatten with loose, slightly parted knees.
DEATH_ARMS = {'L': ((-.9, .38, -.2), -22), 'R': ((.5, -.85, -.2), -18)}
DEATH_LEGS = {'L': (-14, 24, 6), 'R': (-4, 12, -5)}


def death(t):
    rot, shift = _pose('idle', 0)
    buckle = smooth(t/.35)*(1-smooth((t-.3)/.3)); fall = smooth((t-.18)/.6); slump = smooth((t-.5)/.5)
    # Knees give first, then the body topples onto its right side and goes slack.
    shift[IDS['pelvis']] = add(shift[IDS['pelvis']], (0, 0, -3.0*S*buckle))
    for side in ('L', 'R'): solve_leg(rot, shift, side, FEET[side])
    for side, (direction, elbow) in DEATH_ARMS.items():
        up, lo, en = [IDS[f'arm_{side}_{j}'] for j in ('upper', 'lower', 'end')]
        limp = between(unit(sub(REST[lo], REST[up])), unit(direction))
        rot[up] = slerp(rot[up], limp, fall)
        rot[lo] = slerp(rot[lo], axis((0, 1, 0), math.radians(elbow)), fall)
        rot[en] = slerp(rot[en], axis((0, 1, 0), math.radians(20)), fall)
    for side, (hip, knee, spread) in DEATH_LEGS.items():
        ids = [IDS[f'leg_{side}_{j}'] for j in ('upper', 'lower', 'end')]
        rot[ids[0]] = slerp(rot[ids[0]], qmul(axis((1, 0, 0), math.radians(spread)), axis((0, 1, 0), math.radians(hip))), fall)
        rot[ids[1]] = slerp(rot[ids[1]], axis((0, 1, 0), math.radians(knee)), fall)
        rot[ids[2]] = slerp(rot[ids[2]], axis((0, 1, 0), math.radians(-25)), fall)
    rot[IDS['root']] = qmul(axis((0, 1, 0), math.radians(DEATH_ROLL*fall)), axis((1, 0, 0), math.radians(90*fall)))
    shift[0] = (DEATH_ROOT[0]*fall, DEATH_ROOT[1]*fall, DEATH_ROOT[2]*fall*S)
    turn(rot, 'spine', (0, 1, 0), 10*fall); turn(rot, 'spine', (0, 0, 1), -8*slump)
    turn(rot, 'neck', (1, 0, 0), 16*slump); turn(rot, 'head', (1, 0, 0), 24*slump); turn(rot, 'head', (0, 1, 0), DEATH_HEAD*slump)
    turn(rot, 'jaw', (0, 1, 0), 26*slump+8*buckle)
    turn(rot, 'cape', (1, 0, 0), DEATH_CAPE*fall)
    rot[IDS['pennant']] = slerp(rot[IDS['pennant']], (0, 0, 0, 1), fall)
    # The released spear drops flat in front of the body.
    T = world(rot, shift)
    hand_q = T[IDS['arm_R_end']][1]; hand_p = T[IDS['arm_R_end']][0]
    floor_dir = unit((.08, 1, 0))
    q_floor = between(D_REST, floor_dir)
    # Twist about the shaft so the pennant lies flat, not upright.
    n_after = rotate(q_floor, unit(cross(D_REST, PENNANT_DIR)))
    ang = math.atan2(dot(cross(n_after, (0, 0, 1)), floor_dir), dot(n_after, (0, 0, 1)))
    q_floor = qmul(axis(floor_dir, ang), q_floor)
    q_world = slerp(hand_q, q_floor, fall)
    floor_grip = (26.0, 1.0, .98)
    grip = sub(floor_grip, rotate(q_floor, sub(G(GRIP), REST[IDS['spear']])))
    p_world = add(lerp(hand_p, grip, fall), (0, 0, 7*S*math.sin(math.pi*fall)))
    rot[IDS['spear']] = qmul(inverse(hand_q), q_world)
    local = rotate(inverse(hand_q), sub(p_world, hand_p))
    shift[IDS['spear']] = sub(local, BONES[IDS['spear']][2])
    return compose(rot, shift)


def slerp(a, b, t):
    d = dot(a, b)
    if d < 0: b = tuple(-x for x in b); d = -d
    if d > .9995: return unit4(tuple(x+(y-x)*t for x, y in zip(a, b)))
    th = math.acos(d); s = math.sin(th)
    return tuple((math.sin((1-t)*th)*x+math.sin(t*th)*y)/s for x, y in zip(a, b))


def unit4(q):
    n = math.sqrt(dot(q, q)); return tuple(x/n for x in q)


# ---------------------------------------------------------------- export
def geometry():
    from .connected_skin import attach
    parts = attach('goblin_chieftan', build_parts(), weights)
    return assemble(materials.islands(parts), weights)


def matrices(frame): return RIG.matrices(frame)
def deform(v, w, frame): return RIG.deform(v, w, frame)
def animation_data(v, w): return sample_clips(RIG, CLIPS, pose, v, w)


def texture_bytes():
    from .connected_skin import attach
    return materials.texture_bytes(attach('goblin_chieftan', build_parts(), weights))


def build():
    skin = texture_bytes(); (ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts, v, n, uv, t, w = geometry(); clips, bounds = animation_data(v, w)
    data = iqm.encode(v, n, uv, t, w, BONES, clips, bounds, mesh_label='Project_Broom_goblin_chieftan', material_path=SKIN)
    path = ROOT/MODEL; path.write_bytes(data)
    manifest = dict(schemaVersion=1, workId='BRG-M51', format='IQM v2', runtimeModel=path.relative_to(ROOT).as_posix(),
                    sha256=hashlib.sha256(data).hexdigest(), skin=SKIN, skinSha256=hashlib.sha256(skin).hexdigest(),
                    dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v), 4) for a in range(3)],
                    parts=len(parts), vertices=len(v), triangles=len(t), boneCount=len(BONES),
                    bones=[dict(name=n, parent=p, local=v) for n, p, v in BONES],
                    clips=[{k: v for k, v in c.items() if k != 'frames'} | dict(frameCount=len(c['frames'])) for c in clips],
                    poseBounds=bounds, authoringSource='assets/monsters/goblin_chieftan/goblin-chieftan-animated.blend')
    out = ROOT/'assets/monsters/goblin_chieftan'; out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    # Re-import under the package name so connected_skin finds CONNECTED_SKIN.
    from tools.monster_models import goblin_chieftan_animation as module
    print(module.build()['sha256'])

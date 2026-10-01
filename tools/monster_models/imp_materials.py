"""Original imp materials. No gameplay meaning; nothing emits light.

2048-square atlas. The connected skin is painted per triangle from continuous
rest positions, normals and bone-weight fractions (left half, 16-pixel islands
in spatial order), so the face, torso, limbs and tail carry no source-part
colour seams. Accessories use the right half (256-pixel role cells).

Paint targets the engine's flat bright light: baked top/front light, painted
occlusion and a subtle specular sheen, and a deliberately wide value range. A
deep rose-crimson body (a nod to Brogue's pink glyph colour, not a literal
material claim) has lighter lit planes and painted anatomy, and grades to
near-black maroon at the hands, feet, tail tip and horn bases. Dark goat legs
carry a lighter rose rim on the thigh and shin fronts so they separate from
dark floors. Ivory horns, spurs and claws and narrow gold eyes under heavy
lids keep the silhouette and face readable at 128 and 192 units. Brogue's IMP_LIGHT stays
Brogue's; this skin adds no emission, glow or light.
"""
import math

from .pixie_materials import hash3, vnoise, encode_png, mix, clamp, smooth, scale, gauss

SKIN = 'graphics/BRGIMP.png'
SIZE = 2048
ROLES = ('eye', 'horn', 'finger', 'claw', 'tooth', 'lid', 'spur', 'spare')
RECTS = {n: (1024+i % 4*256+8, i//4*256+8, 1024+i % 4*256+248, i//4*256+248) for i, n in enumerate(ROLES)}
SKIN_ISLANDS = 8192

# ---------------------------------------------------------------- palette
ROSE = (188, 40, 72)
ROSE_HI = (246, 128, 140)
DEEP = (56, 5, 22)
MAROON = (32, 3, 14)
FUR = (20, 6, 13)
FUR_HI = (74, 26, 42)
RIM = (176, 62, 92)
IVORY = (238, 222, 180)
AMBER = (255, 190, 40)
INK = (18, 4, 12)


def role(n):
    if n.startswith('eye_'): return 'eye'
    if n.startswith('horn_'): return 'horn'
    if n.startswith(('finger_', 'thumb_')): return 'finger'
    if n.startswith(('claw_', 'toe_claw_')): return 'claw'
    if n.startswith('tooth_'): return 'tooth'
    if n.startswith('lid_'): return 'lid'
    if n.startswith(('spur_', 'spike_')): return 'spur'
    return 'skin'


def repack(parts):
    for p in parts:
        r = role(p.name)
        if r == 'skin': continue
        x0, y0, x1, y1 = RECTS[r]
        p.uv = [(round((x0+u*(x1-x0))/SIZE, 7), round(1-(y0+v*(y1-y0))/SIZE, 7)) for u, v in p.uv]
    return parts


def local_uv(name, uv):
    x0, y0, x1, y1 = RECTS[role(name)]
    return ((uv[0]*SIZE-x0)/(x1-x0), ((1-uv[1])*SIZE-y0)/(y1-y0))


# ---------------------------------------------------------------- accessories
def shade(name, u, v):
    """u, v are the part's own tube/blob parameters (tube: u along, v around)."""
    if name == 'eye':
        # Blob latitude v: 0 back pole .. 1 front pole; u: angle from the up axis.
        # A vertical slit pupil in a gold iris hot at the centre, dark at the rim.
        if v > .6:
            lateral = math.sin(math.pi*v)*abs(math.sin(math.tau*u))
            k = (v-.6)/.4
            c = mix((150, 60, 6), (255, 196, 36), k**.6)
            c = mix(c, (255, 244, 150), .55*smooth((k-.7)/.25))
            c = scale(c, .88+.12*math.sin(u*math.tau*20))
            if v > .8 and lateral < .1: return INK
            return mix(c, (50, 8, 2), smooth((.66-v)/.05))
        return (46, 8, 8)
    if name == 'lid':
        # Heavy rose-maroon lid; the rim facing the eye (u near 0.5, lower edge) is a dark lash line.
        rim = gauss(min(abs(u-.5), 1), .12)*smooth((v-.45)/.2)
        c = mix((150, 34, 62), (90, 12, 36), smooth((.8-v)/.4))
        c = mix(c, (225, 110, 128), .3*gauss(min(u, 1-u), .12)*smooth((v-.5)/.3))
        return mix(c, (16, 2, 8), .9*rim)
    if name in ('horn', 'spur'):
        # u: root 0 .. tip 1. Near-black maroon root grading to ridged ivory and a pale tip.
        ridge = .5+.5*math.sin(u*(62 if name == 'horn' else 30))
        c = mix((30, 4, 12), (120, 70, 60), smooth((u-.02)/.2))
        c = mix(c, IVORY, smooth((u-.18)/.4))
        c = scale(c, .8+.2*ridge*(1-u*.6))
        top = .5+.5*math.cos(v*math.tau)
        return mix(c, (255, 250, 232), .35*top**6*smooth((u-.2)/.3))
    if name == 'finger':
        c = mix(DEEP, (24, 3, 10), smooth(u*1.2))
        knuckle = gauss(abs(math.sin(u*math.pi*2.5)), .15)
        return scale(c, .85+.2*knuckle)
    if name == 'claw':
        c = mix((80, 50, 44), IVORY, smooth((u-.1)/.45))
        top = .5+.5*math.cos(v*math.tau)
        return mix(c, (255, 252, 236), .45*top**5*smooth(u*2))
    if name == 'tooth':
        return mix((250, 244, 220), (200, 180, 140), smooth((u-.5)/.5)*.4)
    return (128, 128, 128)


def accessory_pixels(buffer):
    for name, (x0, y0, x1, y1) in RECTS.items():
        pad = 8
        for y in range(y0-pad, y1+pad):
            for x in range(x0-pad, x1+pad):
                if x < 1024 or x >= SIZE or y < 0 or y >= SIZE: continue
                u = clamp((x-x0)/(x1-x0)); v = clamp((y-y0)/(y1-y0))
                c = shade(name, u, v)
                o = (y*SIZE+x)*3
                buffer[o:o+3] = bytes(max(0, min(255, round(q))) for q in c)


# ---------------------------------------------------------------- skin
def fur_legs(point, normal, light):
    x, y, z = point
    nx, ny, nz = normal
    tuft = vnoise(x*2.2, y*2.2, z*1.1)+.6*vnoise(x*6, y*6, z*2.5)
    c = mix(FUR, FUR_HI, clamp(light**1.4*.8+.35*tuft))
    # Lighter rose rim on the fronts of thighs and shins so legs separate from dark floors.
    rim = smooth((nx-.25)/.45)*(.55+.45*smooth((nz+.2)/.6))
    return mix(c, RIM, .5*rim*(.8+.4*tuft))


def torso_anatomy(point, normal, c):
    """Painted pectorals, sternum, abdominals, ribs and collarbones (front),
    spine and shoulder blades (back), so bare skin does not read as cloth."""
    x, y, z = point
    nx, ny, nz = normal
    ay = abs(y)
    front = smooth((nx-.05)/.35)
    back = smooth((-nx-.05)/.35)
    dark = 0.
    lite = 0.
    # Pectoral lower edge and a highlight on the upper chest.
    edge = 24.7+.28*(ay-1.5)**2
    dark += .55*gauss(z-edge, .28)*smooth((3.2-ay)/.5)*front
    lite += .35*gauss(math.hypot(ay-1.6, z-26.0), 1.1)*front
    # Sternum groove and abdominal blocks.
    dark += .4*gauss(y, .22)*smooth((27-z)/.5)*smooth((z-19.8)/.4)*front
    for zz in (23.1, 21.9, 20.7):
        dark += .35*gauss(z-zz, .16)*smooth((1.5-ay)/.25)*front
    lite += .18*gauss(abs(math.sin((z-20.1)*2.6)), .5)*smooth((1.4-ay)/.3)*smooth((23.5-z)/.4)*smooth((z-19.9)/.3)*front
    dark += .7*gauss(math.hypot(y, z-19.55), .22)*front
    # Ribs along the flanks, collarbones, armpit and waist occlusion.
    ribs = gauss(abs(math.sin((z-21.4)*2.1)), .35)*smooth((ay-1.7)/.4)*smooth((26-z)/.6)*smooth((z-21.2)/.5)
    dark += .35*ribs*smooth((nx+.4)/.5)
    col = 27.7+.22*ay
    lite += .5*gauss(z-col, .16)*smooth((3.4-ay)/.4)*smooth((ay-.5)/.3)*front
    dark += .35*gauss(z-col+.35, .2)*smooth((3.4-ay)/.4)*front
    dark += .5*gauss(math.hypot(ay-3.3, z-26.4), .8)
    dark += .35*gauss(ay-2.3, .5)*gauss(z-21.6, 1.2)*(1-front*.5)
    # Back: spine ridge with knobs, shoulder blades, a dark dorsal stripe.
    knobs = gauss(y, .3)*(.5+.5*math.cos(z*4.2))
    dark += .6*back*gauss(y, .45)*smooth((z-18.5)/.5)
    lite += .35*back*knobs
    blade = gauss(math.hypot((ay-1.9)/1.1, (z-26.2)/1.6), 1.)
    lite += .3*back*blade
    dark += .45*back*gauss(math.hypot((ay-1.9)/1.1, (z-26.2)/1.6)-1., .18)
    c = mix(c, MAROON, clamp(dark))
    return mix(c, ROSE_HI, clamp(lite))


def skin_pigment(point, normal, m):
    """m: continuous bone-weight fractions (head, ear, arm, hand, leg, foot, torso, tail)."""
    from .imp_animation import HEAD_C, EYE_Y, EYE_Z, MOUTH, head_surface_x
    x, y, z = point
    nx, ny, nz = normal
    ay = abs(y)
    light = clamp(.36+.38*nz+.32*nx)
    c = mix(DEEP, ROSE, light**.8)
    # Lit planes, then a subtle specular sheen on up/forward-facing skin.
    c = mix(c, ROSE_HI, .5*smooth((nz*.7+nx*.5-.55)/.3))
    c = mix(c, (255, 206, 206), .3*gauss(nz*.6+nx*.6-1.05, .12))
    # Legs: near-black maroon goat fur from mid-thigh down, hooflike dark feet.
    leg = m['leg']+m['foot']
    if leg > .3:
        cover = smooth((leg-.35)/.3)*smooth((17.2-z+1.2*max(0, x))/1.6)
        if cover > 0:
            c = mix(c, fur_legs(point, normal, light), cover)
        c = mix(c, (20, 8, 14), .8*smooth((m['foot']-.5)/.3)*smooth((2.8-z)/1.2))
    # Torso: slightly paler belly, painted anatomy.
    if m['torso'] > .3 and m['head'] < .4:
        belly = smooth((nx-.25)/.4)*smooth((m['torso']-.4)/.3)*gauss(ay, 2.2)
        c = mix(c, (238, 128, 140), .35*belly)
        c = mix(c, torso_anatomy(point, normal, c), smooth((m['torso']-.35)/.3)*(1-smooth((m['arm']-.3)/.3)))
    dorsal = smooth((-nx-.15)/.4)
    if m['tail']+m['arm'] > .4 and m['head'] < .5:
        c = mix(c, MAROON, .55*dorsal*gauss(math.sin(z*1.3-x*.6), .5)*smooth((m['tail']+m['arm']-.4)/.3))
    # Arms: darkening forearms and hands, painted elbow and muscle shading.
    if m['arm'] > .4:
        # Forearms grade to near-black maroon hands.
        c = mix(c, DEEP, .55*smooth((m['hand']-.1)/.4))
        c = mix(c, (26, 3, 10), .85*smooth((m['hand']-.55)/.35))
        elbow = min(math.hypot(x+.6, ay-6.4, z-22.7), 9)
        c = mix(c, MAROON, .45*gauss(elbow, .9))
        c = mix(c, ROSE_HI, .25*gauss(z-25.5, 1.2)*smooth((nx+.2)/.5))
    # Tail: dark rings, dark spade with a rose edge.
    if m['tail'] > .5:
        ring = gauss(math.sin(-x*1.6), .35)
        c = mix(c, MAROON, .55*ring*smooth((-x-5)/2))
        # The tail darkens toward its tip; the spade is near black with a lit edge.
        c = mix(c, (30, 3, 12), .85*smooth((z-20.5)/4)*smooth((-x-10.5)/1.2))
        spade = smooth((z-25.8)/.5)*smooth((-x-10)/1)
        if spade > 0:
            c = mix(c, (22, 2, 9), spade*.9)
            c = mix(c, RIM, spade*.3*smooth((nz-.2)/.4))
    if m['head'] > .5:
        c = face_paint(point, normal, m, c, light)
    return c


def face_paint(point, normal, m, c, light):
    from .imp_animation import HEAD_C, EYE_Y, EYE_Z, MOUTH, head_surface_x
    x, y, z = point
    nx, ny, nz = normal
    ay = abs(y)
    front = smooth((nx-.1)/.45)
    if m['ear'] > .25:
        # Ears: dark crimson inner bowl with veins, rose rim and dark tip.
        inner = smooth((nx+.1)/.4)
        vein = gauss(math.sin(ay*3.2+z*1.1), .2)
        e = mix((160, 26, 70), (96, 8, 40), .5*vein)
        c = mix(c, e, .8*inner*smooth((m['ear']-.4)/.3))
        return mix(c, MAROON, .8*smooth((ay-8.4)/1.2))
    # Horn bases: near-black maroon where the horns seat.
    for sgn in (1, -1):
        c = mix(c, (24, 2, 10), .9*gauss(math.hypot(x-2.0, y-sgn*1.5, z-35.3), .95))
    # Sunken sockets (painted occlusion) slanted up at the outer corner.
    sy = ay-EYE_Y
    socket = gauss(math.hypot(sy/1.35, (z-EYE_Z-.3*sy)/.85), 1.)*front
    c = mix(c, (40, 3, 16), .85*socket)
    # Hard V brow: dark top; lit ridge; a dark pinch between the brows.
    brow = gauss(z-(EYE_Z+1.25-.4*(1.6-ay)), .32)*front*smooth((2.9-ay)/.6)
    c = mix(c, MAROON, .5*brow)
    c = mix(c, MAROON, .6*gauss(y, .25)*gauss(z-EYE_Z-.5, .45)*front)
    # Cheekbone highlights, hollow cheeks, a lit nose ridge, dark muzzle underside.
    c = mix(c, ROSE_HI, .5*gauss(math.hypot(ay-2.2, z-EYE_Z+1.15), .55)*front)
    c = mix(c, DEEP, .45*gauss(math.hypot(ay-2.0, z-EYE_Z+2.3), .6)*front)
    c = mix(c, DEEP, .5*smooth((-nz-.3)/.4)*smooth((32-z)/.8))
    # Sly smirk: a thin dark line curled up at the imp's left corner, lips parted
    # there over painted sharp teeth; a dimple of shadow at the raised corner.
    mx, mz0, half = MOUTH
    if nx > .05 and ay < half+.4:
        t = y/half
        line = mz0+.1*t+.5*max(0., t)**2
        d = z-line
        open_ = .28*smooth((t-.2)/.5)*smooth((1.05-t)/.2)
        inside = smooth((open_-abs(d+open_*.2))/.05)*(open_ > .02)
        teeth = smooth((d+.02)/.06)*smooth((abs(math.sin(y*7.5))-.25)/.15)
        c = mix(c, mix((24, 2, 8), (246, 236, 210), .9*teeth), inside)
        c = mix(c, (26, 3, 10), .9*gauss(d, .06+.02*abs(t))*smooth((half+.25-ay)/.2))
        c = mix(c, DEEP, .6*gauss(math.hypot(y-half-.1, z-line-.45), .22))
        c = mix(c, ROSE_HI, .3*gauss(d+.35, .12)*smooth((half-ay)/.4))
    return c


def island(index):
    return (index % 64)*16, (index//64)*16


def bake_atlas(parts, ids, fraction_groups, pigment, accessories, pixels, origin=(-20, -20, -2)):
    """Continuous rest pigment baked into padded per-triangle 16-pixel islands.

    Generic over the creature: parts[0] is the connected skin, ids maps bone
    names, fraction_groups maps pigment keys to bone names, pigment(point,
    normal, fractions) returns an RGB tuple and accessories(buffer) paints the
    right half. Islands are laid out in spatial (Morton) order.
    """
    from .rat import Part
    body = parts[0]
    normal = body.normals()
    groups = {k: {ids[b] for b in v if b in ids} for k, v in fraction_groups.items()}
    fractions = [{k: math.fsum(w for b, w in row if b in g) for k, g in groups.items()} for row in body.skin_weights]
    tris = list(body.triangles())
    assert len(tris) <= SKIN_ISLANDS, len(tris)
    def morton(t):
        c = [sum(body.vertices[i][k] for i in t)/3 for k in range(3)]
        q = [max(0, min(1023, int((c[k]-origin[k])*8))) for k in range(3)]
        code = 0
        for bit in range(10):
            for k in range(3):
                code |= ((q[k] >> bit) & 1) << (3*bit+k)
        return code, t
    tris = [t for _, t in sorted(morton(t) for t in tris)]
    if pixels:
        buffer = bytearray(SIZE*SIZE*3)
        accessories(buffer)
        cache = {}
    result = Part('Connected_skin')
    result.skin_weights = []
    result.skin_topology = []
    steps = 6
    for index, tri in enumerate(tris):
        x0, y0 = island(index)
        if pixels:
            P = [body.vertices[i] for i in tri]
            N = [normal[i] for i in tri]
            F = [fractions[i] for i in tri]
            lattice = {}
            for i in range(steps+1):
                for j in range(steps+1-i):
                    b, cc = i/steps, j/steps
                    a = 1-b-cc
                    key = tuple(round(a*P[0][k]+b*P[1][k]+cc*P[2][k], 5) for k in range(3))
                    frac = {k: round(a*F[0][k]+b*F[1][k]+cc*F[2][k], 4) for k in groups}
                    ck = (key, tuple(frac.values()))
                    if ck not in cache:
                        nn = [a*N[0][k]+b*N[1][k]+cc*N[2][k] for k in range(3)]
                        length = math.sqrt(sum(q*q for q in nn)) or 1
                        cache[ck] = pigment(key, [q/length for q in nn], frac)
                    lattice[i, j] = cache[ck]
            for dy in range(16):
                for dx in range(16):
                    bi = clamp((dx-2)/12)*steps
                    cj = clamp((dy-2)/12)*steps
                    if bi+cj > steps:
                        k = steps/(bi+cj)
                        bi, cj = bi*k, cj*k
                    i, j = min(int(bi), steps-1), min(int(cj), steps-1)
                    fi, fj = bi-i, cj-j
                    if i+j >= steps:
                        i, j = (i-1, j) if i > 0 else (i, j-1)
                        fi, fj = bi-i, cj-j
                    if fi+fj <= 1:
                        c00, c10, c01 = lattice[i, j], lattice[i+1, j], lattice[i, j+1]
                        color = [c00[k]+(c10[k]-c00[k])*fi+(c01[k]-c00[k])*fj for k in range(3)]
                    else:
                        c11 = lattice[i+1, j+1] if (i+1, j+1) in lattice else lattice[i+1, j]
                        c10, c01 = lattice[i+1, j], lattice[i, j+1]
                        gi, gj = 1-fi, 1-fj
                        color = [c11[k]+(c01[k]-c11[k])*gi+(c10[k]-c11[k])*gj for k in range(3)]
                    o = ((y0+dy)*SIZE+x0+dx)*3
                    buffer[o:o+3] = bytes(max(0, min(255, round(q))) for q in color)
        base = len(result.vertices)
        for i, (dx, dy) in zip(tri, ((2, 2), (14, 2), (2, 14))):
            result.vertices.append(body.vertices[i])
            result.uv.append(((x0+dx)/SIZE, 1-(y0+dy)/SIZE))
            result.skin_weights.append(body.skin_weights[i])
            result.skin_topology.append(body.skin_topology[i])
        result.faces.append((base, base+1, base+2))
    if pixels:
        return encode_png(buffer, SIZE, SIZE)
    return [result]+parts[1:]


FRACTIONS = {'head': ('head', 'ear_L', 'ear_R'), 'ear': ('ear_L', 'ear_R'),
             'arm': ('arm_L', 'forearm_L', 'hand_L', 'arm_R', 'forearm_R', 'hand_R'),
             'hand': ('hand_L', 'hand_R'),
             'leg': ('thigh_L', 'shin_L', 'foot_L', 'toes_L', 'thigh_R', 'shin_R', 'foot_R', 'toes_R'),
             'foot': ('foot_L', 'toes_L', 'foot_R', 'toes_R'), 'torso': ('pelvis', 'spine', 'chest', 'neck'),
             'tail': ('tail_0', 'tail_1', 'tail_2', 'tail_3', 'tail_4')}


def connected_atlas(parts, pixels=False):
    from .imp_animation import IDS
    return bake_atlas(parts, IDS, FRACTIONS, skin_pigment, accessory_pixels, pixels)

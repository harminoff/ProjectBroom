"""Goblin warlord atlas: continuous rest-position paint in per-triangle islands.

Every triangle (fused skin and war gear) gets a padded 16 px island laid out in
Morton order of its 3D centroid, so mip levels blend spatial neighbours. Paint
is evaluated from rest position, normal, a baked proximity occlusion term and
the part's own surface parameters; nothing is sampled from source-part UVs.
The fused goblin-brown skin therefore stays continuous across limb junctions.
Painted light, occlusion and specular pools compensate for UZDoom's flat light.
Blue (crest, cloak, pennant, eye paint) is the Brogue glyph identity cue only.
"""
import math
import struct
import zlib
from .rat import Part

SIZE = 2048
CELL = 16
GRID = SIZE//CELL
S = 1.15
ROLES = ('skin', 'iron', 'blade', 'bone', 'crest', 'fur', 'cloth', 'leather', 'hide', 'wood',
         'cord', 'dark', 'iris', 'face')
LIGHT = (.42, .28, .86)
HALF = (.62, .12, .78)


def role(name):
    if name == 'Connected_skin': return 'skin'
    if name.startswith(('spear_blade', 'spear_lug')): return 'blade'
    if name.startswith(('helm_dome', 'helm_rim', 'helm_nasal', 'pauldron_L', 'belt_buckle', 'spear_socket', 'spear_butt')):
        return 'bone' if name.startswith('pauldron_fang') else 'iron'
    if name.startswith(('helm_horn', 'pauldron_fang', 'jaw_tusk', 'trophy_skull', 'trophy_snout')): return 'bone'
    if name.startswith('crest'): return 'crest'
    if name == 'mantle': return 'fur'
    if name in ('cape', 'pennant'): return 'cloth'
    if name.startswith(('bracer', 'shin_wrap', 'belt')): return 'leather'
    if name.startswith('kilt'): return 'hide'
    if name == 'spear_shaft': return 'wood'
    if name.startswith(('spear_lashing', 'trophy_cord')): return 'cord'
    if name.startswith('head_eye_iris'): return 'iris'
    if name.startswith(('head_eye', 'head_nostril', 'jaw_mouth', 'trophy_eye')): return 'dark'
    if name.startswith(('head_ear_inner', 'jaw_lower')): return 'face'
    raise ValueError('Unassigned warlord material: '+name)


def dot(a, b): return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
def norm(a):
    n = math.sqrt(dot(a, a)) or 1.
    return (a[0]/n, a[1]/n, a[2]/n)
def clamp(x, lo=0., hi=1.): return lo if x < lo else hi if x > hi else x
def mix(a, b, t): return (a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t, a[2]+(b[2]-a[2])*t)
LIGHT = norm(LIGHT); HALF = norm(HALF)


def noise(p, f):
    """Trilinear value noise; deterministic integer lattice."""
    x, y, z = p[0]*f, p[1]*f, p[2]*f
    ix, iy, iz = math.floor(x), math.floor(y), math.floor(z)
    fx, fy, fz = x-ix, y-iy, z-iz
    fx, fy, fz = fx*fx*(3-2*fx), fy*fy*(3-2*fy), fz*fz*(3-2*fz)
    X0, X1 = ix*73856093, (ix+1)*73856093; Y0, Y1 = iy*19349663, (iy+1)*19349663
    Z0, Z1 = iz*83492791, (iz+1)*83492791
    def h(a, b, c):
        v = a ^ b ^ c; v = (v ^ (v >> 13))*1274126177 & 0xffffffff
        return ((v ^ (v >> 16)) & 1023)/1023.
    c000, c100, c010, c110 = h(X0, Y0, Z0), h(X1, Y0, Z0), h(X0, Y1, Z0), h(X1, Y1, Z0)
    c001, c101, c011, c111 = h(X0, Y0, Z1), h(X1, Y0, Z1), h(X0, Y1, Z1), h(X1, Y1, Z1)
    a0 = c000+(c100-c000)*fx; b0 = c010+(c110-c010)*fx
    a1 = c001+(c101-c001)*fx; b1 = c011+(c111-c011)*fx
    lo = a0+(b0-a0)*fy; hi = a1+(b1-a1)*fy
    return lo+(hi-lo)*fz


def segment_distance(p, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]
    t = clamp(((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy))
    return math.hypot(p[0]-a[0]-t*dx, p[1]-a[1]-t*dy), t


SCARS = (((-3.9*S, 35.2*S), (.9*S, 30.3*S)), ((-2.3*S, 33.4*S), (1.9*S, 29.6*S)), ((1.2*S, 38.2*S), (2.3*S, 35.0*S)))
BALDRIC = ((8.3*S, 33.0*S), (-5.2*S, 21.6*S))
HARNESS = ((-8.3*S, 33.0*S), (5.2*S, 21.6*S))
HANDS = ((4.9*S, -10.35*S, 18.8*S), (4.6*S, 10*S, 18.6*S))


def skin(p, n, occ):
    x, y, z = p; g = (x/S, y/S, z/S)
    base = (86, 73, 49)
    mott = noise(p, .9)-.5; fine = noise(p, 3.1)-.5
    head = clamp((g[2]-35.2)/1.2)
    face = head*clamp((n[0]-.05)/.4)*clamp((g[0]-2.2)/1.2)
    base = mix(base, (106, 88, 62), face)
    base = mix(base, (90, 76, 52), head*(1-face))
    for h in HANDS:
        d = math.dist(p, h)
        if d < 3.6*S:
            k = clamp((3.6*S-d)/(1.2*S))
            base = mix(base, (64, 50, 35), .75*k)
    if g[2] < 3.6: base = mix(base, (70, 56, 40), clamp((3.6-g[2])/1.5)*.8)
    col = (base[0]+22*mott+9*fine, base[1]+18*mott+8*fine, base[2]+12*mott+6*fine)
    # Painted anatomy for flat engine light: pec/ab separation, ribs, obliques,
    # lit deltoids, dark armpits, joint creases, darker extremities.
    front = clamp(n[0]*1.4)
    torso = clamp((g[2]-20.5)/1.5)*(1-head)
    ay = abs(g[1])
    arm = clamp((ay-6.6)/.8)
    body = torso*(1-arm)
    d = -34*math.exp(-((g[2]-31.1+.28*ay)/.7)**2-((ay-3.0)/2.3)**2)*front*body
    d += 14*math.exp(-((g[2]-32.2)/1.3)**2-((ay-2.9)/1.8)**2)*front*body
    d -= 22*math.exp(-(g[1]/.45)**2)*clamp((g[2]-27.3)/.6)*clamp((32.4-g[2])/.8)*front*body
    d -= 24*math.exp(-(g[1]/.4)**2)*clamp((g[2]-21.3)/.8)*clamp((27.6-g[2])/.6)*front*body
    for zz in (23.3, 25.4):
        d -= 16*math.exp(-((g[2]-zz)/.3)**2)*clamp((2.8-ay)/.4)*front*body
    d -= 16*math.exp(-((ay-2.7)/.35)**2)*clamp((g[2]-21)/.8)*clamp((27.2-g[2])/.8)*front*body
    side = clamp(abs(n[1])*1.3)
    ribs = max(0., math.sin((g[2]-24.2)*math.pi/1.05))*clamp((g[2]-24)/.5)*clamp((29.4-g[2])/.8)
    d -= 16*ribs*math.exp(-((ay-4.5)/.9)**2)*body*(.4+.6*side)
    d -= 20*math.exp(-((ay-4.4)/.8)**2-((g[2]-22.8)/1.6)**2)*body
    d -= 48*math.exp(-((ay-5.9)/.9)**2-((g[2]-27.4)/1.2)**2)*(1-head)
    d += 28*math.exp(-((ay-7.6)/1.7)**2-((g[2]-31.4)/1.7)**2)*clamp(n[2]+.45)*(1-head)
    d -= 18*math.exp(-((g[2]-36.2)/.35)**2)*face
    for jx, jy, jz, strength in ((2.0, 9.9, 25.4, 26), (4.6, 4.1, 11.2, 30)):
        dj = math.dist((g[0], ay, g[2]), (jx, jy, jz))
        crease = abs(math.sin(dj*4.2))**.5
        d -= strength*math.exp(-(dj/1.6)**2)*(.5+.5*crease)
    leg = clamp((20-g[2])/1.5)*clamp((g[2]-12.2)/1.)*(1-arm)
    d -= 20*math.exp(-((ay-4.2+.5*g[0]/3)/.45)**2)*front*leg
    d -= 22*clamp((2.9-ay)/1.2)*leg
    d += 12*math.exp(-((ay-5.4)/.9)**2)*clamp(n[2]+.6)*leg
    col = (col[0]+d, col[1]+d*.95, col[2]+d*.85)
    ext = max(clamp((26.5-g[2])/8)*arm, clamp((12.5-g[2])/10))
    col = mix(col, (52, 42, 29), .55*ext)
    for h in HANDS:
        dh = math.dist(p, h)/S
        if dh < 3.2:
            knuckle = max(0., math.sin(g[2]*5.4+g[0]*2))**3
            col = mix(col, (34, 26, 18), .45*knuckle*clamp((3.2-dh)/.8))
    for a, b in SCARS:
        dist, t = segment_distance((y, z), a, b)
        if dist < .8 and n[0] > .1:
            k = clamp((.62-dist)/.2); rim = clamp((.8-dist)/.18)-k
            col = mix(col, (30, 20, 14), .5*rim)
            col = mix(col, (190, 146, 122), .9*k)
    # Bold blue war paint (glyph-colour cue): chest chevron and arm bands.
    paint_col = (32+24*fine, 60+28*fine, 168+30*mott)
    if body > .2 and n[0] > .1:
        for sgn in (-1, 1):
            dist, t = segment_distance((g[1], g[2]), (sgn*4.5, 31.4), (0, 28.3))
            if dist < .75: col = mix(col, paint_col, .92*clamp((.75-dist)/.15)*body)
    if arm > .5:
        for z0, h in ((27.6, .45), (29.3, .32)):
            if abs(g[2]-z0) < h: col = mix(col, paint_col, .92*clamp((h-abs(g[2]-z0))/.12))
    # Blue war-paint mask across the eyes (glyph-colour identity cue).
    band = abs(g[2]-(35.55+3.2)-.34*(abs(g[1])-1.9))
    if face > .05 and band < .72 and abs(g[1]) < 2.95:
        k = clamp((.72-band)/.2)*clamp((2.95-abs(g[1]))/.4)*clamp(face*3)
        paint = (34+30*fine, 58+30*fine, 148+30*mott)
        col = mix(col, paint, .9*k)
    # Crossed leather harness (baldric plus a second strap) with an iron boss.
    for strap_line in (BALDRIC, HARNESS):
      if body > .3 and head < .1:
        dist, t = segment_distance((y, z), strap_line[0], strap_line[1])
        BAL = strap_line
        if dist < .92*S:
            strap = (64+10*fine, 42+8*fine, 26+6*fine)
            edge = clamp((dist/S-.66)/.26)
            strap = mix(strap, (22, 14, 9), edge*.8)
            strap = mix(strap, (112, 80, 50), math.exp(-((dist/S-.52)/.06)**2)*.7)
            length = math.hypot(BAL[1][0]-BAL[0][0], BAL[1][1]-BAL[0][1])
            if abs(((t*length/S) % 3.4)-1.7) < .2 and dist/S < .2: strap = (128, 122, 108)
            col = mix(col, strap, clamp((.92*S-dist)/(.08*S)))
    if body > .3 and n[0] > .2:
        db = math.hypot(g[1], g[2]-26.2)
        if db < 1.15:
            spec = max(0., dot(n, HALF))**8
            col = mix(col, (96+90*spec, 98+90*spec, 104+86*spec), clamp((1.15-db)/.1))
            if db > .95: col = mix(col, (30, 30, 32), .7)
    return col, .9


def fur(p, n, occ):
    x, y, z = p; g = (x/S+1.15, y/S, z/S)
    a = math.atan2(g[1]/6.45, g[0]/4.0)
    center = (4.0*math.cos(a), 6.45*math.sin(a), 33.9-.35*math.cos(a)+.25*math.cos(2*a))
    r = math.dist(g, center)
    tip = clamp((r-1.55)/1.0)
    streak = math.sin(a*61+2.5*math.sin(g[2]*2.3)+3*noise(p, 1.3))
    clump = noise(p, 1.6)-.5
    col = mix((42, 37, 33), (138, 128, 110), tip*.85+.15*clamp(streak))
    return (col[0]+30*clump+10*streak, col[1]+26*clump+9*streak, col[2]+20*clump+7*streak), .6


def iron(p, n, occ, bright=False):
    base = (150, 155, 162) if bright else (74, 78, 86)
    ham = 9*math.sin(p[0]*5.1+math.sin(p[1]*4.3))*math.sin(p[2]*4.7)
    rust = clamp((noise(p, .8)-.62)*4)*(0 if bright else 1)
    col = mix((base[0]+ham, base[1]+ham, base[2]+ham), (112, 70, 44), .65*rust)
    spec = max(0., dot(n, HALF))**(18 if bright else 22)
    k = 125 if bright else 62
    return (col[0]+k*spec, col[1]+k*spec, col[2]+k*.96*spec), 1.


def bone(p, n, occ, uv):
    u, v = uv
    ridge = 18*max(0, math.sin(u*44))*(1-u)
    base = mix((150, 128, 92), (224, 212, 178), clamp(u*1.4))
    spec = max(0., dot(n, HALF))**10
    grain = noise(p, 2.2)-.5
    return (base[0]-ridge+18*grain+70*spec, base[1]-ridge+16*grain+66*spec, base[2]-ridge*1.2+12*grain+58*spec), .85


def crest(p, n, occ, uv, tuft):
    x, y, z = p
    top = clamp((z/S-43.5)/3.2) if not tuft else clamp(uv[0])
    streak = math.sin(x*11+2.2*math.sin(z*3.1)+y*5)
    col = mix((22, 36, 104), (104, 158, 250), top)
    col = mix(col, (44, 92, 222), .35)
    return (col[0]+12*streak, col[1]+16*streak, col[2]+20*streak), .7


def cloth(p, n, occ, uv, pennant):
    x, y, z = p; u, v = uv
    weave = noise(p, 2.6)-.5
    if pennant:
        border = max(clamp((.12-min(v, 1-v))/.05), clamp((u-.9)/.04))
        col = mix((40, 70, 172), (206, 192, 150), border)
        fold = 14*math.sin(u*math.pi*2.2+.4)
    else:
        radial = norm((x+1.9*S, y*.7, 0.))
        outer = dot(n, radial) > -.05
        col = (40, 70, 176) if outer else (22, 26, 58)
        fold = 20*math.sin(u*math.tau*3.5+.7)*v
        hem = clamp((v-.8)/.2)
        col = mix(col, (30, 30, 36), .6*hem)
        # Painted pale band along the cloak edge: reads as a leader's mantle.
        edge = clamp((.055-min(u, 1-u))/.02)
        col = mix(col, (190, 176, 136), .8*edge*(1 if outer else 0))
    return (col[0]+fold+14*weave, col[1]+fold+16*weave, col[2]+fold*1.3+22*weave), .75


def leather(p, n, occ, uv, wraps):
    u, v = uv
    grain = noise(p, 2.4)-.5
    col = (78, 52, 33)
    if wraps:
        band = math.sin((u*7+v)*math.tau)
        col = mix(col, (40, 26, 16), clamp(-band*1.5)*.7)
        col = mix(col, (112, 82, 54), clamp(band-.7)*1.4)
    else:
        a = math.atan2(p[1]/5.0, p[0]/S+.55)
        stud = math.cos(a*12)
        if stud > .93 and abs(p[2]/S-22.3) < .35: col = (186, 178, 158)
    return (col[0]+20*grain, col[1]+15*grain, col[2]+10*grain), .8


def hide(p, n, occ, uv):
    u, v = uv
    patch = noise(p, .9)
    col = mix((112, 82, 52), (66, 46, 30), clamp((patch-.45)*2.5))
    edge = clamp((.12-min(u, 1-u))/.06)
    stitch = edge*(1 if math.sin(v*70) > .2 else .3)
    col = mix(col, (44, 30, 20), .6*stitch)
    hem = clamp((v-.86)/.14)
    col = mix(col, (52, 40, 30), .55*hem)
    grain = noise(p, 3)-.5
    return (col[0]+18*grain, col[1]+14*grain, col[2]+9*grain), .75


def wood(p, n, occ, uv):
    u, v = uv
    grain = math.sin(v*math.tau*6+3*math.sin(u*31)+4*noise(p, .7))
    knot = clamp((noise(p, .6)-.72)*5)
    col = mix((104, 74, 42), (54, 36, 20), .5*clamp(-grain)+.6*knot)
    spec = max(0., dot(n, HALF))**8
    return (col[0]+26*spec, col[1]+20*spec, col[2]+14*spec), .8


def cord(p, n, occ, uv):
    u, v = uv
    twist = math.sin((u*56+v*2)*math.tau/2)
    col = mix((158, 130, 86), (92, 72, 44), clamp(-twist))
    return col, .7


def paint(role_name, name, p, n, occ, uv):
    if role_name == 'skin': col, ao = skin(p, n, occ)
    elif role_name == 'fur': col, ao = fur(p, n, occ)
    elif role_name == 'iron': col, ao = iron(p, n, occ)
    elif role_name == 'blade': col, ao = iron(p, n, occ, True)
    elif role_name == 'bone': col, ao = bone(p, n, occ, uv)
    elif role_name == 'crest': col, ao = crest(p, n, occ, uv, name != 'crest')
    elif role_name == 'cloth': col, ao = cloth(p, n, occ, uv, name == 'pennant')
    elif role_name == 'leather': col, ao = leather(p, n, occ, uv, name != 'belt')
    elif role_name == 'hide': col, ao = hide(p, n, occ, uv)
    elif role_name == 'wood': col, ao = wood(p, n, occ, uv)
    elif role_name == 'cord': col, ao = cord(p, n, occ, uv)
    elif role_name == 'dark': col, ao = (18, 13, 10), .2
    elif role_name == 'iris':
        k = clamp((p[2]/S-38.72)/.2+.5)
        col, ao = mix((196, 112, 18), (255, 218, 96), k), .2
    else: col, ao = (136, 94, 80), .6
    lit = .64+.44*max(0., dot(n, LIGHT))-.16*max(0., -n[2])
    shade = lit*(1-ao*.75*occ)
    return (col[0]*shade, col[1]*shade, col[2]*shade)


# ---------------------------------------------------------------- baking
def occlusion(parts):
    """Proximity occlusion from every rest triangle (contact shadows, creases)."""
    tris = []
    for p in parts:
        for a, b, c in p.triangles():
            A, B, C = p.vertices[a], p.vertices[b], p.vertices[c]
            cr = cross(sub(B, A), sub(C, A)); area = math.sqrt(dot(cr, cr))/2
            if area < 1e-9: continue
            tris.append(((A[0]+B[0]+C[0])/3, (A[1]+B[1]+C[1])/3, (A[2]+B[2]+C[2])/3, area))
    R = 2.4; grid = {}
    for t in tris: grid.setdefault((math.floor(t[0]/R), math.floor(t[1]/R), math.floor(t[2]/R)), []).append(t)
    result = []
    for p in parts:
        normals = p.normals(); values = []
        for v, n in zip(p.vertices, normals):
            key = (math.floor(v[0]/R), math.floor(v[1]/R), math.floor(v[2]/R)); total = 0.
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        for cx, cy, cz, area in grid.get((key[0]+dx, key[1]+dy, key[2]+dz), ()):
                            ex, ey, ez = cx-v[0], cy-v[1], cz-v[2]
                            d2 = ex*ex+ey*ey+ez*ez
                            if d2 < .02 or d2 > R*R: continue
                            d = math.sqrt(d2); cos = (ex*n[0]+ey*n[1]+ez*n[2])/d
                            if cos > .15: total += area*cos/(math.pi*d2+area)*(1-d/R)
            # A floor plane also darkens undersides near the ground.
            values.append(clamp(total*.85+.35*clamp(1-v[2]/2.5)*clamp(-n[2]+.3)))
        result.append((values, normals))
    return result


def sub(a, b): return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def morton(i):
    x = y = 0
    for bit in range(8):
        x |= ((i >> (2*bit)) & 1) << bit; y |= ((i >> (2*bit+1)) & 1) << bit
    return x, y


def _triangles(parts):
    """Stable list of (part index, triangle, sort key)."""
    out = []
    lo = [min(v[a] for p in parts for v in p.vertices) for a in range(3)]
    hi = [max(v[a] for p in parts for v in p.vertices) for a in range(3)]
    for pi, p in enumerate(parts):
        for tri in p.triangles():
            c = [sum(p.vertices[i][a] for i in tri)/3 for a in range(3)]
            q = [min(1023, int((c[a]-lo[a])/(hi[a]-lo[a]+1e-9)*1024)) for a in range(3)]
            key = 0
            for bit in range(10):
                for a in range(3): key |= ((q[a] >> bit) & 1) << (3*bit+a)
            out.append((key, pi, tri))
    out.sort(key=lambda e: (e[0], e[1], e[2]))
    if len(out) > GRID*GRID: raise ValueError(f'{len(out)} triangles exceed the {GRID*GRID} island atlas')
    return out


def islands(parts):
    """Replace every part's UVs with its unique padded triangle islands."""
    order = _triangles(parts)
    new = [Part(p.name) for p in parts]
    for q, p in zip(new, parts):
        if hasattr(p, 'skin_weights'): q.skin_weights = []; q.skin_topology = []
    for k, (key, pi, tri) in enumerate(order):
        x0, y0 = morton(k); x0 *= CELL; y0 *= CELL
        p, q = parts[pi], new[pi]; base = len(q.vertices)
        for i, (dx, dy) in zip(tri, ((2, 2), (CELL-2, 2), (2, CELL-2))):
            q.vertices.append(p.vertices[i]); q.uv.append(((x0+dx)/SIZE, 1-(y0+dy)/SIZE))
            if hasattr(p, 'skin_weights'):
                q.skin_weights.append(p.skin_weights[i]); q.skin_topology.append(p.skin_topology[i])
        q.faces.append((base, base+1, base+2))
    return new


def texture_bytes(parts):
    order = _triangles(parts)
    shading = occlusion(parts)
    roles = [role(p.name) for p in parts]
    buffer = bytearray(SIZE*SIZE*3)
    lattice = (.5, 3.5, 6.5, 9.5, 12.5, 15.5)
    span = CELL-4
    for k, (key, pi, tri) in enumerate(order):
        x0, y0 = morton(k); x0 *= CELL; y0 *= CELL
        p = parts[pi]; occ, normals = shading[pi]
        P = [p.vertices[i] for i in tri]; N = [normals[i] for i in tri]; O = [occ[i] for i in tri]
        UV = [p.uv[i] for i in tri] if roles[pi] != 'skin' else [(0, 0)]*3
        grid = []
        for ly in lattice:
            row = []
            for lx in lattice:
                b = (lx-2)/span; c = (ly-2)/span; a = 1-b-c
                pos = tuple(a*P[0][j]+b*P[1][j]+c*P[2][j] for j in range(3))
                nrm = norm(tuple(a*N[0][j]+b*N[1][j]+c*N[2][j] for j in range(3)))
                o = clamp(a*O[0]+b*O[1]+c*O[2])
                uv = (a*UV[0][0]+b*UV[1][0]+c*UV[2][0], a*UV[0][1]+b*UV[1][1]+c*UV[2][1])
                row.append(paint(roles[pi], p.name, pos, nrm, o, uv))
            grid.append(row)
        blocks = []
        for by in range(8):
            iy, ty = STEPS[by]; r0, r1 = grid[iy], grid[iy+1]
            row = bytearray()
            grain = GRAIN[k & 15][by]
            for bx in range(8):
                ix, tx = STEPS[bx]
                c00, c10, c01, c11 = r0[ix], r0[ix+1], r1[ix], r1[ix+1]
                gr = grain[bx]
                for j in range(3):
                    top = c00[j]+(c10[j]-c00[j])*tx; bottom = c01[j]+(c11[j]-c01[j])*tx
                    value = int(top+(bottom-top)*ty+gr+.5)
                    row.append(0 if value < 0 else 255 if value > 255 else value)
            wide = bytearray()
            for bx in range(8): wide += row[bx*3:bx*3+3]*2
            offset = ((y0+2*by)*SIZE+x0)*3
            buffer[offset:offset+48] = wide; buffer[offset+SIZE*3:offset+SIZE*3+48] = wide
    return encode_png(buffer, SIZE, SIZE)


STEPS = [(min(4, int((2*b+1-.5)/3)), (2*b+1-.5)/3-min(4, int((2*b+1-.5)/3))) for b in range(8)]
GRAIN = [[[((((v*31+by*7+bx*13)*2654435761) >> 7) & 15)/15*8-4 for bx in range(8)] for by in range(8)] for v in range(16)]


def encode_png(pixels, width, height):
    def chunk(k, d): return struct.pack('>I', len(d))+k+d+struct.pack('>I', zlib.crc32(k+d) & 0xffffffff)
    raw = b''.join(b'\0'+bytes(pixels[y*width*3:(y+1)*width*3]) for y in range(height))
    return (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(raw, 9))+chunk(b'IEND', b''))

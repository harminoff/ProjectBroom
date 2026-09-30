"""Original aged ogre shaman: stooped connected anatomy and relic staff.

Brogue describes an ogre bent with age whose lost strength is outweighed by
occult power. Everything here is presentation only: the staff, relics, paint
and ritual gestures add no light, collision, damage, spell, AI, turn or RNG
behaviour. +X is forward, Z is up and the floor is Z=0.
"""
import hashlib
import json
import math
from . import iqm, ogre_shaman_materials
from .creatures import Sculpt, TILE
from .rat import ROOT, Part, add, sub, mul, unit, cross, spline
from .skeletal import Rig, axis, between, inverse, qmul, rotate, assemble, sample_clips

SKIN = 'graphics/BRGOGSH.png'
ARM = dict(upper=(-1.5, 13.4, 48.2), lower=(1.2, 17.6, 37.6), end=(9.2, 15.2, 32.6))
LEG = dict(upper=(-2.2, 7.2, 26.2), lower=(3.6, 8.6, 14.6), end=(-.6, 9.2, 3.8))
GRIP = (10.9, -15.8, 31.4)          # staff axis inside the closed right hand
SPECS = [('root', None, (0, 0, 0)), ('pelvis', 'root', (-2, 0, 27)),
         ('spine', 'pelvis', (-4, 0, 37)), ('chest', 'spine', (-3.6, 0, 46.5)),
         ('neck', 'chest', (1.8, 0, 53.2)), ('head', 'neck', (6.6, 0, 56.4)),
         ('jaw', 'head', (9.8, 0, 55.2))]
for side, sign in (('L', 1), ('R', -1)):
    for limb, parent, joints in (('arm', 'chest', ARM), ('leg', 'pelvis', LEG)):
        for joint in ('upper', 'lower', 'end'):
            x, y, z = joints[joint]
            name = f'{limb}_{side}_{joint}'
            SPECS.append((name, parent, (x, sign*y, z)))
            parent = name
SPECS.append(('staff', 'arm_R_end', GRIP))
RIG = Rig.from_world(SPECS)
BONES, REST = RIG.bones, RIG.rest
IDS = {n: i for i, (n, p, v) in enumerate(BONES)}
CLIPS = [('idle', 48, 16, True), ('hobble', 32, 35, True), ('cudgel', 28, 35, False),
         ('chant_strike', 30, 35, False), ('recoil', 14, 35, False), ('collapse', 40, 35, False)]
STAFF_TIP, STAFF_TOP = 1.2, 76.0


def mirror(p, sign): return (p[0], sign*p[1], p[2])


def torso_loft(name, controls, sides=36, samples=4):
    """Loft rings perpendicular to a bent spine path in the XZ plane.

    Each control is x, z, half width, front depth, back depth. Separate front
    and back depths give a sagging paunch below a pronounced dorsal hump.
    """
    p = Part(name)
    rows = spline(controls, samples)
    centers = []
    for i, (x, z, width, front, back) in enumerate(rows):
        a, b = rows[max(0, i-1)], rows[min(len(rows)-1, i+1)]
        tx, tz = b[0]-a[0], b[1]-a[1]
        length = math.hypot(tx, tz)
        tx, tz = tx/length, tz/length
        nx, nz = tz, -tx
        for j in range(sides+1):
            angle = math.tau*j/sides
            c, s = math.cos(angle), math.sin(angle)
            depth = (front if c > 0 else back)*c
            # Aged sag: flanks fold slightly inward below the ribs.
            flank = 1-.035*math.exp(-((z-41)/4)**2)*abs(s)
            p.vertex((x+nx*depth, width*s*flank, z+nz*depth), 'fur', i/(len(rows)-1), j/sides)
        centers.append((x, 0, z))
    for i in range(len(rows)-1):
        for j in range(sides):
            a = i*(sides+1)+j
            p.faces.append((a, a+sides+1, a+sides+2, a+1))
    for end, reverse in ((0, False), (len(rows)-1, True)):
        center = p.vertex(centers[end], 'fur', end/(len(rows)-1), .5)
        for j in range(sides):
            a = end*(sides+1)+j
            p.faces.append((center, a, a+1) if reverse else (center, a+1, a))
    return p


TORSO = [(-1.6, 19.2, 5.2, 4.2, 4.2), (-1.6, 21.5, 8.6, 7.2, 7.6), (-1.7, 25.5, 10.2, 8.4, 8.6),
         (-1.2, 29.5, 11.1, 9.7, 8.1), (-1.3, 33.5, 11.5, 10.4, 7.6), (-2.3, 37.5, 11.1, 9.3, 7.6),
         (-3.1, 41.5, 10.7, 7.7, 8.7), (-3.2, 45.5, 10.9, 7.0, 10.0), (-1.9, 49.5, 10.4, 6.4, 9.7),
         (.6, 52.6, 8.2, 5.6, 8.1), (3.4, 54.8, 5.4, 4.5, 5.2), (5.6, 56.4, 4.4, 3.9, 4.2)]


def sheet(name, grid, thickness, tile='paw', inward=None):
    """Closed thin shell from a rows x columns grid of outer points."""
    p = Part(name)
    rows, cols = len(grid), len(grid[0])
    for layer in (0, 1):
        for r, row in enumerate(grid):
            for c, point in enumerate(row):
                if layer:
                    direction = inward(point) if inward else (0, 0, 0)
                    point = add(point, mul(direction, thickness))
                p.vertex(point, tile, c/(cols-1), .04+.92*r/(rows-1))
    n = rows*cols
    for r in range(rows-1):
        for c in range(cols-1):
            a = r*cols+c
            p.faces.append((a, a+1, a+cols+1, a+cols))
            p.faces.append((n+a, n+a+cols, n+a+cols+1, n+a+1))
    for r in range(rows-1):
        for c in (0, cols-1):
            a, b = r*cols+c, (r+1)*cols+c
            p.faces.append((a, b, n+b, n+a) if c == 0 else (a, n+a, n+b, b))
    for c in range(cols-1):
        for r in (0, rows-1):
            a, b = r*cols+c, r*cols+c+1
            p.faces.append((a, n+a, n+b, b) if r == 0 else (a, b, n+b, n+a))
    return p


def torso_at(z):
    """Interpolated torso loft profile (x, z, width, front, back) at a height."""
    rows = spline(TORSO, 8)
    for a, b in zip(rows, rows[1:]):
        if a[1] <= z <= b[1]:
            t = (z-a[1])/(b[1]-a[1])
            return tuple(p+(q-p)*t for p, q in zip(a, b))
    return rows[0] if z < rows[0][1] else rows[-1]


def mantle_grid(rows=15, cols=21):
    """Hide mantle: a shawl over hump and upper arms and a longer back panel.

    Every point is offset from the sampled torso profile, so the hide hugs the
    stooped back instead of standing off it like a slab.
    """
    grid = []
    for r in range(rows):
        s = r/(rows-1)
        row = []
        for c in range(cols):
            u = c/(cols-1)
            side = smooth((abs(u-.5)-.17)/.26)
            bottom = 23.5+16.5*side
            z = 54.0-(54.0-bottom)*s
            angle = math.pi+1.42*math.pi*(u-.5)
            ca, sa = math.cos(angle), math.sin(angle)
            cx, _, width, front, back = torso_at(z)
            envelope = 9.8+9.9*smooth((53.6-z)/5.2)-8.0*smooth((41-z)/5)
            hug = width+1.3+.5*s
            wm = hug+max(0, envelope-hug)*clamp((abs(sa)-.28)/.5)
            ripple = .5*math.sin(u*math.tau*4.5+1.3)*s*s
            depth = back+1.25+.5*s+ripple if ca < 0 else front+2.3
            lift = 2.0*math.exp(-((z-49)/3.5)**2)*clamp((abs(sa)-.6)/.4)
            hem = (1.2*math.sin(u*37)+.8*math.sin(u*71))*(r == rows-1)
            row.append((cx+depth*ca, wm*sa, z+lift+hem))
        grid.append(row)
    return grid


def inward_from_axis(point):
    x, y, z = point
    return unit((-3-x, -y, 0))


def ring(center, rx, ry, count, z_wave=0):
    return [(center[0]+rx*math.cos(a), center[1]+ry*math.sin(a), center[2]+z_wave*math.sin(3*a))
            for a in (math.tau*i/count for i in range(count+1))]


def build_parts():
    s = Sculpt()
    s.oval('pelvis', (-1.8, 0, 26.5), (8.2, 9.6, 6.6))
    s.parts.append(torso_loft('torso', TORSO))
    # Head: low cranium, heavy brow, hooked nose, sagging jowls and a jaw.
    s.oval('head_cranium', (6.6, 0, 59.4), (5.7, 5.5, 5.3), 'body', 28, 16)
    s.oval('head_face', (9.8, 0, 57.6), (3.5, 4.8, 3.5), 'body', 24, 14)
    s.strand('head_brow', [(10.9, -4.9, 60.2, .95), (12.3, -2.6, 61.0, 1.3), (12.7, 0, 60.7, 1.05),
                           (12.3, 2.6, 61.0, 1.3), (10.9, 4.9, 60.2, .95)], 'body', 14, 4)
    s.strand('head_nose', [(12.2, 0, 60.3, .95), (13.6, 0, 59.0, 1.2), (14.6, 0, 57.6, 1.4),
                           (14.2, 0, 56.4, 1.0), (13.2, 0, 56.0, .65)], 'body', 16, 4)
    s.strand('head_lip', [(12.2, -3.3, 55.3, .7), (13.1, -1.4, 55.4, .8), (13.2, 1.4, 55.4, .8),
                          (12.2, 3.3, 55.3, .7)], 'body', 12, 3)
    for sign in (-1, 1):
        s.oval(f'head_nostril_{sign}', (13.4, sign*1.15, 56.7), (1.0, .95, .85), 'body', 14, 10)
        s.oval(f'head_jowl_{sign}', (10.4, sign*3.8, 55.0), (2.2, 1.95, 2.45), 'body', 16, 12)
        ear = s.strand(f'head_ear_{sign}', [(4.9, sign*5.1, 59.2, 1.45), (4.3, sign*6.9, 58.4, 1.3),
                                            (3.8, sign*8.1, 56.6, .9), (3.6, sign*8.5, 54.4, .38)], 'body', 14, 4)
        ear.vertices = [(3.9+(x-3.9)*.52, y, z) for x, y, z in ear.vertices]
    s.oval('head_jaw', (11.2, 0, 53.9), (2.7, 4.3, 2.0), 'body', 24, 12)
    # Shoulders, trapezius and aged limbs. Arms stand clear of the flanks.
    for side, sign in (('L', 1), ('R', -1)):
        up, lo, end = (mirror(ARM[j], sign) for j in ('upper', 'lower', 'end'))
        s.oval(f'shoulder_{side}', (-1.8, sign*12.4, 49.0), (5.4, 5.0, 5.3))
        s.oval(f'shoulder_{side}_trap', (-3.0, sign*7.2, 52.2), (4.8, 4.4, 3.4))
        mid_upper = add(up, mul(sub(lo, up), .45))
        fore = add(lo, mul(sub(end, lo), .3))
        s.strand(f'arm_{side}', [(*up, 4.4), (*mid_upper, 3.7), (*lo, 3.0), (*fore, 3.2), (*end, 2.25)], sides=20, samples=4)
        s.oval(f'arm_{side}_elbow', add(lo, (-1.0, sign*.4, .2)), (2.2, 2.3, 2.6))
        hip, knee, ankle = (mirror(LEG[j], sign) for j in ('upper', 'lower', 'end'))
        s.strand(f'leg_{side}', [(*hip, 5.5), (*add(hip, mul(sub(knee, hip), .5)), 4.8), (*knee, 3.8),
                                 (*add(knee, mul(sub(ankle, knee), .35)), 3.7), (*ankle, 2.55)], sides=20, samples=4)
        s.oval(f'leg_{side}_kneecap', add(knee, (1.9, 0, .3)), (1.9, 2.5, 2.6))
        s.oval(f'foot_{side}', (2.9, sign*9.3, 2.15), (5.3, 3.7, 1.9), 'body', 24, 12)
        s.oval(f'foot_{side}_heel', (-1.1, sign*9.2, 2.45), (2.4, 2.6, 2.2), 'body', 16, 10)
        for i in range(4):
            y = sign*9.3+(i-1.5)*1.6
            s.oval(f'foot_{side}_toe{i}', (7.4, y, 1.6), (1.8, .82, 1.25), 'body', 12, 8)
            s.oval(f'nail_{side}_toe{i}', (9.05, y, 1.95), (.42, .62, .45), 'bone', 10, 6)
    # Right hand: a knobbly fist closed round the staff axis.
    gx, gy, gz = GRIP
    s.oval('hand_R_palm', (gx-1.9, gy+.2, gz+.2), (2.2, 2.3, 3.3))
    for i in range(4):
        z = gz-1.95+i*1.3
        r = 1.72+.08*(i == 1)
        pts = [(gx-2.2, gy-1.4, z+.35)]
        for k in range(1, 6):
            a = math.pi+.3-k*1.0
            pts.append((gx+r*math.cos(a)*(1.02+.05*k), gy+r*math.sin(a)*(1.02+.05*k)*-1, z))
        s.strand(f'hand_R_finger{i}', [(*pt, .7-.045*k) for k, pt in enumerate(pts)], 'body', 10, 3)
    s.strand('hand_R_thumb', [(gx-2.3, gy+1.6, gz+2.6, .95), (gx-.6, gy+2.25, gz+3.0, .8),
                              (gx+1.2, gy+1.5, gz+2.8, .62)], 'body', 12, 3)
    # Left hand: open, long-fingered ritual hand, fingers spread apart.
    lx, ly, lz = mirror(ARM['end'], 1)
    s.oval('hand_L_palm', (lx+1.7, ly-.3, lz-1.3), (2.7, 1.75, 2.9))
    for i in range(4):
        spread = (i-1.5)
        base = (lx+3.6, ly-.4+spread*1.12, lz-1.2+abs(spread)*.25)
        mid = (lx+5.6, ly-.4+spread*1.55, lz-2.3)
        tip = (lx+6.6, ly-.4+spread*1.95, lz-4.3-.2*(i in (1, 2)))
        s.strand(f'hand_L_finger{i}', [(*base, .68), (*mid, .56), (*tip, .38)], 'body', 10, 3)
        s.oval(f'nail_L_finger{i}', add(tip, (.15, 0, -.35)), (.34, .36, .42), 'bone', 8, 6)
    s.strand('hand_L_thumb', [(lx+1.6, ly-1.7, lz-.2, .9), (lx+3.3, ly-3.0, lz-.9, .7),
                              (lx+4.5, ly-3.3, lz-2.0, .5)], 'body', 10, 3)
    for i in range(4):
        z = gz-1.95+i*1.3
        s.oval(f'nail_R_finger{i}', (gx+.9, gy+1.55, z), (.4, .3, .45), 'bone', 8, 6)
    # Face details: deep eyes, mouth line, tusks, lower teeth.
    for sign in (-1, 1):
        s.oval(f'eye_socket_{sign}', (12.05, sign*2.55, 59.15), (.55, 1.1, .68), 'dark', 18, 10)
        s.oval(f'eye_iris_{sign}', (12.45, sign*2.5, 59.1), (.22, .5, .44), 'accent', 16, 8)
        s.oval(f'eye_pupil_{sign}', (12.6, sign*2.5, 59.1), (.08, .17, .3), 'dark', 12, 8)
        s.strand(f'tusk_{sign}', [(12.2, sign*2.4, 54.6, .56), (13.2, sign*2.65, 56.0, .42),
                                  (13.3, sign*3.05, 57.2-.5*(sign > 0), .12)], 'bone', 10, 3)
    s.strand('mouth_line', [(12.4, -3.3, 55.0, .2), (13.55, -1.3, 54.9, .24), (13.55, 1.3, 54.9, .24),
                            (12.4, 3.3, 55.0, .2)], 'dark', 8, 3)
    for i in range(4):
        y = (i-1.5)*.95
        s.oval(f'tooth_{i}', (13.2, y, 55.0), (.28, .36, .42), 'bone', 8, 6)
    # Hair: grey brows, drooping moustache, long divided beard, scalp braid.
    for sign in (-1, 1):
        for i in range(4):
            y = sign*(1.2+i*.95)
            s.strand(f'hair_brow_{sign}_{i}', [(12.1-.35*i, y, 61.6, .34), (13.3-.4*i, y+sign*.5, 61.9-.1*i, .26),
                                                (13.9-.45*i, y+sign*1.1, 61.2-.2*i, .08)], 'bone', 6, 2)
        s.strand(f'hair_moustache_{sign}', [(13.7, sign*.7, 56.2, .5), (14.1, sign*2.2, 55.5, .45),
                                            (14.0, sign*3.2, 53.8, .32), (13.6, sign*3.5, 51.4, .1)], 'bone', 8, 3)
        for i in range(2):
            x = 2.6-2.2*i
            z = 63.0-.6*i
            s.strand(f'hair_lock_{sign}_{i}', [(x, sign*(4.8+.3*i), z, .4), (x-.9, sign*(5.5+.3*i), z-2.2, .34),
                                                (x-1.5, sign*(5.4+.3*i), z-4.8-.4*i, .2),
                                                (x-1.9, sign*(5.0+.3*i), z-6.8-.4*i, .05)], 'bone', 8, 3)
    for i in range(9):
        y = (i-4)*.78
        braid = -1 if i < 4 else (1 if i > 4 else 0)
        length = 8.4-abs(i-4)*.55
        root = (12.8-.18*abs(i-4), y, 53.6+.2*abs(i-4))
        end = (13.9, braid*1.7+y*.18, root[2]-length)
        mid = (13.9, (root[1]+end[1])/2, (root[2]+end[2])/2+.4)
        s.strand(f'hair_beard_{i}', [(*root, .62), (*mid, .5), (*end, .16)], 'bone', 8, 3)
    for sign in (-1, 1):
        s.oval(f'relic_beard_bead_{sign}', (13.9, sign*1.75, 46.6), (.75, .75, .95), 'accent', 12, 8)
    s.strand('hair_braid', [(5.0, 0, 64.5, .75), (2.4, 0, 64.3, .95), (-.5, 0, 62.4, .9),
                            (-2.6, 0, 59.3, .75), (-4.0, 0, 55.6, .5), (-5.0, 0, 52.4, .2)], 'bone', 10, 4)
    s.strand('relic_braid_ring', [(-2.5+.95*math.sin(a), 1.1*math.cos(a), 59.4-.55*math.sin(a), .26) for a in
                                  (math.tau*i/14 for i in range(15))], 'cloth', 8, 1)
    for sign in (-1, 1):
        s.strand(f'relic_earring_{sign}', [(3.7+.8*math.cos(a), sign*8.55, 54.5+.8*math.sin(a), .15)
                                           for a in (math.tau*i/14 for i in range(15))], 'accent', 6, 1)
    # Hide mantle, fur collar and bone-toggle cord across the chest.
    s.parts.append(sheet('mantle_hide', mantle_grid(), .75, 'paw', inward_from_axis))
    top = mantle_grid()[0]
    for i, (x, y, z) in enumerate(top[1:-1:2]):
        size = 1.25+.25*math.sin(i*2.3)
        s.oval(f'mantle_fur_{i}', (x+.15, y*1.03, z+.55), (size*1.1, size*1.25, size*.8), 'glow', 12, 8)
    s.strand('mantle_tie', [(3.2, -7.4, 52.4, .32), (6.2, -3.2, 50.8, .3), (6.9, 0, 50.6, .3),
                            (6.2, 3.2, 50.8, .3), (3.2, 7.4, 52.4, .32)], 'cloth', 8, 3)
    s.strand('relic_toggle', [(6.9, -1.2, 50.6, .45), (7.1, 1.2, 50.6, .45)], 'bone', 8, 2)
    # Necklace of teeth/claw talismans above the paunch.
    necklace = [(1.5+6.6*math.cos(a), 7.2*math.sin(a), 50.9-2.8*math.cos(a)) for a in
                (-1.3+2.6*i/12 for i in range(13))]
    s.strand('neck_cord', [(*p, .22) for p in necklace], 'cloth', 8, 2)
    for i, p in enumerate(necklace[1:-1:1]):
        if i % 2:continue
        length = 1.9+.6*(i == 5)
        s.strand(f'relic_neck_{i}', [(p[0]+.25, p[1], p[2]-.2, .42), (p[0]+.55, p[1], p[2]-length, .08)], 'bone', 8, 2)
    # Tattered hide loincloth, rope belt, pouch and small skull fetish.
    p = Part('wrap_hide')
    n = 40
    for row in range(4):
        for i in range(n):
            a = math.tau*i/n
            front = math.cos(a) > .6
            bottom = 20.5+1.2*math.sin(i*2.1)+.7*math.sin(i*3.7)-(5.5 if front else 0)
            z = 30.3 if row in (0, 3) else bottom
            inset = .25 if row >= 2 else 0
            fold = (.2 if row in (0, 3) else .6)*math.cos(10*a)
            rx = 10.1 if math.cos(a) > 0 else 8.9
            flare = 1.0 if row in (1, 2) else 0
            p.vertex((-1.4+(rx+fold+flare-inset)*math.cos(a), (11.6+fold+flare-inset)*math.sin(a), z),
                     'paw', i/n, float(row in (1, 2)))
    for row in range(4):
        for i in range(n):
            p.faces.append((row*n+i, ((row+1) % 4)*n+i, ((row+1) % 4)*n+(i+1) % n, row*n+(i+1) % n))
    s.parts.append(p)
    belt = [(-1.3+(10.55 if math.cos(a) > 0 else 9.1)*math.cos(a), 12.0*math.sin(a), 30.2+.25*math.sin(2*a))
            for a in (math.tau*i/48 for i in range(49))]
    s.strand('wrap_belt', [(*q, .5) for q in belt], 'cloth', 8, 1)
    s.oval('wrap_pouch', (1.4, 12.6, 26.3), (2.6, 1.6, 3.1), 'accent', 16, 10)
    s.strand('wrap_pouch_cord', [(1.2, 12.4, 29.8, .22), (1.6, 13.1, 29.0, .2), (1.4, 13.7, 26.5, .18)], 'cloth', 6, 2)
    s.oval('relic_hip_skull', (4.6, -11.9, 25.2), (1.7, 1.5, 1.6), 'bone', 14, 10)
    s.oval('relic_hip_snout', (6.1, -11.9, 24.4), (1.3, 1.0, .9), 'bone', 12, 8)
    s.oval('relic_hip_orbits', (6.1, -11.9, 25.5), (1.05, 1.15, .45), 'dark', 12, 6)
    s.strand('relic_hip_cord', [(4.3, -11.6, 30.2, .2), (4.5, -11.9, 27.0, .2)], 'cloth', 6, 2)
    build_staff(s)
    # Python 3.12 changed float sum() rounding; quantize authored coordinates so
    # the bake fingerprint is identical in system Python and Blender's Python.
    for part in s.parts:
        part.vertices = [tuple(round(c, 6)+0. for c in v) for v in part.vertices]
    return ogre_shaman_materials.repack(s.parts)


def bend(z):
    """Crooked staff centreline; exactly on the grip axis inside the fist."""
    gx, gy, gz = GRIP
    w = smooth((abs(z-gz)-3)/6)
    return (gx+w*(.55*math.sin(z*.19)+.35*math.sin(z*.53)), gy+w*.45*math.sin(z*.23+1.3), z)


def build_staff(s):
    """Crooked forked staff: bound grip, lashed skull and hanging relics."""
    gx, gy, gz = GRIP
    shaft = [(*bend(z), r) for z, r in ((STAFF_TIP, .95), (8, 1.1), (18, 1.18), (26, 1.2), (29, 1.2),
                                         (31.4, 1.2), (34, 1.22), (38, 1.3),
                                         (48, 1.25), (58, 1.3), (66, 1.45), (70.5, 1.6))]
    s.strand('staff_shaft', shaft, 'wood', 14, 4)
    top = bend(70.5)
    s.strand('staff_tine_front', [(*top, 1.35), (top[0]+1.5, top[1]+.6, 73.6, 1.0), (top[0]+1.4, top[1]+2.0, 76.0, .62),
                                  (top[0]+.5, top[1]+2.8, STAFF_TOP, .22)], 'wood', 12, 4)
    s.strand('staff_tine_back', [(*top, 1.3), (top[0]-1.6, top[1]-.8, 73.2, .95), (top[0]-2.0, top[1]-2.3, 75.2, .55),
                                 (top[0]-1.4, top[1]-3.3, 75.8, .18)], 'wood', 12, 4)
    for i, z in enumerate((13, 44, 61)):
        c = bend(z)
        s.oval(f'staff_knot_{i}', (c[0]+.9*math.cos(i*2.1), c[1]+.9*math.sin(i*2.1), z), (1.0, 1.0, 1.4), 'wood', 10, 8)
    for i in range(7):
        z = gz-4.8+i*.7
        c = bend(z)
        if abs(z-gz) < 2.4:continue
        s.strand(f'staff_binding_{i}', [(c[0]+1.33*math.cos(a), c[1]+1.33*math.sin(a), z+.15*math.sin(a), .2)
                                        for a in (math.tau*j/16 for j in range(17))], 'cloth', 6, 1)
    for i in range(5):
        z = 64+i*.9
        c = bend(z)
        s.strand(f'staff_lash_{i}', [(c[0]+1.62*math.cos(a), c[1]+1.62*math.sin(a), z+.2*math.sin(a), .22)
                                     for a in (math.tau*j/16 for j in range(17))], 'cloth', 6, 1)
    # Lashed animal skull between the tines, facing forward.
    sx, sy, sz = top[0]+.4, top[1], 72.4
    s.oval('relic_staff_skull', (sx, sy, sz), (1.9, 1.75, 1.7), 'bone', 16, 10)
    s.oval('relic_staff_muzzle', (sx+2.0, sy, sz-.6), (1.6, 1.1, 1.0), 'bone', 14, 8)
    for sign in (-1, 1):
        s.oval(f'relic_staff_orbit_{sign}', (sx+1.2, sy+sign*.95, sz+.25), (.55, .5, .5), 'dark', 10, 6)
        s.strand(f'relic_staff_horn_{sign}', [(sx-.4, sy+sign*1.2, sz+1.2, .5), (sx-1.4, sy+sign*2.6, sz+2.2, .35),
                                              (sx-1.0, sy+sign*3.3, sz+3.4, .1)], 'bone', 8, 3)
    for i in range(4):
        s.oval(f'relic_staff_fang_{i}', (sx+3.2, sy+(i-1.5)*.55, sz-1.35), (.18, .18, .45), 'bone', 6, 5)
    # Dangling talismans below the crown: cords, bone charms and feathers.
    for i, (dy, dx, length) in enumerate(((-2.2, .6, 9.0), (1.9, .3, 11.5), (0, -1.9, 7.5))):
        c = bend(64.5)
        start = (c[0]+dx, c[1]+dy*.6, 64.5)
        end = (c[0]+dx*1.6, c[1]+dy, 64.5-length)
        s.strand(f'staff_cord_{i}', [(*start, .17), ((start[0]+end[0])/2, (start[1]+end[1])/2+.2*dy, (start[2]+end[2])/2, .16),
                                     (*end, .16)], 'cloth', 6, 3)
        if i == 1:
            s.strand('relic_staff_feather', [(end[0], end[1], end[2]+.3, .2), (end[0]+.2, end[1]+.3, end[2]-2.2, .55),
                                             (end[0]+.1, end[1]+.4, end[2]-4.6, .45), (end[0], end[1]+.3, end[2]-6.4, .05)], 'glow', 8, 3)
        else:
            s.oval(f'relic_staff_charm_{i}', (end[0], end[1], end[2]-1.1), (.55, .7, 1.4), 'bone', 10, 8)
    s.strand('relic_staff_feather_b', [(bend(66)[0]-1.4, bend(66)[1]-.2, 66, .2), (bend(66)[0]-2.6, bend(66)[1]-.5, 63.8, .5),
                                       (bend(66)[0]-3.1, bend(66)[1]-.6, 61.2, .4), (bend(66)[0]-3.2, bend(66)[1]-.6, 59.2, .05)], 'glow', 8, 3)


def clamp(v, lo=0., hi=1.): return max(lo, min(hi, v))


def weights(part, v, uv):
    n = part.name
    if n.startswith(('staff', 'relic_staff')):return [(IDS['staff'], 1)]
    if n.startswith(('tusk', 'tooth', 'hair_beard', 'relic_beard', 'head_jaw')):return [(IDS['jaw'], 1)]
    if n.startswith(('head', 'eye', 'hair', 'mouth', 'relic_ear', 'relic_braid')):return [(IDS['head'], 1)]
    if n.startswith(('nail_L_finger', 'hand_L')):return [(IDS['arm_L_end'], 1)]
    if n.startswith(('nail_R_finger', 'hand_R')):return [(IDS['arm_R_end'], 1)]
    if n.startswith(('foot_', 'nail_')):return [(IDS[f'leg_{n.split("_")[1]}_end'], 1)]
    if n.startswith(('neck_', 'relic_neck', 'relic_toggle')) or n in ('mantle_tie',):return [(IDS['chest'], 1)]
    if n.startswith('mantle'):
        base = RIG.chain_weights(v, [IDS[b] for b in ('pelvis', 'spine', 'chest', 'neck')])
        t = .55*clamp((abs(v[1])-11)/6)*clamp((v[2]-43)/6)
        if t <= 0:return base
        side = 'L' if v[1] > 0 else 'R'
        return [(b, w*(1-t)) for b, w in base]+[(IDS[f'arm_{side}_upper'], t)]
    if n == 'wrap_hide':
        # The hem follows the thighs so kneeling drapes it instead of burying it.
        t = .75*clamp((27.5-v[2])/7)
        if t <= 0:return [(IDS['pelvis'], 1)]
        share = clamp(.5+v[1]/6)
        out = [(IDS['pelvis'], 1-t)]
        if share > 0:out.append((IDS['leg_L_upper'], t*share))
        if share < 1:out.append((IDS['leg_R_upper'], t*(1-share)))
        return out
    if n.startswith(('wrap', 'relic_hip')):return [(IDS['pelvis'], 1)]
    if n.startswith('shoulder_'):
        side = n.split('_')[1]
        t = clamp((abs(v[1])-8)/6)
        return [(IDS['chest'], 1-t), (IDS[f'arm_{side}_upper'], t)] if t < 1 else [(IDS[f'arm_{side}_upper'], 1)]
    if n.startswith(('arm_', 'leg_')):
        limb, side = n.split('_')[:2]
        return RIG.chain_weights(v, [IDS[f'{limb}_{side}_{j}'] for j in ('upper', 'lower', 'end')])
    if n == 'pelvis':return [(IDS['pelvis'], 1)]
    return RIG.chain_weights(v, [IDS[b] for b in ('pelvis', 'spine', 'chest', 'neck', 'head')])


# --- posing -----------------------------------------------------------------

def smooth(x):
    x = clamp(x)
    return x*x*(3-2*x)


def window(t, a, b): return smooth((t-a)/(b-a))


class Pose:
    def __init__(self):
        self.rot = [(0, 0, 0, 1) for _ in BONES]
        self.shift = [(0, 0, 0) for _ in BONES]

    def turn(self, bone, direction, degrees):
        self.rot[IDS[bone]] = qmul(self.rot[IDS[bone]], axis(direction, math.radians(degrees)))

    def frame(self):
        return [(*add(local, self.shift[i]), *self.rot[i], 1, 1, 1) for i, (n, p, local) in enumerate(BONES)]

    def world(self):
        return RIG.matrices(self.frame())

    def reach(self, chain, target, world_q=None, clamp_reach=False, pole=None):
        """Two-bone IK to a world target, solved in the parent's rest frame.

        Optionally orients the end bone in world space (planted feet, staff).
        """
        ids = [IDS[f'{chain}_{j}'] for j in ('upper', 'lower', 'end')]
        parent = BONES[ids[0]][1]
        pw, pq = self.world()[parent]
        local = add(REST[parent], rotate(inverse(pq), sub(target, pw)))
        root, joint, end = [REST[i] for i in ids]
        root = add(root, self.shift[ids[0]])
        a, b = math.dist(REST[ids[0]], joint), math.dist(joint, end)
        distance = math.dist(local, root)
        if clamp_reach and distance > (a+b)*.995:
            local = add(root, mul(unit(sub(local, root)), (a+b)*.995))
            distance = (a+b)*.995
        if not abs(a-b)+1e-6 < distance < a+b-1e-6:
            raise ValueError(('unreachable', chain, target, distance, a+b))
        direction = unit(sub(local, root))
        along = (a*a-b*b+distance*distance)/(2*distance)
        pole = sub(joint, REST[ids[0]]) if pole is None else pole
        bend = unit(sub(pole, mul(direction, sum(x*y for x, y in zip(pole, direction)))))
        knee = add(root, add(mul(direction, along), mul(bend, math.sqrt(max(0, a*a-along*along)))))
        upper = between(sub(joint, REST[ids[0]]), sub(knee, root))
        lower = between(sub(end, joint), sub(local, knee))
        self.rot[ids[0]] = upper
        self.rot[ids[1]] = qmul(inverse(upper), lower)
        self.rot[ids[2]] = inverse(lower) if world_q is None else qmul(qmul(inverse(lower), inverse(pq)), world_q)


def staff_q(pitch=0., roll=0., yaw=0.):
    """World staff orientation: pitch tips the crown forward, roll outward."""
    q = axis((0, 0, 1), math.radians(yaw))
    q = qmul(q, axis((1, 0, 0), math.radians(roll)))
    return qmul(q, axis((0, 1, 0), math.radians(pitch)))


def hand_for_grip(grip, q):
    """Wrist target that places the rest grip at a world point for orientation q."""
    return sub(grip, rotate(q, sub(GRIP, REST[IDS['arm_R_end']])))


def leg_pole(side):
    """Knees bend forward and slightly outward, never across the midline."""
    return (1, .3 if side == 'L' else -.3, 0)


def plant_feet(pose, offsets=None):
    """Keep both soles level in world space: no automatic floor compensation."""
    for side in ('L', 'R'):
        d = (offsets or {}).get(side, (0, 0, 0))
        pose.reach(f'leg_{side}', add(REST[IDS[f'leg_{side}_end']], d), (0, 0, 0, 1), pole=leg_pole(side))


def pose(name, t):
    P = Pose()
    phase = math.tau*t
    rest_hand_L = REST[IDS['arm_L_end']]
    if name == 'idle':
        breath = math.sin(phase)
        P.shift[IDS['pelvis']] = (0, 0, -.15*breath)
        P.turn('chest', (0, 1, 0), -.9*breath)
        P.turn('neck', (0, 1, 0), .6*breath)
        P.turn('head', (0, 0, 1), 3.2*math.sin(phase+.6))
        P.turn('head', (0, 1, 0), 1.4*math.sin(2*phase))
        P.turn('jaw', (0, 1, 0), 2.2+2.2*math.sin(3*phase))
        plant_feet(P)
        P.reach('arm_L', add(rest_hand_L, (.4*math.sin(phase), 0, .5*math.sin(phase+.4))))
        P.reach('arm_R', hand_for_grip(add(GRIP, (0, 0, .2*breath)), staff_q()), staff_q())
    elif name == 'hobble':
        bob = math.cos(2*phase)
        P.shift[IDS['pelvis']] = (0, .55*math.sin(phase), -.55-.45*bob)
        P.turn('pelvis', (1, 0, 0), 2.2*math.sin(phase))
        P.turn('chest', (0, 1, 0), 1.4*bob)
        P.turn('chest', (0, 0, 1), -2.5*math.sin(phase))
        P.turn('head', (0, 1, 0), -1.2*bob)
        P.turn('head', (0, 0, 1), 2*math.sin(phase))
        offsets = {}
        for side, offset in (('L', 0), ('R', .5)):
            q = (t+offset) % 1
            if q < .6:
                dx, lift = 3.0-6.0*q/.6, 0
            else:
                u = smooth((q-.6)/.4)
                dx, lift = -3+6*u, 2.3*math.sin(math.pi*(q-.6)/.4)
            offsets[side] = (dx, 0, lift)
        plant_feet(P, offsets)
        q = t % 1  # the staff moves with the opposite (left) leg
        if q < .6:
            dx, lift = 2.4-4.8*q/.6, 0
        else:
            u = smooth((q-.6)/.4)
            dx, lift = -2.4+4.8*u, 2.6*math.sin(math.pi*(q-.6)/.4)
        sq = staff_q(pitch=-1.8*dx/2.4)
        P.reach('arm_R', hand_for_grip(add(GRIP, (dx, 0, lift)), sq), sq)
        P.reach('arm_L', add(rest_hand_L, (-1.6*math.sin(phase+.3), 0, .8*math.cos(phase))))
    elif name == 'cudgel':
        # Rear back with the staff lifted over the shoulder, then chop the
        # skull crown down and across toward the target; recover slowly.
        wind = window(t, 0, .36)*(1-window(t, .38, .5))
        strike = window(t, .36, .5)*(1-window(t, .68, 1))
        P.shift[IDS['pelvis']] = (2.2*strike-1.0*wind, 0, -1.3*strike+.3*wind)
        P.turn('spine', (0, 1, 0), -6*wind+10*strike)
        P.turn('chest', (0, 1, 0), -9*wind+18*strike)
        P.turn('chest', (0, 0, 1), 12*wind-9*strike)
        P.turn('neck', (0, 1, 0), -5*wind+4*strike)
        P.turn('head', (0, 1, 0), -8*wind+4*strike)
        P.turn('jaw', (0, 1, 0), 3+14*strike+7*wind)
        plant_feet(P)
        pitch = -28*wind+13*strike
        grip = add(GRIP, (-4.0*wind+6.0*strike, -1.0*wind+4.0*strike, 13.5*wind+4.5*strike))
        sq = staff_q(pitch=pitch, roll=14*wind-9*strike)
        P.reach('arm_R', hand_for_grip(grip, sq), sq)
        P.reach('arm_L', add(rest_hand_L, (1.0*wind+3.5*strike, -2.0*wind-1.0*strike, 9.0*wind-1.0*strike)))
    elif name == 'chant_strike':
        raise_ = window(t, 0, .44)*(1-window(t, .56, .68))
        jab = window(t, .56, .68)*(1-window(t, .8, 1))
        P.shift[IDS['pelvis']] = (1.4*jab, 0, .5*raise_-.5*jab)
        P.turn('spine', (0, 1, 0), -4*raise_+6*jab)
        P.turn('chest', (0, 1, 0), -8*raise_+12*jab)
        P.turn('neck', (0, 1, 0), -6*raise_)
        P.turn('head', (0, 1, 0), -12*raise_+4*jab)
        P.turn('head', (0, 0, 1), 4*math.sin(math.tau*2*t)*raise_)
        P.turn('jaw', (0, 1, 0), 2+15*raise_+9*jab+4*math.sin(math.tau*4*t)*raise_)
        plant_feet(P)
        grip = add(GRIP, (-1.2*raise_+5.5*jab, .6*raise_+1.6*jab, 8.5*raise_+.8*jab))
        sq = staff_q(pitch=-3*raise_+13*jab)
        P.reach('arm_R', hand_for_grip(grip, sq), sq)
        P.reach('arm_L', add(rest_hand_L, (2.2*raise_+4.2*jab, -2.2*raise_-3.2*jab, 16.5*raise_+2.5*jab)))
    elif name == 'recoil':
        pulse = math.sin(math.pi*clamp(t/.8))**2
        P.shift[IDS['pelvis']] = (-1.4*pulse, 0, -.4*pulse)
        P.turn('spine', (0, 1, 0), -5*pulse)
        P.turn('chest', (0, 1, 0), -8*pulse)
        P.turn('head', (0, 0, 1), -9*pulse)
        P.turn('head', (0, 1, 0), -7*pulse)
        P.turn('jaw', (0, 1, 0), 2+8*pulse)
        plant_feet(P)
        sq = staff_q(pitch=-6*pulse)
        P.reach('arm_R', hand_for_grip(add(GRIP, (-2.2*pulse, 0, 1.4*pulse)), sq), sq)
        P.reach('arm_L', add(rest_hand_L, (-1.5*pulse, .8*pulse, 5.5*pulse)))
    elif name == 'collapse':
        collapse_pose(P, t)
    return P.frame()


def collapse_pose(P, t):
    """Knees buckle, the body folds forward and the head drops toward the floor.

    The limp right hand never opens. The staff topples about its tip and comes
    to rest diagonally across the right knee and left haunch, its tip on the
    floor and its skull crown lowered behind the body.
    """
    sink = window(t, 0, .5)
    kneel = window(t, .1, .55)
    fold = window(t, .18, .8)
    settle = window(t, .66, .92)
    topple = window(t, .06, .74)**1.5
    P.shift[IDS['pelvis']] = (-2.8*sink-.6*settle, .3*settle, -13.2*sink-.2*settle)
    P.turn('pelvis', (0, 1, 0), 30*fold)
    P.turn('spine', (0, 1, 0), 32*fold)
    P.turn('chest', (0, 1, 0), 28*fold)
    P.turn('pelvis', (1, 0, 0), 7*settle)
    P.turn('chest', (1, 0, 0), 10*settle)
    P.turn('neck', (0, 1, 0), 14*fold)
    P.turn('head', (0, 1, 0), 12*fold)
    P.turn('head', (1, 0, 0), 20*settle)
    P.turn('head', (0, 0, 1), -12*settle)
    P.turn('jaw', (0, 1, 0), 3+15*fold)
    theta = 172*kneel
    for side, sign in (('L', 1), ('R', -1)):
        rest = REST[IDS[f'leg_{side}_end']]
        target = (-6.3, sign*9.8, 4.3)
        ankle = tuple(r+(q-r)*kneel for r, q in zip(rest, target))
        ankle = add(ankle, (0, 0, 7.2*math.sin(math.radians(theta))))
        P.reach(f'leg_{side}', ankle, axis((0, 1, 0), math.radians(theta)), pole=leg_pole(side))
    world = P.world()
    cpos, cq = world[IDS['chest']]
    def natural(bone):
        return add(cpos, rotate(cq, sub(REST[IDS[bone]], REST[IDS['chest']])))
    # Left arm goes limp; the knuckles come to rest on the floor.
    limp = window(t, .3, .88)
    target = tuple(a+(b-a)*limp for a, b in zip(natural('arm_L_end'), (12.5, 12.5, 6.2)))
    P.reach('arm_L', target, qmul(axis((0, 0, 1), math.radians(-25*limp)), axis((0, 1, 0), math.radians(-33*limp))),
            clamp_reach=True)
    # Staff pivots about its sliding tip, from upright to almost flat.
    elevation = math.radians(90-75*topple)
    heading = unit((-1, 1, 0))
    direction = (math.cos(elevation)*heading[0], math.cos(elevation)*heading[1], math.sin(elevation))
    sq = between((0, 0, 1), direction)
    tip_rest = bend(STAFF_TIP)
    tip = tuple(a+(b-a)*topple for a, b in zip(tip_rest, (29.6, -29.6, 1.25)))
    grip = sub(tip, rotate(sq, sub(tip_rest, GRIP)))
    P.reach('arm_R', hand_for_grip(grip, sq), sq)


def geometry():
    from .connected_skin import attach
    parts = attach('ogre_shaman', build_parts(), weights)
    return assemble(ogre_shaman_materials.connected_atlas(parts), weights)


def matrices(frame): return RIG.matrices(frame)
def deform(v, w, frame): return RIG.deform(v, w, frame)
def animation_data(v, w): return sample_clips(RIG, CLIPS, pose, v, w)


def texture_bytes():
    from .connected_skin import attach
    return ogre_shaman_materials.connected_atlas(attach('ogre_shaman', build_parts(), weights), True)


def build():
    skin = texture_bytes()
    (ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts, v, n, uv, tr, w = geometry()
    clips, bounds = animation_data(v, w)
    data = iqm.encode(v, n, uv, tr, w, BONES, clips, bounds, mesh_label='Project_Broom_ogre_shaman', material_path=SKIN)
    path = ROOT/'mod/BrogueDoom/models/monsters/27_ogre_shaman.iqm'
    path.write_bytes(data)
    manifest = dict(schemaVersion=1, workId='BRG-M27', format='IQM v2', runtimeModel=path.relative_to(ROOT).as_posix(),
                    sha256=hashlib.sha256(data).hexdigest(), skin=SKIN, skinSha256=hashlib.sha256(skin).hexdigest(),
                    dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v), 4) for a in range(3)],
                    parts=len(parts), vertices=len(v), triangles=len(tr), boneCount=len(BONES),
                    bones=[dict(name=n, parent=p, local=v) for n, p, v in BONES],
                    clips=[{k: v for k, v in c.items() if k != 'frames'} | dict(frameCount=len(c['frames'])) for c in clips],
                    poseBounds=bounds, authoringSource='assets/monsters/ogre_shaman/ogre-shaman-animated.blend')
    out = ROOT/'assets/monsters/ogre_shaman'
    out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    print(build()['sha256'])

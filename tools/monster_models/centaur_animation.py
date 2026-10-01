"""Original centaur archer: dun horse body joined to a lean human torso.

Brogue describes the centaur as half man and half horse, an expert with the
bow and arrow. Everything here is presentation only: the bow, string, quiver
and the nocked arrow add no light, projectile, collision, damage, targeting,
AI, turn or RNG behaviour. Brogue owns the actual bolt and its outcome.
+X is forward, Z is up and the floor is Z=0.
"""
import hashlib
import json
import math
from . import iqm, centaur_materials
from .creatures import Sculpt
from .rat import ROOT, Part, add, sub, mul, unit, cross, spline
from .skeletal import Rig, axis, between, inverse, qmul, rotate, assemble, sample_clips

SKIN = 'graphics/BRGCTR.png'


def mirror(p, sign): return (p[0], sign*p[1], p[2])


# Human arms: the left (bow) forearm is carried forward, the right hangs.
ARM_L = dict(upper=(13.2, 10.4, 59.0), lower=(13.6, 11.0, 48.6), end=(22.4, 13.6, 47.8))
ARM_R = dict(upper=(13.2, -10.4, 59.0), lower=(12.8, -11.1, 48.6), end=(16.8, -12.3, 40.6))
GRIP = (24.6, 12.0, 47.6)            # bow grip axis inside the closed left fist
FINGER_R = (17.35, -12.0, 35.5)      # draw-hand hook point inside the curled fingers (rest)
# Equine legs: shoulder/hip anchor, elbow|stifle, knee|hock, fetlock.
FORE = dict(shoulder=(11.2, 6.6, 38.0), upper=(9.8, 6.2, 27.2), lower=(11.6, 6.0, 15.0), end=(10.1, 6.0, 5.0))
HIND = dict(hip=(-18.6, 6.8, 36.0), upper=(-13.6, 7.0, 25.2), lower=(-20.4, 6.6, 14.6), end=(-18.6, 6.2, 5.0))
BRACE = 2.9                           # string sits this far behind the grip
BOW_HALF = 15.3                       # string anchors, above/below the grip
# Quiver on the back; its mouth rises behind the right shoulder.
Q_BOTTOM, Q_TOP = (4.6, 6.4, 48.8), (6.6, -6.4, 67.6)
ARROW_LEN = 21.0
ARROW_OUT = 4.6                      # nocks stand this far above the quiver mouth


def quiver_axis(): return unit(sub(Q_BOTTOM, Q_TOP))


def quiver_frame():
    d = quiver_axis()
    a = unit(cross(d, (1, 0, 0)))
    return d, a, cross(d, a)


def arrow_slots():
    """Nock positions of the carried arrows; slot 0 is the one that is drawn."""
    d, a, b = quiver_frame()
    out = []
    for i, (r, ang) in enumerate(((0.55, 2.2), (1.25, .3), (1.2, 1.5), (1.25, 2.7), (1.2, 3.9), (1.25, 5.1), (.5, 5.3))):
        offset = add(mul(a, r*math.cos(ang)), mul(b, r*math.sin(ang)))
        out.append(add(add(Q_TOP, offset), mul(d, -ARROW_OUT-.25*math.sin(i*2.1))))
    return out


NOCK_REST = arrow_slots()[0]

SPECS = [('root', None, (0, 0, 0)), ('pelvis', 'root', (-15, 0, 36)), ('barrel', 'pelvis', (-3, 0, 35.5)),
         ('withers', 'barrel', (9, 0, 38)), ('waist', 'withers', (13.2, 0, 46)), ('chest', 'waist', (13.5, 0, 54)),
         ('neck', 'chest', (13.2, 0, 62.5)), ('head', 'neck', (14.0, 0, 67.2))]
for side, sign in (('L', 1), ('R', -1)):
    joints = ARM_L if side == 'L' else ARM_R
    parent = 'chest'
    for joint in ('upper', 'lower', 'end'):
        SPECS.append((f'arm_{side}_{joint}', parent, joints[joint]))
        parent = f'arm_{side}_{joint}'
for side, sign in (('L', 1), ('R', -1)):
    parent = 'withers'
    for joint in ('shoulder', 'upper', 'lower', 'end'):
        SPECS.append((f'fore_{side}_{joint}', parent, mirror(FORE[joint], sign)))
        parent = f'fore_{side}_{joint}'
    parent = 'pelvis'
    for joint in ('hip', 'upper', 'lower', 'end'):
        SPECS.append((f'hind_{side}_{joint}', parent, mirror(HIND[joint], sign)))
        parent = f'hind_{side}_{joint}'
parent = 'pelvis'
TAIL = [(-24.4, 0, 40.6), (-26.4, 0, 37.0), (-27.3, 0, 31.4), (-27.4, 0, 25.0)]
for i, p in enumerate(TAIL):
    SPECS.append((f'tail_{i}', parent, p))
    parent = f'tail_{i}'
SPECS += [('bow', 'arm_L_end', GRIP), ('bow_top', 'bow', GRIP), ('bow_bottom', 'bow', GRIP),
          ('bow_string', 'bow', add(GRIP, (-BRACE, 0, 0))), ('arrow', 'chest', NOCK_REST)]
RIG = Rig.from_world(SPECS)
BONES, REST = RIG.bones, RIG.rest
IDS = {n: i for i, (n, p, v) in enumerate(BONES)}
CLIPS = [('idle', 48, 16, True), ('trot', 32, 35, True), ('shoot', 38, 35, False),
         ('rear_shot', 42, 35, False), ('flinch', 14, 35, False), ('fall', 46, 35, False)]


def clamp(v, lo=0., hi=1.): return max(lo, min(hi, v))


def smooth(x):
    x = clamp(x)
    return x*x*(3-2*x)


def window(t, a, b): return smooth((t-a)/(b-a))


# --- shapes -------------------------------------------------------------------

def horse_loft(name, rows, sides=40, samples=4):
    """Equine trunk lofted along +X: x, centre z, half width, back, belly.

    A soft superellipse gives the full, slightly squared barrel of a horse.
    """
    p = Part(name)
    rows = spline(rows, samples)
    for i, (x, zc, w, top, bottom) in enumerate(rows):
        for j in range(sides+1):
            a = math.tau*j/sides
            c, s = math.cos(a), math.sin(a)
            e = 2/2.5
            y = w*math.copysign(abs(s)**e, s)
            z = zc+(top if c > 0 else bottom)*math.copysign(abs(c)**e, c)
            p.vertex((x, y, z), 'fur', i/(len(rows)-1), j/sides)
    for i in range(len(rows)-1):
        for j in range(sides):
            a = i*(sides+1)+j
            p.faces.append((a, a+1, a+sides+2, a+sides+1))
    for end, reverse in ((0, True), (len(rows)-1, False)):
        x, zc = rows[end][:2]
        center = p.vertex((x, 0, zc), 'fur', end/(len(rows)-1), .5)
        for j in range(sides):
            a = end*(sides+1)+j
            p.faces.append((center, a+1, a) if reverse else (center, a, a+1))
    return p


def torso_loft(name, controls, sides=36, samples=4):
    """Human torso lofted up a gently bent path: x, z, half width, front, back."""
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
            p.vertex((x+nx*depth, width*s, z+nz*depth), 'fur', i/(len(rows)-1), j/sides)
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


HORSE = [(-25.6, 36.6, 2.2, 2.2, 2.2), (-24.4, 36.6, 6.4, 5.8, 6.8), (-21.0, 36.3, 9.2, 7.6, 9.3),
         (-15.5, 35.6, 9.9, 8.1, 9.9), (-9.0, 35.1, 10.1, 7.2, 10.2), (-2.5, 35.1, 10.5, 7.3, 10.8),
         (4.0, 35.6, 10.1, 8.2, 10.6), (9.5, 36.5, 9.0, 8.7, 9.8), (13.5, 37.5, 7.5, 7.7, 8.4),
         (16.3, 38.5, 4.9, 5.1, 5.8), (17.6, 39.0, 1.6, 1.6, 1.6)]
TORSO = [(12.5, 36.0, 8.4, 6.0, 7.0), (13.0, 41.0, 8.0, 5.8, 6.0), (13.4, 45.0, 7.4, 5.2, 5.0),
         (13.6, 48.5, 6.5, 4.8, 4.2), (13.7, 51.5, 6.9, 5.0, 4.2), (13.6, 54.5, 8.1, 5.5, 4.5),
         (13.4, 57.5, 9.3, 5.4, 4.7), (13.1, 60.0, 9.6, 4.6, 4.5), (13.0, 61.8, 7.6, 3.8, 4.0),
         (13.2, 63.2, 3.4, 2.7, 3.0), (13.6, 65.0, 2.8, 2.4, 2.6), (14.0, 66.8, 2.7, 2.3, 2.4)]


def vane(name, base, direction, radial, length, height, thickness=.07):
    """Thin closed fletching vane in the plane of the shaft and a radial."""
    p = Part(name)
    side = unit(cross(direction, radial))
    outline = [(0, .15), (length, .15), (length*.82, height), (length*.18, height*.8)]
    for layer in (-1, 1):
        for i, (s, h) in enumerate(outline):
            co = add(add(add(base, mul(direction, s)), mul(radial, h)), mul(side, layer*thickness))
            p.vertex(co, 'whisker', .1+.8*i/3, .2 if layer < 0 else .8)
    p.faces += [(3, 2, 1, 0), (4, 5, 6, 7)]
    for i in range(4):
        j = (i+1) % 4
        p.faces.append((i, j, j+4, i+4))
    return p


def build_arrow(s, name, nock, direction, spin=0.):
    d = unit(direction)
    ref = (0, 0, 1) if abs(d[2]) < .9 else (1, 0, 0)
    a = unit(cross(d, ref))
    b = cross(d, a)
    s.strand(f'{name}_shaft', [(*add(nock, mul(d, .3)), .2), (*add(nock, mul(d, ARROW_LEN-1.6)), .21)], 'wood', 8, 1)
    s.oval(f'{name}_nock', add(nock, mul(d, .35)), (.3, .3, .3), 'bone', 8, 6)
    head = add(nock, mul(d, ARROW_LEN-1.9))
    s.strand(f'{name}_head', [(*head, .24), (*add(head, mul(d, .6)), .5), (*add(head, mul(d, 1.4)), .36),
                              (*add(head, mul(d, 1.9)), .02)], 'bone', 8, 2)
    for k in range(3):
        ang = spin+math.tau*k/3
        radial = add(mul(a, math.cos(ang)), mul(b, math.sin(ang)))
        s.parts.append(vane(f'{name}_vane{k}', add(nock, mul(d, .9)), d, radial, 3.6, 1.05))


def limb_curve(sign):
    """Recurve bow limb centreline in grip-relative (x, z); tips recurve forward."""
    pts = [(0, 1.9, .66), (-.35, 5.0, .6), (-1.1, 8.5, .52), (-2.0, 11.5, .45), (-2.55, 13.8, .4),
           (-2.45, 15.3, .36), (-1.85, 16.6, .3)]
    return [(x, sign*z, r) for x, z, r in pts]


def build_bow(s):
    gx, gy, gz = GRIP
    s.strand('bow_grip', [(gx, gy, gz-2.4, .8), (gx, gy, gz, .84), (gx, gy, gz+2.4, .8)], 'wood', 12, 2)
    for tag, sign in (('top', 1), ('bottom', -1)):
        pts = [(gx+x, gy, gz+z, r) for x, z, r in limb_curve(sign)]
        limb = s.strand(f'bow_limb_{tag}', pts, 'wood', 10, 5)
        # Flatten the limb: wide across the bow plane, thin front to back.
        cx = {round(v[2], 3): v for v in limb.vertices}
        limb.vertices = [(v[0], gy+(v[1]-gy)*1.45, v[2]) for v in limb.vertices]
        tip = pts[-2]
        s.oval(f'bow_horn_{tag}', (tip[0]+.25, gy, tip[2]+sign*.7), (.42, .5, 1.0), 'accent', 10, 8)
        for i, z in enumerate((3.2, 3.8)):
            s.strand(f'bow_wrap_{tag}{i}', [(gx+.95*math.cos(a)-.2*(z > 3.5), gy+1.0*math.sin(a), gz+sign*z, .16)
                                            for a in (math.tau*j/14 for j in range(15))], 'cloth', 6, 1)
        # String: nock point (bow_string) to limb anchor, many rows for a smooth draw.
        anchor = (gx-BRACE, gy, gz+sign*BOW_HALF)
        rows = [(gx-BRACE, gy, gz+sign*BOW_HALF*k/8, .13) for k in range(9)]
        s.strand(f'bow_string_{tag}', rows, 'cloth', 6, 1)
    s.strand('bow_arrow_rest', [(gx+.2, gy+.75, gz+2.2, .28), (gx+.2, gy+.95, gz+2.8, .22)], 'accent', 6, 1)


def ring(center, radius, direction, count=24):
    d = unit(direction)
    a = unit(cross(d, (0, 0, 1) if abs(d[2]) < .9 else (1, 0, 0)))
    b = cross(d, a)
    return [add(center, add(mul(a, radius*math.cos(t)), mul(b, radius*math.sin(t))))
            for t in (math.tau*i/count for i in range(count+1))]


def build_quiver(s):
    d = quiver_axis()
    length = math.dist(Q_BOTTOM, Q_TOP)
    pts = []
    for k, (f, r) in enumerate(((0, 1.6), (.03, 2.2), (.25, 2.35), (.6, 2.3), (.9, 2.45), (.985, 2.7), (1, 2.62))):
        pts.append((*add(Q_TOP, mul(d, length*(1-f))), r))
    s.strand('quiver_body', pts[::-1], 'cloth', 16, 3)
    for i, f in enumerate((.12, .5, .88)):
        c = add(Q_TOP, mul(d, length*f))
        s.strand(f'quiver_band{i}', [(*q, .26) for q in ring(c, 2.45 if f < .8 else 2.5, d, 18)], 'accent', 6, 1)
    for i, (nock, spin) in enumerate(zip(arrow_slots()[1:], (.2, 1.1, 2.3, .7, 1.8, 2.9))):
        build_arrow(s, f'quiver_arrow{i}', nock, d, spin)
    # Strap: quiver mouth over the right shoulder, across the chest to the left hip.
    s.strand('strap_front', [(7.6, -6.6, 64.6, .42), (11.0, -8.6, 63.4, .45), (14.8, -7.6, 61.6, .45),
                             (18.4, -4.2, 57.2, .45), (19.2, 0.0, 53.4, .45), (18.6, 4.0, 50.0, .45),
                             (16.4, 7.0, 47.6, .45), (12.4, 7.9, 46.4, .45), (7.6, 7.4, 47.0, .42),
                             (5.0, 6.6, 49.8, .4)], 'cloth', 8, 3)
    s.oval('strap_buckle', (19.35, 0.0, 53.4), (.5, 1.1, .8), 'bone', 10, 8)


def build_parts():
    s = Sculpt()
    # --- equine trunk and legs ---
    s.parts.append(horse_loft('horse_body', HORSE))
    for side, sign in (('L', 1), ('R', -1)):
        s.oval(f'fore_{side}_scapula', (10.4, sign*6.2, 36.0), (5.2, 2.9, 7.4))
        s.oval(f'fore_{side}_breast', (14.4, sign*3.9, 32.6), (2.3, 2.7, 4.2))
        s.oval(f'hind_{side}_thigh', (-17.0, sign*7.5, 30.4), (6.2, 2.9, 7.6))
        s.oval(f'hind_{side}_buttock', (-22.2, sign*4.7, 33.6), (3.0, 3.3, 5.6))
        sh, el, kn, fe = (mirror(FORE[j], sign) for j in ('shoulder', 'upper', 'lower', 'end'))
        s.strand(f'fore_{side}_forearm', [(*add(el, (.4, 0, 3.6)), 3.5), (*el, 3.1), (*add(el, mul(sub(kn, el), .45)), 2.3),
                                          (*add(kn, (0, 0, 2.2)), 1.75), (*kn, 1.8)], sides=16, samples=4)
        s.oval(f'fore_{side}_knee', add(kn, (.35, 0, 0)), (1.75, 1.9, 2.1))
        s.strand(f'fore_{side}_cannon', [(*kn, 1.55), (*add(kn, mul(sub(fe, kn), .5)), 1.22), (*add(fe, (0, 0, 1.2)), 1.3)],
                 sides=14, samples=3)
        s.oval(f'fore_{side}_fetlock', add(fe, (-.15, 0, 0)), (1.8, 1.65, 1.75))
        s.strand(f'fore_{side}_pastern', [(*fe, 1.4), (*add(fe, (.9, 0, -1.4)), 1.25), (*add(fe, (1.5, 0, -2.3)), 1.35)],
                 sides=14, samples=2)
        s.oval(f'fore_{side}_elbow', add(el, (-2.0, 0, .6)), (2.2, 2.2, 2.4))
        hp, st, hk, hf = (mirror(HIND[j], sign) for j in ('hip', 'upper', 'lower', 'end'))
        s.strand(f'hind_{side}_gaskin', [(*add(st, (.8, 0, 2.2)), 3.4), (*st, 3.3), (*add(st, mul(sub(hk, st), .5)), 2.4),
                                         (*add(hk, (.6, 0, 1.3)), 1.8), (*hk, 1.6)], sides=16, samples=4)
        s.oval(f'hind_{side}_hock', add(hk, (-.7, 0, .3)), (1.7, 1.55, 2.3))
        s.strand(f'hind_{side}_cannon', [(*hk, 1.6), (*add(hk, mul(sub(hf, hk), .5)), 1.25), (*add(hf, (0, 0, 1.2)), 1.3)],
                 sides=14, samples=3)
        s.oval(f'hind_{side}_fetlock', add(hf, (-.2, 0, 0)), (1.8, 1.6, 1.7))
        s.strand(f'hind_{side}_pastern', [(*hf, 1.35), (*add(hf, (.8, 0, -1.4)), 1.2), (*add(hf, (1.35, 0, -2.3)), 1.3)],
                 sides=14, samples=2)
        s.oval(f'hind_{side}_stifle', add(st, (1.2, 0, .4)), (1.9, 2.3, 2.2))
        # Hooves: hard keratin, separate from the skin.
        for limb, fe_ in (('fore', fe), ('hind', hf)):
            c = add(fe_, (1.55 if limb == 'fore' else 1.4, 0, -3.8))
            s.strand(f'hoof_{limb}_{side}', [(c[0]-.1, c[1], 2.55, 1.55), (c[0]+.1, c[1], 1.7, 1.9), (c[0]+.35, c[1], .75, 2.2),
                                              (c[0]+.4, c[1], .24, 2.25)], 'dark', 16, 2)
            for k in range(7):
                ang = math.pi*.35+math.pi*1.3*k/6
                base = (c[0]-.1+1.55*math.cos(ang), c[1]+1.55*math.sin(ang), 2.9)
                tip = (c[0]-.1+2.25*math.cos(ang)-.4, c[1]+2.3*math.sin(ang), 1.2)
                s.strand(f'feather_{limb}_{side}{k}', [(*base, .45), (*tip, .08)], 'glow', 6, 1)
    s.strand('tail_dock', [(-23.4, 0, 40.6, 2.4), (-24.8, 0, 39.8, 2.1), (-26.0, 0, 38.0, 1.6)], sides=16, samples=2)
    # --- human torso, head and arms ---
    s.parts.append(torso_loft('torso', TORSO))
    for sign in (-1, 1):
        side = 'L' if sign > 0 else 'R'
        up = (ARM_L if sign > 0 else ARM_R)['upper']
        # Broad pectoral plates whose lower edge lifts toward the armpit.
        s.oval(f'torso_pec_{sign}', (16.9, sign*3.7, 56.9), (2.1, 3.6, 2.3))
        s.oval(f'torso_pec_{sign}_outer', (15.7, sign*6.3, 57.8), (1.8, 2.0, 1.8))
        # Ribcage flare under the arm; lats narrowing into the waist.
        s.oval(f'torso_rib_{sign}', (14.4, sign*5.5, 53.2), (3.4, 2.4, 3.2))
        s.oval(f'torso_lat_{sign}', (12.4, sign*6.1, 55.2), (2.6, 1.8, 3.8))
        # Sternocleidomastoid from behind the ear down to the collarbone notch.
        s.strand(f'torso_scm_{sign}', [(13.9, sign*2.6, 68.2, .7), (15.2, sign*1.7, 64.4, .75), (16.1, sign*.8, 61.6, .6)],
                 'body', 10, 3)
        # Rounded deltoid cap wrapping the shoulder joint, with its front head.
        s.oval(f'shoulder_{side}_delt', add(up, (.1, sign*.05, -1.3)), (3.1, 2.6, 3.5))
        s.oval(f'shoulder_{side}_delt_front', add(up, (1.4, -sign*.3, -2.2)), (1.7, 2.0, 2.5))
        # Trapezius: a gentle slope from the neck out to the shoulder top.
        s.strand(f'shoulder_{side}_trap', [(12.6, sign*1.8, 65.0, 1.9), (12.5, sign*4.8, 63.0, 1.8), (12.7, sign*8.4, 61.6, 1.5)],
                 'body', 14, 3)
    s.oval('head_cranium', (13.6, 0, 71.2), (4.4, 3.8, 4.5), 'body', 28, 16)
    s.oval('head_face', (15.6, 0, 69.4), (2.8, 3.1, 3.6), 'body', 24, 14)
    s.oval('head_jaw', (15.9, 0, 66.7), (2.5, 2.9, 1.9), 'body', 24, 12)
    s.oval('head_chin', (17.5, 0, 65.9), (1.2, 1.6, 1.15), 'body', 16, 10)
    s.strand('head_nose', [(17.95, 0, 71.3, .42), (18.55, 0, 70.1, .55), (19.1, 0, 68.7, .66), (19.2, 0, 68.1, .55),
                           (18.8, 0, 67.75, .4)], 'body', 14, 3)
    s.strand('head_brow', [(17.0, -3.1, 71.2, .62), (17.95, -1.6, 71.7, .78), (18.25, 0, 71.45, .6),
                           (17.95, 1.6, 71.7, .78), (17.0, 3.1, 71.2, .62)], 'body', 12, 3)
    for sign in (-1, 1):
        s.oval(f'head_cheek_{sign}', (16.95, sign*2.55, 69.55), (1.05, 1.15, .75), 'body', 14, 10)
        s.oval(f'head_ear_{sign}', (13.7, sign*3.75, 70.0), (.85, .45, 1.35), 'body', 14, 10)
        s.oval(f'head_nostril_{sign}', (18.65, sign*.62, 68.1), (.55, .45, .4), 'body', 10, 8)
    for side, joints, sign in (('L', ARM_L, 1), ('R', ARM_R, -1)):
        up, lo, end = joints['upper'], joints['lower'], joints['end']
        mid = add(up, mul(sub(lo, up), .42))
        fore = add(lo, mul(sub(end, lo), .3))
        s.strand(f'arm_{side}', [(*add(up, (0, 0, .3)), 2.6), (*mid, 2.3), (*add(lo, mul(sub(up, lo), .12)), 1.75),
                                 (*lo, 1.7), (*fore, 1.9), (*end, 1.35)], sides=18, samples=4)
        s.oval(f'arm_{side}_bicep', add(mid, (1.1, 0, -.6)), (1.7, 1.9, 3.0))
        s.oval(f'arm_{side}_tricep', add(mid, (-1.0, 0, -.2)), (1.4, 1.6, 2.8))
    build_hands(s)
    # --- accessories: eyes, hair, beard, bracer, quiver, bow ---
    for sign in (-1, 1):
        # Eyes sit under the heavy brow, half-covered by an upper lid.
        s.oval(f'eye_white_{sign}', (17.72, sign*1.45, 70.2), (.26, .5, .27), 'bone', 14, 8)
        s.strand(f'eye_socket_lash_{sign}', [(17.93, sign*.98, 70.46, .06), (18.08, sign*1.45, 70.56, .07),
                                             (17.93, sign*1.95, 70.45, .06)], 'dark', 6, 3)
        s.oval(f'eye_iris_{sign}', (17.92, sign*1.43, 70.18), (.12, .25, .24), 'accent', 12, 8)
        s.oval(f'eye_pupil_{sign}', (17.99, sign*1.43, 70.18), (.06, .11, .12), 'dark', 10, 6)
        s.strand(f'eyelid_upper_{sign}', [(17.85, sign*.95, 70.52, .14), (18.0, sign*1.45, 70.64, .15),
                                          (17.85, sign*1.98, 70.5, .13)], 'body', 8, 3)
        s.strand(f'eyelid_lower_{sign}', [(17.88, sign*1.0, 69.9, .09), (17.97, sign*1.45, 69.8, .1),
                                          (17.86, sign*1.95, 69.92, .09)], 'body', 8, 3)
        s.strand(f'hair_brow_{sign}', [(18.05, sign*.55, 71.72, .26), (18.3, sign*1.7, 71.9, .3),
                                       (17.75, sign*2.9, 71.62, .2)], 'glow', 8, 2)
        s.strand(f'hair_moustache_{sign}', [(19.0, sign*.3, 67.3, .3), (18.9, sign*1.3, 67.0, .32),
                                            (18.4, sign*2.1, 66.2, .22)], 'glow', 8, 2)
        s.strand(f'hair_sideburn_{sign}', [(14.7, sign*3.35, 69.6, .55), (15.1, sign*3.25, 68.2, .55),
                                           (15.5, sign*3.0, 66.8, .45)], 'glow', 8, 3)
    # Scalp shell under combed-back locks gathered into a bun.
    s.oval('hair_cap', (13.0, 0, 72.0), (4.5, 3.95, 4.2), 'glow', 28, 16)
    for i in range(11):
        y = (i-5)*.72
        front = 17.0-.1*y*y
        pts = []
        for k, x in enumerate((front, 15.5, 13.5, 11.3, 9.6)):
            dx, dy = (x-13.6)/4.4, y/3.8
            z = 71.2+4.5*math.sqrt(max(0, 1-dx*dx-dy*dy))+.3
            pts.append((x, y*(1-.3*k/4), z, .55 if 0 < k < 4 else .35))
        s.strand(f'hair_comb_{i}', pts, 'glow', 8, 3)
    s.oval('hair_bun', (8.7, 0, 72.6), (1.9, 1.8, 1.7), 'glow', 16, 10)
    s.strand('hair_tie', [(9.9+.1*math.cos(a), 1.1*math.cos(a), 72.6+1.1*math.sin(a), .22) for a in
                          (math.tau*i/16 for i in range(17))], 'cloth', 6, 1)
    for i in range(5):
        y = (i-2)*1.1
        s.strand(f'hair_lock_{i}', [(9.4, y*.6, 71.8, .45), (8.4, y, 70.3-.3*abs(i-2), .38), (8.3, y*1.1, 67.8-.4*abs(i-2), .15)],
                 'glow', 8, 2)
    # Short beard: a thin shell over the jaw with broken tufts along its edge.
    s.oval('hair_beard', (16.4, 0, 66.15), (2.6, 3.02, 1.95), 'glow', 24, 12)
    for i in range(13):
        a = math.radians(-100+200*i/12)
        root = (16.0+2.3*math.cos(a), 2.8*math.sin(a), 65.0+.5*abs(math.sin(a)))
        drop = 1.4+.5*(abs(math.degrees(a)) < 30)+.2*math.sin(i*2.7)
        tip = add(root, (.35*math.cos(a)+.2, .3*math.sin(a), -drop))
        s.strand(f'hair_tuft_{i}', [(*root, .42), (*add(root, mul(sub(tip, root), .5)), .3), (*tip, .05)], 'glow', 8, 2)
    # Short dark mane along the withers crest behind the rider's back.
    for i in range(8):
        x = 3.0+.8*i
        top = 43.8+1.4*clamp((x-4)/5.5)
        s.strand(f'mane_{i}', [(x, .35*math.sin(i*1.9), top-.4, .6), (x-.8, .5*math.sin(i*1.9), top+.6, .4),
                               (x-1.5, .6*math.sin(i*1.9), top+1.2, .08)], 'wood', 8, 2)
    # Leather bracer on the bow forearm and a cord wrist wrap on the draw arm.
    lo, end = ARM_L['lower'], ARM_L['end']
    s.strand('bracer', [(*add(lo, mul(sub(end, lo), .35)), 2.2), (*add(lo, mul(sub(end, lo), .62)), 2.15),
                        (*add(lo, mul(sub(end, lo), .9)), 1.72)], 'cloth', 16, 2)
    for i, f in enumerate((.42, .6, .78)):
        c = add(lo, mul(sub(end, lo), f))
        s.strand(f'bracer_lace{i}', [(*q, .15) for q in ring(c, 2.25-.45*f, sub(end, lo), 14)], 'accent', 6, 1)
    build_quiver(s)
    build_bow(s)
    build_arrow(s, 'arrow', NOCK_REST, quiver_axis(), .5)
    build_tail(s)
    for part in s.parts:
        part.vertices = [tuple(round(c, 6)+0. for c in v) for v in part.vertices]
    return centaur_materials.repack(s.parts)


def build_tail(s):
    """Long dark horse tail: several tapered locks hanging from the dock."""
    for i, (dy, dx, length, r) in enumerate(((0, 0, 1, 1.6), (-.9, .3, .93, 1.2), (.9, .3, .95, 1.2),
                                              (-.5, -.6, .86, 1.0), (.5, -.6, .9, 1.0), (0, -.9, .8, .9))):
        pts = []
        for k, (x, y, z) in enumerate([(-24.9, 0, 39.2), (-26.8, 0, 36.2), (-27.5, 0, 30.6), (-27.4, 0, 24.4), (-27.0, 0, 18.2)]):
            f = k/4
            z = 39.6-(39.6-z)*length
            pts.append((x+dx*f, y+dy*f*1.4, z, r*(1-.55*f)*(.75 if k == 0 else 1)))
        pts[-1] = (*pts[-1][:3], .12)
        s.strand(f'tail_lock{i}', pts, 'wood', 10, 3)


def build_hands(s):
    """Left fist closed around the vertical bow grip; right hand loosely hooked."""
    gx, gy, gz = GRIP
    wx, wy, wz = ARM_L['end']
    s.oval('hand_L_palm', (gx-1.55, gy+.9, gz+.05), (1.6, 1.15, 2.2))
    for i in range(4):
        z = gz+1.5-i*1.0
        pts = [(gx-1.7, gy+1.6, z)]
        for k in range(1, 6):
            a = math.radians(125-k*52)
            pts.append((gx+1.4*math.cos(a), gy+1.4*math.sin(a)*1.02, z-.05*k))
        s.strand(f'hand_L_finger{i}', [(*p, .52-.035*k) for k, p in enumerate(pts)], 'body', 10, 3)
    s.strand('hand_L_thumb', [(gx-1.6, gy+1.4, gz+1.9, .62), (gx-.3, gy+.3, gz+2.2, .52), (gx+.9, gy-.9, gz+1.9, .42)], 'body', 10, 3)
    rx, ry, rz = ARM_R['end']
    s.oval('hand_R_palm', (rx+.2, ry-.05, rz-2.2), (1.4, .95, 2.1))
    # Relaxed right hand: separate, slightly curled and spread fingers and a
    # thumb, kept out of the fused cage so they stay individually readable.
    for i, length in enumerate((1.0, 1.1, 1.0, .82)):
        x = rx+1.25-i*.72
        spread = (i-1.5)*.18
        base = (x, ry+.05, rz-3.9)
        mid = (x+.15*length, ry+.45-spread, rz-3.9-1.3*length)
        tip = (x+.3*length, ry+1.25-spread*1.6, rz-3.9-1.95*length)
        s.strand(f'digit_R_finger{i}', [(*base, .4), (*mid, .34), (*tip, .26)], 'body', 10, 3)
        s.oval(f'digit_R_knuckle{i}', (x, ry-.05, rz-3.85), (.42, .42, .42), 'body', 8, 6)
    s.strand('digit_R_thumb', [(rx+1.0, ry+.55, rz-2.4, .48), (rx+1.6, ry+.95, rz-3.7, .4),
                               (rx+1.65, ry+1.15, rz-4.7, .3)], 'body', 10, 3)


# --- weights ------------------------------------------------------------------

def sharp_chain(point, chain, k=.24):
    """Rigid segments that blend only near each joint (crisp equine joints)."""
    ids = [IDS[b] for b in chain]
    best = None
    for n, (a, b) in enumerate(zip(ids, ids[1:])):
        start, end = REST[a], REST[b]
        d = sub(end, start)
        t = clamp(sum(x*y for x, y in zip(sub(point, start), d))/sum(x*x for x in d))
        distance = math.dist(point, add(start, mul(d, t)))
        if best is None or distance < best[0]-1e-9:
            best = (distance, n, t)
    _, n, t = best
    a, b = ids[n], ids[n+1]
    if n == len(ids)-2 and t >= 1:
        return [(b, 1)]
    wb = .5*smooth((t-(1-k))/k)
    out = {a: 1-wb, b: wb}
    if n > 0 and t < k:
        wp = .5*smooth((k-t)/k)
        out = {ids[n-1]: wp, a: (1-wp)*(1-wb), b: (1-wp)*wb}
    return [(i, w) for i, w in out.items() if w > 1e-9]


LEG = {'fore': ('shoulder', 'upper', 'lower', 'end'), 'hind': ('hip', 'upper', 'lower', 'end')}


def weights(part, v, uv):
    """Quantised skin weights: Python 3.12's compensated float sum() in Blender
    differs from system Python in the last bits, so round to 1e-6 and give the
    final influence the exact complement to keep bake fingerprints identical."""
    raw = raw_weights(part, v, uv)
    if len(raw) == 1:
        return [(raw[0][0], 1)]
    out = [(b, round(w, 6)) for b, w in raw[:-1]]
    rest = 1.
    for b, w in out:
        rest -= w
    result = [(b, w) for b, w in out if w > 0]+([(raw[-1][0], rest)] if rest > 0 else [])
    return [(result[0][0], 1)] if len(result) == 1 else result


def raw_weights(part, v, uv):
    n = part.name
    if n.startswith('bow_limb_top') or n.startswith('bow_wrap_top') or n == 'bow_horn_top':
        t = clamp((v[2]-GRIP[2]-1.8)/13.6)**1.2 if n.startswith('bow_limb') else 1
        return [(IDS['bow'], 1-t), (IDS['bow_top'], t)] if t < 1 else [(IDS['bow_top'], 1)]
    if n.startswith('bow_limb_bottom') or n.startswith('bow_wrap_bottom') or n == 'bow_horn_bottom':
        t = clamp((GRIP[2]-v[2]-1.8)/13.6)**1.2 if n.startswith('bow_limb') else 1
        return [(IDS['bow'], 1-t), (IDS['bow_bottom'], t)] if t < 1 else [(IDS['bow_bottom'], 1)]
    if n.startswith('bow_string'):
        tag = n.split('_')[-1]
        t = clamp(round(abs(v[2]-GRIP[2])/BOW_HALF, 9))
        return [(IDS['bow_string'], 1-t), (IDS['bow_'+tag], t)] if 0 < t < 1 else [(IDS['bow_string'] if t == 0 else IDS['bow_'+tag], 1)]
    if n.startswith('bow'):return [(IDS['bow'], 1)]
    if n.startswith('arrow'):return [(IDS['arrow'], 1)]
    if n.startswith(('quiver', 'strap')):return [(IDS['chest'], 1)]
    if n.startswith(('hoof_', 'feather_')):
        limb, side = n.split('_')[1], n.split('_')[2][0]
        return [(IDS[f'{limb}_{side}_end'], 1)]
    if n.startswith('tail'):
        if n == 'tail_dock':return RIG.chain_weights(v, [IDS['pelvis'], IDS['tail_0'], IDS['tail_1']])
        return RIG.chain_weights(v, [IDS[f'tail_{i}'] for i in range(4)])
    if n.startswith(('head', 'eye', 'hair')):return [(IDS['head'], 1)]
    if n.startswith('hand_L'):return [(IDS['arm_L_end'], 1)]
    if n.startswith(('hand_R', 'digit_R')):return [(IDS['arm_R_end'], 1)]
    if n.startswith('bracer'):return RIG.chain_weights(v, [IDS['arm_L_lower'], IDS['arm_L_end']])
    if n.startswith('shoulder_'):
        side = n.split('_')[1]
        t = clamp((abs(v[1])-6.5)/5)
        return [(IDS['chest'], 1-t), (IDS[f'arm_{side}_upper'], t)] if t < 1 else [(IDS[f'arm_{side}_upper'], 1)]
    if n.startswith('arm_'):
        side = n.split('_')[1]
        return RIG.chain_weights(v, [IDS[f'arm_{side}_{j}'] for j in ('upper', 'lower', 'end')])
    if n.startswith(('fore_', 'hind_')):
        limb, side = n.split('_')[:2]
        chain = [f'{limb}_{side}_{j}' for j in LEG[limb]]
        if n.endswith(('scapula', 'breast', 'thigh', 'buttock')):
            parent = 'withers' if limb == 'fore' else 'pelvis'
            top = 34.0 if limb == 'fore' else 31.0
            t = clamp((top-v[2])/9)*(.9 if n.endswith(('scapula', 'thigh')) else .5)
            return [(IDS[parent], 1-t), (IDS[chain[0]], t)] if t > 0 else [(IDS[parent], 1)]
        return sharp_chain(v, chain)
    if n.startswith('torso'):
        return RIG.chain_weights(v, [IDS[b] for b in ('withers', 'waist', 'chest', 'neck', 'head')])
    # Horse trunk: hindquarters to forehand.
    return RIG.chain_weights(v, [IDS[b] for b in ('pelvis', 'barrel', 'withers')])


# --- posing -------------------------------------------------------------------

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

    def place(self, bone, position, q):
        """Set a bone's world position/orientation through its parent's frame."""
        i = IDS[bone]
        pw, pq = self.world()[BONES[i][1]]
        local = rotate(inverse(pq), sub(position, pw))
        self.shift[i] = sub(local, BONES[i][2])
        self.rot[i] = qmul(inverse(pq), q)

    def reach(self, chain, target, world_q=None, pole=None, clamp_reach=False, joints=('upper', 'lower', 'end')):
        """Two-bone IK to a world target, solved in the parent's frame."""
        ids = [IDS[f'{chain}_{j}'] for j in joints]
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
        pole = sub(joint, REST[ids[0]]) if pole is None else rotate(inverse(pq), pole)
        bend = unit(sub(pole, mul(direction, sum(x*y for x, y in zip(pole, direction)))))
        knee = add(root, add(mul(direction, along), mul(bend, math.sqrt(max(0, a*a-along*along)))))
        upper = between(sub(joint, REST[ids[0]]), sub(knee, root))
        lower = between(sub(end, joint), sub(local, knee))
        self.rot[ids[0]] = upper
        self.rot[ids[1]] = qmul(inverse(upper), lower)
        self.rot[ids[2]] = inverse(lower) if world_q is None else qmul(qmul(inverse(lower), inverse(pq)), world_q)


def slerp(a, b, t):
    d = sum(x*y for x, y in zip(a, b))
    if d < 0:
        b, d = tuple(-x for x in b), -d
    if d > .9995:
        q = tuple(x+(y-x)*t for x, y in zip(a, b))
    else:
        th = math.acos(d)
        s = math.sin(th)
        q = tuple(x*math.sin((1-t)*th)/s+y*math.sin(t*th)/s for x, y in zip(a, b))
    n = math.sqrt(sum(x*x for x in q))
    return tuple(x/n for x in q)


def lerp(a, b, t): return tuple(x+(y-x)*t for x, y in zip(a, b))


POLE = {'fore': (1, 0, 0), 'hind': (-1, 0, 0)}


def plant_hooves(P, offsets=None, flex=None):
    """IK every leg to its hoof target; planted hooves stay level in world space."""
    for limb in ('fore', 'hind'):
        for side in ('L', 'R'):
            key = f'{limb}_{side}'
            d = (offsets or {}).get(key, (0, 0, 0))
            q = (flex or {}).get(key, (0, 0, 0, 1))
            # The scapula/hip swings the whole leg toward its hoof target first.
            anchor = f'{key}_{"shoulder" if limb == "fore" else "hip"}'
            P.turn(anchor, (0, 1, 0), -math.degrees(math.atan2(d[0], 30))*.8)
            P.reach(key, add(REST[IDS[f'{key}_end']], d), q, POLE[limb])


CARRY_CANT = -14.0
CARRY_PITCH = 8.0
CARRY_DROP = (0, 0, -4.0)


def grip_q(pitch=0., cant=0., yaw=0.):
    """World bow orientation: pitch tilts the top limb forward, cant to the right."""
    q = axis((0, 0, 1), math.radians(yaw))
    q = qmul(q, axis((0, 1, 0), math.radians(pitch)))
    return qmul(q, axis((1, 0, 0), math.radians(cant)))


def hand_for_grip(grip, q):
    """Wrist target that places the rest grip at a world point for orientation q."""
    return sub(grip, rotate(q, sub(GRIP, REST[IDS['arm_L_end']])))


def wrist_for_finger(point, q):
    return sub(point, rotate(q, sub(FINGER_R, REST[IDS['arm_R_end']])))


def breathe(P, phase, amount=1.):
    b = math.sin(phase)*amount
    P.turn('chest', (0, 1, 0), -.8*b)
    P.turn('neck', (0, 1, 0), .5*b)


def tail_sway(P, phase, amp=4., lift=0.):
    for i in range(4):
        P.turn(f'tail_{i}', (0, 0, 1), amp*math.sin(phase-i*.7))
        if lift:P.turn(f'tail_{i}', (0, 1, 0), -lift*(1-i*.2))


def carry(cpos, cq, offset=(0, 0, 0), pitch=0.):
    """Carried bow: held low at the side, top limb tipped forward and canted
    outward so it stays clear of the face. Shared by every clip's rest pose."""
    q = qmul(cq, grip_q(CARRY_PITCH+pitch, CARRY_CANT))
    g = add(cpos, rotate(cq, sub(add(add(GRIP, CARRY_DROP), offset), REST[IDS['chest']])))
    return g, q


def idle_arms(P, phase, drift=0.):
    world = P.world()
    cpos, cq = world[IDS['chest']]
    g, q = carry(cpos, cq)
    g = add(g, (.25*math.sin(phase), 0, .3*math.sin(phase+.5)+drift))
    P.reach('arm_L', hand_for_grip(g, q), q, (0, 1, -1))
    rh = add(cpos, rotate(cq, sub(REST[IDS['arm_R_end']], REST[IDS['chest']])))
    P.reach('arm_R', add(rh, (.3*math.sin(phase+1), 0, .25*math.sin(phase))), None, (0, -1, -.3))


def pose(name, t):
    P = Pose()
    phase = math.tau*t
    if name == 'idle':
        breath = math.sin(phase)
        P.shift[IDS['pelvis']] = (0, 0, -.4-.12*breath)
        breathe(P, phase)
        P.turn('head', (0, 0, 1), 6*math.sin(phase))
        P.turn('head', (0, 1, 0), 1.5*math.sin(2*phase))
        # A resting hind hoof tipped on its toe, as horses rest one hind leg.
        # The weight shifts off the right hind mid-cycle; it rests on its toe.
        k = (1-math.cos(phase))/2
        rest_q = axis((0, 1, 0), math.radians(18*k))
        plant_hooves(P, {'hind_R': (1.2*k, 0, (1.5+.2*math.sin(phase))*k)}, {'hind_R': rest_q})
        idle_arms(P, phase)
        tail_sway(P, phase, 3)
    elif name == 'trot':
        trot_pose(P, t)
    elif name in ('shoot', 'rear_shot'):
        shot_pose(P, t, name == 'rear_shot')
    elif name == 'flinch':
        pulse = math.sin(math.pi*clamp(t/.8))**2
        P.shift[IDS['pelvis']] = (-1.6*pulse, .6*pulse, -.4-.5*pulse)
        P.turn('pelvis', (0, 0, 1), 3*pulse)
        P.turn('withers', (0, 1, 0), -3*pulse)
        P.turn('waist', (0, 1, 0), -7*pulse)
        P.turn('waist', (0, 0, 1), 8*pulse)
        P.turn('chest', (1, 0, 0), -6*pulse)
        P.turn('head', (0, 1, 0), -12*pulse)
        P.turn('head', (0, 0, 1), -10*pulse)
        plant_hooves(P)
        world = P.world()
        cpos, cq = world[IDS['chest']]
        g, bq = carry(cpos, cq, (-3*pulse, -2*pulse, 4*pulse), -8*pulse)
        P.reach('arm_L', hand_for_grip(g, bq), bq, (0, 1, -1))
        rh = add(cpos, rotate(cq, sub(REST[IDS['arm_R_end']], REST[IDS['chest']])))
        P.reach('arm_R', add(rh, (1.5*pulse, 2.0*pulse, 5*pulse)), None, (0, -1, -.3))
        tail_sway(P, 0, 0, 25*pulse)
    elif name == 'fall':
        fall_pose(P, t)
    return P.frame()


def trot_pose(P, t):
    """Two-beat trot: diagonal pairs swing together; the rider's torso steadies."""
    phase = math.tau*t
    bob = math.cos(2*phase)
    P.shift[IDS['pelvis']] = (0, 0, -.9+.5*bob)
    P.turn('pelvis', (0, 1, 0), 1.2*math.sin(phase))
    P.turn('withers', (0, 1, 0), -1.0*math.sin(phase))
    P.turn('waist', (0, 1, 0), 2.5-1.0*bob)
    P.turn('head', (0, 1, 0), .8*bob)
    offsets, flex = {}, {}
    stance = .56
    for key, offset in (('fore_L', 0), ('hind_R', 0), ('fore_R', .5), ('hind_L', .5)):
        q = (t+offset) % 1
        if q < stance:
            dx, lift, curl = 5.0-10.0*q/stance, 0, 0
        else:
            u = (q-stance)/(1-stance)
            dx = -5.0+10.0*smooth(u)
            lift = (5.2 if key.startswith('fore') else 4.2)*math.sin(math.pi*u)**1.2
            curl = math.sin(math.pi*min(1, u*1.25))
        offsets[key] = (dx, 0, lift)
        flex[key] = axis((0, 1, 0), math.radians((70 if key.startswith('fore') else 45)*curl))
    plant_hooves(P, offsets, flex)
    world = P.world()
    cpos, cq = world[IDS['chest']]
    g, q = carry(cpos, cq)
    P.reach('arm_L', hand_for_grip(add(g, (0, 0, -.3*bob)), q), q, (0, 1, -1))
    rh = add(cpos, rotate(cq, sub(REST[IDS['arm_R_end']], REST[IDS['chest']])))
    P.reach('arm_R', add(rh, (1.2*math.sin(phase), 0, .4*bob)), None, (0, -1, -.3))
    tail_sway(P, phase*2, 3, 6)


# Shot timing: reach to the quiver, nock, draw, hold, release, recover.
ANCHOR = (2.6, -1.4, -2.8)            # head-local nock anchor under the right cheek
TIP_LIMIT = 29.8                      # arrow tip x limit inside the centred cell
DRAW = 19.0                           # full draw: nock to grip
NOCK_UP = 1.9                         # nocking point above the grip centre
SHELF = (.15, .9, NOCK_UP)            # arrow rest, left of the grip


def shot_pose(P, t, rear):
    reach = window(t, .02, .16)
    grab = window(t, .16, .24)
    nock = window(t, .24, .40)
    draw = window(t, .40, .58)
    release = t >= .70
    follow = window(t, .70, .78)
    settle = window(t, .76, 1)
    ready = window(t, .2, .4)*(1-settle)
    lift = window(t, .06, .40)*(1-window(t, .72, .96)) if rear else 0
    # Horse rocks back over its hooves (or half-rears); the rider leans back
    # and turns part side-on so the drawn arrow stays inside the cell.
    P.shift[IDS['pelvis']] = (-3.0*ready-1.0*lift, 0, -.4-1.1*ready-1.4*lift)
    P.turn('pelvis', (0, 1, 0), -10*lift)
    P.turn('withers', (0, 1, 0), -3*lift)
    P.turn('waist', (0, 1, 0), -18*ready+13*lift)
    P.turn('waist', (0, 0, 1), -18*ready)
    P.turn('chest', (0, 0, 1), -14*ready)
    P.turn('neck', (0, 0, 1), 16*ready)
    P.turn('head', (0, 0, 1), 16*ready)
    P.turn('head', (0, 1, 0), (20 if rear else 15)*ready)
    if rear:
        wave = math.sin(math.tau*2*t)
        fore = {'fore_L': (3.0*lift, 0, 9.0*lift), 'fore_R': ((4.0+.8*wave)*lift, 0, (7.5+1.5*wave)*lift)}
        flex = {k: axis((0, 1, 0), math.radians(95*lift)) for k in fore}
        plant_hooves(P, fore, flex)
    else:
        plant_hooves(P)
    tail_sway(P, math.tau*t, 2, 10*ready)
    world = P.world()
    cpos, cq = world[IDS['chest']]
    npos, nq = world[IDS['head']]
    anchor = add(npos, rotate(nq, ANCHOR))
    dq, _, _ = quiver_frame()
    slot = add(cpos, rotate(cq, sub(NOCK_REST, REST[IDS['chest']])))
    pulled = add(slot, rotate(cq, mul(dq, -3.5)))
    hand_rest = add(cpos, rotate(cq, sub(FINGER_R, REST[IDS['chest']])))
    # Nock point H on the string. The bow is pitched down while the arrow
    # overhangs, and levels only as the draw brings the nock to the anchor, so
    # the cosmetic arrow tip never leaves the cell.
    nock_at = add(anchor, (5.5, 2.5, -8.5))
    H = lerp(nock_at, anchor, draw)
    H = add(H, (0, 0, .08*math.sin(math.tau*6*t)*window(t, .56, .6)))
    aim = 7.0 if rear else -1.0
    pitch = max(aim, math.degrees(math.acos(clamp((TIP_LIMIT-H[0])/ARROW_LEN, -1, 1))))
    pull = (DRAW-BRACE)*draw
    nock_local = (-BRACE-pull, 0, NOCK_UP)
    held = grip_q(pitch, 16-6*draw)
    carried, carry_q = carry(cpos, cq)
    aimed = sub(H, rotate(held, nock_local))
    grip = lerp(carried, aimed, ready)
    bq = slerp(carry_q, held, ready)
    P.reach('arm_L', hand_for_grip(grip, bq), bq, (0, 1, -1))
    world = P.world()
    bpos, bqw = world[IDS['bow']]
    shelf = add(bpos, rotate(bqw, SHELF))
    string_nock = add(bpos, rotate(bqw, nock_local))
    # Draw hand: quiver mouth -> nocking point -> anchor -> loose and recover.
    if release:
        loose = add(anchor, rotate(nq, (-3.4, -2.6, .8)))
        finger = lerp(lerp(anchor, loose, follow), hand_rest, settle)
    elif t < .16:
        finger = lerp(hand_rest, slot, reach)
    elif t < .24:
        finger = lerp(slot, pulled, grab)
    elif t < .40:
        finger = lerp(pulled, string_nock, nock)
    else:
        finger = string_nock
    shaft = unit(sub(shelf, string_nock))
    hq_draw = qmul(between((0, 0, -1), shaft), axis((0, 0, 1), math.radians(90)))
    turn = nock if t < .70 else 1-settle
    hq_reach = qmul(cq, between((0, 0, -1), (-.8, .1, -.6)))
    hq = slerp(slerp(cq, hq_reach, reach*(1-window(t, .24, .40))), hq_draw, turn)
    pole = lerp((0, -1, .4), (-1, -.7, .1), turn)
    P.reach('arm_R', wrist_for_finger(finger, hq), hq, pole)
    world = P.world()
    hpos, hqw = world[IDS['arm_R_end']]
    hook = add(hpos, rotate(hqw, sub(FINGER_R, REST[IDS['arm_R_end']])))
    # String follows the hook while the arrow is on it; snaps back on release.
    on_string = t >= .40 and not release
    if on_string:
        local = rotate(inverse(bqw), sub(hook, bpos))
        P.shift[IDS['bow_string']] = sub(local, BONES[IDS['bow_string']][2])
        P.turn('bow_top', (0, 1, 0), -13*draw)
        P.turn('bow_bottom', (0, 1, 0), 13*draw)
    elif t >= .24 and not release:
        P.shift[IDS['bow_string']] = (0, 0, NOCK_UP*nock)   # fingers seat the nock
    elif release:
        snap = 1-window(t, .70, .73)
        wobble = 2.0*math.sin(math.tau*3*(t-.7))*(1-window(t, .7, .9))
        P.turn('bow_top', (0, 1, 0), -13*snap+wobble)
        P.turn('bow_bottom', (0, 1, 0), 13*snap-wobble)
    # The cosmetic arrow leaves the quiver in the hook, rides the string and,
    # once loosed, is simply the next arrow back in its quiver slot again.
    if t >= .16 and not release:
        direction = unit(sub(shelf, hook))
        carried = slerp(cq, between(dq, direction), nock if t < .40 else 1)
        P.place('arrow', hook, carried)


def blend(A, B, w, early=None, w_early=0.):
    """Per-bone blend; bones named in `early` use their own weight."""
    P = Pose()
    ws = [w_early if early and n in early else w for n, p, v in BONES]
    P.shift = [lerp(a, b, k) for a, b, k in zip(A.shift, B.shift, ws)]
    P.rot = [slerp(a, b, k) for a, b, k in zip(A.rot, B.rot, ws)]
    return P


FALL_ROLL = 84.0
FALL_CENTRE = (-3.6, 3.7, 12.0)
FALL_HAND_L = (16.5, -18.5, 6.8)
FALL_HAND_R = (18.0, -14.0, 2.4)
FALL_BOW_YAW = -37.0


def fall_buckle(t):
    """Knees buckle over planted hooves; the rider slumps forward."""
    A = Pose()
    sink = window(t, 0, .3)
    A.shift[IDS['pelvis']] = (-.8*sink, 0, -.4-8.5*sink)
    A.turn('pelvis', (0, 1, 0), 4*sink)
    A.turn('withers', (0, 1, 0), 5*sink)
    A.turn('waist', (0, 1, 0), 7*sink)
    A.turn('chest', (0, 1, 0), 5*sink)
    A.turn('head', (0, 1, 0), 16*sink)
    plant_hooves(A)
    idle_arms(A, 0)
    return A


def fall_limp():
    """Final pose: the horse lies on its right side, legs loose, rider limp."""
    B = Pose()
    q = axis((1, 0, 0), math.radians(FALL_ROLL))
    B.rot[IDS['root']] = q
    B.shift[IDS['root']] = sub(FALL_CENTRE, rotate(q, REST[IDS['barrel']]))
    for side in ('L', 'R'):
        top = side == 'L'
        B.turn(f'fore_{side}_shoulder', (1, 0, 0), -27 if top else 4)
        B.turn(f'fore_{side}_shoulder', (0, 1, 0), -14 if top else 6)
        B.turn(f'fore_{side}_upper', (0, 1, 0), -34 if top else -22)
        B.turn(f'fore_{side}_lower', (0, 1, 0), 100 if top else 84)
        B.turn(f'fore_{side}_end', (0, 1, 0), 34)
        B.turn(f'hind_{side}_hip', (1, 0, 0), -26 if top else 5)
        B.turn(f'hind_{side}_hip', (0, 1, 0), 10 if top else -6)
        B.turn(f'hind_{side}_upper', (0, 1, 0), 40 if top else 30)
        B.turn(f'hind_{side}_lower', (0, 1, 0), -78 if top else -64)
        B.turn(f'hind_{side}_end', (0, 1, 0), 30)
    # Rider slumps forward and sideways onto the floor before the horse's chest;
    # the head lolls onto the floor. (Angles were fitted to keep every vertex
    # inside the cell and above the floor.)
    B.turn('waist', (0, 1, 0), 28)
    B.turn('waist', (1, 0, 0), -7)
    B.turn('waist', (0, 0, 1), 7)
    B.turn('chest', (0, 1, 0), 2)
    B.turn('chest', (1, 0, 0), 22)
    B.turn('chest', (0, 0, 1), 16)
    B.turn('neck', (1, 0, 0), 34)
    B.turn('neck', (0, 1, 0), -8.5)
    B.turn('head', (1, 0, 0), 45)
    B.turn('head', (0, 1, 0), 18)
    B.turn('head', (0, 0, 1), -10)
    B.turn('arm_L_upper', (1, 0, 0), 30)
    B.turn('arm_L_upper', (0, 1, 0), -20)
    B.turn('arm_L_lower', (0, 1, 0), -20)
    B.turn('arm_R_upper', (1, 0, 0), -10)
    B.turn('arm_R_upper', (0, 1, 0), -40)
    B.turn('arm_R_lower', (0, 1, 0), -20)
    for i in range(4):
        B.turn(f'tail_{i}', (1, 0, 0), -14 if i == 0 else 4)
        B.turn(f'tail_{i}', (0, 1, 0), -18 if i == 0 else 6)
    return B


def fall_pose(P, t):
    """Legs buckle, the horse rolls onto its right side, the rider goes limp."""
    A, B = fall_buckle(t), fall_limp()
    r = window(t, .24, .8)
    # The rider folds before the horse finishes rolling, so the torso never
    # sweeps outside the cell while the body turns over.
    C = blend(A, B, r, ('waist', 'chest', 'neck', 'head'), window(t, .3, .75))
    P.shift, P.rot = C.shift, C.rot
    # Physical roll path: the barrel centre descends steadily while turning.
    P.shift[IDS['root']], P.rot[IDS['root']] = (0, 0, 0), (0, 0, 0, 1)
    centre = P.world()[IDS['barrel']][0]
    q = axis((1, 0, 0), math.radians(FALL_ROLL*r))
    target = lerp(centre, FALL_CENTRE, r)
    target = add(target, (0, 2.5*math.sin(math.pi*r), 5.0*math.sin(math.pi*r)**.5))
    P.rot[IDS['root']] = q
    P.shift[IDS['root']] = sub(target, rotate(q, centre))
    # Arms go slack onto the floor; the bow slips flat, still in the left fist.
    world = P.world()
    cpos, cq = world[IDS['chest']]
    def natural(bone):
        return add(cpos, rotate(cq, sub(REST[IDS[bone]], REST[IDS['chest']])))
    drop = window(t, .3, .9)
    bow_flat = qmul(axis((0, 0, 1), math.radians(FALL_BOW_YAW)), axis((1, 0, 0), math.radians(-108)))
    held, carry_q = carry(cpos, cq)
    bq = slerp(carry_q, bow_flat, drop)
    wrist = hand_for_grip(held, carry_q)
    P.reach('arm_L', lerp(wrist, FALL_HAND_L, drop), bq, (0, 1, -1), clamp_reach=True)
    P.reach('arm_R', lerp(natural('arm_R_end'), FALL_HAND_R, drop), None, (-1, 0, .3), clamp_reach=True)


def geometry():
    from .connected_skin import attach
    parts = attach('centaur', build_parts(), weights)
    return assemble(centaur_materials.connected_atlas(parts), weights)


def matrices(frame): return RIG.matrices(frame)
def deform(v, w, frame): return RIG.deform(v, w, frame)
def animation_data(v, w): return sample_clips(RIG, CLIPS, pose, v, w)


def texture_bytes():
    from .connected_skin import attach
    return centaur_materials.connected_atlas(attach('centaur', build_parts(), weights), True)


def build():
    skin = texture_bytes()
    (ROOT/'mod/BrogueDoom'/SKIN).write_bytes(skin)
    parts, v, n, uv, tr, w = geometry()
    clips, bounds = animation_data(v, w)
    data = iqm.encode(v, n, uv, tr, w, BONES, clips, bounds, mesh_label='Project_Broom_centaur', material_path=SKIN)
    path = ROOT/'mod/BrogueDoom/models/monsters/35_centaur.iqm'
    path.write_bytes(data)
    manifest = dict(schemaVersion=1, workId='BRG-M35', format='IQM v2', runtimeModel=path.relative_to(ROOT).as_posix(),
                    sha256=hashlib.sha256(data).hexdigest(), skin=SKIN, skinSha256=hashlib.sha256(skin).hexdigest(),
                    dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v), 4) for a in range(3)],
                    parts=len(parts), vertices=len(v), triangles=len(tr), boneCount=len(BONES),
                    bones=[dict(name=n, parent=p, local=v) for n, p, v in BONES],
                    clips=[{k: v for k, v in c.items() if k != 'frames'} | dict(frameCount=len(c['frames'])) for c in clips],
                    poseBounds=bounds, authoringSource='assets/monsters/centaur/centaur-animated.blend')
    out = ROOT/'assets/monsters/centaur'
    out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    print(build()['sha256'])

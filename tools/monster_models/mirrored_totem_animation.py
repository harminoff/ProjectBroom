"""Mirrored totem: a shoulder-high triangular prism of framed mirror panels.

Brogue (Globals.c) describes "a prism of shoulder-high mirrored surfaces"
that gleams in the darkness. Its catalog carries MA_REFLECT_100, the
beckoning bolt, and DF_MIRROR_TOTEM_STEP, whose message says the totem
flashes, reflecting the red glow of the glyph. Reflection, beckoning, glyph
reactions, timing and death stay Brogue-owned; this model only shows a
mirror prism. The object is immobile: the movement role rests. Activation
opens the panels on a fullbright flash crystal; the alternate lowers the front
mirror toward the target; death shatters every panel at a jagged crack.
"""
import math
from .rat import add, sub, mul, ROOT
from .skeletal import axis, qmul
from . import relic_kit as kit
from . import mirrored_totem_materials as materials

SKIN = 'graphics/BRGMIRT.png'
SIDE = 18.0
APOTHEM = SIDE/(2*math.sqrt(3))
PANEL_Z = (12.0, 44.0)  # prism on a taller stepped plinth
FACES = (60, 180, 300)  # a prism edge faces the camera; two mirrors angle toward it
VERTICES = (0, 120, 240)
CORNER = SIDE/math.sqrt(3)
SPECS = [('root', None, (0, 0, 0))]
SPECS += [('%s_%d' % (half, k), 'root', (APOTHEM*math.cos(math.radians(a)), APOTHEM*math.sin(math.radians(a)), PANEL_Z[0]))
          for k, a in enumerate(FACES) for half in ('panel', 'shard')]
SPECS += [('cap', 'root', (0, 0, PANEL_Z[1])), ('flash', 'root', (0, 0, 28.0))]
SPECS += [('column_%d' % k, 'root', (CORNER*math.cos(math.radians(a)), CORNER*math.sin(math.radians(a)), PANEL_Z[0]))
          for k, a in enumerate(VERTICES)]
CLIPS = kit.clip_specs(('idle', 'rest', 'flash', 'beckon', 'recoil', 'shatter'))
R = kit.Relic('mirrored_totem', 'BRG-M62', 62, SKIN, SPECS, CLIPS, materials.ATLAS)
BONES, REST, IDS, RIG = R.bones, R.rest, R.ids, R.rig
MODEL = R.model
DURATIONS = kit.durations(CLIPS)
HEIGHT = PANEL_Z[1]-PANEL_Z[0]
HALF = SIDE/2-.5
CRACK = [(HALF, 12.0), (4.2, 14.6), (.6, 11.4), (-3.1, 15.2), (-HALF, 13.0)]
LOWER = [(-HALF, 0), (HALF, 0)]+CRACK
UPPER = list(reversed(CRACK))+[(HALF, HEIGHT), (-HALF, HEIGHT)]


def radial(a, r, z):
    a = math.radians(a)
    return (r*math.cos(a), r*math.sin(a), z)


def tangent(a):
    return (-math.sin(math.radians(a)), math.cos(math.radians(a)), 0)


REST_FLASH = (0, 0, 28.0)


def _parts(relic, parts):
    put = relic.put
    hexa = math.pi/6
    # Taller stepped, carved lacquer plinth with engraved pewter bands.
    put(parts, kit.lathe('lacquer_plinth', [(14.4, .1), (14.8, 1.2), (14.8, 2.6), (13.4, 3.2), (12.8, 3.4), (12.8, 6.4),
                                             (11.8, 7.0), (11.2, 7.2), (11.2, 10.6), (10.6, 11.4), (10.2, 12.0)],
                         6, phase=hexa, flat=True), 'lacquer', 'root')
    for name, prof in (('plinth_pewter_band', [(14.7, 1.5), (15.1, 1.7), (15.1, 2.2), (14.7, 2.4)]),
                       ('plinth_pewter_step', [(12.7, 5.2), (13.1, 5.4), (13.1, 5.9), (12.7, 6.1)]),
                       ('plinth_pewter_lip', [(11.1, 9.2), (11.5, 9.4), (11.5, 9.9), (11.1, 10.1)])):
        put(parts, kit.lathe(name, prof, 6, phase=hexa, flat=True, caps=False), 'pewter', 'root')
    for k, a in enumerate(FACES):
        n = radial(a, 1, 0); t = tangent(a)
        origin = add(mul(n, APOTHEM-.55), (0, 0, PANEL_Z[0]))
        box = (-HALF, HALF, 0, HEIGHT)
        glass = 'mirror_%d' % k  # each face has its own reflected banding
        put(parts, kit.plate('mirror_lower_%d' % k, LOWER, 1.0, origin, t, (0, 0, 1), uv_box=box), glass, 'panel_%d' % k)
        put(parts, kit.plate('mirror_upper_%d' % k, UPPER, 1.0, origin, t, (0, 0, 1), uv_box=box), glass, 'shard_%d' % k)
        face = add(mul(n, APOTHEM+.1), (0, 0, PANEL_Z[0]))

        def at(a_, b_):
            return add(face, add(mul(t, a_), (0, 0, b_)))
        # Heavy engraved pewter frame: thick foot and head rails, stiles.
        put(parts, kit.tube('frame_foot_%d' % k, [(*at(-HALF-.2, 1.0), 1.1), (*at(HALF+.2, 1.0), 1.1)], 8, 1), 'pewter', 'panel_%d' % k)
        put(parts, kit.tube('frame_head_%d' % k, [(*at(-HALF-.2, HEIGHT-1.0), 1.1), (*at(HALF+.2, HEIGHT-1.0), 1.1)], 8, 1), 'pewter', 'shard_%d' % k)
        for s_, b0 in ((-1, 13.0), (1, 12.0)):
            put(parts, kit.tube('frame_stile_low_%d_%d' % (k, s_ > 0), [(*at(s_*(HALF-.3), 1.0), .8), (*at(s_*(HALF-.3), b0), .8)], 6, 1), 'pewter', 'panel_%d' % k)
            put(parts, kit.tube('frame_stile_high_%d_%d' % (k, s_ > 0), [(*at(s_*(HALF-.3), b0), .8), (*at(s_*(HALF-.3), HEIGHT-1.0), .8)], 6, 1), 'pewter', 'shard_%d' % k)
        put(parts, kit.ellipsoid('frame_boss_%d' % k, at(0, HEIGHT-1.0), (1.2, 1.8, 1.8), 4, 2, flat=True), 'silver', 'shard_%d' % k)
        put(parts, kit.ellipsoid('frame_foot_boss_%d' % k, at(0, 1.0), (1.1, 1.6, 1.4), 4, 2, flat=True), 'silver', 'panel_%d' % k)
    # Engraved pewter corner columns with knops frame the prism edges.
    for k, a in enumerate(VERTICES):
        bone = 'column_%d' % k
        base = radial(a, CORNER, PANEL_Z[0])
        put(parts, kit.lathe('corner_column_%d' % k, [(1.9, 0), (1.5, 1.2), (1.25, 3), (1.25, HEIGHT-3), (1.5, HEIGHT-1.2), (1.9, HEIGHT)],
                             8, center=base, flat=True), 'pewter', bone)
        for j, z in enumerate((HEIGHT*.33, HEIGHT*.66)):
            put(parts, kit.ellipsoid('column_knop_%d_%d' % (k, j), add(base, (0, 0, z)), (1.9, 1.9, 1.1), 8, 4, flat=True), 'silver', bone)
    # Distinct crown: pewter triangular crown, a ring of six small mirror
    # shards and a tall faceted mirror finial.
    top = PANEL_Z[1]
    put(parts, kit.lathe('prism_crown', [(12.2, top), (12.6, top+1.1), (11.6, top+2.4), (8.2, top+3.4), (6.0, top+3.8)],
                         3, phase=0, flat=True), 'pewter', 'cap')
    for j in range(6):
        a = 30+60*j
        base = radial(a, 7.2, top+3.0)
        out = kit.unit(add(mul(radial(a, 1, 0), .38), (0, 0, .92)))
        put(parts, kit.plate('crown_mirror_shard_%d' % j, [(0, -1.3), (5.8, -.4), (7.2, .2), (4.5, 1.2), (0, 1.3)], .45,
                             base, out, tangent(a), taper=.5), 'mirror_3', 'cap')
    put(parts, kit.lathe('crown_finial_collar', [(3.2, top+3.4), (3.6, top+4.4), (2.2, top+5.2)], 6, flat=True), 'silver', 'cap')
    put(parts, kit.lathe('crown_mirror_finial', [(2.2, top+5.0), (3.0, top+7.0), (0, top+13.0)], 4, phase=math.pi/4, flat=True), 'mirror_3', 'cap')
    # Fullbright flash crystal: three crossed tall diamonds, sealed inside
    # the closed prism (inradius clears its 3.3-unit arms).
    c = REST_FLASH
    for j in range(3):
        a = 60*j+30
        put(parts, kit.plate('flash_diamond_%d' % j, [(0, -7.0), (3.3, 0), (0, 7.0), (-3.3, 0)], .35, c,
                             radial(a, 1, 0), (0, 0, 1), taper=1.0), 'flash', 'flash')
    put(parts, kit.ellipsoid('flash_core', c, (1.9, 1.9, 2.6), 6, 3, flat=True), 'flash', 'flash')


def geometry():
    return R.geometry(_parts)


def _open(frame, k, degrees, extra=(0, 0, 0, 1)):
    q = qmul(axis(tangent(FACES[k]), math.radians(degrees)), extra)
    R.turn_q(frame, 'panel_%d' % k, q); R.turn_q(frame, 'shard_%d' % k, q)


def pose(name, t):
    frame = R.rest_frame()
    if name == 'rest':
        return [tuple(r) for r in frame]
    phase = math.tau*t
    if name == 'idle':
        R.turn(frame, 'cap', 4*math.sin(phase), (0, 0, 1))
    elif name == 'flash':
        p = math.sin(math.pi*t)**2
        for k in range(3):
            _open(frame, k, 31*p)
        R.move(frame, 'cap', (0, 0, 11*p)); R.turn(frame, 'cap', 10*p, (.3, 1, 0))
        R.move(frame, 'flash', (0, 0, 17*p)); R.turn(frame, 'flash', 70*p, (0, 0, 1))
    elif name == 'beckon':
        p = math.sin(math.pi*t)**2
        _open(frame, 0, 50*p); _open(frame, 2, 50*p)
        _open(frame, 1, 10*p)
        R.move(frame, 'cap', (-1.5*p, 0, 3*p)); R.turn(frame, 'cap', -15*p, (0, 1, 0))
        R.move(frame, 'flash', (0, 0, 7*p)); R.turn(frame, 'flash', -50*p, (0, 0, 1))
    elif name == 'recoil':
        p = math.sin(math.pi*t)**2
        for k in range(3):
            _open(frame, k, 5*p*math.sin(phase*2+k*2.1))
        R.move(frame, 'cap', (0, 0, 1.4*p)); R.turn(frame, 'cap', -9*p, (1, .4, 0))
    elif name == 'shatter':
        geometry()
        # Lower panels fall outward flat onto the floor; the cracked
        # upper shards collapse in a stacked heap on the plinth; the crown
        # topples off beside it.
        for k, a in enumerate(FACES):
            s = kit.smooth((t-.05*k)/.62)
            n = radial(a, 1, 0)
            q = axis(tangent(a), math.radians(90))
            xy = radial(a, 15.6, 0)[:2]
            R.fall(frame, 'panel_%d' % k, s, q, xy, hop=2, final=R.placement('panel_%d' % k, q, xy))
            s2 = kit.smooth((t-.12-.07*k)/.6)
            q2 = qmul(axis((0, 0, 1), math.radians((35, -50, 22)[k])), axis(tangent(a), math.radians(-90)))
            # Each shard settles about its own centre, near the plinth axis.
            centre = add(REST[IDS['shard_%d' % k]], (0, 0, 22.0))
            xy2 = add(radial(a, 1.2, 0), mul(tangent(a), (1.5, -2.0, .8)[k]))[:2]
            final = R.placement('shard_%d' % k, q2, xy2, floor=12.1+1.15*k, contact=centre)
            R.fall(frame, 'shard_%d' % k, s2, q2, final[:2], hop=4, final=final)
        s = kit.smooth((t-.28)/.6)
        # The crown topples backward onto the fallen rear mirror.
        q = qmul(axis((0, 0, 1), math.radians(20)), axis(tangent(180), math.radians(96)))
        final = R.placement('cap', q, radial(180, 21.0, 0)[:2], floor=1.3, contact=(0, 0, PANEL_Z[1]+5))
        R.fall(frame, 'cap', s, q, final[:2], hop=5, final=final)
        # Corner columns snap at the foot and fall flat, lying tangentially
        # on the floor between the fallen panels.
        for k, a in enumerate(VERTICES):
            s3 = kit.smooth((t-.16-.06*k)/.58)
            q3 = qmul(axis((0, 0, 1), math.radians((10, -8, 6)[k])), axis(radial(a, 1, 0), math.radians(90)))
            mid = add(REST[IDS['column_%d' % k]], (0, 0, HEIGHT/2))
            final = R.placement('column_%d' % k, q3, radial(a, 18.5, 0)[:2], contact=mid)
            R.fall(frame, 'column_%d' % k, s3, q3, final[:2], hop=3, final=final)
        # The flash crystal gutters and lies down sealed inside the plinth.
        s = kit.smooth((t-.05)/.5)
        R.turn(frame, 'flash', 90*s, tangent(30)); R.move(frame, 'flash', (0, 0, -22*s))
    else:
        raise ValueError(name)
    return [tuple(r) for r in frame]


def matrices(frame): return RIG.matrices(frame)
def deform(v, w, frame): return RIG.deform(v, w, frame)
def animation_data(v, w): return R.animation(pose, v, w)
def texture_bytes(): return materials.texture_bytes()


def build():
    return R.export(geometry, animation_data, texture_bytes)


if __name__ == '__main__':
    from tools.monster_models import mirrored_totem_animation as module
    print(module.build()['sha256'])

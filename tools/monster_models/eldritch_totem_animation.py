"""Eldritch totem: a twisted, segmented alien spire ringed by spectral blades.

Brogue (Globals.c) describes a totem at the centre of a summoning circle that
radiates a strange energy; its glyph colour is glyphColor (dark red) and it
summons spectral blades (and furies). The summoning circle is Brogue terrain
and is not modelled. Summons, activation, timing and death stay Brogue-owned.
The pillar is immobile: the movement role rests. Activation opens the stacked
segments on a fullbright red core and fans the blade ring out flat; the
alternate strike aims the blades forward; death topples the segments and
drops the blades flat around the stump.
"""
import math
from .rat import add, sub, mul, ROOT
from .skeletal import axis, qmul
from . import relic_kit as kit
from . import eldritch_totem_materials as materials

SKIN = 'graphics/BRGELDT.png'
FIN_ANGLES = tuple(36+72*k for k in range(5))
FIN_BASE = (5.7, 28.2)  # radius, height of each blade's guard on the collar
SPECS = [('root', None, (0, 0, 0)),
         ('seg1', 'root', (0, 0, 16)), ('seg2', 'root', (0, 0, 31)), ('crown', 'root', (0, 0, 45)),
         ('core0', 'root', (0, 0, 16)), ('core1', 'seg1', (0, 0, 31)), ('core2', 'seg2', (0, 0, 45))]
SPECS += [('fin_%d' % k, 'root', (FIN_BASE[0]*math.cos(math.radians(a)), FIN_BASE[0]*math.sin(math.radians(a)), FIN_BASE[1]))
          for k, a in enumerate(FIN_ANGLES)]
CLIPS = kit.clip_specs(('idle', 'rest', 'crackle', 'strike', 'recoil', 'topple'))
R = kit.Relic('eldritch_totem', 'BRG-M61', 61, SKIN, SPECS, CLIPS, materials.ATLAS)
BONES, REST, IDS, RIG = R.bones, R.rest, R.ids, R.rig
MODEL = R.model
DURATIONS = kit.durations(CLIPS)
FINS = ['fin_%d' % k for k in range(5)]
SEGS = ['seg1', 'seg2', 'crown']
PROFILES = {
    'root': [(10.4, .1), (10.7, 1.2), (8.2, 2.6), (6.6, 4.5), (5.9, 7), (5.6, 10), (6.1, 13), (5.4, 16)],
    'seg1': [(5.4, 16), (6.5, 18.5), (7.1, 21.5), (6.9, 24.5), (6.0, 27.5), (5.2, 29.5), (4.9, 31)],
    'seg2': [(4.9, 31), (5.8, 33), (6.2, 36), (5.6, 39), (4.6, 42), (4.2, 45)],
    'crown': [(4.2, 45), (5.4, 47), (4.6, 49.5), (3.2, 52), (1.8, 55), (0, 58)],
}
GAP = 4.3  # activation separation between stacked segments


def radial(a, r, z):
    a = math.radians(a)
    return (r*math.cos(a), r*math.sin(a), z)


def _twist(i, z):
    return .046*z


def _blade_outline():
    # Curved single-edged spectral blade, length along +a, width along b.
    return [(0, -1.2), (5, -1.9), (10.5, -1.8), (15.5, -1.1), (19.5, .2), (21.5, 1.4),
            (17.5, 1.7), (12, 2.3), (6, 2.2), (1.5, 1.6), (0, 1.2)]


def _fin_frame(a):
    d = radial(a, 1, 0); t = (-math.sin(math.radians(a)), math.cos(math.radians(a)), 0)
    along = kit.unit(add(mul(d, .42), (0, 0, .91)))
    return along, t


def _parts(relic, parts):
    put = relic.put
    for bone, prof in PROFILES.items():
        put(parts, kit.lathe('twisted_spire_'+bone, prof, 5, twist=_twist, flat=True), 'stone', bone)
    # A cairn of broken, faceted stones buries the spire's foot.
    for k in range(7):
        a = 51.4*k+17
        r = 8.4+1.1*math.sin(k*2.3)
        size = (3.6+.6*math.cos(k*1.7), 2.9+.5*math.sin(k*3.1), 2.2+.5*math.cos(k*2.2))
        put(parts, kit.transform(kit.ellipsoid('cairn_stone_%d' % k, (0, 0, 0), size, 5, 3, flat=True),
                                 axis((0, 0, 1), math.radians(a+25*math.sin(k))), radial(a, r, size[2]+.1)), 'stone', 'root')
    # Angular horn spurs jut from each segment's upper lip.
    for bone, (prof, n0) in {'root': (PROFILES['root'], 0), 'seg1': (PROFILES['seg1'], 1), 'seg2': (PROFILES['seg2'], 2)}.items():
        z = prof[-2][1]; r = prof[-2][0]
        for j in range(3):
            a = 120*j+40*n0+15
            pts = [(*radial(a, r-.6, z-1.2), .95), (*radial(a+6, r+2.2, z+.6), .55), (*radial(a+12, r+4.4, z+3.2), .04)]
            put(parts, kit.tube('horn_spur_%d_%d' % (n0, j), pts, 4, 2, flat=True), 'spur', bone)
    # Glowing core rods hide inside each segment top until activation.
    for k, (bone, parent, top) in enumerate((('core0', 'root', 16), ('core1', 'seg1', 31), ('core2', 'seg2', 45))):
        put(parts, kit.lathe('ichor_core_%d' % k, [(1.6, top-7.6), (2.5, top-6.8), (2.7, top-3.9), (2.5, top-1.0), (1.6, top-.5)], 10), 'core', bone)
    # Dark iron collar carries the blade guards on seg1.
    put(parts, kit.lathe('blade_collar', [(5.35, 26.3), (6.3, 26.9), (6.5, 28.2), (6.2, 29.4), (5.2, 30.0)], 10,
                         flat=True, caps=False), 'metal', 'seg1')
    for k, a in enumerate(FIN_ANGLES):
        bone = 'fin_%d' % k
        along, t = _fin_frame(a)
        base = radial(a, FIN_BASE[0], FIN_BASE[1])
        blade = kit.plate('spectral_blade_%d' % k, _blade_outline(), .95, add(base, mul(along, 1.4)), along, t, taper=.3)
        put(parts, blade, 'blade', bone)
        put(parts, kit.tube('blade_guard_%d' % k, [(*add(base, mul(t, -2.6)), .55), (*base, .8), (*add(base, mul(t, 2.6)), .55)], 7, 2), 'metal', bone)
        put(parts, kit.ellipsoid('blade_pommel_%d' % k, add(base, mul(along, -.3)), (1.0, 1.0, 1.0), 8, 5), 'metal', bone)


def geometry():
    return R.geometry(_parts)


def _tangent(a):
    return (-math.sin(math.radians(a)), math.cos(math.radians(a)), 0)


def pose(name, t):
    frame = R.rest_frame()
    if name == 'rest':
        return [tuple(r) for r in frame]
    phase = math.tau*t
    if name == 'idle':
        for k, a in enumerate(FIN_ANGLES):
            R.turn(frame, 'fin_%d' % k, 3*math.sin(phase+k*1.3), _tangent(a))
        R.turn(frame, 'crown', 5*math.sin(phase), (0, 0, 1))
    elif name == 'crackle':
        p = math.sin(math.pi*t)**2
        for k, (seg, twist) in enumerate(zip(SEGS, (22, -26, 38))):
            R.turn(frame, seg, twist*p, (0, 0, 1)); R.move(frame, seg, (0, 0, GAP*(k+1)*p))
        for core in ('core0', 'core1', 'core2'):
            R.move(frame, core, (0, 0, (GAP+.9)*p))
        for k, a in enumerate(FIN_ANGLES):
            R.turn(frame, 'fin_%d' % k, 64*p, _tangent(a))
        R.group(frame, FINS, axis((0, 0, 1), math.radians(30*p)), (0, 0, 0), (0, 0, GAP*p))
    elif name == 'strike':
        p = math.sin(math.pi*t)**2
        for k, a in enumerate(FIN_ANGLES):
            # Blades swing round toward the target (+X) and point outward.
            target = a*.45 if a < 180 else 360-(360-a)*.45
            q = qmul(axis((0, 0, 1), math.radians((target-a)*p)), axis(_tangent(a), math.radians(48*p)))
            R.turn_q(frame, 'fin_%d' % k, q)
        for k, seg in enumerate(SEGS):
            R.move(frame, seg, (0, 0, 1.8*(k+1)*p))
        for core in ('core0', 'core1', 'core2'):
            R.move(frame, core, (0, 0, 2.7*p))
        R.group(frame, SEGS+FINS, axis((0, 1, 0), math.radians(9*p)), (0, 0, 16))
    elif name == 'recoil':
        p = math.sin(math.pi*t)**2
        R.move(frame, 'seg1', (0, 1.3*p, 0)); R.move(frame, 'seg2', (-1.6*p, 0, 0)); R.move(frame, 'crown', (0, -1.8*p, 0))
        R.turn(frame, 'crown', -10*p, (1, 0, 0))
        for k, a in enumerate(FIN_ANGLES):
            R.turn(frame, 'fin_%d' % k, 9*p*math.sin(phase*2+k), _tangent(a))
        R.group(frame, SEGS+FINS, axis((0, 1, 0), math.radians(-6*p)), (0, 0, 16))
    elif name == 'topple':
        geometry()
        # Segments break apart and fall outward to lie on the floor; the
        # blades drop flat, crossed in the gaps. The rooted base remains.
        for k, (seg, a) in enumerate((('seg1', 100), ('seg2', 220), ('crown', 340))):
            s = kit.smooth((t-.1*k)/.62)
            q = qmul(axis((0, 0, 1), math.radians(8-8*k)), axis(_tangent(a), math.radians(90)))
            xy = radial(a, 11.8, 0)[:2]
            R.fall(frame, seg, s, q, xy, hop=2.5, final=R.placement(seg, q, xy))
        for k, (a, b) in enumerate(zip(FIN_ANGLES, (42, 58, 162, 282, 298))):
            s = kit.smooth((t-.04-.05*k)/.58)
            q = qmul(axis((0, 0, 1), math.radians(b-a+(9 if k % 2 else -9))), axis(_tangent(a), math.radians(65)))
            xy = radial(b, 8.2, 0)[:2]
            R.fall(frame, 'fin_%d' % k, s, q, xy, hop=3, final=R.placement('fin_%d' % k, q, xy))
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
    from tools.monster_models import eldritch_totem_animation as module
    print(module.build()['sha256'])

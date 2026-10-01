"""Phylactery: the lich's soul gem clasped in a gilded claw reliquary.

Brogue (Globals.c) describes a gem that bound the soul of an ancient
sorcerer; its glyph and light colour is lichLightColor (-50,80,30), and it
carries LICH_LIGHT, so the gem is the only fullbright surface. Summoning,
the lich's regeneration and the phylactery's death all stay Brogue-owned.
The object is immobile: the unused movement role rests, the activation
roles are a gem rise/claw bloom and a forward sorcerous lean, and death
shatters the gem into four quarters that fall beside the plinth.
"""
import math
from .rat import add, sub, mul, ROOT
from .skeletal import axis, qmul
from . import relic_kit as kit
from . import phylactery_materials as materials

SKIN = 'graphics/BRGPHYL.png'
CLAW_ANGLES = (45, 135, 225, 315)
GEM_PIVOT = (0, 0, 27.2)
SPECS = [('root', None, (0, 0, 0)), ('stem', 'root', (0, 0, 5.5))]
SPECS += [('claw_%d' % k, 'root', (5.9*math.cos(math.radians(a)), 5.9*math.sin(math.radians(a)), 18.9))
          for k, a in enumerate(CLAW_ANGLES)]
SPECS += [('shard_%d' % k, 'root', GEM_PIVOT) for k in range(4)]
CLIPS = kit.clip_specs(('idle', 'rest', 'enchant', 'sorcery', 'recoil', 'shatter'))
S = 1.3  # authored in compact units, exported larger so it reads at 192 units
R = kit.Relic('phylactery', 'BRG-M41', 41, SKIN, SPECS, CLIPS, materials.ATLAS, S)
BONES, REST, IDS, RIG = R.bones, R.rest, R.ids, R.rig
MODEL = R.model
DURATIONS = kit.durations(CLIPS)
TOP = ['stem']+['claw_%d' % k for k in range(4)]+['shard_%d' % k for k in range(4)]
SHARDS = ['shard_%d' % k for k in range(4)]
GEM = REST[IDS['shard_0']]
GEM_PROFILE = [(0, 19.6), (5.9, 25.8), (6.3, 27.2), (5.9, 28.6), (4.1, 32.2), (0, 37.4)]


def radial(a, r, z):
    a = math.radians(a)
    return (r*math.cos(a), r*math.sin(a), z)


def _parts(relic, parts):
    put = relic.put
    oct8 = math.pi/8
    # Octagonal serpentine plinth with proud gilt bands.
    put(parts, kit.lathe('serpentine_plinth', [(11.2, .1), (11.8, .9), (11.8, 2.0), (10.9, 2.6), (9.6, 3.0),
                                                (9.6, 4.6), (8.6, 5.2), (8.0, 5.6)], 8, phase=oct8, flat=True), 'onyx', 'root')
    put(parts, kit.lathe('plinth_gilt_band', [(11.7, 1.1), (12.05, 1.35), (12.05, 1.75), (11.7, 2.0)], 8,
                         phase=oct8, flat=True, caps=False), 'gold', 'root')
    put(parts, kit.lathe('plinth_upper_band', [(9.5, 3.3), (9.85, 3.55), (9.85, 4.05), (9.5, 4.3)], 8,
                         phase=oct8, flat=True, caps=False), 'gold', 'root')
    # Four clawed gilt feet grip the floor; the front one faces the camera.
    for k, a in enumerate((0, 90, 180, 270)):
        put(parts, kit.ellipsoid('foot_knuckle_%d' % k, radial(a, 10.4, 3.0), (1.9, 1.9, 1.5), 10, 6), 'gold', 'root')
        for j, da in enumerate((-24, 0, 24)):
            reach = 14.3 if da == 0 else 12.9
            pts = [(*radial(a+da*.35, 10.3, 3.9), 1.05), (*radial(a+da*.7, 12.0, 3.3), .9),
                   (*radial(a+da, reach-.7, 1.9), .62), (*radial(a+da, reach, .35), .1)]
            put(parts, kit.tube('foot_talon_%d_%d' % (k, j), pts, 7, 3), 'gold', 'root')
    # Pale bone skull set on the plinth at the front, below the gem.
    put(parts, kit.ellipsoid('skull_cranium', (6.5, 0, 8.6), (2.4, 2.75, 2.6), 14, 9), 'bone', 'root')
    put(parts, kit.ellipsoid('skull_jaw', (7.3, 0, 6.5), (1.7, 2.0, 1.05), 12, 6), 'bone', 'root')
    for s in (-1, 1):
        # Slanted deep sockets under a heavy brow give a baleful stare.
        socket = kit.ellipsoid('skull_socket_%s' % ('L' if s > 0 else 'R'), (0, 0, 0), (.6, .95, .7), 10, 6)
        put(parts, kit.transform(socket, axis((1, 0, 0), math.radians(-s*24)), (8.5, s*1.2, 8.5)), 'dark', 'root')
        put(parts, kit.tube('skull_brow_%s' % ('L' if s > 0 else 'R'), [(8.35, s*.2, 9.0, .42), (8.55, s*1.25, 9.55, .5),
                                                                     (8.0, s*2.2, 9.85, .35)], 6, 2), 'bone', 'root')
    put(parts, kit.ellipsoid('skull_nasal', (8.95, 0, 7.45), (.35, .32, .55), 8, 5), 'dark', 'root')
    # Gilt octagonal stem and dished cup.
    put(parts, kit.lathe('gilt_stem_cup', [(4.4, 5.5), (3.1, 7.2), (2.3, 9.8), (2.3, 12.8), (3.2, 15), (5.3, 16.8),
                                           (6.7, 18.6), (6.9, 19.6), (6.1, 20.0), (3.2, 19.0), (0, 18.6)], 8,
                         phase=oct8, flat=True), 'gold', 'stem')
    put(parts, kit.lathe('stem_knop', [(2.2, 9.8), (3.6, 10.5), (3.8, 11.2), (3.6, 11.9), (2.2, 12.6)], 8,
                         phase=0, flat=True, caps=False), 'onyx', 'stem')
    # Four thorned claws clasp the gem at the diagonals.
    for k, a in enumerate(CLAW_ANGLES):
        bone = 'claw_%d' % k
        put(parts, kit.ellipsoid('claw_knuckle_%d' % k, radial(a, 5.9, 18.9), (1.7, 1.7, 1.5), 10, 6), 'gold', bone)
        pts = [(*radial(a, 5.9, 18.9), 1.35), (*radial(a, 8.0, 22.5), 1.2), (*radial(a, 8.6, 25.5), 1.05),
               (*radial(a, 7.4, 29.0), .9), (*radial(a, 5.4, 32.2), .6), (*radial(a, 3.0, 35.4), .08)]
        put(parts, kit.tube('gilt_claw_%d' % k, pts, 8, 3), 'gold', bone)
        put(parts, kit.tube('claw_thorn_%d' % k, [(*radial(a, 8.3, 25.4), .6), (*radial(a+3, 10.2, 26.6), .35),
                                                   (*radial(a+5, 11.6, 27.9), .05)], 6, 2), 'gold', bone)
        put(parts, kit.tube('claw_spur_%d' % k, [(*radial(a, 7.6, 21.6), .45), (*radial(a-4, 9.8, 21.2), .05)], 6, 1), 'gold', bone)
    # Faceted soul gem cut into four closed quarters (they part on death).
    for k in range(4):
        put(parts, kit.lathe('soul_gem_quarter_%d' % k, GEM_PROFILE, 2, a0=k*math.pi/2, a1=(k+1)*math.pi/2,
                             flat=True), 'gem', 'shard_%d' % k)


def geometry():
    return R.geometry(_parts)


def _claw_axis(k):
    a = math.radians(CLAW_ANGLES[k])
    return (-math.sin(a), math.cos(a), 0)


def pose(name, t):
    frame = R.rest_frame()
    if name == 'rest':
        return [tuple(r) for r in frame]
    phase = math.tau*t
    if name == 'idle':
        R.group(frame, SHARDS, axis((0, 0, 1), math.radians(7*math.sin(phase))), GEM, (0, 0, .45*S*math.sin(phase)))
    elif name == 'enchant':
        p = math.sin(math.pi*t)**2
        for k in range(4):
            R.turn(frame, 'claw_%d' % k, 44*p, _claw_axis(k))
        R.group(frame, SHARDS, axis((0, 0, 1), math.radians(70*p)), GEM, (0, 0, 7.5*S*p))
    elif name == 'sorcery':
        p = math.sin(math.pi*t)**2
        for k in range(4):
            q = qmul(axis(_claw_axis(k), math.radians(26*p)), axis(radial(CLAW_ANGLES[k], 1, 0), math.radians(34*p)))
            R.turn_q(frame, 'claw_%d' % k, q)
        R.group(frame, SHARDS, axis((0, 0, 1), math.radians(-110*p)), GEM, (0, 0, 3.5*S*p))
        R.group(frame, TOP, axis((0, 1, 0), math.radians(17*p)), REST[IDS['stem']])
    elif name == 'recoil':
        p = math.sin(math.pi*t)**2
        for k in range(4):
            R.turn(frame, 'claw_%d' % k, 7*p*math.sin(phase*2+k), _claw_axis(k))
        R.group(frame, TOP, axis((0, 1, 0), math.radians(-10*p)), REST[IDS['stem']])
    elif name == 'shatter':
        geometry()
        crack = kit.smooth(t/.22)
        # The gem jolts, then its quarters burst out and land flat, glowing
        # side up, around the plinth; the claws fall outward to lean from
        # the plinth rim to the floor; the emptied cup topples.
        s = kit.smooth((t-.12)/.62)
        for k in range(4):
            a = 20+90*k
            q = qmul(axis((0, 0, 1), math.radians(18 if k % 2 else -14)),
                     axis(radial(a, 1, 0), math.radians(90 if k % 2 else -90)))
            xy = radial(a, 21.5, 0)[:2]
            R.fall(frame, 'shard_%d' % k, s, q, xy, hop=7*S, final=R.placement('shard_%d' % k, q, xy))
            if s == 0:
                R.move(frame, 'shard_%d' % k, (0, 0, 1.2*S*crack))
        c = kit.smooth((t-.2)/.6)
        for k, a in enumerate(CLAW_ANGLES):
            q, pivot = R.lean('claw_%d' % k, _claw_axis(k), radial(a, 8.4*S, 7.3*S))
            R.fall(frame, 'claw_%d' % k, c, q, pivot[:2], hop=2*S, final=pivot)
        R.turn(frame, 'stem', -64*kit.smooth((t-.3)/.6), (.35, 1, 0))
        R.settle(frame, 'stem', lift_only=True)
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
    # Re-import by package name so module-level registries are shared.
    from tools.monster_models import phylactery_animation as module
    print(module.build()['sha256'])

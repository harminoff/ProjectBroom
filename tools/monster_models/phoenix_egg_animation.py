"""Phoenix egg: an ember-cracked glowing egg cradled in a nest of cooling ash.

Brogue (Globals.c) describes the egg "cradled in a nest of cooling ashes";
its translucent membrane reveals a yolk that glows brighter by the second.
The glyph colour is phoenixColor (red with a random green component) and it
carries PHOENIX_EGG_LIGHT, so the membrane is fullbright; it dies as DF_ASH_BLOOD
and "bursts as a newborn phoenix rises from the ashes". Hatching, summoning,
timing and death stay Brogue-owned. The egg is immobile: the movement role
rests; activation cracks the cap open over the rising yolk, the alternate
blooms the shell plates, and death bursts the shell across the nest.
"""
import math
from .rat import add, sub, mul, ROOT
from .skeletal import axis, qmul
from . import relic_kit as kit
from . import phoenix_egg_materials as materials

SKIN = 'graphics/BRGPHEGG.png'
EGG_BASE = 6.3
EGG_HEIGHT = 23.0
EGG_RADIUS = 8.4
CUT = 16.5  # local height of the cap's crack line
YOLK = (0, 0, 15.0)
PLATE_ANGLES = tuple(45+90*k for k in range(4))
SPECS = [('root', None, (0, 0, 0))]
SPECS += [('plate_%d' % k, 'root', (0, 0, EGG_BASE)) for k in range(4)]
SPECS += [('cap', 'root', (0, 0, EGG_BASE+CUT)), ('yolk', 'root', YOLK)]
CLIPS = kit.clip_specs(('idle', 'rest', 'kindle', 'bloom', 'recoil', 'burst'))
S = 1.1  # exported slightly larger so the egg reads at 192 units
R = kit.Relic('phoenix_egg', 'BRG-M66', 66, SKIN, SPECS, CLIPS, materials.ATLAS, S)
BONES, REST, IDS, RIG = R.bones, R.rest, R.ids, R.rig
MODEL = R.model
DURATIONS = kit.durations(CLIPS)
EGG = ['plate_%d' % k for k in range(4)]+['cap', 'yolk']
PIVOT = REST[IDS['plate_0']]


def radial(a, r, z):
    a = math.radians(a)
    return (r*math.cos(a), r*math.sin(a), z)


def tangent(a):
    return (-math.sin(math.radians(a)), math.cos(math.radians(a)), 0)


def egg_point(theta):
    z = EGG_HEIGHT/2*(1-math.cos(theta))
    r = EGG_RADIUS*math.sin(theta)*(1+.1*math.cos(theta))
    return (round(r, 6)+0.0, round(EGG_BASE+z, 6))


def _profiles():
    cut = math.acos(1-2*CUT/EGG_HEIGHT)
    lower = [egg_point(cut*i/9) for i in range(10)]
    upper = [egg_point(cut+(math.pi-cut)*i/6) for i in range(7)]
    return lower, upper


def _parts(relic, parts):
    put = relic.put
    lower, upper = _profiles()
    centre = (0, 0, EGG_BASE+EGG_HEIGHT/2)
    # A lumpy heap of cooling ash, with charred sticks crossing through it
    # and splaying out of it; a few stick ends still glow as embers.
    def lumps(j, i):
        return 1+.07*math.sin(j*math.tau*3/18+i*.9)+.05*math.cos(j*math.tau*5/18+i*1.7)
    put(parts, kit.lathe('ash_mound', [(17.4, .1), (15.6, .55), (13.2, 1.7), (10.6, 3.6), (8.0, 5.8), (5.4, 7.8), (0, 9.0)],
                         18, phase=.1, wobble=lumps), 'ash', 'root')
    for k in range(14):
        a = 25.7*k+8*math.sin(k*2.7)
        r1 = 9.8+2.0*math.sin(k*1.9); r2 = 11.2+2.2*math.cos(k*1.3)
        z1 = 3.6+1.3*math.sin(k*1.1)+(k % 3)*1.0; z2 = 4.4+1.4*math.cos(k*.7)+((k+1) % 3)*.9
        span = 34+9*math.sin(k)
        rad = .62+.16*math.sin(k*2.1)
        # Straight crossing chords, not a ring: sticks overlap like a nest.
        p1 = radial(a-span, r1+1.5, z1); p2 = radial(a+span, r2+1.5, z2)
        mid = add(mul(add(p1, p2), .5), (0, 0, .8))
        pts = [(*p1, rad*.5), (*add(mul(p1, .6), mul(mid, .4)), rad), (*mid, rad*.95),
               (*add(mul(p2, .6), mul(mid, .4)), rad*.8), (*p2, rad*.4)]
        put(parts, kit.tube('charred_stick_%02d' % k, pts, 6, 2), 'char', 'root')
    for k in range(9):
        a = 40*k+17+6*math.cos(k*1.3)
        z0 = 6.2+.8*math.sin(k*2.2); rise = 2.5+2.8*((k*7) % 5)/4
        tip = radial(a+9*math.sin(k), 16.4+1.0*math.cos(k*1.7), z0+rise-3.2)
        pts = [(*radial(a-4, 7.6, z0), .7), (*radial(a, 11.5, z0+rise*.55), .58), (*tip, .3)]
        put(parts, kit.tube('splayed_stick_%d' % k, pts, 6, 3), 'char', 'root')
        if k % 3 == 1:
            put(parts, kit.ellipsoid('stick_ember_%d' % k, tip, (.75, .75, .6), 6, 3, flat=True), 'inner', 'root')
    for k in range(6):
        a = 60*k+41
        put(parts, kit.ellipsoid('glowing_ember_%d' % k, radial(a, 12.6+.8*math.sin(k*3), 4.6+.6*math.cos(k*2)),
                                 (1.1, .85, .6), 6, 3, flat=True), 'inner', 'root')
    # Fullbright membrane shell: four crack-bounded plates and a cap.
    for k, a in enumerate(PLATE_ANGLES):
        a0 = math.radians(a-45); a1 = math.radians(a+45)
        put(parts, kit.shell('egg_plate_%d' % k, lower, 6, a0, a1, centre), 'shell', 'plate_%d' % k)
        put(parts, kit.shell('egg_plate_inner_%d' % k, lower, 6, a0, a1, centre, inner=True), 'inner', 'plate_%d' % k)
    put(parts, kit.shell('egg_cap', upper, 24, 0, math.tau, centre), 'cap', 'cap')
    put(parts, kit.shell('egg_cap_inner', upper, 24, 0, math.tau, centre, inner=True), 'inner', 'cap')
    put(parts, kit.ellipsoid('glowing_yolk', YOLK, (3.8, 3.8, 3.8), 12, 8), 'yolk', 'yolk')


def geometry():
    return R.geometry(_parts)


def _splay(frame, degrees):
    for k, a in enumerate(PLATE_ANGLES):
        R.turn(frame, 'plate_%d' % k, degrees, tangent(a))


def pose(name, t):
    frame = R.rest_frame()
    if name == 'rest':
        return [tuple(r) for r in frame]
    phase = math.tau*t
    if name == 'idle':
        R.group(frame, EGG, axis((math.cos(phase), math.sin(phase), 0), math.radians(3.2)), PIVOT)
    elif name == 'kindle':
        p = math.sin(math.pi*t)**2
        _splay(frame, 13*p)
        R.move(frame, 'cap', (0, 0, 9*S*p)); R.turn(frame, 'cap', 28*p, tangent(200))
        R.move(frame, 'yolk', (0, 0, 7*S*p))
        R.group(frame, EGG, axis((0, 1, 0), math.radians(5*p)), PIVOT)
    elif name == 'bloom':
        p = math.sin(math.pi*t)**2
        _splay(frame, 34*p)
        R.move(frame, 'cap', (0, 0, 5.5*S*p)); R.turn(frame, 'cap', -14*p, tangent(90))
        R.move(frame, 'yolk', (0, 0, 2.5*S*p))
    elif name == 'recoil':
        p = math.sin(math.pi*t)**2
        R.group(frame, EGG, axis((0, 1, 0), math.radians(-9*p)), PIVOT)
        _splay(frame, 3*p*math.sin(phase*3))
    elif name == 'burst':
        geometry()
        # The shell bursts: plates are thrown out to lean from the nest rim
        # onto the floor, the cap flips away, the yolk sinks into the ash.
        for k, a in enumerate(PLATE_ANGLES):
            s = kit.smooth((t-.05-.03*k)/.55)
            q, loc = R.lean('plate_%d' % k, tangent(a), radial(a, 11.2*S, 5.2*S), lo=40, hi=170)
            R.fall(frame, 'plate_%d' % k, s, q, loc[:2], hop=6*S, final=loc)
        s = kit.smooth((t-.02)/.6)
        q = qmul(axis((0, 0, 1), math.radians(30)), axis(tangent(205), math.radians(160)))
        final = R.placement('cap', q, radial(205, 20.5, 0)[:2])
        R.fall(frame, 'cap', s, q, final[:2], hop=11*S, final=final)
        s = kit.smooth((t-.15)/.6)
        R.move(frame, 'yolk', (0, 0, -10.8*S*s))
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
    from tools.monster_models import phoenix_egg_animation as module
    print(module.build()['sha256'])

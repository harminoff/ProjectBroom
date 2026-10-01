"""Original sentinel (Brogue MK_SENTINEL): an ancient, faceless indigo-stone
statue on a plinth, holding aloft a gleaming warding crystal ringed by
floating crystal shards.

Presentation only. Brogue CE owns the sentinel's immobility (a turret),
slow spell casting, spark and healing bolts, negation death, rubble and every
outcome. The figure never moves off its plinth; the walk role is a static
rest. Only the crystal texels are fullbright (atlas-keyed shader); there is no
dynamic light, particle, projectile or collision here.
"""
import math
from . import guardian_kit as K
from .guardian_kit import Q, add, sub, mul, unit, lerp, smooth, window, frame_rotation, carved_block, stone_core, euler, along, IDENT
from .skeletal import assemble, sample_clips, rotate, qmul, axis

SKIN = 'graphics/BRGSNTL.png'
MODEL = 'mod/BrogueDoom/models/monsters/37_sentinel.iqm'
SHADER = 'mod/BrogueDoom/shaders/sentinel-crystal.fp'
LABEL = 'sentinel'
SCALE = .94
GLOW_REGION = (1536, 0, 512)   # atlas square (x, y, size) holding every emissive crystal island
STONE_REGION = (0, 512, 1536)
CRYSTAL = (3.0, 0.0, 57.0)
SHARDS = 5
HANDS = {'L': (3.2, 3.1, 52.4), 'R': (3.2, -3.1, 52.4)}


def _specs():
    specs = [('root', None, (0, 0, 0)), ('body_lower', 'root', (0, 0, 7)), ('body_upper', 'body_lower', (0, 0, 24)),
             ('head', 'body_upper', (.5, 0, 40))]
    for side, s in (('L', 1), ('R', -1)):
        sh = (0.0, s*8.6, 37.6); hand = HANDS[side]
        el = K.bend_joint(sh, hand, 9.4, 10.6, (-.1, s, -.35))
        specs += [(f'arm_{side}_upper', 'body_upper', K.r6(sh)), (f'arm_{side}_lower', f'arm_{side}_upper', K.r6(el)),
                  (f'arm_{side}_end', f'arm_{side}_lower', K.r6(hand))]
    specs.append(('crystal', 'root', CRYSTAL))
    specs += [(f'shard_{i}', 'crystal', K.r6(shard_rest(i))) for i in range(SHARDS)]
    return specs


def shard_rest(i):
    a = math.tau*i/SHARDS
    return add(CRYSTAL, (6.2*math.cos(a), 6.2*math.sin(a), 1.6*math.sin(2*a)))


kit = K.Kit(_specs(), SCALE)
BONES, REST, IDS = kit.BONES, kit.REST, kit.IDS
CLIPS = [('idle', 48, 16, True), ('rest', 40, 16, True), ('focus', 19, 30, False),
         ('mend', 19, 30, False), ('jolt', 15, 30, False), ('shatter', 45, 30, False)]


def diamond(h):
    """Box -> faceted bipyramid (crystal)."""
    return lambda v: (v[0]*max(.05, 1-abs(v[2])/h)**.9, v[1]*max(.05, 1-abs(v[2])/h)**.9, v[2])


def crystal_parts():
    parts = []
    def B(*a, **k):
        k.update(chip=0, rough=0, pillow=0, hewn=0, role='glow'); parts.append(carved_block(*a, **k)); return parts[-1]
    B('crystal_main', 'crystal', CRYSTAL, (2.6, 2.6, 5.4), rot=euler(0, 0, 45), bevel=.25, seed=701, step=1.4, shape=diamond(5.4))
    B('crystal_side_0', 'crystal', add(CRYSTAL, (.6, 2.0, -1.6)), (1.1, 1.1, 2.6), rot=euler(24, 0, 20), bevel=.15, seed=702, step=1.2,
      shape=diamond(2.6))
    B('crystal_side_1', 'crystal', add(CRYSTAL, (-.4, -2.1, -1.2)), (1.0, 1.0, 2.3), rot=euler(-26, 8, -30), bevel=.15, seed=703,
      step=1.2, shape=diamond(2.3))
    for i in range(SHARDS):
        B(f'shard_{i}', f'shard_{i}', shard_rest(i), (1.1, 1.1, 2.6), rot=euler(0, 0, 45+i*20), bevel=.12, seed=710+i, step=1.2,
          shape=diamond(2.6))
    return parts


def stone_parts():
    parts = []
    def B(*a, **k): parts.append(carved_block(*a, **k)); return parts[-1]
    def C(*a, **k): parts.append(stone_core(*a, **k)); return parts[-1]
    # Plinth: a stepped, chipped base the figure never leaves.
    B('plinth', 'root', (0, 0, 2.95), (10.2, 10.8, 2.3), bevel=1.2, seed=801, chip=1.3, pillow=.05)
    B('plinth_step', 'root', (0, 0, 5.7), (8.4, 9.0, .95), bevel=.7, seed=802, chip=.8)
    # Robed body: a flared hem column and a narrow, weathered torso.
    B('robe_hem', 'body_lower', (0, 0, 15.2), (6.2, 7.0, 8.6), bevel=4.2, seed=803, hewn=.14,
      shape=lambda v: (v[0]*(1+.2*max(0, -v[2]/8.6)), v[1]*(1+.2*max(0, -v[2]/8.6)), v[2]))
    B('robe_band', 'body_lower', (0, 0, 22.4), (5.9, 6.7, 1.1), bevel=.7, seed=804, pillow=.1)
    C('core_waist', 'body_upper', (0, 0, 24.5), 4.4, seed=805)
    B('torso', 'body_upper', (0, 0, 31.2), (5.0, 6.6, 6.4), bevel=2.6, seed=806,
      shape=lambda v: (v[0], v[1]*(.82+.18*(v[2]/6.4+1)/2), v[2]))
    B('mantle', 'body_upper', (0, 0, 37.2), (5.4, 9.4, 2.2), bevel=1.8, seed=807, pillow=.3)
    B('collar', 'body_upper', (.3, 0, 39.4), (3.8, 4.8, 1.0), bevel=.7, seed=808, pillow=.2)
    # Faceless, eroded head tilted up toward the crystal.
    C('core_neck', 'head', (.4, 0, 40.4), 2.6, seed=809)
    B('head_stone', 'head', (1.1, 0, 44.6), (3.6, 3.3, 4.2), rot=euler(0, -12, 0), bevel=3.1, seed=810, pillow=.3, hewn=.16, chip=.6)
    B('head_brow', 'head', (3.6, 0, 45.8), (1.2, 3.0, .9), rot=euler(0, -20, 0), bevel=.8, seed=811, pillow=.4, chip=.5)
    for side, s in (('L', 1), ('R', -1)):
        k = 820 if side == 'L' else 850
        sh, el, hd = kit.rest(f'arm_{side}_upper'), kit.rest(f'arm_{side}_lower'), kit.rest(f'arm_{side}_end')
        C(f'core_shoulder_{side}', f'arm_{side}_upper', sh, 3.0, seed=k)
        B(f'sleeve_upper_{side}', f'arm_{side}_upper', lerp(sh, el, .5), (2.4, 2.3, 4.6), rot=along(sh, el), seed=k+1)
        C(f'core_elbow_{side}', f'arm_{side}_lower', el, 2.2, seed=k+2)
        B(f'sleeve_lower_{side}', f'arm_{side}_lower', lerp(el, hd, .42), (2.3, 2.2, 4.0), rot=along(el, hd), seed=k+3,
          shape=lambda v: (v[0]*(1+.35*max(0, v[2]/4.0)), v[1]*(1+.35*max(0, v[2]/4.0)), v[2]))
        B(f'hand_{side}', f'arm_{side}_end', add(hd, (0, -s*.3, .6)), (1.3, 1.0, 2.0), rot=along(el, hd), bevel=.6, seed=k+4, chip=.3)
    return parts


def authoring_parts():
    parts = stone_parts()+crystal_parts()
    for p in parts: assert min(q[2] for q in p.vertices) > .2, p.name
    return parts


def build_parts():
    parts = authoring_parts()
    for p in parts:
        p.vertices = [mul(q, SCALE) for q in p.vertices]
        c, cols, half = p.box; p.box = (mul(c, SCALE), cols, mul(half, SCALE))
    return parts


def weights(part, v, uv): return [(IDS[part.bone], 1)]


def spin(deg): return Q(0, 0, deg)


def place_crystal(world, centre, turn, ring, ring_axis=(1, 0, 0), ring_radius=6.2, ring_tilt=0.0, jitter=0.0):
    """Crystal at ``centre``, turned ``turn`` degrees; shards on a ring of ``ring_radius``.

    ``ring``: 0 = rest orbit around the crystal, 1 = the ring stands in the plane
    whose normal is ``ring_axis`` (a burst facing that direction).
    """
    world[IDS['crystal']] = (tuple(centre), spin(turn))
    n = unit(ring_axis); u = unit(sub((0, 0, 1), mul(n, n[2]))) if abs(n[2]) < .9 else (1, 0, 0); v = K.cross(n, u)
    for i in range(SHARDS):
        a = math.tau*i/SHARDS+math.radians(turn)
        rest_off = sub(shard_rest(i), CRYSTAL)
        orbit = rotate(spin(turn), rest_off)
        burst = add(mul(u, ring_radius*math.cos(a)), mul(v, ring_radius*math.sin(a)))
        off = lerp(orbit, burst, ring)
        off = add(off, (0, 0, jitter*math.sin(7.3*i+turn)))
        world[IDS[f'shard_{i}']] = (add(centre, off), qmul(axis((0, 0, 1), math.radians(turn*2+i*40)), Q(ring_tilt*(i % 2*2-1), 0, 0)))


def hands_on(world, centre, spread=0.0, lift=(0, 0, 0)):
    for side, s in (('L', 1), ('R', -1)):
        target = add(add(centre, sub(HANDS[side], CRYSTAL)), add((0, s*spread, 0), lift))
        kit.limb(world, f'arm_{side}', 'body_upper', target, (-.1, s, -.35), None, reach=.999)


def body(rot, shift=None):
    return kit.fk(kit.body_frame(rot, shift or {}))


RUBBLE = {
    'body_lower': ((-3, 3), Q(0, -86, 30)), 'body_upper': ((14, -9), Q(4, 88, -20)), 'head': ((23, 9), Q(20, 70, 40)),
    'arm_L_upper': ((6, 17), Q(0, -90, 10)), 'arm_R_upper': ((-12, -16), Q(0, 90, -20)),
    'arm_L_lower': ((16, 21), Q(0, 90, 60)), 'arm_R_lower': ((2, -22), Q(0, -90, 40)),
    'arm_L_end': ((25, 2), Q(0, 90, 0)), 'arm_R_end': ((-20, 8), Q(0, 90, 0)),
    'crystal': ((22, -18), Q(0, 88, 35)),
}
SHARD_FLOOR = [(-22, -6), (9, 26), (27, -4), (-6, -26), (-24, 18)]
STACK = {'body_upper': .6}
TIMING = {'crystal': (.02, .42), 'head': (.2, .6), 'body_upper': (.3, .78), 'body_lower': (.42, .9),
          'arm_L_upper': (.28, .66), 'arm_R_upper': (.3, .68), 'arm_L_lower': (.22, .6), 'arm_R_lower': (.24, .62),
          'arm_L_end': (.14, .5), 'arm_R_end': (.16, .52)}
_RUBBLE = None


def rubble():
    parts = authoring_parts(); layout = dict(RUBBLE)
    for i, xy in enumerate(SHARD_FLOOR): layout[f'shard_{i}'] = (xy, Q(0, 90, i*50))
    world = kit.rubble(parts, layout, STACK)
    world[IDS['root']] = (kit.rest('root'), IDENT)
    return world


def pose(name, t):
    global _RUBBLE
    phase = math.tau*t
    if name in ('idle', 'rest'):
        # Immobile: only the warding crystal turns and bobs; shards orbit it.
        bob = (.5 if name == 'idle' else .3)*math.sin(phase)
        world = body({'head': Q(0, -2+1.5*math.sin(phase), 0)})
        centre = add(CRYSTAL, (0, 0, bob))
        place_crystal(world, centre, 360*t, 0.0)
        hands_on(world, centre)
    elif name == 'focus':
        # Casting pulse: gather (t~.25) with the crystal drawn down to the chest, then on
        # the middle frame the crystal is thrust forward at arm's length and the shards
        # blaze outward into a wide ring facing the target.
        gather = window(t, .04, .26)*(1-window(t, .34, .46))
        cast = window(t, .34, .46)*(1-window(t, .72, 1.0))
        world = body({'body_lower': Q(0, 3*gather-4*cast, 0), 'body_upper': Q(0, 8*gather-12*cast, 0),
                      'head': Q(0, 10*gather-6*cast, 0)})
        centre = lerp(lerp(CRYSTAL, (6.5, 0, 45.0), gather), (15.0, 0, 48.0), cast)
        place_crystal(world, centre, 40*t+90*cast, cast, ring_axis=(1, 0, 0), ring_radius=6.2+11.0*cast, ring_tilt=30*cast)
        hands_on(world, centre, spread=2.5*cast, lift=(-1.0*cast, 0, -1.5*cast))
    elif name == 'mend':
        # Healing: the crystal is lowered into cupped hands before the chest and the shards
        # spread into a wide, low horizontal ring around the whole figure.
        low = window(t, .06, .4)*(1-window(t, .72, 1.0))
        world = body({'body_upper': Q(0, 10*low, 0), 'head': Q(0, 22*low, 0)})
        centre = lerp(CRYSTAL, (8.0, 0, 38.0), low)
        place_crystal(world, centre, 90*t, low, ring_axis=(0, 0, 1), ring_radius=6.2+15.5*low)
        for i in range(SHARDS):
            loc, q = world[IDS[f'shard_{i}']]; world[IDS[f'shard_{i}']] = (add(loc, (-7*low, 0, -6*low)), q)
        hands_on(world, centre, spread=-.5*low)
    elif name == 'jolt':
        k = math.sin(math.pi*t)**2
        world = body({'body_upper': Q(4*k, -6*k, 0), 'head': Q(-6*k, -12*k, 5*k)}, {'body_lower': (-.6*k, 0, 0)})
        centre = add(CRYSTAL, (-2.5*k, .6*k, 1.2*k))
        place_crystal(world, centre, 30*t, .15*k, ring_axis=(1, 0, 0), ring_radius=8, jitter=1.5*k)
        hands_on(world, centre, spread=1.0*k)
    elif name == 'shatter':
        # The crystal cracks loose first and its shards scatter to the floor; then the
        # statue breaks at the waist and topples into rubble beside its plinth.
        if _RUBBLE is None: _RUBBLE = rubble()
        start = body({})
        place_crystal(start, CRYSTAL, 0, 0.0); hands_on(start, CRYSTAL)
        # Shards first burst outward, then fall.
        timing = dict(TIMING)
        for i in range(SHARDS): timing[f'shard_{i}'] = (.04+.02*i, .4+.04*i)
        world = kit.collapse(start, _RUBBLE, t, timing, arcs={**{f'shard_{i}': 9.0 for i in range(SHARDS)}, 'crystal': 4.0})
        world[IDS['root']] = (kit.rest('root'), IDENT)
    return kit.frame_from_world(world)


def geometry():
    parts = build_parts()
    stone = [p for p in parts if p.role != 'glow']; glow = [p for p in parts if p.role == 'glow']
    K.layout_regions([(stone, STONE_REGION), (glow, GLOW_REGION)])
    return assemble(parts, weights)


def matrices(frame): return kit.RIG.matrices(frame)
def deform(v, w, frame): return kit.RIG.deform(v, w, frame)
def animation_data(v, w): return sample_clips(kit.RIG, CLIPS, pose, v, w)


def build():
    from . import sentinel_materials as M
    parts, v, n, uv, tr, w = geometry()
    image, spec = M.paint(parts)
    return K.export(__import__(__name__, fromlist=['x']), 'BRG-M37', 'sentinel', LABEL, parts, v, n, uv, tr, w, image, spec,
                    dict(emissive=dict(region=list(GLOW_REGION), shader='shaders/sentinel-crystal.fp')), maps=False)


if __name__ == '__main__':
    import importlib
    print(importlib.import_module('tools.monster_models.sentinel_animation').build()['sha256'])

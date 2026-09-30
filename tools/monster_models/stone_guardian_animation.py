"""Original stone guardian (Brogue MK_GUARDIAN): a monumental vault statue of a
knight with a great double-bitted battleaxe, carved from rigid stone segments.

Presentation only. Brogue CE owns everything the guardian does: it is
inanimate and invulnerable to weapons, moves only when the player moves,
reflects, dies if negated, leaves rubble, and resolves every strike. These
clips only illustrate those outcomes; nothing feeds back to the simulation.
"""
import math
from . import guardian_kit as K
from .guardian_kit import Q, add, sub, mul, unit, lerp, smooth, window, frame_rotation, carved_block, stone_core, euler, IDENT
from .skeletal import assemble, sample_clips, rotate, qmul

SKIN = 'graphics/BRGSGRD.png'
MODEL = 'mod/BrogueDoom/models/monsters/57_guardian.iqm'
LABEL = 'guardian'  # mesh label must match MK_GUARDIAN
SCALE = .9
# Rest: the axe stands head-down before the statue, both fists stacked on the haft.
GRIP_R = (11.0, 0.0, 40.0)
GRIP_L = (11.0, 0.0, 44.6)
HAFT = (0, 0, -1)          # rest direction from the grip toward the axe head
BLADE = (0, 1, 0)          # rest direction of the axe bits (faces the camera)
HEAD_AT = 29.0             # grip-to-axe-head-centre distance along the haft
kit = K.Kit(K.knight_specs(GRIP_R, GRIP_L), SCALE)
BONES, REST, IDS = kit.BONES, kit.REST, kit.IDS
CLIPS = [('idle', 48, 16, True), ('advance', 36, 30, True), ('cleave', 19, 30, False),
         ('sweep', 19, 30, False), ('recoil', 15, 30, False), ('crumble', 45, 30, False)]


def axe_parts():
    """Battleaxe authored in place at rest: vertical haft, head down, bits along Y."""
    g = GRIP_R; parts = []; x, y = g[0], g[1]
    hz = g[2]-HEAD_AT
    def B(*a, **k): k.setdefault('rough', .12); parts.append(carved_block(*a, **k)); return parts[-1]
    B('axe_haft', 'weapon', (x, y, (hz+g[2]+8.5)/2), (1.05, 1.05, (g[2]+8.5-hz)/2), bevel=.9, seed=301, chip=.3, pillow=0, hewn=.02)
    B('axe_pommel', 'weapon', (x, y, g[2]+9.2), (1.7, 1.7, 1.3), bevel=1.0, seed=302, chip=.4)
    for i, dz in enumerate((-9.5, -17.5)):
        B(f'axe_binding_{i}', 'weapon', (x, y, g[2]+dz), (1.45, 1.45, .55), bevel=.4, seed=303+i, chip=.2, pillow=0)
    B('axe_socket', 'weapon', (x, y, hz), (2.1, 2.5, 5.2), bevel=1.2, seed=305, chip=.6)
    B('axe_spike', 'weapon', (x, y, hz-6.4), (1.3, 1.3, 2.6), bevel=.7, seed=306, chip=.3,
      shape=lambda v: (v[0]*(.35+.65*(v[2]+2.6)/5.2), v[1]*(.35+.65*(v[2]+2.6)/5.2), v[2]))
    B('axe_top', 'weapon', (x, y, hz+6.1), (1.5, 1.5, 1.0), bevel=.6, seed=307, chip=.3)
    for s in (1, -1):
        def crescent(v, s=s):
            t = (s*v[1]/5.8+1)/2  # 0 at the socket, 1 at the cutting edge
            return (v[0]*(1-.62*t), v[1]+s*.9*(1-(v[2]/6.2)**2)*t, v[2]*(.5+.8*t*t))
        B(f'axe_bit_{s}', 'weapon', (x, y+s*7.6, hz+.4), (1.0, 5.8, 6.2), bevel=.8, seed=308+s, chip=.8, pillow=.05, shape=crescent)
    return parts


def authoring_parts():
    parts = K.knight_parts(kit, head='bearded') + axe_parts()
    for p in parts: assert min(q[2] for q in p.vertices) > .2, p.name
    return parts


def build_parts():
    parts = authoring_parts()
    for p in parts:
        p.vertices = [mul(q, SCALE) for q in p.vertices]
        c, cols, half = p.box; p.box = (mul(c, SCALE), cols, mul(half, SCALE))
    return parts


def weights(part, v, uv): return [(IDS[part.bone], 1)]


def axe(direction, pole):
    return frame_rotation(HAFT, BLADE, direction, pole)


def head_centre(grip, q): return add(grip, rotate(q, mul(HAFT, HEAD_AT)))


def pose_body(rot, shift, cape=.72, sway=(0, 0, 0)):
    world = kit.fk(kit.body_frame(rot, shift)); K.hang_cape(kit, world, cape, sway); return world


_RUBBLE = None
RUBBLE = {
    'leg_L_end': ((3, 9.5), Q(0, 0, 8)), 'leg_R_end': ((1.5, -10.5), Q(0, 0, -6)),
    'leg_L_lower': ((16, 13), Q(0, -90, -10)), 'leg_R_lower': ((13, -14.5), Q(0, -92, 12)),
    'leg_L_upper': ((4, 13.5), Q(6, -88, 14)), 'leg_R_upper': ((1, -15), Q(-6, -86, -9)),
    'pelvis': ((-2, 0), Q(0, -12, 4)), 'waist': ((8, 1), Q(4, -88, 6)),
    'chest': ((-17, 1), Q(0, -90, 3)), 'head': ((-16, -19), Q(8, 94, -30)),
    'arm_L_upper': ((-9, 22), Q(0, -90, 0)), 'arm_R_upper': ((-10, -23), Q(0, -90, 0)),
    'arm_L_lower': ((6, 22), Q(0, -90, 4)), 'arm_R_lower': ((6, -24), Q(0, -88, -4)),
    'arm_L_end': ((24, 16), Q(0, -90, 8)), 'arm_R_end': ((23, -18), Q(0, -86, -6)),
    'weapon': ((5, -7), Q(0, 90, -45)), 'cape': ((-13, 0), Q(0, -86, 90)),
}
STACK = {'chest': 2.2, 'pelvis': 3.0, 'leg_L_upper': 1.0, 'leg_R_upper': 1.0}
TIMING = {'leg_L_end': (.1, .4), 'leg_R_end': (.1, .4), 'leg_L_lower': (.3, .66), 'leg_R_lower': (.28, .64),
          'leg_L_upper': (.3, .7), 'leg_R_upper': (.3, .7), 'pelvis': (.26, .72), 'waist': (.3, .76),
          'chest': (.36, .88), 'head': (.22, .64), 'arm_L_upper': (.4, .78), 'arm_R_upper': (.42, .8),
          'arm_L_lower': (.36, .74), 'arm_R_lower': (.38, .76), 'arm_L_end': (.34, .72), 'arm_R_end': (.36, .74),
          'weapon': (.08, .5), 'cape': (.4, .9)}


def standing(t_idle=0.0):
    world = pose_body({'head': Q(0, 2*math.cos(t_idle), 5*math.sin(t_idle))}, {'pelvis': (0, .25*math.sin(t_idle), 0)})
    K.grip_hands(kit, world, GRIP_R, IDENT)
    K.plant_legs(kit, world)
    return world


def kneel(s):
    world = pose_body({'pelvis': Q(0, 8*s, 0), 'chest': Q(0, 14*s, 0), 'head': Q(0, 16*s, 0)}, {'pelvis': (-3*s, 0, -9*s)})
    grip = add(GRIP_R, (4*s, -1*s, -8*s)); q = axe(unit((.55*s, -.1*s, -1)), BLADE)
    K.grip_hands(kit, world, grip, q, reach=.99)
    K.plant_legs(kit, world)
    return world


def pose(name, t):
    global _RUBBLE
    phase = math.tau*t
    if name == 'idle':
        # A statue's vigil: only the carved head slowly sweeps its gaze.
        world = standing(phase)
    elif name == 'advance':
        sway = math.sin(phase); bob = -1.0*abs(math.cos(phase))
        world = pose_body({'pelvis': Q(-2.5*sway, 0, 3*math.cos(phase)), 'chest': Q(2*sway, 4, -5*math.cos(phase)),
                           'head': Q(-1.5*sway, -2, 3*math.cos(phase))}, {'pelvis': (0, 1.4*sway, bob)})
        # The axe is lifted off the floor and carried forward, head low.
        grip = add(GRIP_R, (1.5, 0, 3.0+bob)); q = axe(unit((.5, .04*sway, -1)), BLADE)
        K.grip_hands(kit, world, grip, q, reach=.995)
        feet = {}; fq = {}
        for side, off in (('L', 0), ('R', .5)):
            u = (t+off) % 1
            if u < .6: dx = 4.0-8.0*u/.6; lift = 0.0; pitch = 0.0
            else:
                k = (u-.6)/.4; dx = -4.0+8*smooth(k); lift = 3.6*math.sin(math.pi*k); pitch = -8*math.sin(math.pi*k)
            feet[side] = add(kit.rest(f'leg_{side}_end'), (dx, 0, lift)); fq[side] = Q(0, pitch, 0)
        K.plant_legs(kit, world, feet, foot_q=fq)
    elif name == 'cleave':
        # Windup (t~.25): the axe is hauled up behind the right shoulder. The middle
        # frame holds a huge overhead chop finished low: the statue hinges forward
        # in a wide lunge and the axe head strikes the floor far in front.
        up = window(t, .04, .26)*(1-window(t, .34, .47))
        hit = window(t, .34, .47)*(1-window(t, .7, 1.0))
        world = pose_body({'pelvis': Q(0, -4*up+14*hit, -6*up), 'waist': Q(0, -5*up+10*hit, -6*up),
                           'chest': Q(0, -8*up+14*hit, -10*up), 'head': Q(0, 4*up-18*hit, 6*up)},
                          {'pelvis': (-1.5*up+2*hit, 0, -.5*up-8.5*hit)})
        rest_q = IDENT
        raised = axe(unit((-.7, -.25, .68)), unit((.1, 1, .15)))
        struck = axe(unit((.62, -.34, -.71)), unit((.3, 1, 0)))
        grip = lerp(lerp(GRIP_R, (-1.0, -9.0, 60.0), up), (5.0, -3.0, 32.0), hit)
        q = K.slerp(K.slerp(rest_q, raised, up), struck, hit)
        K.grip_hands(kit, world, grip, q, reach=.999, slide={'R': 9*hit, 'L': 3*hit},
                     bends={'R': (-.3, -1, -.2), 'L': (-.3, 1, -.4)})
        K.plant_legs(kit, world, {'L': add(kit.rest('leg_L_end'), (8*hit, 1.5*hit, 0)),
                                  'R': add(kit.rest('leg_R_end'), (-6*hit, -2.5*hit, 0))},
                     foot_q={'L': Q(0, 0, 8*hit), 'R': Q(0, 0, -14*hit)})
    elif name == 'sweep':
        # Cocked across the left hip at t~.25; the middle frame holds a wide
        # horizontal sweep: the axe swung far out to the right front at waist
        # height, torso twisted, stance braced wide.
        wind = window(t, .04, .26)*(1-window(t, .33, .46))
        swing = window(t, .33, .46)*(1-window(t, .7, 1.0))
        world = pose_body({'waist': Q(0, 0, 12*wind-18*swing), 'chest': Q(0, 4*wind+6*swing, 20*wind-26*swing),
                           'head': Q(0, 0, -10*wind+14*swing)}, {'pelvis': (0, 1.5*wind-1.2*swing, -1.5*wind-5*swing)})
        cocked = axe(unit((-.74, .45, .42)), unit((0, 0, 1)))
        swept = axe(unit((.62, -.78, -.05)), unit((0, 0, 1)))
        grip = add(lerp(lerp(GRIP_R, (3.0, 6.0, 38.0), wind), (7.0, -5.0, 34.0), swing), (-14*4*swing*(1-swing), 0, 0))
        q = K.slerp(K.slerp(IDENT, cocked, wind), swept, swing)
        K.grip_hands(kit, world, grip, q, reach=.999, slide={'R': 1*swing, 'L': 1*swing},
                     bends={'R': (-.4, -1, -.6), 'L': (-.5, 1, -.5)})
        K.plant_legs(kit, world, {'L': add(kit.rest('leg_L_end'), (2*swing, 3.5*swing, 0)),
                                  'R': add(kit.rest('leg_R_end'), (-1*swing, -3.5*swing, 0))},
                     foot_q={'L': Q(0, 0, 10*swing), 'R': Q(0, 0, -10*swing)})
    elif name == 'recoil':
        k = math.sin(math.pi*t)**2
        world = pose_body({'waist': Q(3*k, -5*k, 0), 'chest': Q(3*k, -9*k, -6*k), 'head': Q(-6*k, -14*k, 8*k)},
                          {'pelvis': (-2.0*k, 0, -1.2*k)})
        grip = add(GRIP_R, (-2.5*k, 0, 1.5*k)); q = axe(unit((.22*k, 0, -1)), BLADE)
        K.grip_hands(kit, world, grip, q, reach=.995)
        K.plant_legs(kit, world)
    elif name == 'crumble':
        if _RUBBLE is None: _RUBBLE = kit.rubble(authoring_parts(), RUBBLE, STACK)
        world = kit.collapse(kneel(window(t, 0, .34)), _RUBBLE, t, TIMING, arcs={'weapon': 10.0})
    return kit.frame_from_world(world)


def geometry():
    parts = build_parts(); K.layout_islands(parts)
    return assemble(parts, weights)


def matrices(frame): return kit.RIG.matrices(frame)
def deform(v, w, frame): return kit.RIG.deform(v, w, frame)
def animation_data(v, w): return sample_clips(kit.RIG, CLIPS, pose, v, w)


def build():
    from . import stone_guardian_materials as M
    parts, v, n, uv, tr, w = geometry()
    image, spec = M.paint(parts)
    return K.export(__import__(__name__, fromlist=['x']), 'BRG-M57', 'stone_guardian', LABEL, parts, v, n, uv, tr, w, image, spec)


if __name__ == '__main__':
    import importlib
    print(importlib.import_module('tools.monster_models.stone_guardian_animation').build()['sha256'])

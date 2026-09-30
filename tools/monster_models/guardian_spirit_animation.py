"""Original guardian spirit (Brogue MK_CHARM_GUARDIAN): the crimson spectral outline
of a knight with a great bearded battleaxe, hovering just above the floor. It has
the guardian family's skeleton but continuous, smooth armour shells, and is
drawn as translucent fullbright additive light in Brogue's spectral image
colour (the same crimson as the spectral sword), rim-bright with a dim core.

Presentation only. Brogue CE owns everything: the charm that summons it, its
allegiance, invulnerability, reflection, negation death, timing and every
strike. The ethereal light it casts in Brogue (SPECTRAL_IMAGE_LIGHT) stays a
Brogue light; this model is only additive geometry (shader
``guardian-spirit-glow.fp``), with no dynamic light, particles or collision.
"""
import math
from . import guardian_kit as K
from .guardian_kit import Q, add, sub, mul, unit, lerp, smooth, window, frame_rotation, carved_block, euler, IDENT
from .skeletal import assemble, sample_clips, rotate, qmul

SKIN = 'graphics/BRGGSPR.png'
MODEL = 'mod/BrogueDoom/models/monsters/59_charm_guardian.iqm'
SHADER = 'mod/BrogueDoom/shaders/guardian-spirit-glow.fp'
LABEL = 'charm_guardian'  # mesh label must match MK_CHARM_GUARDIAN
SCALE = .9
HOVER = 4.0
# Rest: the axe is held at port across the body, head high on the spirit's left.
GRIP_R = (8.5, -8.0, 33.0)
HAFT = unit((.04, .72, .69))
BLADE = unit((.25, .55, -.8))
GRIP_L = K.r6(add(GRIP_R, mul(HAFT, 14.0)))
HEAD_AT = 29.0
kit = K.Kit(K.knight_specs(GRIP_R, GRIP_L), SCALE)
BONES, REST, IDS = kit.BONES, kit.REST, kit.IDS
CLIPS = [('idle', 48, 16, True), ('glide', 36, 30, True), ('reap', 19, 30, False),
         ('jab', 19, 30, False), ('recoil', 15, 30, False), ('fade', 45, 30, False)]


def axe_parts():
    parts = []; g = GRIP_R; H = HAFT
    def at(d): return add(g, mul(H, d))
    rot = K.along(at(0), at(1), BLADE)   # local z along the haft, x toward the blade
    def B(*a, **k):
        k.update(chip=0, rough=.03, hewn=.01); k.setdefault('pillow', .05); parts.append(carved_block(*a, **k)); return parts[-1]
    B('axe_haft', 'weapon', at(12.5), (.95, .95, 21.5), rot=rot, bevel=.8, seed=901)
    B('axe_butt', 'weapon', at(-9.6), (1.4, 1.4, 1.1), rot=rot, bevel=.9, seed=902)
    B('axe_socket', 'weapon', at(HEAD_AT), (1.8, 1.8, 3.6), rot=rot, bevel=.9, seed=903)
    B('axe_spike', 'weapon', at(HEAD_AT+5.6), (1.0, 1.0, 2.6), rot=rot, bevel=.5, seed=904,
      shape=lambda v: (v[0]*(.3+.7*(2.6-v[2])/5.2), v[1]*(.3+.7*(2.6-v[2])/5.2), v[2]))
    # One great bearded crescent bit, with a short back hook.
    def bit(v):
        t = (v[0]/6.4+1)/2   # 0 at the socket, 1 at the edge
        return (v[0]+.6*(1-(v[2]/7.2)**2)*t, v[1]*(1-.7*t), v[2]*(.45+.85*t*t)-1.6*t*t)
    B('axe_bit', 'weapon', add(at(HEAD_AT), rotate_to(rot, (7.6, 0, 0))), (6.4, .8, 7.2), rot=rot, bevel=.6, seed=905, shape=bit)
    B('axe_hook', 'weapon', add(at(HEAD_AT), rotate_to(rot, (-3.6, 0, .4))), (2.0, .7, 1.4), rot=rot, bevel=.5, seed=906,
      shape=lambda v: (v[0], v[1], v[2]+.6*max(0, -v[0]/2.0)))
    return parts


def rotate_to(cols, v): return add(add(mul(cols[0], v[0]), mul(cols[1], v[1])), mul(cols[2], v[2]))


def spirit_armour(kit):
    """Continuous armour shells for the ghost knight (same skeleton as the family's knight kit).

    One cuirass shell, one flared skirt, one tapered sleeve per upper arm and
    forearm with a single elbow couter, and a tapered thigh plus greave with a
    knee cop per leg. The body is rendered opaque (see the shader), so only the
    nearest surface shows and overlapping shells do not stack light.
    """
    parts = []
    def B(*a, **k):
        k.setdefault('chip', 0); k.setdefault('rough', .04); k.setdefault('hewn', .02); k.setdefault('pillow', .1)
        parts.append(carved_block(*a, **k)); return parts[-1]
    def C(*a, **k): parts.append(K.stone_core(*a, **k)); return parts[-1]
    R = kit.rest
    def taper(h, a, b):
        """Scale x/y from ``a`` at the -z end to ``b`` at the +z end of a block with half length ``h``."""
        return lambda v: (v[0]*(a+(b-a)*max(0.0, min(1.0, (v[2]/h+1)/2))), v[1]*(a+(b-a)*max(0.0, min(1.0, (v[2]/h+1)/2))), v[2])
    # Pelvis: a slim belt and a single flared skirt shell with a scalloped hem.
    B('belt', 'pelvis', (.2, 0, 33.6), (6.6, 9.0, 1.3), bevel=1.2, seed=102, pillow=.2)
    B('skirt', 'pelvis', (.2, 0, 26.4), (8.0, 10.2, 7.6), bevel=3.0, seed=104, pillow=.15,
      shape=lambda v: (v[0]*(.8+.42*max(0.0, min(1.0, (1-v[2]/7.6)/2))), v[1]*(.8+.5*max(0.0, min(1.0, (1-v[2]/7.6)/2))),
                       v[2]+.9*math.sin(v[1]*.9)*max(0.0, -v[2]/7.6)))
    # Waist: dark core plus a thin lame under the cuirass.
    C('core_waist', 'waist', (0, 0, 38.0), 5.0, seed=112)
    B('lame_upper', 'waist', (.4, 0, 40.4), (6.2, 8.4, 2.4), bevel=1.6, seed=114, pillow=.3, shape=taper(2.4, .96, .86))
    # Chest: one cuirass shell tapering from broad shoulders to the waist with a forward keel, a gorget cone, one backplate.
    def cuirass(v):
        x, y, z = v; t = max(0.0, min(1.0, (z/8.8+1)/2))
        return (x+2.6*max(0, 1-abs(y)/11.5)**1.5*(.3+.7*t)*(x > 0), y*(.56+.44*t**.8), z)
    B('breastplate', 'chest', (.4, 0, 50.2), (7.4, 12.6, 8.8), bevel=5.4, seed=115, shape=cuirass, pillow=.14)
    B('gorget', 'chest', (.4, 0, 57.6), (5.2, 6.6, 2.0), bevel=1.6, seed=116, pillow=.25, shape=taper(2.0, .8, 1.0))
    B('backplate_0', 'chest', (-7.6, 0, 51.4), (1.3, 8.6, 5.6), bevel=1.2, seed=117, pillow=.35, shape=taper(5.6, .6, 1.0))
    B('cape', 'cape', (-10.2, 0, 34.0), (1.1, 12.0, 21.0), rot=euler(0, -7, 0), bevel=1.0, seed=119, pillow=.1, hewn=.06,
      shape=lambda v: (v[0]-2.4*max(0, -v[2]/21)**2+.8*math.sin(v[1]*.55), v[1]*(.62+.38*(v[2]/21+1)/2)*(1+.5*max(0, -v[2]/21)), v[2]))
    B('cape_clasp', 'cape', (-6.4, 0, 56.4), (1.8, 8.0, 1.5), bevel=1.2, seed=120, pillow=.3)
    # Head: a rounded, crested great helm with bright visor slits.
    C('core_neck', 'head', (.6, 0, 58.6), 3.4, seed=121)
    B('helm_dome', 'head', (.8, 0, 64.0), (5.7, 5.3, 6.4), bevel=5.0, seed=122, pillow=.2,
      shape=lambda v: (v[0]+.9*max(0, 1-abs(v[1])/5.3)*(v[0] > 0), v[1]*(1-.14*max(0, v[2]/6.4)), v[2]))
    B('helm_crest', 'head', (-.6, 0, 71.2), (5.6, .9, 1.6), bevel=.8, seed=124, pillow=.2,
      shape=lambda v: (v[0], v[1], v[2]-.08*v[0]*v[0]/5.6))
    B('helm_visor_rib', 'head', (7.0, 0, 62.6), (.7, .8, 3.6), bevel=.6, seed=125)
    for sgn in (1, -1):
        B(f'face_eye_{sgn}', 'head', (6.7, sgn*2.5, 65.0), (.7, 1.7, .45), bevel=.35, seed=128+sgn, role='void', pillow=0, hewn=0)
    B('helm_band', 'head', (.8, 0, 58.8), (5.6, 5.4, 1.0), bevel=1.0, seed=126, pillow=.1)
    # Arms: a domed pauldron, one tapered sleeve per segment, a single elbow couter, a fist.
    def dome(rx, ry, drop):
        return lambda v: (v[0], v[1], v[2]-drop*((v[0]/rx)**2+(v[1]/ry)**2))
    for side, sgn in (('L', 1), ('R', -1)):
        k = 140 if side == 'L' else 170
        sh, el, wr = R(f'arm_{side}_upper'), R(f'arm_{side}_lower'), R(f'arm_{side}_end')
        B(f'pauldron_{side}', f'arm_{side}_upper', add(sh, (-.3, sgn*1.6, 1.9)), (6.8, 6.2, 3.1), rot=euler(sgn*-20, 0, 0),
          bevel=2.6, seed=k, pillow=.2, shape=dome(6.8, 6.2, 3.6))
        C(f'core_shoulder_{side}', f'arm_{side}_upper', add(sh, (0, 0, -1)), 3.6, seed=k+2)
        hu = math.dist(sh, el)/2+1.4
        B(f'sleeve_upper_{side}', f'arm_{side}_upper', lerp(sh, el, .5), (3.4, 3.4, hu), rot=K.along(sh, el), bevel=1.7, seed=k+3, pillow=.08,
          shape=taper(hu, 1.0, .8))
        C(f'core_elbow_{side}', f'arm_{side}_lower', el, 3.0, seed=k+4)
        B(f'couter_{side}', f'arm_{side}_lower', add(el, mul(unit(sub(el, lerp(sh, wr, .5))), 1.2)), (2.6, 3.1, 2.7),
          rot=K.along(el, add(el, sub(el, lerp(sh, wr, .5)))), bevel=2.5, seed=k+5, pillow=.3)
        hl = math.dist(el, wr)/2+1.4
        B(f'sleeve_lower_{side}', f'arm_{side}_lower', lerp(el, wr, .5), (3.0, 2.9, hl), rot=K.along(el, wr), bevel=1.5, seed=k+6, pillow=.08,
          shape=taper(hl, .95, .75))
        grip = add(wr, mul(unit(sub(wr, el)), 3.0))
        B(f'gauntlet_{side}', f'arm_{side}_end', grip, (2.9, 2.6, 3.2), rot=K.along(el, wr), bevel=2.2, seed=k+8, pillow=.1)
    # Legs: a tapered thigh, a knee cop and a greave that tapers away into smoke.
    for side, sgn in (('L', 1), ('R', -1)):
        k = 200 if side == 'L' else 230
        hp, kn, an = R(f'leg_{side}_upper'), R(f'leg_{side}_lower'), R(f'leg_{side}_end')
        C(f'core_hip_{side}', f'leg_{side}_upper', hp, 4.0, seed=k)
        B(f'cuisse_{side}', f'leg_{side}_upper', lerp(hp, kn, .5), (4.2, 3.9, 7.4), rot=K.along(hp, kn), bevel=2.2, seed=k+1, pillow=.08,
          shape=taper(7.4, 1.0, .74))
        C(f'core_knee_{side}', f'leg_{side}_lower', kn, 3.4, seed=k+2)
        B(f'poleyn_{side}', f'leg_{side}_lower', add(kn, (2.6, 0, .3)), (2.4, 3.3, 3.0), bevel=2.4, seed=k+3, pillow=.4)
        B(f'greave_{side}', f'leg_{side}_lower', lerp(kn, an, .45), (3.4, 3.3, 7.2), rot=K.along(kn, an), bevel=1.8, seed=k+4, pillow=.08,
          shape=lambda v: (v[0]*(1-.62*max(0, min(1, (v[2]/7.2+1)/2))), v[1]*(1-.62*max(0, min(1, (v[2]/7.2+1)/2))), v[2]))
    return parts


def authoring_parts():
    parts = spirit_armour(kit) + axe_parts()
    for p in parts: assert min(q[2] for q in p.vertices) > .2, p.name
    return parts


def build_parts():
    parts = authoring_parts()
    for p in parts:
        p.vertices = [mul(q, SCALE) for q in p.vertices]
        c, cols, half = p.box; p.box = (mul(c, SCALE), cols, mul(half, SCALE))
    return parts


def weights(part, v, uv): return [(IDS[part.bone], 1)]


def axe(direction, pole): return frame_rotation(HAFT, BLADE, direction, pole)


def body(rot, shift, lift, cape=.8, sway=(0, 0, 0)):
    shift = dict(shift); p = shift.get('pelvis', (0, 0, 0)); shift['pelvis'] = add(p, (0, 0, lift))
    world = kit.fk(kit.body_frame(rot, shift)); K.hang_cape(kit, world, cape, sway); return world


def dangle(world, lift, dx=(0, 0), pitch=(18, 18)):
    """Weightless legs: the tapered greaves hang below the hovering body."""
    feet = {s: add(kit.rest(f'leg_{s}_end'), (d, 0, lift+1.5)) for s, d in zip('LR', dx)}
    K.plant_legs(kit, world, feet, foot_q={s: Q(0, p, 0) for s, p in zip('LR', pitch)})


RUBBLE = {
    'leg_L_end': ((4, 9), Q(0, -90, 10)), 'leg_R_end': ((3, -10), Q(0, -90, -8)),
    'leg_L_lower': ((10, 10), Q(0, -90, -10)), 'leg_R_lower': ((9, -11), Q(0, -92, 12)),
    'leg_L_upper': ((0, 9), Q(6, -88, 14)), 'leg_R_upper': ((-1, -10), Q(-6, -86, -9)),
    'pelvis': ((-3, 0), Q(0, -8, 4)), 'waist': ((4, 1), Q(4, -88, 6)),
    'chest': ((-12, 0), Q(0, -90, 3)), 'head': ((15, 6), Q(10, -84, 40)),
    'arm_L_upper': ((-6, 17), Q(0, -90, 0)), 'arm_R_upper': ((-7, -18), Q(0, -90, 0)),
    'arm_L_lower': ((7, 18), Q(0, -90, 4)), 'arm_R_lower': ((7, -18), Q(0, -88, -4)),
    'arm_L_end': ((18, 14), Q(0, -90, 8)), 'arm_R_end': ((18, -14), Q(0, -86, -6)),
    'weapon': ((4, -4), frame_rotation(HAFT, BLADE, (.8, -.6, 0), (.6, .8, 0))), 'cape': ((-15, 0), Q(0, -86, 90)),
}
STACK = {'chest': 2.2, 'pelvis': 1.5}
TIMING = {'leg_L_end': (.1, .36), 'leg_R_end': (.12, .38), 'leg_L_lower': (.14, .44), 'leg_R_lower': (.16, .46),
          'leg_L_upper': (.2, .52), 'leg_R_upper': (.22, .54), 'pelvis': (.24, .58), 'waist': (.28, .62),
          'chest': (.3, .7), 'head': (.36, .9), 'arm_L_upper': (.3, .66), 'arm_R_upper': (.32, .68),
          'arm_L_lower': (.28, .62), 'arm_R_lower': (.3, .64), 'arm_L_end': (.26, .6), 'arm_R_end': (.28, .62),
          'weapon': (.06, .5), 'cape': (.34, .82)}
_RUBBLE = None


def pose(name, t):
    global _RUBBLE
    phase = math.tau*t
    if name == 'idle':
        # Weightless hover: a slow bob, the cloak drifting and the head watching calmly.
        lift = HOVER+.9*math.sin(phase)
        world = body({'head': Q(0, 1.5*math.cos(phase), 4*math.sin(phase)), 'chest': Q(0, 0, 1.5*math.sin(phase))}, {}, lift,
                     sway=(0, 3*math.sin(phase+1), 0))
        K.grip_hands(kit, world, add(GRIP_R, (0, 0, lift-HOVER)), IDENT, haft=HAFT)
        dangle(world, lift, pitch=(18+4*math.sin(phase), 18-4*math.sin(phase)))
    elif name == 'glide':
        lift = HOVER+.6*math.sin(2*phase)
        world = body({'pelvis': Q(0, 6, 0), 'chest': Q(0, 4, 0), 'head': Q(0, -8, 0)}, {'pelvis': (1.0, 0, 0)}, lift,
                     cape=.95, sway=(0, 10+3*math.sin(2*phase), 0))
        K.grip_hands(kit, world, add(GRIP_R, (1.5, 0, lift-HOVER)), axe(unit((.2, .7, .68)), BLADE), haft=HAFT, reach=.995)
        dangle(world, lift+1.0, dx=(-2.5+1.2*math.sin(phase), -3.5-1.2*math.sin(phase)), pitch=(34, 30))
    elif name == 'reap':
        # Raised high over the right shoulder (t~.25); on the middle frame a great
        # diagonal reaping cut finishes low and wide on the spirit's left, body swept
        # forward and twisted, cloak streaming back.
        up = window(t, .04, .26)*(1-window(t, .34, .47))
        cut = window(t, .34, .47)*(1-window(t, .7, 1.0))
        lift = HOVER-3*cut
        world = body({'pelvis': Q(0, 8*cut, -10*up+12*cut), 'waist': Q(0, -4*up+8*cut, -10*up+14*cut),
                      'chest': Q(0, -6*up+14*cut, -14*up+22*cut), 'head': Q(0, 4*up-12*cut, 8*up-14*cut)},
                     {'pelvis': (-1.5*up+3*cut, 0, -1.5*cut)}, lift, cape=.9, sway=(0, 18*cut, 10*cut))
        raised = axe(unit((-.35, -.55, .76)), unit((-.2, .7, .3)))
        low = axe(unit((.55, .6, -.58)), unit((-.2, .3, .9)))
        grip = add(lerp(lerp(GRIP_R, (0.0, -12.0, 52.0), up), (2.0, 0.0, 31.0), cut), (-8*4*cut*(1-cut), 0, 0))
        q = K.slerp(K.slerp(IDENT, raised, up), low, cut)
        K.grip_hands(kit, world, grip, q, haft=HAFT, reach=.999, slide={'L': 4*up}, bends={'R': (-.4, -1, -.2), 'L': (-.3, 1, -.5)})
        dangle(world, lift, dx=(4*cut, -5*cut), pitch=(18-10*cut, 30))
    elif name == 'jab':
        # Drawn back (t~.25); on the middle frame the spirit lunges and drives the axe's
        # top spike straight out ahead at chest height, haft level, arms extended.
        back = window(t, .04, .26)*(1-window(t, .33, .45))
        jab = window(t, .33, .45)*(1-window(t, .7, 1.0))
        lift = HOVER+1*back-1.5*jab
        world = body({'pelvis': Q(0, 6*jab, 6*back), 'chest': Q(0, -4*back+10*jab, 10*back-6*jab), 'head': Q(0, 3*back-8*jab, -4*back)},
                     {'pelvis': (-2.5*back+4*jab, 0, 0)}, lift, cape=.9, sway=(0, 14*jab, 0))
        drawn = axe(unit((.35, .35, .87)), BLADE)
        level = axe(unit((1, .05, .02)), (0, 0, -1))
        grip = lerp(lerp(GRIP_R, (-2.0, -7.0, 38.0), back), (-5.0, -4.0, 42.0), jab)
        q = K.slerp(K.slerp(IDENT, drawn, back), level, jab)
        K.grip_hands(kit, world, grip, q, haft=HAFT, reach=.999, slide={'R': -2*jab, 'L': 3*jab},
                     bends={'R': (-.3, -1, -.4), 'L': (-.2, 1, -.6)})
        dangle(world, lift, dx=(3*jab, -4*jab), pitch=(14, 34))
    elif name == 'recoil':
        k = math.sin(math.pi*t)**2
        lift = HOVER+1.5*k
        world = body({'waist': Q(3*k, -5*k, 0), 'chest': Q(3*k, -10*k, -6*k), 'head': Q(-6*k, -14*k, 8*k)},
                     {'pelvis': (-2.5*k, 0, 0)}, lift, sway=(0, -8*k, 0))
        K.grip_hands(kit, world, add(GRIP_R, (-2.5*k, 0, lift-HOVER+1.0*k)), axe(unit(lerp(HAFT, (-.2, .6, .78), k)), BLADE),
                     haft=HAFT, reach=.995)
        dangle(world, lift, pitch=(18+10*k, 18+10*k))
    elif name == 'fade':
        # The light gives out: the empty armour sags, then clatters to the floor as a pile.
        if _RUBBLE is None: _RUBBLE = kit.rubble(authoring_parts(), RUBBLE, STACK)
        s = window(t, 0, .3)
        start = body({'chest': Q(0, 18*s, 0), 'head': Q(0, 24*s, 0), 'waist': Q(0, 8*s, 0)}, {'pelvis': (-1*s, 0, 0)}, HOVER-2*s)
        K.grip_hands(kit, start, add(GRIP_R, (2*s, 0, -2*s)), axe(unit(lerp(HAFT, (.3, .3, .9), s)), BLADE), haft=HAFT, reach=.99)
        dangle(start, HOVER-2*s, pitch=(18, 18))
        world = kit.collapse(start, _RUBBLE, t, TIMING, arcs={'weapon': 5.0, 'head': 3.0})
    return kit.frame_from_world(world)


def geometry():
    parts = build_parts(); K.layout_islands(parts)
    return assemble(parts, weights)


def matrices(frame): return kit.RIG.matrices(frame)
def deform(v, w, frame): return kit.RIG.deform(v, w, frame)
def animation_data(v, w): return sample_clips(kit.RIG, CLIPS, pose, v, w)


def build():
    from . import guardian_spirit_materials as M
    parts, v, n, uv, tr, w = geometry()
    image, spec = M.paint(parts)
    return K.export(__import__(__name__, fromlist=['x']), 'BRG-M59', 'guardian_spirit', LABEL, parts, v, n, uv, tr, w, image, spec,
                    dict(emissive=dict(shader='shaders/guardian-spirit-glow.fp', renderStyle='Add')), maps=False)


if __name__ == '__main__':
    import importlib
    print(importlib.import_module('tools.monster_models.guardian_spirit_animation').build()['sha256'])

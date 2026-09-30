"""Original winged guardian (Brogue MK_WINGED_GUARDIAN): a pale marble statue of
a sword-wielding armoured angel with carved stone wings, from the stone
guardian's lineage (shared knight kit).

Presentation only. Brogue CE owns the guardian's blinking relocation,
invulnerability, reflection, negation death, glyph machinery, timing and every
strike; the clips only illustrate those outcomes. No flight, glow or collision.
"""
import math
from . import guardian_kit as K
from .guardian_kit import Q, add, sub, mul, unit, lerp, smooth, window, frame_rotation, carved_block, stone_core, euler, along, IDENT
from .skeletal import assemble, sample_clips, rotate, qmul

SKIN = 'graphics/BRGWGRD.png'
MODEL = 'mod/BrogueDoom/models/monsters/58_winged_guardian.iqm'
LABEL = 'winged_guardian'
SCALE = .9
BLADE_DIR = unit((.36, -.36, .86))     # rest sword axis, grip toward tip
BLADE_POLE = (0, 1, 0)
GRIP_R = (10.0, -3.0, 39.0)
GRIP_L = K.r6(sub(GRIP_R, mul(BLADE_DIR, 4.3)))
# The leading edge is a quadratic arc: shoulder -> apex over the head line (control point) -> wrist.
WING = {'root': (-6.5, 5.0, 53.0), 'ctrl': (-10.0, 10.0, 94.0), 'wrist': (-12.0, 24.0, 66.0), 'tip': (-15.0, 28.5, 44.0),
        'inner': (-9.0, 13.0, 47.0), 'fan': (-12.5, 22.0, 50.0)}
FEATHERS = 8
# Feather groups on separate bones so the primaries can fan: 0-2 tip, 3-4 mid, 5-7 hand.
def feather_bone(i): return 'tip' if i < 3 else 'mid' if i < 5 else 'hand'


def _wing_specs():
    out = []
    for side, s in (('L', 1), ('R', -1)):
        r, w = WING['root'], WING['wrist']
        out += [(f'wing_{side}_arm', 'chest', (r[0], s*r[1], r[2])), (f'wing_{side}_hand', f'wing_{side}_arm', (w[0], s*w[1], w[2])),
                (f'wing_{side}_mid', f'wing_{side}_hand', (w[0], s*w[1], w[2])),
                (f'wing_{side}_tip', f'wing_{side}_hand', (w[0], s*w[1], w[2]))]
    return out


kit = K.Kit(K.knight_specs(GRIP_R, GRIP_L, extra=_wing_specs(), cape=False), SCALE)
BONES, REST, IDS = kit.BONES, kit.REST, kit.IDS
CLIPS = [('idle', 48, 16, True), ('stride', 36, 30, True), ('thrust', 19, 30, False),
         ('slash', 19, 30, False), ('recoil', 15, 30, False), ('crumble', 45, 30, False)]


def sword_parts():
    parts = []; g = GRIP_R; S = BLADE_DIR; P = BLADE_POLE
    def at(d): return add(g, mul(S, d))
    def B(*a, **k): k.setdefault('rough', .1); k.setdefault('hewn', .02); parts.append(carved_block(*a, **k)); return parts[-1]
    rot = along(at(0), at(1), (1, 0, 0))  # local z along blade; x = flat normal, y = blade width
    B('sword_grip', 'weapon', at(-3.2), (.95, .95, 5.4), rot=rot, bevel=.8, seed=401, chip=.2, pillow=0)
    B('sword_pommel', 'weapon', at(-9.3), (1.6, 1.6, 1.3), rot=rot, bevel=1.1, seed=402, chip=.3)
    B('sword_guard', 'weapon', at(3.2), (1.3, 6.4, 1.0), rot=rot, bevel=.8, seed=403, chip=.3,
      shape=lambda v: (v[0], v[1], v[2]+.5*(v[1]/6.4)**2))
    B('sword_blade', 'weapon', at(18.6), (.55, 1.55, 15.0), rot=rot, bevel=.45, seed=404, chip=.35, pillow=0,
      shape=lambda v: (v[0]*(1-.5*max(0, (v[2]-9)/6)), v[1]*(1-.9*max(0, (v[2]-9)/6)**1.3), v[2]))
    B('sword_fuller', 'weapon', at(13.0), (.62, .35, 8.5), rot=rot, bevel=.3, seed=405, chip=0, pillow=0, role='void')
    return parts


def _side(pt, s): return (pt[0], s*pt[1], pt[2])


def edge_point(side_sign, t):
    """Point on the wing's leading-edge arc (authoring units)."""
    p0, c, p1 = (_side(WING[k], side_sign) for k in ('root', 'ctrl', 'wrist'))
    return tuple((1-t)**2*p0[i]+2*t*(1-t)*c[i]+t*t*p1[i] for i in range(3))


# Covert rows over the arm and secondaries under them: (count, length, half width, inset from the edge, x offset).
COVERT_ROWS = ((11, 8.5, 2.5, 0.0, -1.5), (10, 13.0, 2.7, 2.5, -.75), (9, 18.0, 2.9, 5.0, 0.0))


def wing_parts():
    parts = []
    def B(*a, **k): parts.append(carved_block(*a, **k)); return parts[-1]
    for side, s in (('L', 1), ('R', -1)):
        k = 500 if side == 'L' else 700
        wrist, tip, inner, fan = (_side(WING[n], s) for n in ('wrist', 'tip', 'inner', 'fan'))
        pole = (-1, -s*.25, 0)
        # Overlapping scalloped covert rows cover the whole arm, so the leading edge is a feathered curve.
        for row, (count, length, half_w, inset, xoff) in enumerate(COVERT_ROWS):
            for i in range(count):
                t = .03+.95*(i+.5*(row % 2))/count
                t = min(t, .99)
                base = edge_point(s, t)
                d = unit(sub(fan, base)); base = add(base, mul(d, inset)); base = add(base, (xoff, 0, 0))
                end = add(base, mul(d, length)); h = length/2
                bone = f'wing_{side}_arm' if t < .55 else f'wing_{side}_hand'
                B(f'wing_covert_{side}_r{row}_{i}', bone, lerp(base, end, .5), (.8+.05*row, half_w, h), rot=along(base, end, pole),
                  bevel=.7, seed=k+row*20+i, pillow=.3, chip=.4, rough=.1,
                  shape=lambda v, h=h: (v[0]+.6*max(0, v[2]/h)**2, v[1]*(1-.6*max(0, v[2]/h)**2.2), v[2]))
        # Long flight feathers fan from the wrist and the lower leading edge: primaries (tip bone),
        # secondaries (mid bone) and inner feathers (hand bone).
        for i in range(FEATHERS):
            t = i/(FEATHERS-1)
            start = edge_point(s, 1-.42*t)
            end = lerp(tip, inner, t); end = add(end, (.45*(i % 2), 0, 3.0*math.sin(math.pi*t)))
            start = add(start, (.45*(i % 2)+.9, 0, 0))
            L = math.dist(start, end)/2
            B(f'wing_feather_{side}_{i}', f'wing_{side}_{feather_bone(i)}', lerp(start, end, .5), (.9-.1*t, 2.9-.3*t, L), rot=along(start, end, pole),
              bevel=.7, seed=k+400+i, pillow=.3, chip=.4, rough=.1,
              shape=lambda v, L=L: (v[0], v[1]*(1-.5*max(0, v[2]/L)**2), v[2]+.7*(v[1]/2.9)*(1 if v[2] > 0 else 0)))
    return parts


def angel_head():
    parts = []
    def B(*a, **k): parts.append(carved_block(*a, **k)); return parts[-1]
    # A large serene face: brow, nose, lips, chin and lidded eyes on a tapering mask.
    B('face_mass', 'head', (2.8, 0, 62.2), (3.7, 3.9, 4.8), bevel=3.6, seed=610, pillow=.2, chip=.1, hewn=.02,
      shape=lambda v: (v[0]+.5*(v[2] < -2)*(-.1*v[2]), v[1]*(1-.32*max(0, -v[2]/4.8)), v[2]))
    B('face_brow', 'head', (5.9, 0, 64.6), (.8, 3.5, .55), rot=euler(0, 8, 0), bevel=.55, seed=611, chip=.1, hewn=0,
      shape=lambda v: (v[0]-.14*v[1]*v[1]/4.2, v[1], v[2]+.45*(v[1]/4.2)**2))
    B('face_nose', 'head', (6.6, 0, 62.4), (1.0, .8, 2.2), rot=euler(0, 12, 0), bevel=.55, seed=612, chip=.1, hewn=0,
      shape=lambda v: (v[0], v[1]*(.5+.5*(v[2]+2.2)/4.4), v[2]))
    B('face_lip_upper', 'head', (6.0, 0, 59.7), (.75, 2.0, .42), bevel=.4, seed=618, chip=0, hewn=0, pillow=.4,
      shape=lambda v: (v[0], v[1], v[2]-.25*(v[1]/2.0)**2))
    B('face_lip_lower', 'head', (5.8, 0, 58.7), (.75, 1.7, .5), bevel=.45, seed=619, chip=0, hewn=0, pillow=.4)
    B('face_chin', 'head', (5.0, 0, 57.4), (1.5, 1.9, 1.1), bevel=.8, seed=613, chip=.1, hewn=0)
    for s in (1, -1):
        B(f'face_eye_{s}', 'head', (6.1, s*2.2, 63.2), (.6, 1.25, .62), bevel=.45, seed=614+s, chip=0, role='void', pillow=0, hewn=0)
        B(f'face_lid_{s}', 'head', (6.2, s*2.2, 64.0), (.75, 1.5, .32), bevel=.3, seed=620+s, chip=0, hewn=0, pillow=.3)
        B(f'face_cheek_{s}', 'head', (4.2, s*4.1, 60.8), (1.9, .9, 2.3), rot=euler(0, 0, s*-12), bevel=.8, seed=622+s, chip=.1, pillow=.4)
    # Hair: a crown base swept back, framed by long carved locks down both sides and the back.
    B('hair_crown', 'head', (-1.8, 0, 66.4), (5.0, 5.2, 3.2), bevel=3.1, seed=601, pillow=.25, rough=.3,
      shape=lambda v: (v[0], v[1], v[2]))
    for s in (1, -1):
        for j, (y, x0, z0) in enumerate(((2.6, 3.4, 67.2), (4.2, 1.8, 66.6), (5.2, -.6, 65.4))):
            a = (x0, s*y, z0); e = (.6-.8*j, s*(8.6+1.4*j), 54.6-1.6*j)
            L = math.dist(a, e)/2
            B(f'hair_lock_{"LR"[s < 0]}{j}', 'head', lerp(a, e, .5), (1.3, 2.1-.25*j, L), rot=along(a, e, (1, 0, 0)), bevel=.8, seed=630+3*j+(s > 0),
              pillow=.35, rough=.3, chip=.3,
              shape=lambda v, L=L: (v[0]+.6*math.sin(v[2]*.9), v[1]*(1-.45*max(0, v[2]/L)**2), v[2]))
    for j, y in enumerate((-4.4, -1.5, 1.5, 4.4)):
        a = (-4.6, y, 67.0); e = (-8.0, y*1.15, 55.6-.6*(j % 2))
        L = math.dist(a, e)/2
        B(f'hair_back_{j}', 'head', lerp(a, e, .5), (1.2, 1.7, L), rot=along(a, e, (0, 1, 0)), bevel=.8, seed=650+j, pillow=.35, rough=.3,
          shape=lambda v, L=L: (v[0], v[1]*(1-.4*max(0, v[2]/L)**2), v[2]+.5*math.sin(v[1]*1.4)))
    B('circlet', 'head', (-.3, 0, 67.3), (5.7, 5.7, .55), bevel=.4, seed=617, pillow=.05, chip=.2,
      shape=lambda v: (v[0], v[1], v[2]-.04*v[0]*v[0]/5.7*(v[0] > 0)))
    return parts


def robe_parts():
    parts = []
    def B(*a, **k): parts.append(carved_block(*a, **k)); return parts[-1]
    for side, s in (('L', 1), ('R', -1)):
        hp, kn = kit.rest(f'leg_{side}_upper'), kit.rest(f'leg_{side}_lower')
        # Robe panels ride each thigh, so a stride parts the skirt instead of cutting it.
        B(f'robe_front_{side}', f'leg_{side}_upper', (4.8, s*5.2, 21.0), (1.1, 4.4, 10.5), rot=euler(s*-5, -8, 0),
          bevel=.9, seed=620+s, pillow=.2, hewn=.1, shape=lambda v: (v[0], v[1]*(1+.22*max(0, -v[2]/10.5)), v[2]))
        B(f'robe_side_{side}', f'leg_{side}_upper', (-.6, s*10.4, 21.2), (4.8, 1.1, 10.3), rot=euler(s*9, 0, 0),
          bevel=.9, seed=623+s, pillow=.2, hewn=.1, shape=lambda v: (v[0]*(1+.22*max(0, -v[2]/10.3)), v[1], v[2]))
    B('robe_back', 'pelvis', (-6.2, 0, 21.2), (1.2, 9.2, 10.6), rot=euler(0, 7, 0), bevel=.9, seed=626, pillow=.2, hewn=.1,
      shape=lambda v: (v[0], v[1]*(1+.2*max(0, -v[2]/10.6)), v[2]))
    return parts


def authoring_parts():
    parts = K.knight_parts(kit, head='none', cape=False, tassets=False, pauldron=.72) + angel_head() + robe_parts() + wing_parts() + sword_parts()
    for p in parts: assert min(q[2] for q in p.vertices) > .2, p.name
    return parts


def build_parts():
    parts = authoring_parts()
    for p in parts:
        p.vertices = [mul(q, SCALE) for q in p.vertices]
        c, cols, half = p.box; p.box = (mul(c, SCALE), cols, mul(half, SCALE))
    return parts


def weights(part, v, uv): return [(IDS[part.bone], 1)]


def sword(direction, pole): return frame_rotation(BLADE_DIR, BLADE_POLE, direction, pole)


FAN_DEG = 14.0


def wings(world, spread=0.0, mantle=0.0, flutter=0.0, sweep=0.0, fan=0.0):
    """Pose both wings: ``spread`` opens the V, ``mantle`` sweeps them forward, ``fan`` opens the primaries."""
    for side, s in (('L', 1), ('R', -1)):
        arm, hand = f'wing_{side}_arm', f'wing_{side}_hand'
        a0 = unit(sub(WING['wrist'], WING['root'])); h0 = unit(sub(WING['tip'], WING['wrist']))
        a0 = (a0[0], s*a0[1], a0[2]); h0 = (h0[0], s*h0[1], h0[2])
        a1 = unit(lerp(lerp(lerp(a0, (.0, s*.78, .63), spread), (.55, s*.55, .5), mantle), (-.6, s*.25, .6), sweep))
        h1 = unit(lerp(lerp(lerp(h0, (.05, s*.6, -.8), spread), (.75, s*.05, -.65), mantle), (-.5, s*.1, -.86), sweep))
        h1 = unit(add(h1, (0, s*.08*flutter, 0)))
        pole0 = (-1, 0, 0); pole1 = unit(lerp(lerp(pole0, (-1, 0, .1), spread), (-.3, -s*1, 0), mantle))
        kit.follow(world, arm, 'chest')
        cq = world[kit.IDS['chest']][1]
        # Wing directions are authored in the chest frame, so a lunge carries them.
        qa = qmul(cq, frame_rotation(a0, pole0, a1, pole1))
        root = world[kit.IDS[arm]][0]
        world[kit.IDS[arm]] = (root, qa)
        wrist = add(root, rotate(qa, sub(kit.rest(hand), kit.rest(arm))))
        qh = qmul(cq, frame_rotation(h0, pole0, h1, pole1))
        world[kit.IDS[hand]] = (wrist, qh)
        # Primaries and secondaries pivot about the wrist in the wing plane (outward is +y on the left).
        world[kit.IDS[f'wing_{side}_mid']] = (wrist, qmul(qh, Q(s*.5*fan*FAN_DEG, 0, 0)))
        world[kit.IDS[f'wing_{side}_tip']] = (wrist, qmul(qh, Q(s*fan*FAN_DEG, 0, 0)))


def pose_body(rot, shift):
    return kit.fk(kit.body_frame(rot, shift))


RUBBLE = {
    'leg_L_end': ((3, 9.5), Q(0, 0, 8)), 'leg_R_end': ((1.5, -10.5), Q(0, 0, -6)),
    'leg_L_lower': ((15, 12), Q(0, -90, -10)), 'leg_R_lower': ((13, -13.5), Q(0, -92, 12)),
    'leg_L_upper': ((3, 13), Q(6, -88, 14)), 'leg_R_upper': ((1, -14), Q(-6, -86, -9)),
    'pelvis': ((-2, 0), Q(0, -12, 4)), 'waist': ((8, 1), Q(4, -88, 6)),
    'chest': ((-14, 1), Q(0, -90, 3)), 'head': ((20, 4), Q(8, 94, 30)),
    'arm_L_upper': ((-7, 18), Q(0, -90, 0)), 'arm_R_upper': ((-8, -19), Q(0, -90, 0)),
    'arm_L_lower': ((7, 19), Q(0, -90, 4)), 'arm_R_lower': ((7, -20), Q(0, -88, -4)),
    'arm_L_end': ((22, 14), Q(0, -90, 8)), 'arm_R_end': ((21, -15), Q(0, -86, -6)),
    'weapon': ((-2, -12), Q(0, -90, 20)),
    'wing_L_arm': ((-15, 11), Q(0, 88, 20)), 'wing_R_arm': ((-15, -11), Q(0, 88, -20)),
    'wing_L_hand': ((-9, 17), Q(0, 90, -15)), 'wing_R_hand': ((-9, -17), Q(0, 90, 15)),
    'wing_L_mid': ((-11, 22), Q(0, 90, -10)), 'wing_R_mid': ((-11, -22), Q(0, 90, 10)),
    'wing_L_tip': ((-14, 18), Q(0, 90, -25)), 'wing_R_tip': ((-14, -18), Q(0, 90, 25)),
}
STACK = {'chest': 1.5, 'pelvis': 2.0}
TIMING = {'leg_L_end': (.1, .4), 'leg_R_end': (.1, .4), 'leg_L_lower': (.3, .66), 'leg_R_lower': (.28, .64),
          'leg_L_upper': (.3, .7), 'leg_R_upper': (.3, .7), 'pelvis': (.26, .72), 'waist': (.3, .76),
          'chest': (.36, .88), 'head': (.22, .64), 'arm_L_upper': (.4, .78), 'arm_R_upper': (.42, .8),
          'arm_L_lower': (.36, .74), 'arm_R_lower': (.38, .76), 'arm_L_end': (.34, .72), 'arm_R_end': (.36, .74),
          'weapon': (.08, .5), 'wing_L_arm': (.16, .6), 'wing_R_arm': (.2, .64), 'wing_L_hand': (.12, .56), 'wing_R_hand': (.16, .6),
          'wing_L_mid': (.12, .56), 'wing_R_mid': (.16, .6), 'wing_L_tip': (.12, .56), 'wing_R_tip': (.16, .6)}
_RUBBLE = None


def kneel(s):
    world = pose_body({'pelvis': Q(0, 8*s, 0), 'chest': Q(0, 14*s, 0), 'head': Q(0, 16*s, 0)}, {'pelvis': (-3*s, 0, -9*s)})
    K.grip_hands(kit, world, add(GRIP_R, (3*s, 0, -9*s)), sword(unit(lerp(BLADE_DIR, (.05, 0, 1), s)), BLADE_POLE), reach=.99,
                 haft=BLADE_DIR)
    wings(world, spread=.5*s)
    K.plant_legs(kit, world)
    return world


def pose(name, t):
    global _RUBBLE
    phase = math.tau*t
    if name == 'idle':
        # A vigilant marble angel: the head surveys the room, the wings barely settle.
        world = pose_body({'head': Q(0, 2*math.cos(phase), 6*math.sin(phase))}, {'pelvis': (0, .2*math.sin(phase), 0)})
        K.grip_hands(kit, world, GRIP_R, IDENT, haft=BLADE_DIR)
        wings(world, spread=.02+.02*math.sin(phase), fan=.1+.08*math.sin(phase))
        K.plant_legs(kit, world)
    elif name == 'stride':
        sway = math.sin(phase); bob = -.9*abs(math.cos(phase))
        world = pose_body({'pelvis': Q(-2*sway, 0, 3*math.cos(phase)), 'chest': Q(1.5*sway, 3, -4*math.cos(phase)),
                           'head': Q(-1*sway, -2, 3*math.cos(phase))}, {'pelvis': (0, 1.2*sway, bob)})
        K.grip_hands(kit, world, add(GRIP_R, (0, 0, bob)), sword(unit((.5, .05, .86)), BLADE_POLE), reach=.995, haft=BLADE_DIR)
        wings(world, spread=.04+.03*math.sin(2*phase), fan=.2+.15*math.sin(2*phase))
        feet = {}; fq = {}
        for side, off in (('L', 0), ('R', .5)):
            u = (t+off) % 1
            if u < .6: dx = 4.0-8.0*u/.6; lift = 0.0; pitch = 0.0
            else:
                k = (u-.6)/.4; dx = -4.0+8*smooth(k); lift = 3.4*math.sin(math.pi*k); pitch = -8*math.sin(math.pi*k)
            feet[side] = add(kit.rest(f'leg_{side}_end'), (dx, 0, lift)); fq[side] = Q(0, pitch, 0)
        K.plant_legs(kit, world, feet, foot_q=fq)
    elif name == 'thrust':
        # Draw back (t~.25) with wings half raised; the middle frame holds a deep
        # lunging stab driven forward and down while both wings flare into a wide V.
        back = window(t, .04, .26)*(1-window(t, .34, .46))
        hit = window(t, .34, .46)*(1-window(t, .7, 1.0))
        world = pose_body({'pelvis': Q(0, 6*hit, 0), 'waist': Q(0, -4*back+8*hit, 8*back), 'chest': Q(0, -6*back+12*hit, 12*back-4*hit),
                           'head': Q(0, 4*back-12*hit, -6*back)}, {'pelvis': (-2*back+2.5*hit, 0, -1*back-7*hit)})
        drawn = sword(unit((.9, .1, .43)), (0, 1, 0))
        stab = sword(unit((.72, -.1, -.69)), (0, 1, 0))
        grip = add(lerp(lerp(GRIP_R, (-1.0, -6.0, 44.0), back), (9.0, -2.0, 35.0), hit), (-12*4*hit*(1-hit), 0, 0))
        q = K.slerp(K.slerp(IDENT, drawn, back), stab, hit)
        K.grip_hands(kit, world, grip, q, reach=.999, haft=BLADE_DIR)
        wings(world, spread=-.35*hit, fan=.2*back+1.0*hit)
        K.plant_legs(kit, world, {'L': add(kit.rest('leg_L_end'), (8*hit, 1.5*hit, 0)),
                                  'R': add(kit.rest('leg_R_end'), (-6*hit, -2.5*hit, 0))},
                     foot_q={'L': Q(0, 0, 8*hit), 'R': Q(0, 0, -14*hit)})
    elif name == 'slash':
        # Raised high on the left (t~.25); the middle frame holds a low, wide cut
        # finished out to the right with the torso twisted and the wings mantled forward.
        up = window(t, .04, .26)*(1-window(t, .33, .46))
        cut = window(t, .33, .46)*(1-window(t, .7, 1.0))
        world = pose_body({'waist': Q(0, 0, 10*up-16*cut), 'chest': Q(0, -4*up+10*cut, 18*up-22*cut),
                           'head': Q(0, 0, -8*up+12*cut)}, {'pelvis': (0, 1*up-1*cut, -1*up-5*cut)})
        raised = sword(unit((-.2, .45, .87)), (-1, 0, 0))
        low = sword(unit((.55, -.8, -.22)), (0, 0, 1))
        grip = add(lerp(lerp(GRIP_R, (2.0, 7.0, 50.0), up), (10.0, -6.0, 32.0), cut), (-8*4*cut*(1-cut), 0, 0))
        q = K.slerp(K.slerp(IDENT, raised, up), low, cut)
        K.grip_hands(kit, world, grip, q, reach=.999, haft=BLADE_DIR)
        wings(world, spread=.1*up, sweep=.5*cut, fan=.15*up+.2*cut)
        K.plant_legs(kit, world, {'L': add(kit.rest('leg_L_end'), (2*cut, 3.5*cut, 0)),
                                  'R': add(kit.rest('leg_R_end'), (-1*cut, -3.5*cut, 0))},
                     foot_q={'L': Q(0, 0, 10*cut), 'R': Q(0, 0, -10*cut)})
    elif name == 'recoil':
        k = math.sin(math.pi*t)**2
        world = pose_body({'waist': Q(3*k, -5*k, 0), 'chest': Q(3*k, -9*k, -6*k), 'head': Q(-6*k, -14*k, 8*k)},
                          {'pelvis': (-2.0*k, 0, -1.2*k)})
        K.grip_hands(kit, world, add(GRIP_R, (-2.5*k, 0, 1.5*k)), sword(unit(lerp(BLADE_DIR, (.2, 0, 1), k)), BLADE_POLE),
                     reach=.995, haft=BLADE_DIR)
        wings(world, spread=.1, mantle=.35*k, fan=-.3*k)
        K.plant_legs(kit, world)
    elif name == 'crumble':
        if _RUBBLE is None: _RUBBLE = kit.rubble(authoring_parts(), RUBBLE, STACK)
        world = kit.collapse(kneel(window(t, 0, .34)), _RUBBLE, t, TIMING, arcs={'weapon': 6.0})
    return kit.frame_from_world(world)


def geometry():
    parts = build_parts(); K.layout_islands(parts)
    return assemble(parts, weights)


def matrices(frame): return kit.RIG.matrices(frame)
def deform(v, w, frame): return kit.RIG.deform(v, w, frame)
def animation_data(v, w): return sample_clips(kit.RIG, CLIPS, pose, v, w)


def build():
    from . import winged_guardian_materials as M
    parts, v, n, uv, tr, w = geometry()
    image, spec = M.paint(parts)
    return K.export(__import__(__name__, fromlist=['x']), 'BRG-M58', 'winged_guardian', LABEL, parts, v, n, uv, tr, w, image, spec)


if __name__ == '__main__':
    import importlib
    print(importlib.import_module('tools.monster_models.winged_guardian_animation').build()['sha256'])

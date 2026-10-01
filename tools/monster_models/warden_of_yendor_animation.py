"""Original Warden of Yendor (Brogue MK_WARDEN_OF_YENDOR): a towering, near-faceless
armoured hunter in a tattered violet mantle, lit from within by Yendorian
violet-magenta light.

Presentation only. Brogue CE owns everything the Warden does: its
invulnerability, its endless hunt, timing, damage, blood, light radius and every
strike outcome. These clips only illustrate those outcomes; nothing feeds back
to the simulation, and no rubble, cloak or light actor collides or blocks anything.

Built on the guardian family's rigid carved-plate kit (read-only import). The
light is thin fullbright plates on their own bones (sternum core with cracks,
a V visor slit, knuckle seams); the collapse sinks them into the armour so the
glow goes out with the death clip. The mantle is three ragged rigid panels.
"""
import math
from . import guardian_kit as K
from .guardian_kit import Q, add, sub, mul, unit, lerp, smooth, window, slerp, carved_block, stone_core, euler, along, IDENT
from .skeletal import assemble, sample_clips, rotate, qmul

SKIN = 'graphics/BRGWRDN.png'
MODEL = 'mod/BrogueDoom/models/monsters/60_warden_of_yendor.iqm'
LABEL = 'warden_of_yendor'
SHADER = 'shaders/warden-yendor-light.fp'
SCALE = .745
DZ = 6.0   # torso lift over the long legs

SHOULDER = (0.0, 16.0, 70.0)
ELBOW = (-1.5, 18.6, 55.5)
WRIST = (2.0, 18.6, 41.0)
HIP = (0.0, 7.0, 39.0)
KNEE = (2.5, 7.6, 21.5)
ANKLE = (0.0, 8.2, 5.5)
GLOW_CHEST = (13.0, 0.0, 58.0+DZ)
GLOW_HEAD = (7.2, 0.0, 70.5+DZ)
GLOW_ARM = (WRIST[0]+6.3, 18.6, WRIST[2]-6.2)
LIFT = {'pelvis', 'waist', 'chest', 'head', 'pauldron_L', 'pauldron_R', 'glow_chest', 'glow_head'}


STRIPS = [  # (y, x, upper length, lower length): eight tattered strips from shoulders and upper back
    (-24.0, -5.0, 15, 26), (-17.5, -11.0, 14, 33), (-11.0, -13.0, 14, 27), (-4.0, -14.4, 13, 32),
    (4.0, -13.0, 13, 28), (11.0, -14.4, 14, 34), (17.5, -11.6, 14, 26), (24.0, -5.0, 15, 32)]
STRIP_TOP = 71.0


def _strip_specs():
    out = []
    for i, (y, x, l1, l2) in enumerate(STRIPS):
        out += [(f'cloak_{i}_a', 'chest', (x, y, STRIP_TOP)), (f'cloak_{i}_b', f'cloak_{i}_a', (x, y, STRIP_TOP-l1))]
    return out


def specs():
    s = [('root', None, (0, 0, 0)), ('pelvis', 'root', (0, 0, 34+DZ)), ('waist', 'pelvis', (0, 0, 40+DZ)),
         ('chest', 'waist', (0, 0, 49+DZ)), ('head', 'chest', (1, 0, 66+DZ))]
    for side, sg in (('L', 1), ('R', -1)):
        s.append((f'pauldron_{side}', 'chest', (0, sg*15, 62+DZ)))
        s += [(f'arm_{side}_upper', 'chest', (SHOULDER[0], sg*SHOULDER[1], SHOULDER[2])),
              (f'arm_{side}_lower', f'arm_{side}_upper', (ELBOW[0], sg*ELBOW[1], ELBOW[2])),
              (f'arm_{side}_end', f'arm_{side}_lower', (WRIST[0], sg*WRIST[1], WRIST[2]))]
        s += [(f'leg_{side}_upper', 'pelvis', (HIP[0], sg*HIP[1], HIP[2])),
              (f'leg_{side}_lower', f'leg_{side}_upper', (KNEE[0], sg*KNEE[1], KNEE[2])),
              (f'leg_{side}_end', f'leg_{side}_lower', (ANKLE[0], sg*ANKLE[1], ANKLE[2]))]
    s += _strip_specs()
    s += [('glow_chest', 'chest', GLOW_CHEST), ('glow_head', 'head', GLOW_HEAD),
          ('glow_L', 'arm_L_end', GLOW_ARM), ('glow_R', 'arm_R_end', (GLOW_ARM[0], -GLOW_ARM[1], GLOW_ARM[2]))]
    return s


kit = K.Kit(specs(), SCALE)
BONES, REST, IDS = kit.BONES, kit.REST, kit.IDS
CLIPS = [('idle', 56, 16, True), ('stride', 44, 30, True), ('strike', 33, 30, False),
         ('sweep', 31, 30, False), ('recoil', 15, 30, False), ('collapse', 51, 30, False)]
# Glow bone -> (parent, local vector that buries the plate in its armour).
GLOWS = {'glow_chest': ('chest', (-4.0, 0, 0)), 'glow_head': ('head', (-3.8, 0, 0)),
         'glow_L': ('arm_L_end', (-2.8, 0, 0)), 'glow_R': ('arm_R_end', (-2.8, 0, 0))}


def authoring_parts():
    parts = []
    def B(*a, **k):
        k.setdefault('pillow', .06); k.setdefault('rough', .1); k.setdefault('chip', .7)
        half = a[3]
        k['bevel'] = k['bevel']*.55 if 'bevel' in k else min(half)*.2   # sharp plate edges, not soft stone
        parts.append(carved_block(*a, **k)); return parts[-1]
    def C(*a, **k):
        parts.append(stone_core(*a, **k)); return parts[-1]
    R = kit.rest
    # ---- pelvis: narrow hip block, belt with a sigil plate, long tassets
    B('hip_block', 'pelvis', (0, 0, 32.5), (6.0, 9.0, 3.6), bevel=2.4, seed=1)
    B('belt', 'pelvis', (.2, 0, 36.3), (6.6, 9.6, 1.4), bevel=1.0, seed=2, pillow=.15)
    B('belt_sigil', 'pelvis', (7.0, 0, 36.3), (.8, 2.2, 1.9), bevel=.6, seed=3, chip=.3, pillow=.3,
      shape=lambda v: (v[0]+.8*max(0, 1-abs(v[1])/2.2), v[1], v[2]))
    for s in (1, -1):
        B(f'tasset_front_{s}', 'pelvis', (7.2, s*4.6, 26.5), (1.3, 4.0, 8.2), rot=euler(s*-5, -9, s*8), bevel=1.1, seed=4+s, pillow=.3,
          shape=lambda v: (v[0]+.7*max(0, 1-abs(v[1])/4.0), v[1]*(1-.45*max(0, -v[2]/8.2)), v[2]))
        B(f'tasset_side_{s}', 'pelvis', (.4, s*9.6, 27.6), (4.4, 1.1, 7.2), rot=euler(s*12, 0, 0), bevel=1.0, seed=7+s, pillow=.3,
          shape=lambda v: (v[0]*(1-.4*max(0, -v[2]/7.2)), v[1], v[2]))
    B('tasset_rear', 'pelvis', (-6.8, 0, 27.4), (1.2, 7.4, 7.6), rot=euler(0, 12, 0), bevel=1.0, seed=10, pillow=.3,
      shape=lambda v: (v[0]-.04*v[1]**2, v[1]*(1-.4*max(0, -v[2]/7.6)), v[2]))
    # ---- waist: dark core under three overlapping curved fauld lames
    C('core_waist', 'waist', (0, 0, 40.5), 4.2, seed=11)
    for i, (z, hx, hy) in enumerate(((45.2, 5.2, 7.2), (42.2, 5.7, 8.0), (39.2, 6.2, 8.8))):
        B(f'fauld_{i}', 'waist', (.3+.3*i, 0, z), (hx, hy, 1.7), rot=euler(0, -3*i, 0), bevel=.9, seed=12+i, pillow=.05,
          shape=lambda v, hy=hy, hx=hx: (v[0]-.05*v[1]**2+1.0*max(0, 1-abs(v[1])/hy), v[1], v[2]-.03*v[1]**2))
    # ---- chest: V-tapered faceted cuirass. Two breast facets meet in a central ridge,
    # narrowing to a pointed plackart; every plate is angled or ridged.
    for s in (1, -1):
        anchor = -s*7.4
        B(f'breast_{s}', 'chest', (2.2, s*6.0, 55.6), (7.0, 7.4, 6.8), rot=euler(0, 0, s*18), bevel=2.0, seed=14+s, pillow=.05,
          shape=lambda v, anchor=anchor: (v[0], anchor+(v[1]-anchor)*(.55+.45*max(0.0, (v[2]/6.8+1)/2)), v[2]))
        B(f'plackart_{s}', 'chest', (5.4, s*2.4, 46.6), (4.6, 3.6, 5.8), rot=euler(0, 4, s*14), bevel=1.3, seed=16+s, pillow=.04,
          shape=lambda v, anchor=-s*3.6: (v[0], anchor+(v[1]-anchor)*(.12+.88*max(0.0, (v[2]/5.8+1)/2)), v[2]))
    B('gorget', 'chest', (.3, 0, 62.4), (5.6, 8.4, 2.0), bevel=1.2, seed=18, pillow=.1,
      shape=lambda v: (v[0]+1.2*max(0, 1-abs(v[1])/8.4), v[1], v[2]))
    B('collar_rear', 'chest', (-4.6, 0, 66.5), (1.7, 7.8, 6.2), rot=euler(0, -9, 0), bevel=1.0, seed=19, pillow=.3,
      shape=lambda v: (v[0], v[1]*(.8+.3*(v[2]/6.2+1)/2), v[2]))
    for i, z in enumerate((57.0, 51.4, 46.0)):
        B(f'backplate_{i}', 'chest', (-9.4, 0, z), (1.6, 8.6-1.6*i, 2.5), bevel=1.0, seed=20+i, pillow=.1,
          shape=lambda v: (v[0]-.035*v[1]**2-.8*max(0, 1-abs(v[1])/6.0), v[1], v[2]))
    B('spine_blade', 'chest', (-11.4, 0, 58.0), (1.1, .9, 7.0), bevel=.5, seed=23, chip=.3, pillow=0,
      shape=lambda v: (v[0], v[1], v[2]) if v[2] < 0 else (v[0]-.5*v[2], v[1]*(1-.55*v[2]/7.0), v[2]))
    # ---- head: tall tapering great-helm, blank tapered mask, swept-back crown of blades
    C('core_neck', 'head', (1, 0, 63.4), 3.1, seed=24)
    B('helm', 'head', (.8, 0, 70.4), (4.6, 4.2, 8.0), bevel=3.0, seed=25, pillow=.1,
      shape=lambda v: (v[0]*(1-.30*max(0.0, (v[2]/8.0+1)/2)**1.4), v[1]*(1-.36*max(0.0, (v[2]/8.0+1)/2)**1.4), v[2]))
    B('faceplate', 'head', (4.9, 0, 68.6), (1.5, 3.4, 6.8), rot=euler(0, -3, 0), bevel=.8, seed=26, chip=.3, pillow=.05, hewn=.03,
      shape=lambda v: (v[0], v[1]*(.62+.38*(v[2]+6.8)/13.6), v[2]))
    B('brow', 'head', (6.0, 0, 72.6), (1.3, 3.6, .8), rot=euler(0, 16, 0), bevel=.6, seed=27, chip=.2, pillow=.08)
    for s in (1, -1):
        B(f'cheek_{s}', 'head', (2.0, s*4.5, 67.0), (2.4, .8, 4.8), rot=euler(0, 0, s*-10), bevel=.8, seed=29+s, pillow=.2,
          shape=lambda v: (v[0], v[1], v[2]*(1 if v[2] > 0 else .9)))
    crown = [(0, 0.0, 4.8, 0), (1, 2.3, 4.0, 10), (-1, -2.3, 4.0, -10), (2, 4.0, 3.0, 18), (-2, -4.0, 3.0, -18)]
    for i, (idx, y, h, splay) in enumerate(crown):
        B(f'crest_{i}', 'head', (-1.6-abs(idx)*.7, y, 78.4+h/2-abs(idx)*.6), (2.0, .75, h/2+1.0), rot=euler(splay, -34+abs(idx)*4, 0),
          bevel=.35, seed=32+i, chip=.3, pillow=0,
          shape=lambda v, hh=h/2+1.0: (v[0]*(1-.7*max(0, v[2]/hh)), v[1]*(1-.7*max(0, v[2]/hh)), v[2]))
    # ---- shoulders: three curved, downward-overlapping lames per side, swept spikes
    for side, s in (('L', 1), ('R', -1)):
        k = 40 if side == 'L' else 70
        pb = f'pauldron_{side}'
        pv = (0, s*15.0, 62.0)     # authoring pivot for shrinking (pre-lift)
        mine = []
        for i, (yy, zz, hx, hy, tilt) in enumerate(((17.0, 66.0, 8.2, 7.0, -14), (19.4, 62.4, 7.6, 6.4, -25), (21.4, 59.0, 6.8, 5.6, -36))):
            mine.append(B(f'pauldron_lame_{i}_{side}', pb, (-.4, s*yy, zz), (hx, hy, 1.6), rot=euler(s*tilt, 0, 0), bevel=1.0, seed=k+i, pillow=.05,
                          shape=lambda v, hx=hx, hy=hy: (v[0], v[1]*(1-.25*max(0, abs(v[0])/hx)), v[2]+1.4*max(0, 1-abs(v[0])/hx)-.07*v[1]**2)))
        d = unit((-.62, s*.5, .55)); base = (-1.6, s*22.0, 65.5)
        mine.append(B(f'pauldron_spike_{side}', pb, add(base, mul(d, 6.0)), (1.5, 2.2, 6.0), rot=along((0, 0, 0), d, (0, s, 0)), bevel=.6, seed=k+3, chip=.4, pillow=0,
                      shape=lambda v: (v[0]*(1-.8*max(0, v[2]/6.0)), v[1]*(1-.8*max(0, v[2]/6.0)), v[2])))
        for p in mine:      # 20% smaller about the shoulder
            p.vertices = [add(pv, mul(sub(q, pv), .8)) for q in p.vertices]
            c, cols, half = p.box; p.box = (add(pv, mul(sub(c, pv), .8)), cols, mul(half, .8))
        sh, el, wr = (tuple(R(f'arm_{side}_{j}')) for j in ('upper', 'lower', 'end'))
        C(f'core_shoulder_{side}', f'arm_{side}_upper', add(sh, (0, 0, -1)), 3.8, seed=k+4)
        B(f'rerebrace_{side}', f'arm_{side}_upper', lerp(sh, el, .52), (4.0, 3.8, 6.8), rot=along(sh, el), seed=k+5,
          shape=lambda v: (v[0]*(1-.2*(v[2]/6.8+1)/2), v[1]*(1-.2*(v[2]/6.8+1)/2), v[2]))
        C(f'core_elbow_{side}', f'arm_{side}_lower', el, 3.4, seed=k+6)
        B(f'couter_{side}', f'arm_{side}_lower', add(el, (-3.2, 0, 0)), (2.0, 3.2, 3.0), rot=euler(0, 12, 0), bevel=1.0, seed=k+7, pillow=.3)
        B(f'couter_spike_{side}', f'arm_{side}_lower', add(el, (-6.6, 0, .4)), (2.8, 1.0, 1.0), rot=euler(0, 8, 0), bevel=.5, seed=k+8, chip=.3, pillow=0,
          shape=lambda v: (v[0], v[1]*(1-.8*max(0, -v[0]/2.8)), v[2]*(1-.8*max(0, -v[0]/2.8))))
        B(f'vambrace_{side}', f'arm_{side}_lower', lerp(el, wr, .48), (4.4, 4.2, 6.4), rot=along(el, wr), seed=k+9, pillow=.03,
          shape=lambda v: (v[0]*(1-.42*(v[2]/6.4+1)/2)+.9*max(0, 1-abs(v[1])/4.0)*(v[0] > 0), v[1]*(1-.42*(v[2]/6.4+1)/2), v[2]))
        B(f'cuff_{side}', f'arm_{side}_lower', lerp(el, wr, .9), (3.6, 3.4, 1.2), rot=along(el, wr), bevel=.8, seed=k+10, pillow=.1)
        # Taloned gauntlet: tapered back-of-hand plate, four articulated finger plates ending in claws, thumb claw.
        B(f'gauntlet_palm_{side}', f'arm_{side}_end', add(wr, (1.6, 0, -3.0)), (4.0, 4.6, 3.6), bevel=1.6, seed=k+11, chip=.8, pillow=.03,
          shape=lambda v: (v[0]*(1-.1*max(0, -v[2]/3.6)), v[1]*(1-.16*max(0, -v[2]/3.6)), v[2]))
        B(f'knuckle_guard_{side}', f'arm_{side}_end', add(wr, (4.6, 0, -6.2)), (1.3, 4.6, .9), rot=euler(0, -8, 0), bevel=.6, seed=k+12, pillow=.05,
          shape=lambda v: (v[0]+.6*max(0, 1-abs(v[1])/4.6), v[1], v[2]))
        for i, dy in enumerate((-3.3, -1.1, 1.1, 3.3)):
            B(f'finger_{side}_{i}', f'arm_{side}_end', add(wr, (4.0, dy, -8.8)), (1.3, .95, 2.5), rot=euler(0, -18, 0), bevel=.5, seed=k+13+i, chip=.3, pillow=.05)
            B(f'claw_{side}_{i}', f'arm_{side}_end', add(wr, (7.0, dy, -13.05)), (.95, .7, 2.9), rot=euler(0, -50, 0), bevel=.3, seed=k+17+i, chip=.2, pillow=0,
              shape=lambda v: (v[0]*(1-.9*max(0.0, (-v[2]/2.9+1)/2)**1.2), v[1]*(1-.9*max(0.0, (-v[2]/2.9+1)/2)**1.2), v[2]))
        B(f'thumb_{side}', f'arm_{side}_end', add(wr, (3.6, -s*4.8, -5.0)), (2.0, 1.0, 3.2), rot=euler(0, -28, 0), bevel=.4, seed=k+22, chip=.2, pillow=0,
          shape=lambda v: (v[0]*(1-.85*max(0.0, (-v[2]/3.2+1)/2)**1.2), v[1]*(1-.85*max(0.0, (-v[2]/3.2+1)/2)**1.2), v[2]))
    # ---- legs: long cuisse, spiked poleyn, greave and a broad sabaton
    for side, s in (('L', 1), ('R', -1)):
        k = 100 if side == 'L' else 130
        hp, kn, an = (tuple(R(f'leg_{side}_{j}')) for j in ('upper', 'lower', 'end'))
        C(f'core_hip_{side}', f'leg_{side}_upper', hp, 3.9, seed=k)
        B(f'cuisse_{side}', f'leg_{side}_upper', lerp(hp, kn, .48), (4.6, 4.4, 8.4), rot=along(hp, kn), seed=k+1, pillow=.03,
          shape=lambda v: (v[0]*(1-.14*v[2]/8.4)+.9*max(0, 1-abs(v[1])/4.4)*(v[0] > 0), v[1]*(1-.14*v[2]/8.4), v[2]))
        C(f'core_knee_{side}', f'leg_{side}_lower', kn, 3.5, seed=k+2)
        B(f'poleyn_{side}', f'leg_{side}_lower', add(kn, (4.0, 0, .3)), (2.2, 3.8, 3.4), rot=euler(0, -8, 0), bevel=1.2, seed=k+3, pillow=.1,
          shape=lambda v: (v[0]+1.2*max(0, 1-abs(v[1])/3.8), v[1], v[2]))
        B(f'poleyn_spike_{side}', f'leg_{side}_lower', add(kn, (7.2, 0, .6)), (1.9, 1.1, 1.1), bevel=.5, seed=k+4, chip=.3, pillow=0,
          shape=lambda v: (v[0], v[1]*(1-.8*max(0, v[0]/1.9)), v[2]*(1-.8*max(0, v[0]/1.9))))
        B(f'greave_{side}', f'leg_{side}_lower', lerp(kn, an, .5), (4.0, 3.9, 7.6), rot=along(kn, an), seed=k+5, pillow=.03,
          shape=lambda v: (v[0]*(1+.1*v[2]/7.6)+.9*max(0, 1-abs(v[1])/3.9)*(v[0] > 0), v[1]*(1+.1*v[2]/7.6), v[2]))
        C(f'core_ankle_{side}', f'leg_{side}_end', add(an, (0, 0, .3)), 2.9, seed=k+6)
        B(f'sabaton_{side}', f'leg_{side}_end', (3.2, s*8.2, 2.8), (7.0, 4.2, 2.2), bevel=1.4, seed=k+7, rough=.06, pillow=0, hewn=.03,
          shape=lambda v: (v[0], v[1]*(1-.2*max(0, v[0]/7.0)), v[2]-.4*max(0, v[0]/7.0)))
        B(f'sabaton_toe_{side}', f'leg_{side}_end', (10.6, s*8.2, 2.0), (2.6, 2.4, 1.4), bevel=.9, seed=k+8, rough=.05, pillow=0, hewn=.02,
          shape=lambda v: (v[0], v[1]*(1-.45*max(0, v[0]/2.6)), v[2]*(1-.3*max(0, v[0]/2.6))))
    # ---- mantle: eight long, narrow, tapering tattered strips, each a two-bone chain
    for i, (y, x, l1, l2) in enumerate(STRIPS):
        w = 3.7 if abs(y) < 20 else 3.2
        hz1, hz2 = l1/2, l2/2
        B(f'cloak_{i}_a', f'cloak_{i}_a', (x, y, STRIP_TOP-hz1), (.9, w, hz1), bevel=.5, seed=300+2*i, pillow=0, hewn=.08, chip=0, step=4.0,
          shape=lambda v, hz=hz1, i=i: (v[0]+.7*math.sin(v[2]*.3+i), v[1]*(1-.3*(hz-v[2])/(2*hz)), v[2]))
        B(f'cloak_{i}_b', f'cloak_{i}_b', (x, y, STRIP_TOP-l1-hz2), (.85, w*.92, hz2), bevel=.4, seed=301+2*i, pillow=0, hewn=.08, chip=0, step=3.0,
          shape=lambda v, hz=hz2, i=i: (v[0]*(1-.5*max(0.0, (hz-v[2])/(2*hz))), v[1]*(1-.94*max(0.0, (hz-v[2])/(2*hz))**1.25)+1.1*math.sin(v[2]*.45+i*1.7)*((hz-v[2])/(2*hz)), v[2]))
    # ---- Yendorian light: thin fullbright plates, each group on its own bone
    def G(name, bone, c, half, rot=None, shape=None, seed=0):
        p = carved_block(name, bone, c, half, rot=rot, bevel=min(half)*.6, seed=seed, chip=0, role='void', pillow=0, hewn=0, step=2.0, shape=shape)
        parts.append(p); return p
    # Sternum: a lozenge on the ridge and an asymmetric, forking fracture laid on the plate facets.
    G('glow_core', 'glow_chest', (11.9, .9, 57.4), (1.2, 1.4, 3.0), seed=200, shape=lambda v: (v[0], v[1]*(1-abs(v[2])/3.4), v[2]))

    def facet(s, centre, hx, phi_deg, ry_deg, hy):
        """Frame of a plate facet: (front point, normal, in-plane y, in-plane z, euler tail)."""
        ph = math.radians(phi_deg); ry = math.radians(ry_deg)
        n = (math.cos(ry)*math.cos(ph), math.cos(ry)*math.sin(ph), -math.sin(ry))
        ey = (-math.sin(ph), math.cos(ph), 0.0)
        ez = (math.sin(ry)*math.cos(ph), math.sin(ry)*math.sin(ph), math.cos(ry))
        return add(centre, mul(n, hx)), n, ey, ez, (ry_deg, phi_deg), hy

    def fracture(name, s, fr, segs, seed):
        """segs: (w outward from the ridge edge, v up the facet, angle deg in (w, v), length)."""
        p0, n, ey, ez, (ryd, phd), hy = fr
        for j, (w, v, ang, ln) in enumerate(segs):
            r = math.radians(ang); d = (math.cos(r), math.sin(r))
            u = -s*hy+s*(w+d[0]*ln/2); vv = v+d[1]*ln/2
            c = add(add(p0, mul(n, .3)), add(mul(ey, u), mul(ez, vv)))
            G(f'glow_{name}_{s}_{j}', 'glow_chest', c, (.42, ln/2, .3), rot=euler(math.degrees(math.atan2(d[1], s*d[0])), ryd, phd), seed=seed+j)

    def end(seg):
        w, v, ang, ln = seg; r = math.radians(ang); return (w+math.cos(r)*ln, v+math.sin(r)*ln)

    def chain(points, extra=.5):
        out = []
        for (w0, v0), (w1, v1) in zip(points, points[1:]):
            out.append((w0, v0, math.degrees(math.atan2(v1-v0, w1-w0)), math.hypot(w1-w0, v1-v0)+extra))
        return out
    # One continuous lightning-crack from the gorget down through the core to the plackart tip:
    # a zigzag on the +1 breast facet, then on down the +1 plackart facet, with two short
    # side branches that leave the line away from the core.
    upper = chain([(1.6, 6.4), (.9, 4.4), (1.9, 3.0), (.5, 1.8), (1.5, .2), (.7, -1.6), (1.6, -3.2)])
    fracture('fissure', 1, facet(1, (2.2, 6.0, 55.6), 7.0, 18, 0, 7.4), upper+[(.9, 4.4, 20, 2.4)], 210)
    lower = chain([(1.2, 5.0), (.8, 3.4), (1.5, 1.6), (.9, 0.0), (1.4, -1.6), (.8, -3.2), (.7, -4.8)])
    fracture('fissure_low', 1, facet(1, (5.4, 2.4, 46.6), 4.6, 14, 4, 3.6), lower+[(.9, 0.0, -28, 1.6)], 240)
    hx, hz = GLOW_HEAD[0], GLOW_HEAD[2]-DZ
    for sgn in (1, -1):
        G(f'glow_visor_{sgn}', 'glow_head', (hx, sgn*1.7, hz+.9), (.5, 2.2, .28), rot=euler(sgn*28, 0, 0), seed=220+(sgn > 0))
    for side, s in (('L', 1), ('R', -1)):
        wr = R(f'arm_{side}_end')
        # One thin seam across the knuckle guard (two halves following its ridge).
        for j, sg in enumerate((1, -1)):
            c = add(wr, (4.6+1.3*math.cos(math.radians(8))+.3+.25, sg*2.2, -6.2+1.3*math.sin(math.radians(8))+.05))
            G(f'glow_knuckle_{side}_{j}', f'glow_{side}', c, (.3, 2.3, .32), rot=euler(0, -8, sg*7.4), seed=230+j+(s > 0)*2)
    for p in parts:
        if p.bone in LIFT:
            p.vertices = [add(q, (0, 0, DZ)) for q in p.vertices]
            c, cols, half = p.box; p.box = (add(c, (0, 0, DZ)), cols, half)
        if p.bone in ('head', 'glow_head'):
            pivot = (1.0, 0.0, 66.0+DZ); grow = lambda q: add(add(pivot, mul(sub(q, pivot), 1.12)), (0, 0, 1.0))
            p.vertices = [grow(q) for q in p.vertices]
            c, cols, half = p.box; p.box = (grow(c), cols, mul(half, 1.12))
    for p in parts: assert min(q[2] for q in p.vertices) > .2, p.name
    return parts


def build_parts():
    parts = authoring_parts()
    for p in parts:
        p.vertices = [mul(q, SCALE) for q in p.vertices]
        c, cols, half = p.box; p.box = (mul(c, SCALE), cols, mul(half, SCALE))
    return parts


def weights(part, v, uv): return [(IDS[part.bone], 1)]


# ------------------------------------------------------------------ posing
def glow(world, out):
    """Seat each light group on its armour; ``out`` 0 burns, 1 is buried and dark."""
    for bone, (parent, back) in GLOWS.items():
        pl, pq = world[IDS[parent]]
        loc = add(pl, rotate(pq, add(sub(kit.rest(bone), kit.rest(parent)), mul(back, out))))
        world[IDS[bone]] = (loc, pq)


def cloak(world, amount=.7, sway=(0, 0, 0), spread=0.0, phase=0.0, wob=1.0):
    """Eight two-bone strips hang from the shoulders and upper back: mostly vertical, swung back by
    ``sway[1]`` degrees, flared outward by ``spread``, and each trailing with its own phase (``wob``)."""
    for i, (y, x, l1, l2) in enumerate(STRIPS):
        a_, b_ = f'cloak_{i}_a', f'cloak_{i}_b'
        ph = phase+.8*i; side = 1 if y > 0 else -1; wide = abs(y)/24.0
        kit.follow(world, a_, 'chest')
        loc, q = world[IDS[a_]]
        roll = sway[0]+side*spread*(.4+.6*wide)+wob*1.6*math.sin(ph+.5)
        pa = sway[1]+wob*3.0*math.sin(ph)
        world[IDS[a_]] = (loc, qmul(Q(roll, pa, sway[2]), slerp(q, IDENT, amount)))
        pb = .5*sway[1]+wob*5.0*math.sin(ph+1.3)+.35*spread
        kit.follow(world, b_, a_, q=Q(side*.5*spread+wob*2.0*math.sin(ph+2.0), pb, 0))


def pose_body(rot, shift):
    return kit.fk(kit.body_frame(rot, shift))


def legs(world, feet=None, foot_q=None):
    K.plant_legs(kit, world, feet, bend=(1, 0, 0), foot_q=foot_q)


def hang(world, side, offset=(0, 0, 0), bend=(-.85, .5, 0), end_q=None, reach=.985):
    """A free arm hangs from the chest like the rest pose, plus a world offset."""
    ch = world[IDS['chest']]; s = 1 if side == 'L' else -1
    target = add(ch[0], rotate(ch[1], sub(kit.rest(f'arm_{side}_end'), kit.rest('chest'))))
    kit.limb(world, f'arm_{side}', 'chest', add(target, offset), rotate(ch[1], (bend[0], s*bend[1], bend[2])), end_q, reach)


_RUBBLE = None
RUBBLE = {
    'leg_L_end': ((4, 13), Q(0, 0, 8)), 'leg_R_end': ((3, -13), Q(0, 0, -6)),
    'leg_L_lower': ((19, 17), Q(0, -90, -10)), 'leg_R_lower': ((16, -17), Q(0, -92, 12)),
    'leg_L_upper': ((6, 17), Q(20, -70, 14)), 'leg_R_upper': ((4, -17), Q(-6, -86, -9)),
    'pelvis': ((0, -1), Q(14, -22, 4)), 'waist': ((11, 3), Q(4, -88, 6)),
    'chest': ((-12, 3), Q(10, -82, 3)), 'head': ((24, -16), Q(84, 0, 28)),
    'pauldron_L': ((-18, 22), Q(-78, 12, 8)), 'pauldron_R': ((-19, -22), Q(60, -20, -6)),
    'arm_L_upper': ((-10, 25), Q(0, -90, 0)), 'arm_R_upper': ((-11, -25), Q(0, -90, 0)),
    'arm_L_lower': ((9, 25), Q(24, -78, 4)), 'arm_R_lower': ((8, -26), Q(0, -88, -4)),
    'arm_L_end': ((25, 22), Q(0, -90, 8)), 'arm_R_end': ((24, -23), Q(0, -86, -6)),
}
STACK = {'chest': 1.2, 'pelvis': 1.5, 'leg_L_upper': .5, 'leg_R_upper': .5, 'pauldron_L': 1.0, 'pauldron_R': 1.0}
TIMING = {'leg_L_end': (.1, .4), 'leg_R_end': (.1, .4), 'leg_L_lower': (.3, .66), 'leg_R_lower': (.28, .64),
          'leg_L_upper': (.3, .7), 'leg_R_upper': (.3, .7), 'pelvis': (.26, .72), 'waist': (.3, .76),
          'chest': (.3, .72), 'head': (.4, .9), 'pauldron_L': (.28, .66), 'pauldron_R': (.34, .72),
          'arm_L_upper': (.4, .78), 'arm_R_upper': (.42, .8), 'arm_L_lower': (.36, .74), 'arm_R_lower': (.38, .76),
          'arm_L_end': (.34, .72), 'arm_R_end': (.36, .74)}
for _i in range(len(STRIPS)):
    TIMING[f'cloak_{_i}_a'] = (.42, .92); TIMING[f'cloak_{_i}_b'] = (.5, 1.0)


def rubble_world():
    """Heap pose: a low, wide pile; the empty helm on its side on the floor beside it; the mantle strips
    draped across the pile and trailing out onto the floor."""
    parts = authoring_parts()
    layout = dict(RUBBLE); stack = dict(STACK)
    world = kit.rubble(parts, layout, stack)
    P = kit.pieces(parts)
    def top(bone):
        loc, q = world[IDS[bone]]
        return max(add(loc, rotate(q, sub(v, kit.rest(bone))))[2] for v in P[bone])
    heap = max(top(b) for b in ('chest', 'pelvis'))
    hc = (0.0, 0.0)
    for i, (y, x, l1, l2) in enumerate(STRIPS):
        side = 1 if y > 0 else -1
        phi = 180-(y/24.0)*50; curl = -side*30
        d = (math.cos(math.radians(phi)), math.sin(math.radians(phi)))
        db = (math.cos(math.radians(phi+curl)), math.sin(math.radians(phi+curl)))
        r0 = 4.0; end_a = (hc[0]+d[0]*(r0+l1), hc[1]+d[1]*(r0+l1))
        layout[f'cloak_{i}_a'] = ((hc[0]+d[0]*(r0+l1/2), hc[1]+d[1]*(r0+l1/2)), Q(0, -90, phi))
        layout[f'cloak_{i}_b'] = ((end_a[0]+db[0]*l2/2*.55, end_a[1]+db[1]*l2/2*.55), Q(0, -90, phi+curl))
        stack[f'cloak_{i}_a'] = heap*.55; stack[f'cloak_{i}_b'] = 0.0
    return kit.rubble(parts, layout, stack)


def kneel(s):
    """First stage of the collapse: the armour sags to its knees, arms slack."""
    world = pose_body({'pelvis': Q(0, 10*s, 0), 'chest': Q(0, 16*s, 0), 'head': Q(0, 18*s, 0)}, {'pelvis': (-3*s, 0, -9*s)})
    for side in 'LR': hang(world, side, (0, 0, -2*s))
    legs(world)
    cloak(world, .7, (0, 8*s, 0), 6*s, 0.0, 1.0)
    return world


def pose(name, t):
    global _RUBBLE
    phase = math.tau*t
    out = 0.0
    if name == 'idle':
        # Weight held, head turned by degrees; the light breathes (shader), the mantle stirs.
        world = pose_body({'waist': Q(.5*math.sin(phase), 0, 0), 'chest': Q(0, .8*math.sin(phase), 1.4*math.sin(phase)),
                           'head': Q(0, 1.2*math.cos(phase), 5*math.sin(phase))}, {'pelvis': (0, .5*math.sin(phase), 0)})
        for side, off in (('L', 0), ('R', 1)):
            hang(world, side, (.6*math.sin(phase+off), 0, .4*math.cos(phase)))
        legs(world)
        cloak(world, .78, (0, 3.0+2.0*math.sin(phase), 0), 2.0+1.5*math.sin(phase), phase, 1.0)
    elif name == 'stride':
        # A slow, inexorable stride: long planted steps, arms hanging heavy, mantle trailing.
        sway = math.sin(phase); bob = -1.0*abs(math.cos(phase))
        world = pose_body({'pelvis': Q(-2.5*sway, 0, 3.5*math.cos(phase)), 'chest': Q(2*sway, 3, -5*math.cos(phase)),
                           'head': Q(-1.5*sway, 0, 2.5*math.cos(phase))}, {'pelvis': (0, 1.5*sway, bob)})
        feet = {}; fq = {}
        for side, off in (('L', 0), ('R', .5)):
            u = (t+off) % 1
            if u < .6: dx = 5.0-10.0*u/.6; lift = 0.0; pitch = 0.0
            else:
                k = (u-.6)/.4; dx = -5.0+10*smooth(k); lift = 4.4*math.sin(math.pi*k); pitch = -9*math.sin(math.pi*k)
            feet[side] = add(kit.rest(f'leg_{side}_end'), (dx, 0, lift)); fq[side] = Q(0, pitch, 0)
            hang(world, side, (5.0*-math.cos(phase+off*math.tau), 0, 1.0*abs(math.cos(phase+off*math.tau))))
        legs(world, feet, fq)
        cloak(world, .62, (0, 9+3*math.sin(phase*2), 0), 5+2*math.sin(phase*2), phase*2, 1.6)
    elif name == 'strike':
        # Single-arm hammer-fist. The right gauntlet is hauled high behind the crest
        # (t~.25); the middle frame drives it forward and down at full extension in a
        # long lunge: torso twisted and pitched, left arm flung back, mantle swung out.
        up = window(t, .04, .26)*(1-window(t, .34, .47))
        hit = window(t, .34, .47)*(1-window(t, .68, 1.0))
        world = pose_body({'pelvis': Q(0, -3*up+12*hit, 6*up-8*hit), 'waist': Q(0, -5*up+12*hit, 8*up-10*hit),
                           'chest': Q(-4*up+6*hit, -10*up+22*hit, 12*up-14*hit), 'head': Q(0, -3*up-20*hit, -6*up+16*hit)},
                          {'pelvis': (-1.5*up+3.0*hit, 0, -.8*up-12.0*hit)})
        ch = world[IDS['chest']]
        hangp = add(ch[0], rotate(ch[1], sub(kit.rest('arm_R_end'), kit.rest('chest'))))
        target = lerp(lerp(hangp, (-6.0, -13.0, 96.0), up), (36.0, -30.0, 5.0), hit)
        bend = unit(lerp(lerp((-1, 0, 0), (-.3, -1, .4), up), (-.2, -.5, 1), hit))
        kit.limb(world, 'arm_R', 'chest', target, bend, None, .999 if hit > .5 else .995)
        hang(world, 'L', (-12*hit-3*up, 12*hit-2*up, 18*hit+2*up), bend=(-.4, .9, .3), reach=.999)
        legs(world, {'L': add(kit.rest('leg_L_end'), (12*hit, 3*hit, 0)), 'R': add(kit.rest('leg_R_end'), (-9*hit, -4*hit, 0))},
             {'L': Q(0, 0, -6*hit), 'R': Q(0, 0, -20*hit)})
        cloak(world, .72, (0, 24*hit-6*up, 0), 15*hit+4*up, 0.0, 2.0*hit+.3)
    elif name == 'sweep':
        # Backhand: right gauntlet cocked over the left shoulder, then swung wide to
        # the right at shoulder height; torso twisted, stance braced.
        wind = window(t, .04, .26)*(1-window(t, .33, .46))
        swing = window(t, .33, .46)*(1-window(t, .7, 1.0))
        world = pose_body({'waist': Q(0, 0, 10*wind-20*swing), 'chest': Q(-3*wind+3*swing, -5*wind+2*swing, 16*wind-28*swing),
                           'head': Q(0, -3*wind, -12*wind+20*swing)}, {'pelvis': (0, 1.2*wind-1.0*swing, -1.0*wind-4.0*swing)})
        ch = world[IDS['chest']]
        hangp = add(ch[0], rotate(ch[1], sub(kit.rest('arm_R_end'), kit.rest('chest'))))
        target = lerp(lerp(hangp, (6.0, 10.0, 84.0), wind), (19.0, -27.0, 68.0), swing)
        bend = unit(lerp(lerp((-1, 0, 0), (-.2, -1, .8), wind), (-.3, -.1, -1), swing))
        kit.limb(world, 'arm_R', 'chest', target, bend, None, .995)
        hang(world, 'L', (-9*swing-3*wind, -4*wind+1.5*swing, 3*wind+2*swing))
        legs(world, {'L': add(kit.rest('leg_L_end'), (1.5*swing, 3.5*swing, 0)), 'R': add(kit.rest('leg_R_end'), (-1.5*swing, -3.5*swing, 0))},
             {'L': Q(0, 0, 10*swing), 'R': Q(0, 0, -10*swing)})
        cloak(world, .7, (0, 10*swing, 0), 14*swing, 0.0, 1.0)
    elif name == 'recoil':
        k = math.sin(math.pi*t)**2
        world = pose_body({'waist': Q(3*k, -5*k, 0), 'chest': Q(3*k, -9*k, -6*k), 'head': Q(-6*k, -14*k, 8*k)}, {'pelvis': (-2.0*k, 0, -1.2*k)})
        for side, s in (('L', 1), ('R', -1)): hang(world, side, (-5.5*k, s*.8*k, 4.5*k))
        legs(world)
        cloak(world, .7, (0, 10*k, 0), 10*k, 0.0, 1.0)
    elif name == 'collapse':
        if _RUBBLE is None: _RUBBLE = rubble_world()
        world = kit.collapse(kneel(window(t, 0, .34)), _RUBBLE, t, TIMING)
        out = window(t, .30, .72)
    glow(world, out)
    return kit.frame_from_world(world)


# ------------------------------------------------------------------ export
def geometry():
    parts = build_parts(); K.layout_islands(parts)
    return assemble(parts, weights)


def matrices(frame): return kit.RIG.matrices(frame)
def deform(v, w, frame): return kit.RIG.deform(v, w, frame)
def animation_data(v, w): return sample_clips(kit.RIG, CLIPS, pose, v, w)


def build():
    from . import warden_of_yendor_materials as M
    parts, v, n, uv, tr, w = geometry()
    image, spec = M.paint(parts)
    return K.export(__import__(__name__, fromlist=['x']), 'BRG-M60', 'warden_of_yendor', LABEL, parts, v, n, uv, tr, w, image, spec, maps=False)


if __name__ == '__main__':
    import importlib
    print(importlib.import_module('tools.monster_models.warden_of_yendor_animation').build()['sha256'])

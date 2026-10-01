"""Shared presentation kit for the guardian family (stone guardian, winged
guardian, guardian spirit, sentinel).

Presentation only. Brogue CE owns every guardian rule: invulnerability,
moving only when the player moves, blinking, reflection, negation death,
spell casting, healing, timing, AI and RNG. Nothing here feeds data back.

The golem's stone kit is imported read-only (``carved_block``, ``stone_core``,
``layout_islands``, rotations, ``settle`` and the golem painter's pigment and
corner data). The golem's own posing helpers are bound to the golem rig, so
``Kit`` re-expresses the same world-space rigid posing for any rig here.
"""
import hashlib
import json
import math
from . import iqm, golem_materials as GM
from .golem_animation import (carved_block, stone_core, layout_islands, euler, along, frame_rotation,
                              matrix_quat, slerp, settle, Q, lerp, smooth, window, dot, value_noise)
from .rat import ROOT, add, sub, mul, unit, cross
from .skeletal import Rig, inverse, qmul, rotate, assemble, sample_clips

__all__ = ['carved_block', 'stone_core', 'layout_islands', 'euler', 'along', 'frame_rotation', 'matrix_quat',
           'slerp', 'settle', 'Q', 'lerp', 'smooth', 'window', 'dot', 'value_noise', 'Kit', 'paint', 'layout_regions',
           'tics', 'export', 'IDENT']

IDENT = (0.0, 0.0, 0.0, 1.0)
SIZE = GM.SIZE


def tics(frames, fps):
    """Engine tics at 35 Hz that play a whole clip."""
    return math.ceil(frames*35/fps)


def transformed(part, loc, q, pivot):
    """Rigidly move a part's vertices and box (for authoring props in a rest pose)."""
    part.vertices = [add(loc, rotate(q, sub(v, pivot))) for v in part.vertices]
    c, cols, half = part.box
    part.box = (add(loc, rotate(q, sub(c, pivot))), [rotate(q, e) for e in cols], half)
    return part


class Kit:
    """World-space rigid posing on an authoring rig, exported uniformly scaled."""

    def __init__(self, specs, scale):
        self.specs = specs; self.scale = scale
        self.A_RIG = Rig.from_world(specs); self.A_REST = self.A_RIG.rest
        self.RIG = Rig.from_world([(n, p, mul(v, scale)) for n, p, v in specs])
        self.BONES, self.REST = self.RIG.bones, self.RIG.rest
        self.IDS = {n: i for i, (n, p, v) in enumerate(self.BONES)}

    def rest(self, name): return tuple(self.A_REST[self.IDS[name]])

    def world_rest(self):
        return [(tuple(self.A_REST[i]), IDENT) for i in range(len(self.BONES))]

    def fk(self, frame): return [tuple(x) for x in self.A_RIG.matrices(frame)]

    def body_frame(self, rot=None, shift=None):
        rot = rot or {}; shift = shift or {}
        return [(*add(local, shift.get(n, (0, 0, 0))), *rot.get(n, IDENT), 1, 1, 1) for n, p, local in self.A_RIG.bones]

    def follow(self, world, child, parent, offset=(0, 0, 0), q=None):
        """Place ``child`` rigidly on ``parent`` as at rest, plus a world offset and extra local rotation."""
        pl, pq = world[self.IDS[parent]]
        loc = add(add(pl, rotate(pq, sub(self.rest(child), self.rest(parent)))), offset)
        world[self.IDS[child]] = (loc, qmul(pq, q) if q else pq)

    def frame_from_world(self, world):
        frame = []; s = self.scale
        for i, (name, parent, local) in enumerate(self.BONES):
            loc, q = world[i]; loc = mul(loc, s)
            if parent < 0: frame.append((*loc, *q, 1, 1, 1)); continue
            ploc, pq = world[parent]; ploc = mul(ploc, s); inv = inverse(pq)
            frame.append((*rotate(inv, sub(loc, ploc)), *qmul(inv, q), 1, 1, 1))
        return frame

    def two_bone(self, world, names, target, bend, end_q=None, reach=None):
        """Analytic IK in world space (same construction as the golem's)."""
        ids = [self.IDS[n] for n in names]; a0, b0, c0 = (self.A_REST[i] for i in ids)
        root = world[ids[0]][0]; a = math.dist(a0, b0); b = math.dist(b0, c0); d = math.dist(root, target)
        if reach is not None and d > reach*(a+b):
            target = add(root, mul(unit(sub(target, root)), reach*(a+b))); d = reach*(a+b)
        if reach is not None and d < abs(a-b)+.05*(a+b):
            target = add(root, mul(unit(sub(target, root)), abs(a-b)+.05*(a+b))); d = abs(a-b)+.05*(a+b)
        if not abs(a-b)+1e-6 < d < a+b-1e-6: raise ValueError(('unreachable limb', names, target, d, a+b))
        direction = unit(sub(target, root)); along_d = (a*a-b*b+d*d)/(2*d)
        n = unit(sub(bend, mul(direction, dot(bend, direction))))
        mid = add(root, add(mul(direction, along_d), mul(n, math.sqrt(max(0.0, a*a-along_d*along_d)))))
        rest_dir = unit(sub(c0, a0)); rest_bend = sub(b0, add(a0, mul(rest_dir, dot(sub(b0, a0), rest_dir))))
        qa = frame_rotation(sub(b0, a0), rest_bend, sub(mid, root), n)
        qb = frame_rotation(sub(c0, b0), rest_bend, sub(target, mid), n)
        world[ids[0]] = (root, qa); world[ids[1]] = (mid, qb)
        world[ids[2]] = (tuple(target), end_q if end_q is not None else qb)
        return tuple(target)

    def limb(self, world, prefix, parent, target, bend, end_q=None, reach=None, shoulder_offset=(0, 0, 0)):
        """Seat a limb root on its parent, then solve the limb to ``target``."""
        names = [f'{prefix}_{j}' for j in ('upper', 'lower', 'end')]
        self.follow(world, names[0], parent, shoulder_offset); world[self.IDS[names[0]]] = (world[self.IDS[names[0]]][0], IDENT)
        return self.two_bone(world, names, target, bend, end_q, reach)

    def pieces(self, parts):
        out = {}
        for p in parts: out.setdefault(p.bone, []).extend(p.vertices)
        return out

    def rubble(self, parts, layout, stack=None, floor=.35):
        """World pose laying every listed bone's rigid pieces on the floor."""
        world = self.world_rest(); P = self.pieces(parts); stack = stack or {}
        for name, (xy, q) in layout.items():
            i = self.IDS[name]
            world[i] = (tuple(settle(P.get(name, [self.A_REST[i]]), self.A_REST[i], q, xy, floor+stack.get(name, 0))), q)
        return world

    def collapse(self, start, end, t, timing, arc=1.5, arcs=None):
        """Blend each bone from ``start`` to ``end`` world pose with its own fall window."""
        world = [None]*len(self.BONES)
        for i, (bone, parent, local) in enumerate(self.BONES):
            a, b = timing.get(bone, (0, 1))
            u = max(0.0, min(1.0, (t-a)/(b-a))); fall = u*u; spin = smooth(u)
            (al, aq), (bl, bq) = start[i], end[i]
            loc = (al[0]+(bl[0]-al[0])*spin, al[1]+(bl[1]-al[1])*spin, al[2]+(bl[2]-al[2])*fall+(arcs or {}).get(bone, arc)*math.sin(math.pi*u))
            world[i] = (loc, slerp(aq, bq, spin))
        return world


# ------------------------------------------------------------------ layout
def layout_regions(groups, size=SIZE):
    """Pack each (parts, (x0, y0, square)) group into its own atlas square.

    Uses the golem's area-proportional packer, then offsets island pixels, so a
    shader can key an emissive region from texture coordinates alone.
    """
    for parts, (x0, y0, sq) in groups:
        layout_islands(parts, size=sq)
        for p in parts:
            new = []
            for u, v in p.uv:
                px = u*sq-.5; py = (1-v)*sq-.5
                new.append(((px+x0+.5)/size, 1-(py+y0+.5)/size))
            p.uv = new


# ------------------------------------------------------------------ paint
def paint(parts, pigment, background=(96, 94, 90), spec_bg=20):
    """Per-pixel painter over the golem's corner data with a creature pigment.

    ``pigment(np, P, L, N, E, CH, AO, pi)`` returns (rgb float array, spec float
    array) for the interpolated rest-space samples of part indices ``pi``.
    """
    import numpy as np
    part, V, Lc, Nc, Ec, Cc, AOc, UV = GM._corner_data(np, parts)
    image = np.zeros((SIZE, SIZE, 3), dtype=np.uint8); image[:] = background
    spec = np.zeros((SIZE, SIZE), dtype=np.uint8); spec[:] = spec_bg
    x0 = np.rint(UV[:, 0, 0]*SIZE-.5).astype(int); y0 = np.rint((1-UV[:, 0, 1])*SIZE-.5).astype(int)
    x1 = np.rint(UV[:, 2, 0]*SIZE-.5).astype(int); y1 = np.rint((1-UV[:, 2, 1])*SIZE-.5).astype(int)
    pad = 2; order = np.arange(len(part)); start = 0
    while start < len(order):
        chunk = order[start:start+1500]; start += len(chunk)
        idx = []; px = []; py = []
        for k in chunk:
            xs = np.arange(x0[k]-pad, x1[k]+pad+1); ys = np.arange(y0[k]-pad, y1[k]+pad+1)
            gx, gy = np.meshgrid(xs, ys); px.append(gx.ravel()); py.append(gy.ravel()); idx.append(np.full(gx.size, k))
        idx = np.concatenate(idx); px = np.concatenate(px); py = np.concatenate(py)
        keep = (px >= 0) & (py >= 0) & (px < SIZE) & (py < SIZE)
        idx, px, py = idx[keep], px[keep], py[keep]
        s = np.clip((px-x0[idx])/np.maximum(x1[idx]-x0[idx], 1), -.3, 1.3)
        t = np.clip((py-y0[idx])/np.maximum(y1[idx]-y0[idx], 1), -.3, 1.3)
        upper = s >= t
        w = np.stack([np.where(upper, 1-s, 1-t), np.where(upper, s-t, 0), np.where(upper, t, s), np.where(upper, 0, t-s)], 1)
        def interp(a): return np.einsum('nc,nc...->n...', w, a[idx])
        N = interp(Nc); N = N/np.maximum(np.linalg.norm(N, axis=1), 1e-9)[:, None]
        col, level = pigment(np, interp(V), interp(Lc), N, interp(Ec), interp(Cc), interp(AOc), part[idx])
        image[py, px] = np.clip(np.rint(col), 0, 255).astype(np.uint8)
        spec[py, px] = np.clip(np.rint(level), 0, 255).astype(np.uint8)
    return image, spec


def stone_pigment(parts, pal, feature=GM.feature_id, extra=None):
    """Golem stone pigment with this creature's palette and optional carved extras.

    ``extra(np, P, L, N, E, pi, col, spec)`` may modify colour/spec in place.
    """
    import numpy as np
    roles = np.array([GM.ROLE_IDS[p.role] if p.role in GM.ROLE_IDS else 0 for p in parts])
    seeds = np.array([p.seed for p in parts]); feats = np.array([feature(p.name) for p in parts])
    halves = np.array([p.box[2] for p in parts])

    def pigment(np, P, L, N, E, CH, AO, pi):
        col, crack, groove = GM.pigment(np, P, L, N, E, CH, AO, roles[pi], seeds[pi], feats[pi], halves[pi], pal)
        col = col.astype(np.float64)
        level = 24+34*np.clip(E, 0, 1)**1.5+22*np.clip(CH*2, 0, 1)-18*np.maximum(crack, groove)
        level = np.where(roles[pi] == 2, 4, np.where(roles[pi] == 1, 30, level))
        if extra: extra(np, P, L, N, E, AO, pi, col, level)
        return col, level
    return pigment


def flat_normal():
    return GM.encode_png(bytes((128, 128, 255))*16, 4, 4)


# ------------------------------------------------------------------ export
def export(module, work_id, slug, label, parts, v, n, uv, tr, w, image, spec, extra_manifest=None, maps=True):
    """Write IQM, diffuse, _N/_S maps and the creature manifest. Returns the manifest."""
    skin = GM.encode_png(image.tobytes(), SIZE, SIZE)
    (ROOT/'mod/BrogueDoom'/module.SKIN).write_bytes(skin)
    stem = module.SKIN[:-4]; supplemental = {}
    for name, data in ((stem+'_N.png', flat_normal()), (stem+'_S.png', GM.encode_png(spec.repeat(3).tobytes(), SIZE, SIZE))) if maps else ():
        (ROOT/'mod/BrogueDoom'/name).write_bytes(data); supplemental[name] = hashlib.sha256(data).hexdigest()
    clips, bounds = module.animation_data(v, w)
    data = iqm.encode(v, n, uv, tr, w, module.BONES, clips, bounds, mesh_label='Project_Broom_'+label, material_path=module.SKIN)
    path = ROOT/module.MODEL; path.write_bytes(data)
    manifest = dict(schemaVersion=1, workId=work_id, format='IQM v2', runtimeModel=path.relative_to(ROOT).as_posix(),
                    sha256=hashlib.sha256(data).hexdigest(), skin=module.SKIN, skinSha256=hashlib.sha256(skin).hexdigest(),
                    dimensions=[round(max(p[a] for p in v)-min(p[a] for p in v), 4) for a in range(3)],
                    supplementalMaps=supplemental, parts=len(parts), vertices=len(v), triangles=len(tr), boneCount=len(module.BONES),
                    bones=[dict(name=nm, parent=p, local=lv) for nm, p, lv in module.BONES],
                    clips=[{k: val for k, val in c.items() if k != 'frames'} | dict(frameCount=len(c['frames'])) for c in clips],
                    poseBounds=bounds, authoringSource=f'assets/monsters/{slug}/{slug.replace("_", "-")}-animated.blend')
    if extra_manifest: manifest.update(extra_manifest)
    out = ROOT/'assets/monsters'/slug; out.mkdir(exist_ok=True)
    (out/'animation.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


def runtime_bytes(module, parts, v, n, uv, tr, w, image, spec, maps=True):
    """Recompute every runtime file's bytes (tests compare with the exported files)."""
    clips, bounds = module.animation_data(v, w)
    stem = module.SKIN[:-4]
    out = {module.MODEL: iqm.encode(v, n, uv, tr, w, module.BONES, clips, bounds, mesh_label='Project_Broom_'+module.LABEL,
                                     material_path=module.SKIN),
            'mod/BrogueDoom/'+module.SKIN: GM.encode_png(image.tobytes(), SIZE, SIZE)}
    if maps:
        out['mod/BrogueDoom/'+stem+'_N.png'] = flat_normal()
        out['mod/BrogueDoom/'+stem+'_S.png'] = GM.encode_png(spec.repeat(3).tobytes(), SIZE, SIZE)
    return out


# ------------------------------------------------------------ knight body
def bend_joint(a, c, la, lb, bend):
    """Middle joint between ``a`` and ``c`` for segment lengths la/lb bent toward ``bend``."""
    d = math.dist(a, c); direction = unit(sub(c, a))
    x = (la*la-lb*lb+d*d)/(2*d); n = unit(sub(bend, mul(direction, dot(bend, direction))))
    return add(a, add(mul(direction, x), mul(n, math.sqrt(max(0.0, la*la-x*x)))))


def r6(p): return tuple(round(x, 6) for x in p)


SHOULDER = (0.0, 13.5, 55.0)


def knight_specs(grip_r, grip_l, extra=(), cape=True, arm=(12.8, 12.4), elbow_bend=(-.35, 1, -.25), wrist_back=3.0):
    """Knight skeleton whose rest pose already grips the weapon.

    ``grip_r``/``grip_l`` are the fist centres on the weapon at rest. Wrists sit
    ``wrist_back`` behind each fist toward the shoulder; elbows are solved for
    fixed segment lengths, so IK later reuses exactly these lengths.
    """
    specs = [('root', None, (0, 0, 0)), ('pelvis', 'root', (0, 0, 32)), ('waist', 'pelvis', (0, 0, 37)),
             ('chest', 'waist', (0, 0, 45)), ('head', 'chest', (1, 0, 59))]
    for side, s, grip in (('L', 1, grip_l), ('R', -1, grip_r)):
        sh = (SHOULDER[0], s*SHOULDER[1], SHOULDER[2])
        to = unit(sub(grip, sh)); wrist = sub(grip, mul(to, wrist_back))
        el = bend_joint(sh, wrist, arm[0], arm[1], (elbow_bend[0], s*elbow_bend[1], elbow_bend[2]))
        specs += [(f'arm_{side}_upper', 'chest', r6(sh)), (f'arm_{side}_lower', f'arm_{side}_upper', r6(el)),
                  (f'arm_{side}_end', f'arm_{side}_lower', r6(wrist))]
    for side, s in (('L', 1), ('R', -1)):
        specs += [(f'leg_{side}_upper', 'pelvis', (0, s*6.5, 31)), (f'leg_{side}_lower', f'leg_{side}_upper', (1.5, s*7, 17.5)),
                  (f'leg_{side}_end', f'leg_{side}_lower', (0, s*7.5, 5))]
    specs.append(('weapon', 'arm_R_end', r6(grip_r)))
    if cape: specs.append(('cape', 'chest', (-7.6, 0, 56.4)))
    specs += list(extra)
    return specs


def knight_parts(kit, head='bearded', legs='sabaton', cape=True, tassets=True, chip=1.0, rough=.22, hewn=.09, pillow=.14, pauldron=1.0):
    """Carved plate-armoured knight segments on ``kit``'s rest skeleton."""
    parts = []
    def B(*a, **k):
        k.setdefault('chip', chip); k.setdefault('rough', rough); k.setdefault('hewn', hewn); k.setdefault('pillow', pillow)
        parts.append(carved_block(*a, **k)); return parts[-1]
    def C(*a, **k): parts.append(stone_core(*a, **k)); return parts[-1]
    R = kit.rest
    # Pelvis: hip block, carved belt, armoured tassets and a front tabard.
    B('hip_block', 'pelvis', (0, 0, 30.2), (6.4, 9.6, 3.4), bevel=2.2, seed=101)
    B('belt', 'pelvis', (.2, 0, 33.6), (7.0, 10.3, 1.5), bevel=1.0, seed=102, pillow=.2)
    B('belt_buckle', 'pelvis', (7.4, 0, 33.6), (.9, 2.0, 1.9), bevel=.7, seed=103, chip=.3, pillow=.3)
    if tassets:
        for s in (1, -1):
            B(f'tasset_front_{s}', 'pelvis', (7.4, s*5.4, 26.4), (1.2, 4.2, 5.4), rot=euler(s*-6, -16, 0), bevel=1.0, seed=104+s, pillow=.4)
            B(f'tasset_side_{s}', 'pelvis', (.6, s*10.6, 26.8), (4.6, 1.2, 5.0), rot=euler(s*14, 0, 0), bevel=1.0, seed=107+s, pillow=.4)
        B('tasset_rear', 'pelvis', (-7.0, 0, 26.6), (1.2, 7.8, 5.2), rot=euler(0, 14, 0), bevel=1.0, seed=110, pillow=.4)
        B('tabard', 'pelvis', (8.3, 0, 21.0), (.8, 3.4, 8.4), rot=euler(0, -6, 0), bevel=.7, seed=111, pillow=.3,
          shape=lambda v: (v[0], v[1]*(1+.18*max(0, -v[2]/8.4)), v[2]))
    # Waist: two lames over a dark core.
    C('core_waist', 'waist', (0, 0, 38.0), 5.4, seed=112)
    B('lame_lower', 'waist', (.2, 0, 37.4), (6.3, 9.0, 2.0), bevel=1.3, seed=113)
    B('lame_upper', 'waist', (.5, 0, 41.2), (6.9, 10.0, 2.1), bevel=1.3, seed=114)
    # Chest: keeled breastplate that swells forward, gorget, backplate spine.
    def keel(v):
        x, y, z = v; t = (z/7.6+1)/2
        return (x+2.4*max(0, 1-abs(y)/12.5)**1.5*(.4+.6*t)*(x > 0), y*(.78+.22*t), z)
    B('breastplate', 'chest', (.4, 0, 50.0), (7.6, 12.6, 7.6), bevel=3.4, seed=115, shape=keel, hewn=.05)
    B('gorget', 'chest', (.4, 0, 57.2), (5.6, 7.4, 1.7), bevel=1.2, seed=116, pillow=.25)
    for i, z in enumerate((54, 48.5)):
        B(f'backplate_{i}', 'chest', (-7.8, 0, z), (1.4, 8.5-1.5*i, 2.4), bevel=1.0, seed=117+i, pillow=.35)
    if cape:
        B('cape', 'cape', (-10.2, 0, 34.0), (1.4, 12.6, 21.0), rot=euler(0, -7, 0), bevel=1.1, seed=119, pillow=.1, hewn=.12,
          shape=lambda v: (v[0]-2.4*max(0, -v[2]/21)**2+.8*math.sin(v[1]*.55), v[1]*(1+.26*max(0, -v[2]/21)), v[2]))
        B('cape_clasp', 'cape', (-6.4, 0, 56.4), (2.0, 11.0, 1.6), bevel=1.0, seed=120, pillow=.3)
    # Head.
    C('core_neck', 'head', (.6, 0, 58.6), 3.6, seed=121)
    if head == 'bearded':
        # Open kettle helm framing a stern carved face with a spade beard.
        B('helm_dome', 'head', (-.2, 0, 66.2), (5.3, 5.3, 4.4), bevel=4.0, seed=122, pillow=.2,
          shape=lambda v: (v[0], v[1]*(1-.1*max(0, v[2]/4.4)), v[2]))
        B('helm_brim', 'head', (.6, 0, 64.1), (5.9, 5.8, .7), bevel=.6, seed=123, pillow=.1)
        B('helm_crest', 'head', (-.6, 0, 70.6), (5.2, .8, 1.3), bevel=.7, seed=124, pillow=.2,
          shape=lambda v: (v[0], v[1], v[2]-.07*v[0]*v[0]/5.2))
        B('face_mass', 'head', (3.2, 0, 60.8), (2.6, 3.5, 3.2), bevel=2.0, seed=125, pillow=.2, chip=.3)
        B('face_brow', 'head', (5.6, 0, 62.75), (1.1, 3.8, .8), rot=euler(0, 10, 0), bevel=.7, seed=126, chip=.2,
          shape=lambda v: (v[0]-.12*v[1]*v[1]/3.6, v[1], v[2]))
        B('face_nose', 'head', (6.2, 0, 60.9), (.9, .75, 1.5), rot=euler(0, 12, 0), bevel=.5, seed=127, chip=.2,
          shape=lambda v: (v[0], v[1]*(.55+.45*(v[2]+1.5)/3.0), v[2]))
        for s in (1, -1):
            B(f'face_eye_{s}', 'head', (5.35, s*1.85, 61.7), (.6, 1.15, .72), bevel=.5, seed=128+s, chip=0, role='void', pillow=0, hewn=0)
            B(f'face_cheek_{s}', 'head', (2.8, s*4.6, 61.0), (2.8, .9, 3.2), rot=euler(0, 0, s*-14), bevel=.8, seed=130+s, pillow=.3)
        B('face_moustache', 'head', (5.7, 0, 59.4), (.8, 2.6, .6), bevel=.5, seed=132, chip=.2,
          shape=lambda v: (v[0], v[1], v[2]-.2*v[1]*v[1]/2.6))
        B('face_beard', 'head', (4.6, 0, 56.8), (1.9, 3.4, 2.8), rot=euler(0, -14, 0), bevel=1.3, seed=133, pillow=.3, chip=.4,
          shape=lambda v: (v[0], v[1]*(.45+.55*(v[2]+2.8)/5.6), v[2]))
    elif head == 'greathelm':
        # Closed great helm with a visor slit and a flared crest.
        B('helm_dome', 'head', (.8, 0, 64.0), (5.6, 5.2, 6.4), bevel=3.2, seed=122, pillow=.15,
          shape=lambda v: (v[0]+.9*max(0, 1-abs(v[1])/5.2)*(v[0] > 0), v[1]*(1-.12*max(0, v[2]/6.4)), v[2]))
        B('helm_crest', 'head', (-.6, 0, 71.2), (5.6, .9, 1.6), bevel=.7, seed=124, pillow=.2,
          shape=lambda v: (v[0], v[1], v[2]-.08*v[0]*v[0]/5.6))
        B('helm_visor_rib', 'head', (7.0, 0, 62.6), (.7, .8, 3.6), bevel=.5, seed=125, chip=.2)
        for s in (1, -1):
            B(f'face_eye_{s}', 'head', (6.6, s*2.5, 65.0), (.7, 1.7, .45), bevel=.35, seed=128+s, chip=0, role='void', pillow=0, hewn=0)
        B('helm_band', 'head', (.8, 0, 58.8), (5.8, 5.6, 1.0), bevel=.8, seed=126, pillow=.1)
    # Arms: layered pauldrons, rerebrace, couter, vambrace, flared cuff, gauntlet.
    for side, s in (('L', 1), ('R', -1)):
        k = 140 if side == 'L' else 170
        sh, el, wr = R(f'arm_{side}_upper'), R(f'arm_{side}_lower'), R(f'arm_{side}_end')
        B(f'pauldron_{side}', f'arm_{side}_upper', add(sh, (-.4, s*1.6*pauldron, 1.8*pauldron)), mul((6.2, 5.2, 4.2), pauldron), rot=euler(s*-20, 0, 0),
          bevel=3.2*pauldron, seed=k, pillow=.2, chip=chip*1.2)
        B(f'pauldron_lame_{side}', f'arm_{side}_upper', add(sh, (-.2, s*2.8, -2.6)), mul((5.4, 4.2, 1.5), pauldron), rot=euler(s*-26, 0, 0),
          bevel=1.0, seed=k+1, pillow=.3)
        C(f'core_shoulder_{side}', f'arm_{side}_upper', add(sh, (0, 0, -1)), 3.8, seed=k+2)
        B(f'rerebrace_{side}', f'arm_{side}_upper', lerp(sh, el, .55), (3.1, 3.0, 4.6), rot=along(sh, el), seed=k+3)
        C(f'core_elbow_{side}', f'arm_{side}_lower', el, 3.1, seed=k+4)
        B(f'couter_{side}', f'arm_{side}_lower', add(el, mul(unit(sub(el, lerp(sh, wr, .5))), 1.6)), (1.4, 2.6, 2.4),
          rot=along(el, add(el, sub(el, lerp(sh, wr, .5)))), bevel=.9, seed=k+5, pillow=.4)
        B(f'vambrace_{side}', f'arm_{side}_lower', lerp(el, wr, .5), (3.1, 2.9, 4.8), rot=along(el, wr), seed=k+6,
          shape=lambda v: (v[0]*(1+.1*v[2]/4.8), v[1]*(1+.1*v[2]/4.8), v[2]))
        B(f'cuff_{side}', f'arm_{side}_lower', lerp(el, wr, .9), (3.9, 3.7, 1.2), rot=along(el, wr), bevel=.8, seed=k+7, pillow=.2)
        grip = add(wr, mul(unit(sub(wr, el)), 3.0))
        B(f'gauntlet_{side}', f'arm_{side}_end', grip, (3.0, 2.7, 3.2), rot=along(el, wr), bevel=1.3, seed=k+8)
    # Legs: cuisse, poleyn, greave and a pointed, lamed sabaton.
    for side, s in (('L', 1), ('R', -1)):
        k = 200 if side == 'L' else 230
        hp, kn, an = R(f'leg_{side}_upper'), R(f'leg_{side}_lower'), R(f'leg_{side}_end')
        C(f'core_hip_{side}', f'leg_{side}_upper', hp, 4.2, seed=k)
        B(f'cuisse_{side}', f'leg_{side}_upper', lerp(hp, kn, .47), (4.3, 4.0, 5.9), rot=along(hp, kn), seed=k+1,
          shape=lambda v: (v[0]*(1-.08*v[2]/5.9), v[1]*(1-.08*v[2]/5.9), v[2]))
        C(f'core_knee_{side}', f'leg_{side}_lower', kn, 3.6, seed=k+2)
        B(f'poleyn_{side}', f'leg_{side}_lower', add(kn, (3.2, 0, .3)), (1.5, 3.2, 2.7), bevel=1.0, seed=k+3, pillow=.4)
        if legs == 'sabaton':
            B(f'greave_{side}', f'leg_{side}_lower', lerp(kn, an, .5), (3.6, 3.5, 5.0), rot=along(kn, an), seed=k+4,
              shape=lambda v: (v[0]*(1+.12*v[2]/5), v[1]*(1+.12*v[2]/5), v[2]))
            C(f'core_ankle_{side}', f'leg_{side}_end', add(an, (0, 0, .3)), 3.0, seed=k+5)
            B(f'sabaton_{side}', f'leg_{side}_end', (2.6, s*7.5, 2.75), (5.6, 3.6, 2.0), bevel=1.3, seed=k+6, rough=.08,
              pillow=0, hewn=.03, shape=lambda v: (v[0], v[1]*(1-.2*max(0, v[0]/5.6)), v[2]-.4*max(0, v[0]/5.6)))
            B(f'sabaton_toe_{side}', f'leg_{side}_end', (9.0, s*7.5, 2.0), (2.2, 2.2, 1.35), bevel=.9, seed=k+7, rough=.06,
              pillow=0, hewn=.02, shape=lambda v: (v[0], v[1]*(1-.45*max(0, v[0]/2.2)), v[2]*(1-.3*max(0, v[0]/2.2))))
        else:
            # Spectral greaves taper away to nothing above the floor.
            B(f'greave_{side}', f'leg_{side}_lower', lerp(kn, an, .42), (3.4, 3.3, 6.2), rot=along(kn, an), seed=k+4,
              shape=lambda v: (v[0]*(1-.55*max(0, v[2]/6.2)), v[1]*(1-.55*max(0, v[2]/6.2)), v[2]))
    return parts


def hang_cape(kit, world, amount=.72, sway=(0, 0, 0)):
    """Cape follows the chest's clasp but mostly keeps hanging (rigid, cosmetic)."""
    kit.follow(world, 'cape', 'chest')
    loc, q = world[kit.IDS['cape']]
    world[kit.IDS['cape']] = (loc, qmul(Q(*sway), slerp(q, IDENT, amount)))


def grip_hands(kit, world, grip, q, hands=('R', 'L'), bends=None, reach=.999, slide=None, haft=(0, 0, -1)):
    """Solve arms so each fist keeps its rest relation to the posed weapon.

    ``slide`` moves a fist along the rest haft axis ``haft`` (world units), so a
    hand can slide toward the head during a chop and still wrap the haft.
    """
    g0 = kit.rest('weapon'); world[kit.IDS['weapon']] = (tuple(grip), q)
    for side in hands:
        s = 1 if side == 'L' else -1
        rel = add(sub(kit.rest(f'arm_{side}_end'), g0), mul(haft, (slide or {}).get(side, 0)))
        wrist = add(grip, rotate(q, rel))
        bend = (bends or {}).get(side, (-.4, s, -.3))
        kit.limb(world, f'arm_{side}', 'chest', wrist, bend, q, reach)


def plant_legs(kit, world, feet=None, bend=(1, 0, 0), foot_q=None):
    feet = feet or {}
    for side in 'LR':
        target = feet.get(side, kit.rest(f'leg_{side}_end'))
        kit.limb(world, f'leg_{side}', 'pelvis', target, bend, (foot_q or {}).get(side, IDENT))


# ------------------------------------------------------------------ tests
def creature_tests(module_name, materials_name, symbol, gldefs, emissive=False, unused_bones=(), death_top=30.0,
                   planted=(), uses_root=False):
    """Shared unittest base for a guardian-family creature (used by test_<slug>.py)."""
    import importlib
    import unittest
    from .skeletal_registry import find, PENDING
    g = importlib.import_module('tools.monster_models.'+module_name)

    class Base(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            cls.g = g
            cls.parts, cls.v, cls.n, cls.uv, cls.tri, cls.w = g.geometry()
            cls.clips, cls.bounds = g.animation_data(cls.v, cls.w)
            cls.names = [c['name'] for c in cls.clips]

        def frame(self, clip, i=None):
            frames = self.clips[self.names.index(clip)]['frames']
            return frames[len(frames)//2 if i is None else i]

        def test_profile_matches_clips(self):
            row = find(symbol)
            self.assertEqual(row['clips'], self.names)
            self.assertEqual(row['durations'][2:], [tics(len(c['frames']), c['fps']) for c in self.clips][2:])
            self.assertEqual(row['walkFrames'], len(self.clips[1]['frames']))
            self.assertEqual([c['loop'] for c in self.clips], [True, True, False, False, False, False])
            self.assertEqual(row['model'], g.MODEL.rsplit('/', 1)[1]); self.assertEqual(row['skin'], g.SKIN)
            self.assertNotIn('visualScale', row)
            self.assertTrue((ROOT/row['report']).is_file())
            for path in row.get('ownedFiles', []): self.assertTrue((ROOT/path).is_file(), path)
            self.assertEqual(bool(row.get('emissive')), emissive)

        def test_rigid_segments(self):
            for row in self.w:
                self.assertEqual(len(row), 1); self.assertEqual(row[0][1], 1)
            used = {g.BONES[row[0][0]][0] for row in self.w}
            self.assertEqual(used, {n for n, p, v in g.BONES}-(set() if uses_root else {'root'})-set(unused_bones))
            for p in self.parts: self.assertEqual(len(p.vertices), 4*len(p.faces))

        def test_cell_clearance_and_loops(self):
            for b in self.bounds:
                self.assertGreaterEqual(b[0], -32); self.assertGreaterEqual(b[1], -32)
                self.assertLessEqual(b[3], 32); self.assertLessEqual(b[4], 32)
            for c in self.clips:
                count = len(c['frames'])
                for i, frame in enumerate(c['frames']):
                    t = i/(count if c['loop'] else count-1)
                    self.assertEqual(frame, g.pose(c['name'], t))
                    # No automatic floor compensation: every raw frame is above the floor.
                    self.assertGreater(min(p[2] for p in g.deform(self.v, self.w, frame)), .07, (c['name'], i))
                if c['loop']:
                    a = g.deform(self.v, self.w, g.pose(c['name'], 0)); b = g.deform(self.v, self.w, g.pose(c['name'], 1))
                    self.assertLess(max(math.dist(x, y) for x, y in zip(a, b)), 1e-8)

        def test_action_middle_frames_change_silhouette(self):
            rest = g.deform(self.v, self.w, self.frame(self.names[0], 0))
            for clip in self.names[2:4]:
                mid = g.deform(self.v, self.w, self.frame(clip))
                first = g.deform(self.v, self.w, self.frame(clip, 0))
                self.assertGreater(max(math.dist(a, b) for a, b in zip(mid, first)), 15, clip)
                def box(points): return [min(p[k] for p in points) for k in range(3)]+[max(p[k] for p in points) for k in range(3)]
                r, m = box(rest), box(mid)
                self.assertGreater(max(abs(a-b) for a, b in zip(r, m)), 6, clip)

        def test_death_ends_on_the_floor(self):
            death = self.names[5]
            last = g.deform(self.v, self.w, self.frame(death, -1))
            self.assertLess(max(p[2] for p in last), death_top)
            self.assertGreater(min(p[2] for p in last), .07)

        def test_planted_feet(self):
            for clip in planted:
                count = len(self.clips[self.names.index(clip)]['frames'])
                for i in range(count):
                    T = g.matrices(self.frame(clip, i))
                    for side in 'LR':
                        self.assertLess(math.dist(T[g.IDS[f'leg_{side}_end']][0], g.REST[g.IDS[f'leg_{side}_end']]), 1e-6, (clip, i, side))

        def test_islands_do_not_overlap(self):
            seen = set()
            for p in self.parts:
                for f in p.faces:
                    us = [p.uv[i] for i in f]
                    for u, v in us: self.assertTrue(0 < u < 1 and 0 < v < 1)
                    key = (round(us[0][0]*SIZE), round(us[0][1]*SIZE)); self.assertNotIn(key, seen); seen.add(key)

        def test_material_definition(self):
            snippet = PENDING/(symbol+'.gldefs')
            text = snippet.read_text() if snippet.is_file() else (ROOT/'mod/BrogueDoom/GLDEFS').read_text()
            block = text[text.index(f'material "{g.SKIN}"'):]; block = block[:block.index('}')]
            for word in gldefs.get('present', ()): self.assertIn(word, block)
            for word in gldefs.get('absent', ()): self.assertNotIn(word, block.lower())

        def test_runtime_and_material_bytes(self):
            m = importlib.import_module('tools.monster_models.'+materials_name)
            image, spec = m.paint(self.parts)
            maps = not emissive and not hasattr(g, 'SHADER')
            for path, blob in runtime_bytes(g, self.parts, self.v, self.n, self.uv, self.tri, self.w, image, spec, maps).items():
                self.assertEqual(blob, (ROOT/path).read_bytes(), path)
            self.__class__.image = image

    return Base

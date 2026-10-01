"""Dragon: connected skin, wing/jaw/flame anatomy, planted paws, cell clearance, key poses, hidden flames,
slumped death and bytes."""
import collections
import io
import math
import unittest
from . import dragon_animation as g, dragon_materials as m, iqm
from .skeletal_registry import find


def closed(part):
    edges = collections.Counter()
    for face in part.faces:
        for a, b in zip(face, face[1:]+face[:1]):
            edges[tuple(sorted((tuple(round(c, 6) for c in part.vertices[a]), tuple(round(c, 6) for c in part.vertices[b]))))] += 1
    return set(edges.values()) == {2}


def middle_travel(clip):
    """Largest bone travel from the clip's first frame, at the middle frame and overall."""
    frames = clip['frames']
    first = [p for p, _ in g.matrices(frames[0])]
    def travel(f): return max(math.dist(a, b) for a, (b, _) in zip(first, g.matrices(f)))
    return travel(frames[len(frames)//2]), max(travel(f) for f in frames)


def s_abs(v): return abs(v)


def paw_tip(T, side):
    s = 1 if side == 'L' else -1
    loc, q = T[g.IDS['paw_'+side]]
    return g.add(loc, g.rotate(q, g.sub(g.TOEF[s], g.WRISTF[s])))


class DragonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts, cls.v, cls.n, cls.uv, cls.tri, cls.w = g.geometry()
        cls.clips, cls.bounds = g.animation_data(cls.v, cls.w)
        cls.named = {c['name']: c for c in cls.clips}
        cls.source = {p.name: p for p in g.build_parts()}
        cls.owner = [p.name for p in cls.parts for _ in p.vertices]

    def test_connected_closed_skin_and_weights(self):
        p = self.parts[0]; ids = p.skin_topology; edges = collections.Counter(); graph = {i: set() for i in ids}
        for face in p.faces:
            for a, b in zip(face, face[1:]+face[:1]):
                a, b = ids[a], ids[b]; self.assertNotEqual(a, b)
                edges[tuple(sorted((a, b)))] += 1; graph[a].add(b); graph[b].add(a)
        self.assertEqual(set(edges.values()), {2})
        seen = {ids[0]}; todo = [ids[0]]
        while todo:
            for i in graph[todo.pop()]:
                if i not in seen: seen.add(i); todo.append(i)
        self.assertEqual(seen, set(ids))
        reps = {}
        for i, key in enumerate(ids):
            if key in reps:
                j = reps[key]; self.assertEqual(self.v[i], self.v[j]); self.assertEqual(self.w[i], self.w[j])
            reps[key] = i
        used = {g.BONES[b][0] for row in self.w[:len(ids)] for b, weight in row if weight > .01}
        for bone in ('pelvis', 'chest', 'neck_0', 'neck_1', 'head', 'tail_0', 'tail_5', 'arm_L', 'fore_R', 'paw_L', 'thigh_L',
                     'shin_R', 'foot_L', 'toes_R'):
            self.assertIn(bone, used)
        for row in self.w:
            self.assertAlmostEqual(math.fsum(weight for _, weight in row), 1, places=6); self.assertLessEqual(len(row), 4)

    def test_signature_anatomy(self):
        for name in ('horn_L', 'horn2_R', 'horn3_L', 'eye_L', 'lid_R', 'tooth_3_L', 'tooth_5_R', 'ltooth_1_R', 'jaw', 'tongue',
                     'claw_1_L', 'claw_h2_R', 'claw_thumb_L', 'spine_3', 'tail_blade', 'finger_3_R', 'wing_arm_L', 'wing_knob_R',
                     'membrane_0_L', 'membrane_2_R', 'flame_0', 'flame_2a', 'flame_2f', 'flame_1b', 'flame_3s2'):
            self.assertIn(name, self.source); self.assertTrue(closed(self.source[name]), name)
        # Six upper teeth per side, three lower teeth per side, three fore and three hind claws per paw.
        self.assertEqual(sum(n.startswith('tooth_') for n in self.source), 12)
        self.assertEqual(sum(n.startswith('ltooth_') for n in self.source), 6)
        self.assertEqual(sum(n.startswith('claw_') and n[5] in '012' for n in self.source), 6)
        self.assertEqual(sum(n.startswith('claw_h') for n in self.source), 6)
        self.assertEqual(sum(n.startswith('membrane_') for n in self.source), 6)
        self.assertEqual(sum(n.startswith('finger_') for n in self.source), 6)
        self.assertGreaterEqual(sum(n.startswith('spine_') for n in self.source), 16)
        for name, bone in (('horn_L', 'head'), ('eye_R', 'head'), ('tooth_2_L', 'head'), ('jaw', 'jaw'), ('tongue', 'jaw'),
                           ('ltooth_0_R', 'jaw'), ('claw_0_L', 'paw_L'), ('claw_h1_R', 'toes_R'), ('claw_thumb_L', 'wing_b_L'),
                           ('wing_knob_R', 'wing_b_R'), ('tail_blade', 'tail_5'), ('flame_0', 'flame_0'), ('flame_1b', 'flame_1'),
                           ('flame_2c', 'flame_2'), ('flame_3s4', 'flame_3')):
            p = self.source[name]
            self.assertTrue(all(g.weights(p, v, u) == [(g.IDS[bone], 1)] for v, u in zip(p.vertices, p.uv)), name)
        # Horns sweep back over the neck; the tail reaches well behind; wings peak above the head; whole rest pose fits the cell.
        rest = [v for p in self.source.values() for v in p.vertices]
        horn = self.source['horn_L'].vertices
        self.assertLess(min(v[0] for v in horn), 4); self.assertGreater(max(v[2] for v in horn), 44)
        self.assertLess(min(v[0] for v in self.source['skin_tail'].vertices), -22)
        # Horns sweep back and down at their tips (the head reads first); folded wing arms angle back and outward.
        self.assertLess(horn[len(horn)//2][2]-max(v[2] for v in horn), 0.5)
        wing = self.source['wing_arm_L'].vertices
        self.assertLess(min(v[0] for v in wing), g.S0[1][0]-8); self.assertGreater(max(v[1] for v in wing), 14)
        self.assertLess(max(v[2] for v in wing), 36)
        self.assertTrue(48 < max(v[2] for v in rest) < 56)
        for a in range(2):
            self.assertGreaterEqual(min(v[a] for v in rest), -32); self.assertLessEqual(max(v[a] for v in rest), 32)
        self.assertEqual(find('MK_DRAGON').get('visualScale', 1.0), 1.0)
        for i, (name, parent, local) in enumerate(g.BONES):
            self.assertLess(math.dist(g.REST[i], g.RIG.rest[i]), 1e-9, name)
        self.assertEqual(len(g.BONES), 48)

    def test_wing_membranes_follow_the_finger_bones(self):
        # Each membrane vertex is influenced only by the two bordering finger chains or the body line.
        allowed = {
            0: {'f1a', 'f1b', 'f2a', 'f2b'}, 1: {'f2a', 'f2b', 'f3a', 'f3b'},
            2: {'f3a', 'f3b', 'chest', 'spine', 'pelvis'}}
        for side in ('L', 'R'):
            for k in range(3):
                p = self.source[f'membrane_{k}_{side}']
                names = {g.BONES[b][0][:-2] if g.BONES[b][0][-2:] in ('_L', '_R') else g.BONES[b][0]
                         for v, u in zip(p.vertices, p.uv) for b, w in g.weights(p, v, u)}
                self.assertTrue(names <= allowed[k], (side, k, names))
        # Spread wings stay a real membrane: consecutive fingers must not cross in the breath key pose.
        T = g.matrices(self.named['breathe']['frames'][len(self.named['breathe']['frames'])//2])
        for side, s in g.SIDES:
            tips = [T[g.IDS[f'f{f}b_'+side]][0] for f in (1, 2, 3)]
            for a, b in zip(tips, tips[1:]):
                self.assertGreater(math.dist(a, b), 2.0)

    def test_profile_clearance_and_loops(self):
        self.assertEqual([c['name'] for c in self.clips], ['idle', 'stalk', 'breathe', 'lash', 'recoil', 'death'])
        self.assertEqual([c['loop'] for c in self.clips], [True, True, False, False, False, False])
        profile = find('MK_DRAGON')
        self.assertEqual(profile['clips'], [c['name'] for c in self.clips])
        # Durations are engine tics at 35 Hz: long enough to play every frame at the clip's fps.
        for role in range(2, 6):
            c = self.clips[role]
            self.assertGreaterEqual(profile['durations'][role], math.ceil(len(c['frames'])*35/c['fps']), c['name'])
        self.assertEqual(profile['walkFrames'], len(self.named['stalk']['frames']))
        self.assertEqual(profile['skin'], g.SKIN); self.assertTrue(g.MODEL.endswith(profile['model']))
        self.assertEqual(profile['class'], 'BrogueMonsterK50')
        # Every frame of every clip stays inside the -32..+32 cell, measured from the deformed skin, and above the floor.
        for name, c in self.named.items():
            for i, frame in enumerate(c['frames']):
                d = g.deform(self.v, self.w, frame)
                for a in range(2):
                    self.assertGreaterEqual(min(p[a] for p in d), -32, (name, i, a)); self.assertLessEqual(max(p[a] for p in d), 32, (name, i, a))
                self.assertGreater(min(p[2] for p in d), .05, (name, i))
        for b in self.bounds:
            self.assertGreaterEqual(b[0], -32); self.assertGreaterEqual(b[1], -32)
            self.assertLessEqual(b[3], 32); self.assertLessEqual(b[4], 32); self.assertGreaterEqual(b[2], .07-1e-9)
        for c in self.clips:
            count = len(c['frames'])
            for i, frame in enumerate(c['frames']):
                expect = g.pose(c['name'], i/(count if c['loop'] else count-1))
                for row, want in zip(frame, expect): self.assertEqual(row[3:], want[3:]); self.assertEqual(row[7:], (1, 1, 1))
            if c['loop']:
                a = g.deform(self.v, self.w, g.pose(c['name'], 0)); b = g.deform(self.v, self.w, g.pose(c['name'], 1))
                self.assertLess(max(math.dist(x, y) for x, y in zip(a, b)), 1e-8)

    def test_planted_paws_and_gait(self):
        # Idle: all four paws stay exactly on their rest spots while the body breathes.
        for frame in self.named['idle']['frames']:
            T = g.matrices(frame)
            for side, s in g.SIDES:
                self.assertLess(math.dist(T[g.IDS['toes_'+side]][0], g.BALL[s]), 1e-4, side)
                self.assertLess(math.dist(paw_tip(T, side), g.TOEF[s]), 1e-4, side)
        # Walk: lateral-sequence gait, exactly one paw swinging at a time; the other three stay on the floor.
        floor = {}
        for side, s in g.SIDES:
            floor[side, 'f'] = g.TOEF[s][2]; floor[side, 'h'] = g.BALL[s][2]
        swings = collections.Counter()
        for frame in self.named['stalk']['frames']:
            T = g.matrices(frame)
            heights = {}
            for side, s in g.SIDES:
                heights[side, 'f'] = paw_tip(T, side)[2]-floor[side, 'f']
                heights[side, 'h'] = T[g.IDS['toes_'+side]][0][2]-floor[side, 'h']
            up = [k for k, h in heights.items() if h > .3]
            self.assertLessEqual(len(up), 1)
            for k in up: swings[k] += 1
            for k, h in heights.items():
                if h <= .3: self.assertLess(abs(h), .3)
        self.assertEqual(len(swings), 4)
        for k, count in swings.items(): self.assertGreaterEqual(count, 4)

    def test_compact_quadruped_stance(self):
        for frame in self.named['idle']['frames']:
            T = g.matrices(frame)
            chest, pelvis, head = (T[g.IDS[b]][0] for b in ('chest', 'pelvis', 'head'))
            self.assertLess(abs(chest[2]-pelvis[2]), 3.5)          # level back
            self.assertGreater(head[0], chest[0]+5)                # head forward
            self.assertGreater(head[2], chest[2]+22)               # tall S-neck
            # Wings stay folded high: wrist peaks above the back, fingers trailing behind it.
            for side in ('L', 'R'):
                wrist = T[g.IDS['f1a_'+side]][0]
                tip = T[g.IDS['f3b_'+side]][0]
                self.assertGreater(wrist[2], chest[2]+12); self.assertLess(tip[0], wrist[0]-3)
                self.assertGreater(s_abs(wrist[1]), 12)

    def test_middle_frame_key_poses(self):
        for name in ('breathe', 'lash', 'recoil'):
            mid, top = middle_travel(self.named[name])
            self.assertGreater(mid, 6 if name != 'recoil' else 4.5, name)
            self.assertGreater(mid, .8*top, name)
        frames = self.named['breathe']['frames']; mid = frames[len(frames)//2]
        idle = self.named['idle']['frames'][0]
        T, T0 = g.matrices(mid), g.matrices(idle)
        # Breath: low, jaw open, wings flared out beyond the body, body pulled back.
        d = g.deform(self.v, self.w, mid)
        self.assertLess(max(p[2] for p, o in zip(d, self.owner) if not o.startswith(('membrane', 'finger', 'wing'))), 42)
        self.assertLess(T[g.IDS['chest']][0][2], T0[g.IDS['chest']][0][2]-2)
        self.assertLess(T[g.IDS['pelvis']][0][0], T0[g.IDS['pelvis']][0][0]-6)
        jaw_open = g.rotate(T[g.IDS['jaw']][1], (1, 0, 0))
        self.assertLess(jaw_open[2], -.4)
        for side, s in g.SIDES:
            self.assertGreater(s*T[g.IDS['f1b_'+side]][0][1], 14)
        # Lash: body yawed hard, one forepaw raked well off the floor; recoil throws the head back and the muzzle up.
        frames = self.named['lash']['frames']; T = g.matrices(frames[len(frames)//2])
        self.assertGreater(paw_tip(T, 'R')[2], 9)
        frames = self.named['recoil']['frames']; T = g.matrices(frames[len(frames)//2])
        self.assertLess(T[g.IDS['head']][0][0], T0[g.IDS['head']][0][0]-3)   # head thrown back over the shoulders
        self.assertGreater(g.rotate(T[g.IDS['head']][1], (1, 0, 0))[2], .3)      # muzzle pointing up

    def test_flames_parked_in_the_chest_except_in_breath(self):
        # Every flame vertex is parked inside the chest/belly/hip volume at rest, so no other clip can show fire.
        def inside(pt):
            return min(sum(((pt[i]-c[i])/r[i])**2 for i in range(3)) for c, r in g.TORSO_BLOBS)
        flame = {n: p for n, p in self.source.items() if n.startswith('flame_')}
        self.assertGreaterEqual(len(flame), 25)
        for name, p in flame.items():
            self.assertLess(max(inside(v) for v in p.vertices), .95, name)
        for name, c in self.named.items():
            if name == 'breathe': continue
            for i, frame in enumerate(c['frames']):
                for k in range(4):
                    row = frame[g.IDS[f'flame_{k}']]
                    self.assertEqual(row[:3], g.BONES[g.IDS[f'flame_{k}']][2], (name, i, k))
                    self.assertEqual(row[3:7], (0., 0., 0., 1.), (name, i, k))
        frames = self.named['breathe']['frames']
        for f in (frames[0], frames[-1]):
            self.assertEqual(f[g.IDS['flame_0']][3:7], (0., 0., 0., 1.))
        mid = frames[len(frames)//2]
        d = g.deform(self.v, self.w, mid)
        tip = max(p[0] for p, o in zip(d, self.owner) if o.startswith('flame_'))
        snout = max(p[0] for p, o in zip(d, self.owner) if o in ('jaw', 'tooth_5_L', 'skin_snout'))
        # A long cone: streak tongues reach at least 12 units beyond the jaws, fanned sideways at least +-4 units.
        self.assertGreater(tip-snout, 12)
        ys = [p[1] for p, o in zip(d, self.owner) if o.startswith('flame_')]
        self.assertGreater(max(ys)-min(ys), 8)
        zs = [p[2] for p, o in zip(d, self.owner) if o.startswith('flame_')]
        self.assertGreater(max(zs)-min(zs), 8)
        for f in frames:
            self.assertLess(max(p[0] for p in g.deform(self.v, self.w, f)), 32)

    def test_predatory_face(self):
        s = self.source
        # Long wedge snout with a flat top and nostril ridges; eyes are small slits flush under a heavy brow.
        snout = s['skin_snout'].vertices
        self.assertGreater(max(v[0] for v in snout)-min(v[0] for v in snout), 10)
        top = [v[2] for v in snout if abs(v[1]) < .8 and v[0] > 22 and v[2] > g.HEAD_DZ+30.5]
        self.assertTrue(top and max(top)-min(top) < 1.5)
        for name in ('skin_nridge_L', 'skin_nostril_R', 'skin_brow_L'):
            self.assertIn(name, s)
        for side in ('L', 'R'):
            eye = s['eye_'+side].vertices
            ext = [max(v[a] for v in eye)-min(v[a] for v in eye) for a in range(3)]
            self.assertLess(max(ext), 2.6)                          # no eyeball dome
            brow = s['skin_brow_'+side].vertices
            self.assertGreater(max(v[2] for v in brow), max(v[2] for v in eye)+1.2)   # brow overhangs the eye
            self.assertGreater(max(abs(v[1]) for v in brow), max(abs(v[1]) for v in eye)-.6)
        self.assertEqual(sum(n.startswith('horn4_') for n in s), 8)     # brow spines
        self.assertEqual(sum(n.startswith('horn5_') for n in s), 6)     # jaw frill spikes
        # Fangs overlap the lower jaw: long upper teeth hang below the top of the jaw.
        jaw_top = max(v[2] for v in s['jaw'].vertices)
        fang = min(v[2] for v in s['tooth_1_L'].vertices)
        self.assertLess(fang, jaw_top-2.5)
        # The top of the head is painted darker than the cheek plates, so the face reads from the front.
        base = m.mix(m.SCALE_LO, m.SCALE_MID, .6)
        frac = dict(head=1., neck=0., torso=0., fleg=0., hleg=0., paw=0., tail=0.)
        topc = m.head_paint((18., 0., 35.1+g.HEAD_DZ), (0., 0., 1.), frac, base, .8)
        cheek = m.head_paint((20.4, 3.9, 28.6+g.HEAD_DZ), (0., 1., 0.), frac, base, .8)
        self.assertLess(sum(topc), sum(cheek)-40)

    def test_death_ends_slumped_on_the_floor(self):
        frames = self.named['death']['frames']
        T = g.matrices(frames[len(frames)//2])
        # The sampled middle frame is still collapsing: body lower than standing but not yet down.
        T0 = g.matrices(self.named['idle']['frames'][0])
        self.assertLess(T[g.IDS['chest']][0][2], T0[g.IDS['chest']][0][2]-1.5)
        end = g.deform(self.v, self.w, frames[-1])
        self.assertLess(min(p[2] for p in end), .4)
        body = [p for p, o in zip(end, self.owner) if o == 'Connected_skin']
        self.assertLess(sorted(p[2] for p in body)[len(body)//2], 9.5)
        T = g.matrices(frames[-1])
        for bone in ('pelvis', 'chest', 'head', 'tail_3', 'paw_L', 'paw_R', 'toes_L', 'toes_R'):
            self.assertLess(T[g.IDS[bone]][0][2], 12, bone)
        # Only the horns and the draped wing bones stand higher; everything is under 20 and the whole corpse is lower than idle.
        self.assertLess(max(p[2] for p in end), 20)
        idle_top = max(p[2] for p in g.deform(self.v, self.w, self.named['idle']['frames'][0]))
        self.assertLess(max(p[2] for p in end), .5*idle_top)
        # No flame, and the wings droop to both sides of the body.
        for side, s in g.SIDES:
            self.assertGreater(s*T[g.IDS['f2b_'+side]][0][1], 8)
            self.assertLess(T[g.IDS['f2b_'+side]][0][2], 12)
        self.assertEqual(frames[-1], frames[-2])

    def test_head_is_held_high_on_the_s_neck(self):
        # Idle: the horned head towers over the body (skull top / horn tips 48-56 units), while the breath key pose stays low.
        for frame in self.named['idle']['frames']:
            d = g.deform(self.v, self.w, frame)
            head = [p for p, o in zip(d, self.owner) if o in ('horn_L', 'horn_R', 'jaw', 'eye_L')]
            self.assertTrue(48 <= max(p[2] for p in head) <= 56, max(p[2] for p in head))
            T = g.matrices(frame)
            self.assertGreater(T[g.IDS['head']][0][2], 40)
        frames = self.named['breathe']['frames']
        T = g.matrices(frames[len(frames)//2])
        self.assertLess(T[g.IDS['head']][0][2], 32)
        self.assertLess(g.deform(self.v, self.w, frames[len(frames)//2])[self.owner.index('jaw')][2], 32)

    def test_no_floor_dips_lift_the_root(self):
        # The exporter lifts the whole root when any vertex is below z=0.07; key poses must not need that.
        for name in ('idle', 'stalk', 'breathe', 'lash', 'recoil'):
            c = self.named[name]; count = len(c['frames'])
            for i, frame in enumerate(c['frames']):
                want = g.pose(name, i/(count if c['loop'] else count-1))[0][2]
                self.assertLess(frame[0][2]-want, .01, (name, i))   # baked-cage rounding only; no visible hover
        frames = self.named['death']['frames']
        self.assertLess(frames[-1][0][2]-g.pose('death', 1)[0][2], .3)

    def test_green_palette_and_fullbright_flame(self):
        from PIL import Image
        skin = Image.open(io.BytesIO(g.texture_bytes())).convert('RGB')
        # Skin islands: overall emerald green (Brogue's dragonColor), not red.
        px = [skin.getpixel((x, y)) for y in range(0, 2048, 8) for x in range(0, 1024, 8)]
        px = [p for p in px if sum(p) > 20]
        r, gr, b = (sum(p[i] for p in px)/len(px) for i in range(3))
        self.assertGreater(gr, 1.25*r); self.assertGreater(gr, 1.3*b)
        # Brighter flank scales vs dark dorsal band: a wide green value range.
        greens = sorted(p[1] for p in px)
        self.assertGreater(greens[int(.95*len(greens))]-greens[int(.05*len(greens))], 90)
        def cell(name):
            x0, y0, x1, y1 = m.RECTS[name]
            return skin.getpixel(((x0+x1)//2, (y0+y1)//2))
        # Eyes amber/gold, membranes light olive/jade, fire stays orange.
        eye = m.shade('eye', .3, .9); self.assertTrue(eye[0] > 200 and eye[1] > 150 and eye[2] < 120, eye)
        mem = cell('membrane'); self.assertGreaterEqual(mem[1], mem[0]-10); self.assertGreater(mem[1], 130); self.assertGreater(mem[1], mem[2]+50)
        fire = cell('flame'); self.assertGreater(fire[0], 230); self.assertGreater(fire[0], fire[2]+80)
        # The flame cells are exactly what the fullbright shader region covers, and the pending/registered GLDEFS names it.
        import re
        text = (g.ROOT/'mod/BrogueDoom/shaders/dragon-flame.fp').read_text()
        nums = [float(q) for q in re.findall(r'step\(([0-9.]+), vTexCoord', text)]
        self.assertEqual(len(nums), 7)
        fu0, fu1, fv0, fv1, eu0, eu1, ev1 = nums[0], nums[1], nums[2], nums[3], nums[4], nums[5], nums[6]
        for name in ('flame', 'flick'):
            x0, y0, x1, y1 = m.RECTS[name]
            self.assertGreaterEqual(x0/m.SIZE, fu0); self.assertLessEqual(x1/m.SIZE, fu1)
            self.assertGreaterEqual(y0/m.SIZE, fv0); self.assertLessEqual(y1/m.SIZE, fv1)
        x0, y0, x1, y1 = m.RECTS['eye']
        self.assertGreaterEqual(x0/m.SIZE, eu0); self.assertLessEqual(x1/m.SIZE, eu1); self.assertLessEqual(y1/m.SIZE, ev1)
        for name in m.RECTS:
            if name in ('flame', 'flick', 'eye'): continue
            x0, y0, x1, y1 = m.RECTS[name]
            self.assertTrue(x1/m.SIZE <= fu0 or x0/m.SIZE >= fu1 or y1/m.SIZE <= fv0 or y0/m.SIZE >= fv1, name)
            self.assertTrue(x1/m.SIZE <= eu0 or x0/m.SIZE >= eu1 or y0/m.SIZE >= ev1, name)
        gl = g.ROOT/'assets/monsters/skeletal_pending/MK_DRAGON.gldefs'
        text = gl.read_text() if gl.exists() else (g.ROOT/'mod/BrogueDoom/GLDEFS').read_text()
        self.assertIn('shaders/dragon-flame.fp', text)
        self.assertIn('shaders/dragon-flame.fp', ' '.join(find('MK_DRAGON').get('ownedFiles', [])))

    def test_no_degenerate_triangles(self):
        for c in self.clips:
            for frame in (c['frames'][0], c['frames'][len(c['frames'])//2], c['frames'][-1]):
                d = g.deform(self.v, self.w, frame)
                for a, b, cc in self.tri:
                    e1 = [d[b][k]-d[a][k] for k in range(3)]; e2 = [d[cc][k]-d[a][k] for k in range(3)]
                    cr = (e1[1]*e2[2]-e1[2]*e2[1], e1[2]*e2[0]-e1[0]*e2[2], e1[0]*e2[1]-e1[1]*e2[0])
                    self.assertGreater(sum(x*x for x in cr), 0)

    def test_atlas_roles(self):
        self.assertTrue({m.role(p.name) for p in self.parts} <= set(m.ROLES) | {'skin', 'membrane'})
        for u, v in self.uv: self.assertTrue(0 <= u <= 1 and 0 <= v <= 1)
        skin = self.parts[0]
        self.assertLessEqual(len(skin.faces), m.SKIN_ISLANDS)
        self.assertTrue(all(u < .5 for u, v in skin.uv))
        self.assertTrue(all(u > .5 for p in self.parts[1:] for u, v in p.uv))
        # Membranes have their own large cell; no two roles share pixels.
        rects = list(m.RECTS.values())
        for i, a in enumerate(rects):
            for b in rects[i+1:]:
                self.assertTrue(a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])

    def test_runtime_and_material_bytes(self):
        data = iqm.encode(self.v, self.n, self.uv, self.tri, self.w, g.BONES, self.clips, self.bounds,
                          mesh_label='Project_Broom_dragon', material_path=g.SKIN)
        self.assertEqual(data, (g.ROOT/g.MODEL).read_bytes())
        skin = g.texture_bytes()
        self.assertEqual(skin, (g.ROOT/'mod/BrogueDoom'/g.SKIN).read_bytes())
        from PIL import Image
        im = Image.open(io.BytesIO(skin)).convert('RGB')
        def px(u, v): return im.getpixel((int(u*m.SIZE), int((1-v)*m.SIZE)))
        # Ivory horn tips and pale ochre belly plates are far lighter than the deep crimson scale seams; membrane is warmer
        # and lighter than the body.
        horn = self.parts[[p.name for p in self.parts].index('horn_L')]
        self.assertGreater(sum(px(*horn.uv[len(horn.uv)-8])), 450)
        self.assertLess(sum(m.SEAM), 60); self.assertGreater(sum(m.BELLY), 480)
        mem = self.parts[[p.name for p in self.parts].index('membrane_1_L')]
        centre = px(*mem.uv[len(mem.uv)//4])
        self.assertGreater(centre[0], 150); self.assertGreater(sum(centre), 300)
        # Painted value range on the skin is wide (dark seams to lit ochre plates).
        luma = [sum(im.getpixel((x, y)))/3 for y in range(0, 2048, 16) for x in range(0, 1024, 16)]
        self.assertGreater(max(luma)-min(luma), 150)


if __name__ == '__main__': unittest.main()

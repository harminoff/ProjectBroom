"""Imp: connected skin, sly anatomy and spurs, predatory crouch, planted feet, scaled clearance,
key poses, limp death and bytes."""
import collections
import math
import unittest
from . import imp_animation as g, imp_materials as m, iqm
from .skeletal_registry import find

K = g.SCALE   # design units -> exported units


def ks(p): return tuple(K*c for c in p)


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


class ImpTests(unittest.TestCase):
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
        for bone in ('head', 'ear_L', 'ear_R', 'tail_0', 'tail_4', 'arm_L', 'forearm_R', 'thigh_L', 'shin_R', 'foot_L', 'toes_R'):
            self.assertIn(bone, used)
        for row in self.w:
            self.assertAlmostEqual(math.fsum(weight for _, weight in row), 1, places=6); self.assertLessEqual(len(row), 4)

    def test_signature_anatomy(self):
        for name in ('horn_L', 'horn_R', 'eye_L', 'eye_R', 'lid_L', 'lid_low_R', 'tooth_1_L', 'tooth_3_R', 'claw_1_L',
                     'claw_thumb_R', 'toe_claw_0_L', 'spur_elbow_L', 'spur_shoulder_R', 'spike_3'):
            self.assertIn(name, self.source); self.assertTrue(closed(self.source[name]), name)
        self.assertEqual(sum(n.startswith('claw_') and 'thumb' not in n for n in self.source), 6)
        self.assertEqual(sum(n.startswith('spike_') for n in self.source), 7)
        # Sly smirk: three sharp teeth at the raised left corner, one fang on the right.
        self.assertEqual(sorted(n for n in self.source if n.startswith('tooth_')), ['tooth_0_L', 'tooth_1_L', 'tooth_2_L', 'tooth_3_R'])
        for name, bone in (('horn_L', 'head'), ('eye_R', 'head'), ('lid_L', 'head'), ('claw_0_L', 'claws_L'), ('skin_spade', 'tail_4'),
                           ('toe_claw_2_R', 'toes_R'), ('spur_elbow_R', 'forearm_R'), ('spur_shoulder_L', 'arm_L'), ('spike_0', 'neck'),
                           ('spike_6', 'pelvis')):
            p = self.source[name]
            self.assertTrue(all(g.weights(p, v, u) == [(g.IDS[bone], 1)] for v, u in zip(p.vertices, p.uv)), name)
        # Sharp horns swept hard back; ears trimmed from the cartoon span; the tail reaches well behind.
        rest = [v for p in self.source.values() for v in p.vertices]
        horn = self.source['horn_L'].vertices
        self.assertLess(min(v[0] for v in horn), -7.5); self.assertGreater(max(v[2] for v in horn), 40)
        self.assertTrue(7.5 < max(v[1] for v in self.source['skin_ear_L'].vertices) < 9.2)
        self.assertLess(min(v[0] for v in self.source['skin_tail'].vertices), -12.5)
        self.assertLess(max(v[2] for v in rest), 44)
        # The 46-48-unit presentation is baked into the exported mesh and rig (unit bone
        # scales); the profile carries no MODELDEF visualScale.
        self.assertEqual(find('MK_IMP').get('visualScale', 1.0), 1.0)
        self.assertTrue(45.5 < max(v[2] for v in self.v)-min(v[2] for v in self.v) < 48.5)
        for i, (name, parent, local) in enumerate(g.BONES):
            self.assertLess(math.dist(g.REST[i], ks(g.D_REST[i])), 1e-9, name)

    def test_profile_clearance_and_no_floor_compensation(self):
        self.assertEqual([c['name'] for c in self.clips], ['idle', 'walk', 'slice', 'snatch', 'recoil', 'death'])
        self.assertEqual([c['loop'] for c in self.clips], [True, True, False, False, False, False])
        profile = find('MK_IMP')
        self.assertEqual(profile['clips'], [c['name'] for c in self.clips])
        # Durations are engine tics at 35 Hz: long enough to play every frame at the clip's fps.
        for role in range(2, 6):
            c = self.clips[role]
            self.assertGreaterEqual(profile['durations'][role], math.ceil(len(c['frames'])*35/c['fps']), c['name'])
        self.assertEqual(profile['walkFrames'], len(self.named['walk']['frames']))
        self.assertEqual(profile['skin'], g.SKIN); self.assertTrue(g.MODEL.endswith(profile['model']))
        for b in self.bounds:
            self.assertGreaterEqual(b[0], -32); self.assertGreaterEqual(b[1], -32)
            self.assertLessEqual(b[3], 32); self.assertLessEqual(b[4], 32); self.assertGreater(b[2], .07)
        for c in self.clips:
            count = len(c['frames'])
            for i, frame in enumerate(c['frames']):
                self.assertEqual(frame, g.pose(c['name'], i/(count if c['loop'] else count-1)))
                for row in frame: self.assertEqual(row[7:], (1, 1, 1))
            if c['loop']:
                a = g.deform(self.v, self.w, g.pose(c['name'], 0)); b = g.deform(self.v, self.w, g.pose(c['name'], 1))
                self.assertLess(max(math.dist(x, y) for x, y in zip(a, b)), 1e-8)

    def test_planted_feet_and_gait(self):
        for name in ('idle', 'recoil'):
            c = self.named[name]
            for frame in c['frames']:
                T = g.matrices(frame)
                for side, s in g.SIDES:
                    self.assertLess(math.dist(T[g.IDS['toes_'+side]][0], ks(g.BALL[s])), 1e-5, (name, side))
        heights = [[g.matrices(f)[g.IDS['toes_'+side]][0][2] for f in self.named['walk']['frames']] for side in ('L', 'R')]
        for h in heights:
            self.assertAlmostEqual(min(h), K*g.BALL[1][2], places=5); self.assertGreater(max(h), 3.5*K)
        # Alternating stance: one foot is always planted.
        for a, b in zip(*heights):
            self.assertLess(min(a, b), K*g.BALL[1][2]+1e-5)

    def test_predatory_crouch(self):
        # Every idle frame: torso pitched forward, head level, long arms hanging low and
        # forward with the claws opened (not steepled at the chest), tail raised behind.
        for frame in self.named['idle']['frames']:
            T = g.matrices(frame)
            pelvis, chest, head = (T[g.IDS[b]][0] for b in ('pelvis', 'chest', 'head'))
            self.assertLess(pelvis[2], K*(g.PELVIS[2]-2.2))
            self.assertGreater(chest[0]-pelvis[0], 1.5*K)   # rest offset is 0.8
            for side, s in g.SIDES:
                hand = T[g.IDS['hand_'+side]][0]
                self.assertLess(hand[2], pelvis[2]); self.assertGreater(hand[0], 3.*K); self.assertGreater(s*hand[1], 5*K)
            self.assertGreater(T[g.IDS['tail_4']][0][2], pelvis[2]+2*K)
        e, n, w = g.hand_frame(1)
        q = self.named['idle']['frames'][0][g.IDS['claws_L']][3:7]
        self.assertGreater(abs(q[3]), .9)

    def test_middle_frame_key_poses(self):
        for name in ('slice', 'snatch', 'recoil'):
            mid, top = middle_travel(self.named[name])
            self.assertGreater(mid, 7 if name != 'recoil' else 4.5, name)
            self.assertGreater(mid, .8*top, name)
        # Slice rakes the right claws far forward; snatch reaches low with both hands.
        T = g.matrices(self.named['slice']['frames'][12])
        self.assertGreater(T[g.IDS['claws_R']][0][0], 14*K)
        T = g.matrices(self.named['snatch']['frames'][12])
        for side in ('L', 'R'):
            self.assertGreater(T[g.IDS['claws_'+side]][0][0], 11*K)
            self.assertLess(T[g.IDS['claws_'+side]][0][2], 22*K)

    def test_death_ends_limp_on_the_floor(self):
        frames = self.named['death']['frames']
        # The sampled middle frame is still mid-fall: pitched far over, not yet down.
        T = g.matrices(frames[len(frames)//2])
        self.assertGreater(T[g.IDS['pelvis']][0][2], 6*K); self.assertGreater(T[g.IDS['head']][0][2], 6*K)
        self.assertGreater(T[g.IDS['head']][0][0]-T[g.IDS['pelvis']][0][0], 6*K)
        end = g.deform(self.v, self.w, frames[-1])
        self.assertLess(min(p[2] for p in end), .4)
        body = [p for p, o in zip(end, self.owner) if o == 'Connected_skin']
        self.assertLess(sorted(p[2] for p in body)[len(body)//2], 4.5*K)
        T = g.matrices(frames[-1])
        for bone in ('pelvis', 'chest', 'head', 'tail_3', 'claws_L', 'claws_R'):
            self.assertLess(T[g.IDS[bone]][0][2], 5*K, bone)
        # Only the rigid horns may stand clear of a body lying within 10 units of the floor.
        self.assertLess(max(p[2] for p, o in zip(end, self.owner) if not o.startswith('horn')), 10*K)
        self.assertLess(max(p[2] for p in end), 18.5*K)
        self.assertEqual(frames[-1], g.pose('death', 1))

    def test_no_degenerate_or_inverted_accessories(self):
        rest_normals = {}
        for c in self.clips:
            for frame in (c['frames'][0], c['frames'][len(c['frames'])//2], c['frames'][-1]):
                d = g.deform(self.v, self.w, frame)
                for a, b, cc in self.tri:
                    e1 = [d[b][k]-d[a][k] for k in range(3)]; e2 = [d[cc][k]-d[a][k] for k in range(3)]
                    cr = (e1[1]*e2[2]-e1[2]*e2[1], e1[2]*e2[0]-e1[0]*e2[2], e1[0]*e2[1]-e1[1]*e2[0])
                    self.assertGreater(sum(x*x for x in cr), 0)

    def test_atlas_roles(self):
        self.assertTrue({m.role(p.name) for p in self.parts} <= set(m.ROLES) | {'skin'})
        for u, v in self.uv: self.assertTrue(0 <= u <= 1 and 0 <= v <= 1)
        skin = self.parts[0]
        self.assertLessEqual(len(skin.faces), m.SKIN_ISLANDS)
        self.assertTrue(all(u < .5 for u, v in skin.uv))
        self.assertTrue(all(u > .5 for p in self.parts[1:] for u, v in p.uv))

    def test_runtime_and_material_bytes(self):
        data = iqm.encode(self.v, self.n, self.uv, self.tri, self.w, g.BONES, self.clips, self.bounds,
                          mesh_label='Project_Broom_imp', material_path=g.SKIN)
        self.assertEqual(data, (g.ROOT/g.MODEL).read_bytes())
        skin = g.texture_bytes()
        self.assertEqual(skin, (g.ROOT/'mod/BrogueDoom'/g.SKIN).read_bytes())
        from PIL import Image
        import io
        im = Image.open(io.BytesIO(skin)).convert('RGB')
        def px(u, v): return im.getpixel((int(u*m.SIZE), int((1-v)*m.SIZE)))
        # Ivory horns and amber eyes are far lighter than the maroon-black leg fur.
        horn = self.parts[[p.name for p in self.parts].index('horn_L')]
        self.assertGreater(sum(px(*horn.uv[len(horn.uv)//2])), 450)
        self.assertLess(sum(m.FUR), 60)


if __name__ == '__main__': unittest.main()

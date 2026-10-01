"""Centaur anatomy, planted hooves, bow grip/string/arrow, limp fall and bytes."""
import collections
import math
import unittest
from . import centaur_animation as g, centaur_materials as m, iqm
from .skeletal import rotate


def world_point(world, bone, rest_point):
    pos, q = world[g.IDS[bone]]
    return tuple(a+b for a, b in zip(pos, rotate(q, [x-y for x, y in zip(rest_point, g.REST[g.IDS[bone]])])))


class CentaurTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts, cls.v, cls.n, cls.uv, cls.tri, cls.w = g.geometry()
        cls.clips, cls.bounds = g.animation_data(cls.v, cls.w)
        cls.source = {p.name: p for p in g.build_parts()}

    def frames(self):
        for c in self.clips:
            count = len(c['frames'])
            for i, frame in enumerate(c['frames']):
                yield c['name'], i/(count if c['loop'] else count-1), frame

    def test_connected_closed_skin_and_seams(self):
        p = self.parts[0]
        ids = p.skin_topology
        edges = collections.Counter()
        graph = {i: set() for i in ids}
        reps = {}
        for face in p.faces:
            for a, b in zip(face, face[1:]+face[:1]):
                a, b = ids[a], ids[b]
                self.assertNotEqual(a, b)
                edges[tuple(sorted((a, b)))] += 1
                graph[a].add(b)
                graph[b].add(a)
        self.assertEqual(set(edges.values()), {2})
        seen = {ids[0]}
        todo = [ids[0]]
        while todo:
            for i in graph[todo.pop()]:
                if i not in seen:
                    seen.add(i)
                    todo.append(i)
        self.assertEqual(seen, set(ids))
        for i, key in enumerate(ids):
            if key in reps:
                j = reps[key]
                self.assertEqual(self.v[i], self.v[j])
                self.assertEqual(self.w[i], self.w[j])
                self.assertLess(math.dist(self.n[i], self.n[j]), 1e-8)
            reps[key] = i
        # One skin carries both the equine legs and the human arms and head.
        used = {g.BONES[b][0] for row in p.skin_weights for b, weight in row if weight > .01}
        for side in ('L', 'R'):
            for joint in ('upper', 'lower', 'end'):
                for limb in ('arm', 'fore', 'hind'):
                    self.assertIn(f'{limb}_{side}_{joint}', used)
        for bone in ('pelvis', 'barrel', 'withers', 'waist', 'chest', 'neck', 'head', 'tail_0'):
            self.assertIn(bone, used)
        for row in self.w:
            self.assertAlmostEqual(sum(weight for b, weight in row), 1)
            self.assertLessEqual(len(row), 4)
        self.assertLessEqual(len(p.faces), 12288)  # atlas island capacity

    def test_six_roles_centered_clearance_and_no_floor_compensation(self):
        self.assertEqual([c['name'] for c in self.clips], ['idle', 'trot', 'shoot', 'rear_shot', 'flinch', 'fall'])
        self.assertEqual([c['loop'] for c in self.clips], [True, True, False, False, False, False])
        for b in self.bounds:
            self.assertGreaterEqual(b[0], -32)
            self.assertGreaterEqual(b[1], -32)
            self.assertLessEqual(b[3], 32)
            self.assertLessEqual(b[4], 32)
            self.assertGreater(b[2], .07)
        for name, t, f in self.frames():
            self.assertEqual(f, g.pose(name, t), 'Automatic floor compensation masks an anatomy/IK defect')
            self.assertTrue(all(row[7:] == (1, 1, 1) for row in f))
        for c in self.clips:
            if c['loop']:
                a = g.deform(self.v, self.w, g.pose(c['name'], 0))
                b = g.deform(self.v, self.w, g.pose(c['name'], 1))
                self.assertLess(max(math.dist(p, q) for p, q in zip(a, b)), 1e-8)
        rest = g.deform(self.v, self.w, g.pose('idle', 0))
        for c in self.clips[2:5]:
            end = g.deform(self.v, self.w, c['frames'][-1])
            self.assertLess(max(math.dist(p, q) for p, q in zip(rest, end)), .6, c['name']+' must recover')

    def test_planted_level_non_sliding_hooves(self):
        keys = [f'{limb}_{side}' for limb in ('fore', 'hind') for side in ('L', 'R')]
        for name, t, f in self.frames():
            world = g.matrices(f)
            planted = set()
            for key in keys:
                pos, q = world[g.IDS[key+'_end']]
                rest = g.REST[g.IDS[key+'_end']]
                if abs(pos[2]-rest[2]) < 1e-6:
                    planted.add(key)
                    self.assertLess(max(abs(c) for c in q[:3]), 1e-6, 'planted hoof must stay level')
                    if name != 'trot':  # stationary clips: planted hooves do not slide
                        self.assertLess(math.dist(pos, rest), 1e-6, (name, t, key))
            if name in ('shoot', 'flinch'):
                self.assertEqual(len(planted), 4, (name, t))
            elif name == 'idle':
                self.assertGreaterEqual(planted, {'fore_L', 'fore_R', 'hind_L'})
                if t == 0:
                    self.assertEqual(len(planted), 4)
            elif name == 'trot':
                self.assertGreaterEqual(len(planted), 2, t)
                for pair in (('fore_L', 'hind_R'), ('fore_R', 'hind_L')):
                    self.assertEqual(pair[0] in planted, pair[1] in planted, 'diagonal pairs move together')
            elif name == 'rear_shot':
                self.assertGreaterEqual(planted, {'hind_L', 'hind_R'})
            elif name == 'fall' and t == 0:
                self.assertEqual(len(planted), 4)

    def test_bow_gripped_and_string_attached_in_every_frame(self):
        bow = g.IDS['bow']
        for name, t, f in self.frames():
            self.assertEqual(f[bow][:7], (*g.BONES[bow][2], 0, 0, 0, 1), name)
        gx, gy, gz = g.GRIP
        angles = set()
        for i in range(4):
            for x, y, z in self.source[f'hand_L_finger{i}'].vertices:
                self.assertLess(math.hypot(x-gx, y-gy), 2.8)
                angles.add(int(math.degrees(math.atan2(y-gy, x-gx))//30))
        self.assertGreaterEqual(len(angles), 10)  # fingers wrap at least 300 degrees
        # String ends stay on the limb tips in every pose, including the draw.
        src = [p for p in g.build_parts()]
        for tag in ('top', 'bottom'):
            string = next(p for p in src if p.name == f'bow_string_{tag}')
            limb = next(p for p in src if p.name == f'bow_limb_{tag}')
            anchor = max(string.vertices, key=lambda v: abs(v[2]-gz))
            anchor_w = g.weights(string, anchor, None)
            limb_w = [g.weights(limb, v, None) for v in limb.vertices]
            self.assertEqual(anchor_w, [(g.IDS['bow_'+tag], 1)])
            for name, t, f in self.frames():
                a = g.deform([anchor], [anchor_w], f)[0]
                pts = g.deform(limb.vertices, limb_w, f)
                self.assertLess(min(math.dist(a, p) for p in pts), 1.0, (name, t, tag))

    def test_cosmetic_arrow_rides_string_then_returns_to_quiver(self):
        arrow, string = g.IDS['arrow'], g.IDS['bow_string']
        drawn = 0
        for name in ('shoot', 'rear_shot'):
            clip = next(c for c in self.clips if c['name'] == name)
            count = len(clip['frames'])
            for i, f in enumerate(clip['frames']):
                t = i/(count-1)
                world = g.matrices(f)
                if t < .16 or t >= .70:
                    self.assertEqual(f[arrow][:7], (*g.BONES[arrow][2], 0, 0, 0, 1), (name, t))
                    self.assertEqual(f[string][:3], g.BONES[string][2], (name, t))
                if .42 <= t < .70:
                    drawn += 1
                    self.assertLess(math.dist(world[arrow][0], world[string][0]), 1e-6)
                    tip = world_point(world, 'arrow', [a+b*g.ARROW_LEN for a, b in zip(g.NOCK_REST, g.quiver_axis())])
                    self.assertLess(abs(tip[0]), 32)
        self.assertGreater(drawn, 12)
        # Full draw brings the nock back to the anchor under the cheek.
        world = g.matrices(g.pose('shoot', .64))
        anchor = world_point(world, 'head', [a+b for a, b in zip(g.REST[g.IDS['head']], g.ANCHOR)])
        self.assertLess(math.dist(world[string][0], anchor), .1)

    def test_limp_fall_on_side(self):
        frame = g.pose('fall', 1)
        world = g.matrices(frame)
        q = world[g.IDS['barrel']][1]
        side_up = rotate(q, (0, 1, 0))
        self.assertGreater(side_up[2], .95, 'horse lies on its right side')
        self.assertLess(world[g.IDS['barrel']][0][2], 14)
        self.assertLess(world[g.IDS['head']][0][2], 14)
        for side in ('L', 'R'):
            self.assertLess(world[g.IDS[f'arm_{side}_end']][0][2], 8)  # both hands lie low
        settled = g.deform(self.v, self.w, frame)
        self.assertLess(max(p[2] for p in settled), 30)
        bow_axis = rotate(world[g.IDS['bow']][1], (0, 0, 1))
        self.assertLess(abs(bow_axis[2]), .35, 'the bow lies flat on the floor')
        # Not a kneel: every hoof is lifted off its standing support.
        for limb in ('fore', 'hind'):
            for side in ('L', 'R'):
                pos, q = world[g.IDS[f'{limb}_{side}_end']]
                self.assertGreater(max(abs(c) for c in q[:3]), .3)

    def test_continuous_pigment_and_accessory_isolation(self):
        self.assertEqual({m.role(p.name) for p in g.build_parts()}, set(m.ROLES))
        for p in self.parts:
            for u, v in p.uv:
                self.assertTrue(0 <= u <= 1 and 0 <= v <= 1)
                # Accessories own the top-right quadrant; skin islands never enter it.
                self.assertEqual(u > .5 and v > .5, p.name != 'Connected_skin', p.name)
        p = self.parts[0]
        self.assertEqual(len(p.vertices), len(p.faces)*3)
        self.assertEqual(len({tuple(p.uv[i] for i in f) for f in p.faces}), len(p.faces))
        bright = lambda c: sum(c)/3
        flank = m.pigment((-8, 10, 33), (0, 1, 0), 0)
        self.assertLess(bright(m.pigment((10, 6.5, 8), (0, 1, 0), 0)), bright(flank)-40, 'dark points on the lower legs')
        self.assertLess(bright(m.pigment((-8, 0, 42.3), (0, 0, 1), 0)), bright(flank)-20, 'dorsal stripe')
        # The join blends by the continuous human fraction, with no hard step.
        steps = [m.pigment((13.5, 7, 46), (0, 1, 0), h/10) for h in range(11)]
        self.assertLess(max(math.dist(a, b) for a, b in zip(steps, steps[1:])), 40)
        self.assertGreater(math.dist(steps[0], steps[-1]), 20)

    def test_runtime_and_material_bytes(self):
        data = iqm.encode(self.v, self.n, self.uv, self.tri, self.w, g.BONES, self.clips, self.bounds,
                          mesh_label='Project_Broom_centaur', material_path=g.SKIN)
        self.assertEqual(data, (g.ROOT/'mod/BrogueDoom/models/monsters/35_centaur.iqm').read_bytes())
        self.assertEqual(g.texture_bytes(), (g.ROOT/'mod/BrogueDoom'/g.SKIN).read_bytes())


if __name__ == '__main__':
    unittest.main()

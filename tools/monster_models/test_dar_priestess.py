"""Dar priestess: fused anatomy, held/released staff, relic chains, bounds and bytes."""
import collections
import math
import unittest
from . import dar_priestess_animation as g, dar_priestess_materials as m, iqm


class DarPriestessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts, cls.v, cls.n, cls.uv, cls.tri, cls.w = g.geometry()
        cls.clips, cls.bounds = g.animation_data(cls.v, cls.w)
        cls.source = g.build_parts()

    def phases(self):
        for name, count, fps, loop in g.CLIPS:
            for i in range(count):
                yield name, i, i/(count if loop else count-1)

    def test_connected_closed_skin_and_seams(self):
        p = self.parts[0]
        ids = p.skin_topology
        edges = collections.Counter()
        graph = {i: set() for i in ids}
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
        reps = {}
        for i, key in enumerate(ids):
            if key in reps:
                j = reps[key]
                self.assertEqual(self.v[i], self.v[j])
                self.assertEqual(self.w[i], self.w[j])
            reps[key] = i
        used = {g.BONES[b][0] for row in self.w for b, weight in row if weight > .01}
        for limb in ('arm', 'leg'):
            for side in ('L', 'R'):
                for joint in ('upper', 'lower', 'end'):
                    self.assertIn(f'{limb}_{side}_{joint}', used)

    def test_weights_normalized_and_bounded(self):
        for row in self.w:
            self.assertLessEqual(len(row), 4)
            self.assertAlmostEqual(sum(weight for b, weight in row), 1, places=5)
        for p in self.source:
            if g.CONNECTED_SKIN(p.name):
                continue
            for v, u in zip(p.vertices, p.uv):
                row = g.weights(p, v, u)
                self.assertLessEqual(len(row), 4)
                self.assertAlmostEqual(sum(w for b, w in row), 1, places=6)

    def test_six_roles_centered_clearance_and_no_floor_compensation(self):
        self.assertEqual([c['loop'] for c in self.clips], [True, True, False, False, False, False])
        for b in self.bounds:
            self.assertGreaterEqual(b[0], -32)
            self.assertGreaterEqual(b[1], -32)
            self.assertLessEqual(b[3], 32)
            self.assertLessEqual(b[4], 32)
            self.assertGreater(b[2], .07)
        for c in self.clips:
            for i, f in enumerate(c['frames']):
                raw = g.pose(c['name'], i/(len(c['frames']) if c['loop'] else len(c['frames'])-1))
                self.assertEqual(f, raw, 'Automatic floor compensation masks an anatomy/IK defect')
                self.assertTrue(all(row[7:] == (1, 1, 1) for row in f))
            if c['loop']:
                a = g.deform(self.v, self.w, g.pose(c['name'], 0))
                b = g.deform(self.v, self.w, g.pose(c['name'], 1))
                self.assertLess(max(math.dist(x, y) for x, y in zip(a, b)), 1e-8)
        settled = g.deform(self.v, self.w, g.pose('fall', 1))
        body = [p for p, row in zip(settled, self.w) if not any(g.BONES[b][0] in ('staff', 'charms') for b, w in row)]
        self.assertLess(max(p[2] for p in body), 36, 'death must read collapsed, not a standing crouch')

    def test_staff_held_then_released_flat(self):
        for name, i, t in self.phases():
            m_ = g.matrices(g.pose(name, t))
            staff, hand = m_[g.IDS['staff']], m_[g.IDS['arm_L_end']]
            held = name != 'fall' or i == 0
            if held:
                self.assertLess(math.dist(staff[0], hand[0]), 1e-8, (name, i))
                self.assertLess(min(math.dist(staff[1], hand[1]), math.dist(staff[1], tuple(-x for x in hand[1]))), 1e-8)
            # Charms and the sickle remain on their parents' transforms.
            self.assertLess(math.dist(m_[g.IDS['sickle']][0], m_[g.IDS['arm_R_end']][0]), 1e-8)
        final = g.matrices(g.pose('fall', 1))[g.IDS['staff']]
        shaft = g.rotate(final[1], (0, 0, 1))
        ring_normal = g.rotate(final[1], (1, 0, 0))
        self.assertLess(abs(shaft[2]), 1e-6)
        self.assertGreater(ring_normal[2], .999)

    def test_relics_hang_on_chains_from_the_girdle(self):
        names = {p.name for p in self.source}
        for i, (a, kind, drop) in enumerate(g.RELICS):
            self.assertIn(f'relic_{i}_chain', names)
            self.assertEqual(g.BONES[g.IDS[f'relic_{i}']][1], g.IDS['pelvis'])
            chain = next(p for p in self.source if p.name == f'relic_{i}_chain')
            top = max(chain.vertices, key=lambda v: v[2])
            self.assertLess(math.dist(top[:2], g.REST[g.IDS[f'relic_{i}']][:2]), 1.2)
        self.assertEqual(len([n for n in names if n.startswith('hand_R_finger')]), 4)
        self.assertEqual(len([n for n in names if n.startswith('hand_L_finger')]), 4)

    def test_continuous_skin_atlas_and_accessory_isolation(self):
        self.assertTrue({m.role(p.name) for p in self.source} <= set(m.ROLES))
        for p in self.parts:
            for u, v in p.uv:
                self.assertTrue(0 <= u <= 1 and 0 <= v <= 1)
                self.assertLess(u, .5) if p.name == 'Connected_skin' else self.assertGreater(u, .5)
        p = self.parts[0]
        self.assertEqual(len(p.vertices), len(p.faces)*3)
        self.assertEqual(len({tuple(p.uv[i] for i in f) for f in p.faces}), len(p.faces))
        rects = list(m.RECTS.values())
        for i, a in enumerate(rects):
            for b in rects[i+1:]:
                gap = max(b[0]-a[2], a[0]-b[2], b[1]-a[3], a[1]-b[3])
                self.assertGreaterEqual(gap, 16)

    def test_runtime_and_material_bytes(self):
        data = iqm.encode(self.v, self.n, self.uv, self.tri, self.w, g.BONES, self.clips, self.bounds,
                          mesh_label='Project_Broom_dar_priestess', material_path=g.SKIN)
        self.assertEqual(data, (g.ROOT/g.MODEL).read_bytes())
        self.assertEqual(g.texture_bytes(), (g.ROOT/'mod/BrogueDoom'/g.SKIN).read_bytes())


if __name__ == '__main__':
    unittest.main()

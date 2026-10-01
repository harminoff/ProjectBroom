"""Dar battlemage: fused anatomy, ember key isolation, cloth, bounds and bytes."""
import collections
import math
import re
import unittest
from . import dar_battlemage_animation as g, dar_battlemage_materials as m, iqm


class DarBattlemageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts, cls.v, cls.n, cls.uv, cls.tri, cls.w = g.geometry()
        cls.clips, cls.bounds = g.animation_data(cls.v, cls.w)
        cls.source = g.build_parts()

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
        used = {g.BONES[b][0] for row in self.w for b, weight in row if weight > .01}
        for limb in ('arm', 'leg'):
            for side in ('L', 'R'):
                for joint in ('upper', 'lower', 'end'):
                    self.assertIn(f'{limb}_{side}_{joint}', used)
        for row in self.w:
            self.assertLessEqual(len(row), 4)
            self.assertAlmostEqual(sum(weight for b, weight in row), 1, places=5)

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
        self.assertLess(max(p[2] for p in settled), 18, 'death must lie on the floor')

    def test_supports_and_attachments(self):
        for name, count, fps, loop in g.CLIPS:
            for i in range(count):
                t = i/(count if loop else count-1)
                mats = g.matrices(g.pose(name, t))
                if name == 'advance' or (name == 'cut' and i in (0, count-1)):
                    planted = sum(abs(mats[g.IDS[f'leg_{s}_end']][0][2]-2.4) < 1e-7 for s in ('L', 'R'))
                    self.assertGreaterEqual(planted, 1)
                if name == 'cut':
                    # The rear (right) foot stays planted through the lunge.
                    self.assertLess(abs(mats[g.IDS['leg_R_end']][0][2]-2.4), 1e-7)
        # Death ends prone on the floor, not in a crouch: head and pelvis low.
        final = g.matrices(g.pose('fall', 1))
        self.assertLess(final[g.IDS['head']][0][2], 16)
        self.assertLess(final[g.IDS['pelvis']][0][2], 12)
        self.assertEqual(g.BONES[g.IDS['tome']][1], g.IDS['pelvis'])
        self.assertEqual(g.BONES[g.IDS['topknot']][1], g.IDS['head'])
        names = {p.name for p in self.source}
        for side in ('L', 'R'):
            self.assertEqual(len([n for n in names if n.startswith(f'hand_{side}_finger')]), 4)
            self.assertIn(f'bracer_{side}', names)

    def test_ember_key_is_confined_to_eyes_and_hands(self):
        # Every accessory role except the ember iris stays outside the key.
        for name, (x0, y0, x1, y1) in m.RECTS.items():
            samples = [m.shade(name, u/20, v/20) for u in range(21) for v in range(21)]
            if name == 'ember':
                self.assertTrue(all(m.ember_key(c) for c in samples))
            else:
                self.assertFalse(any(m.ember_key(c) for c in samples), name)
        # Continuous pigment: only vertices near the hands meet the key.
        body = self.parts[0]
        normals = body.normals()
        hot = [v for v, n in zip(body.vertices, normals) if m.ember_key(tuple(round(max(0, min(255, c))) for c in m.pigment(v, n)))]
        self.assertGreater(len(hot), 40)
        for v in hot:
            self.assertLess(min(math.dist(v, c) for c, tip in m.HANDS.values()), 4.8)
        # The shader thresholds are the same numbers as ember_key().
        text = (g.ROOT/'mod/BrogueDoom'/g.SHADER).read_text()
        self.assertEqual(sorted(set(re.findall(r'step\((0\.\d+)', text))), ['0.3', '0.34', '0.86'])
        self.assertNotIn('timer', text.lower())

    def test_continuous_skin_atlas_and_accessory_isolation(self):
        self.assertTrue({m.role(p.name) for p in self.source} <= set(m.ROLES))
        for p in self.parts:
            for u, v in p.uv:
                self.assertTrue(0 <= u <= 1 and 0 <= v <= 1)
                self.assertLess(u, .5) if p.name == 'Connected_skin' else self.assertGreater(u, .5)
        p = self.parts[0]
        self.assertEqual(len(p.vertices), len(p.faces)*3)
        rects = list(m.RECTS.values())
        for i, a in enumerate(rects):
            for b in rects[i+1:]:
                self.assertGreaterEqual(max(b[0]-a[2], a[0]-b[2], b[1]-a[3], a[1]-b[3]), 16)

    def test_runtime_and_material_bytes(self):
        data = iqm.encode(self.v, self.n, self.uv, self.tri, self.w, g.BONES, self.clips, self.bounds,
                          mesh_label='Project_Broom_dar_battlemage', material_path=g.SKIN)
        self.assertEqual(data, (g.ROOT/g.MODEL).read_bytes())
        self.assertEqual(g.texture_bytes(), (g.ROOT/'mod/BrogueDoom'/g.SKIN).read_bytes())


if __name__ == '__main__':
    unittest.main()

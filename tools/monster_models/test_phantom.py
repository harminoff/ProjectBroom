"""Phantom: fused apparition, additive veil binding, bounds, key poses and bytes."""
import collections
import math
import unittest
from pathlib import Path
from . import phantom_animation as g, phantom_materials as m, iqm
from .skeletal_registry import find, PENDING, ROOT


class PhantomTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts, cls.v, cls.n, cls.uv, cls.tri, cls.w = g.geometry()
        cls.clips, cls.bounds = g.animation_data(cls.v, cls.w)
        cls.source = g.build_parts()

    def test_connected_closed_skin_and_seams(self):
        p = self.parts[0]
        self.assertEqual(p.name, 'Connected_skin')
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
        seen, todo = {ids[0]}, [ids[0]]
        while todo:
            for i in graph[todo.pop()]:
                if i not in seen:
                    seen.add(i)
                    todo.append(i)
        self.assertEqual(seen, set(ids))
        used = {g.BONES[b][0] for row in self.w for b, weight in row if weight > .01}
        for bone in ['chest', 'neck', 'head', 'jaw']+[f'tail_{i}' for i in range(5)]+[f'arm_{s}_{j}' for s in 'LR' for j in ('upper', 'lower', 'end')]:
            self.assertIn(bone, used)

    def test_weights_normalized_and_bounded(self):
        for row in self.w:
            self.assertLessEqual(len(row), 4)
            self.assertAlmostEqual(math.fsum(weight for b, weight in row), 1, places=5)

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
                self.assertEqual(f, raw, 'Automatic floor compensation masks a pose defect')
                self.assertTrue(all(row[7:] == (1, 1, 1) for row in f))
            if c['loop']:
                a = g.deform(self.v, self.w, g.pose(c['name'], 0))
                b = g.deform(self.v, self.w, g.pose(c['name'], 1))
                self.assertLess(max(math.dist(x, y) for x, y in zip(a, b)), 1e-8)

    def test_hovers_and_dissipates_into_a_floor_heap(self):
        # Legless and hovering while alive; death ends as a low heap on the floor.
        self.assertFalse(any(n.startswith('leg_') for n, p, v in g.BONES))
        for name in ('idle', 'drift'):
            for f in range(8):
                d = g.deform(self.v, self.w, g.pose(name, f/8))
                self.assertGreater(min(p[2] for p in d), 1.0)
        settled = g.deform(self.v, self.w, g.pose('dissipate', 1))
        self.assertLess(max(p[2] for p in settled), 26, 'death must end collapsed, not hovering')

    def test_action_key_pose_is_the_middle_frame(self):
        rest = g.deform(self.v, self.w, g.pose('lunge', 0))
        for name, count, fps, loop in g.CLIPS[2:]:
            mid = g.deform(self.v, self.w, g.pose(name, (count//2)/(count-1)))
            first = g.deform(self.v, self.w, g.pose(name, 0))
            self.assertLess(max(math.dist(a, b) for a, b in zip(first, rest)), 1e-8)
            self.assertGreater(max(math.dist(a, b) for a, b in zip(mid, first)), 12, name)

    def test_signature_parts(self):
        names = {p.name for p in self.source}
        self.assertEqual(len([n for n in names if n.startswith('claw_')]), 10)
        self.assertEqual(len([n for n in names if n.startswith('hair_')]), 5)
        self.assertGreaterEqual(len([n for n in names if n.startswith('drop_')]), 5)
        self.assertFalse(any(k in n for n in names for k in ('hood', 'sword', 'foot', 'leg')))

    def test_island_atlas_and_skin_paint(self):
        self.assertLessEqual(len(self.tri), m.GRID*m.GRID)
        islands = set()
        for p in self.parts:
            self.assertEqual(len(p.vertices), len(p.faces)*3)
            for f in p.faces:
                islands.add(tuple(p.uv[i] for i in f))
            for u, v in p.uv:
                self.assertTrue(0 <= u <= 1 and 0 <= v <= 1)
        self.assertEqual(len(islands), len(self.tri))
        self.assertEqual(m.pigment((4.35, 1.3, 57.55), (1, 0, 0), 'Connected_skin', 0), (0.0, 0.0, 0.0), 'painted socket hole')

    def test_profile_and_additive_veil_binding(self):
        row = find('MK_PHANTOM')
        self.assertEqual(row['clips'], [c[0] for c in g.CLIPS])
        self.assertEqual(row['walkFrames'], g.CLIPS[1][1])
        self.assertTrue(row['additiveFlame'])
        self.assertEqual(row['skin'], g.SKIN)
        self.assertEqual('mod/BrogueDoom/models/monsters/'+row['model'], g.MODEL)
        snippet = PENDING/'MK_PHANTOM.gldefs'
        text = snippet.read_text() if snippet.is_file() else (ROOT/'mod/BrogueDoom/GLDEFS').read_text()
        block = text[text.index('material "graphics/BRGPHANT.png"'):]
        self.assertIn('shaders/phantom-veil.fp', block[:block.index('}')])
        shader = (ROOT/'mod/BrogueDoom/shaders/phantom-veil.fp').read_text()
        self.assertIn('material.Bright', shader)
        for forbidden in ('uLightLevel', 'random', 'AddLight'):
            self.assertNotIn(forbidden, shader)

    def test_runtime_and_material_bytes(self):
        data = iqm.encode(self.v, self.n, self.uv, self.tri, self.w, g.BONES, self.clips, self.bounds,
                          mesh_label='Project_Broom_phantom', material_path=g.SKIN)
        self.assertEqual(data, (g.ROOT/g.MODEL).read_bytes())
        self.assertEqual(g.texture_bytes(), (g.ROOT/'mod/BrogueDoom'/g.SKIN).read_bytes())


if __name__ == '__main__':
    unittest.main()

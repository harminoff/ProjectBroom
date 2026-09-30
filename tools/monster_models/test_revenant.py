"""Revenant: fused shroud/hood/sleeves, planted stalk, seated collapse, key poses and bytes."""
import collections
import math
import unittest
from . import revenant_animation as g, revenant_materials as m, iqm
from .skeletal_registry import find


class RevenantTests(unittest.TestCase):
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
        for limb in ('arm', 'leg'):
            for side in 'LR':
                for joint in ('upper', 'lower', 'end'):
                    self.assertIn(f'{limb}_{side}_{joint}', used)

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

    def test_planted_feet_and_floor_collapse(self):
        for name, count, fps, loop in g.CLIPS:
            for i in range(count):
                t = i/(count if loop else count-1)
                mats_ = g.matrices(g.pose(name, t))
                planted = sum(abs(mats_[g.IDS[f'leg_{s}_end']][0][2]-g.ANKLE) < 1e-6 for s in 'LR')
                self.assertGreaterEqual(planted, 1 if name == 'stalk' else 2, (name, i))
        settled = g.deform(self.v, self.w, g.pose('fall', 1))
        self.assertLess(max(p[2] for p in settled), 30, 'death must end folded on the floor')

    def test_action_key_pose_is_the_middle_frame(self):
        rest = g.deform(self.v, self.w, g.pose('smash', 0))
        for name, count, fps, loop in g.CLIPS[2:]:
            mid = g.deform(self.v, self.w, g.pose(name, (count//2)/(count-1)))
            first = g.deform(self.v, self.w, g.pose(name, 0))
            self.assertLess(max(math.dist(a, b) for a, b in zip(first, rest)), 1e-8)
            self.assertGreater(max(math.dist(a, b) for a, b in zip(mid, first)), 12, name)
        smash = self.clips[2]['frames']
        top = max(p[2] for p in g.deform(self.v, self.w, smash[len(smash)//2]))
        self.assertGreater(top, 72, 'overhead raise must lift the silhouette')

    def test_shredded_hem_hides_feet_and_fades(self):
        names = [p.name for p in self.source]
        strips = [p for p in self.source if p.name.startswith('rag_hem_')]
        self.assertGreaterEqual(len(strips), 30)
        self.assertFalse(any(n.startswith(('foot', 'cord')) for n in names))
        for p in strips:
            self.assertGreater(min(v[2] for v in p.vertices), 1.0)
        base = sum(m.pigment((0, 9, 14), (0, 1, 0), 'rag_hem_0_0', 0))
        tip = sum(m.pigment((0, 9, 2), (0, 1, 0), 'rag_hem_0_0', 0))
        self.assertLess(tip, .4*base, 'hem strips must fade toward their tips')
        # Stooped rest pose: the skull sits forward of and below the mantle hump.
        mantle = next(p for p in self.source if p.name == 'mantle')
        skull = next(p for p in self.source if p.name == 'skull_cranium')
        self.assertGreater(max(v[2] for v in mantle.vertices), max(v[2] for v in skull.vertices))
        self.assertGreater(min(v[0] for v in skull.vertices), min(v[0] for v in mantle.vertices)+3)

    def test_skull_sits_inside_the_hood_and_hands_hang_from_cuffs(self):
        by = {p.name: p for p in self.source}
        hood = by['hood']
        cranium = by['skull_cranium']
        for axis_ in range(3):
            self.assertLess(min(v[axis_] for v in hood.vertices), min(v[axis_] for v in cranium.vertices))
        self.assertGreater(max(v[2] for v in hood.vertices), max(v[2] for v in cranium.vertices))
        self.assertEqual(len([n for n in by if n.startswith('nail_')]), 10)
        self.assertFalse(any(k in n for n in by for k in ('wing', 'sword', 'tail', 'claw_')))
        for p in self.source:
            if p.name.startswith(('hand_', 'nail_')):
                side = 'L' if p.vertices[0][1] > 0 else 'R'
                self.assertTrue(all(g.weights(p, v, u) == [(g.IDS[f'arm_{side}_end'], 1)] for v, u in zip(p.vertices, p.uv)))

    def test_island_atlas_and_value_range(self):
        self.assertLessEqual(len(self.tri), m.GRID*m.GRID)
        islands = set()
        for p in self.parts:
            self.assertEqual(len(p.vertices), len(p.faces)*3)
            for f in p.faces:
                islands.add(tuple(p.uv[i] for i in f))
            for u, v in p.uv:
                self.assertTrue(0 <= u <= 1 and 0 <= v <= 1)
        self.assertEqual(len(islands), len(self.tri))
        skull = sum(m.pigment((7.8, 0, 54.1), (1, 0, 0), 'skull_face', 0))
        cowl = sum(m.pigment((5.2, 0, 59.8), (0, 0, -1), 'Connected_skin', 0))
        self.assertGreater(skull, 4*cowl, 'pale skull must read against the dark cowl')

    def test_profile(self):
        row = find('MK_REVENANT')
        self.assertEqual(row['clips'], [c[0] for c in g.CLIPS])
        self.assertEqual(row['walkFrames'], g.CLIPS[1][1])
        self.assertFalse(row.get('additiveFlame', False))
        self.assertEqual(row['skin'], g.SKIN)
        self.assertEqual('mod/BrogueDoom/models/monsters/'+row['model'], g.MODEL)

    def test_runtime_and_material_bytes(self):
        data = iqm.encode(self.v, self.n, self.uv, self.tri, self.w, g.BONES, self.clips, self.bounds,
                          mesh_label='Project_Broom_revenant', material_path=g.SKIN)
        self.assertEqual(data, (g.ROOT/g.MODEL).read_bytes())
        self.assertEqual(g.texture_bytes(), (g.ROOT/'mod/BrogueDoom'/g.SKIN).read_bytes())


if __name__ == '__main__':
    unittest.main()

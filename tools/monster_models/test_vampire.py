"""Vampire: fused coat/limbs, bat-wing cloak on the arms, key poses, floor collapse and bytes."""
import collections
import math
import unittest
from . import vampire_animation as g, vampire_materials as m, iqm
from .skeletal_registry import find


class VampireTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts, cls.v, cls.n, cls.uv, cls.tri, cls.w = g.geometry()
        cls.clips, cls.bounds = g.animation_data(cls.v, cls.w)
        cls.source = g.build_parts()
        cls.by = {p.name: p for p in cls.source}

    def test_connected_closed_skin(self):
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

    def test_durations_cover_every_action_clip(self):
        row = find('MK_VAMPIRE')
        for (name, count, fps, loop), tics in zip(g.CLIPS, row['durations']):
            if not loop:
                self.assertGreaterEqual(tics, math.ceil(count*35/fps), name)
        self.assertNotIn('visualScale', row)

    def test_planted_feet_and_floor_collapse(self):
        for name, count, fps, loop in g.CLIPS:
            for i in range(count):
                t = i/(count if loop else count-1)
                mats_ = g.matrices(g.pose(name, t))
                planted = sum(abs(mats_[g.IDS[f'leg_{s}_end']][0][2]-g.ANKLE) < 1e-6 for s in 'LR')
                self.assertGreaterEqual(planted, 1 if name == 'prowl' else 2, (name, i))
        settled = g.deform(self.v, self.w, g.pose('collapse', 1))
        self.assertLess(max(p[2] for p in settled), 32, 'death must end collapsed on the floor')

    def test_action_key_pose_is_the_middle_frame(self):
        for name, count, fps, loop in g.CLIPS[2:]:
            mid = g.deform(self.v, self.w, g.pose(name, (count//2)/(count-1)))
            first = g.deform(self.v, self.w, g.pose(name, 0))
            self.assertGreater(max(math.dist(a, b) for a, b in zip(mid, first)), 12, name)
        # The cloak spread is wide and low rather than overhead; the bite lunges low.
        spread = self.clips[3]['frames']
        wide = g.deform(self.v, self.w, spread[len(spread)//2])
        self.assertGreater(max(abs(p[1]) for p in wide), 26)
        self.assertLess(max(p[2] for p in wide), 72)
        bite = self.clips[2]['frames']
        low = g.deform(self.v, self.w, bite[len(bite)//2])
        self.assertLess(max(p[2] for p in low), 52, 'the bite must drop the head low')
        self.assertGreater(max(p[0] for p in low), 24, 'the bite must reach forward')

    def test_cloak_ears_fangs_and_no_opera_collar(self):
        by = self.by
        ribs = [n for n in by if n.startswith('rib_')]
        self.assertEqual(len(ribs), g.CLOAK_SCALLOPS-1)
        # Deep scallops: the hem rises well above the rib points between them.
        self.assertGreater(g.cloak_hem(.5/g.CLOAK_SCALLOPS)-g.cloak_hem(0), 7)
        self.assertEqual(len([n for n in by if n.startswith('fang_')]), 2)
        cranium = by['head_cranium']
        # Ears sweep out and back beyond the skull; the cloak collar stays below the head.
        ears = [v for n, p in by.items() if n.startswith('head_ear') for v in p.vertices]
        self.assertGreater(max(abs(v[1]) for v in ears), max(abs(v[1]) for v in cranium.vertices)+2.5)
        self.assertLess(max(v[2] for v in by['cloak'].vertices), min(v[2] for v in by['head_face'].vertices))
        self.assertLess(max(v[2] for v in by['collar'].vertices), min(v[2] for v in by['head_face'].vertices))
        self.assertFalse(any(k in n for n in by for k in ('medallion', 'staff', 'sword', 'crown', 'hood')))
        # Cloak edges ride the arms: spreading them opens the cloak like a wing.
        spread = self.clips[3]['frames']
        mid = g.deform(self.v, self.w, spread[len(spread)//2])
        rest = g.deform(self.v, self.w, spread[0])
        cloak = [i for i, row in enumerate(self.w) if any(b == g.IDS['arm_L_lower'] for b, w in row)]
        self.assertTrue(cloak)
        self.assertGreater(max(abs(p[1]) for p in mid), max(abs(p[1]) for p in rest)+8)

    def test_predatory_idle_and_outboard_knees(self):
        for f in range(40):
            m_ = g.matrices(g.pose('idle', f/40))
            for side in 'LR':
                wrist = m_[g.IDS[f'arm_{side}_end']][0]
                self.assertGreater(wrist[2], 30, 'claws half-raised, not hanging')
                self.assertGreater(wrist[0], 5, 'claws held out in front')
        for f in range(32):
            m_ = g.matrices(g.pose('prowl', f/32))
            for side, sign in (('L', 1), ('R', -1)):
                self.assertGreater(sign*m_[g.IDS[f'leg_{side}_lower']][0][1], 3.5, (f, side))

    def test_pale_head_reads_against_dark_cloth(self):
        face = sum(m.pigment((5, 1.6, 56), (1, 0, 0), 'head_face', 0))
        cloak = sum(m.pigment((-8, 0, 30), (-1, 0, 0), 'cloak', 0))
        coat = sum(m.pigment((3.8, 2, 38), (1, 0, 0), 'Connected_skin', 0))
        self.assertGreater(face, 2.5*cloak)
        self.assertGreater(face, 1.8*coat)
        # Painted form: hollow cheeks and sockets are darker than the lit cheekbone.
        ridge = sum(m.pigment((4.6, 1.95, 56.45), (1, 0, 0), 'head_face', 0))
        hollow = sum(m.pigment((4.6, 1.75, 55.25), (1, 0, 0), 'head_face', 0))
        socket = sum(m.pigment((5.0, 1.05, 57.05), (1, 0, 0), 'head_face', 0))
        self.assertGreater(ridge, 1.4*hollow)
        self.assertGreater(ridge, 2*socket)
        # A crimson rim separates the cloak edge from dark walls.
        rim = m.pigment((-8.4, 12.3, 10.2), (-.5, .8, 0), 'cloak', 0)
        self.assertGreater(rim[0], 2*rim[1])
        self.assertGreater(rim[0], 80)
        iris = m.pigment((5.4, 1, 57), (1, 0, 0), 'iris_1', 0)
        self.assertGreater(iris[0], 3*iris[1], 'red painted irises, not emissive')

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

    def test_profile(self):
        row = find('MK_VAMPIRE')
        self.assertEqual(row['clips'], [c[0] for c in g.CLIPS])
        self.assertEqual(row['walkFrames'], g.CLIPS[1][1])
        self.assertEqual(row['skin'], g.SKIN)
        self.assertEqual('mod/BrogueDoom/models/monsters/'+row['model'], g.MODEL)
        self.assertNotIn('ownedFiles', row)

    def test_runtime_and_material_bytes(self):
        data = iqm.encode(self.v, self.n, self.uv, self.tri, self.w, g.BONES, self.clips, self.bounds,
                          mesh_label='Project_Broom_vampire', material_path=g.SKIN)
        self.assertEqual(data, (g.ROOT/g.MODEL).read_bytes())
        self.assertEqual(g.texture_bytes(), (g.ROOT/'mod/BrogueDoom'/g.SKIN).read_bytes())


if __name__ == '__main__':
    unittest.main()

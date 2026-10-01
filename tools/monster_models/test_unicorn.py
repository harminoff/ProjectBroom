"""Unicorn connected skin, clearance, planted hooves, horn thrust, limp fall and bytes."""
import collections
import math
import unittest
from . import unicorn_animation as g, unicorn_materials as m, iqm
from .skeletal import rotate

HOOVES = [f'{limb}_{side}' for limb in ('fore', 'hind') for side in ('L', 'R')]


class UnicornTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts, cls.v, cls.n, cls.uv, cls.tri, cls.w = g.geometry()
        cls.clips, cls.bounds = g.animation_data(cls.v, cls.w)

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
        reps = {}
        for i, key in enumerate(ids):
            if key in reps:
                j = reps[key]
                self.assertEqual(self.v[i], self.v[j])
                self.assertEqual(self.w[i], self.w[j])
            reps[key] = i
        used = {g.BONES[b][0] for row in p.skin_weights for b, weight in row if weight > .01}
        for key in HOOVES:
            for joint in ('upper', 'lower', 'end'):
                self.assertIn(f'{key}_{joint}', used)
        for bone in ('pelvis', 'barrel', 'withers', 'neck_0', 'neck_1', 'neck_2', 'head', 'tail_0'):
            self.assertIn(bone, used)
        for row in self.w:
            self.assertAlmostEqual(sum(weight for b, weight in row), 1)
            self.assertLessEqual(len(row), 4)
        self.assertLessEqual(len(p.faces), 12288)  # atlas island capacity

    def test_six_roles_centered_clearance_and_no_floor_compensation(self):
        self.assertEqual([c['name'] for c in self.clips], ['idle', 'trot', 'gore', 'rear_strike', 'flinch', 'fall'])
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
        for c in self.clips[:2]:
            a = g.deform(self.v, self.w, g.pose(c['name'], 0))
            b = g.deform(self.v, self.w, g.pose(c['name'], 1))
            self.assertLess(max(math.dist(p, q) for p, q in zip(a, b)), 1e-8)
        rest = g.deform(self.v, self.w, g.pose('idle', 0))
        for c in self.clips[2:5]:
            end = g.deform(self.v, self.w, c['frames'][-1])
            self.assertLess(max(math.dist(p, q) for p, q in zip(rest, end)), .6, c['name']+' must recover')

    def test_planted_level_non_sliding_hooves(self):
        for name, t, f in self.frames():
            world = g.matrices(f)
            planted = set()
            for key in HOOVES:
                pos, q = world[g.IDS[key+'_end']]
                rest = g.REST[g.IDS[key+'_end']]
                if abs(pos[2]-rest[2]) < 1e-6:
                    planted.add(key)
                    self.assertLess(max(abs(c) for c in q[:3]), 1e-6, 'planted hoof must stay level')
                    if name != 'trot':
                        self.assertLess(math.dist(pos, rest), 1e-6, (name, t, key))
                elif name != 'fall':
                    self.assertGreater(pos[2], rest[2], (name, t, key, 'a lifted hoof stays above its support'))
            if name in ('gore', 'flinch'):
                self.assertEqual(len(planted), 4, (name, t))
            elif name == 'idle':
                self.assertGreaterEqual(planted, {'fore_L', 'fore_R', 'hind_L'})
                if t == 0:
                    self.assertEqual(len(planted), 4)
            elif name == 'trot':
                self.assertGreaterEqual(len(planted), 2, t)
                for pair in (('fore_L', 'hind_R'), ('fore_R', 'hind_L')):
                    self.assertEqual(pair[0] in planted, pair[1] in planted, 'diagonal pairs move together')
            elif name == 'rear_strike':
                self.assertGreaterEqual(planted, {'hind_L', 'hind_R'})
            elif name == 'fall' and t == 0:
                self.assertEqual(len(planted), 4)
        # The rear's key pose (middle frame) lifts both forelegs high.
        world = g.matrices(g.pose('rear_strike', .5))
        for side in 'LR':
            self.assertGreater(world[g.IDS[f'fore_{side}_end']][0][2], 15)

    def test_horn_thrust_key_pose_and_tip_in_cell(self):
        for name, t, f in self.frames():
            tip = g.horn_tip(g.matrices(f))
            self.assertLess(max(abs(tip[0]), abs(tip[1])), 32, (name, t))
            self.assertGreater(tip[2], .07, (name, t))
        # At the gore's middle frame the horn is levelled into a forward thrust.
        clip = next(c for c in self.clips if c['name'] == 'gore')
        world = g.matrices(clip['frames'][len(clip['frames'])//2])
        direction = rotate(world[g.IDS['head']][1], g.HORN_DIR)
        rest_elevation = math.degrees(math.asin(g.HORN_DIR[2]))
        elevation = math.degrees(math.asin(direction[2]))
        self.assertLess(elevation, rest_elevation-35)
        self.assertGreater(g.horn_tip(world)[0], 24)

    def test_limp_fall_on_side(self):
        frame = g.pose('fall', 1)
        world = g.matrices(frame)
        side_up = rotate(world[g.IDS['barrel']][1], (0, 1, 0))
        self.assertGreater(side_up[2], .95, 'lies on its right side, left flank up')
        self.assertLess(world[g.IDS['barrel']][0][2], 14)
        self.assertLess(world[g.IDS['head']][0][2], 9, 'the head lies on the floor')
        settled = g.deform(self.v, self.w, frame)
        self.assertLess(max(p[2] for p in settled), 30)
        for key in HOOVES:
            pos, q = world[g.IDS[key+'_end']]
            self.assertGreater(max(abs(c) for c in q[:3]), .3, 'every hoof is off its standing support')

    def test_painted_form_and_accessory_isolation(self):
        self.assertEqual({m.role(p.name) for p in g.build_parts()}, set(m.ROLES))
        for p in self.parts:
            for u, v in p.uv:
                self.assertTrue(0 <= u <= 1 and 0 <= v <= 1)
                self.assertEqual(u > .5 and v > .5, p.name != 'Connected_skin', p.name)
        p = self.parts[0]
        self.assertEqual(len(p.vertices), len(p.faces)*3)
        bright = lambda c: sum(c)/3
        back = m.pigment((-2, 0, 42.8), (0, 0, 1))
        flank = m.pigment((-2, 8.5, 34), (0, 1, 0))
        belly = m.pigment((-2, 0, 25.2), (0, 0, -1))
        self.assertGreater(bright(back)-bright(belly), 90, 'painted underside occlusion')
        self.assertGreater(bright(back)-bright(flank), 20, 'the barrel darkens down the flank')
        self.assertLess(bright(m.pigment((9.3, 6.4, 6), (0, 1, 0))), bright(m.pigment((9.3, 6.4, 20), (0, 1, 0)))-40,
                        'lower legs grade darker toward the hooves')

    def test_runtime_and_material_bytes(self):
        data = iqm.encode(self.v, self.n, self.uv, self.tri, self.w, g.BONES, self.clips, self.bounds,
                          mesh_label='Project_Broom_unicorn', material_path=g.SKIN)
        self.assertEqual(data, (g.ROOT/'mod/BrogueDoom/models/monsters/63_unicorn.iqm').read_bytes())
        self.assertEqual(g.texture_bytes(), (g.ROOT/'mod/BrogueDoom'/g.SKIN).read_bytes())


if __name__ == '__main__':
    unittest.main()

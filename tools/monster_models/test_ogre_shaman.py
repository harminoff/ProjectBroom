"""Ogre shaman anatomy, gripped staff, planted supports, limp collapse and bytes."""
import collections
import math
import unittest
from . import ogre_shaman_animation as g, ogre_shaman_materials as m, iqm
from .skeletal import rotate


class OgreShamanTests(unittest.TestCase):
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
        used = {g.BONES[b][0] for row in self.w for b, weight in row if weight > .01}
        for limb in ('arm', 'leg'):
            for side in ('L', 'R'):
                for joint in ('upper', 'lower', 'end'):
                    self.assertIn(f'{limb}_{side}_{joint}', used)
        self.assertIn('jaw', used)
        for row in self.w:
            self.assertAlmostEqual(sum(weight for b, weight in row), 1)
            self.assertLessEqual(len(row), 4)
        self.assertLess(len(p.faces), 8192)

    def test_six_roles_centered_clearance_and_no_floor_compensation(self):
        self.assertEqual([c['name'] for c in self.clips],
                         ['idle', 'hobble', 'cudgel', 'chant_strike', 'recoil', 'collapse'])
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
            self.assertLess(max(math.dist(p, q) for p, q in zip(rest, end)), 2.5, c['name']+' must recover')

    def test_staff_stays_in_closed_grip(self):
        staff = g.IDS['staff']
        rest_local = g.BONES[staff][2]
        for name, t, f in self.frames():
            self.assertEqual(f[staff][:7], (*rest_local, 0, 0, 0, 1), name)
        # Four curled fingers and the thumb encircle the staff axis at the grip.
        gx, gy, gz = g.GRIP
        angles = set()
        for i in range(4):
            finger = self.source[f'hand_R_finger{i}']
            for x, y, z in finger.vertices:
                r = math.hypot(x-gx, y-gy)
                self.assertLess(r, 3.1)
                angles.add(int(math.degrees(math.atan2(y-gy, x-gx))//30))
        self.assertGreaterEqual(len(angles), 10)  # at least 300 degrees of wrap
        shaft = self.source['staff_shaft']
        # Unique ring vertices only: each tube ring repeats its seam vertex.
        near = sorted({(x, y, z) for x, y, z in shaft.vertices if abs(z-gz) < 2})
        near = [(x, y) for x, y, z in near]
        self.assertLess(max(math.hypot(x-gx, y-gy) for x, y in near), 1.4)
        centre = [sum(c)/len(near) for c in zip(*near)]
        self.assertLess(math.hypot(centre[0]-gx, centre[1]-gy), .05)
        self.assertGreater(max(v[2] for v in shaft.vertices)-min(v[2] for v in shaft.vertices), 65)
        for part in shaft, self.source['relic_staff_skull']:
            self.assertTrue(all(g.weights(part, v, u) == [(staff, 1)] for v, u in zip(part.vertices, part.uv)))

    def test_planted_supports(self):
        for name, t, f in self.frames():
            world = g.matrices(f)
            planted = 0
            for side in ('L', 'R'):
                pos, q = world[g.IDS[f'leg_{side}_end']]
                if abs(pos[2]-g.REST[g.IDS[f'leg_{side}_end']][2]) < 1e-7:
                    planted += 1
                    self.assertLess(max(abs(c) for c in q[:3]), 1e-7, 'planted sole must stay level')
            if name in ('idle', 'cudgel', 'chant_strike', 'recoil'):
                self.assertEqual(planted, 2, (name, t))
            elif name == 'hobble':
                self.assertGreaterEqual(planted, 1)

    def test_limp_collapse(self):
        frame = g.pose('collapse', 1)
        world = g.matrices(frame)
        z = lambda bone: world[g.IDS[bone]][0][2]
        self.assertLess(z('head'), 20)
        self.assertLess(z('arm_L_end'), 8)
        for side in ('L', 'R'):
            self.assertLess(z(f'leg_{side}_lower'), 8)
        settled = g.deform(self.v, self.w, frame)
        body = [p for p, row in zip(settled, self.w) if all(b != g.IDS['staff'] for b, w in row)]
        self.assertLess(max(p[2] for p in body), 40)  # about half the standing height
        # The released weight rests on the floor: staff tip is down, crown lowered.
        tip_rest = g.bend(g.STAFF_TIP)
        pos, q = world[g.IDS['staff']]
        tip = [a+b for a, b in zip(pos, rotate(q, [x-y for x, y in zip(tip_rest, g.GRIP)]))]
        self.assertLess(tip[2], 1.4)
        top = [a+b for a, b in zip(pos, rotate(q, [x-y for x, y in zip(g.bend(70.5), g.GRIP)]))]
        self.assertLess(top[2], 24)
        self.assertGreater(frame[g.IDS['jaw']][6], -1)  # jaw hangs open
        self.assertLess(frame[g.IDS['jaw']][6], .995)

    def test_continuous_skin_paint_and_accessory_isolation(self):
        self.assertEqual({m.role(p.name) for p in g.build_parts()}, set(m.ROLES))
        for p in self.parts:
            for u, v in p.uv:
                self.assertTrue(0 <= u <= 1 and 0 <= v <= 1)
                self.assertLess(u, .5) if p.name == 'Connected_skin' else self.assertGreater(u, .5)
        p = self.parts[0]
        self.assertEqual(len(p.vertices), len(p.faces)*3)
        self.assertEqual(len({tuple(p.uv[i] for i in f) for f in p.faces}), len(p.faces))
        # Ash paint is placed on front surfaces (eye band, paunch sigil), never
        # smeared through the hump or back by a projection.
        bright = lambda c: sum(c)/3
        skin = bright(m.pigment((-12, 0, 46), (-1, 0, 0)))
        self.assertGreater(bright(m.pigment((12.4, 4.6, 59.3), (1, 0, 0))), skin+40)
        self.assertGreater(bright(m.pigment((9.4, 0, 40.1), (1, 0, 0))), skin+40)
        self.assertLess(abs(bright(m.pigment((-10, 4.6, 36.5), (-1, 0, 0)))-bright(m.pigment((-10, 9, 30), (-1, 0, 0)))), 30)

    def test_runtime_and_material_bytes(self):
        data = iqm.encode(self.v, self.n, self.uv, self.tri, self.w, g.BONES, self.clips, self.bounds,
                          mesh_label='Project_Broom_ogre_shaman', material_path=g.SKIN)
        self.assertEqual(data, (g.ROOT/'mod/BrogueDoom/models/monsters/27_ogre_shaman.iqm').read_bytes())
        self.assertEqual(g.texture_bytes(), (g.ROOT/'mod/BrogueDoom'/g.SKIN).read_bytes())


if __name__ == '__main__':
    unittest.main()

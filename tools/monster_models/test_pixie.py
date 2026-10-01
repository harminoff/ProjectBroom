"""Pixie anatomy, flight gap, wing attachment, limp fall, paint and runtime bytes."""
import collections
import json
import math
import unittest
from . import pixie_animation as g, pixie_materials as m, iqm
from .rat import sub, cross
from .skeletal import rotate


def world_point(world, bone, rest_point):
    pos, q = world[g.IDS[bone]]
    return tuple(a+b for a, b in zip(pos, rotate(q, [x-y for x, y in zip(rest_point, g.REST[g.IDS[bone]])])))


class PixieTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts, cls.v, cls.n, cls.uv, cls.tri, cls.w = g.geometry()
        cls.clips, cls.bounds = g.animation_data(cls.v, cls.w)
        cls.names = [p.name for p in cls.parts for _ in p.vertices]
        cls.posed = {c['name']: [g.deform(cls.v, cls.w, f) for f in c['frames']] for c in cls.clips}

    def frames(self):
        for c in self.clips:
            count = len(c['frames'])
            for i, frame in enumerate(c['frames']):
                yield c['name'], i, i/(count if c['loop'] else count-1), frame

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
                self.assertLess(math.dist(self.n[i], self.n[j]), 1e-8)
            reps[key] = i
        used = {g.BONES[b][0] for row in p.skin_weights for b, weight in row if weight > .01}
        for side in ('L', 'R'):
            for bone in ('arm', 'forearm', 'hand', 'thigh', 'shin', 'foot', 'ear'):
                self.assertIn(f'{bone}_{side}', used)
        for bone in ('pelvis', 'spine', 'chest', 'neck', 'head'):
            self.assertIn(bone, used)
        for row in self.w:
            self.assertAlmostEqual(sum(weight for b, weight in row), 1)
            self.assertLessEqual(len(row), 4)
        self.assertLessEqual(len(p.faces), m.SKIN_ISLANDS)
        # Signature separate anatomy and clothing.
        names = {q.name for q in self.parts}
        for side in ('L', 'R'):
            for part in ('eye_', 'lid_', 'lash_', 'brow_', 'thumb_', 'finger_index_', 'wing_F_', 'wing_H_'):
                self.assertIn(part+side, names)
        self.assertEqual(sum(q.startswith('skirt_petal_') for q in names), 10)
        self.assertEqual(sum(q.startswith('collar_petal_') for q in names), 5)
        self.assertGreaterEqual(sum(q.startswith('hair_lock_') for q in names), 20)
        self.assertIn('pouch', names)

    def test_roles_cell_clearance_hover_gap_and_no_floor_compensation(self):
        self.assertEqual([c['name'] for c in self.clips], ['idle', 'flit', 'poke', 'hex', 'flinch', 'fall'])
        self.assertEqual([c['loop'] for c in self.clips], [True, True, False, False, False, False])
        for b in self.bounds:
            self.assertGreaterEqual(min(b[0], b[1]), -31.5)
            self.assertLessEqual(max(b[3], b[4]), 31.5)
            self.assertGreater(b[2], .07)
        for name, i, t, f in self.frames():
            self.assertEqual(f, g.pose(name, t), 'automatic floor compensation would hide a pose defect')
            self.assertTrue(all(row[7:] == (1, 1, 1) for row in f))
        # The rest mesh and the hover keep the documented 16-unit flight gap.
        self.assertAlmostEqual(min(p[2] for p in self.v), 16.0, delta=.5)
        # The hover bob moves at most one unit around that gap; flitting stays above it.
        for d in self.posed['idle']:
            self.assertGreater(min(p[2] for p in d), 15.)
        for d in self.posed['flit']:
            self.assertGreater(min(p[2] for p in d), 16.)
        for c in self.clips[:2]:
            a, b = g.deform(self.v, self.w, g.pose(c['name'], 0)), g.deform(self.v, self.w, g.pose(c['name'], 1))
            self.assertLess(max(math.dist(p, q) for p, q in zip(a, b)), 1e-8)
        hover = self.posed['idle'][0]
        for c in self.clips[2:5]:
            start, end = self.posed[c['name']][0], self.posed[c['name']][-1]
            self.assertLess(max(math.dist(p, q) for p, q in zip(start, end)), .05, c['name']+' must recover')
            self.assertLess(max(math.dist(p, q) for p, q in zip(start, hover)), 3.5, c['name']+' starts from the hover carry')

    def test_action_key_poses_sit_on_the_sampled_middle_frame(self):
        hover = self.posed['idle'][0]
        def travel(d): return max(math.dist(p, q) for p, q in zip(d, hover))
        for name in ('poke', 'hex', 'flinch'):
            frames = self.posed[name]
            mid = travel(frames[len(frames)//2])
            self.assertGreater(mid, 7, name)
            self.assertGreater(mid, .8*max(travel(d) for d in frames), name)
        # Poke: the right index finger jabs forward at the middle frame.
        c = next(c for c in self.clips if c['name'] == 'poke')
        world = g.matrices(c['frames'][len(c['frames'])//2])
        tip = world_point(world, 'index_R', g.knuckle(-1))
        self.assertGreater(tip[0], 13)

    def test_rigid_accessories_attached_and_no_degenerate_triangles(self):
        rest = [cross(sub(self.v[b], self.v[a]), sub(self.v[c], self.v[a])) for a, b, c in self.tri]
        top = [max(r, key=lambda x: x[1]) for r in self.w]
        rigid = [k for k, (a, b, c) in enumerate(self.tri) if top[a][1] == 1 and not self.names[a].startswith('Connected')]
        skin = [k for k, (a, b, c) in enumerate(self.tri) if self.names[a] == 'Connected_skin']
        for c in self.clips:
            for f, frame in enumerate(c['frames']):
                d = self.posed[c['name']][f]
                world = g.matrices(frame)
                folded = 0
                for k, (a, b, cc) in enumerate(self.tri):
                    cur = cross(sub(d[b], d[a]), sub(d[cc], d[a]))
                    self.assertGreater(sum(x*x for x in cur), 1e-14, (c['name'], f, k))
                for group, limit in ((rigid, 0), (skin, .005*len(skin))):
                    bad = 0
                    for k in group:
                        a, b, cc = self.tri[k]
                        cur = cross(sub(d[b], d[a]), sub(d[cc], d[a]))
                        ref = rotate(world[top[a][0]][1], rest[k])
                        bad += sum(p*q for p, q in zip(ref, cur)) <= 0
                    self.assertLessEqual(bad, limit, (c['name'], f))
                # Wing and finger bones rotate about their fixed roots: never detached.
                for side in ('L', 'R'):
                    for child, parent in ((f'wingF_{side}', 'chest'), (f'wingH_{side}', 'chest'),
                                          (f'index_{side}', f'hand_{side}'), (f'fingers_{side}', f'hand_{side}')):
                        self.assertLess(math.dist(world[g.IDS[child]][0], world_point(world, parent, g.REST[g.IDS[child]])), 1e-9)

    def test_wings_beat_in_flight_and_still_in_death(self):
        sweeps = {}
        for name in ('idle', 'flit'):
            c = next(c for c in self.clips if c['name'] == name)
            angles = [math.degrees(2*math.acos(min(1, abs(f[g.IDS['wingF_L']][6])))) for f in c['frames']]
            sweeps[name] = max(angles)-min(angles)
            self.assertGreater(sweeps[name], 20, name)
        self.assertGreater(sweeps['flit'], sweeps['idle'])
        c = next(c for c in self.clips if c['name'] == 'fall')
        wings = [g.IDS[b] for b in ('wingF_L', 'wingF_R', 'wingH_L', 'wingH_R')]
        tail = c['frames'][int(.78*len(c['frames'])):]
        for f in tail:
            for b in wings:
                self.assertLess(max(abs(x-y) for x, y in zip(f[b][3:7], tail[-1][b][3:7])), 1e-9, 'stilled wings')
        final = self.posed['fall'][-1]
        wing_z = [p[2] for p, name in zip(final, self.names) if name.startswith(('wing_F', 'wing_H'))]
        self.assertLess(max(wing_z), 2.2)

    def test_limp_grounded_fall(self):
        final = self.posed['fall'][-1]
        self.assertLess(max(p[2] for p in final), 8.5)
        self.assertLess(min(p[2] for p in final), .4)
        world = g.matrices(next(c for c in self.clips if c['name'] == 'fall')['frames'][-1])
        for bone in ('pelvis', 'chest', 'head'):
            self.assertLess(world[g.IDS[bone]][0][2], 5, bone)
        # Every body region rests near the floor; none floats above it.
        for prefix in ('skirt_petal', 'hair_cap', 'wing_F', 'wing_H'):
            self.assertLess(min(p[2] for p, n in zip(final, self.names) if n.startswith(prefix)), 1.2, prefix)
        # The middle sampled frame is a limp mid-air drop, not the settled pose.
        middle = self.posed['fall'][len(self.posed['fall'])//2]
        self.assertGreater(min(p[2] for p in middle), 5)

    def test_paint_contrast_and_accessory_isolation(self):
        pale = m.skin_pigment((0.5, 5.5, 30.0), (0, 1, 0), dict(head=0, ear=0, arm=1, hand=0, leg=0, foot=0, torso=0))
        bodice = m.skin_pigment((1.8, 0.4, 33.0), (1, 0, 0), dict(head=0, ear=0, arm=0, hand=0, leg=0, foot=0, torso=1))
        self.assertGreater(sum(pale)/3, 180)
        self.assertLess(sum(bodice)/3, 120)
        self.assertGreater(bodice[1], bodice[0])
        iris = m.shade('eye', .3, .8)
        self.assertGreater(iris[1], iris[0]+60)
        self.assertLess(sum(m.shade('eye', .3, .95))/3, 40)
        self.assertLess(sum(m.shade('lash', 0, 0))/3, 40)
        wing = [m.wing_shade('F', u/20, v/10) for u in range(1, 20) for v in range(1, 10)]
        self.assertGreater(sum(sum(c) for c in wing)/(3*len(wing)), 140)
        # Skin islands stay in the left half; accessories in the right half.
        for p in self.parts:
            for u, v in p.uv:
                self.assertTrue(u < .5 if p.name == 'Connected_skin' else u > .5, p.name)
        profiles = json.loads((g.ROOT/'assets/monsters/skeletal_profiles.json').read_text())['enemies']
        self.assertEqual([r['symbol'] for r in profiles if r['skin'] == g.SKIN], ['MK_PIXIE'])

    def test_runtime_and_material_bytes(self):
        data = iqm.encode(self.v, self.n, self.uv, self.tri, self.w, g.BONES, self.clips, self.bounds,
                          mesh_label='Project_Broom_pixie', material_path=g.SKIN)
        self.assertEqual(data, (g.ROOT/'mod/BrogueDoom/models/monsters/42_pixie.iqm').read_bytes())
        self.assertEqual(g.texture_bytes(), (g.ROOT/'mod/BrogueDoom'/g.SKIN).read_bytes())


if __name__ == '__main__':
    unittest.main()

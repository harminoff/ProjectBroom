"""Lich: fused robe/sleeves, phylactery glow key, crown, key poses, floor collapse and bytes."""
import collections
import math
import unittest
from . import lich_animation as g, lich_materials as m, iqm
from .skeletal_registry import find, PENDING


class LichTests(unittest.TestCase):
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
        row = find('MK_LICH')
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
                self.assertGreaterEqual(planted, 1 if name in ('stride', 'touch') else 2, (name, i))
        settled = g.deform(self.v, self.w, g.pose('crumble', 1))
        self.assertLess(max(p[2] for p in settled), 30, 'death must end collapsed on the floor')

    def test_action_key_pose_is_the_middle_frame(self):
        for name, count, fps, loop in g.CLIPS[2:]:
            mid = g.deform(self.v, self.w, g.pose(name, (count//2)/(count-1)))
            first = g.deform(self.v, self.w, g.pose(name, 0))
            self.assertGreater(max(math.dist(a, b) for a, b in zip(mid, first)), 12, name)
        # The incantation throws the arms wide and low rather than overhead.
        incant = self.clips[3]['frames']
        spread = g.deform(self.v, self.w, incant[len(incant)//2])
        self.assertGreater(max(p[1] for p in spread), 24)
        self.assertLess(min(p[1] for p in spread), -20)
        self.assertLess(max(p[2] for p in spread), 72)
        touch = self.clips[2]['frames']
        reach = g.deform(self.v, self.w, touch[len(touch)//2])
        self.assertGreater(max(p[0] for p in reach), 26, 'the touch must reach far forward')

    def test_regalia_and_phylactery(self):
        by = self.by
        spikes = [n for n in by if n.startswith('crown_spike')]
        self.assertEqual(len(spikes), 9)
        cranium = by['head_cranium']
        self.assertGreater(max(v[2] for p in spikes for v in by[p].vertices), max(v[2] for v in cranium.vertices)+3)
        # Gem hangs on the sternum in front of the robe, below the beard, and
        # the idle left hand is cupped beneath it.
        gem = by['gem']
        self.assertGreater(min(v[0] for v in gem.vertices), m._interp(m.ROBE_ROWS, g.GEM[2], 1)+m._interp(m.ROBE_ROWS, g.GEM[2], 2))
        self.assertGreater(min(v[2] for n, p in by.items() if n.startswith('beard') for v in p.vertices), max(v[2] for v in gem.vertices))
        palm = g.matrices(g.pose('idle', 0))[g.IDS['arm_L_end']][0]
        self.assertLess(math.dist(palm, g.GEM), 8)
        self.assertFalse(any(k in n for n in by for k in ('staff', 'sword', 'wing', 'hood')))

    def test_aged_cope_and_ragged_hem(self):
        # Irregular tatters on the cope hem, and dark folds against faded lit planes.
        lifts = [g.cope_hem(i/44)-3.2*abs(math.sin(math.pi*i/44*5))**1.5 for i in range(45)]
        self.assertGreater(len({round(x, 3) for x in lifts}), 3)
        lit = m.faded((0, 13, 45), (0, 0, 1))
        self.assertLess(max(lit)-min(lit), 45, 'lit cope planes are desaturated, dusty blue')
        values = [sum(m.faded((7*math.cos(a), 14*math.sin(a), 45), (math.cos(a), math.sin(a), 0))) for a in
                  [math.radians(d) for d in range(60, 300, 3)]]
        self.assertGreater(max(values), 2.5*min(values), 'painted fold occlusion')

    def test_glow_key_only_on_gem_and_eyes(self):
        self.assertTrue(m.glow_key(m.pigment((7, 0, 41), (1, 0, 0), 'gem', 0)))
        self.assertTrue(m.glow_key(m.pigment((4, 1, 57), (1, 0, 0), 'glow_eye_1', 0)))
        probes = [(x, y, z) for x in (-8, 0, 6) for y in (-10, 0, 10) for z in (2, 20, 40, 50, 58)]
        normals = [(1, 0, 0), (0, 0, 1), (0, 1, 0), (-1, 0, 0), (.6, .3, .74)]
        for name in ('Connected_skin', 'cope', 'stole', 'crown_band', 'head_face', 'hand_L_palm', 'beard_0',
                     'socket_1', 'tooth_up0', 'nail_L_0', 'cage_0', 'torc'):
            for pt in probes:
                for n in normals:
                    self.assertFalse(m.glow_key(m.pigment(pt, n, name, 0)), (name, pt, n))
        shader = (g.ROOT/'mod/BrogueDoom'/g.SHADER).read_text()
        for token in ('step(0.6, base.r)', 'step(0.86, base.g)', 'step(0.35, base.b)', 'step(0.85, base.b)'):
            self.assertIn(token, shader)
        gldefs = PENDING/'MK_LICH.gldefs'
        text = gldefs.read_text() if gldefs.is_file() else (g.ROOT/'mod/BrogueDoom/GLDEFS').read_text()
        self.assertIn('material "graphics/BRGLICH.png"', text)
        self.assertIn(g.SHADER, text)

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
        gold = sum(m.pigment((2, 0, 60), (1, 0, .3), 'crown_band', 0))
        # Compare with the robe's mean over its folds (lit planes are faded, troughs dark).
        robe = [sum(m.pigment((5.8*math.cos(a), 7.3*math.sin(a), 30), (math.cos(a), math.sin(a), 0), 'Connected_skin', 0))
                for a in [math.radians(d) for d in range(-90, 91, 3)]]
        self.assertGreater(gold, 2*sum(robe)/len(robe), 'gold regalia must stand out from the dark robe')

    def test_profile(self):
        row = find('MK_LICH')
        self.assertEqual(row['clips'], [c[0] for c in g.CLIPS])
        self.assertEqual(row['walkFrames'], g.CLIPS[1][1])
        self.assertEqual(row['skin'], g.SKIN)
        self.assertEqual('mod/BrogueDoom/models/monsters/'+row['model'], g.MODEL)
        self.assertIn('mod/BrogueDoom/'+g.SHADER, row['ownedFiles'])

    def test_runtime_and_material_bytes(self):
        data = iqm.encode(self.v, self.n, self.uv, self.tri, self.w, g.BONES, self.clips, self.bounds,
                          mesh_label='Project_Broom_lich', material_path=g.SKIN)
        self.assertEqual(data, (g.ROOT/g.MODEL).read_bytes())
        self.assertEqual(g.texture_bytes(), (g.ROOT/'mod/BrogueDoom'/g.SKIN).read_bytes())


if __name__ == '__main__':
    unittest.main()

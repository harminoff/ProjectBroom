"""Goblin warlord: connected skin, war gear, grip, clearance, key poses and bytes."""
import collections
import json
import math
import unittest
from . import goblin_chieftan_animation as g, goblin_chieftan_materials as m, iqm
from .skeletal_registry import find


def closed(part):
    edges = collections.Counter()
    for face in part.faces:
        for a, b in zip(face, face[1:]+face[:1]):
            edges[tuple(sorted((tuple(round(c, 6) for c in part.vertices[a]), tuple(round(c, 6) for c in part.vertices[b]))))] += 1
    return set(edges.values()) == {2}


def angle(q): return math.degrees(2*math.acos(min(1, abs(q[3]))))


class GoblinChieftanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts, cls.v, cls.n, cls.uv, cls.tri, cls.w = g.geometry()
        cls.clips, cls.bounds = g.animation_data(cls.v, cls.w)
        cls.source = {p.name: p for p in g.build_parts()}

    def test_connected_closed_skin_and_weights(self):
        p = self.parts[0]; ids = p.skin_topology; edges = collections.Counter(); graph = {i: set() for i in ids}
        for face in p.faces:
            for a, b in zip(face, face[1:]+face[:1]):
                a, b = ids[a], ids[b]; self.assertNotEqual(a, b)
                edges[tuple(sorted((a, b)))] += 1; graph[a].add(b); graph[b].add(a)
        self.assertEqual(set(edges.values()), {2})
        seen = {ids[0]}; todo = [ids[0]]
        while todo:
            for i in graph[todo.pop()]:
                if i not in seen: seen.add(i); todo.append(i)
        self.assertEqual(seen, set(ids))
        reps = {}
        for i, key in enumerate(ids):
            if key in reps:
                j = reps[key]; self.assertEqual(self.v[i], self.v[j]); self.assertEqual(self.w[i], self.w[j])
                self.assertLess(math.dist(self.n[i], self.n[j]), 1e-8)
            reps[key] = i
        used = {g.BONES[b][0] for row in self.w[:len(ids)] for b, weight in row if weight > .01}
        for limb in ('arm', 'leg'):
            for side in ('L', 'R'):
                for joint in ('upper', 'lower', 'end'): self.assertIn(f'{limb}_{side}_{joint}', used)
        for row in self.w:
            self.assertAlmostEqual(sum(weight for b, weight in row), 1, places=6); self.assertLessEqual(len(row), 4)

    def test_war_gear_is_closed_and_rigidly_attached(self):
        for name in ('helm_dome', 'crest', 'cape', 'pennant', 'pauldron_L', 'spear_blade', 'helm_nasal', 'kilt_0'):
            self.assertTrue(closed(self.source[name]), name)
        expected = {'helm_dome': 'head', 'crest': 'head', 'helm_horn_1': 'head', 'mantle': 'spine', 'cape': 'cape',
                    'pauldron_L': 'arm_L_upper', 'bracer_R': 'arm_R_lower', 'belt': 'pelvis', 'trophy_skull': 'pelvis',
                    'spear_shaft': 'spear', 'spear_blade': 'spear', 'pennant': 'pennant', 'jaw_tusk_1': 'jaw'}
        for name, bone in expected.items():
            p = self.source[name]
            self.assertTrue(all(g.weights(p, v, u) == [(g.IDS[bone], 1)] for v, u in zip(p.vertices, p.uv)), name)
        # Taller and heavier than the family goblin (39.2 units) without exceeding one cell.
        rest = [v for p in self.source.values() for v in p.vertices if not p.name.startswith(('spear', 'pennant'))]
        self.assertGreater(max(v[2] for v in rest), 50)
        skin = [v for p in self.source.values() if g.CONNECTED_SKIN(p.name) for v in p.vertices]
        self.assertGreater(max(v[1] for v in skin)-min(v[1] for v in skin), 24)

    def test_centred_clearance_without_floor_compensation(self):
        self.assertEqual([c['name'] for c in self.clips], ['idle', 'walk', 'thrust', 'cleave', 'recoil', 'death'])
        self.assertEqual([c['loop'] for c in self.clips], [True, True, False, False, False, False])
        profile = find('MK_GOBLIN_CHIEFTAN')
        self.assertEqual(profile['clips'], [c['name'] for c in self.clips])
        self.assertEqual(profile['durations'][2:], [len(c['frames']) for c in self.clips][2:])
        self.assertEqual(profile['walkFrames'], len(self.clips[1]['frames']))
        for b in self.bounds:
            self.assertGreaterEqual(b[0], -32); self.assertGreaterEqual(b[1], -32)
            self.assertLessEqual(b[3], 32); self.assertLessEqual(b[4], 32); self.assertGreater(b[2], .07)
        for c in self.clips:
            count = len(c['frames'])
            for i, frame in enumerate(c['frames']):
                raw = g.pose(c['name'], i/(count if c['loop'] else count-1))
                self.assertEqual(frame, raw, 'automatic floor compensation hides a pose defect')
            if c['loop']:
                a = g.deform(self.v, self.w, g.pose(c['name'], 0)); b = g.deform(self.v, self.w, g.pose(c['name'], 1))
                self.assertLess(max(math.dist(x, y) for x, y in zip(a, b)), 1e-8)

    def test_grip_wrists_and_planted_feet(self):
        for name, count, fps, loop in g.CLIPS:
            for i in range(count):
                phase = i/(count if loop else count-1); frame = g.pose(name, phase); T = g.matrices(frame)
                if name != 'death' or phase < .18:
                    self.assertLess(math.dist(T[g.IDS['spear']][0], T[g.IDS['arm_R_end']][0]), 1e-8)
                    self.assertLess(angle(frame[g.IDS['spear']][3:7]), 1e-6)
                if name != 'death':
                    for side in ('L', 'R'):
                        self.assertLess(angle(frame[g.IDS[f'arm_{side}_end']][3:7]), 45, (name, i, side))
                        foot = T[g.IDS[f'leg_{side}_end']][0]
                        if name == 'cleave': self.assertAlmostEqual(foot[2], g.FEET[side][2], places=6)  # wide war-cry stance
                        elif name != 'walk': self.assertLess(math.dist(foot, g.FEET[side]), 1e-6)
                        else: self.assertGreaterEqual(foot[2], g.FEET[side][2]-1e-6)

    def test_middle_frame_key_poses_and_limp_death(self):
        def spear_axis(name, frame):
            T = g.matrices(self.clips[[c['name'] for c in self.clips].index(name)]['frames'][frame])
            from .skeletal import rotate
            return rotate(T[g.IDS['spear']][1], g.D_REST), T
        thrust, _ = spear_axis('thrust', 11)
        self.assertGreater(thrust[0], .6); self.assertLess(abs(thrust[2]), .3); self.assertLess(thrust[1], .55)
        cleave, T = spear_axis('cleave', 12)
        # War-cry key pose: spear arm extended above the helm, shaft overhead.
        self.assertLess(cleave[0], -.6)
        self.assertGreater(T[g.IDS['arm_R_end']][0][2], T[g.IDS['head']][0][2]+4)
        self.assertGreater(T[g.IDS['arm_L_end']][0][2], T[g.IDS['arm_L_upper']][0][2]-2)
        self.assertGreater(angle(self.clips[3]['frames'][12][g.IDS['jaw']][3:7]), 30)
        self.assertGreater(thrust[0]-thrust[1], .3)  # off the 3/4 camera axis
        settled = g.deform(self.v, self.w, g.pose('death', 1))
        self.assertLess(max(p[2] for p in settled), 30)
        self.assertGreater(min(p[2] for p in settled), .07)
        spear = [p for p, owner in zip(settled, self.owners()) if owner.startswith(('spear', 'pennant'))]
        self.assertLess(max(p[2] for p in spear)-min(p[2] for p in spear), 2.5)

    def owners(self):
        out = []
        for p in self.parts: out += [p.name]*len(p.vertices)
        return out

    def test_island_atlas_and_materials(self):
        self.assertTrue({m.role(p.name) for p in self.parts} <= set(m.ROLES))
        seen = set()
        for p in self.parts:
            self.assertEqual(len(p.vertices), len(p.faces)*3)
            for face in p.faces:
                key = tuple(p.uv[i] for i in face); self.assertNotIn(key, seen); seen.add(key)
                for u, v in key: self.assertTrue(0 < u < 1 and 0 < v < 1)
        self.assertLessEqual(len(seen), m.GRID*m.GRID)

    def test_runtime_and_material_bytes(self):
        data = iqm.encode(self.v, self.n, self.uv, self.tri, self.w, g.BONES, self.clips, self.bounds,
                          mesh_label='Project_Broom_goblin_chieftan', material_path=g.SKIN)
        self.assertEqual(data, (g.ROOT/g.MODEL).read_bytes())
        self.assertEqual(g.texture_bytes(), (g.ROOT/'mod/BrogueDoom'/g.SKIN).read_bytes())


if __name__ == '__main__': unittest.main()

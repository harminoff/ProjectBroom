"""Fury: connected skin, feathered wings, hover, clearance, key poses, limp death and bytes."""
import collections
import math
import unittest
from . import fury_animation as g, fury_materials as m, iqm
from .skeletal_registry import find


def closed(part):
    edges = collections.Counter()
    for face in part.faces:
        for a, b in zip(face, face[1:]+face[:1]):
            edges[tuple(sorted((tuple(round(c, 6) for c in part.vertices[a]), tuple(round(c, 6) for c in part.vertices[b]))))] += 1
    return set(edges.values()) == {2}


class FuryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts, cls.v, cls.n, cls.uv, cls.tri, cls.w = g.geometry()
        cls.clips, cls.bounds = g.animation_data(cls.v, cls.w)
        cls.named = {c['name']: c for c in cls.clips}
        cls.source = {p.name: p for p in g.build_parts()}
        cls.owner = [p.name for p in cls.parts for _ in p.vertices]

    def deformed(self, clip, index):
        return g.deform(self.v, self.w, self.named[clip]['frames'][index])

    def of(self, points, *prefixes):
        return [p for p, o in zip(points, self.owner) if o.startswith(prefixes)]

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
        used = {g.BONES[b][0] for row in self.w[:len(ids)] for b, weight in row if weight > .01}
        for bone in ('head', 'neck', 'arm_L', 'forearm_R', 'hand_L', 'thigh_R', 'shin_L', 'foot_R'):
            self.assertIn(bone, used)
        for row in self.w:
            self.assertAlmostEqual(math.fsum(weight for _, weight in row), 1, places=6); self.assertLessEqual(len(row), 4)

    def test_feathered_wings_and_avian_legs(self):
        names = set(self.source)
        for side in ('L', 'R'):
            self.assertEqual(sum(n.startswith('primary_') and n.endswith(side) for n in names), 7)
            self.assertEqual(sum(n.startswith('secondary_') and n.endswith(side) for n in names), 6)
            self.assertEqual(sum(n.startswith('covert_') and n.endswith(side) for n in names), 11)
            self.assertEqual(sum(n.startswith('talon_') and n.endswith(side) for n in names), 4)
        # Part-bird, not clothed: a feathered breast and mantle, and scapulars that carry
        # the plumage over the shoulders into the wing roots (no bare tube-and-knob joint).
        self.assertGreaterEqual(sum(n.startswith('mantle_') for n in names), 50)
        self.assertNotIn('wing_arm_root_L', names)
        for side in ('L', 'R'):
            self.assertEqual(sum(n.startswith('scapular_') and n.endswith(side) for n in names), 5)
        p = self.source['scapular_2_L']
        rows = [g.weights(p, v, u) for v, u in zip(p.vertices, p.uv)]
        self.assertIn([(g.IDS['chest'], 1)], rows)
        self.assertTrue(any(dict(r).get(g.IDS['wing1_L'], 0) > .99 for r in rows))
        self.assertTrue(all(m.shade('covert', .1, .5)[k] < 60 for k in range(3)))   # dark covered roots
        self.assertGreater(m.shade('primary', .9, .9)[0], 3*m.shade('primary', .15, .7)[0])   # lit edges and tips vs dark roots
        for name in ('primary_3_L', 'secondary_0_R', 'covert_20_L', 'tertial_1_R', 'legfeather_2_L', 'tailfeather_2',
                     'mantle_300', 'scapular_4_R',
                     'talon_1_L', 'nail_0_R', 'eye_L', 'tooth_R', 'hair_lock_5'):
            self.assertTrue(closed(self.source[name]), name)
        for name, bone in (('primary_6_L', 'wing3_L'), ('secondary_2_R', 'wing2_R'), ('tertial_0_L', 'wing1_L'),
                           ('talon_3_R', 'toes_R'), ('tailfeather_0', 'tail'), ('eye_R', 'head')):
            p = self.source[name]
            self.assertTrue(all(g.weights(p, v, u) == [(g.IDS[bone], 1)] for v, u in zip(p.vertices, p.uv)), name)
        # A broad span, not a bat: wings are separate feathered limbs on their own back bones.
        rest = [v for p in self.source.values() for v in p.vertices]
        self.assertGreater(max(v[1] for v in rest)-min(v[1] for v in rest), 48)
        for side, s in g.SIDES:
            root = g.REST[g.IDS['wing1_'+side]]
            self.assertLess(math.dist(root, (g.REST[g.IDS['chest']][0]-2.1, s*1.5, 37.2)), 1.)

    def test_profile_clearance_and_no_floor_compensation(self):
        self.assertEqual([c['name'] for c in self.clips], ['idle', 'fly', 'drub', 'lash', 'recoil', 'death'])
        self.assertEqual([c['loop'] for c in self.clips], [True, True, False, False, False, False])
        profile = find('MK_FURY')
        self.assertEqual(profile['clips'], [c['name'] for c in self.clips])
        # Durations are engine tics at 35 Hz: long enough to play every frame at the clip's fps.
        for role in range(2, 6):
            c = self.clips[role]
            self.assertGreaterEqual(profile['durations'][role], math.ceil(len(c['frames'])*35/c['fps']), c['name'])
        self.assertEqual(profile['walkFrames'], len(self.named['fly']['frames']))
        self.assertEqual(profile['skin'], g.SKIN); self.assertTrue(g.MODEL.endswith(profile['model']))
        for b in self.bounds:
            self.assertGreaterEqual(b[0], -32); self.assertGreaterEqual(b[1], -32)
            self.assertLessEqual(b[3], 32); self.assertLessEqual(b[4], 32); self.assertGreater(b[2], .07)
        for c in self.clips:
            count = len(c['frames'])
            for i, frame in enumerate(c['frames']):
                self.assertEqual(frame, g.pose(c['name'], i/(count if c['loop'] else count-1)))
                for row in frame: self.assertEqual(row[7:], (1, 1, 1))
            if c['loop']:
                a = g.deform(self.v, self.w, g.pose(c['name'], 0)); b = g.deform(self.v, self.w, g.pose(c['name'], 1))
                self.assertLess(max(math.dist(x, y) for x, y in zip(a, b)), 1e-8)

    def test_hover_and_wing_beats(self):
        for name, gap in (('idle', 6.5), ('fly', 12), ('drub', 6.5), ('lash', 6.5), ('recoil', 6.5)):
            for frame in self.named[name]['frames']:
                self.assertGreater(min(p[2] for p in g.deform(self.v, self.w, frame)), gap, name)
        tips = [g.matrices(f)[g.IDS['wing3_L']][0][2] for f in self.named['idle']['frames']]
        self.assertGreater(max(tips)-min(tips), 10)
        # Turnaround views sample idle frame 0: the wings are spread, not tucked.
        rest = self.deformed('idle', 0)
        wing = self.of(rest, 'primary_', 'secondary_')
        self.assertGreater(max(p[1] for p in wing)-min(p[1] for p in wing), 44)
        # The gallery's middle samples differ from each loop's first frame.
        for name in ('idle', 'fly'):
            a, b = self.deformed(name, 0), self.deformed(name, len(self.named[name]['frames'])//2)
            self.assertGreater(max(math.dist(x, y) for x, y in zip(a, b)), 1.)

    def test_middle_frame_key_poses(self):
        for name, need in (('drub', 9), ('lash', 9), ('recoil', 5)):
            frames = self.named[name]['frames']
            first = [p for p, _ in g.matrices(frames[0])]
            def travel(f): return max(math.dist(a, b) for a, (b, _) in zip(first, g.matrices(f)))
            mid = travel(frames[len(frames)//2])
            self.assertGreater(mid, need, name); self.assertGreater(mid, .8*max(travel(f) for f in frames), name)
        # Drub: wings raised high over the head, talons and claws driven forward.
        d = self.deformed('drub', 12)
        head = g.matrices(self.named['drub']['frames'][12])[g.IDS['head']][0]
        self.assertGreater(max(p[2] for p in self.of(d, 'primary_')), head[2]+10)
        self.assertGreater(max(p[0] for p in self.of(d, 'talon_')), 6)
        self.assertGreater(max(p[0] for p in self.of(d, 'nail_')), 9)
        # Lash: both wings whipped forward in front of the body.
        d = self.deformed('lash', 12)
        for side in ('L', 'R'):
            self.assertGreater(max(p[0] for p, o in zip(d, self.owner) if o.startswith('primary_') and o.endswith(side)), 12)

    def test_death_ends_limp_on_the_floor(self):
        frames = self.named['death']['frames']
        T = g.matrices(frames[len(frames)//2])
        self.assertGreater(T[g.IDS['pelvis']][0][2], 6); self.assertGreater(T[g.IDS['head']][0][2], 6)
        end = self.deformed('death', -1)
        self.assertLess(min(p[2] for p in end), .4)
        body = self.of(end, 'Connected_skin')
        self.assertLess(sorted(p[2] for p in body)[len(body)//2], 4.5)
        self.assertLess(max(p[2] for p in end), 12)
        # Wings lie splayed flat and stilled on the floor.
        wing = self.of(end, 'primary_', 'secondary_', 'covert_', 'tertial_')
        self.assertLess(max(p[2] for p in wing), 10); self.assertLess(sorted(p[2] for p in wing)[len(wing)//2], 5.5)
        self.assertGreater(max(p[1] for p in wing)-min(p[1] for p in wing), 40)
        a, b = g.deform(self.v, self.w, frames[-2]), end
        self.assertLess(max(math.dist(x, y) for x, y in zip(a, b)), .6)
        T = g.matrices(frames[-1])
        for bone, top in (('pelvis', 5), ('chest', 5), ('head', 6)):   # head bone sits at the skull base
            self.assertLess(T[g.IDS[bone]][0][2], top, bone)
        self.assertLess(min(p[2] for p in self.of(end, 'eye_', 'brow_', 'tooth_')), 4)

    def test_no_degenerate_triangles(self):
        for c in self.clips:
            for frame in (c['frames'][0], c['frames'][len(c['frames'])//2], c['frames'][-1]):
                d = g.deform(self.v, self.w, frame)
                for a, b, cc in self.tri:
                    e1 = [d[b][k]-d[a][k] for k in range(3)]; e2 = [d[cc][k]-d[a][k] for k in range(3)]
                    cr = (e1[1]*e2[2]-e1[2]*e2[1], e1[2]*e2[0]-e1[0]*e2[2], e1[0]*e2[1]-e1[1]*e2[0])
                    self.assertGreater(sum(x*x for x in cr), 0)

    def test_atlas_roles(self):
        self.assertTrue({m.role(p.name) for p in self.parts} <= set(m.RECTS) | {'skin'})
        for u, v in self.uv: self.assertTrue(0 <= u <= 1 and 0 <= v <= 1)
        skin = self.parts[0]
        self.assertTrue(all(u < .5 for u, v in skin.uv))
        self.assertTrue(all(u > .5 for p in self.parts[1:] for u, v in p.uv))

    def test_runtime_and_material_bytes(self):
        data = iqm.encode(self.v, self.n, self.uv, self.tri, self.w, g.BONES, self.clips, self.bounds,
                          mesh_label='Project_Broom_fury', material_path=g.SKIN)
        self.assertEqual(data, (g.ROOT/g.MODEL).read_bytes())
        skin = g.texture_bytes()
        self.assertEqual(skin, (g.ROOT/'mod/BrogueDoom'/g.SKIN).read_bytes())
        # Painted value range: pale ash skin, near-black hair, bright painted red eyes.
        self.assertGreater(sum(m.ASH), 450); self.assertLess(sum(m.BLACKRED), 50)
        self.assertGreater(m.shade('eye', .5, .95)[0], 240)


if __name__ == '__main__': unittest.main()

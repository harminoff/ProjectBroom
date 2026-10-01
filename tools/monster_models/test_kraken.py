"""Kraken: connected skin, seated suckers, cell clearance, key poses, limp death and bytes."""
import collections
import json
import math
import unittest
from . import kraken_animation as g, kraken_materials as m, iqm
from .kraken_animation import point_triangle
from .skeletal_registry import find


class TentacleChecks:
    """Shared checks for the tentacle family (the tentacle horror reuses them)."""
    g = None
    symbol = None
    label = None

    @classmethod
    def setUpClass(cls):
        cls.parts, cls.v, cls.n, cls.uv, cls.tri, cls.w = cls.g.geometry()
        cls.clips, cls.bounds = cls.g.animation_data(cls.v, cls.w)

    def frames(self):
        for c in self.clips:
            count = len(c['frames'])
            for i, frame in enumerate(c['frames']):
                yield c['name'], i, i/(count if c['loop'] else count-1), frame

    def middle(self, name):
        clip = next(c for c in self.clips if c['name'] == name)
        return clip['frames'][int(len(clip['frames'])*.5)]

    def test_profile_matches_manifest(self):
        row = find(self.symbol)
        manifest = json.loads((self.g.ROOT/row['manifest']).read_text())
        self.assertEqual(row['module'], self.g.__name__.rsplit('.', 1)[1])
        self.assertEqual('graphics/'+row['skin'].split('/')[-1], self.g.SKIN)
        self.assertEqual('models/monsters/'+row['model'], self.g.MODEL)
        self.assertEqual(row['clips'], [c[0] for c in self.g.CLIPS])
        counts = {c['name']: c['frameCount'] for c in manifest['clips']}
        self.assertEqual(row['walkFrames'], counts[row['clips'][1]])
        self.assertEqual(row['durations'][2:], [counts[n] for n in row['clips'][2:]])
        self.assertEqual([c[3] for c in self.g.CLIPS], [True, True, False, False, False, False])
        for c in self.g.CLIPS[2:]:
            self.assertEqual(c[1] % 2, 1, 'odd action length puts the key pose exactly on the middle frame')
        self.assertTrue(row['report'].startswith('docs/') and (self.g.ROOT/row['report']).is_file())

    def test_connected_closed_skin(self):
        p = self.parts[0]
        ids = p.skin_topology
        edges = collections.Counter()
        graph = collections.defaultdict(set)
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
        self.assertLessEqual(len(p.faces), 12288)
        used = {self.g.BONES[b][0] for row in p.skin_weights for b, w in row if w > .05}
        for limb in self.g.LIMBS:
            for name in limb.bone_names[1:-1]:
                self.assertIn(name, used, 'every limb segment deforms the connected skin')
        for row in self.w:
            self.assertAlmostEqual(math.fsum(w for b, w in row), 1, places=5)
            self.assertLessEqual(len(row), 4)

    def test_suckers_are_seated_on_the_skin(self):
        skin = self.parts[0]
        cups = [p for p in self.parts if p.name.startswith('cup_')]
        self.assertGreater(len(cups), 60)
        keys = {tuple(v): tuple(tuple(x) for x in w) for v, w in zip(skin.vertices, skin.skin_weights)}
        sample = cups[::7]
        tris = [tuple(skin.vertices[i] for i in t) for t in skin.triangles()]
        for cup in sample:
            near = [t for t in tris if min(math.dist(v, cup.anchor) for v in t) < 4]
            self.assertLess(min(point_triangle(cup.anchor, *t) for t in near), .31, cup.name+' sits on the skin surface')
            carried = {self.g.BONES[b][0] for b, w in cup.skin_weights[0] if w > .15}
            self.assertTrue(carried & cup.bones, cup.name+' rides its own limb segment')
        # Every cup stays seated on the deformed skin through the key poses.
        ids = list(skin.triangles())
        local = {cup.name: [t for t in ids if min(math.dist(skin.vertices[i], cup.anchor) for i in t) < 4] for cup in sample}
        weights = [[tuple(x) for x in w] for w in skin.skin_weights]
        for name in ('idle', self.g.CLIPS[2][0], self.g.CLIPS[3][0], self.g.CLIPS[5][0]):
            frame = self.middle(name) if name != 'idle' else self.clips[0]['frames'][10]
            for cup in sample:
                used = sorted({i for t in local[cup.name] for i in t})
                moved = dict(zip(used, self.g.deform([skin.vertices[i] for i in used], [weights[i] for i in used], frame)))
                anchor = self.g.deform([cup.anchor], [cup.skin_weights[0]], frame)[0]
                gap = min(point_triangle(anchor, *(moved[i] for i in t)) for t in local[cup.name])
                self.assertLess(gap, .6, (name, cup.name, 'cup must stay seated on its skin'))

    def test_cell_clearance_every_frame_and_no_floor_compensation(self):
        for b in self.bounds:
            self.assertGreaterEqual(b[0], -32)
            self.assertGreaterEqual(b[1], -32)
            self.assertLessEqual(b[3], 32)
            self.assertLessEqual(b[4], 32)
            self.assertGreaterEqual(b[2], .07)
        for name, i, t, f in self.frames():
            self.assertEqual(f, self.g.pose(name, t), 'automatic floor compensation would hide a contact defect')
            self.assertTrue(all(tuple(row[7:]) == (1, 1, 1) for row in f))

    def test_loops_seamless_and_actions_recover(self):
        for c in self.clips[:2]:
            a = self.g.deform(self.v, self.w, self.g.pose(c['name'], 0))
            b = self.g.deform(self.v, self.w, self.g.pose(c['name'], 1))
            self.assertLess(max(math.dist(p, q) for p, q in zip(a, b)), 1e-6)
        rest = self.g.deform(self.v, self.w, self.g.pose('idle', 0))
        for c in self.clips[2:5]:
            end = self.g.deform(self.v, self.w, c['frames'][-1])
            self.assertLess(max(math.dist(p, q) for p, q in zip(rest, end)), .7, c['name']+' must recover')

    def tips(self, frame):
        world = self.g.matrices(frame)
        return {l.name: world[l.ids[-1]][0] for l in self.g.LIMBS}

    def test_runtime_and_texture_bytes(self):
        data = iqm.encode(self.v, self.n, self.uv, self.tri, self.w, self.g.BONES, self.clips, self.bounds,
                          mesh_label=self.label, material_path=self.g.SKIN)
        self.assertEqual(data, (self.g.ROOT/'mod/BrogueDoom'/self.g.MODEL).read_bytes())
        self.assertEqual(self.g.texture_bytes(), (self.g.ROOT/'mod/BrogueDoom'/self.g.SKIN).read_bytes())


class KrakenTests(TentacleChecks, unittest.TestCase):
    g = g
    symbol = 'MK_KRAKEN'
    label = 'Project_Broom_kraken'

    def test_anatomy_reads_as_a_kraken(self):
        names = {p.name for p in self.parts}
        self.assertTrue({'eye_L', 'eye_R', 'beak_upper', 'beak_lower'} <= names)
        self.assertEqual(sorted(l.name.split('_')[0] for l in g.LIMBS).count('club'), 2)
        self.assertEqual(len(g.LIMBS), 10)
        # The face looks at the player (+X): both eyes gaze forward, above the
        # 24-unit opaque deep-water surface, and the beak projects past the head.
        for side in (1, -1):
            self.assertGreater(g.eye_gaze(side)[0], .8)
            self.assertGreater(g.eye_centre(side)[2]-g.EYE_R, 24)
        self.assertGreater(g.crown(8.5, -2.3)[0], g.HEAD_C[0]+g.HEAD_R[0])
        # The mantle sits behind and above the head, leaning back.
        self.assertLess(g.MANTLE.rows[-1]['c'][0], g.HEAD_C[0]-20)
        above = [l.name for l in g.LIMBS if max(r['c'][2] for r in l.rows) > 40]
        self.assertEqual(sorted(above), ['club_L', 'club_R', 'riser_L', 'riser_R'])

    def test_slap_and_seize_key_poses_on_middle_frames(self):
        rest = self.tips(self.g.pose('slap', 0))
        slap = self.tips(self.middle('slap'))
        self.assertGreater(slap['riser_R'][0], 22)
        self.assertGreater(math.dist(slap['riser_R'], rest['riser_R']), 15)
        self.assertGreater(slap['riser_L'][2], 44, 'the other arm is cocked overhead')
        seize = self.tips(self.middle('seize'))
        for side in 'LR':
            self.assertGreater(seize['club_'+side][0], 18, 'clubs converge in front of the beak')
            self.assertLess(abs(seize['club_'+side][1]), 8)
        head = g.matrices(self.middle('slap'))[g.IDS['head']]
        self.assertGreater(head[0][0], g.REST[g.IDS['head']][0]+3, 'the body lunges into the slap')

    def test_squat_low_body(self):
        rest = g.deform(self.v, self.w, g.pose('idle', 0))
        self.assertLess(max(p[2] for p in rest), 58, 'a low squat mass, not a stilt-walker')
        world = g.matrices(g.pose('idle', 0))
        self.assertLess(world[g.IDS['head']][0][2], 26)
        for limb in g.LIMBS:
            self.assertGreater(limb.rows[0]['r'], 3.4*limb.rows[len(limb.rows)//2]['r']/2, limb.name+' tapers strongly')

    def test_sink_ends_limp_on_the_floor(self):
        frame = self.clips[5]['frames'][-1]
        settled = g.deform(self.v, self.w, frame)
        self.assertLess(max(p[2] for p in settled), 36)
        world = g.matrices(frame)
        self.assertLess(world[g.IDS['head']][0][2], 15)
        for limb in g.LIMBS:
            tip = world[limb.ids[-1]][0]
            self.assertLess(tip[2], 5, limb.name+' lies on the floor')
        mid = g.deform(self.v, self.w, self.middle('sink'))
        self.assertLess(max(p[2] for p in mid), 45, 'already collapsing by the middle frame')

    def test_painted_value_contrast(self):
        bright = lambda c: sum(c)/3
        limb = g.BY_NAME['riser_L']
        row = limb.at(limb.length*.5)
        up = (0, 0, 1)
        ventral = m.pigment(tuple(a+b*row['r'] for a, b in zip(row['c'], row['V'])), row['V'])
        dorsal = m.pigment(tuple(a-b*row['r'] for a, b in zip(row['c'], row['V'])), tuple(-x for x in row['V']))
        self.assertGreater(bright(ventral)-bright(dorsal), 60, 'pale sucker band against dark dorsal skin')
        eye = g.eye_centre(1)
        ring = m.pigment((eye[0], eye[1]-2.5, eye[2]+4.5), up)
        self.assertLess(bright(ring), 90, 'painted dark eye ring')


if __name__ == '__main__':
    unittest.main()

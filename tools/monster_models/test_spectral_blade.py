"""Spectral blade: shard blade, cage-only trails, clearance, key poses, binding and bytes."""
import math
import unittest
from . import spectral_blade_animation as g, spectral_blade_materials as m, iqm
from .skeletal_registry import find, PENDING, ROOT


class SpectralBladeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts, cls.v, cls.n, cls.uv, cls.tri, cls.w = g.geometry()
        cls.clips, cls.bounds = g.animation_data(cls.v, cls.w)
        cls.names = [p.name for p in cls.parts]

    def deform(self, name, t):
        return g.deform(self.v, self.w, g.pose(name, t))

    def part(self, name, points):
        start = 0
        for p in self.parts:
            if p.name == name:
                return points[start:start+len(p.vertices)]
            start += len(p.vertices)
        raise KeyError(name)

    def test_weights_normalized_bounded_and_no_degenerate_bind_triangles(self):
        for row in self.w:
            self.assertLessEqual(len(row), 4)
            self.assertAlmostEqual(math.fsum(x for _, x in row), 1, places=5)
        for a, b, c in self.tri:
            e1 = [q-p for p, q in zip(self.v[a], self.v[b])]
            e2 = [q-p for p, q in zip(self.v[a], self.v[c])]
            cr = (e1[1]*e2[2]-e1[2]*e2[1], e1[2]*e2[0]-e1[0]*e2[2], e1[0]*e2[1]-e1[1]*e2[0])
            self.assertGreater(math.hypot(*cr), 1e-9)

    def test_six_roles_centered_clearance_no_floor_compensation_unit_scales(self):
        self.assertEqual([c['loop'] for c in self.clips], [True, True, False, False, False, False])
        for b in self.bounds:
            self.assertGreaterEqual(min(b[0], b[1]), -32)
            self.assertLessEqual(max(b[3], b[4]), 32)
            self.assertGreater(b[2], .07)
            self.assertLess(b[5], 72, 'the oblique gallery camera crops above about 72 units')
        for c in self.clips:
            for i, f in enumerate(c['frames']):
                self.assertEqual(f, g.pose(c['name'], i/(len(c['frames']) if c['loop'] else len(c['frames'])-1)))
                self.assertTrue(all(row[7:] == (1, 1, 1) for row in f))
            if c['loop']:
                a, b = self.deform(c['name'], 0), self.deform(c['name'], 1)
                self.assertLess(max(math.dist(x, y) for x, y in zip(a, b)), 1e-6)

    def test_profile_durations_cover_every_action(self):
        row = find('MK_SPECTRAL_BLADE')
        self.assertEqual(row['clips'], [c[0] for c in g.CLIPS])
        self.assertEqual(row['walkFrames'], g.CLIPS[1][1])
        for (name, count, fps, loop), tics in zip(g.CLIPS[2:], row['durations'][2:]):
            self.assertGreaterEqual(tics, math.ceil(count*35/fps), name)
        self.assertNotIn('visualScale', row)

    def test_actions_start_from_idle_and_key_pose_is_the_middle_frame(self):
        rest = self.deform('idle', 0)
        for name, count, fps, loop in g.CLIPS[2:]:
            self.assertEqual(count % 2, 1, 'odd frame counts put t=0.5 on the sampled middle frame')
            first = self.deform(name, 0)
            mid = self.deform(name, (count//2)/(count-1))
            self.assertLess(max(math.dist(a, b) for a, b in zip(first, rest)), 1e-6, name)
            self.assertGreater(max(math.dist(a, b) for a, b in zip(mid, first)), 20, name)

    def test_trails_exist_only_in_their_attack(self):
        def area(name, points):
            pts = self.part(name, points)
            return max(max(q[a] for q in pts)-min(q[a] for q in pts) for a in range(3))
        for clip, count, fps, loop in g.CLIPS:
            for f in (0, count//2, count-1):
                d = self.deform(clip, f/(count if loop else count-1))
                slash, ring = area('slash_trail', d), area('whirl_ring', d)
                self.assertEqual(slash > 10, clip == 'slash' and f == count//2, clip)
                self.assertEqual(ring > 10, clip == 'whirl' and f == count//2, clip)
                if f != count//2 or clip not in ('slash', 'whirl'):
                    self.assertLess(max(slash, ring), 1e-3)

    def test_hovers_then_shatters_onto_the_floor(self):
        for f in range(8):
            d = self.deform('idle', f/8)
            self.assertGreater(min(p[2] for p in d), 1.0)
        end = self.deform('shatter', 1)
        for i in range(5):
            shard = self.part(f'blade_shard_{i}', end)
            self.assertLess(max(p[2] for p in shard), 4.5, 'shards lie on the floor')
        centres = [[sum(c)/len(c) for c in zip(*self.part(f'blade_shard_{i}', end))] for i in range(5)]
        self.assertGreater(min(math.dist(a[:2], b[:2]) for i, a in enumerate(centres) for b in centres[i+1:]), 5)
        gaps = [math.dist(g.pose('shatter', .5)[g.IDS[f'shard_{i}']][:3], g.BONES[g.IDS[f'shard_{i}']][2]) for i in range(5)]
        self.assertGreater(min(gaps), 6, 'the middle frame is the burst')

    def test_signature_parts_and_no_hilt(self):
        self.assertEqual(sum(n.startswith('blade_shard_') for n in self.names), 5)
        self.assertEqual(sum(n.startswith('wisp_') for n in self.names), 3)
        self.assertEqual(sum(n.startswith('mote_') for n in self.names), 3)
        self.assertFalse(any(k in n for n in self.names for k in ('guard', 'grip', 'pommel', 'hilt')))
        # Curved: the point sits well off the straight line from the base.
        self.assertGreater(abs(g.centre(1)[1]-g.centre(0)[1]), 4)

    def test_paint_value_reads_as_light(self):
        edge = m.pigment('blade', 1, .5, 100, 200)
        fuller = [max(m.pigment('blade', .25, k/100, 100, 20)) for k in range(10, 80)]
        self.assertGreater(min(edge), 200)
        self.assertLess(min(fuller), 90, 'darker see-through fuller')
        self.assertGreater(edge[2], edge[0], 'blue-violet identity cue')

    def test_additive_glow_binding(self):
        row = find('MK_SPECTRAL_BLADE')
        self.assertTrue(row['additiveFlame'])
        self.assertTrue(row['emissive'])
        self.assertEqual(row['skin'], g.SKIN)
        self.assertEqual('mod/BrogueDoom/models/monsters/'+row['model'], g.MODEL)
        self.assertIn(g.SHADER, row['ownedFiles'])
        snippet = PENDING/'MK_SPECTRAL_BLADE.gldefs'
        text = snippet.read_text() if snippet.is_file() else (ROOT/'mod/BrogueDoom/GLDEFS').read_text()
        block = text[text.index('material "graphics/BRGSBLAD.png"'):]
        self.assertIn('shaders/spectral-blade-glow.fp', block[:block.index('}')])
        shader = (ROOT/g.SHADER).read_text()
        self.assertIn('material.Bright', shader)
        for forbidden in ('uLightLevel', 'random', 'AddLight'):
            self.assertNotIn(forbidden, shader)

    def test_runtime_and_material_bytes(self):
        data = iqm.encode(self.v, self.n, self.uv, self.tri, self.w, g.BONES, self.clips, self.bounds,
                          mesh_label='Project_Broom_spectral_blade', material_path=g.SKIN)
        self.assertEqual(data, (ROOT/g.MODEL).read_bytes())
        self.assertEqual(g.texture_bytes(), (ROOT/'mod/BrogueDoom'/g.SKIN).read_bytes())


if __name__ == '__main__':
    unittest.main()

"""Spectral sword: hilted image, caged echoes, clearance, key poses, binding and bytes."""
import math
import unittest
from . import spectral_sword_animation as g, spectral_sword_materials as m, iqm
from .skeletal_registry import find, PENDING, ROOT


class SpectralSwordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts, cls.v, cls.n, cls.uv, cls.tri, cls.w = g.geometry()
        cls.clips, cls.bounds = g.animation_data(cls.v, cls.w)
        cls.names = [p.name for p in cls.parts]

    def deform(self, name, t):
        return g.deform(self.v, self.w, g.pose(name, t))

    def group(self, prefix, points):
        out, start = [], 0
        for p in self.parts:
            if p.name.startswith(prefix):
                out += points[start:start+len(p.vertices)]
            start += len(p.vertices)
        return out

    def main(self, points):
        out, start = [], 0
        for p in self.parts:
            if not p.name.startswith(('e1_', 'e2_')):
                out += points[start:start+len(p.vertices)]
            start += len(p.vertices)
        return out

    def test_weights_normalized_and_bounded(self):
        for row in self.w:
            self.assertLessEqual(len(row), 4)
            self.assertAlmostEqual(math.fsum(x for _, x in row), 1, places=5)

    def test_six_roles_centered_clearance_no_floor_compensation_unit_scales(self):
        self.assertEqual([c['loop'] for c in self.clips], [True, True, False, False, False, False])
        for b in self.bounds:
            self.assertGreaterEqual(min(b[0], b[1]), -32)
            self.assertLessEqual(max(b[3], b[4]), 32)
            self.assertGreater(b[2], .07)
            self.assertLess(b[5], 72)
        for c in self.clips:
            for i, f in enumerate(c['frames']):
                self.assertEqual(f, g.pose(c['name'], i/(len(c['frames']) if c['loop'] else len(c['frames'])-1)))
                self.assertTrue(all(row[7:] == (1, 1, 1) for row in f))
            if c['loop']:
                a, b = self.deform(c['name'], 0), self.deform(c['name'], 1)
                self.assertLess(max(math.dist(x, y) for x, y in zip(a, b)), 1e-6)

    def test_profile_durations_cover_every_action(self):
        row = find('MK_SPECTRAL_IMAGE')
        self.assertEqual(row['clips'], [c[0] for c in g.CLIPS])
        self.assertEqual(row['walkFrames'], g.CLIPS[1][1])
        for (name, count, fps, loop), tics in zip(g.CLIPS[2:], row['durations'][2:]):
            self.assertGreaterEqual(tics, math.ceil(count*35/fps), name)
        self.assertNotIn('visualScale', row)

    def test_actions_start_from_idle_and_key_pose_is_the_middle_frame(self):
        rest = self.deform('idle', 0)
        for name, count, fps, loop in g.CLIPS[2:]:
            self.assertEqual(count % 2, 1)
            first = self.deform(name, 0)
            mid = self.deform(name, (count//2)/(count-1))
            self.assertLess(max(math.dist(a, b) for a, b in zip(first, rest)), 1e-6, name)
            self.assertGreater(max(math.dist(a, b) for a, b in zip(self.main(mid), self.main(first))), 20, name)

    def test_hovers_point_down_then_lies_flat_on_the_floor(self):
        d = self.main(self.deform('idle', 0))
        tip = min(d, key=lambda p: p[2])
        self.assertGreater(tip[2], 1.0)
        blade = self.group('double_edged_blade', self.deform('idle', 0))
        pommel = self.group('wheel_pommel', self.deform('idle', 0))
        self.assertLess(max(p[2] for p in blade), min(p[2] for p in pommel), 'point-down hover')
        end = self.main(self.deform('fall', 1))
        self.assertLess(max(p[2] for p in end), 4.5)
        span = math.hypot(max(p[0] for p in end)-min(p[0] for p in end), max(p[1] for p in end)-min(p[1] for p in end))
        self.assertGreater(span, 30, 'the sword lies full length')

    def test_echoes_fan_in_the_cleave_and_vanish_at_death(self):
        count = g.CLIPS[2][1]
        mid = self.deform('cleave', (count//2)/(count-1))
        tips = []
        for prefix in ('double_edged_blade', 'e1_echo_double_edged_blade', 'e2_echo_double_edged_blade'):
            bind = self.group(prefix, self.v)
            tips.append(self.group(prefix, mid)[max(range(len(bind)), key=lambda i: bind[i][2])])
        self.assertGreater(min(math.dist(a, b) for i, a in enumerate(tips) for b in tips[i+1:]), 10, 'a fan of three swords')
        end = self.deform('fall', 1)
        for prefix in ('e1_', 'e2_'):
            pts = self.group(prefix, end)
            self.assertLess(max(max(p[a] for p in pts)-min(p[a] for p in pts) for a in range(3)), 1e-3)
        idle = self.deform('idle', 0)
        for prefix in ('e1_', 'e2_'):
            pts = self.group(prefix, idle)
            self.assertGreater(max(p[2] for p in pts)-min(p[2] for p in pts), 40)

    def test_signature_hilt_parts(self):
        for name in ('double_edged_blade', 'crossguard', 'ecusson', 'guard_gem', 'wrapped_grip', 'wheel_pommel', 'pommel_gem'):
            self.assertIn(name, self.names)
            self.assertIn('e1_echo_'+name, self.names)
            self.assertIn('e2_echo_'+name, self.names)

    def test_paint_echoes_are_fainter_and_crimson(self):
        main = m.pigment('blade', .95, .5, 60, 200)
        e1 = m.pigment('e1_blade', .95, .5, 60, 200)
        e2 = m.pigment('e2_blade', .95, .5, 60, 200)
        self.assertGreater(sum(main), sum(e1))
        self.assertGreater(sum(e1), sum(e2))
        self.assertGreater(m.pigment('blade', .7, .5, 60, 200)[0], 2*m.pigment('blade', .7, .5, 60, 200)[2])

    def test_additive_glow_binding(self):
        row = find('MK_SPECTRAL_IMAGE')
        self.assertTrue(row['additiveFlame'])
        self.assertTrue(row['emissive'])
        self.assertEqual(row['skin'], g.SKIN)
        self.assertEqual('mod/BrogueDoom/models/monsters/'+row['model'], g.MODEL)
        self.assertIn(g.SHADER, row['ownedFiles'])
        snippet = PENDING/'MK_SPECTRAL_IMAGE.gldefs'
        text = snippet.read_text() if snippet.is_file() else (ROOT/'mod/BrogueDoom/GLDEFS').read_text()
        block = text[text.index('material "graphics/BRGSSWRD.png"'):]
        self.assertIn('shaders/spectral-sword-glow.fp', block[:block.index('}')])
        shader = (ROOT/g.SHADER).read_text()
        self.assertIn('material.Bright', shader)
        for forbidden in ('uLightLevel', 'random', 'AddLight'):
            self.assertNotIn(forbidden, shader)

    def test_runtime_and_material_bytes(self):
        data = iqm.encode(self.v, self.n, self.uv, self.tri, self.w, g.BONES, self.clips, self.bounds,
                          mesh_label='Project_Broom_spectral_image', material_path=g.SKIN)
        self.assertEqual(data, (ROOT/g.MODEL).read_bytes())
        self.assertEqual(g.texture_bytes(), (ROOT/'mod/BrogueDoom'/g.SKIN).read_bytes())


if __name__ == '__main__':
    unittest.main()

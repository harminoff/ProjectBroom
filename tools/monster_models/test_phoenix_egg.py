"""Phoenix egg: membrane/nest signature, hidden yolk, cracking key poses,
burst death and exact bytes."""
import math
import unittest
from . import phoenix_egg_animation as model
from .relic_kit import RelicChecks


def centroid(points):
    return tuple(sum(p[i] for p in points)/len(points) for i in range(3))


class PhoenixEggTests(RelicChecks, unittest.TestCase):
    model = model
    symbol = 'MK_PHOENIX_EGG'
    shader = 'shaders/phoenix-egg-membrane.fp'

    def test_ember_egg_in_ash_nest_signature(self):
        names = {p.name for p in self.parts}
        self.assertIn('ash_mound', names); self.assertIn('egg_cap', names); self.assertIn('glowing_yolk', names)
        self.assertEqual(sum(n.startswith('egg_plate_') and 'inner' not in n for n in names), 4)
        self.assertGreaterEqual(sum('stick' in n for n in names), 20)
        roles = {p.name: p.role for p in self.parts}
        self.assertEqual(roles['ash_mound'], 'ash')
        glow = {p.name for p in self.parts if model.R.atlas.glow(p.role)}
        self.assertTrue({'egg_cap', 'glowing_yolk', 'egg_plate_0', 'egg_plate_inner_0'} <= glow)
        self.assertFalse(any('stick_0' in n and 'ember' not in n for n in glow))

    def _yolk_hidden_in_shell(self, verts):
        c = (0, 0, (model.EGG_BASE+model.EGG_HEIGHT/2)*model.S)
        shell = self.part_points(verts, 'egg_plate_inner_')+self.part_points(verts, 'egg_cap_inner')
        inner = min(math.dist(p, c) for p in shell)
        for p in self.part_points(verts, 'glowing_yolk'):
            self.assertLess(math.dist(p, c), inner-.5)

    def test_yolk_hidden_at_rest_and_buried_after_burst(self):
        self._yolk_hidden_in_shell(self.v)
        final = self.posed('burst', len(self.clip['burst']['frames'])-1)
        mound = self.part_points(self.v, 'ash_mound')
        for p in self.part_points(final, 'glowing_yolk'):
            r = math.hypot(p[0], p[1])
            surface = min((q for q in mound), key=lambda q: abs(math.hypot(q[0], q[1])-r))[2]
            self.assertLess(p[2], surface-.3)
            self.assertGreater(p[2], .1)

    def test_kindle_cracks_cap_over_rising_yolk(self):
        mid = self.posed('kindle', 9)
        cut = (model.EGG_BASE+model.CUT)*model.S
        self.assertGreater(max(p[2] for p in self.part_points(mid, 'glowing_yolk')), cut+1)
        rest_cap = min(p[2] for p in self.part_points(self.v, 'egg_cap'))
        self.assertGreater(min(p[2] for p in self.part_points(mid, 'egg_cap'))-rest_cap, 5)

    def test_bloom_splays_plates(self):
        mid = self.posed('bloom', 10)
        spread = lambda pts: max(math.hypot(p[0], p[1]) for p in pts)
        self.assertGreater(spread(self.part_points(mid, 'egg_plate_'))-spread(self.part_points(self.v, 'egg_plate_')), 6)

    def test_burst_scatters_shell_to_the_floor(self):
        final = self.posed('burst', len(self.clip['burst']['frames'])-1)
        for k in range(4):
            plate = self.part_points(final, 'egg_plate_%d' % k)
            self.assertLess(min(p[2] for p in plate), .2)
            self.assertGreater(math.hypot(*centroid(plate)[:2]), 12)
        cap = self.part_points(final, 'egg_cap')
        self.assertLess(max(p[2] for p in cap), 12)
        self.assertLess(self.bounds[-1][5], 12)


if __name__ == '__main__':
    unittest.main()

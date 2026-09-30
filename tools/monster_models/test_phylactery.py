"""Phylactery reliquary: soul-gem signature, key poses, shattered death, bytes."""
import math
import unittest
from . import phylactery_animation as model
from .relic_kit import RelicChecks


def centroid(points):
    return tuple(sum(p[i] for p in points)/len(points) for i in range(3))


class PhylacteryTests(RelicChecks, unittest.TestCase):
    model = model
    symbol = 'MK_PHYLACTERY'
    shader = 'shaders/phylactery-gem.fp'

    def test_soul_gem_reliquary_signature(self):
        names = {p.name for p in self.parts}
        for name in ('serpentine_plinth', 'gilt_stem_cup', 'skull_cranium', 'skull_socket_L', 'skull_socket_R'):
            self.assertIn(name, names)
        self.assertEqual(sum(n.startswith('soul_gem_quarter_') for n in names), 4)
        self.assertEqual(sum(n.startswith('gilt_claw_') for n in names), 4)
        self.assertEqual(sum(n.startswith('foot_talon_') for n in names), 12)
        glow = {p.name for p in self.parts if model.R.atlas.glow(p.role)}
        self.assertEqual(glow, {'soul_gem_quarter_%d' % k for k in range(4)})
        gem = self.part_points(self.v, 'soul_gem_quarter_')
        c = centroid(gem)
        self.assertLess(math.hypot(c[0], c[1]), 1e-6)  # the quarters tile one gem
        self.assertGreater(max(p[2] for p in gem)-min(p[2] for p in gem), 20)
        skull = self.part_points(self.v, 'skull_')
        self.assertGreater(min(p[0] for p in skull), 3)  # faces the +X camera

    def test_enchant_raises_gem_and_blooms_claws_at_middle(self):
        mid = self.posed('enchant', 9)
        rest_gem = centroid(self.part_points(self.v, 'soul_gem_quarter_'))
        gem = centroid(self.part_points(mid, 'soul_gem_quarter_'))
        self.assertGreater(gem[2]-rest_gem[2], 9)
        spread = lambda pts: max(math.hypot(p[0], p[1]) for p in pts)
        self.assertGreater(spread(self.part_points(mid, 'gilt_claw_'))-spread(self.part_points(self.v, 'gilt_claw_')), 5)

    def test_sorcery_leans_toward_target(self):
        mid = self.posed('sorcery', 10)
        gem = centroid(self.part_points(mid, 'soul_gem_quarter_'))
        self.assertGreater(gem[0], 6)

    def test_shattered_death_lies_on_the_floor(self):
        final = self.posed('shatter', len(self.clip['shatter']['frames'])-1)
        for k in range(4):
            shard = self.part_points(final, 'soul_gem_quarter_%d' % k)
            self.assertLess(max(p[2] for p in shard), 11.5)
            self.assertLess(min(p[2] for p in shard), .2)
            c = centroid(shard)
            self.assertGreater(math.hypot(c[0], c[1]), 15)
        for k in range(4):
            claw = self.bone_points(final, 'claw_%d' % k)
            self.assertLess(min(p[2] for p in claw), .2)
        cup = self.part_points(final, 'gilt_stem_cup')
        self.assertLess(max(p[2] for p in cup), 25)
        self.assertLess(self.bounds[-1][5], 26)


if __name__ == '__main__':
    unittest.main()

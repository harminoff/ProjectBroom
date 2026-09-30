"""Mirrored totem: mirror prism signature, sealed flash crystal, opening key
poses, shattered death and exact bytes."""
import math
import unittest
from . import mirrored_totem_animation as model
from .relic_kit import RelicChecks, GLOW_U


def centroid(points):
    return tuple(sum(p[i] for p in points)/len(points) for i in range(3))


class MirroredTotemTests(RelicChecks, unittest.TestCase):
    model = model
    symbol = 'MK_MIRRORED_TOTEM'
    shader = 'shaders/mirrored-totem-mirror.fp'

    def test_mirror_prism_signature(self):
        names = {p.name for p in self.parts}
        self.assertEqual(sum(n.startswith('mirror_') for n in names), 6)
        for name in ('prism_crown', 'lacquer_plinth', 'crown_mirror_finial', 'corner_column_0'):
            self.assertIn(name, names)
        self.assertEqual(sum(n.startswith('crown_mirror_shard_') for n in names), 6)
        # each face has its own reflected-banding cell
        self.assertEqual({p.role for p in self.parts if p.name.startswith('mirror_')}, {'mirror_0', 'mirror_1', 'mirror_2'})
        for p in self.parts:
            us = [u for u, v in p.uv]
            if p.role.startswith('mirror'):
                self.assertTrue(.5 <= min(us) and max(us) < GLOW_U, p.name)  # shader mirror column
            elif p.role != 'flash':
                self.assertLess(max(us), .5, p.name)
        glow = {p.name for p in self.parts if model.R.atlas.glow(p.role)}
        self.assertTrue(glow and all(n.startswith('flash_') for n in glow))
        self.assertLess(max(p[2] for p in self.v), 58)  # shoulder-high prism on a plinth, with crown

    def _inside_prism(self, points, margin=.3):
        inner = model.APOTHEM-1.05
        for p in points:
            for a in model.FACES:
                n = (math.cos(math.radians(a)), math.sin(math.radians(a)))
                self.assertLess(p[0]*n[0]+p[1]*n[1], inner-margin)
            self.assertTrue(model.PANEL_Z[0] < p[2] < model.PANEL_Z[1])

    def test_flash_crystal_sealed_at_rest_and_in_plinth_after_death(self):
        self._inside_prism(self.part_points(self.v, 'flash_'))
        final = self.posed('shatter', len(self.clip['shatter']['frames'])-1)
        for p in self.part_points(final, 'flash_'):
            self.assertLess(p[2], 11.5)
            self.assertLess(math.hypot(p[0], p[1]), 9.8)

    def test_flash_opens_panels_and_raises_crystal(self):
        mid = self.posed('flash', 9)
        crystal = self.part_points(mid, 'flash_')
        self.assertGreater(min(p[2] for p in crystal), 36)
        tops = [max(p[2] for p in self.part_points(mid, 'mirror_upper_%d' % k)) for k in range(3)]
        self.assertTrue(all(t < 41 for t in tops))
        cap = self.part_points(mid, 'prism_crown')
        self.assertGreater(min(p[2] for p in cap), max(p[2] for p in crystal))

    def test_beckon_lowers_the_front_mirrors(self):
        mid = self.posed('beckon', 10)
        for k in (0, 2):
            c = centroid(self.part_points(mid, 'mirror_upper_%d' % k))
            r = centroid(self.part_points(self.v, 'mirror_upper_%d' % k))
            self.assertGreater(c[0]-r[0], 6)
            self.assertLess(c[2], r[2]-5)
        self.assertGreater(max(p[2] for p in self.part_points(mid, 'flash_')), 38)

    def test_shattered_death(self):
        final = self.posed('shatter', len(self.clip['shatter']['frames'])-1)
        for k in range(3):
            low = self.part_points(final, 'mirror_lower_%d' % k)
            self.assertLess(max(p[2] for p in low), 3)
            high = self.part_points(final, 'mirror_upper_%d' % k)
            self.assertGreater(min(p[2] for p in high), 11.9)
            self.assertLess(max(p[2] for p in high), 17)
        for k in range(3):
            column = self.bone_points(final, 'column_%d' % k)
            self.assertLess(min(p[2] for p in column), .2)
            self.assertLess(max(p[2] for p in column), 4.5)
        self.assertLess(self.bounds[-1][5], 25)


if __name__ == '__main__':
    unittest.main()

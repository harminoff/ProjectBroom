"""Sentinel: immobile statue, crystal glow region, clearance, casting poses, shatter and exact bytes."""
import math
import unittest
from . import guardian_kit as K
from . import sentinel_animation as g

Base = K.creature_tests('sentinel_animation', 'sentinel_materials', 'MK_SENTINEL',
                        {'present': ('shaders/sentinel-crystal.fp',), 'absent': ('brightmap',)}, uses_root=True)


class SentinelTests(Base):
    def test_never_leaves_its_plinth(self):
        # Immobile turret: the root and plinth never move and the walk role is a static rest.
        for c in self.clips:
            for f in c['frames']:
                self.assertEqual(tuple(f[0][:7]), (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0))
        for i in range(len(self.clips[1]['frames'])):
            T = g.matrices(self.frame('rest', i))
            for bone in ('body_lower', 'body_upper'):
                self.assertLess(math.dist(T[g.IDS[bone]][0], g.REST[g.IDS[bone]]), 1e-9)

    def test_glow_islands_live_only_in_the_shader_region(self):
        x0, y0, size = g.GLOW_REGION
        for p in self.parts:
            for u, v in p.uv:
                px, py = u*K.SIZE, (1-v)*K.SIZE
                inside = x0 <= px < x0+size and y0 <= py < y0+size
                self.assertEqual(inside, p.role == 'glow', p.name)
        shader = (K.ROOT/g.SHADER).read_text()
        self.assertIn('step(0.75, uv.x)', shader); self.assertIn('step(0.25, uv.y)', shader)
        self.assertEqual(x0/K.SIZE, .75); self.assertEqual((y0+size)/K.SIZE, .25)

    def test_focus_thrusts_the_crystal_and_bursts_the_ring(self):
        rest = g.matrices(self.frame('idle', 0)); T = g.matrices(self.frame('focus'))
        self.assertGreater(T[g.IDS['crystal']][0][0], rest[g.IDS['crystal']][0][0]+10)
        radii = [math.dist(T[g.IDS[f'shard_{i}']][0], T[g.IDS['crystal']][0]) for i in range(g.SHARDS)]
        self.assertGreater(min(radii), 14)

    def test_mend_lowers_the_crystal_into_a_wide_low_ring(self):
        T = g.matrices(self.frame('mend'))
        self.assertLess(T[g.IDS['crystal']][0][2], 40)
        for i in range(g.SHARDS):
            loc = T[g.IDS[f'shard_{i}']][0]
            self.assertLess(loc[2], 34); self.assertGreater(math.hypot(loc[0], loc[1]), 10)

    def test_crystal_value_range(self):
        import numpy
        self.test_runtime_and_material_bytes()
        x0, y0, size = g.GLOW_REGION
        region = self.image[y0:y0+size, x0:x0+size].reshape(-1, 3)
        lit = region[region.sum(1) > 0]
        self.assertGreater(numpy.percentile(lit[:, 2], 50), 200)   # the crystal is blue light


del Base  # keep unittest from collecting the shared base as its own case


if __name__ == '__main__': unittest.main()

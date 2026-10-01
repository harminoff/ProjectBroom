"""Eldritch totem: alien spire signature, hidden glowing cores, blade fan,
toppled death, colour-keyed glyphs and exact bytes."""
import math
import unittest
import zlib
import numpy as np
from . import eldritch_totem_animation as model, eldritch_totem_materials as materials
from .relic_kit import RelicChecks, rotate, inverse, sub, add, SIZE, CELL, ROOT


def centroid(points):
    return tuple(sum(p[i] for p in points)/len(points) for i in range(3))


def profile_radius(profile, z):
    for (r, zz), (R, ZZ) in zip(profile, profile[1:]):
        if zz <= z <= ZZ:
            return r+(R-r)*(z-zz)/(ZZ-zz)
    return -1


class EldritchTotemTests(RelicChecks, unittest.TestCase):
    model = model
    symbol = 'MK_ELDRITCH_TOTEM'
    shader = 'shaders/eldritch-totem-glyphs.fp'

    def test_alien_spire_signature(self):
        names = {p.name for p in self.parts}
        for bone in model.PROFILES:
            self.assertIn('twisted_spire_'+bone, names)
        self.assertEqual(sum(n.startswith('spectral_blade_') for n in names), 5)
        self.assertEqual(sum(n.startswith('cairn_stone_') for n in names), 7)
        self.assertFalse(any('tendril' in n or 'eye' in n for n in names))
        glow = {p.name for p in self.parts if model.R.atlas.glow(p.role)}
        self.assertEqual(glow, {'spectral_blade_%d' % k for k in range(5)} | {'ichor_core_%d' % k for k in range(3)})
        spire = self.part_points(self.v, 'twisted_spire_')
        self.assertGreater(max(p[2] for p in spire), 56)

    def _core_inside(self, frame):
        """Each core, taken into its segment's rest frame, stays inside it."""
        tf = model.RIG.matrices(frame)
        verts = model.deform(self.v, self.w, frame)
        for k, (core, seg) in enumerate((('core0', 'root'), ('core1', 'seg1'), ('core2', 'seg2'))):
            loc, q = tf[model.IDS[seg]]; pivot = model.REST[model.IDS[seg]]
            prof = model.PROFILES[seg]
            for p in self.part_points(verts, 'ichor_core_%d' % k):
                local = add(pivot, rotate(inverse(q), sub(p, loc)))
                limit = profile_radius(prof, local[2])
                self.assertGreater(limit-math.hypot(local[0], local[1]), .3, (core, local))

    def test_cores_hidden_at_rest_and_after_death(self):
        self._core_inside(model.pose('rest', 0))
        self._core_inside(self.clip['topple']['frames'][-1])

    def test_crackle_opens_glowing_gaps_and_fans_blades(self):
        mid = self.posed('crackle', 9)
        tops = [16, 31, 45]
        for k, (seg, top) in enumerate(zip(('seg1', 'seg2', 'crown'), tops)):
            base = min(p[2] for p in self.bone_points(mid, seg))
            below = [p for p in self.part_points(mid, 'ichor_core_%d' % k)]
            self.assertGreater(base-top-(k*model.GAP), 3.5)  # open gap
            self.assertGreater(max(p[2] for p in below), base)  # core spans it
        for k in range(5):
            blade = self.part_points(mid, 'spectral_blade_%d' % k)
            self.assertLess(max(p[2] for p in blade)-min(p[2] for p in blade), 8)  # near horizontal
            self.assertGreater(max(math.hypot(p[0], p[1]) for p in blade), 24)

    def test_strike_swings_blades_toward_target(self):
        rest = centroid(self.part_points(self.v, 'spectral_blade_'))
        mid = centroid(self.part_points(self.posed('strike', 10), 'spectral_blade_'))
        self.assertGreater(mid[0]-rest[0], 6)

    def test_toppled_death_lies_on_the_floor(self):
        final = self.posed('topple', len(self.clip['topple']['frames'])-1)
        for seg in ('seg1', 'seg2', 'crown'):
            pts = self.bone_points(final, seg)
            self.assertLess(min(p[2] for p in pts), .2)
            self.assertLess(max(p[2] for p in pts), 18)
        for k in range(5):
            blade = self.part_points(final, 'spectral_blade_%d' % k)
            self.assertLess(max(p[2] for p in blade), 4)
        self.assertLess(self.bounds[-1][5], 18)

    def test_glyph_key_only_in_stone_cell(self):
        png = (ROOT/'mod/BrogueDoom'/model.SKIN).read_bytes()
        raw = zlib.decompress(png[png.index(b'IDAT')+4:png.index(b'IEND')-8])
        rows = np.frombuffer(raw, dtype=np.uint8).reshape(SIZE, SIZE*3+1)[:, 1:].reshape(SIZE, SIZE, 3)
        key = (rows[..., 0] >= 230) & (rows[..., 1] <= 76) & (rows[..., 2] <= 76)
        key[:, 3*CELL:] = False  # column 3 is fullbright anyway
        c, r = materials.ATLAS.roles['stone']
        inside = key[r*CELL:(r+1)*CELL, c*CELL:(c+1)*CELL].sum()
        self.assertGreater(inside, 1500)
        self.assertEqual(int(key.sum()), int(inside))


if __name__ == '__main__':
    unittest.main()

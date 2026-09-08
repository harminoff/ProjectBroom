"""Geometry proof gates for the full-size dynamic terrain projection."""
import unittest
from collections import Counter, defaultdict

from .compile import make_map_text
from .test_compile import sample_model
from .verify import blocks, int_property, optional_int_property, bool_property
from .terrain_geometry import verify_geometry
from .verify import VerifyError


class TerrainGeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.level = sample_model()['levels'][0]
        cls.text, _, _ = make_map_text(cls.level, 79, 29, addressable=True)

    def test_all_cells_and_two_role_controls(self):
        sectors = blocks(self.text, 'sector')
        self.assertEqual(len(sectors), 2291 * 3)
        tags = [int_property(s, 'id') for s in sectors]
        self.assertEqual(len(set(tags)), len(tags))
        for base in (10000, 30000, 40000):
            self.assertEqual(set(range(base, base + 2291)), {tag for tag in tags if base <= tag < base + 2291})
        self.assertEqual(Counter(int_property(s, 'user_brogue_role') for s in sectors), {0: 2291, 1: 2291, 2: 2291})
        for sector in sectors:
            self.assertGreater(int_property(sector, 'heightceiling'), int_property(sector, 'heightfloor'))

    def test_closed_polygons_shared_internal_boundaries(self):
        sides = blocks(self.text, 'sidedef')
        sectors = blocks(self.text, 'sector')
        vertices = blocks(self.text, 'vertex')
        degrees = defaultdict(Counter)
        edges = set()
        for line in blocks(self.text, 'linedef'):
            a, b = int_property(line, 'v1'), int_property(line, 'v2')
            self.assertNotEqual(a, b)
            self.assertNotIn(tuple(sorted((a, b))), edges)
            edges.add(tuple(sorted((a, b))))
            front = int_property(sides[int_property(line, 'sidefront')], 'sector')
            back = optional_int_property(line, 'sideback')
            for side in (int_property(line, 'sidefront'), back):
                if side is not None:
                    sector = int_property(sides[side], 'sector')
                    degrees[sector][a] += 1
                    degrees[sector][b] += 1
            if int_property(sectors[front], 'user_brogue_role') == 0 and back is None:
                ax, ay = int_property(vertices[a], 'x'), int_property(vertices[a], 'y')
                bx, by = int_property(vertices[b], 'x'), int_property(vertices[b], 'y')
                self.assertTrue((ax == bx and ax in (0, 79*64)) or (ay == by and ay in (0,29*64)))
            self.assertEqual(bool_property(line, 'twosided'), back is not None)
        self.assertEqual(len(degrees), 2291 * 3)
        for degree in degrees.values():
            self.assertTrue(all(count == 2 for count in degree.values()))

    def test_reserved_planes_are_render_only(self):
        setups = [line for line in blocks(self.text, 'linedef') if optional_int_property(line, 'special') == 160]
        self.assertEqual(len(setups), 4582)
        for line in setups:
            self.assertEqual(int_property(line, 'arg1'), 3)
            self.assertEqual(int_property(line, 'arg2'), 2049)
            self.assertEqual(int_property(line, 'arg3'), 255)

    def test_byte_identical(self):
        self.assertEqual(self.text, make_map_text(self.level, 79, 29, addressable=True)[0])

    def test_verifier_rejects_collision_and_wrong_plane_owner(self):
        verify_geometry(self.level, self.text)
        for broken in (self.text.replace('blocking = false;', 'blocking = true;', 1),
                       self.text.replace('arg1 = 3;', 'arg1 = 1;', 1),
                       self.text.replace('user_brogue_owner = 0;', 'user_brogue_owner = 1;', 1)):
            with self.assertRaises(VerifyError):
                verify_geometry(self.level, broken)


if __name__ == '__main__':
    unittest.main()
